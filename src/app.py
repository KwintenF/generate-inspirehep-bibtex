import gradio as gr
import os
from pathlib import Path
import tempfile

from latex_parser import LaTeXParser
from key_identifier import KeyIdentifier
from inspirehep_client import InspireHEPClient
from bibtex_manager import BibTeXManager

class BibTeXGeneratorApp:
    def __init__(self):
        self.latex_parser = LaTeXParser()
        self.key_identifier = KeyIdentifier()
        self.inspirehep_client = InspireHEPClient()
        self.bibtex_manager = BibTeXManager()
    
    def process_latex_file(self, latex_file, output_filename="", progress=gr.Progress()):
        """Main processing function called by Gradio interface."""
        
        if latex_file is None:
            return "❌ Please upload a LaTeX file first.", None, ""
        
        try:
            progress(0.1, desc="Reading LaTeX file...")
            
            # Extract citations and bibliography name from uploaded file
            citations, bibliography_name = self.latex_parser.process_uploaded_file(latex_file.name)
            
            if not citations:
                return "⚠️ No citations found in the LaTeX file.", None, ""
            
            progress(0.2, desc=f"Found {len(citations)} citations...")
            
            # Identify citation key types
            categorized_keys = self.key_identifier.process_keys(citations)
            
            progress(0.3, desc="Identifying citation types...")
            
            # Report what we found
            status_msg = f"Found {len(citations)} total citations:\n"
            status_msg += f"• InspireHEP IDs: {len(categorized_keys['inspirehep'])}\n"
            status_msg += f"• InspireHEP BibTeX keys: {len(categorized_keys['inspirehep_bibtex'])}\n"
            status_msg += f"• arXiv IDs: {len(categorized_keys['arxiv'])}\n"
            status_msg += f"• Unknown keys: {len(categorized_keys['unknown'])}\n\n"
            
            if categorized_keys['unknown']:
                status_msg += f"Unknown keys: {', '.join(categorized_keys['unknown'])}\n\n"
            
            progress(0.4, desc="Fetching BibTeX entries from InspireHEP...")
            
            # Fetch BibTeX entries
            bibtex_entries = self.inspirehep_client.fetch_bibtex_entries(categorized_keys)
            
            progress(0.8, desc="Writing BibTeX file...")
            
            # Determine output filename
            output_name = self.bibtex_manager.determine_output_filename(
                custom_name=output_filename if output_filename.strip() else None,
                bibliography_name=bibliography_name
            )
            
            # Create a temporary directory for output
            temp_dir = tempfile.mkdtemp()
            output_path = self.bibtex_manager.write_bibtex_file(
                bibtex_entries, 
                output_name, 
                temp_dir
            )
            
            progress(1.0, desc="Complete!")
            
            # Generate summary
            summary = self.bibtex_manager.get_summary(
                bibtex_entries, 
                categorized_keys['unknown']
            )
            
            status_msg += f"✅ Successfully generated: {output_name}\n"
            status_msg += f"📁 Entries written: {len(bibtex_entries)}\n\n"
            status_msg += summary
            
            return status_msg, output_path, output_name
            
        except Exception as e:
            return f"❌ Error processing file: {str(e)}", None, ""

def create_interface():
    """Create and configure the Gradio interface."""
    
    app = BibTeXGeneratorApp()
    
    with gr.Blocks(title="InspireHEP BibTeX Generator", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("""
        # 📚 InspireHEP BibTeX Generator
        
        Upload a LaTeX file with `\\cite{}` commands and automatically generate a BibTeX file from InspireHEP.
        
        **Supported citation formats:**
        - InspireHEP record IDs (numeric, e.g., `123456`)
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
                    "🚀 Generate BibTeX", 
                    variant="primary", 
                    size="lg"
                )
                
            with gr.Column(scale=3):
                # Output section
                gr.Markdown("### 📋 Results")
                
                status_output = gr.Textbox(
                    label="Status",
                    lines=15,
                    max_lines=20,
                    interactive=False
                )
                
                download_file = gr.File(
                    label="Download BibTeX file",
                    interactive=False
                )
        
        # Event handlers
        process_btn.click(
            fn=app.process_latex_file,
            inputs=[latex_file, output_filename],
            outputs=[status_output, download_file, gr.State()]
        )
        
        # Example section
        with gr.Row():
            gr.Markdown("""
            ### 💡 Example LaTeX citations:
            ```latex
            \\cite{123456}                    % InspireHEP record ID
            \\cite{2301.12345}               % arXiv ID (new format)
            \\cite{hep-th/0501001}           % arXiv ID (old format)
            \\cite{arXiv:2301.12345}         % arXiv ID with prefix
            \\cite{123456,2301.12345,unknown} % Multiple citations
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