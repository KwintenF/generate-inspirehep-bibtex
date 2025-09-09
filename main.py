#!/usr/bin/env python3
"""
InspireHEP BibTeX Generator
Main entry point for the application.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.app import create_interface

if __name__ == "__main__":
    print(" Starting InspireHEP BibTeX Generator...")
    print(" Open your browser to: http://127.0.0.1:7860")
    
    interface = create_interface()
    interface.launch(
        share=False,
        server_name="127.0.0.1", 
        server_port=7860,
        show_error=True,
        quiet=False
    )
