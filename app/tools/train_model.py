import json

from app.tools.bias_classifier import BiasClassifier

if __name__ == '__main__':
    bias = BiasClassifier()

    with open('../datasets/train_CoCoLoFa.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = [item['text'] for item in data]
    labels = [item['label'] for item in data]
    bias.train(texts, labels)

    bias.save()
