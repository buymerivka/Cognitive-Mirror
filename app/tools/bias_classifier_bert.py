# import os
#
# import joblib
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
# from sklearn.pipeline import FeatureUnion
# from sklearn.preprocessing import LabelEncoder
#
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
#
# import evaluate
# import numpy as np
# from transformers import DataCollatorWithPadding
#
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#
#
# class BiasClassifier:
#     def __init__(self, model_name: str = "bert-base-uncased", max_len: int = 160,
#                  test_size: float = 0.1,
#                  seed: int = 42, ):
#         self.model_name = model_name
#         self.max_len = max_len
#         self.test_size = test_size
#         self.seed = seed
#
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
#         self.label_encoder = LabelEncoder()
#
#         self.model = None
#         self.trainer = None
#
#     def train(self, texts, labels):
#
#
