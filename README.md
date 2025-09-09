# InspireHEP BibTeX Generator

A Python tool that automatically extracts citations from LaTeX files and generates clean, standardized BibTeX files using the InspireHEP database. The tool handles deduplication, key standardization, and outputs both a cleaned BibTeX file and a standardized LaTeX file.

## Features

- **Multiple Citation Formats**: Supports InspireHEP record IDs, InspireHEP BibTeX keys, and arXiv identifiers
- **Automatic Deduplication**: Detects and removes duplicate entries from different citation formats
- **Key Standardization**: Converts all citation keys to InspireHEP BibTeX format (e.g., `Author:YEARxxx`)
- **LaTeX File Generation**: Creates a new LaTeX file with standardized citation keys
- **Web Interface**: User-friendly Gradio interface for easy file processing
- **Comprehensive Testing**: test suite with unit tests

## Supported Citation Types

| Format | Example | Description |
|--------|---------|-------------|
| InspireHEP Record ID | `\cite{1724847}` | Numeric record identifiers |
| InspireHEP BibTeX Key | `\cite{Dumitrescu:2025vfp}` | Standard BibTeX keys from InspireHEP |
| arXiv (New Format) | `\cite{2301.12345}` | Post-2007 arXiv identifiers |
| arXiv (Old Format) | `\cite{hep-th/9803103}` | Pre-2007 arXiv identifiers |
| arXiv with Prefix | `\cite{arXiv:2301.12345}` | arXiv IDs with explicit prefix |
| arXiv with Version | `\cite{2301.12345v2}` | Versioned arXiv identifiers |

## Installation

### Prerequisites
- Python 3.8+
- Internet connection (for InspireHEP API access)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Packages
- `requests` - For InspireHEP API calls
- `gradio` - interface

## Quick Start

### Command Line Interface
```bash
python main.py
```

This will start the Gradio web interface at `http://127.0.0.1:7860`

### Web Interface Usage
1. Upload your LaTeX file containing `\cite{}` commands
2. Optionally specify an output filename
3. Click "🚀 Generate Files"
4. Download the standardized LaTeX and BibTeX files

## Project Structure

```
generate-inspirehep-bibtex/
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   ├── app.py                   # Gradio web interface
│   ├── latex_parser.py          # LaTeX citation extraction
│   ├── key_identifier.py        # Citation type identification
│   ├── inspirehep_client.py     # InspireHEP API client
│   ├── bibtex_manager.py        # BibTeX file management
│   └── bibtex_processor.py      # Deduplication and standardization
├── tests/                       # Unit tests
│   ├── test_key_identifier.py   # Key identification tests
│   ├── test_latex_parser.py     # LaTeX parsing tests
│   └── test_inspirehep_client.py # API client tests
├── examples/                    # Example files
│   ├── tex_files/               # Sample LaTeX files
│   │   ├── basic_paper.tex
│   │   ├── mixed_citations.tex
│   │   ├── edge_cases.tex
│   │   └── bibtex_keys.tex
│   └── README.md                # Example documentation
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## How It Works

### 1. Citation Extraction
The tool scans your LaTeX file for `\cite{}` commands and extracts all citation keys:
```latex
\cite{1724847,Dumitrescu:2025vfp,arXiv:2301.12345}
```

### 2. Key Classification
Each citation key is classified by type:
- **InspireHEP IDs**: Pure numeric (e.g., `1724847`)
- **InspireHEP BibTeX**: Author:Year format (e.g., `Dumitrescu:2025vfp`)
- **arXiv IDs**: Various arXiv formats (e.g., `2301.12345`, `hep-th/9803103`)

### 3. Data Retrieval
The tool queries the InspireHEP API to fetch BibTeX entries for each citation.

### 4. Deduplication
Duplicate entries are detected and removed based on the standardized BibTeX keys extracted from the fetched entries.

### 5. Standardization
- **BibTeX File**: Contains unique entries with standardized keys
- **LaTeX File**: All citations updated to use standardized keys

## 📊 Example Workflow

**Input LaTeX:**
```latex
\documentclass{article}
\begin{document}
Recent work \cite{1724847} and \cite{arXiv:2301.12345} show that...
The framework in \cite{Dumitrescu:2025vfp} confirms this.
\bibliography{references}
\end{document}
```

**Processing:**
- Detects that `1724847` and `arXiv:2301.12345` refer to the same paper as `Dumitrescu:2025vfp`
- Removes duplicate entries
- Standardizes citation keys

**Output LaTeX:**
```latex
\documentclass{article}
\begin{document}
Recent work \cite{Dumitrescu:2025vfp} and \cite{Dumitrescu:2025vfp} show that...
The framework in \cite{Dumitrescu:2025vfp} confirms this.
\bibliography{references}
\end{document}
```

**Output BibTeX:**
```bibtex
% BibTeX file generated from InspireHEP
@article{Dumitrescu:2025vfp,
    author = "Dumitrescu, Test Author",
    title = "{Example Paper Title}",
    journal = "Test Journal",
    year = "2025"
}
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test files
python tests/test_key_identifier.py
python tests/test_latex_parser.py
python tests/test_inspirehep_client.py
```

### Test Coverage
- **Key Identification**: Tests all citation format recognition
- **LaTeX Parsing**: Tests citation extraction and bibliography detection
- **API Client**: Tests InspireHEP API interactions (with mocking)

## Example Files

The `examples/` directory contains sample LaTeX files for testing:

- **`basic_paper.tex`**: Clean citations with mixed formats
- **`mixed_citations.tex`**: Multiple citations per command, unknown keys
- **`edge_cases.tex`**: Problematic citations, version numbers, formatting issues
- **`bibtex_keys.tex`**: Focus on InspireHEP BibTeX key format

## Configuration

### Environment Variables
- `SKIP_INTEGRATION_TESTS=true`: Skip tests that make real API calls

### API Rate Limiting
The tool includes built-in rate limiting (0.1s delay between API calls) to be respectful to the InspireHEP API.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check the `examples/` directory for usage examples
- **API Reference**: InspireHEP API documentation at https://inspirehep.net/help/api

## Use Cases

- **Academic Writing**: Clean up bibliography management in research papers
- **Collaboration**: Standardize citation formats across team projects
- **Migration**: Convert between different citation management systems
- **Quality Control**: Ensure consistent bibliography formatting

---

**Generated with InspireHEP BibTeX Generator**

*Developed with assistance from Claude (Anthropic)*
