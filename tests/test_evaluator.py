import csv
import tempfile
import unittest
from pathlib import Path

from bhasha_scam_bench.cli import _default_dataset
from bhasha_scam_bench.evaluator import (
    baseline_predict,
    evaluate,
    load_dataset,
    load_predictions,
    predictions_from_baseline,
)


class EvaluatorTests(unittest.TestCase):
    def test_bundled_dataset_loads_and_has_three_languages(self):
        rows = load_dataset(_default_dataset())
        self.assertEqual(len(rows), 36)
        self.assertEqual({row["language"] for row in rows}, {"en", "hi", "te"})

    def test_baseline_flags_english_upi_pin_request(self):
        self.assertEqual(baseline_predict("Enter your UPI PIN to receive a refund"), "scam")

    def test_baseline_flags_hindi_otp_request(self):
        self.assertEqual(baseline_predict("अपना OTP भेजें"), "scam")

    def test_baseline_flags_telugu_upi_pin_request(self):
        self.assertEqual(baseline_predict("మీ యూపీఐ పిన్ నమోదు చేయండి"), "scam")

    def test_evaluation_reports_per_language_metrics(self):
        rows = load_dataset(_default_dataset())
        report = evaluate(rows, predictions_from_baseline(rows))
        self.assertEqual(set(report["by_language"]), {"en", "hi", "te"})
        self.assertEqual(report["overall"]["examples"], 36)
        self.assertGreaterEqual(report["overall"]["recall"], 0.0)

    def test_missing_prediction_is_rejected(self):
        rows = load_dataset(_default_dataset())
        with self.assertRaisesRegex(ValueError, "missing predictions"):
            evaluate(rows, {})

    def test_duplicate_dataset_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.csv"
            path.write_text(
                "id,language,category,label,text" + chr(10) + "1,en,test,scam,example" + chr(10) + "1,en,test,scam,example2" + chr(10),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate id"):
                load_dataset(path)

    def test_prediction_csv_loads(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "predictions.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["id", "prediction"])
                writer.writerow(["EN-S-001", "scam"])
            self.assertEqual(load_predictions(path), {"EN-S-001": "scam"})


if __name__ == "__main__":
    unittest.main()
