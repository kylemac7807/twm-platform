---
name: twm-gold-answer-sheet
description: Building a hand-verified answer sheet (gold record) for one document in the evaluation sample. Use when preparing or checking evaluation data for M3.
---
# Build a hand-verified answer sheet

Gold records use the same typed schema as extraction output (`specs/eval-harness-spec.md`): gold IS a valid contract instance, plus `verified_by` and `verified_date`.

1. Claude drafts the full record from the document, every field with its page position.
2. A human (Kyle or an analyst) checks each field against the page: correct, wrong, or missing. Rates must match exactly; a close number is wrong.
3. Record the verifier, the date, and any field the verifier could not determine (left empty, noted). Never fill a gold field by inference.
4. Store in `evals/gold/` as JSONL, one object per document; never commit the source document.
5. Budget guide (Oct 5, 2026): rate card 30 to 60 minutes; pricing exhibit 1 to 2 hours; agreement terms 1 to 2 hours. The sample is about 20 documents covering each type and the five demo documents first.
