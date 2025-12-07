import argparse
import os
import glob
from src.parser import PDFParser
from src.ranking import RankingEngine
from src.output import OutputGenerator  # Updated import to match src/output.py

def main():
    # 1. Setup CLI Arguments
    parser = argparse.ArgumentParser(description="DocLayout AI - Assignment CLI")
    parser.add_argument('-i', '--input', required=True, help="Folder containing PDF files")
    parser.add_argument('-o', '--output', required=True, help="Path to save output JSON file")
    parser.add_argument('-p', '--persona', required=True, help="User Persona (e.g., 'Data Scientist')")
    parser.add_argument('-j', '--job', required=True, help="Job to be done (Query string)")
    
    args = parser.parse_args()

    # 2. Validate Input
    pdf_files = glob.glob(os.path.join(args.input, "*.pdf"))
    if not pdf_files:
        print(f"Error: No PDF files found in '{args.input}'")
        return

    print(f"Processing {len(pdf_files)} documents...")
    print(f"Persona: {args.persona}")
    print(f"Query: {args.job}")

    # 3. Initialize Modules
    # Note: These classes are now imported from your new modular src/ folder
    pdf_parser = PDFParser()
    ranker = RankingEngine() 
    
    formatter = OutputGenerator(
        [os.path.basename(p) for p in pdf_files], 
        args.persona, 
        args.job
    )

    # 4. Execution Loop
    for pdf_path in pdf_files:
        print(f"\nScanning: {os.path.basename(pdf_path)}...")
        
        try:
            # A. Parse Candidates (Heuristic)
            # Updated method name to match src/parser.py
            candidates = pdf_parser.extract_candidates(pdf_path)
            print(f"  -> Found {len(candidates)} structural candidates")

            if not candidates:
                continue

            # B. Rank Candidates (Semantic)
            # Updated method name to match src/ranking.py
            matches = ranker.rank_candidates(candidates, args.job, top_k=10)
            print(f"  -> Identified {len(matches)} relevant sections")

            # C. Extract Content
            sections = pdf_parser.extract_sections(pdf_path, matches)
            
            # D. Add to Results
            for sec in sections:
                formatter.add_result(os.path.basename(pdf_path), sec)
        
        except Exception as e:
            print(f"  X Error processing file: {e}")

    # 5. Finalize and Save
    print("\nGenerating Final JSON...")
    # Ensure directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    formatter.save_json(args.output)
    print("Done.")

if __name__ == "__main__":
    main()