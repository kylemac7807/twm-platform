# Plan: M2, the thin thread

**Drafted** October 6, 2026. Status: **accepted by Kyle, October 6, 2026.** No code before the API key exists (action item C8).

## Order of work, each step a commit with tests

| # | Step | Files | Proves |
|---|---|---|---|
| 1 (done Oct 6) | **Document record and intake.** Register, fingerprint, sniff, classify by filename and first-page text, link families on contract numbers, readiness grade | `src/twm/pipeline/ingest.py`, `src/twm/pipeline/models.py` (DocumentRecord), `tests/test_ingest.py` | the seven Accenture files become one family; a fake-PDF viewer page is caught |
| 2 (done Oct 6) | **Reading interface and local reader.** Protocol plus a native-PDF reader that returns text blocks and tables with page and bounding box, quality grade | `src/twm/pipeline/read.py`, `tests/test_read.py` | a rate in the pricing exhibit can be located by page and position |
| 3 | **Model wrapper.** One `call()` with model name from config, temperature 0, JSON validated against the task contract, retry at most twice, every call logged; reads the key from `.env`; a fake model for tests | `src/twm/llm.py`, `tests/test_llm.py` | swap-ability and the call log |
| 4 | **Extraction.** Task contracts as pydantic models (from `specs/extraction-task-contracts.md`), prompts per contract, sectioning, page verification of every number, abstention | `src/twm/pipeline/extract.py`, `src/twm/pipeline/contracts.py`, `prompts/`, `tests/test_extract.py` | the pricing grid becomes verified rows; an invented number is rejected in a test |
| 5 | **Normalization model step.** Similarity over resolved titles (local embeddings or simple token similarity for the prototype), model confirmation with disambiguation notes, confidence floor, write-back to the mapping table as `method=model` | `src/twm/pipeline/normalize.py` (extend), `tests/test_normalize_model.py` | an unseen Accenture title is resolved with reasoning, or flagged |
| 6 | **Ledger.** SQLite schema (observations, documents, runs, mapping decisions), append and supersede, derived reporting-currency column with reference rate | `src/twm/pipeline/ledger.py`, `tests/test_ledger.py` | re-running a family supersedes rather than duplicates |
| 7 | **End-to-end run and report.** `run_family()`, run report in plain language, one traced row, field-level agreement against the answer sheet | `src/twm/pipeline/run.py`, `evals/gold/tx_tss699_att21.jsonl` (drafted), `tests/test_run.py` | both families run with no code change |
| 8 | **Review.** Independent pass for bugs, rule violations, data-boundary leaks; fix; record | `work/m2-thin-thread/review.md` | |

## Risks and how they are handled

- **The pricing exhibit's text layer is messy** (the earlier Deloitte PDF shifted columns). Step 2 keeps bounding boxes so the verification in step 4 can reject shifted values; the answer sheet in step 7 measures the damage.
- **Model cost and non-determinism.** Temperature 0, cached calls keyed by content hash, a spending limit on the key. The fake model keeps tests free.
- **Scope creep toward the workbench.** The report is text and a spreadsheet export, nothing more.
- **Key not present.** Steps 1, 2, 6 and all tests run without it; steps 3 to 5 and 7 need it. Claude stops before step 3 if the key is missing and says so.

## What Kyle sees along the way

After step 1: the family listing. After step 4: the first verified rate rows. After step 7: the run report and the traced row. Each as a short message with one example, not a log.

## Estimated effort

About two working sessions of Claude time once the key exists, with Kyle's reading at the three points above.
