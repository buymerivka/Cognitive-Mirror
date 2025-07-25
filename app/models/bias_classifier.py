import json

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

    def predict(self, texts):
        X = self.vectorizer.transform(texts)
        probs = self.model.predict_proba(X)
        labels = self.label_encoder.classes_

        return [
            {
                'text': text,
                'bias probabilities': dict(zip(labels, prob_row))
            }
            for text, prob_row in zip(texts, probs)
        ]

    def save(self, model_path='model.joblib', vectorizer_path='vectorizer.joblib'):
        joblib.dump(self.model, model_path)
        joblib.dump((self.vectorizer, self.label_encoder), vectorizer_path)

    def load(self, model_path='model.joblib', vectorizer_path='vectorizer.joblib'):
        self.model = joblib.load(model_path)
        self.vectorizer, self.label_encoder = joblib.load(vectorizer_path)


if __name__ == '__main__':
    with open('../datasets/small_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = [item['text'] for item in data]
    labels = [item['label'] for item in data]

    classifier = BiasClassifier()
    classifier.train(texts, labels)
    classifier.save()

    classifier = BiasClassifier()
    classifier.load()

    new_texts = [
        'He is either good or bad.'
    ]

    results = classifier.predict(new_texts)

    for r in results:
        print(f'\nText: {r['text']}')
        print('Bias probabilities:')
        for bias, prob in sorted(r['bias probabilities'].items(), key=lambda x: -x[1]):
            percent = prob * 100
            print(f'  {bias}: {percent:.1f}%')
