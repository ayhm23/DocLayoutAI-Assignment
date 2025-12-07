import unittest
from src.parser import PDFParser

class TestParserLogic(unittest.TestCase):
    def setUp(self):
        self.parser = PDFParser()

    def test_heuristic_identification_bold(self):
        mock_span = {
            "text": "Chapter One",
            "size": 12.0, "flags": 0, "font": "Arial-Bold",
            "page_width": 600, "x0": 50, "x1": 150
        }
        reasons = self.parser._evaluate_heading_heuristics(
            "Chapter One", 12.0, mock_span, 10.0, 400
        )
        self.assertIn("Bold", reasons)

    def test_heuristic_identification_large_size(self):
        mock_span = {
            "text": "Introduction",
            "size": 15.0, "flags": 0, "font": "Arial",
            "page_width": 600, "x0": 50, "x1": 150
        }
        reasons = self.parser._evaluate_heading_heuristics(
            "Introduction", 15.0, mock_span, 10.0, 400
        )
        self.assertIn("Larger font", reasons)

    def test_heuristic_rejection_normal_text(self):
        # Update: Make the text explicitly Left-Aligned to avoid "Centered" detection
        mock_span = {
            "text": "Just some normal sentence text.",
            "size": 10.0, 
            "flags": 0,
            "font": "Arial",
            "page_width": 600,
            "x0": 50, "x1": 300 # Left aligned (Right margin is 300px, Left is 50px)
        }
        reasons = self.parser._evaluate_heading_heuristics(
            "Just some normal sentence text.", 10.0, mock_span, 10.0, 400
        )
        self.assertEqual(reasons, [])

if __name__ == '__main__':
    unittest.main()