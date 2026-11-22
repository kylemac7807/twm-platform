# Kickoff brief: the full run of the document library

Tell a session to read this file and follow it. Packaged November 22, 2026; nothing here has been started. Action item B30. Kyle McNamara decides.

## Read first, in this order

`CLAUDE.md`; `docs/how-we-build.md`; the skills `twm-build-task`, `twm-run-a-document`, `twm-precision-first`, `twm-rates-and-money`, `twm-write-for-kyle`; `docs/library-summary.md` (the approved description of the library: use its numbers and words); `work/volume-run/intent.md` (the estimate, the staging and the decisions waiting for Kyle); `work/contract-terms/review.md` (what the engine does and its known limits); `specs/rate-conditions.md`; `docs/action-items.md` items B30, B32, B33, B35, B36, B37.

## The artifact chain applies

Write `work/volume-run/spec.md` and `plan.md` and tell Kyle the plan is ready. No run of more than the sets named below before he says go. Finish with `review.md`.

## Before any bulk run, in this order

| # | What | Why | Size |
|---|---|---|---|
| 1 | Intake labels for web-format contracts (B35) | 155 of the 163 SEC master agreements are mislabelled | about an hour |
| 2 | Rate tables inside a contract file go to the rate-table reader, whatever the file's label (B37) | Today only a file labelled rate card is read that way. The Florida price sheets and the Michigan Knowledge Services rate card sit at the back of full contracts, and a seven-page price sheet read as prose overruns one model answer | about an hour, with tests; re-base any regression replay whose calls change |
| 3 | Party names: drop state-of-formation phrases (B37) | "a Delaware limited liability partnership" yields the party "Delaware Limited" | minutes, with a test |
| 4 | Term reading for web-format contracts (B36) | the engine skips a saved web page; an SEC agreement is one | about half a day |
| 5 | The daily stop of 200 model calls (`DAILY_CALL_STOP` in `src/twm/pipeline/run.py`) | at 200 a day the run takes two weeks | Kyle sets the number |
| 6 | Ledger writes: stop re-reading every live row after each insert in `run.py` | 1,648 rows took minutes | small |

## The first contract sets (chosen November 22 with the engine's no-cost tools)

All are PDFs with a text layer. Calls and cost are before job-title questions, at about 7 cents a call.

| Order | Contract set | Files | What it holds | Why it is next | Needs | Calls, cost |
|---|---|---|---|---|---|---|
| 1 | Florida Dept of Management Services and Remy Corporation | `corpus/manifests/v3_downloads/v3_gov/088_*` (173 pages) | Exhibit E price sheet, pages 166 to 172: about 280 rows of job family, job title and level, each with the state's ceiling rate and the vendor's price | The first of ten Florida staffing vendors (088 to 097) priced against one job list: one client, many vendors, the same roles. The closest thing in the library to a bank's rate card | item 2 above | about 12, $1 |
| 2 | State of Michigan and Knowledge Services | `.../055_*` (238 pages) | Schedule B pricing from page 89: job category, job title, skill level 1 to 5, maximum bill rate; a 1 percent state fee and a 0.85 percent vendor-funded programme fee | A staffing programme's full rate card, a new kind of vendor, and two fees the inventory has no name for | item 2 above | about 18, $1.50 |
| 3 | Texas DIR and Deloitte & Touche, contract DIR-CPO-4882 | `.../062_*` to `066_*` | A cooperative contract; its pricing index is discounts off list (10 percent by service), no dollar rates | A second vendor at a client we hold. Runs today, unchanged. Pass `--vendor` | nothing | about 6, $0.45 |
| 4 | Texas DIR and Accenture, contract DIR-CPO-5153 | `.../067_*` to `070_*` | The same kind of contract: 5 percent off list by role, no dollar rates | The same vendor and client as the set we hold, a second contract. The vendor resolves from the ledger without `--vendor`. Runs today, unchanged | nothing | about 10, $0.70 |
| 5 | State of Michigan and Accenture | `.../051_*` (479 pages) | One cumulative file of change notices and statements of work; milestone pricing | A second client for Accenture. Runs today; pass `--vendor` | nothing | about 19, $1.35 |

Then fill the pilot out to about 15 sets so every kind is covered: an SEC agreement (after item 4), a UK contract, an invoice and timesheet set, a New York or federal multi-vendor award.

How to run one set, from the project folder (back up `ledger.sqlite` first; the main ledger is brought up to date under B33):

```
.venv/Scripts/python.exe -m twm.pipeline.run corpus/manifests/v3_downloads/v3_gov/062_*.pdf corpus/manifests/v3_downloads/v3_gov/063_*.pdf corpus/manifests/v3_downloads/v3_gov/064_*.pdf corpus/manifests/v3_downloads/v3_gov/065_*.pdf corpus/manifests/v3_downloads/v3_gov/066_*.pdf --vendor "Deloitte & Touche LLP" --client "Texas DIR"
```

Report each run to Kyle the way `twm-run-a-document` says: what the set was, the disclosure check, rows, questions raised and why, one traced row and one traced condition.

## Spend

The engine's key draws on Kyle's Ultra API credit: $200 a month, renewing on the 5th, no rollover, with his own balance behind it. The full run is estimated at $130 to $180. Say what a run will cost before starting it; stop and report at the daily limit Kyle sets; the run already stops at the first credit refusal. Every answer is cached, so a repeat costs nothing.

## After the full run

Update `docs/library-summary.md`: the "read by the engine" column, and the "likely to contain rates" range replaced by the measured count. Add a regression replay for a handful of sets. Hand the draft answer sheets in `evals/gold/` to the Evaluation (B26). Update the action list and the decision log.

## Writing

Plain language, one example per new term. "Contract set", never family. "Document library", never corpus. "Contracted rate", never cap. Describe the library by what the documents are, never by who collected them or when.
