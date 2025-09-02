import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.tools.preprocessor import preprocessing


def classify(text: str, paragraph_index: int, sentence_index: int, char_start: int, char_end: int,
             local_model_path: str, local_tokenizer_path: str, n: int = 1, max_n: int = 5):
    if n > max_n:
        n = max_n

    tokenizer = AutoTokenizer.from_pretrained(local_tokenizer_path, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(local_model_path, local_files_only=True)

    inputs = tokenizer(text, padding='max_length', truncation=True, max_length=128, return_tensors='pt')

    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1)[0]

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


def text_classify_by_sentence(text: str, local_model_path: str, local_tokenizer_path: str, n: int = 1, max_n: int = 5):
    sentences_data = [data for data in preprocessing(text)]
    result = []
    for sentence_data in sentences_data:
        result.append(classify(sentence_data.text, sentence_data.paragraphIndex, sentence_data.sentenceIndex,
                               sentence_data.charStart, sentence_data.charEnd, local_model_path, local_tokenizer_path,
                               n, max_n))

    return result


def text_classify_by_paragraph(text: str, local_model_path: str, local_tokenizer_path: str, n: int = 1, max_n: int = 5):
    parsed_data = preprocessing(text)
    paragraphs = []
    current_paragraph_idx = -1
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
        result.append(classify(paragraph['text'],
                               paragraph['paragraph_id'],
                               paragraph['sentence_id'],
                               paragraph['char_start'],
                               paragraph['char_end'],
                               local_model_path,
                               local_tokenizer_path,
                               n, max_n))
    return result
