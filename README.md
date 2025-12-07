# DocLayout AI: Persona-Driven Document Intelligence

## 1. Project Overview

DocLayout AI is an offline, command-line system designed to automate the process of identifying and ranking relevant sections from PDF documents based on a specific user persona and job-to-be-done (JTBD).

Unlike generic search tools, this system uses a persona-driven approach to determine contextual relevance, producing structured insights in JSON format. It is designed to operate entirely offline on CPU resources, strictly adhering to assignment constraints.

## 2. Technical Implementation Report

As requested for the project evaluation, this section outlines the development phases and architectural design choices.

### Phase 1: Structural Parsing (Heuristic Engine)

- Module: `src/parser.py`
- Logic: Implemented a Heuristic Parser using PyMuPDF. It analyzes font metadata (size, weight, casing) directly from the PDF byte stream to identify headings and structural boundaries.
- Benefit: This approach allows for near-instantaneous structure extraction without GPU acceleration.

### Phase 2: Semantic Relevance (NLP Engine)

- Module: `src/ranking.py`
- Logic: Utilizes sentence-transformer embeddings (e.g., `intfloat/e5-small-v2`). The engine generates embeddings for the user persona/query and compares them against document headings using cosine similarity.
- Benefit: Captures the intent of the persona (e.g., "HR Professional") rather than just matching text strings.

### Phase 3: Output Generation

- Module: `src/output.py`
- Logic: The system compiles the top-ranked results into a standardized JSON schema containing metadata, ranked sections, and refined content snippets, facilitating downstream integration.

## 3. Installation & Setup

### Prerequisites

- Python 3.8 or higher
- No GPU required (CPU compatible)

### Setup Steps

1. Clone the repository (or unzip the project folder).
2. Navigate to the project root:
   ```bash
   cd DocLayoutAI-Assignment
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Data Setup

Ensure your PDF files are located in the `data/` directory as configured in `config.json`.

## 4. How to Run the Application

The application supports two modes of operation: an Interactive Mode (menu-driven) and a CLI Mode (manual arguments).

### Option A: Interactive Mode (Recommended)

This mode reads from `config.json` and presents a menu to select pre-configured collections.

Command:
```bash
python -m src.interactive_runner
```

The script will list available collections (e.g., Collection 1, Collection 2). Enter the number of the collection you wish to process. Results are automatically saved to the `output/` folder defined in the config.

### Option B: CLI Mode (Manual)

Use this mode to run the tool on a specific folder with custom arguments.

Command Syntax:
```bash
python -m src.main -i <INPUT_DIR> -p <PERSONA> -j <JOB_QUERY> -o <OUTPUT_PATH>
```

Example:
```bash
python -m src.main -i "./data/Collection 1/PDFs" -p "Travel Planner" -j "Find travel destinations" -o "./output/manual_result.json"
```

Arguments:
- `-i`: Path to the folder containing PDF files.
- `-p`: User persona description (e.g., "Data Scientist").
- `-j`: Job-to-be-done or query string.
- `-o`: Path where the output JSON file will be saved.

## 5. Testing Instructions

The project includes a comprehensive test suite covering Unit Tests (logic verification) and Integration Tests (full pipeline verification).

### Run All Tests (Recommended)
```bash
python -m unittest discover tests
```

### Run Specific Test Scripts

1. Test Heuristic Parser Logic (verifies header vs paragraph detection):
```bash
python -m unittest tests/test_parser.py
```

2. Test Utility Functions:
```bash
python -m unittest tests/test_utils.py
```

3. Test Full Pipeline (Integration) — runs the pipeline on a sample PDF:
```bash
python -m unittest tests/test_integration.py
```

## 6. Directory Structure

```
DocLayoutAI-Assignment/
├── config.json                 # Configuration for Interactive Mode
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation & Report
├── run_tests.bat               # One-click test script (Windows)
├── data/                       # Document collections
│   ├── Collection 1/
│   │   └── PDFs/               
│   └── ...
├── src/                        # Source Code
│   ├── main.py                 # CLI Entry point
│   ├── interactive_runner.py   # Interactive Entry point
│   ├── parser.py               # Heuristic PDF parsing logic
│   ├── ranking.py              # Semantic NLP ranking logic
│   ├── output.py               # JSON formatter
│   └── utils.py                # Helper functions
└── tests/                      # Test Suite
    ├── test_parser.py          # Unit tests for parser
    ├── test_utils.py           # Unit tests for utilities
    ├── test_integration.py     # End-to-end pipeline tests
    └── test_data/              # Contains sample.pdf for testing
```
