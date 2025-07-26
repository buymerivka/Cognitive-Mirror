
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder


class BiasClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=50000, analyzer='char_wb')
        self.model = LogisticRegression(max_iter=1000)
        self.label_encoder = LabelEncoder()

    def train(self, texts, labels):
        y = self.label_encoder.fit_transform(labels)
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, y)

    def predict(self, texts, top_n: int = 1):
        if top_n > 14:
            top_n = 14

        X = self.vectorizer.transform(texts)
        probs = self.model.predict_proba(X)
        labels = self.label_encoder.classes_

        results = []

        for text, prob in zip(texts, probs):
            prediction = []
            for label, cur_prob in zip(labels, prob):
                prediction.append({
                    'label': str(label),
                    'score': f'{float(cur_prob):.4f}'
                })
            prediction = sorted(prediction, key=lambda x: x['score'], reverse=True)
            prediction = prediction[:top_n]
            results.append(prediction)

        return [
            {
                'text': text,
                'predictions': result
            }
            for text, result in zip(texts, results)
        ]

    def save(self, model_path='../models/model.joblib', vectorizer_path='../models/vectorizer.joblib'):
        joblib.dump(self.model, model_path)
        joblib.dump((self.vectorizer, self.label_encoder), vectorizer_path)

    def load(self, model_path='../models/model.joblib', vectorizer_path='../models/vectorizer.joblib'):
        self.model = joblib.load(model_path)
        self.vectorizer, self.label_encoder = joblib.load(vectorizer_path)
