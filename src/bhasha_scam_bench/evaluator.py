"""Dataset loading, baseline predictions, and classification metrics."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Iterable

LABELS = {"scam", "legitimate"}
REQUIRED_COLUMNS = {"id", "language", "category", "label", "text"}


def load_dataset(path: str | Path) -> list[dict[str, str]]:
    """Load and validate a benchmark CSV."""
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
        for line, row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in row.items() if key is not None}
            if not row.get("id") or not row.get("text"):
                raise ValueError(f"Line {line}: id and text must not be empty")
            if row["id"] in seen:
                raise ValueError(f"Line {line}: duplicate id {row['id']!r}")
            if row.get("label") not in LABELS:
                raise ValueError(f"Line {line}: label must be one of {sorted(LABELS)}")
            seen.add(row["id"])
            rows.append(row)
    if not rows:
        raise ValueError("Dataset has no examples")
    return rows


def baseline_predict(text: str) -> str:
    """Return a deliberately simple, explainable demo prediction.

    This is not a security product or a reliable detector. It exists only so
    users can run the benchmark immediately and replace it with their own
    model or rules.
    """
    value = text.casefold()
    indicators = (
        "otp", "upi pin", "collect request", "kyc", "suspend", "blocked",
        "install apk", "screen share", "anydesk", "verify now", "claim reward",
        "\u0913\u091f\u0940\u092a\u0940", "\u0915\u0947\u0935\u093e\u0908\u0938\u0940", "\u0916\u093e\u0924\u093e \u092c\u0902\u0926", "\u0924\u0941\u0930\u0902\u0924 \u0932\u093f\u0902\u0915", "\u092f\u0942\u092a\u0940\u0906\u0908 \u092a\u093f\u0928",
        "\u0c12\u0c1f\u0c3f\u0c2a\u0c3f", "\u0c15\u0c47\u0c35\u0c48\u0c38\u0c40", "\u0c16\u0c3e\u0c24\u0c3e \u0c28\u0c3f\u0c32\u0c3f\u0c2a\u0c3f", "\u0c32\u0c3f\u0c02\u0c15\u0c4d \u0c24\u0c46\u0c30\u0c35\u0c02\u0c21\u0c3f", "\u0c2f\u0c42\u0c2a\u0c40\u0c06\u0c08 \u0c2a\u0c3f\u0c28\u0c4d", "\u0c2a\u0c3f\u0c28\u0c4d \u0c28\u0c2e\u0c4b\u0c26\u0c41",
    )
    return "scam" if any(term in value for term in indicators) else "legitimate"


def predictions_from_baseline(rows: Iterable[dict[str, str]]) -> dict[str, str]:
    return {row["id"]: baseline_predict(row["text"]) for row in rows}


def load_predictions(path: str | Path) -> dict[str, str]:
    """Load predictions from a CSV with id,prediction columns."""
    result: dict[str, str] = {}
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        if not {"id", "prediction"}.issubset(columns):
            raise ValueError("Predictions CSV must contain id and prediction columns")
        for line, row in enumerate(reader, start=2):
            example_id = (row.get("id") or "").strip()
            prediction = (row.get("prediction") or "").strip()
            if not example_id:
                raise ValueError(f"Line {line}: id must not be empty")
            if example_id in result:
                raise ValueError(f"Line {line}: duplicate prediction id {example_id!r}")
            if prediction not in LABELS:
                raise ValueError(f"Line {line}: prediction must be one of {sorted(LABELS)}")
            result[example_id] = prediction
    if not result:
        raise ValueError("Predictions file has no rows")
    return result


def _scores(actual: list[str], predicted: list[str]) -> dict[str, float | int]:
    tp = sum(a == p == "scam" for a, p in zip(actual, predicted))
    tn = sum(a == p == "legitimate" for a, p in zip(actual, predicted))
    fp = sum(a == "legitimate" and p == "scam" for a, p in zip(actual, predicted))
    fn = sum(a == "scam" and p == "legitimate" for a, p in zip(actual, predicted))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    total = len(actual)
    return {
        "examples": total,
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
    }


def evaluate(rows: list[dict[str, str]], predictions: dict[str, str]) -> dict[str, object]:
    """Compute overall and per-language scores; reject incomplete predictions."""
    expected_ids = {row["id"] for row in rows}
    missing = expected_ids - predictions.keys()
    extra = predictions.keys() - expected_ids
    if missing or extra:
        pieces = []
        if missing:
            pieces.append(f"missing predictions for {len(missing)} example(s)")
        if extra:
            pieces.append(f"unknown prediction ids: {', '.join(sorted(extra)[:5])}")
        raise ValueError("; ".join(pieces))

    actual = [row["label"] for row in rows]
    predicted = [predictions[row["id"]] for row in rows]
    by_language: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in rows:
        by_language[row["language"]].append((row["label"], predictions[row["id"]]))
    language_scores = {
        language: _scores([a for a, _ in pairs], [p for _, p in pairs])
        for language, pairs in sorted(by_language.items())
    }
    return {"overall": _scores(actual, predicted), "by_language": language_scores}
