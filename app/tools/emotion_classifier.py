import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.tools.emotion_model_download import ensure_model
from app.tools.preprocessor import preprocessing

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
    top_emotions = {id2label[idx]: f'{probs[idx].item():.4f}' for idx in top_indices}
    return {
        'text': text,
        'predictions': [{
            'label': list(top_emotions.keys())[i],
            'score': list(top_emotions.values())[i],
        } for i in range(len(top_emotions))]
    }


def text_classify_by_sentence(text: str, n: int = 1):
    sentences = [data.text for data in preprocessing(text)]
    result = []
    for sentence in sentences:
        result.append(emotion_classify(sentence, n))

    return result


def text_classify_by_paragraph(text: str, n: int = 1):
    parsed_data = preprocessing(text)
    print(parsed_data)
    paragraphs = []
    current_paragraph_idx = -1
    for data in parsed_data:
        if data.paragraphIndex == current_paragraph_idx:
            paragraphs[-1] += ' ' + data.text
        else:
            paragraphs.append(data.text)
            current_paragraph_idx += 1
    result = []
    print(paragraphs)
    for paragraph in paragraphs:
        result.append(emotion_classify(paragraph, n))

    return result
