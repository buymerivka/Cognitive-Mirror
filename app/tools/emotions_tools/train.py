import os
import numpy as np
from datasets import load_dataset
from sklearn.metrics import f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def main():
    # 1. Load dataset
    dataset = load_dataset(
        "parquet",
        data_files={
            "train": f"{BASE_DIR}/models/bert_emotions/train.parquet",
            "test": f"{BASE_DIR}/models/bert_emotions/test.parquet",
        }
    )

    # 2. Normalize label column name
    for split in dataset.keys():
        if "emotion" in dataset[split].features:
            dataset[split] = dataset[split].rename_column("emotion", "labels")

    # 3. Encode labels
    dataset = dataset.class_encode_column("labels")

    # 4. Model & tokenizer
    model_id = "vinai/bertweet-base"
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)

    def tokenize(batch):
        return tokenizer(batch["text"], padding="max_length", truncation=True, max_length=128)

    tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])

    labels = tokenized_dataset["train"].features["labels"].names
    num_labels = len(labels)
    label2id = {label: i for i, label in enumerate(labels)}
    id2label = {i: label for i, label in enumerate(labels)}

    model = AutoModelForSequenceClassification.from_pretrained(
        model_id,
        num_labels=num_labels,
        label2id={k: str(v) for k, v in label2id.items()},
        id2label={str(k): v for k, v in id2label.items()},
    )

    # 5. Metrics
    def compute_metrics(eval_pred):
        predictions, expected_labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        score = f1_score(expected_labels, predictions, average="weighted")
        return {"f1": score}

    # 6. Training arguments
    training_args = TrainingArguments(
        output_dir=f"{BASE_DIR}/models/emotions_bert_model",
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=8,
        learning_rate=5e-5,
        num_train_epochs=3,
        weight_decay=0.01,
        logging_dir=f"{BASE_DIR}/logs",
        logging_steps=50,
        eval_strategy="epoch",  # or evaluation_strategy if HF >=4.6
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        dataloader_num_workers=2,
        fp16=True,  # mixed precision
    )

    # 7. Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["test"],
        compute_metrics=compute_metrics,
        tokenizer=tokenizer,
    )

    # 8. Train
    trainer.train()

    # 9. Evaluate
    metrics = trainer.evaluate()
    print(metrics)


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
