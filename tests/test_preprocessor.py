import unittest
from tools import preprocessor

class TestPreprocessing(unittest.TestCase):
    def test_simple_input(self):
        text = "Hello world. <br> This is a test."
        result = preprocessor.preprocessing(text)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].text, "Hello world.")
        self.assertEqual(result[1].text, "This is a test.")

    def test_paragraphs_and_whitespace(self):
        text = "First sentence.   \n\n   Second sentence.   \n\n\n Third sentence."
        result = preprocessor.preprocessing(text)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].paragraphIndex, 0)
        self.assertEqual(result[1].paragraphIndex, 1)
        self.assertEqual(result[2].paragraphIndex, 2)

    def test_position_indices(self):
        text = "Sentence one. <b> Sentence two."
        result = preprocessor.preprocessing(text)

        self.assertTrue(text[result[0].charStart:result[0].charEnd + 1].startswith("Sentence"))
        self.assertTrue(text[result[1].charStart:result[1].charEnd + 1].startswith("Sentence"))

    def test_complicated_input(self):
        text = """\nFirst sentence. <br> Second sentence.\nThird <i>sentence</i> is here.\n\nFourth sentence. Fifth sentence"""
        result = preprocessor.preprocessing(text)

        self.assertEqual(result[1].paragraphIndex, 0)
        self.assertEqual(result[2].text, "Third sentence is here.")
        self.assertEqual(result[3].charStart, 71)

if __name__ == '__main__':
    unittest.main()
