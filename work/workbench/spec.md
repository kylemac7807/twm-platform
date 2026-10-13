# Spec: review workbench, first version

**From** `intent.md` (accepted Oct 6), the design record (`docs/architecture-components.md`, "Cross-cutting: Review workbench", decided Oct 6) and the decision log. **Written** Oct 13, 2026, in the main session; Kyle chose to build the workbench here rather than in a worker stream.

## What it is

A web application on Kyle's machine, in Python with Streamlit, that reads the ledger (`ledger.sqlite`) and the documents it points at, and lets one analyst do three jobs:

1. **See the documents** as intake sorted them: each file, its class, confidence and evidence, its readiness, its contract set, and the system's own flags.
2. **Work the queues**: every place the system abstained. Decide an item once, with a name and a reason; the decision is recorded, the item closes, and every ledger row that was waiting on it is updated.
3. **Inspect any rate**: from a ledger row to the page it came from, with the box drawn on the page image, beside the row's extraction and resolution.

The fourth job in the design record, the executive views, waits for findings, which do not exist yet.

## Who uses it

One analyst role (decided Oct 6). For now that is Kyle. The analyst types a name once per session; there is no login. The audit record is designed so a second reviewer role can be added later without changing data: every decision table has `decided_by` and `decided_at`, plus `reviewed_by` and `reviewed_at`, nullable, unused in this version.

## Inputs

- `ledger.sqlite`: tables `documents`, `runs`, `observations`, `mapping_decisions`, `review_queue` (schema in `src/twm/pipeline/ledger.py`).
- The document files at the paths in `documents.path`, for page images (PDF) or the table position (web page).
- The taxonomy (`TaxonomyStore`) for the pick-lists: roles grouped by family, the four bands, the location values.

## Outputs

- **Decisions**, written to the ledger through `ledger.py` methods only, never to the taxonomy CSVs.
- **An export of decisions to codify** (`pending_codification()`), one row per decision that has not yet been applied to the taxonomy, so the main session can append the mapping or location rule with the `twm-change-the-taxonomy` skill and mark it applied. The workbench never edits `taxonomy/`.

## Screens

### 1. Documents

A table of every registered document: filename, class and confidence, class evidence (the quoted snippet), true type versus declared extension, readiness, page count, contract numbers, contract set (root document named), flags. Grouped by contract set. Nothing editable here except "confirm classification" and "confirm contract-set link", which are queue items of kind `intake` and appear in the queue screen too.

### 2. Queues

One list per kind: **title** (unresolved or ambiguous titles), **location** (place names awaiting a decision), **intake** (weak classification, suggested links), **extraction** and **reading** (notes from those stages). Each item shows the system's own words for why it abstained.

Rules for the title queue, which carries almost all the volume:

- Items are **grouped by observed title within a client**: one decision resolves every ledger row with that title for that client (resolve once, applied to humans).
- Sorted by **rows unlocked**, the number of live, uncounted ledger rows the decision would affect, largest first, so the first decisions clear the most rows.
- A decision is: a canonical role (from the pick-list, grouped by family) or "no role, leave flagged"; a band or **unbanded** (the default; no band without evidence, Kyle's rule); an optional technology tag; and a **reason** (required, free text). The page quote and the rate are shown beside the item so the analyst decides with the evidence in view.
- **Bulk**: the analyst can select several items and apply one decision when the titles are the same role (for example, three long cyber-security labels that are all security architects). Each item still gets its own decision row.
- Ambiguous dual-grade items ("Project Manager I / Test Leads") are shown with both halves and the analyst picks one, or splits it into two titles.

For the location queue: the place name, the client, the rows affected; the decision is onshore / nearshore / offshore and a reason, recorded for that client only.

For intake: confirm or correct the class; confirm or reject a suggested contract-set link.

What happens when a decision is saved (all inside `ledger.py`):

1. A row in a new table `queue_decisions` (see below).
2. For a title decision: a row in `mapping_decisions` with `method = "analyst"`, `decided_by` = the name; every live observation with that title and client gets `canonical_role_id`, `twm_band`, `band_source = "analyst"`, `resolution_status = "resolved"`, `resolution_confidence = 1.0`, and `counted` recomputed by the same gate as before (extraction confidence ≥ 0.90 and a usable scan).
3. For a location decision: `attr_location` set on those observations, `needs_location_review` cleared.
4. The queue item's `status` becomes `resolved`.
5. Nothing is deleted; a decision can be reversed by a new decision, which supersedes the old one in `queue_decisions` (`superseded_by`), never edits it.

### 3. Inspect

Pick a document, then a row (filterable by title, counted / not counted, status). The screen shows: the page image with the row's box drawn (PDF), or the table row and column (web page); the quote; the extracted fields as stated (rate, currency, unit, period, location, level); the resolution (role, band, source of the band, confidence, status); and the decision history for that title if any. Read only.

### 4. Decisions to codify

A table of decisions not yet applied to the taxonomy, with a download as CSV in the shape the taxonomy CSVs expect (`title_mappings.csv` columns for title decisions; `location_rules.csv` columns for location decisions). A button marks a decision applied once the main session has appended it.

## Data additions (additive only; existing lines of `ledger.py` untouched)

New table at the end of `SCHEMA`:

```
queue_decisions(id, queue_id, kind, client, item, decision_json, reason, decided_by, decided_at,
                reviewed_by, reviewed_at, applied_to_taxonomy INTEGER DEFAULT 0, applied_at, superseded_by)
```

New methods at the end of the `Ledger` class: `queue_items(kind, status)`, `queue_groups_for_titles()` (grouped by title and client with rows-unlocked counts), `decide_title(...)`, `decide_location(...)`, `decide_intake(...)`, `decision_history(item)`, `pending_codification()`, `mark_applied(decision_id)`, `observation(obs_id)`, `documents_by_set()`. Each is a plain function over SQL; the screens call them and nothing else.

## Rules it must obey

- **Honest screens**: what the system found, what it declined to decide, and the system's own reason, verbatim. No field is prefilled with a guess; the band default is unbanded.
- **Precision first**: a decision needs a reason; bulk apply needs an explicit confirmation showing the count.
- **Rates and money**: shown as stated with currency and unit; the reporting-currency value only when the ledger holds a conversion, with its rate and date.
- **Data boundary**: the workbench reads and writes one local ledger; it has no network calls, no model calls, no export other than the codification CSV and the page images it renders.
- **Flag then codify**: decisions become rules only through the export and the main session; the workbench never writes to `taxonomy/`.
- **Append, never overwrite**: decisions supersede, observations are updated in place only in the resolution columns (the extraction columns are never touched), and the old decision stays.

## Out of scope for this version

Executive views and findings; a second reviewer role (columns reserved only); login and identity; running the pipeline from the screen (documents are run from the command line for now); editing extracted values (an extraction the analyst disagrees with is a queue item of kind `extraction` whose decision is "re-run" or "exclude", recorded, not edited); Azure deployment.

## Done when

Kyle opens the workbench on the existing ledger, sees the Texas and G-Cloud contract sets, works the 19 open title items and sees each decision land in the ledger with his name and reason and the affected rows become counted, clicks the traced Texas row and sees page 8 with the box drawn, downloads the decisions-to-codify CSV; the ledger methods and the codification export are covered by tests; `review.md` is written; and `tests/PROMISES.md` exists (test strategy B29, folded in here).
