import os
import json
from pprint import pprint

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import FeatureUnion

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class BiasClassifier:
    def __init__(self):
        self.vectorizer = FeatureUnion([
            ("word", TfidfVectorizer(ngram_range=(1, 3), analyzer='word', strip_accents='unicode')),
            ("char_wb", TfidfVectorizer(ngram_range=(3, 6), analyzer='char', strip_accents='unicode'))
        ])
        self.model = LogisticRegression(C = 10, class_weight='balanced', solver='saga', max_iter=10000, random_state=42, verbose=1)
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

    def save(self, model_path=f'{BASE_DIR}/models/propaganda_model/model.joblib',
             vectorizer_path=f'{BASE_DIR}/models/propaganda_model/vectorizer.joblib'):
        joblib.dump(self.model, model_path)
        joblib.dump((self.vectorizer, self.label_encoder), vectorizer_path)

    def load(self, model_path=f'{BASE_DIR}/models/propaganda_model/model.joblib',
             vectorizer_path=f'{BASE_DIR}/models/propaganda_model/vectorizer.joblib'):
        self.model = joblib.load(model_path)
        self.vectorizer, self.label_encoder = joblib.load(vectorizer_path)
