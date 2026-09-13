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
