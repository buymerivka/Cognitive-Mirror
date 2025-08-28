import pandas as pd
from sklearn.model_selection import train_test_split

# 1. Load dataset
df = pd.read_parquet("../../models/bert_emotions/emotions_dataset.parquet")

# 2. Inspect columns
print(df.columns)

# Assuming columns: 'text' and 'emotion'
X = df["Sentence"].values
y = df["Label"].values

# 3. Split dataset (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Train size:", len(X_train))
print("Test size:", len(X_test))

# 4. Convert to DataFrame if needed
train_df = pd.DataFrame({"text": X_train, "emotion": y_train})
test_df = pd.DataFrame({"text": X_test, "emotion": y_test})

# Optional: save splits
train_df.to_parquet("train.parquet", index=False)
test_df.to_parquet("test.parquet", index=False)
