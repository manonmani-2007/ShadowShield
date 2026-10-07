import json
import time
from pathlib import Path
from collections import Counter

from backend.detector import analyze_prompt


BASE_DIR = Path(__file__).resolve().parents[1]

PROMPT_FILE = BASE_DIR / "dataset/evaluation/long_prompt_1000.txt"
GROUND_TRUTH_FILE = BASE_DIR / "dataset/evaluation/ground_truth.json"
RESULTS_FILE = BASE_DIR / "dataset/evaluation/evaluation_results.json"


def evaluate():

    prompt = PROMPT_FILE.read_text(encoding="utf-8")

    ground_truth = json.loads(
        GROUND_TRUTH_FILE.read_text(encoding="utf-8")
    )

    # Run the complete ShadowShield detector.
    start = time.perf_counter()
    result = analyze_prompt(prompt)
    latency_ms = (time.perf_counter() - start) * 1000

    expected = {
        (item["type"], item["line"], item["value"])
        for item in ground_truth["findings"]
    }

    predicted = {
        (item["type"], item["line"], item["value"])
        for item in result["detections"]
    }

    true_positives = len(expected & predicted)
    false_positives = len(predicted - expected)
    false_negatives = len(expected - predicted)

    precision = (
        true_positives / (true_positives + false_positives)
        if true_positives + false_positives
        else 0
    )

    recall = (
        true_positives / (true_positives + false_negatives)
        if true_positives + false_negatives
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0
    )

    # Check that every annotated sensitive value has
    # been removed from the redacted document.
    #
    # This is a simple leakage check, not a complete
    # redaction-accuracy measurement.

    remaining_values = [
        item
        for item in ground_truth["findings"]
        if item["value"] in result["redacted_text"]
    ]

    redaction_leakage_count = len(remaining_values)

    expected_counts = dict(
        Counter(
            item["type"]
            for item in ground_truth["findings"]
        )
    )

    report = {
        "lines_analyzed": result["lines_analyzed"],
        "characters_analyzed": result["characters_analyzed"],
        "ground_truth_findings": len(expected),
        "detected_findings": len(predicted),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "latency_ms": latency_ms,
        "risk_level": result["risk_level"],
        "action": result["action"],
        "risk_score": result["risk_score"],
        "expected_counts": expected_counts,
        "detected_counts": result["finding_counts"],
        "redaction_leakage_count": redaction_leakage_count,
        "remaining_sensitive_values": remaining_values,
        "false_positive_findings": [
            {
                "type": item[0],
                "line": item[1],
                "value": item[2]
            }
            for item in sorted(predicted - expected)
        ],
        "missed_findings": [
            {
                "type": item[0],
                "line": item[1],
                "value": item[2]
            }
            for item in sorted(expected - predicted)
        ]
    }

    RESULTS_FILE.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print("\n" + "=" * 65)
    print("SHADOWSHIELD LONG-PROMPT EVALUATION")
    print("=" * 65)

    print(f"\nLines analyzed:       {report['lines_analyzed']}")
    print(f"Characters analyzed:  {report['characters_analyzed']}")
    print(f"Ground-truth findings:{report['ground_truth_findings']:>8}")
    print(f"Detected findings:    {report['detected_findings']:>8}")

    print("\nDETECTION METRICS")
    print("-" * 65)

    print(f"True positives:       {true_positives}")
    print(f"False positives:      {false_positives}")
    print(f"False negatives:      {false_negatives}")

    print(f"\nPrecision:            {precision:.4f}")
    print(f"Recall:               {recall:.4f}")
    print(f"F1 score:             {f1:.4f}")

    print(f"\nDetection latency:    {latency_ms:.2f} ms")

    print("\nRISK ASSESSMENT")
    print("-" * 65)

    print(f"Risk level:           {result['risk_level']}")
    print(f"Action:               {result['action']}")
    print(f"Risk score:           {result['risk_score']}")

    print("\nFINDINGS BY CATEGORY")
    print("-" * 65)

    for category in sorted(
        set(expected_counts) | set(result["finding_counts"])
    ):
        expected_count = expected_counts.get(category, 0)
        detected_count = result["finding_counts"].get(category, 0)

        print(
            f"{category:25}"
            f"Expected: {expected_count:<4}"
            f"Detected: {detected_count}"
        )

    print("\nREDACTION CHECK")
    print("-" * 65)

    print(
        f"Ground-truth values still present: "
        f"{redaction_leakage_count}"
    )

    if redaction_leakage_count == 0:
        print("Leakage check: PASS")
    else:
        print("Leakage check: FAIL")

    print("\nFALSE POSITIVES")
    print("-" * 65)

    for item in report["false_positive_findings"]:
        print(item)

    if not report["false_positive_findings"]:
        print("None")

    print("\nMISSED FINDINGS")
    print("-" * 65)

    for item in report["missed_findings"]:
        print(item)

    if not report["missed_findings"]:
        print("None")

    print(f"\nResults saved to:\n{RESULTS_FILE}")


if __name__ == "__main__":
    evaluate()