import re
from pathlib import Path
from typing import List, Tuple, Optional

class LaTeXParser:
    def __init__(self):
        self.cite_pattern = re.compile(r'\\cite\{([^}]+)\}')
        self.bibliography_pattern = re.compile(r'\\bibliography\{([^}]+)\}')
        
    def extract_citations(self, latex_content: str) -> List[str]:
        """Extract all citation keys from LaTeX content."""
        matches = self.cite_pattern.findall(latex_content)
        
        # Handle multiple citations in single \cite{key1,key2,key3}
        all_keys = []
        for match in matches:
            keys = [key.strip() for key in match.split(',')]
            all_keys.extend(keys)
        
        return list(set(all_keys))  # Remove duplicates
    
    def extract_bibliography_name(self, latex_content: str) -> Optional[str]:
        """Extract bibliography filename from \bibliography{filename} command."""
        match = self.bibliography_pattern.search(latex_content)
        if match:
            return match.group(1).strip()
        return None
    
    def process_uploaded_file(self, file_path: str) -> Tuple[List[str], Optional[str]]:
        """
        Process uploaded LaTeX file from Gradio.
        
        In Gradio, uploaded files are saved to a temporary location.
        The file_path parameter contains the full path to the temporary file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            citations = self.extract_citations(content)
            bibliography_name = self.extract_bibliography_name(content)
            
            return citations, bibliography_name
            
        except Exception as e:
            raise Exception(f"Error reading LaTeX file: {str(e)}")