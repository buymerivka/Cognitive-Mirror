import os
import unittest

from app.tools.classifier import classify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
MODEL_DIR = os.path.join(BASE_DIR, 'app', 'models', 'bert-goemotions')


class TestEmotionClassifier(unittest.TestCase):

    def test_single_emotion(self):
        result = classify("I'm so proud of myself today!", 0, 0, 0,
                          0,
                          MODEL_DIR,
                          MODEL_DIR, n=1, max_n=28)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 6)
        self.assertEqual(len(result['predictions']), 1)

        top_emotion, confidence = result['predictions'][0]['label'], result['predictions'][0]['score']
        self.assertIsInstance(top_emotion, str)
        self.assertTrue(0 <= float(confidence) <= 1)

    def test_top_n_emotions(self):
        result = classify("I'm so proud of myself today!", 0, 0, 0,
                          0,
                          MODEL_DIR,
                          MODEL_DIR, n=3, max_n=28)
        self.assertEqual(len(result), 6)
        self.assertEqual(len(result['predictions']), 3)

        for emotion_w_score in result['predictions']:
            label = emotion_w_score['label']
            score = emotion_w_score['score']
            self.assertIsInstance(label, str)
            self.assertTrue(0 <= float(score) <= 1)

    def test_empty_input(self):
        result = classify('', 0, 0, 0,
                          0,
                          MODEL_DIR,
                          MODEL_DIR, n=3, max_n=28)
        self.assertIsInstance(result, dict)
        self.assertGreaterEqual(len(result), 0)

    def test_unicode_input(self):
        result = classify("I'm so happy!", 0, 0, 0,
                          0,
                          MODEL_DIR,
                          MODEL_DIR, n=2, max_n=28)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 6)

    def test_large_n(self):
        result = classify('Everything is fine', 0, 0, 0,
                          0,
                          MODEL_DIR,
                          MODEL_DIR, n=50, max_n=28)
        self.assertLessEqual(len(result), 28)


if __name__ == '__main__':
    unittest.main()
