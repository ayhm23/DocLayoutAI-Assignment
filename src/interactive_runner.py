import json
import os
import glob
import sys
import time

# Use modular imports (matching your src folder)
from src.parser import PDFParser
from src.ranking import RankingEngine
from src.output import OutputGenerator

def load_config():
    if not os.path.exists("config.json"):
        print("Error: config.json not found in the project root.")
        sys.exit(1)
    with open("config.json", "r") as f:
        return json.load(f)

def process_collection(name, config):
    coll = config["collections"][name]
    settings = config["output_settings"]
    
    input_dir = coll["input_folder"]
    output_dir = settings["output_folder"]
    
    # 1. Validate Input Folder
    if not os.path.exists(input_dir):
        print(f"Error: The folder '{input_dir}' does not exist.")
        print("Check your config.json paths.")
        return

    print(f"\n--- Processing: {name} ---")
    print(f"Goal: {coll['job_to_be_done']}")
    
    # 2. Initialize Modules
    parser = PDFParser()
    ranker = RankingEngine()
    
    pdfs = glob.glob(os.path.join(input_dir, "*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {input_dir}")
        return

    # 3. Setup Output Generator (Uses top_k from config)
    formatter = OutputGenerator(
        [os.path.basename(p) for p in pdfs],
        coll["persona"],
        coll["job_to_be_done"],
        top_k=settings.get("top_k_output", 5)  # Default to 5 if missing
    )

    # 4. Processing Loop
    for pdf in pdfs:
        print(f"Scanning: {os.path.basename(pdf)}...")
        try:
            # A. Parse
            candidates = parser.extract_candidates(pdf)
            
            # B. Rank
            matches = ranker.rank_candidates(
                candidates, 
                coll.get("job_query", coll["job_to_be_done"]),
                top_k=settings.get("top_k_matches", 10)
            )
            
            # C. Extract
            sections = parser.extract_sections(pdf, matches)
            
            # D. Save to memory
            for sec in sections:
                formatter.add_result(os.path.basename(pdf), sec)
                
        except Exception as e:
            print(f"  Error: {e}")

    # 5. Save Final JSON
    os.makedirs(output_dir, exist_ok=True)
    out_filename = f"{name.replace(' ', '_')}_results.json"
    out_path = os.path.join(output_dir, out_filename)
    formatter.save_json(out_path)
    print(f"\nSuccess! Output with Top {settings.get('top_k_output', 5)} saved to:")
    print(out_path)

def main():
    config = load_config()
    collections = list(config["collections"].keys())
    
    print("\n" + "="*40)
    print("   DocLayout AI - Interactive Runner")
    print("="*40)
    
    for i, c in enumerate(collections, 1):
        print(f"{i}. {c}")
        
    choice = input("\nSelect Collection (Number or 'all'): ").strip().lower()
    
    if choice == 'all':
        for c in collections:
            process_collection(c, config)
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(collections):
                process_collection(collections[idx], config)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")

if __name__ == "__main__":
    main()