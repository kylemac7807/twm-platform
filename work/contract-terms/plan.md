# Plan: contract terms

**Drafted October 13, 2026.** Status: **waiting for Kyle to say go.** No code is written until then. Five minutes of reading; the spec beside it has the detail.

## Order of work, each step a commit with tests

| # | Step | Files | Proves |
|---|---|---|---|
| 1 | **Shared-module additions** (add only, at the end): a `ContractFact` record (party, contract number, effective date, expiry, term, governing agreement, pricing model, amendment number, contract value) with page and quote, shaped so Azure's prebuilt contract model can fill it later; a `facts` list and a `subtype` note on the existing term record; a confidence on named resources; `party_candidates` on the document record; three ledger tables, `contract_terms`, `named_resources` and `vendor_names`, with add, supersede, lookup, list and count methods | `contracts.py`, `models.py`, `ledger.py`, `tests/test_contract_terms.py` | terms append and supersede like rates; every addition listed in `status.md` |
| 2 | **Term reading, and the library rehearsal.** Pages chosen by a short signal vocabulary kept as data (payment, invoice, discount, escalation, credit, minimum, term, effective, between the parties, change notice) and grouped into sections of at most six pages, all through the reading interface; a rewritten prompt with the schema, one example per term type and the rule "quote only what is printed"; every quote checked on its page word by word, position taken from the lines that carry it; a quote not found is queued, not stored. Then the selector runs over all 419 documents in the library with no model, and the page counts per document are recorded in `work/contract-terms/rehearsal.md` | `extract.py`, `rehearsal.md` | offline: an invented quote is rejected; a quote on the neighbouring page is corrected and noted; across the library, no document sends every page and the ones that send none are listed with a reason |
| 3 | **Vendor resolved once.** Intake records every party name printed on the first pages as a candidate with its evidence ("between X and Y"; a party line with a corporate suffix such as LLP, Inc., Ltd). The run resolves the vendor through the `vendor_names` table; an unknown name goes to the review queue, and `--vendor` answers it and writes the answer to the table. The client is `--client`, standing in for the deployment setting on a bank's site; it is never derived | `ingest.py`, `run.py`, `ledger.py` | Texas and Michigan each ask once, then resolve from the table on every later run; a document naming two unknown companies queues both and stores no vendor |
| 4 | **Routing and the first real runs.** Master agreements, statements of work, amendments and rate cards with no rate table go through term reading; results land in the two tables; the report lists facts, terms by type with pages, named resources, abstentions; a draft answer sheet is written; a daily call count persisted under `.cache/llm` stops the run at 200. Run Texas 081 and 084, fix what breaks the way the thin thread did, then Michigan through the same code unchanged | `run.py` | the run report Kyle reads: parties, contract number, term, every term with a page, for Texas and for Michigan |
| 5 | **Every contract year, by two general table rules.** A large table is split by its block rows and column groups before the model reads it (on the Texas grid: four calls on page 8 instead of one); where a heading row names periods, the model reads the first period and the software copies the rest from the same table row, each verified on the page with its cell position; behind `--all-periods`; the report states base rows and expanded rows separately. Run on Texas 085 and compare with the 53 rows | `extract.py`, `run.py` | offline: one base row expands to eight rows whose values are all printed on page 8; a changed cell is rejected; both rules are a no-op on the G-Cloud tables and the Michigan payment tables; real: the row count and one traced year-5 row |
| 6 | *If time remains:* **reference exchange rate.** One Bank of Canada daily rate for a currency and date, cached, fetched only with `--fx`; feeds the existing derived column | new `fx.py` | offline with a saved response; never applied silently |
| 7 | **Review.** Independent pass for bugs, rule violations and data-boundary leaks; fix; record | `work/contract-terms/review.md` | |

## Model spend (expected)

| Document | Pages | Calls, first pass |
|---|---|---|
| Texas 081 master agreement | 110 | 3 to 5 |
| Texas 084 Exhibit 2 | 25 | 4 to 5 |
| Texas 087 key personnel | 3 | 1 |
| Michigan Deloitte, cumulative | 378 (41 image-only skipped) | 15 to 20, capped |
| Texas 085 pricing grid, split | 11 | 4, plus a few title resolutions |

About 30 to 40 calls for a full pass; repeats come from the cache. Hard stop at 200 in a day, enforced by the run itself.

## Risks and how they are handled

- **Overfitting to the two public sets.** The library rehearsal in step 2 (419 documents, no spend) is the check that page selection generalizes; the vendor table in step 3 replaces name heuristics with decisions that accumulate; the table rules in step 5 are tested to do nothing where they do not apply. Nothing in the code names Texas, Michigan, Accenture or Deloitte; the tests may.
- **A 378-page file.** Page selection and a per-document cap keep the calls bounded; the report says how many signal pages were left unread so Kyle can raise the cap.
- **The model quotes loosely** (punctuation, line breaks, a hyphen). Verification matches the words in order, not the characters; what still fails is queued with the model's claim.
- **Page numbers off by one** at section edges. A quote found on a neighbouring page of the same section is accepted with the page corrected and the correction noted; further away is rejected.
- **Long answers truncate** on a dense page. Sections stay small; the prompt asks for at most 25 terms per answer and the rest under abstained; a truncated answer is flagged, never half-stored.
- **Michigan's class is "amendment"** because a change notice is page 1 of a cumulative file. Routing treats master agreement, statement of work and amendment alike, so the class only labels; the facts from each change notice keep their own page, so the chain is visible.
- **The vendor rule misfires** on a document naming two companies. It then leaves the field empty and flags; the operator's `--vendor` still works.

## When this moves to Azure

Nothing in steps 2 to 5 touches a PDF library; all of it works on the reading interface. Azure Document Intelligence then replaces the local reader behind that interface: its layout output gives section headings and paragraphs, which replace keyword page selection with real sections; its tables carry the same cell positions the splitting and expansion rules use; and its prebuilt contract model fills the facts record (parties, contract id, effective, expiration and renewal dates) as an alternative to the frontier model, with the evaluation harness deciding which fills it better.

## What Kyle sees along the way

After step 2: the rehearsal table, one line per document class, with the outliers named. After step 4: the run report for Texas 081 and 084, then for Michigan, each as a short message with one traced term. After step 5: the row count with and without the flag and one traced year-5 row. Each step's questions, if any, go in `status.md`.

## Two things to confirm (defaults stated; silence means the default)

1. Contract-year rows are **off by default** behind `--all-periods`, as the parallel plan says; on for the volume run. Say if you want them on now.
2. Step 5 also brings in the remote-location block and the managed-services columns of the Texas grid (the model declined them in the thin thread because the table was too large in one go). That roughly quadruples the base rows before the year expansion. Say if you want year expansion only.
