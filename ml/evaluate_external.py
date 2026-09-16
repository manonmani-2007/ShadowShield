import pandas as pd
import joblib

from pathlib import Path

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

TEST_FILE = (
    BASE_DIR
    / "dataset"
    / "processed"
    / "external_test_normalized.csv"
)

MODEL_DIR = BASE_DIR / "ml" / "models"

RESULTS_FILE = (
    BASE_DIR
    / "dataset"
    / "processed"
    / "external_test_results.csv"
)


# ============================================================
# LOAD TEST DATA
# ============================================================

print("=" * 70)
print("ShadowShield - External Test Evaluation")
print("=" * 70)

df = pd.read_csv(TEST_FILE)

df = df[
    df["text"].notna()
    & (df["text"].str.strip() != "")
].copy()

X_test = df["text"].astype(str)
y_test = df["label"].astype(str)

print(f"\nExternal test samples: {len(df)}")

print("\nTest labels:")
print(y_test.value_counts())


# ============================================================
# LOAD TF-IDF
# ============================================================

vectorizer_path = MODEL_DIR / "tfidf_vectorizer.joblib"

vectorizer = joblib.load(vectorizer_path)

X_test_tfidf = vectorizer.transform(X_test)

print(f"\nTF-IDF test matrix: {X_test_tfidf.shape}")


# ============================================================
# MODELS
# ============================================================

model_files = {
    "Logistic Regression":
        MODEL_DIR / "logistic_regression.joblib",

    "Random Forest":
        MODEL_DIR / "random_forest.joblib",

    "SVM":
        MODEL_DIR / "svm.joblib"
}


results = []


# ============================================================
# EVALUATION
# ============================================================

for name, model_path in model_files.items():

    print("\n" + "=" * 70)
    print(f"Evaluating: {name}")
    print("=" * 70)

    model = joblib.load(model_path)

    predictions = model.predict(
        X_test_tfidf
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        pos_label="sensitive"
    )

    recall = recall_score(
        y_test,
        predictions,
        pos_label="sensitive"
    )

    f1 = f1_score(
        y_test,
        predictions,
        pos_label="sensitive"
    )

    cm = confusion_matrix(
        y_test,
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
            y_test,
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


# ============================================================
# SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_df.to_csv(
    RESULTS_FILE,
    index=False
)

print("\n" + "=" * 70)
print("EXTERNAL TEST MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)

print("\nResults saved to:")
print(RESULTS_FILE)

print("\nExternal evaluation completed successfully.")