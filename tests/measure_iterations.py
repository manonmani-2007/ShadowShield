import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

DATASET = "dataset/processed/combined_train.csv"

df = pd.read_csv(DATASET)

X = df["text"].astype(str)
y = df["label"].astype(str)

# Same split for every iteration
X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


def evaluate(name, vectorizer):

    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)

    model = LogisticRegression(
        max_iter=2000,
        random_state=42
    )

    model.fit(X_train_vec, y_train)

    predictions = model.predict(X_val_vec)

    accuracy = accuracy_score(y_val, predictions)
    precision = precision_score(
        y_val,
        predictions,
        pos_label="sensitive",
        zero_division=0
    )
    recall = recall_score(
        y_val,
        predictions,
        pos_label="sensitive",
        zero_division=0
    )
    f1 = f1_score(
        y_val,
        predictions,
        pos_label="sensitive",
        zero_division=0
    )

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    print(f"Accuracy :  {accuracy * 100:.2f}%")
    print(f"Precision:  {precision * 100:.2f}%")
    print(f"Recall   :  {recall * 100:.2f}%")
    print(f"F1-score :  {f1 * 100:.2f}%")

    print(f"Training features: {X_train_vec.shape[1]}")

    return {
        "Version": name,
        "Accuracy": accuracy * 100,
        "Precision": precision * 100,
        "Recall": recall * 100,
        "F1-score": f1 * 100
    }


results = []

# ============================================================
# ITERATION 1 — BASIC BASELINE
# CountVectorizer instead of TF-IDF
# ============================================================

results.append(
    evaluate(
        "Iteration 1 - CountVectorizer Baseline",
        CountVectorizer(
            max_features=500,
            ngram_range=(1, 1)
        )
    )
)


# ============================================================
# ITERATION 2 — REFINED MODEL
# TF-IDF with increased feature representation
# ============================================================

results.append(
    evaluate(
        "Iteration 2 - TF-IDF Refined",
        TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            sublinear_tf=True
        )
    )
)


# ============================================================
# SUMMARY
# ============================================================

result_df = pd.DataFrame(results)

print("\n\n")
print("=" * 75)
print("SHADOWSHIELD ITERATION COMPARISON")
print("=" * 75)

print(
    result_df.to_string(
        index=False,
        formatters={
            "Accuracy": "{:.2f}%".format,
            "Precision": "{:.2f}%".format,
            "Recall": "{:.2f}%".format,
            "F1-score": "{:.2f}%".format
        }
    )
)

result_df.to_csv(
    "dataset/processed/iteration_results.csv",
    index=False
)

print("\nResults saved to:")
print("dataset/processed/iteration_results.csv")