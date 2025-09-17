import os
import re

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from datasets import Dataset, load_from_disk
from sklearn.metrics import f1_score, matthews_corrcoef
from torch.utils.data import DataLoader
from transformers import (
    AutoModelForSequenceClassification,
    BertweetTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def clean_tweet_for_bert(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'@\w+', '<USER>', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def add_clean_versions(batch):
    batch['text_bert'] = clean_tweet_for_bert(batch['text'])
    return batch


def split_dataset():
    usecols = ['labels', 'text']
    datasetPD = pd.read_csv(f'{BASE_DIR}/corpus/df_tweets_HiQualProp.csv', usecols=usecols)
    dataset = Dataset.from_pandas(datasetPD)
    dataset = dataset.shuffle(seed=42)
    dataset = dataset.map(add_clean_versions)
    dataset = dataset.remove_columns('text')
    dataset = dataset.rename_column('text_bert', 'text')

    dataset_test = dataset[:3000]
    dataset_val = dataset[3000:6000]
    dataset_train = dataset[6000:]

    dataset_test = Dataset.from_dict(dataset_test)
    dataset_val = Dataset.from_dict(dataset_val)
    dataset_train = Dataset.from_dict(dataset_train)
    return dataset_test, dataset_val, dataset_train


def tokenize_dataset(dataset):
    model_id = 'vinai/bertweet-base'
    tokenizer = BertweetTokenizer.from_pretrained(model_id, use_fast=False)

    def tokenize(batch):
        return tokenizer(batch['text'], padding='max_length', truncation=True, max_length=128)

    tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=['text'])
    return tokenized_dataset


def train_teacher(tokenized_train, tokenized_val):
    model_id = 'vinai/bertweet-base'
    labels = set(tokenized_train['labels'])
    num_labels = len(labels)

    model = AutoModelForSequenceClassification.from_pretrained(
        model_id, num_labels=num_labels
    )

    def compute_metrics(eval_pred):
        predictions, expected_labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        score_weighted = f1_score(expected_labels, predictions, average='weighted')
        score_binary = f1_score(expected_labels, predictions, average='binary')
        return {'f1_weighted': float(score_weighted) if score_weighted == 1 else score_weighted,
                'f1_binary': float(score_binary) if score_binary == 1 else score_binary,
                'matthews correlation coefficient': matthews_corrcoef(expected_labels, predictions)}

    training_args = TrainingArguments(
        output_dir='../models/propaganda_bert_model_teacher',
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
        dataloader_num_workers=4
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        compute_metrics=compute_metrics
    )

    trainer.train()


def predicted_by_teacher(tokenized_train):
    teacher_logits = []
    teacher_predictions = []

    device = torch.device('mps')

    model = AutoModelForSequenceClassification.from_pretrained(
        '../models/propaganda_bert_model_teacher/checkpoint-2214',
        local_files_only=True).to(device)

    tokenizer = BertweetTokenizer.from_pretrained('vinai/bertweet-base', use_fast=False)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors='pt')

    train_loader = DataLoader(tokenized_train, batch_size=32, collate_fn=data_collator)

    for i, batch in enumerate(train_loader):
        inputs = {k: v.to(device) for k, v in batch.items() if k != 'labels'}
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits.cpu()
        probs = F.softmax(logits, dim=-1)
        teacher_logits.append(logits)
        teacher_predictions.append(probs)
        if i % 50 == 0:
            print(f'Batch {i}')
            print('Logits:', logits[:2])
            print('Probabilities:', probs[:2])

    teacher_logits = torch.cat(teacher_logits, dim=0)
    teacher_predictions = torch.cat(teacher_predictions, dim=0)

    teacher_logits_list = teacher_logits.tolist()
    teacher_predictions_list = teacher_predictions.tolist()

    return teacher_logits_list, teacher_predictions_list


class DistillationTrainingArguments(TrainingArguments):
    def __init__(self, *args, alpha=0.5, temperature=2.0, **kwargs):
        super().__init__(*args, **kwargs)

        self.alpha = alpha
        self.temperature = temperature


class DistillationTrainer(Trainer):
    def __init__(self, *args, teacher_model=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher = teacher_model
        # place teacher on same device as student
        self._move_model_to_device(self.teacher, self.model.device)
        self.teacher.eval()

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        # compute student output
        outputs_student = model(**inputs)
        student_loss = outputs_student.loss
        with torch.no_grad():
            outputs_teacher = self.teacher(**inputs)

        assert outputs_student.logits.size() == outputs_teacher.logits.size()

        loss_function = nn.KLDivLoss(reduction='batchmean')
        loss_logits = (loss_function(
            F.log_softmax(outputs_student.logits / self.args.temperature, dim=-1),
            F.softmax(outputs_teacher.logits / self.args.temperature, dim=-1)) * (self.args.temperature ** 2))
        loss = self.args.alpha * student_loss + (1. - self.args.alpha) * loss_logits
        return (loss, outputs_student) if return_outputs else loss


def train_student(tokenized_train, tokenized_val):
    model_id = 'distilroberta-base'
    labels = set(tokenized_train['labels'])
    num_labels = len(labels)

    student_model = AutoModelForSequenceClassification.from_pretrained(
        model_id, num_labels=num_labels
    )

    teacher_model = AutoModelForSequenceClassification.from_pretrained(
        '../models/propaganda_bert_model_teacher/checkpoint-2214',
        local_files_only=True)

    def compute_metrics(eval_pred):
        predictions, expected_labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        score_weighted = f1_score(expected_labels, predictions, average='weighted')
        score_binary = f1_score(expected_labels, predictions, average='binary')
        return {'f1_weighted': float(score_weighted) if score_weighted == 1 else score_weighted,
                'f1_binary': float(score_binary) if score_binary == 1 else score_binary,
                'matthews correlation coefficient': matthews_corrcoef(expected_labels, predictions)}

    training_args = DistillationTrainingArguments(
        output_dir='../models/propaganda_bert_model_student',
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
        alpha=0.5,
        temperature=2.0
    )

    trainer = DistillationTrainer(
        model=student_model,
        args=training_args,
        teacher_model=teacher_model,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        compute_metrics=compute_metrics
    )

    trainer.train()


if __name__ == '__main__':
    import multiprocessing

    multiprocessing.freeze_support()

    dataset_dict = load_from_disk('tokenized_dataset')
    tokenized_val = dataset_dict['val']
    tokenized_test = dataset_dict['test']
    tokenized_train = load_from_disk('tokenized_train_with_teacher')

    student_model = AutoModelForSequenceClassification.from_pretrained(
        '../models/propaganda_bert_model_3.0/checkpoint-2499', local_files_only=True)
    teacher_model = AutoModelForSequenceClassification.from_pretrained(
        '../models/propaganda_bert_model_teacher/checkpoint-2214', local_files_only=True)

    tokenizer = BertweetTokenizer.from_pretrained('vinai/bertweet-base', use_fast=False)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors='pt')

    def compute_metrics(eval_pred):
        predictions, expected_labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        score_weighted = f1_score(expected_labels, predictions, average='weighted')
        score_binary = f1_score(expected_labels, predictions, average='binary')
        return {'f1_weighted': float(score_weighted) if score_weighted == 1 else score_weighted,
                'f1_binary': float(score_binary) if score_binary == 1 else score_binary,
                'matthews correlation coefficient': matthews_corrcoef(expected_labels, predictions)}

    trainer = Trainer(
        model=student_model,
        eval_dataset=tokenized_test,
        compute_metrics=compute_metrics,
        data_collator=data_collator
    )

    metrics = trainer.evaluate()
    print(metrics)
