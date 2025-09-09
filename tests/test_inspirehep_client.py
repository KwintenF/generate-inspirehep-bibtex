import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import requests

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from inspirehep_client import InspireHEPClient


class TestInspireHEPClient(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.client = InspireHEPClient()
    
    def test_client_initialization(self):
        """Test that client initializes correctly."""
        self.assertEqual(self.client.base_url, "https://inspirehep.net/api")
        self.assertIsInstance(self.client.session, requests.Session)
        self.assertEqual(
            self.client.session.headers['User-Agent'], 
            'BibTeX-Generator/1.0'
        )
        self.assertEqual(
            self.client.session.headers['Accept'], 
            'application/json'
        )
    
    @patch('inspirehep_client.requests.Session.get')
    def test_get_bibtex_by_inspirehep_id_success(self, mock_get):
        """Test successful BibTeX retrieval by InspireHEP ID."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """@article{Dumitrescu:2025vfp,
    author = "Dumitrescu, Test",
    title = "{Test Paper}",
    journal = "Test Journal",
    year = "2025"
}"""
        mock_get.return_value = mock_response
        
        result = self.client.get_bibtex_by_inspirehep_id("1724847")
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://inspirehep.net/api/literature/1724847",
            params={'format': 'bibtex'}
        )
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertIn("@article", result)
        self.assertIn("Dumitrescu:2025vfp", result)
        self.assertIn("Test Paper", result)
    
    @patch('inspirehep_client.requests.Session.get')
    def test_get_bibtex_by_inspirehep_id_not_found(self, mock_get):
        """Test handling of 404 (record not found)."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            result = self.client.get_bibtex_by_inspirehep_id("999999")
            
            self.assertIsNone(result)
            mock_print.assert_called_with("Warning: InspireHEP record 999999 not found")
    
    @patch('inspirehep_client.requests.Session.get')
    def test_get_bibtex_by_inspirehep_id_server_error(self, mock_get):
        """Test handling of server errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            result = self.client.get_bibtex_by_inspirehep_id("1724847")
            
            self.assertIsNone(result)
            mock_print.assert_called_with("Error fetching 1724847: HTTP 500")
    
    @patch('inspirehep_client.requests.Session.get')
    def test_get_bibtex_by_inspirehep_id_network_error(self, mock_get):
        """Test handling of network errors."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        with patch('builtins.print') as mock_print:
            result = self.client.get_bibtex_by_inspirehep_id("1724847")
            
            self.assertIsNone(result)
            mock_print.assert_called_with("Network error fetching 1724847: Network error")
    
    @patch('inspirehep_client.requests.Session.get')
    def test_search_by_arxiv_success(self, mock_get):
        """Test successful arXiv paper search."""
        # Mock search response
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'hits': {
                'hits': [
                    {'id': 1234567}
                ]
            }
        }
        
        # Mock BibTeX response
        bibtex_response = Mock()
        bibtex_response.status_code = 200
        bibtex_response.text = """@article{Author:2021abc,
    title = "{Test arXiv Paper}",
    eprint = "2112.00006"
}"""
        
        # Configure mock to return different responses for different calls
        mock_get.side_effect = [search_response, bibtex_response]
        
        result = self.client.search_by_arxiv("2112.00006")
        
        # Verify search request
        self.assertEqual(mock_get.call_count, 2)
        search_call = mock_get.call_args_list[0]
        self.assertEqual(search_call[0][0], "https://inspirehep.net/api/literature")
        self.assertEqual(search_call[1]['params']['q'], "eprint:2112.00006")
        
        # Verify BibTeX request
        bibtex_call = mock_get.call_args_list[1]
        self.assertEqual(bibtex_call[0][0], "https://inspirehep.net/api/literature/1234567")
        
        self.assertIsNotNone(result)
        self.assertIn("Test arXiv Paper", result)
        self.assertIn("2112.00006", result)
    
    @patch('inspirehep_client.requests.Session.get')
    def test_search_by_arxiv_with_prefix(self, mock_get):
        """Test arXiv search with 'arXiv:' prefix removal."""
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {'hits': {'hits': [{'id': 1234567}]}}
        
        bibtex_response = Mock()
        bibtex_response.status_code = 200
        bibtex_response.text = "@article{test}"
        
        mock_get.side_effect = [search_response, bibtex_response]
        
        result = self.client.search_by_arxiv("arXiv:2112.00006")
        
        # Verify that prefix was removed in search
        search_call = mock_get.call_args_list[0]
        self.assertEqual(search_call[1]['params']['q'], "eprint:2112.00006")
    
    @patch('inspirehep_client.requests.Session.get')
    def test_search_by_arxiv_not_found(self, mock_get):
        """Test arXiv search when paper is not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'hits': {'hits': []}}
        mock_get.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            result = self.client.search_by_arxiv("9999.99999")
            
            self.assertIsNone(result)
            mock_print.assert_called_with("Warning: arXiv paper 9999.99999 not found in InspireHEP")
    
    @patch('inspirehep_client.requests.Session.get')
    def test_search_by_bibtex_key_success(self, mock_get):
        """Test successful BibTeX key search."""
        # Mock search response
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'hits': {
                'hits': [
                    {'id': 1234567}
                ]
            }
        }
        
        # Mock BibTeX response
        bibtex_response = Mock()
        bibtex_response.status_code = 200
        bibtex_response.text = """@article{Dumitrescu:2025vfp,
    author = "Dumitrescu, Test",
    title = "{Test Paper}"
}"""
        
        mock_get.side_effect = [search_response, bibtex_response]
        
        result = self.client.search_by_bibtex_key("Dumitrescu:2025vfp")
        
        # Verify search request
        search_call = mock_get.call_args_list[0]
        self.assertEqual(search_call[1]['params']['q'], 'texkeys:"Dumitrescu:2025vfp"')
        
        self.assertIsNotNone(result)
        self.assertIn("Dumitrescu:2025vfp", result)
    
    @patch('inspirehep_client.requests.Session.get')
    def test_search_by_bibtex_key_not_found(self, mock_get):
        """Test BibTeX key search when not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'hits': {'hits': []}}
        mock_get.return_value = mock_response
        
        with patch('builtins.print') as mock_print:
            result = self.client.search_by_bibtex_key("NonExistent:2023abc")
            
            self.assertIsNone(result)
            mock_print.assert_called_with("Warning: BibTeX key NonExistent:2023abc not found in InspireHEP")
    
    @patch('inspirehep_client.InspireHEPClient.get_bibtex_by_inspirehep_id')
    @patch('inspirehep_client.InspireHEPClient.search_by_bibtex_key')
    @patch('inspirehep_client.InspireHEPClient.search_by_arxiv')
    @patch('inspirehep_client.time.sleep')  # Mock sleep to speed up tests
    def test_fetch_bibtex_entries_complete(self, mock_sleep, mock_arxiv, mock_bibtex_key, mock_inspirehep):
        """Test complete BibTeX entries fetching workflow."""
        # Setup return values
        mock_inspirehep.return_value = "@article{inspirehep_entry}"
        mock_bibtex_key.return_value = "@article{bibtex_key_entry}"
        mock_arxiv.return_value = "@article{arxiv_entry}"
        
        categorized_keys = {
            'inspirehep': ['1724847', '796859'],
            'inspirehep_bibtex': ['Dumitrescu:2025vfp', 'Carleo:2019ptp'],
            'arxiv': ['2112.00006', 'hep-th/9803103'],
            'unknown': ['unknown_key_123']
        }
        
        with patch('builtins.print') as mock_print:
            result = self.client.fetch_bibtex_entries(categorized_keys)
        
        # Verify all methods were called with correct arguments
        mock_inspirehep.assert_any_call('1724847')
        mock_inspirehep.assert_any_call('796859')
        mock_bibtex_key.assert_any_call('Dumitrescu:2025vfp')
        mock_bibtex_key.assert_any_call('Carleo:2019ptp')
        mock_arxiv.assert_any_call('2112.00006')
        mock_arxiv.assert_any_call('hep-th/9803103')
        
        # Verify sleep was called (rate limiting)
        self.assertEqual(mock_sleep.call_count, 6)  # One for each successful fetch
        
        # Verify results
        self.assertEqual(len(result), 6)  # All successful fetches
        self.assertIn('1724847', result)
        self.assertIn('Dumitrescu:2025vfp', result)
        self.assertIn('2112.00006', result)
        
        # Verify warning for unknown keys
        mock_print.assert_called_with("Warning: Could not identify these citation keys: unknown_key_123")
    
    @patch('inspirehep_client.InspireHEPClient.get_bibtex_by_inspirehep_id')
    @patch('inspirehep_client.time.sleep')
    def test_fetch_bibtex_entries_partial_success(self, mock_sleep, mock_inspirehep):
        """Test fetching with some failures."""
        # First call succeeds, second fails
        mock_inspirehep.side_effect = ["@article{success}", None]
        
        categorized_keys = {
            'inspirehep': ['1724847', '999999'],
            'inspirehep_bibtex': [],
            'arxiv': [],
            'unknown': []
        }
        
        result = self.client.fetch_bibtex_entries(categorized_keys)
        
        # Only successful entry should be in results
        self.assertEqual(len(result), 1)
        self.assertIn('1724847', result)
        self.assertNotIn('999999', result)
    
    def test_fetch_bibtex_entries_empty_input(self):
        """Test fetching with empty categorized keys."""
        categorized_keys = {
            'inspirehep': [],
            'inspirehep_bibtex': [],
            'arxiv': [],
            'unknown': []
        }
        
        result = self.client.fetch_bibtex_entries(categorized_keys)
        
        self.assertEqual(len(result), 0)
        self.assertEqual(result, {})
    
    @patch('inspirehep_client.requests.Session.get')
    def test_malformed_json_response(self, mock_get):
        """Test handling of malformed JSON responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        result = self.client.search_by_arxiv("2112.00006")
        
        # Should handle JSON parsing error gracefully
        self.assertIsNone(result)
    
    @patch('inspirehep_client.requests.Session.get')
    def test_unexpected_response_structure(self, mock_get):
        """Test handling of unexpected API response structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'unexpected': 'structure'
        }  # Missing 'hits' key
        mock_get.return_value = mock_response
        
        result = self.client.search_by_arxiv("2112.00006")
        
        # Should handle missing keys gracefully
        self.assertIsNone(result)
    
    def test_rate_limiting_integration(self):
        """Test that rate limiting (sleep) is applied correctly."""
        with patch('inspirehep_client.time.sleep') as mock_sleep, \
             patch('inspirehep_client.InspireHEPClient.get_bibtex_by_inspirehep_id') as mock_get:
            
            mock_get.return_value = "@article{test}"
            
            categorized_keys = {
                'inspirehep': ['1', '2', '3'],
                'inspirehep_bibtex': [],
                'arxiv': [],
                'unknown': []
            }
            
            self.client.fetch_bibtex_entries(categorized_keys)
            
            # Should sleep after each successful fetch
            self.assertEqual(mock_sleep.call_count, 3)
            mock_sleep.assert_called_with(0.1)


class TestInspireHEPClientIntegration(unittest.TestCase):
    """
    Integration tests that make real API calls.
    These can be skipped if network is unavailable.
    """
    
    def setUp(self):
        self.client = InspireHEPClient()
        # Skip integration tests if we don't want to make real API calls
        self.skip_integration = os.getenv('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true'
    
    def test_real_inspirehep_id_fetch(self):
        """Test fetching a real InspireHEP record (if integration tests enabled)."""
        if self.skip_integration:
            self.skipTest("Integration tests disabled")
        
        # Use a known stable InspireHEP record ID
        result = self.client.get_bibtex_by_inspirehep_id("1724847")
        
        if result is not None:  # Record might not exist anymore
            self.assertIn("@", result)  # Should be BibTeX format
            self.assertTrue(len(result) > 100)  # Should have substantial content
    
    def test_real_arxiv_search(self):
        """Test searching for a real arXiv paper (if integration tests enabled)."""
        if self.skip_integration:
            self.skipTest("Integration tests disabled")
        
        # Use a known arXiv ID that should be in InspireHEP
        result = self.client.search_by_arxiv("2112.00006")
        
        if result is not None:
            self.assertIn("@", result)
            self.assertIn("2112.00006", result.lower())


if __name__ == '__main__':
    # Set environment variable to skip integration tests by default
    os.environ.setdefault('SKIP_INTEGRATION_TESTS', 'true')
    unittest.main()