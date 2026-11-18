# BhashaScamBench

A small, transparent benchmark for evaluating scam-message classifiers on **synthetic** India-focused examples in English, Hindi, and Telugu.

> **Research prototype, not a consumer security product.** The bundled examples are synthetic and too small to measure real-world accuracy. Never use this score to decide that a real message, link, payment request, or sender is safe.

## What it does

- Provides a documented CSV benchmark with scam and legitimate examples across three languages.
- Runs a simple demonstration ruleset out of the box.
- Scores your own predictions with accuracy, precision, recall, F1, confusion counts, and per-language results.
- Uses only the Python standard library at runtime; no message is uploaded anywhere.

It does not connect to SMS, WhatsApp, email, a bank, or UPI. It does not fetch or open links, and it is not an operational scam detector.

## Install

Python 3.10 or newer is required.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install git+https://github.com/contact-tsandeep/bhasha-scam-bench.git
```

To install from a source checkout instead:

```powershell
python -m pip install .
```

## Run the bundled example

```powershell
bhasha-scam-bench evaluate
```

Machine-readable output:

```powershell
bhasha-scam-bench evaluate --json
```

Run the included demo rules explicitly:

```powershell
bhasha-scam-bench evaluate --baseline
```

The baseline is intentionally basic and exists to make the benchmark immediately runnable. Its score is not a product claim.

## Evaluate your own classifier

Create a CSV with one prediction for every example ID:

```csv
id,prediction
EN-S-001,scam
EN-L-001,legitimate
```

Use exactly `scam` or `legitimate` as the prediction, then run:

```powershell
bhasha-scam-bench evaluate --predictions predictions.csv
```

Use another compatible dataset with `--dataset path/to/messages.csv`. It must contain `id,language,category,label,text`; `expected_signals` and `provenance` are optional descriptive fields. Labels must be `scam` or `legitimate`, and IDs must be unique. Predictions must cover every dataset row exactly once.

## Dataset fields

| Field | Meaning |
|---|---|
| `id` | Stable example identifier |
| `language` | `en`, `hi`, or `te` for the bundled examples |
| `category` | Scenario family, such as `upi_collect` or `credential_request` |
| `label` | Intended class: `scam` or `legitimate` |
| `text` | Synthetic message text; all example links use the reserved `example.invalid` domain |
| `expected_signals` | Human-readable cues a test author intended to represent |
| `provenance` | How the example was created; bundled rows are `synthetic_example` |

## Contribute safely

Read [CONTRIBUTING.md](CONTRIBUTING.md) before adding examples. Submit synthetic examples or examples with clear permission and careful redaction. Do not submit real phone numbers, names, account details, OTPs, UPI IDs, payment links, or private messages. New examples should be reviewed by a fluent speaker and include provenance.

See [SECURITY.md](SECURITY.md) for responsible disclosure and [LICENSE](LICENSE) for reuse terms.
