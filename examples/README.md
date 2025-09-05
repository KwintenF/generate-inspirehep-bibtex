# Test Examples

This directory contains test cases for the InspireHEP BibTeX Generator.

## Structure

- `tex_files/` - Input LaTeX files for testing
- `expected_outputs/` - Expected BibTeX output files (generated after testing)

## Test Cases

### 1. `basic_paper.tex`
**Purpose**: Test basic functionality with clean, valid citations.

**Features**:
- Mix of InspireHEP record IDs and arXiv IDs (old/new format)
- Contains `\bibliography{physics_refs}` command
- Single citations per `\cite{}` command
- All keys should be identifiable and found in InspireHEP

**Expected Citations**:
- `1724847` (InspireHEP ID)
- `2112.00006` (arXiv new format)
- `796859` (InspireHEP ID) 
- `hep-th/9803103` (arXiv old format)
- `2301.12345` (arXiv new format)
- `1450044` (InspireHEP ID)

### 2. `mixed_citations.tex`
**Purpose**: Test comprehensive citation handling with some unknown keys.

**Features**:
- Multiple citations per `\cite{}` command
- Mix of valid and invalid citation keys
- No `\bibliography{}` command (tests default naming)
- arXiv IDs with `arXiv:` prefix

**Expected Behavior**:
- Should identify and fetch valid citations
- Should warn about unknown keys: `unknown_key_123`, `some_unknown_paper`, etc.
- Should use default filename `references.bib`

### 3. `edge_cases.tex`
**Purpose**: Stress test with problematic and edge-case citations.

**Features**:
- arXiv IDs with version numbers (`v1`, `v2`, etc.)
- arXiv IDs with explicit `arXiv:` prefix
- Malformed/empty citations
- Whitespace and formatting issues
- Multiple `\bibliography{}` commands

**Expected Behavior**:
- Should handle version numbers correctly
- Should ignore empty citations
- Should warn about malformed keys
- Should use first `\bibliography{}` command found

### 4. `bibtex_keys.tex`
**Purpose**: Test InspireHEP BibTeX key format citations.

**Features**:
- InspireHEP BibTeX keys in Author:YEARxxx format
- Mix of BibTeX keys with other citation types
- Some fake BibTeX keys to test warnings

**Expected Citations**:
- `Dumitrescu:2025vfp` (InspireHEP BibTeX key)
- `Carleo:2019ptp` (InspireHEP BibTeX key)
- `Preskill:2018fag` (InspireHEP BibTeX key)
- `Biamonte:2017zfb` (InspireHEP BibTeX key)
- Mixed with arXiv IDs and InspireHEP record IDs

## Usage

To test manually:
1. Start the application: `python main.py`
2. Upload one of the test files
3. Compare output with expected behavior
4. Check for proper error handling and warnings

## Citation Key Types

The test files include examples of:

- **InspireHEP IDs**: `1724847`, `796859`, `1450044`
- **InspireHEP BibTeX keys**: `Dumitrescu:2025vfp`, `Carleo:2019ptp`, `Preskill:2018fag`
- **arXiv (new)**: `2112.00006`, `2301.12345`, `1907.12345`
- **arXiv (old)**: `hep-th/9803103`, `astro-ph/0605709`, `gr-qc/0506127`
- **arXiv with prefix**: `arXiv:2112.00006`, `arXiv:hep-th/9803103`
- **With versions**: `2112.00006v1`, `2301.12345v2`
- **Unknown/Invalid**: `unknown_key_123`, `not-a-valid-format`, `random_string_2023`