import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import tempfile


class BibTeXProcessor:
    """Process BibTeX entries to extract standardized keys and handle deduplication."""
    
    def __init__(self):
        # Regex to extract BibTeX entry key from @article{key, ...}
        self.entry_key_pattern = re.compile(r'@\w+\{([^,\s]+),', re.IGNORECASE)
    
    def extract_bibtex_key(self, bibtex_entry: str) -> Optional[str]:
        """Extract the citation key from a BibTeX entry."""
        match = self.entry_key_pattern.search(bibtex_entry)
        if match:
            return match.group(1).strip()
        return None
    
    def process_and_deduplicate(self, bibtex_entries: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Process BibTeX entries to:
        1. Extract standardized InspireHEP BibTeX keys from entries
        2. Remove duplicates based on BibTeX key
        3. Create mapping from original citation keys to standardized keys
        
        Returns:
            - deduplicated_entries: {standard_key: bibtex_entry}
            - key_mapping: {original_key: standard_key}
        """
        deduplicated_entries = {}
        key_mapping = {}
        seen_keys = {}
        
        for original_key, bibtex_entry in bibtex_entries.items():
            # Extract the standard BibTeX key from the entry
            standard_key = self.extract_bibtex_key(bibtex_entry)
            
            if not standard_key:
                print(f"Warning: Could not extract BibTeX key from entry for {original_key}")
                # Use original key as fallback
                standard_key = original_key
            
            # Check for duplicates
            if standard_key in seen_keys:
                print(f"Duplicate detected: {original_key} -> {standard_key} (same as {seen_keys[standard_key]})")
                # Map to existing standard key
                key_mapping[original_key] = standard_key
            else:
                # New entry
                deduplicated_entries[standard_key] = bibtex_entry
                key_mapping[original_key] = standard_key
                seen_keys[standard_key] = original_key
        
        return deduplicated_entries, key_mapping
    
    def create_standardized_latex(self, 
                                latex_content: str, 
                                key_mapping: Dict[str, str],
                                output_path: str) -> str:
        """
        Create a new LaTeX file with all citation keys replaced by standardized InspireHEP keys.
        
        Args:
            latex_content: Original LaTeX content
            key_mapping: {original_key: standard_key} mapping
            output_path: Path where to save the new LaTeX file
            
        Returns:
            Path to the created standardized LaTeX file
        """
        updated_content = latex_content
        replacements_made = 0
        
        # Find all \cite{...} commands and replace keys
        def replace_cite_keys(match):
            nonlocal replacements_made
            full_cite = match.group(0)  # Full \cite{...}
            keys_part = match.group(1)  # Content inside braces
            
            # Split multiple keys by comma
            keys = [key.strip() for key in keys_part.split(',') if key.strip()]
            new_keys = []
            
            for key in keys:
                if key in key_mapping:
                    new_keys.append(key_mapping[key])
                    replacements_made += 1
                else:
                    # Keep original key if no mapping found
                    new_keys.append(key)
            
            # Reconstruct \cite{new_keys}
            return f"\\cite{{{','.join(new_keys)}}}"
        
        # Apply replacements
        cite_pattern = re.compile(r'\\cite\{([^}]+)\}')
        updated_content = cite_pattern.sub(replace_cite_keys, updated_content)
        
        # Write updated LaTeX file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return output_path, replacements_made
    
    def generate_processing_summary(self, 
                                  original_count: int,
                                  deduplicated_count: int,
                                  key_mapping: Dict[str, str],
                                  replacements_made: int) -> str:
        """Generate a summary of the processing results."""
        duplicates_removed = original_count - deduplicated_count
        
        summary = f"🔄 **Processing Summary:**\n"
        summary += f"📥 Original entries fetched: {original_count}\n"
        summary += f"🗑️ Duplicates removed: {duplicates_removed}\n"
        summary += f"📤 Final unique entries: {deduplicated_count}\n"
        summary += f"🔄 Citation key replacements: {replacements_made}\n\n"
        
        if duplicates_removed > 0:
            summary += f"**Duplicate entries found:**\n"
            # Find which keys were duplicates
            seen_standard = {}
            for orig, standard in key_mapping.items():
                if standard in seen_standard:
                    summary += f"• `{orig}` → `{standard}` (duplicate of `{seen_standard[standard]}`)\n"
                else:
                    seen_standard[standard] = orig
            summary += "\n"
        
        if replacements_made > 0:
            summary += f"**Citation key standardization:**\n"
            for orig, standard in key_mapping.items():
                if orig != standard:
                    summary += f"• `{orig}` → `{standard}`\n"
        
        return summary