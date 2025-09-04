import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.tools.preprocessor import preprocessing


def classify(text: str, paragraph_index: int, sentence_index: int, char_start: int, char_end: int,
             local_model_path: str, local_tokenizer_path: str, n: int, max_n: int):
    if n > max_n:
        n = max_n
    print(n)
    print(max_n)

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


def text_full_classify(text: str, propaganda_local_model_path: str, propaganda_local_tokenizer_path: str,
                       manipulations_local_model_path: str, manipulations_local_tokenizer_path: str,
                       emotions_local_model_path: str, emotions_local_tokenizer_path: str, max_propaganda: int,
                       max_manipulations: int, max_emotions: int, top_n_propaganda: int, top_n_manipulations: int,
                       top_n_emotions: int):

    sentences_data = [data for data in preprocessing(text)]
    result = {
        'propaganda_analyzed': [],
        'manipulations_analyzed': [],
        'emotions_analyzed': []
    }
    for sentence_data in sentences_data:
        propaganda_analysis = classify(sentence_data.text, sentence_data.paragraphIndex, sentence_data.sentenceIndex,
                                       sentence_data.charStart, sentence_data.charEnd, propaganda_local_model_path,
                                       propaganda_local_tokenizer_path, top_n_propaganda, max_propaganda)

        if propaganda_analysis['predictions'][0]['label'] != 'general discourse':
            manipulations_analysis = classify(sentence_data.text, sentence_data.paragraphIndex,
                                              sentence_data.sentenceIndex, sentence_data.charStart,
                                              sentence_data.charEnd, manipulations_local_model_path,
                                              manipulations_local_tokenizer_path,
                                              top_n_manipulations, max_manipulations)

            emotions_analysis = classify(sentence_data.text, sentence_data.paragraphIndex,
                                              sentence_data.sentenceIndex, sentence_data.charStart,
                                              sentence_data.charEnd, emotions_local_model_path,
                                              emotions_local_tokenizer_path, top_n_emotions, max_emotions)
            result['manipulations_analyzed'].append(manipulations_analysis)
            result['emotions_analyzed'].append(emotions_analysis)

        result['propaganda_analyzed'].append(propaganda_analysis)
    return result


def text_classify_by_sentence(text: str, local_model_path: str, local_tokenizer_path: str, display_n: int, max_n):
    sentences_data = [data for data in preprocessing(text)]
    result = []
    for sentence_data in sentences_data:
        result.append(classify(sentence_data.text, sentence_data.paragraphIndex, sentence_data.sentenceIndex,
                               sentence_data.charStart, sentence_data.charEnd, local_model_path, local_tokenizer_path,
                               display_n, max_n))

    return result


def text_classify_by_paragraph(text: str, local_model_path: str, local_tokenizer_path: str, display_n: int, max_n: int):
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
                               display_n,
                               max_n))
    return result
