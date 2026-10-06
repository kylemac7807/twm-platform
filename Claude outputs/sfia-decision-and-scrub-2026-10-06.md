# SFIA — decision memo and scrub plan

**Date:** October 6, 2026 · **From:** Cowork · **For:** Kyle, and Claude Code (action items B16–B19)
**Decision recorded in:** `docs/requirements-and-rationale.md` §3.1 and the decision log (v0.5). `docs/action-items.md` updated: A4 and D1 done, C3 closed, D4 done, B16–B19 added. `docs/architecture-decisions.md` §5 amended.

## The decision

**SFIA is excluded from the TWM Role Framework and from the product by default — not just from the prototype.** The `crosswalk_sfia` column and the "SFIA as crosswalk" idea are retired. No SFIA framework documents are held in the repo or read by anyone building the framework. An SFIA view can only ever be a client-scoped, separately licensed add-on negotiated with that client's consent to the Foundation's reporting terms. No legal read and no SFIA Foundation conversation are needed to exclude it.

## Licence terms, verified from the primary source

Sources: sfia-online.org "Choosing a licence"; *SFIA General Terms 2024* (PDF). Read October 6, 2026.

| Term | What the Foundation says |
|---|---|
| Partner Licence | £2,000/year single country; Global Partner £4,000/year; Accredited Consultant £300/year per named individual |
| Free Corporate licence | "does not permit commercial exploitation of SFIA in relation to the sale or provision of services" |
| Royalty | "Royalties shall normally be based on 5% of the standard price for the product" |
| What the royalty applies to | "a specifically-priced product or service that is dependent on SFIA. Examples: a product that assesses people's SFIA skills, **a skills database containing SFIA information**, a publication containing significant amounts of information from SFIA" |
| Reporting | "Licensees shall send to The Foundation a quarterly report of sales, showing customers' names, prices and royalties due" |
| Derivative works | "Licensees shall not use SFIA content, structure, or methodology to create, publish, or promote derivative frameworks, without explicit authorisation" |

The figures carried since September 1 were right; the reporting and derivative-works clauses were new and decisive.

## Why, in order of weight

1. **Reporting.** Quarterly disclosure of customer names and prices to a third party in the UK cannot coexist with a consortium agreement whose premise is that nothing about a member leaves. No fee level fixes this.
2. **Royalty scope.** The Foundation's own example — "a skills database containing SFIA information" — describes a benchmark ledger carrying SFIA codes. "Crosswalk only" does not escape it; the moment SFIA codes sit in a product column, the product is in scope.
3. **Derivative works.** The clause covers "structure, or methodology", not just text. The cleanest protection for the TWM Role Framework is the provenance it already has — O*NET, DDaT, TBIPS, Texas DIR, G-Cloud — and tests that fail if SFIA appears. Keeping SFIA documents out of the repo keeps that provenance clean.
4. **Market relevance.** SFIA is a UK/Australian public-sector convention. Penetration among Canadian and US banks is low. What TWM gives up is a convenience for a possible future UK or Australian client, not a core capability.

## What stays, deliberately

- **Public vendor rate cards that use "SFIA 1–7" as level labels** (the G-Cloud 14 cards). Reading a label printed in a public vendor document is not using SFIA content. The band-crosswalk rows for those labels stay, renamed as a vendor level scheme (B17).
- **Public documents that mention SFIA** stay in the corpus as source data.

## The scrub — what Cowork found (October 6 inventory)

No SFIA framework files exist on disk — the repo is already clean of SFIA *content*. What remains are *references* in TWM's own artifacts:

| Where | What | Action | Owner |
|---|---|---|---|
| `src/twm/taxonomy/models.py`, `taxonomy/canonical_roles.csv` | `crosswalk_sfia` field/column (empty) | Remove; record in taxonomy version note | Claude Code (B16) |
| `tests/test_taxonomy.py` | `test_sfia_crosswalk_empty_pending_licence`; SFIA label rows in band test | Replace with a "no SFIA string anywhere in taxonomy content" test; keep label rows under the renamed scheme | Claude Code (B16) |
| `src/twm/taxonomy/heldout.py`, `acceptance.py`, `scripts/seed_taxonomy_v0.py`, `src/twm/pipeline/ingest.py`, `contracts.py` | Mentions in comments/strings | Reword to "vendor level label" where they refer to G-Cloud 14 | Claude Code (B16) |
| `taxonomy/band_crosswalk.csv` | 7 rows, scheme "SFIA", notes "licensing pending" | Rename scheme; rewrite notes to "public vendor rate-card level label" | Claude Code (B17) |
| `specs/role-framework-v0-spec.md`, `specs/extraction-task-contracts.md` | Column spec and table rows; example "SFIA 4" | Same relabelling | Claude Code (B17) |
| `CLAUDE.md` data rule and crosswalk list | "crosswalk only, not the spine", "SFIA-pending" | Replace with the exclusion rule | Claude Code (B18) |
| `.claude/skills/twm-change-the-taxonomy`, `twm-new-document-source` | One mention each | Reword to "excluded" | Claude Code (B18) |
| `docs/corpus-catalog.md`, `docs/corpus-sources-and-demo-set.md`, `corpus/twm_corpus/MASTER_CATALOG.md`, `corpus/.../01_skills_frameworks/manifest.md`, `corpus/collected_by_kyle_2026-01/README.md` | "pending licence decision" language and SFIA download leads | Reword to "excluded"; delete the SFIA download lead | Cowork on request, or Claude Code (B18) |
| 13 × `corpus/gc15_ratecards/*_SFIA_ratecard.md` | Misnamed — G-Cloud 15 cards are not SFIA-based | Rename to `_GC15_ratecard.md`; update references | Claude Code (B19) |
| 14 × G-Cloud 14 extraction files `*_SFIA_ratecard*.md` | Vendor cards genuinely use SFIA levels | Keep name only if the vendor's card title says SFIA; otherwise `_GC14_` | Claude Code (B19) |
| `Claude outputs/` (handoff, review, requirements copy, retrieval status) | Historical Cowork documents | Leave as history; they are dated | — |
| `.cache/llm/*.json` | Model-call cache entries containing the word | Leave; cache, not an artifact | — |

## What this closes on the action list

A4 (SFIA decision) — done. C3 (register for SFIA files) — closed; do not register. D1 (this memo) — done. D4 (Design Decisions §5) — done. Open question 1 in the requirements doc — closed. The legal read and the Foundation conversation never enter the list.
