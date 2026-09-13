# Evaluation Harness Specification

Purpose: field-level, precision-weighted measurement of extraction and normalization quality, designed to run federated later (in client tenants, only scores leaving). Locally it runs on the public corpus + synthetic documents.

## Gold set format (`evals/gold/*.jsonl`)

One JSON object per document: the document reference + the hand-verified correct `RateCardExtraction`/`SOWExtraction` output (same pydantic schemas — gold IS a valid contract instance), plus `verified_by` and `verified_date`. Building gold records from consulting verification work is the production pattern; here, build them by hand-checking ~20 corpus documents (start: 5 G-Cloud cards, Texas Appendix C, Michigan/Deloitte, 3 EDGAR MSAs).

## Metrics (implement in `src/twm/evals/metrics.py`)

Per FIELD, not per document:
- For table extraction: row alignment first (match gold rows to predicted rows by title+level key), then per-field precision/recall/F1 across: rate_value, currency, rate_unit, level_raw, observed_title, location_raw, effective_date, rate_qualifier.
- `rate_value` correctness = exact decimal match after unit normalization; a wrong-but-close number is WRONG (this is money).
- Report per document genus (rate card / MSA / SOW / scanned) — models fail differently by genus.

## Precision weighting

Headline score per field: `F_beta` with **beta = 0.25** (precision weighted ~16x recall) for anything feeding a leakage claim; standard F1 reported alongside. Rationale: a false leakage claim in front of a vendor is existential; a miss is caught next refresh. The operational consequence: tune confidence thresholds so the pipeline abstains (flags) rather than guesses — measure and report **abstention rate** and **accuracy-given-nonabstention** as first-class numbers.

## Comparison runs

`evals/run.py --models claude-x,gpt-y --gold evals/gold/ --report evals/reports/<date>.md`
Output table: model × field × {P, R, F0.25, abstention}. Persist every report in git — the trend IS the asset. Same harness, unchanged, is what later runs inside client tenants (federated: only these reports leave).

## Thresholds to calibrate (open items from the requirements doc)

- TitleResolution confidence floor for auto-accept (start 0.75; calibrate on gold).
- Embedding similarity floor for candidate retrieval (start 0.85 cosine).
- Both get calibration curves (threshold vs precision) in the first eval report.
