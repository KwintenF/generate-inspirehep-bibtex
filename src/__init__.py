"""
InspireHEP BibTeX Generator

A tool to extract citations from LaTeX files and generate BibTeX files using InspireHEP API.
"""

from .latex_parser import LaTeXParser
from .key_identifier import KeyIdentifier, KeyType
from .inspirehep_client import InspireHEPClient
from .bibtex_manager import BibTeXManager
from .app import BibTeXGeneratorApp, create_interface

__version__ = "1.0.0"
__author__ = "InspireHEP BibTeX Generator"

__all__ = [
    "LaTeXParser",
    "KeyIdentifier", 
    "KeyType",
    "InspireHEPClient",
    "BibTeXManager",
    "BibTeXGeneratorApp",
    "create_interface"
]