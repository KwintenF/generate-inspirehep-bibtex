import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from key_identifier import KeyIdentifier, KeyType


class TestKeyIdentifier(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.identifier = KeyIdentifier()
    
    def test_inspirehep_ids(self):
        """Test identification of InspireHEP record IDs (numeric)."""
        inspirehep_ids = [
            "1724847",
            "796859", 
            "1450044",
            "123456",
            "123456789012345"  # Very long ID from edge cases
        ]
        
        for key in inspirehep_ids:
            with self.subTest(key=key):
                key_type = self.identifier.identify_key_type(key)
                self.assertEqual(key_type, KeyType.INSPIREHEP, 
                               f"Key '{key}' should be identified as InspireHEP ID")
    
    def test_inspirehep_bibtex_keys(self):
        """Test identification of InspireHEP BibTeX keys (Author:YEARxxx)."""
        bibtex_keys = [
            "Dumitrescu:2025vfp",
            "Carleo:2019ptp", 
            "Preskill:2018fag",
            "Biamonte:2017zfb",
            "Unknown:2023abc",      # Valid pattern even if fake
            "FakeAuthor:2024xyz"    # Valid pattern even if fake
        ]
        
        for key in bibtex_keys:
            with self.subTest(key=key):
                key_type = self.identifier.identify_key_type(key)
                self.assertEqual(key_type, KeyType.INSPIREHEP_BIBTEX,
                               f"Key '{key}' should be identified as InspireHEP BibTeX key")
    
    def test_arxiv_new_format(self):
        """Test identification of arXiv IDs in new format (YYMM.NNNN)."""
        arxiv_new = [
            "2112.00006",
            "2301.12345", 
            "1907.12345",
            "2201.04502"
        ]
        
        for key in arxiv_new:
            with self.subTest(key=key):
                key_type = self.identifier.identify_key_type(key)
                self.assertEqual(key_type, KeyType.ARXIV,
                               f"Key '{key}' should be identified as arXiv ID")
    
    def test_arxiv_old_format(self):
        """Test identification of arXiv IDs in old format (subject-class/YYMMnnn)."""
        arxiv_old = [
            "hep-th/9803103",
            "astro-ph/0605709",
            "gr-qc/0506127"
        ]
        
        for key in arxiv_old:
            with self.subTest(key=key):
                key_type = self.identifier.identify_key_type(key)
                self.assertEqual(key_type, KeyType.ARXIV,
                               f"Key '{key}' should be identified as arXiv ID")
    
    def test_arxiv_with_versions(self):
        """Test identification of arXiv IDs with version numbers."""
        arxiv_versioned = [
            "2112.00006v1",
            "2301.12345v2", 
            "1907.12345v3"
        ]
        
        for key in arxiv_versioned:
            with self.subTest(key=key):
                key_type = self.identifier.identify_key_type(key)
                self.assertEqual(key_type, KeyType.ARXIV,
                               f"Key '{key}' should be identified as arXiv ID with version")
    
    def test_arxiv_with_prefix(self):
        """Test identification of arXiv IDs with 'arXiv:' prefix."""
        arxiv_prefixed = [
            "arXiv:2112.00006",
            "arXiv:hep-th/9803103",
            "arXiv:2301.12345v1"
        ]
        
        for key in arxiv_prefixed:
            with self.subTest(key=key):
                key_type = self.identifier.identify_key_type(key)
                self.assertEqual(key_type, KeyType.ARXIV,
                               f"Key '{key}' should be identified as arXiv ID with prefix")
    
    def test_unknown_keys(self):
        """Test identification of unknown/invalid citation keys."""
        unknown_keys = [
            "unknown_key_123",
            "some_unknown_paper", 
            "another_missing_ref",
            "mystery_citation_2023",
            "weird_key_format",
            "not-a-valid-format",
            "123abc456",
            "random_string_2023",
            "test_paper_2023",
            "some-paper-2022",
            "unknown_complicated_key_with_numbers_123_xyz"
        ]
        
        for key in unknown_keys:
            with self.subTest(key=key):
                key_type = self.identifier.identify_key_type(key)
                self.assertEqual(key_type, KeyType.UNKNOWN,
                               f"Key '{key}' should be identified as unknown")
    
    def test_edge_cases(self):
        """Test edge cases and malformed citations."""
        # Empty string should be unknown
        self.assertEqual(self.identifier.identify_key_type(""), KeyType.UNKNOWN)
        
        # Whitespace should be handled
        self.assertEqual(self.identifier.identify_key_type(" 1724847 "), KeyType.INSPIREHEP)
        self.assertEqual(self.identifier.identify_key_type("  arXiv:2112.00006  "), KeyType.ARXIV)
    
    def test_normalize_key(self):
        """Test key normalization functionality."""
        # arXiv prefix removal
        self.assertEqual(self.identifier.normalize_key("arXiv:2112.00006"), "2112.00006")
        self.assertEqual(self.identifier.normalize_key("arXiv:hep-th/9803103"), "hep-th/9803103")
        
        # No change for non-prefixed keys
        self.assertEqual(self.identifier.normalize_key("1724847"), "1724847")
        self.assertEqual(self.identifier.normalize_key("Dumitrescu:2025vfp"), "Dumitrescu:2025vfp")
        
        # Whitespace handling
        self.assertEqual(self.identifier.normalize_key(" 1724847 "), "1724847")
    
    def test_process_keys_categorization(self):
        """Test the complete key processing and categorization."""
        test_keys = [
            "1724847",                    # InspireHEP ID
            "Dumitrescu:2025vfp",        # InspireHEP BibTeX
            "2112.00006",                # arXiv new
            "hep-th/9803103",            # arXiv old  
            "arXiv:2301.12345v1",        # arXiv with prefix and version
            "unknown_key_123",           # Unknown
            "796859",                    # InspireHEP ID
            "Carleo:2019ptp",            # InspireHEP BibTeX
            "mystery_citation_2023"      # Unknown
        ]
        
        result = self.identifier.process_keys(test_keys)
        
        # Check that all categories exist
        self.assertIn('inspirehep', result)
        self.assertIn('inspirehep_bibtex', result)
        self.assertIn('arxiv', result)
        self.assertIn('unknown', result)
        
        # Check specific categorizations
        self.assertIn("1724847", result['inspirehep'])
        self.assertIn("796859", result['inspirehep'])
        
        self.assertIn("Dumitrescu:2025vfp", result['inspirehep_bibtex'])
        self.assertIn("Carleo:2019ptp", result['inspirehep_bibtex'])
        
        self.assertIn("2112.00006", result['arxiv'])
        self.assertIn("hep-th/9803103", result['arxiv'])
        self.assertIn("2301.12345v1", result['arxiv'])  # Normalized (prefix removed)
        
        self.assertIn("unknown_key_123", result['unknown'])
        self.assertIn("mystery_citation_2023", result['unknown'])
        
        # Check counts
        self.assertEqual(len(result['inspirehep']), 2)
        self.assertEqual(len(result['inspirehep_bibtex']), 2)
        self.assertEqual(len(result['arxiv']), 3)
        self.assertEqual(len(result['unknown']), 2)
    
    def test_bibtex_key_pattern_validation(self):
        """Test specific patterns for BibTeX key validation."""
        # Valid patterns
        valid_bibtex = [
            "Author:2023abc",
            "Smith:2020xyz", 
            "VanDer:2021def",
            "Author123:2024ghi"
        ]
        
        for key in valid_bibtex:
            with self.subTest(key=key):
                self.assertEqual(self.identifier.identify_key_type(key), KeyType.INSPIREHEP_BIBTEX)
        
        # Invalid patterns (should be unknown)
        invalid_bibtex = [
            "Author:202abc",      # Year too short
            "Author:20233abc",    # Year too long
            "Author:2023ab",      # Suffix too short
            "Author:2023abcd",    # Suffix too long
            "123Author:2023abc",  # Starts with number
            ":2023abc",          # No author
            "Author:abc"         # No year
        ]
        
        for key in invalid_bibtex:
            with self.subTest(key=key):
                self.assertEqual(self.identifier.identify_key_type(key), KeyType.UNKNOWN)


if __name__ == '__main__':
    unittest.main()