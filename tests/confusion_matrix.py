import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Load the external holdout dataset
data = pd.read_csv("dataset/processed/external_test_normalized.csv")

# Text and labels
X = data["text"]
y = data["label"]

# Load the same TF-IDF configuration used by the final model
vectorizer = TfidfVectorizer(
    max_features=50000,
    ngram_range=(1, 2),
    sublinear_tf=True
)

# IMPORTANT:
# The final model was trained on the combined training dataset.
train_data = pd.read_csv("dataset/processed/combined_train.csv")

X_train = train_data["text"]
y_train = train_data["label"]

# Train TF-IDF on training data only
X_train_tfidf = vectorizer.fit_transform(X_train)

# Transform external holdout using the same vectorizer
X_test_tfidf = vectorizer.transform(X)

# Train final Logistic Regression model
model = LogisticRegression(
    max_iter=1000,
    random_state=42
)

model.fit(X_train_tfidf, y_train)

# Predict external holdout
y_pred = model.predict(X_test_tfidf)

# Confusion matrix
cm = confusion_matrix(
    y,
    y_pred,
    labels=["safe", "sensitive"]
)

print("\nConfusion Matrix:")
print(cm)

print("\nExpected:")
print("True Negative  (Safe → Safe):", cm[0][0])
print("False Positive (Safe → Sensitive):", cm[0][1])
print("False Negative (Sensitive → Safe):", cm[1][0])
print("True Positive  (Sensitive → Sensitive):", cm[1][1])

# Create figure
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Safe", "Sensitive"]
)

fig, ax = plt.subplots(figsize=(7, 6))
disp.plot(ax=ax, cmap="Blues", values_format="d", colorbar=False)

plt.title("ShadowShield - Final Model Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("Actual Label")
plt.tight_layout()

# Save high-quality image for report
output_path = "dataset/evaluation/confusion_matrix.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print("\nConfusion matrix saved to:")
print(output_path)

plt.show()