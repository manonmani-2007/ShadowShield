import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "dataset"
    / "processed"
    / "combined_train.csv"
)

MODEL_DIR = BASE_DIR / "ml" / "models"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("ShadowShield - ML Training")
print("=" * 70)

df = pd.read_csv(DATA_FILE)

print(f"\nDataset size: {len(df)}")

# Remove empty text
df = df[
    df["text"].notna()
    & (df["text"].str.strip() != "")
].copy()

X = df["text"].astype(str)
y = df["label"].astype(str)


# ============================================================
# TRAIN / VALIDATION SPLIT
# ============================================================

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Training samples: {len(X_train)}")
print(f"Validation samples: {len(X_val)}")


# ============================================================
# TF-IDF
# ============================================================

print("\nCreating TF-IDF features...")

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True,
    max_features=50000
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_val_tfidf = vectorizer.transform(X_val)

print(f"TF-IDF vocabulary size: {len(vectorizer.vocabulary_)}")
print(f"Training matrix: {X_train_tfidf.shape}")
print(f"Validation matrix: {X_val_tfidf.shape}")


# ============================================================
# MODELS
# ============================================================

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    ),

    "SVM": LinearSVC(
        random_state=42
    )
}


# ============================================================
# TRAIN + EVALUATE
# ============================================================

results = []

for name, model in models.items():

    print("\n" + "=" * 70)
    print(f"Training: {name}")
    print("=" * 70)

    model.fit(
        X_train_tfidf,
        y_train
    )

    predictions = model.predict(
        X_val_tfidf
    )

    accuracy = accuracy_score(
        y_val,
        predictions
    )

    precision = precision_score(
        y_val,
        predictions,
        pos_label="sensitive"
    )

    recall = recall_score(
        y_val,
        predictions,
        pos_label="sensitive"
    )

    f1 = f1_score(
        y_val,
        predictions,
        pos_label="sensitive"
    )

    cm = confusion_matrix(
        y_val,
        predictions,
        labels=["safe", "sensitive"]
    )

    tn, fp, fn, tp = cm.ravel()

    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

    print(f"\nAccuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")
    print(f"FPR      : {fpr:.4f}")
    print(f"FNR      : {fnr:.4f}")

    print("\nConfusion Matrix")
    print("                 Predicted")
    print("                 Safe  Sensitive")
    print(f"Actual Safe      {tn:4d}  {fp:9d}")
    print(f"Actual Sensitive {fn:4d}  {tp:9d}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_val,
            predictions
        )
    )

    results.append({
        "model": name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "fpr": fpr,
        "fnr": fnr
    })

    # Save model
    filename = name.lower().replace(" ", "_") + ".joblib"

    model_path = MODEL_DIR / filename

    joblib.dump(
        model,
        model_path
    )

    print(f"Saved model: {model_path}")


# ============================================================
# SAVE TF-IDF VECTORIZER
# ============================================================

vectorizer_path = MODEL_DIR / "tfidf_vectorizer.joblib"

joblib.dump(
    vectorizer,
    vectorizer_path
)

print("\n" + "=" * 70)
print("Saved TF-IDF vectorizer")
print("=" * 70)

print(vectorizer_path)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_path = (
    BASE_DIR
    / "dataset"
    / "processed"
    / "model_results.csv"
)

results_df.to_csv(
    results_path,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)

print("\nResults saved to:")
print(results_path)

print("\nTraining completed successfully.")