import os
from pathlib import Path
from typing import Dict, Optional, Tuple

class BibTeXManager:
    def __init__(self):
        pass
    
    def determine_output_filename(self, 
                                custom_name: Optional[str] = None,
                                bibliography_name: Optional[str] = None,
                                default_name: str = "references") -> str:
        """
        Determine the output filename for the BibTeX file.
        
        Priority:
        1. Custom name from user input
        2. Bibliography name extracted from LaTeX file
        3. Default name
        """
        if custom_name:
            filename = custom_name.strip()
        elif bibliography_name:
            filename = bibliography_name.strip()
        else:
            filename = default_name
        
        # Ensure .bib extension
        if not filename.endswith('.bib'):
            filename += '.bib'
            
        return filename
    
    def write_bibtex_file(self, 
                         bibtex_entries: Dict[str, str], 
                         filename: str,
                         output_dir: str = ".") -> str:
        """Write all BibTeX entries to a single file."""
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Full path for the output file
        output_path = Path(output_dir) / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("% BibTeX file generated from InspireHEP\n")
                f.write("% Generated using generate-inspirehep-bibtex\n")
                f.write("% All citation keys have been standardized to InspireHEP format\n\n")
                
                for key, bibtex in bibtex_entries.items():
                    f.write(f"% Entry for standardized key: {key}\n")
                    f.write(bibtex.strip())
                    f.write("\n\n")
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Error writing BibTeX file: {str(e)}")
    
    def write_latex_and_bibtex_files(self,
                                    bibtex_entries: Dict[str, str],
                                    latex_content: str,
                                    latex_filename: str,
                                    bib_filename: str,
                                    output_dir: str = ".") -> Tuple[str, str]:
        """
        Write both standardized LaTeX and BibTeX files.
        
        Returns:
            Tuple of (latex_path, bibtex_path)
        """
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Write BibTeX file
        bibtex_path = self.write_bibtex_file(bibtex_entries, bib_filename, output_dir)
        
        # Write LaTeX file
        latex_path = Path(output_dir) / latex_filename
        try:
            with open(latex_path, 'w', encoding='utf-8') as f:
                f.write("% LaTeX file with standardized InspireHEP citation keys\n")
                f.write("% Generated using generate-inspirehep-bibtex\n\n")
                f.write(latex_content)
            
            return str(latex_path), bibtex_path
            
        except Exception as e:
            raise Exception(f"Error writing LaTeX file: {str(e)}")
    
    def get_summary(self, bibtex_entries: Dict[str, str], 
                   unknown_keys: list = None) -> str:
        """Generate a summary of the processing results."""
        total_found = len(bibtex_entries)
        total_unknown = len(unknown_keys) if unknown_keys else 0
        
        summary = f"Processing complete!\n"
        summary += f"✅ Found and processed: {total_found} entries\n"
        
        if total_unknown > 0:
            summary += f"⚠️ Unknown citation keys: {total_unknown}\n"
            summary += f"   Keys: {', '.join(unknown_keys)}\n"
        
        if bibtex_entries:
            summary += f"\nProcessed keys:\n"
            for key in bibtex_entries.keys():
                summary += f"  • {key}\n"
        
        return summary