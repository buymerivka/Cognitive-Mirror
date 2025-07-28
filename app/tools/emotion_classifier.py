import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.tools.emotion_model_download import ensure_model
from app.tools.preprocessor import preprocessing

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ensure_model()


def emotion_classify(text: str, paragraph_index: int, sentence_index: int, char_start: int, char_end: int, n: int = 1):
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
        } for i in range(len(top_emotions))],
        'paragraphIndex': paragraph_index,
        'sentenceIndex': sentence_index,
        'charStart': char_start,
        'charEnd': char_end,
    }


def text_classify_by_sentence(text: str, n: int = 1):
    sentences_data = [data for data in preprocessing(text)]
    result = []
    for sentence_data in sentences_data:
        result.append(emotion_classify(sentence_data.text, sentence_data.paragraphIndex, sentence_data.sentenceIndex,
                      sentence_data.charStart, sentence_data.charEnd, n))

    return result


def text_classify_by_paragraph(text: str, n: int = 1):
    parsed_data = preprocessing(text)
    paragraphs = []
    current_paragraph_idx = -1
    print(parsed_data)
    for data in parsed_data:
        if data.paragraphIndex == current_paragraph_idx:
            paragraphs[-1]['text'] += ' ' + data.text
            paragraphs[-1]['char_end'] = data.charEnd
        else:
            paragraphs.append({'text': data.text,
                               'sentence_id': -1,
                               'paragraph_id': data.paragraphIndex,
                               'char_start': data.charStart,
                               'char_end': data.charEnd})
            current_paragraph_idx += 1
    result = []

    for paragraph in paragraphs:
        result.append(emotion_classify(paragraph['text'],
                                       paragraph['paragraph_id'],
                                       paragraph['sentence_id'],
                                       paragraph['char_start'],
                                       paragraph['char_end'],
                                       n))
    print(result)
    return result
