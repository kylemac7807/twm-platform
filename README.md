# TWM Platform

Phase 1 pipeline for Technology Workforce Management: contract ingestion,
rate/title extraction, normalization against the TWM Role Framework, and the
Master Benchmark Ledger.

**Start here:** read `CLAUDE.md` (standing context + build order), then the
spec for whatever you're building in `specs/`. Decisions and their rationale:
`docs/requirements-and-rationale.md` (the living decision log) and
`docs/architecture-decisions.md`.

## First-time setup (M0)
1. Drop the Sept 1 corpus package contents into `corpus/` (adds
   `twm_corpus/` with fetch_frameworks.sh + download_originals.sh + earlier
   extractions).
2. `python3 corpus/scripts/v3_download.py` (and run the two Sept 1 scripts)
   → originals land under `corpus/downloads/` (gitignored).
3. `pip install -e .` · `pytest`

## Working with the Role Framework (M1)
- Tables: `taxonomy/*.csv` — edit directly (append or deprecate rows; never silently edit). `taxonomy/REPORT.md` is generated.
- Regenerate the acceptance report: `python -m twm.taxonomy.acceptance`
- Resolve a title in code: `from twm.taxonomy import TaxonomyStore; from twm.pipeline.normalize import resolve; resolve("Sr. Java Developer", TaxonomyStore.load())`
- Tests: `pytest` (normalization rules, taxonomy integrity, acceptance thresholds).
