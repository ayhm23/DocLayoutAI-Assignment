import unittest
from src.utils import clean_text, is_all_upper, is_title_case, is_bold_font

class TestUtils(unittest.TestCase):

    def test_clean_text_basics(self):
        # Test basic whitespace removal
        raw = "  Hello   World  \n "
        self.assertEqual(clean_text(raw), "Hello World")

    def test_clean_text_binary_protection(self):
        # Test that binary garbage returns empty string
        binary_garbage = "\x00\x01\x02\x03"
        self.assertEqual(clean_text(binary_garbage), "")

    def test_clean_text_truncation(self):
        # Test "Smart Truncation": It should stop at the next period after max_words
        
        # Scenario: 10 words limit. We provide 10 words, then "stop.", then more words.
        # "word " * 10 generates 10 words. "stop." is the 11th.
        long_text = ("word " * 10) + "stop. " + ("more " * 50)
        
        cleaned = clean_text(long_text, max_words=10)
        
        # Logic check:
        # 1. Takes first 10 words (prefix).
        # 2. Looks at suffix ("stop.", "more"...).
        # 3. Finds "stop." immediately. Stops there.
        # Total: 10 words + "stop." = 11 words.
        
        self.assertEqual(len(cleaned.split()), 11)
        self.assertTrue(cleaned.endswith("stop."))

    def test_clean_text_no_period_fallback(self):
        # Test what happens if there are NO periods (infinite sentence)
        # Your logic appends " ..." at the very end
        long_text = "word " * 20
        cleaned = clean_text(long_text, max_words=10)
        
        # Should return all 20 words + "..."
        self.assertTrue(cleaned.endswith("..."))
        self.assertEqual(len(cleaned.split()), 21)

    def test_is_all_upper(self):
        self.assertTrue(is_all_upper("HELLO WORLD"))
        self.assertFalse(is_all_upper("Hello World"))

    def test_is_title_case(self):
        self.assertTrue(is_title_case("The Quick Brown Fox"))
        self.assertFalse(is_title_case("the quick brown fox"))

    def test_is_bold_font(self):
        bold_span_flag = {"flags": 2, "font": "Arial"} 
        bold_span_name = {"flags": 0, "font": "Arial-Bold"}
        normal_span = {"flags": 0, "font": "Arial"}

        self.assertTrue(is_bold_font(bold_span_flag))
        self.assertTrue(is_bold_font(bold_span_name))
        self.assertFalse(is_bold_font(normal_span))

if __name__ == '__main__':
    unittest.main()