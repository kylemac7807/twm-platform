# Plan: review workbench, first version

**Kyle reads this before any code is written** (`docs/how-we-build.md`). Written Oct 13, 2026. Each step ends with its tests passing and a commit; the pre-commit guardrails run every time.

## Steps

| # | Step | Files | Proves it |
|---|---|---|---|
| 1 | **Ledger additions.** The `queue_decisions` table and the methods in the spec, as plain functions over SQL: queue listing, title groups with rows-unlocked counts, decide title / location / intake with supersede, decision history, pending codification, mark applied, documents by contract set | `src/twm/pipeline/ledger.py` (additive: table at the end of `SCHEMA`, methods at the end of the class) | `tests/test_ledger.py` grows: a title decision resolves every row with that title and client and recomputes `counted`; the band stays unbanded unless chosen; a second decision supersedes the first and both remain; a location decision applies to one client only; codification export has the exact `title_mappings.csv` columns; nothing is written to `taxonomy/` |
| 2 | **Page rendering.** A function that returns the page image for a PDF row with the box drawn, and the table position for a web-page row | new `src/twm/workbench/render.py` (pdfplumber + Pillow) | `tests/test_workbench.py`: the Texas row on page 8 renders and the drawn box matches the stored coordinates; a web-page row returns row and column, no image |
| 3 | **The app, screens 1 and 3** (Documents, Inspect): read-only, against the real ledger | new `src/twm/workbench/app.py`, `pages/` | Streamlit's headless app test (`streamlit.testing.v1.AppTest`) opens each screen on a small fixture ledger without error and shows the expected document names and the traced row |
| 4 | **Screen 2, Queues**: grouped title queue sorted by rows unlocked, the decision form with required reason and unbanded default, bulk apply with confirmation, location and intake queues | `src/twm/workbench/pages/queues.py` | App test: deciding a fixture title through the screen produces the same ledger state as step 1's direct call; bulk apply on two items writes two decision rows |
| 5 | **Screen 4, Decisions to codify**: table, CSV download, mark applied | `src/twm/workbench/pages/codify.py` | App test: export rows match `pending_codification()`; mark applied removes the row |
| 6 | **Run it on the real ledger with Kyle**: the 19 open titles, the traced row, the export. Fix what the real data exposes | | the "done when" in the spec, checked live |
| 7 | **Test strategy (B29)**: one-line plain-English description on every test (docstrings), a generator that writes `tests/PROMISES.md` grouped by area, the guardrail regenerates it when `tests/` changes; the rules "every decision becomes a test, every bug becomes a test, every document run becomes a regression check" added to `how-we-build.md`; the Texas and G-Cloud counts (53 rows / 48 counted, 430 / 410) as regression checks | `scripts/promises.py`, `scripts/git-hooks/pre-commit`, `docs/how-we-build.md`, `tests/test_regression.py` | `tests/PROMISES.md` lists every test; the regression checks pass |
| 8 | **Review**: an independent pass for bugs, rule violations (honesty of screens, no taxonomy writes, no network), and what was left | `work/workbench/review.md` | |

## How to run it (after step 3)

```bash
.venv/Scripts/python.exe -m streamlit run src/twm/workbench/app.py -- --ledger ledger.sqlite
```

It opens in the browser at `http://localhost:8501`. No network beyond your own machine.

## Risks

- **Streamlit re-runs the script on every click.** Decisions must be written in one call and the screen re-read from the ledger, never held in memory; the ledger methods are the only state. Covered by step 1's design.
- **Page images for large PDFs are slow** on first render; cache rendered pages per document and page in `.cache/pages/` (ignored by git).
- **The real queue is small (19 titles)**, so bulk apply and rows-unlocked sorting will look trivial today; they are designed for the volume run (B30), when Kyle estimates 300–400 title decisions.
- **Two streams touch `ledger.py`.** Contract-terms adds its own tables and methods at the end; this plan does the same. The main session merges; a textual overlap at the end of the file is expected and mechanical.

## Not in this plan

Findings and executive views; a second reviewer; login; running the pipeline from the screen; the Azure deployment of the workbench. Each is a later task with its own intent.

## Time

Steps 1 to 5 are one long run (a few hours of my time, none of yours). Step 6 is a session with you. Step 7 is the hour Kyle set aside; step 8 is an hour of mine.
