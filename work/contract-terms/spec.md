# Spec: contract terms

**Drafted October 13, 2026** by the contract-terms worker session, from `intent.md`, `docs/architecture-components.md` (1.1 intake, 1.3 extraction, 1.5 ledger), `specs/extraction-task-contracts.md` (contract 2) and the thin-thread review. Status: **for Kyle to read with the plan.**

## What will be built

Four things, in the order the parallel plan lists them.

1. **Term reading.** The pipeline reads the words of a master agreement, statement of work or amendment and records what they say about money and identity: who the parties are, the contract number, the effective date, the term, the pricing model, and every commercial term (a discount, an escalation clause, an invoicing rule, a credit, an expense policy, a minimum commitment, a volume tier, a most-favoured-customer promise). Each is a short quote copied from one page, with the page and the position on it. Example: from the Texas Exhibit 2, page 12, "The rates for the contract year immediately prior to the extension period shall be used to determine the Charges during the extension period", typed as an escalation term.
2. **Two new ledger tables.** `contract_terms` holds the facts and terms above, one row each, with page, box and quote. `named_resources` holds the people or roles a document names (the Texas key-personnel attachment names them), with page and quote. Both follow the ledger's rules: append, supersede on re-run, confidence on every row, verified on the page or not stored.
3. **Vendor and client from the document.** Intake reads the parties from the first pages (Texas page 1: "Between the Texas Department of Information Resources and Accenture LLP"; Michigan page 1: "CONTRACTOR  DELOITTE CONSULTING LLP") and writes a vendor guess with its evidence on the document record. The run uses it for every ledger row when the operator passes no `--vendor`; the command-line value remains an override. When the rules cannot tell which party is the vendor, the field stays empty and the document is flagged.
4. **Every contract year as its own observation.** The Texas pricing grid prices eight years, two service types and two locations for each title; the thin thread kept year 1 of one block (53 rows) because the model said the grid was too large for one answer. The table is split by location block and service type before the model sees it (four calls instead of one on page 8), the model still reads year 1 only, and the software copies years 2 to 8 from the same table row, each verified on the page with its own cell position. The year expansion sits behind a run flag (`--all-periods`) so the default report stays readable.

If time remains: a reference exchange-rate module (`fx.py`) that reads one Bank of Canada daily rate for a date and feeds the existing derived column. Never applied unless the run asks for it.

## Inputs

- A registered document (intake record) and its reading (pages, lines with positions, tables with cell positions), as today.
- The three permitted documents for real model calls: Texas 081 (master agreement, 110 pages), Texas 084 (Exhibit 2 financial provisions, 25 pages), Michigan Deloitte MiIntegrate (one cumulative file, 378 pages: 18 change-notice covers, the contract, statements of work; 41 pages are image-only and are skipped). The rest of the Texas set (082, 083, 085, 086, 087) may be run too; 085 is where the contract-year rows come from.

## Outputs

- Ledger rows in `contract_terms` and `named_resources`, each with run, document, contract set, vendor, client, source class, type, verbatim value, confidence, verified flag, status (`recorded` or `flagged`), page, box, quote.
- Observation rows as today, now carrying the derived vendor, and (with the flag) one row per contract year.
- A plain run report: the parties, contract number, term and effective date per document; the commercial terms found, grouped by type with their pages; named resources; what the model would not commit to, in its words; where the vendor came from; model calls and tokens.
- A draft answer sheet per document for the Evaluation (`evals/gold/<doc>.terms.draft.jsonl`), marked unverified.

## Rules it must obey

- **Precision first.** A term is stored only if its quote is found on the claimed page (or on a neighbouring page of the same section, in which case the page is corrected and the correction noted). A quote the software cannot find is not stored; it goes to the review queue with what the model claimed. A term below the confidence floor is stored as `flagged`, visible but not relied on. The model's abstentions are recorded in its own words. No field is ever filled with a default.
- **Rates and money.** Rate rows found in prose (Michigan's not-to-exceed hourly rates) go through the same page verification as table rows and are stored as stated with currency and unit. Expanded contract-year rows are copies of printed cells, never computed from an escalation percentage. "Contracted rate", never "cap".
- **Data boundary.** Everything stays in the local ledger. Named resources are people's names: local tier only, shown in the workbench, never exported or summarised.
- **Shared modules are extended, not edited.** `contracts.py`, `models.py` and `ledger.py` gain fields, classes, tables and methods at the end; nothing existing changes. Every addition is listed in `status.md`.
- **Model spend.** Pages are selected by commercial-term signals before any call, so a 378-page file costs a bounded number of calls (a per-document cap, reported when it bites). A persisted daily call count stops the run at 200 calls and says so.
- **Observations, not conclusions.** Nothing here decides whether a term was honoured; that is reconciliation, later.

## Out of scope

Reading invoices or timesheets; scoring against a hand-verified answer sheet (the Evaluation); any taxonomy or normalizer change (requests go in `status.md`); the workbench screens that will show these rows; OCR for the 41 image-only Michigan pages; currency conversion applied to any row.
