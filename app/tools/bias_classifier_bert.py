import json
import os

import numpy as np
import pandas as pd
from datasets import load_dataset
from sklearn.metrics import f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def main():

    dataset = load_dataset('json', data_files={'train': f'{BASE_DIR}/datasets/train_CoCoLoFa.json',
                                               'dev': f'{BASE_DIR}/datasets/dev_CoCoLoFa.json',
                                               'test': f'{BASE_DIR}/datasets/test_CoCoLoFa.json'})

    if 'label' in dataset['train'].features.keys():
        dataset = dataset.rename_column('label', 'labels')

    if 'label' in dataset['dev'].features.keys():
        dataset = dataset.rename_column('label', 'labels')

    if 'label' in dataset['test'].features.keys():
        dataset = dataset.rename_column('label', 'labels')

    dataset = dataset.class_encode_column('labels')

    model_id = 'vinai/bertweet-base'
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=False)

    def tokenize(batch):
        return tokenizer(batch['text'], padding='max_length', truncation=True, max_length=128)

    tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=['text'])

    labels = tokenized_dataset['train'].features['labels'].names
    num_labels = len(labels)
    label2id, id2label = dict(), dict()
    for i, label in enumerate(labels):
        label2id[label] = str(i)
        id2label[str(i)] = label

    model = AutoModelForSequenceClassification.from_pretrained(
        model_id, num_labels=num_labels, label2id=label2id, id2label=id2label,
    )

    def compute_metrics(eval_pred):
        predictions, expected_labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        score = f1_score(
                expected_labels, predictions, average='weighted'
            )
        return {'f1': float(score) if score == 1 else score}

    training_args = TrainingArguments(
        output_dir='../models/manipulations_bert_model',
        per_device_train_batch_size=32,
        per_device_eval_batch_size=32,
        learning_rate=5e-5,
        num_train_epochs=3,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=50,
        eval_strategy='epoch',
        save_strategy='epoch',
        save_total_limit=2,
        load_best_model_at_end=True,
        dataloader_num_workers=4,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset['train'],
        eval_dataset=tokenized_dataset['dev'],
        compute_metrics=compute_metrics
    )

    trainer.train()


if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    with open('../datasets/train_CoCoLoFa.json', 'r', encoding='utf-8') as f:
        data = json.load(f)


    labels = [item['label'] for item in data]
    print(set(labels))
