# Status: contract terms (stream A)

Updated at every commit by the worker session in the `contract-terms` worktree. The main session reads this; Kyle decides.

**Last updated:** October 13, 2026. Spec and plan written; waiting for Kyle's go.

## Done

- Read everything the brief lists. Confirmed the three permitted documents are real PDFs by their first bytes (`%PDF`): Texas 081 (110 pages), Texas 084 (25 pages), Michigan Deloitte MiIntegrate (378 pages, 41 image-only).
- Tests pass in this worktree with the main folder's environment (118).
- `spec.md` and `plan.md` written.

## In progress

- Nothing. Code starts when Kyle says go.

## Blocked

- Nothing.

## Questions for Kyle

Two, in `plan.md` under "Two things to confirm". Both have a stated default; silence keeps the default.

## Additions to shared modules (planned; this list becomes the record as each lands)

| Module | Addition | Status |
|---|---|---|
| `contracts.py` | `ContractFact` record (fact type, verbatim value, source position, confidence); `facts` list and `subtype` on the existing term record; `confidence` on `NamedResource` | planned |
| `models.py` | `counterparty_guess`, `client_guess`, `party_evidence` at the end of `DocumentRecord` | planned |
| `ledger.py` | tables `contract_terms` and `named_resources` at the end of `SCHEMA`; methods `supersede_terms`, `add_term`, `add_named_resource`, `live_terms`, `live_named_resources`, `term_counts` at the end of the class | planned |

## Packages needed

- None. (`httpx` for the optional exchange-rate step is already installed.)

## Taxonomy rules to codify (for the main session)

- None yet. Expected after the Michigan run: Deloitte's 18 role labels in "Table 5: Other Services" (for example "CM Specialists", "Programmer/Developers") will show which titles the mapping table lacks.

## Model spend

- Calls so far in this stream: 0.
