import unittest
from unittest.mock import MagicMock, patch
from src.ranking import RankingEngine

class TestRanking(unittest.TestCase):

    @patch('src.ranking.util')  # Mock the calculator
    @patch('src.ranking.SentenceTransformer') # Mock the AI model
    def test_rank_candidates_sorting(self, MockModel, MockUtil):
        # 1. Setup - Create the engine (Mocks prevent downloading 1GB model)
        engine = RankingEngine()
        
        # 2. Input Data - Two candidates
        candidates = [
            {"text": "Bad Match", "page_num": 1, "y": 10},
            {"text": "Good Match", "page_num": 2, "y": 20}
        ]
        
        # 3. Mock the Math (The tricky part)
        # We force the math function to say: Index 1 is best (0.9), Index 0 is worst (0.1)
        mock_scores = MagicMock()
        mock_scores.topk.return_value.indices = [1, 0] # Order: Index 1, then Index 0
        mock_scores.topk.return_value.values = [0.9, 0.1]
        
        # Tell the system: "When cos_sim is called, return our fake scores"
        # We use [0] because the real code does [0] to get the first batch
        MockUtil.cos_sim.return_value = [mock_scores] 

        # 4. Run the actual method
        results = engine.rank_candidates(candidates, "fake query")
        
        # 5. Assert - Did it sort correctly?
        # The first result should be "Good Match" (because we gave it 0.9 score)
        self.assertEqual(results[0]["text"], "Good Match")
        self.assertEqual(results[0]["score"], 0.9)
        
        # The second result should be "Bad Match"
        self.assertEqual(results[1]["text"], "Bad Match")

    def test_empty_candidates(self):
        # This checks if the code crashes on empty input
        with patch('src.ranking.SentenceTransformer'):
            engine = RankingEngine()
            result = engine.rank_candidates([], "query")
            self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()