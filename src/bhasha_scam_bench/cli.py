"""Command-line interface for BhashaScamBench."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluator import evaluate, load_dataset, load_predictions, predictions_from_baseline


def _default_dataset() -> Path:
    return Path(__file__).parent / "data" / "messages.csv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bhasha-scam-bench", description="Evaluate scam-message predictions on a synthetic multilingual benchmark.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = subparsers.add_parser("evaluate", help="score predictions against the benchmark")
    evaluate_parser.add_argument("--dataset", type=Path, default=_default_dataset(), help="benchmark CSV (default: bundled sample dataset)")
    group = evaluate_parser.add_mutually_exclusive_group()
    group.add_argument("--predictions", type=Path, help="CSV with id,prediction columns from your detector")
    group.add_argument("--baseline", action="store_true", help="run the included demo rules (default)")
    evaluate_parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        rows = load_dataset(args.dataset)
        predictions = load_predictions(args.predictions) if args.predictions else predictions_from_baseline(rows)
        report = evaluate(rows, predictions)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}")
        return 2

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    overall = report["overall"]
    print("BhashaScamBench - synthetic starter benchmark")
    print("This score measures this sample only; it is not a real-world safety guarantee.\n")
    print(f"Overall ({overall['examples']} examples)")
    for key in ("accuracy", "precision", "recall", "f1"):
        print(f"  {key:>10}: {overall[key]:.3f}")
    print(f"  confusion: TP={overall['true_positive']} TN={overall['true_negative']} FP={overall['false_positive']} FN={overall['false_negative']}")
    print("\nBy language")
    print(f"  {'language':<12} {'n':>3} {'accuracy':>10} {'precision':>10} {'recall':>10} {'f1':>8}")
    for language, scores in report["by_language"].items():
        print(f"  {language:<12} {scores['examples']:>3} {scores['accuracy']:>10.3f} {scores['precision']:>10.3f} {scores['recall']:>10.3f} {scores['f1']:>8.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
