import requests
import json
from typing import Optional, List, Dict
import time

class InspireHEPClient:
    def __init__(self):
        self.base_url = "https://inspirehep.net/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'BibTeX-Generator/1.0'
        })
    
    def get_bibtex_by_inspirehep_id(self, inspirehep_id: str) -> Optional[str]:
        """Fetch BibTeX entry by InspireHEP record ID."""
        url = f"{self.base_url}/literature/{inspirehep_id}"
        
        try:
            response = self.session.get(url, params={'format': 'bibtex'})
            
            if response.status_code == 200:
                # InspireHEP returns BibTeX in the response body when format=bibtex
                return response.text
            elif response.status_code == 404:
                print(f"Warning: InspireHEP record {inspirehep_id} not found")
                return None
            else:
                print(f"Error fetching {inspirehep_id}: HTTP {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"Network error fetching {inspirehep_id}: {str(e)}")
            return None
    
    def search_by_arxiv(self, arxiv_id: str) -> Optional[str]:
        """Search for a paper by arXiv ID and return BibTeX."""
        # Clean arXiv ID
        if arxiv_id.startswith('arXiv:'):
            arxiv_id = arxiv_id[6:]
        
        url = f"{self.base_url}/literature"
        
        try:
            # Search for the arXiv paper
            response = self.session.get(url, params={
                'q': f'eprint:{arxiv_id}',
                'format': 'json'
            })
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except (ValueError, json.JSONDecodeError) as e:
                    print(f"Error parsing JSON response for arXiv {arxiv_id}: {str(e)}")
                    return None
                    
                hits = data.get('hits', {}).get('hits', [])
                
                if hits:
                    # Get the first result's record ID
                    record_id = hits[0]['id']
                    # Fetch BibTeX for this record
                    return self.get_bibtex_by_inspirehep_id(str(record_id))
                else:
                    print(f"Warning: arXiv paper {arxiv_id} not found in InspireHEP")
                    return None
            else:
                print(f"Error searching for arXiv {arxiv_id}: HTTP {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"Network error searching for {arxiv_id}: {str(e)}")
            return None
    
    def search_by_bibtex_key(self, bibtex_key: str) -> Optional[str]:
        """Search for a paper by BibTeX key (e.g., Dumitrescu:2025vfp) and return BibTeX."""
        url = f"{self.base_url}/literature"
        
        try:
            # Search for the BibTeX key - InspireHEP supports searching by texkey
            response = self.session.get(url, params={
                'q': f'texkeys:"{bibtex_key}"',
                'format': 'json'
            })
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except (ValueError, json.JSONDecodeError) as e:
                    print(f"Error parsing JSON response for BibTeX key {bibtex_key}: {str(e)}")
                    return None
                    
                hits = data.get('hits', {}).get('hits', [])
                
                if hits:
                    # Get the first result's record ID
                    record_id = hits[0]['id']
                    # Fetch BibTeX for this record
                    return self.get_bibtex_by_inspirehep_id(str(record_id))
                else:
                    print(f"Warning: BibTeX key {bibtex_key} not found in InspireHEP")
                    return None
            else:
                print(f"Error searching for BibTeX key {bibtex_key}: HTTP {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"Network error searching for {bibtex_key}: {str(e)}")
            return None
    
    def fetch_bibtex_entries(self, categorized_keys: dict) -> Dict[str, str]:
        """Fetch BibTeX entries for all categorized keys."""
        bibtex_entries = {}
        
        # Process InspireHEP IDs
        for inspirehep_id in categorized_keys.get('inspirehep', []):
            print(f"Fetching InspireHEP record {inspirehep_id}...")
            bibtex = self.get_bibtex_by_inspirehep_id(inspirehep_id)
            if bibtex:
                bibtex_entries[inspirehep_id] = bibtex
            time.sleep(0.1)  # Be nice to the API
        
        # Process InspireHEP BibTeX keys
        for bibtex_key in categorized_keys.get('inspirehep_bibtex', []):
            print(f"Searching for BibTeX key {bibtex_key}...")
            bibtex = self.search_by_bibtex_key(bibtex_key)
            if bibtex:
                bibtex_entries[bibtex_key] = bibtex
            time.sleep(0.1)  # Be nice to the API
        
        # Process arXiv IDs
        for arxiv_id in categorized_keys.get('arxiv', []):
            print(f"Searching for arXiv paper {arxiv_id}...")
            bibtex = self.search_by_arxiv(arxiv_id)
            if bibtex:
                bibtex_entries[arxiv_id] = bibtex
            time.sleep(0.1)  # Be nice to the API
        
        # Report unknown keys
        unknown_keys = categorized_keys.get('unknown', [])
        if unknown_keys:
            print(f"Warning: Could not identify these citation keys: {', '.join(unknown_keys)}")
        
        return bibtex_entries