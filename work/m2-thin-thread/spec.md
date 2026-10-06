# Spec: M2, the thin thread

**Drafted** October 6, 2026 from `docs/architecture-components.md` and the decision log. Status: **draft.**

## Inputs

- The Texas DIR Accenture family on disk: `corpus/manifests/v3_downloads/v3_gov/081` to `087` (master agreement, SOW, Exhibit 2 financial provisions, Attachment 2.1 pricing and volumes, service-level definitions, key personnel, template). Native PDFs.
- The Accenture G-Cloud 15 card: `corpus/twm_corpus/UK_GCloud15_Accenture_service_page_ORIGINAL.html` (a web page with the rate table) as the second family.
- The taxonomy tables in `taxonomy/`.
- A model credential from `.env` (`ANTHROPIC_API_KEY`), never committed.

## Stages and what each must do (from the design record)

| Stage | Must | Interface |
|---|---|---|
| Intake | Register each file with a permanent id and content fingerprint; sniff true type from content; classify (MSA, SOW, amendment, rate card, invoice, timesheet, unknown); link into a family only on strong evidence (contract number on the page), else suggest and flag; record readiness (text layer usable or scan) | `twm.pipeline.ingest`: `register(path) -> DocumentRecord` |
| Reading | Produce text, tables and layout with page and position per element, a confidence per element, and a quality grade | `twm.pipeline.read`: `Reader` protocol; `LocalPdfReader` now, `AzureDocumentIntelligenceReader` later |
| Extraction | Fill `RateCardExtraction` or `SOWExtraction` per section via the model wrapper; abstain on uncertain fields; verify every number against the page; retry a malformed answer at most twice then flag; split long documents by section | `twm.pipeline.extract`: `extract(doc, reading, classification) -> Extraction`; `twm.llm.call(contract, prompt_bundle, model_config)` |
| Normalization | Rules and mapping table (built), then similarity search over resolved titles, then model confirmation above the confidence floor, then flag; place names flagged; bands by precedence, unbanded when no evidence | `twm.pipeline.normalize.resolve` (extend with the model step) |
| Ledger | Append rows, never overwrite; supersede on re-run; rate as stated plus derived reporting-currency column with the reference rate and date; source class; confidence and scan quality on every row | `twm.pipeline.ledger`: SQLite file for the prototype, same schema as PostgreSQL later |
| Report | Plain-language run summary for Kyle; one traced row | `twm.pipeline.run`: `run_family(paths) -> RunReport` |

## Rules this work must obey (skills)

`twm-precision-first`, `twm-rates-and-money`, `twm-data-boundary`, `twm-flag-then-codify`, `twm-run-a-document`. In particular: no default band, no classified place names, no silent currency conversion, no secret in version history, no third-party document committed.

## Field-level scoring

For the Accenture pricing exhibit, Claude drafts a hand-verified answer sheet (`twm-gold-answer-sheet`) of the labour categories and year-1 rates; Kyle or an analyst checks a sample of rows against the PDF. The run reports per-field agreement (title, rate, unit, currency, position) against that sheet. This is the first gold record and the seed of M3.

## Acceptance

1. Both families run with the same code and no per-document changes.
2. Every ledger row traces to a page and position that, when opened, shows the number.
3. No row has a defaulted band or an auto-classified place name.
4. The run report lists every flag with a one-sentence reason.
5. Tests cover intake sniffing and classification, reading positions, extraction verification and abstention, the model wrapper's retry and validation, ledger append and supersede, and the end-to-end run on a small fixture.
6. Model calls are logged (model, tokens, latency, validation pass or fail), the raw material for the Claude-versus-GPT comparison in M3.

## Out of scope

Workbench screens, Azure services, benchmarking across vendors, invoices and timesheets, synthetic data, Power BI.
