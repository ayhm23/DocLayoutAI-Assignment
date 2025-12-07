import unittest
import os
import json
from src.parser import PDFParser
from src.ranking import RankingEngine
from src.output import OutputGenerator

class TestIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # This runs once before all tests
        cls.test_pdf_path = "tests/test_data/sample.pdf"
        cls.output_path = "tests/test_data/test_output.json"
        
        # Ensure directory exists
        os.makedirs("tests/test_data", exist_ok=True)
        
        # Check if user provided the sample PDF
        if not os.path.exists(cls.test_pdf_path):
            raise unittest.SkipTest("Skipping Integration Test: 'tests/test_data/sample.pdf' not found.")

    def test_full_pipeline(self):
        # 1. Initialize
        parser = PDFParser()
        ranker = RankingEngine() # This will download model if missing (Acceptable for Integration Test)
        
        # 2. Parse
        print("\n[Integration] Parsing PDF...")
        candidates = parser.extract_candidates(self.test_pdf_path)
        self.assertIsInstance(candidates, list)
        # We assume the sample PDF has at least one detectable header
        if len(candidates) == 0:
            print("Warning: No candidates found in sample PDF. Is it an image scan?")
        
        # 3. Rank
        print("[Integration] Ranking...")
        query = "summary introduction conclusion" # Generic query
        matches = ranker.rank_candidates(candidates, query, top_k=3)
        self.assertLessEqual(len(matches), 3)
        
        # 4. Extract Content
        print("[Integration] Extracting Content...")
        sections = parser.extract_sections(self.test_pdf_path, matches)
        self.assertEqual(len(sections), len(matches))
        
        # 5. Output
        print("[Integration] Generating JSON...")
        formatter = OutputGenerator(["sample.pdf"], "Tester", "Integration Test")
        for sec in sections:
            formatter.add_result("sample.pdf", sec)
            
        formatter.save_json(self.output_path)
        
        # 6. Verify File Created
        self.assertTrue(os.path.exists(self.output_path))
        
        # 7. Cleanup
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

if __name__ == '__main__':
    unittest.main()