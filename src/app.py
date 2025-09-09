import gradio as gr
import os
from pathlib import Path
import tempfile

from latex_parser import LaTeXParser
from key_identifier import KeyIdentifier
from inspirehep_client import InspireHEPClient
from bibtex_manager import BibTeXManager
from bibtex_processor import BibTeXProcessor

class BibTeXGeneratorApp:
    def __init__(self):
        self.latex_parser = LaTeXParser()
        self.key_identifier = KeyIdentifier()
        self.inspirehep_client = InspireHEPClient()
        self.bibtex_manager = BibTeXManager()
        self.bibtex_processor = BibTeXProcessor()
    
    def process_latex_file(self, latex_file, output_filename="", progress=gr.Progress()):
        """Main processing function called by Gradio interface."""
        
        if latex_file is None:
            return "❌ Please upload a LaTeX file first.", None, None, ""
        
        try:
            progress(0.1, desc="Reading LaTeX file...")
            
            # Read original LaTeX content
            with open(latex_file.name, 'r', encoding='utf-8') as f:
                original_latex_content = f.read()
            
            # Extract citations and bibliography name from uploaded file
            citations, bibliography_name = self.latex_parser.process_uploaded_file(latex_file.name)
            
            if not citations:
                return "⚠️ No citations found in the LaTeX file.", None, None, ""
            
            progress(0.2, desc=f"Found {len(citations)} citations...")
            
            # Identify citation key types
            categorized_keys = self.key_identifier.process_keys(citations)
            
            progress(0.3, desc="Identifying citation types...")
            
            # Report what we found
            status_msg = f"🔍 **Citation Analysis:**\n"
            status_msg += f"📄 Total citations found: {len(citations)}\n"
            status_msg += f"• InspireHEP IDs: {len(categorized_keys['inspirehep'])}\n"
            status_msg += f"• InspireHEP BibTeX keys: {len(categorized_keys['inspirehep_bibtex'])}\n"
            status_msg += f"• arXiv IDs: {len(categorized_keys['arxiv'])}\n"
            status_msg += f"• Unknown keys: {len(categorized_keys['unknown'])}\n\n"
            
            if categorized_keys['unknown']:
                status_msg += f"⚠️ **Unknown keys:** {', '.join(categorized_keys['unknown'])}\n\n"
            
            progress(0.4, desc="Fetching BibTeX entries from InspireHEP...")
            
            # Fetch BibTeX entries
            raw_bibtex_entries = self.inspirehep_client.fetch_bibtex_entries(categorized_keys)
            
            if not raw_bibtex_entries:
                return "❌ No BibTeX entries could be fetched from InspireHEP.", None, None, ""
            
            progress(0.6, desc="Processing and deduplicating entries...")
            
            # Process and deduplicate entries
            deduplicated_entries, key_mapping = self.bibtex_processor.process_and_deduplicate(raw_bibtex_entries)
            
            progress(0.7, desc="Creating standardized LaTeX file...")
            
            # Create temporary directory for output files
            temp_dir = tempfile.mkdtemp()
            
            # Determine filenames
            bib_filename = self.bibtex_manager.determine_output_filename(
                custom_name=output_filename if output_filename.strip() else None,
                bibliography_name=bibliography_name
            )
            
            # Create LaTeX filename based on original file
            original_name = Path(latex_file.name).stem
            latex_filename = f"{original_name}_standardized.tex"
            
            # Create standardized LaTeX file
            latex_path, replacements_made = self.bibtex_processor.create_standardized_latex(
                original_latex_content, 
                key_mapping,
                str(Path(temp_dir) / latex_filename)
            )
            
            progress(0.9, desc="Writing output files...")
            
            # Write both LaTeX and BibTeX files
            final_latex_path, final_bibtex_path = self.bibtex_manager.write_latex_and_bibtex_files(
                deduplicated_entries,
                open(latex_path, 'r', encoding='utf-8').read(),
                latex_filename,
                bib_filename,
                temp_dir
            )
            
            progress(1.0, desc="Complete!")
            
            # Generate comprehensive summary
            processing_summary = self.bibtex_processor.generate_processing_summary(
                len(raw_bibtex_entries),
                len(deduplicated_entries), 
                key_mapping,
                replacements_made
            )
            
            basic_summary = self.bibtex_manager.get_summary(
                deduplicated_entries, 
                categorized_keys['unknown']
            )
            
            status_msg += f"✅ **Files Generated:**\n"
            status_msg += f"📄 LaTeX: {latex_filename}\n"
            status_msg += f"📚 BibTeX: {bib_filename}\n"
            status_msg += f"📁 Final entries: {len(deduplicated_entries)}\n\n"
            status_msg += processing_summary + "\n"
            status_msg += basic_summary
            
            return status_msg, final_latex_path, final_bibtex_path, ""
            
        except Exception as e:
            return f"❌ Error processing file: {str(e)}", None, None, ""

def create_interface():
    """Create and configure the Gradio interface."""
    
    app = BibTeXGeneratorApp()
    
    with gr.Blocks(title="InspireHEP BibTeX Generator", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("""
        # 📚 InspireHEP BibTeX Generator
        
        Upload a LaTeX file with `\\cite{}` commands and automatically generate **both**:
        - **Standardized LaTeX file** with all citation keys converted to InspireHEP format
        - **Deduplicated BibTeX file** with entries from InspireHEP
        
        **Supported citation formats:**
        - InspireHEP record IDs (numeric, e.g., `123456`)
        - InspireHEP BibTeX keys (e.g., `Dumitrescu:2025vfp`, `Carleo:2019ptp`)
        - arXiv IDs (e.g., `2301.12345`, `hep-th/0501001`, `arXiv:2301.12345`)
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Input section
                gr.Markdown("### 📝 Input")
                
                latex_file = gr.File(
                    label="Upload LaTeX file (.tex)",
                    file_types=[".tex"],
                    file_count="single"
                )
                
                output_filename = gr.Textbox(
                    label="Output filename (optional)",
                    placeholder="Leave empty to auto-detect from \\bibliography{} or use 'references.bib'",
                    value=""
                )
                
                process_btn = gr.Button(
                    "🚀 Generate Files", 
                    variant="primary", 
                    size="lg"
                )
                
            with gr.Column(scale=3):
                # Output section
                gr.Markdown("### 📋 Results")
                
                status_output = gr.Textbox(
                    label="Processing Status",
                    lines=12,
                    max_lines=20,
                    interactive=False
                )
                
                with gr.Row():
                    latex_download = gr.File(
                        label="📄 Download Standardized LaTeX",
                        interactive=False
                    )
                    bibtex_download = gr.File(
                        label="📚 Download BibTeX File",
                        interactive=False
                    )
        
        # Event handlers
        process_btn.click(
            fn=app.process_latex_file,
            inputs=[latex_file, output_filename],
            outputs=[status_output, latex_download, bibtex_download, gr.State()]
        )
        
        # Example section
        with gr.Row():
            gr.Markdown("""
            ### 💡 Example LaTeX citations:
            ```latex
            \\cite{123456}                    % InspireHEP record ID
            \\cite{Dumitrescu:2025vfp}       % InspireHEP BibTeX key
            \\cite{2301.12345}               % arXiv ID (new format)
            \\cite{hep-th/0501001}           % arXiv ID (old format)
            \\cite{arXiv:2301.12345}         % arXiv ID with prefix
            \\cite{123456,Carleo:2019ptp,2112.00006} % Multiple citations
            ```
            """)
    
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True
    )