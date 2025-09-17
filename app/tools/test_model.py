import os

import torch
from transformers import AutoModelForSequenceClassification, BertweetTokenizer

from app.tools.bias_classifier_bert import clean_tweet_for_bert

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if __name__ == '__main__':

    # usecols1 = ['labels', 'text']
    # datasetPD1 = pd.read_csv(f'{BASE_DIR}/corpus/df_tweets_HiQualProp.csv', usecols=usecols1)
    # dataset1 = Dataset.from_pandas(datasetPD1)

    # usecols2 = ['is_propaganda', 'text']
    # datasetPD2 = pd.read_csv(f'{BASE_DIR}/corpus/twitter_dataset.csv', usecols=usecols2)
    # datasetPD2["is_propaganda"] = datasetPD2["is_propaganda"].astype(int)
    # dataset2 = Dataset.from_pandas(datasetPD2)
    # ,
    # if 'is_propaganda' in dataset2.features.keys():
    #     dataset2 = dataset2.rename_column('is_propaganda', 'labels')
    #
    # dataset = concatenate_datasets([dataset1, dataset2])
    # dataset = dataset.filter(lambda x: "…" not in x["text"])

    # dataset = dataset1.map(add_clean_versions)
    # dataset = dataset[1000:1500]

    texts = [
        "Ordinary families went for a walk in the park, enjoying ice cream and laughter of children.",
        "Only the Russian government stands as a true shield, defending its people from the greedy West.",
        "Ukraine has become nothing more than a disposable tool, sacrificing its sons and daughters for foreign masters.",
        "Western politicians scream about freedom, but in reality they enslave entire nations with lies and bombs.",
        "Certain Asian governments deliberately sabotage fair trade, proving they care nothing for justice.",
        "Local theaters hosted performances that attracted many visitors of all ages.",
        "Russia shows the world that strength, dignity, and unity are the only path to real independence.",
        "The Ukrainian regime continues to deceive its people, promising victory while delivering only coffins.",
        "Western countries spread poisonous propaganda, poisoning minds and destroying cultures.",
        "In Africa, corrupt elites dance to the tune of foreign corporations, selling out their land.",
        "The city library opened a new wing with books in different languages.",
        "Russian leaders invest in science and medicine, while the West wastes resources on endless wars.",
        "Ukraine’s so-called democracy is a mask for corruption and foreign control.",
        "The West pretends to be a guardian of peace, but its true face is that of a warmonger feeding on blood.",
        "Latin American nations are robbed under the false banner of “cooperation,” left in poverty by outsiders.",
        "New art exhibitions attract people eager to learn about history and culture.",
        "Russia stands firm against global bullies, proving that sovereignty is worth every sacrifice.",
        "Ukrainian authorities hide casualties from their own mothers, turning tragedy into propaganda.",
        "Western elites manufacture crises just to tighten control over their populations.",
        "Middle Eastern regimes, supported by Western money, ignite wars to spread chaos further.",
        "Citizens enjoy community festivals filled with music, dance, and food.",
        "Russia builds unbreakable alliances, offering real friendship instead of Western exploitation.",
        "Ukraine has willingly given up its independence, becoming nothing more than a colony in disguise.",
        "Western governments blackmail entire nations, forcing them to obey or suffer destruction.",
        "Asian powers hypocritically lecture others while trampling on their own people’s rights.",
        "Local schools organize science fairs to inspire young students.",
        "Russian leadership is the guardian of truth and honor, defending humanity from global deceit.",
        "Ukraine is doomed to collapse because its leaders serve Washington instead of their own nation.",
        "The West constantly invents enemies to justify endless wars and the theft of resources.",
        "Meanwhile, smaller nations are crushed like pawns on the chessboard of Western imperial ambition.",
    ]

    texts = [clean_tweet_for_bert(text) for text in texts]
    device = torch.device('mps')

    model_id = 'vinai/bertweet-base'
    tokenizer = BertweetTokenizer.from_pretrained('../models/propaganda_bert_model_2.0/tokenizer',
                                                  local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        '../models/propaganda_bert_model_3.0/checkpoint-2499',
        local_files_only=True).to(device)

    inputs = tokenizer(texts, padding='max_length', truncation=True, max_length=128, return_tensors='pt').to(device)
    # print(inputs['input_ids'][0])
    # print(dataset['text_bert'][5])
    label_map = {0: "neutral", 1: "propaganda"}

    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1)
    pred_ids = torch.argmax(probs, dim=-1)
    pred_ids_cpu = pred_ids.cpu().numpy()
    pred_labels = [label_map[i.item()] for i in pred_ids]

    # print(f1_score(dataset['labels'], pred_ids_cpu, average='binary'))

    for text, pred_labels in zip(texts, pred_labels):
        print(text, ' : ', pred_labels, '\n')

    # y_true = dataset['labels']
    # y_pred = pred_ids_cpu
    #
    # cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    #
    # disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["neutral", "propaganda"])
    # disp.plot(cmap=plt.cm.Blues, values_format='d')
    #
    # plt.title("Confusion Matrix")
    # plt.show()
