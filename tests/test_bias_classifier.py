import unittest

from app.tools import bias_classifier


class TestBiasClassifier(unittest.TestCase):
    def test_train_predict(self):
        text = ['He is either bad or good person', 'All zoomers are productive.',
                'This politicians is corrupt, so all politicians are corrupt.']
        labels = ['Black-and-white thinking', 'Overgeneralization', 'Cherry picking']

        clf = bias_classifier.BiasClassifier()
        clf.train(text, labels)
        clf.save()
        predictions = clf.predict(['This dog is mad, so all dogs are mad.'])

        assert isinstance(predictions, list)
        self.assertEqual(len(predictions[0]['predictions']), 1)
        assert isinstance(predictions[0], dict)

    def test_train_predict_2(self):
        text = ['He is either bad or good person', 'All zoomers are productive.',
                'This politicians is corrupt, so all politicians are corrupt.']
        labels = ['Black-and-white thinking', 'Overgeneralization', 'Cherry picking']

        clf = bias_classifier.BiasClassifier()
        clf.train(text, labels)
        predictions = clf.predict(['This dog is mad, so all dogs are mad.'], 3)

        assert isinstance(predictions, list)
        self.assertEqual(len(predictions[0]['predictions']), 3)
        assert isinstance(predictions[0], dict)

    def test_feature_count(self):
        text = ['He is either bad or good person', 'All zoomers are productive.',
                'This politicians is corrupt, so all politicians are corrupt.']

        clf = bias_classifier.BiasClassifier()
        clf.vectorizer.fit(text)
        feature_count = len(clf.vectorizer.get_feature_names_out())
        assert feature_count < 50000

    def test_initialization(self):
        clf = bias_classifier.BiasClassifier()
        assert clf.vectorizer is not None
        assert clf.model is not None
        assert clf.label_encoder is not None


if __name__ == '__main__':
    unittest.main()
