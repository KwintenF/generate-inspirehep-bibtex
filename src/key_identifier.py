import re
from typing import Union, List
from enum import Enum

class KeyType(Enum):
    INSPIREHEP = "inspirehep"
    INSPIREHEP_BIBTEX = "inspirehep_bibtex"
    ARXIV = "arxiv"
    UNKNOWN = "unknown"

class KeyIdentifier:
    def __init__(self):
        # InspireHEP record IDs are typically numeric
        self.inspirehep_pattern = re.compile(r'^\d+$')
        
        # InspireHEP BibTeX key format: Author:YEARxxx (e.g., Dumitrescu:2025vfp)
        self.inspirehep_bibtex_pattern = re.compile(r'^[A-Za-z][A-Za-z0-9_]*:\d{4}[a-zA-Z]{3}$')
        
        # arXiv patterns for different formats
        # New format: YYMM.NNNN[vN] or YYMM.NNNNvN
        self.arxiv_new_pattern = re.compile(r'^\d{4}\.\d{4,5}(v\d+)?$')
        
        # Old format: subject-class/YYMMnnn[vN]
        self.arxiv_old_pattern = re.compile(r'^[a-z-]+(\.[A-Z]{2})?\/\d{7}(v\d+)?$', re.IGNORECASE)
        
        # Sometimes people use arXiv: prefix
        self.arxiv_prefix_pattern = re.compile(r'^arxiv:(.+)$', re.IGNORECASE)
    
    def identify_key_type(self, key: str) -> KeyType:
        """Identify the type of citation key."""
        key = key.strip()
        
        # Check for arXiv prefix first
        arxiv_match = self.arxiv_prefix_pattern.match(key)
        if arxiv_match:
            key = arxiv_match.group(1)
        
        # Check arXiv patterns
        if self.arxiv_new_pattern.match(key) or self.arxiv_old_pattern.match(key):
            return KeyType.ARXIV
        
        # Check InspireHEP BibTeX key format (Author:YEARxxx)
        if self.inspirehep_bibtex_pattern.match(key):
            return KeyType.INSPIREHEP_BIBTEX
        
        # Check InspireHEP pattern (pure numeric)
        if self.inspirehep_pattern.match(key):
            return KeyType.INSPIREHEP
        
        return KeyType.UNKNOWN
    
    def normalize_key(self, key: str) -> str:
        """Normalize key for API queries."""
        key = key.strip()
        
        # Remove arXiv: prefix if present
        arxiv_match = self.arxiv_prefix_pattern.match(key)
        if arxiv_match:
            return arxiv_match.group(1)
        
        return key
    
    def process_keys(self, keys: List[str]) -> dict:
        """Process a list of keys and categorize them."""
        result = {
            'inspirehep': [],
            'inspirehep_bibtex': [],
            'arxiv': [],
            'unknown': []
        }
        
        for key in keys:
            key_type = self.identify_key_type(key)
            normalized_key = self.normalize_key(key)
            
            if key_type == KeyType.INSPIREHEP:
                result['inspirehep'].append(normalized_key)
            elif key_type == KeyType.INSPIREHEP_BIBTEX:
                result['inspirehep_bibtex'].append(normalized_key)
            elif key_type == KeyType.ARXIV:
                result['arxiv'].append(normalized_key)
            else:
                result['unknown'].append(key)
        
        return result