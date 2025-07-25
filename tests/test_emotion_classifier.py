import unittest

from app.tools.emotion_classifier import emotion_classify


class TestEmotionClassifier(unittest.TestCase):

    def test_single_emotion(self):
        result = emotion_classify("I'm so proud of myself today!", n=1)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 1)

        top_emotion, confidence = next(iter(result.items()))
        self.assertIsInstance(top_emotion, str)
        self.assertTrue(0 <= float(confidence) <= 1)

    def test_top_n_emotions(self):
        result = emotion_classify('I am happy, excited and a little nervous', n=3)
        self.assertEqual(len(result), 3)
        for label, conf in result.items():
            self.assertIsInstance(label, str)
            self.assertTrue(0 <= float(conf) <= 1)

    def test_empty_input(self):
        result = emotion_classify('', n=3)
        self.assertIsInstance(result, dict)
        self.assertGreaterEqual(len(result), 0)

    def test_unicode_input(self):
        result = emotion_classify("I'm so happy!", n=2)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)

    def test_large_n(self):
        result = emotion_classify('Everything is fine', n=50)
        self.assertLessEqual(len(result), 28)


if __name__ == '__main__':
    unittest.main()
