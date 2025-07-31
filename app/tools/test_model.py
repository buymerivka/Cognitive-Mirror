import json

from sklearn.metrics import accuracy_score

from app.tools.bias_classifier import BiasClassifier

if __name__ == '__main__':
    bias = BiasClassifier()
    bias.load()

    with open("../datasets/dev_CoCoLoFa.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = [item["text"] for item in data]
    labels = [item["label"] for item in data]

    predictions = bias.predict(texts)
    predicted_labels = [item["predictions"][0]["label"] for item in predictions]
    accuracy = accuracy_score(labels, predicted_labels)

    print(f"{'True Label':<30} {'Predicted Label':<30} Match")
    print("-" * 70)
    for true_label, pred in zip(labels, predicted_labels):
        match = "✅" if true_label == pred else "❌"
        print(f"{true_label:<30} {pred:<30} {match}")

    print(f"Accuracy: {accuracy:.2%}")
