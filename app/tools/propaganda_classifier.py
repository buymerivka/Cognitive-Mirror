import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.tools.emotion_model_download import ensure_model
from app.tools.preprocessor import preprocessing

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ensure_model()


def propaganda_classify(text: str, paragraph_index: int, sentence_index: int, char_start: int, char_end: int, n: int = 1):
    if n > 5:
        n = 5

    device = torch.device('mps')
    local_tokenizer_path = f'{BASE_DIR}/models/propaganda_bert_model/tokenizer'
    local_model_path = f'{BASE_DIR}/models/propaganda_bert_model/checkpoint-2220'

    tokenizer = AutoTokenizer.from_pretrained(local_tokenizer_path, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(local_model_path, local_files_only=True).to(device)


    inputs = tokenizer(text, padding='max_length', truncation=True, max_length=128, return_tensors='pt').to(device)

    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.sigmoid(logits)[0]

    id2label = model.config.id2label

    top_indices = torch.topk(probs, n).indices.tolist()
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
        result.append(propaganda_classify(sentence_data.text, sentence_data.paragraphIndex, sentence_data.sentenceIndex,
                      sentence_data.charStart, sentence_data.charEnd, n))

    return result


