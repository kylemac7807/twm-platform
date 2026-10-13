# Status: contract terms (stream A)

Updated at every commit by the worker session in the `contract-terms` worktree. The main session reads this; Kyle decides.

**Last updated:** October 13, 2026. Spec and plan written, revised after Kyle's challenge on overfitting (vendor resolved once through a table, a no-spend rehearsal over the whole library, general table rules), then extended with the Azure evolution table, the rate-conditions inventory (`specs/rate-conditions.md`, new file) and Kyle's decision to store terms now and derive in findings. Waiting for Kyle's go.

## Done

- Read everything the brief lists. Confirmed the three permitted documents are real PDFs by their first bytes (`%PDF`): Texas 081 (110 pages), Texas 084 (25 pages), Michigan Deloitte MiIntegrate (378 pages, 41 image-only).
- Tests pass in this worktree with the main folder's environment (118).
- `spec.md` and `plan.md` written.

## In progress

- Nothing. Code starts when Kyle says go.

## Blocked

- Nothing.

## Decisions Kyle made in this stream (for the main session to log in `docs/requirements-and-rationale.md`)

| Date | Decision |
|---|---|
| Oct 13, 2026 | Contract terms are stored as observations beside the rates; a condition never changes a stored rate. Effective contracted rates (escalation percentage, volume tier, period discount applied) are derived columns, labelled derived and citing the clause, built in the findings work with the savings stacking, not in extraction. |
| Oct 13, 2026 | An inventory of the fine print that makes rates opaque or incomparable is kept and grown by flag-then-codify: `specs/rate-conditions.md`, label "rate conditions" (proposed; Kyle may rename). The extraction prompt types terms with its keys. Kyle confirmed the six groups (expenses and pass-throughs; what an hour, a day or a month is; the structure of the rate; discounts, credits and commitments; scope, change and exit; transparency and governance) and the 48 conditions; each key carries its group in the code. |
| Oct 13, 2026 | The move to Azure Document Intelligence is captured now, in `work/contract-terms/spec.md` ("How this evolves on Azure"), so the page-and-position pointer on every term, verification on the page and the one facts record survive the rebuild. Hand-off to B28. |

## Questions for Kyle

Two, in `plan.md` under "Two things to confirm". Both have a stated default; silence keeps the default.

## Additions to shared modules (planned; this list becomes the record as each lands)

| Module | Addition | Status |
|---|---|---|
| `contracts.py` | `ContractFact` record (fact type, verbatim value, source position, confidence); `facts` list and `condition_key` (from `specs/rate-conditions.md`) on the existing term record; `confidence` on `NamedResource` | planned |
| `models.py` | `party_candidates` (names found on the first pages, each with its evidence) at the end of `DocumentRecord` | planned |
| `ledger.py` | tables `contract_terms`, `named_resources` and `vendor_names` at the end of `SCHEMA`; methods `supersede_terms`, `add_term`, `add_named_resource`, `live_terms`, `live_named_resources`, `term_counts`, `lookup_vendor`, `record_vendor_name` at the end of the class | planned |

## Packages needed

- None. (`httpx` for the optional exchange-rate step is already installed.)

## Taxonomy rules to codify (for the main session)

- None yet. Expected after the Michigan run: Deloitte's 18 role labels in "Table 5: Other Services" (for example "CM Specialists", "Programmer/Developers") will show which titles the mapping table lacks.

## Model spend

- Calls so far in this stream: 0.
