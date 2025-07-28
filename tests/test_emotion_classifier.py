import unittest

from app.tools.emotion_classifier import emotion_classify


class TestEmotionClassifier(unittest.TestCase):

    def test_single_emotion(self):
        result = emotion_classify("I'm so proud of myself today!", 0, 0, 0, 0, n=1)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result['predictions']), 1)

        top_emotion, confidence = result['predictions'][0]['label'], result['predictions'][0]['score']
        self.assertIsInstance(top_emotion, str)
        self.assertTrue(0 <= float(confidence) <= 1)

    def test_top_n_emotions(self):
        result = emotion_classify('I am happy, excited and a little nervous', 0, 0, 0, 0, n=3)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result['predictions']), 3)

        for emotion_w_score in result['predictions']:
            label = emotion_w_score['label']
            score = emotion_w_score['score']
            self.assertIsInstance(label, str)
            self.assertTrue(0 <= float(score) <= 1)

    def test_empty_input(self):
        result = emotion_classify('', 0, 0, 0, 0, n=3)
        self.assertIsInstance(result, dict)
        self.assertGreaterEqual(len(result), 0)

    def test_unicode_input(self):
        result = emotion_classify("I'm so happy!", 0, 0, 0, 0, n=2)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)

    def test_large_n(self):
        result = emotion_classify('Everything is fine', 0, 0, 0, 0, n=50)
        self.assertLessEqual(len(result), 28)


if __name__ == '__main__':
    unittest.main()
