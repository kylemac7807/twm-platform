# Spec: contract terms

**Drafted October 13, 2026** by the contract-terms worker session, from `intent.md`, `docs/architecture-components.md` (1.1 intake, 1.3 extraction, 1.5 ledger), `specs/extraction-task-contracts.md` (contract 2) and the thin-thread review. Status: **for Kyle to read with the plan.**

## What will be built

Four things, in the order the parallel plan lists them.

1. **Term reading.** The pipeline reads the words of a master agreement, statement of work or amendment and records what they say about money and identity: who the parties are, the contract number, the effective date, the term, the pricing model, and every commercial term (a discount, an escalation clause, an invoicing rule, a credit, an expense policy, a minimum commitment, a volume tier, a most-favoured-customer promise). Each is a short quote copied from one page, with the page and the position on it. Example: from the Texas Exhibit 2, page 12, "The rates for the contract year immediately prior to the extension period shall be used to determine the Charges during the extension period", typed as an escalation term.
2. **Two new ledger tables.** `contract_terms` holds the facts and terms above, one row each, with page, box and quote. `named_resources` holds the people or roles a document names (the Texas key-personnel attachment names them), with page and quote. Both follow the ledger's rules: append, supersede on re-run, confidence on every row, verified on the page or not stored.
3. **Vendor from the document, resolved once.** Intake finds the party names printed on the first pages and records them as candidates with their evidence. The vendor is then a lookup in a vendor-name table in the ledger (observed name, the vendor it stands for, who decided, when), the same resolve-once pattern as titles: "Accenture LLP", "Accenture Inc." and "Accenture (UK) Ltd" resolve to one vendor after one decision each. A name the table does not know goes to the review queue; the operator's `--vendor` answers it and the answer is written to the table, so the question is never asked twice. The client is not derived at all: on a bank's site the client is the deployment, a setting, and `--client` stands in for that setting here.
4. **Every contract year as its own observation.** The Texas pricing grid prices eight years, two service types and two locations for each title; the thin thread kept year 1 of one block (53 rows) because the model said the grid was too large for one answer. Two general table rules fix this. A large table is split before the model sees it, by its block rows (a row with text in the first cell and nothing else, such as a location heading) and by its column groups (a heading row above the period headings, such as a service type). And where a heading row names periods (contract years, fiscal years, date ranges), the model reads only the first period and the software copies the others from the same table row, each verified on the page with its own cell position. Both rules do nothing on a table that has no blocks or no periods, and that is tested on the G-Cloud and Michigan tables. The expansion sits behind a run flag (`--all-periods`) so the default report stays readable.

If time remains: a reference exchange-rate module (`fx.py`) that reads one Bank of Canada daily rate for a date and feeds the existing derived column. Never applied unless the run asks for it.

## Built for a bank's site, proved on public documents

This is a training run. The two public contract sets are where the code is proved; nothing in it may know those documents. Three things make that true.

- **The keys that make lateral benchmarking possible are what this task puts on every row.** Vendor (resolved once), contract set, and period, beside the role, band, location and technology the normalizer already supplies. With those keys the ledger can be cut the way a bank needs it: the same role across all its vendors, and the same vendor across its own contracts and years. The terms table adds the words beside the numbers (which vendor gives a volume discount, which contract escalates, which invoices in arrears), so a comparison across vendors can be argued from the contract, not only from the rate. Comparison against the public training data is a by-product; the cuts are the product.
- **Everything the model reads comes through the reading interface, never from a PDF library.** Page selection, quote verification, table splitting and period expansion all work on the reading's pages, lines, positions and table cells. That interface is the seam where Azure Document Intelligence replaces the local reader; the section "How this evolves on Azure" below says what carries over and what must not be lost.
- **The fine print is inventoried, not improvised.** `specs/rate-conditions.md` (started today at Kyle's request) lists the devices vendors use to keep a rate opaque or incomparable: travel inside or outside the rate, what a day is, volume tiers, period discounts, prompt-pay discounts, escalation in the grid or by percentage, blended rates, not-to-exceed rates, and so on, each with a real example from the library where one exists. The extraction prompt types every term with a key from that inventory or `other` in the model's words; `other` goes to the review queue and, once named, into the inventory. A test keeps the inventory and the code's key list identical.
- **The rules that pick pages and names are small, visible and tested across the whole library, not on two files.** The commercial-term signal list is a short vocabulary kept as data. Before any model call, the page selector runs over every document in the library (419 files, no model, no spend) and the counts are recorded: how many pages each document would send, and which documents would send none or everything. That is the generalization check; the two public sets are then the proof that the end-to-end path works.

## How this evolves on Azure (so nothing is lost in the move)

Kyle, October 13, 2026: capture how the term reading changes when the application moves to Azure Document Intelligence, so the key points survive the rebuild. What stays, what changes, and what must not be lost:

| Today, on Kyle's machine | On Azure, with Document Intelligence | Must not be lost |
|---|---|---|
| Pages are chosen by a signal vocabulary (payment, invoice, discount, escalation, term) because the local reader sees only lines | Document Intelligence returns the document's own section headings and paragraphs, so the pipeline sends the "Fees", "Invoicing" and "Term" sections by name; the signal vocabulary stays as the fallback for a document with no headings | The rehearsal across the library is re-run with the Azure reader before it goes live; the counts must be as good or better |
| Every term carries page, box and quote from the local reader's lines | Document Intelligence gives a page and a bounding polygon for every paragraph, cell and word; those fill the same `source_ref` (page, box, quote), so clicking a term lights up the clause on the original page exactly as a rate lights up its cell | The pointer to the original page and position on every term and every rate, always, in the same shape |
| The software checks every quote word by word against the page text before storing it | Unchanged: Document Intelligence reads, the model quotes, the software checks. A better reader does not remove the check | Verify on the page, abstain otherwise, never guess |
| The 41 image-only pages of the Michigan file are skipped | Document Intelligence reads them (built-in OCR) and grades each word's confidence, which flows to scan quality on the row | Confidence and scan quality gate what counts |
| Parties, contract number and dates are read by the frontier model | The prebuilt contract model can fill the same facts record; the evaluation harness decides which fills it better, field by field | The facts record is one contract; models are swapped behind it, never hard-wired |
| Tables arrive as cells with positions from the local reader | Tables arrive as cells with positions from Document Intelligence; the splitting and period-expansion rules run unchanged | One table rule set, tested on both readers |
| The model wrapper calls the Anthropic API directly | The same wrapper points at Microsoft Foundry; the cache, the call log and the daily stop stay | Model name is configuration |

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
- **The gate comes first (decided by Kyle, October 13, 2026).** Before a contract set is benchmarked or anything from it is contributed, its disclosure, confidentiality and benchmarking clauses are read and the set is marked restricted, cleared or unchecked at the top of the run report; restricted and unchecked go to the review queue. The clauses are group G of the inventory. Public contracts are a biased sample of what private contracts say, so the check runs on every engagement, not on assumptions from the library.
- **Store now, derive in findings (decided by Kyle, October 13, 2026).** A condition never changes a stored rate. The effective contracted rate for a year or a volume (an escalation percentage applied, a volume tier applied) is a derived column, labelled derived and citing the clause, built once in the findings work with the savings stacking, not in extraction. This task stores the terms with their pages so that work has what it needs.

## Out of scope

Reading invoices or timesheets; scoring against a hand-verified answer sheet (the Evaluation); any taxonomy or normalizer change (requests go in `status.md`); the workbench screens that will show these rows; OCR for the 41 image-only Michigan pages; currency conversion applied to any row.
