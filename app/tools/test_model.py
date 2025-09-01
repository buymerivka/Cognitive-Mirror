import os

import torch
from sklearn.metrics import f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if __name__ == '__main__':

    device = torch.device('mps')

    # usecols = ['strategy', 'text_normalized']
    # datasetPD = pd.read_csv(f'{BASE_DIR}/corpus/df_tweets_HiQualProp.csv', usecols=usecols)
    #
    # data = datasetPD['text_normalized']
    # labels = datasetPD['strategy']
    # data_test = data[:1000].tolist()
    # labels_test = labels[:1000].tolist()

    model_path = '../models/propaganda_bert_model/checkpoint-2220'
    tokenizer_path = '../models/propaganda_bert_model/tokenizer'

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)

    inputs = tokenizer('President Vladimir Putin sought to justify his contentious war against Ukraine during a huge Victory Day parade on Monday , once again falsely calling Ukrainians “ Nazis ” and insisting without evidence that Kyiv was planning to build nuclear weapons . HTTPURL',
                       padding='max_length', truncation=True, max_length=128, return_tensors='pt').to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    predicted_classes_id = outputs.logits.argmax(dim=-1).cpu().numpy()
    predicted_classes_str = [str(label) for label in predicted_classes_id]

    predicted_labels = [model.config.id2label[pred_class] for pred_class in predicted_classes_id]

    # for pred_class, exp_class in zip(predicted_labels, labels_test):
    #     if pred_class == exp_class:
    #         print('Predicted label:', pred_class, 'TRUE')
    #     else:
    #         print('Predicted label:', pred_class, 'FALSE')
    # score = f1_score(labels_test, predicted_labels, average='weighted')
    # print(score)
    print(predicted_labels)
    # true_class_id = [model.config.label2id[label] for label in labels_test]
    #
    # cm = confusion_matrix(true_class_id, predicted_classes_str)
    # disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=list(model.config.id2label.values()))
    # disp.plot(xticks_rotation=45, cmap='Blues')
    # plt.show()
