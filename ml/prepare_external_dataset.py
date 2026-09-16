import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "dataset" / "raw"
PROCESSED_DIR = BASE_DIR / "dataset" / "processed"

TRAIN_FILE = RAW_DIR / "training_external.csv"
TEST_FILE = RAW_DIR / "testing_external.csv"

TRAIN_OUTPUT = PROCESSED_DIR / "external_train_normalized.csv"
TEST_OUTPUT = PROCESSED_DIR / "external_test_normalized.csv"


def normalize_dataset(input_file, output_file):
    df = pd.read_csv(input_file)

    # Keep only the information relevant to ShadowShield
    normalized = pd.DataFrame()

    normalized["text"] = df["Original"].fillna("").astype(str)

    normalized["label"] = (
        df["Need Anonymization"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({
            "yes": "sensitive",
            "no": "safe"
        })
    )

    normalized["category"] = normalized["label"].map({
        "safe": "safe",
        "sensitive": "pii"
    })

    normalized["subcategory"] = "unknown"

    normalized["source_type"] = "external"

    normalized["contains_sensitive"] = (
        normalized["label"] == "sensitive"
    )

    # Remove rows with invalid labels
    normalized = normalized[
        normalized["label"].isin(["safe", "sensitive"])
    ]

    # Remove empty prompts
    normalized = normalized[
        normalized["text"].str.strip() != ""
    ]

    # Remove exact duplicate prompts
    normalized = normalized.drop_duplicates(
        subset=["text"]
    ).reset_index(drop=True)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    normalized.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print("=" * 60)
    print(f"Processed: {input_file.name}")
    print("=" * 60)
    print(f"Rows: {len(normalized)}")
    print("\nLabels:")
    print(normalized["label"].value_counts())

    print("\nColumns:")
    print(normalized.columns.tolist())

    print(f"\nSaved to:")
    print(output_file)


def main():
    normalize_dataset(
        TRAIN_FILE,
        TRAIN_OUTPUT
    )

    normalize_dataset(
        TEST_FILE,
        TEST_OUTPUT
    )


if __name__ == "__main__":
    main()