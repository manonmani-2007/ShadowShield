import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "dataset" / "raw"
PROCESSED_DIR = BASE_DIR / "dataset" / "processed"

EXTERNAL_FILE = PROCESSED_DIR / "external_train_normalized.csv"
SYNTHETIC_FILE = RAW_DIR / "shadowshield_dataset.csv"

OUTPUT_FILE = PROCESSED_DIR / "combined_train.csv"


def main():
    print("=" * 60)
    print("ShadowShield - Combining Training Datasets")
    print("=" * 60)

    # Load external training data
    external = pd.read_csv(EXTERNAL_FILE)

    # Load synthetic training data
    synthetic = pd.read_csv(SYNTHETIC_FILE)

    print(f"\nExternal dataset: {len(external)} samples")
    print(f"Synthetic dataset: {len(synthetic)} samples")

    # Combine
    combined = pd.concat(
        [external, synthetic],
        ignore_index=True
    )

    # Remove duplicate text entries
    before = len(combined)

    combined = combined.drop_duplicates(
        subset=["text"]
    ).reset_index(drop=True)

    duplicates_removed = before - len(combined)

    # Shuffle the dataset
    combined = combined.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)

    # Save
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    combined.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("Combined Dataset")
    print("=" * 60)

    print(f"Total samples: {len(combined)}")
    print(f"Duplicates removed: {duplicates_removed}")

    print("\nLabels:")
    print(combined["label"].value_counts())

    print("\nCategories:")
    print(combined["category"].value_counts())

    print("\nSource types:")
    print(combined["source_type"].value_counts())

    print("\nColumns:")
    print(combined.columns.tolist())

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()