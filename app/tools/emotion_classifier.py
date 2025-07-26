import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.tools.emotion_model_download import ensure_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ensure_model()


def emotion_classify(text: str, n: int = 1):
    if n > 28:
        n = 28
    local_model_path = f'{BASE_DIR}/models/bert-goemotions'

    tokenizer = AutoTokenizer.from_pretrained(local_model_path, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(local_model_path, local_files_only=True)

    id2label = model.config.id2label

    inputs = tokenizer(text, return_tensors='pt')
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.sigmoid(logits)[0]

    # Вивести топ-N емоцій
    top_n = n
    top_indices = torch.topk(probs, top_n).indices.tolist()
    return {id2label[idx]: f'{probs[idx].item():.4f}' for idx in top_indices}


if __name__ == '__main__':
    print(emotion_classify("."))
