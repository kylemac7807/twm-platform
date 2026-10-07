---
name: twm-change-the-taxonomy
description: Adding or changing a canonical role, family, title mapping, band crosswalk row, tech tag or location rule in taxonomy/*.csv. Use for any taxonomy edit.
---
# Change the taxonomy

Rules: mappings and rules are **appended or deprecated, never silently edited**. The seed script is provenance only; edit the CSVs directly. SFIA is excluded from the product (requirements §3.1); no taxonomy content may come from it. Technology never appears in a role name outside Packaged Applications. Management tiers are roles, not bands.

Steps:
1. Make the change in the CSV. For a new role: id in snake_case, family must exist, definition and disambiguation notes written **for the resolve-once model** (how to tell it from its neighbours), crosswalks where known.
2. For a changed mapping: set the old row `status=deprecated`, add the new row with `version_added` and `reviewer`.
3. Run `.venv/Scripts/python.exe -m pytest -q` (integrity tests) and `.venv/Scripts/python.exe -m twm.taxonomy.acceptance` (regenerates `taxonomy/REPORT.md`; the pre-commit hook does this too).
4. Check the report: no ambiguous titles; all rate grids still band-monotonic; note any change in the resolved share.
5. Log a non-trivial change in `docs/requirements-and-rationale.md` and tell Kyle in one plain sentence what moved and why.
