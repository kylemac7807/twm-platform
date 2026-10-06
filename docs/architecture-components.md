# TWM platform — components, requirements and design

**A living document, started October 5, 2026.** This is the running record of the architecture walkthrough Kyle and Claude Code are doing one component at a time. Each component gets the same five headings: what it does, what goes in, what comes out, build or rent, and what the demo shows. Decisions made here are also logged in `requirements-and-rationale.md` (the decision log); this document carries the design detail the log does not. Status words follow the decision log: **Decided**, **Directional**, **Proposed**, **Parked**.

## How the components are grouped

Grouped by Kyle's priority order of analyses (decision log, section 1.1):

| Group | Components | Status |
|---|---|---|
| **1. Core SOW analysis** (first) | Intake · Document reading · Extraction · Normalization · Ledger · Benchmarking | Intake designed Oct 5; normalization built (M1); others to design |
| **2. Invoices to timecards to SOWs** (second) | Reconciliation (reuses intake and extraction) | To design |
| **3. HR-system link** (third, parked) | Identity matching across SOW, timesheet, invoice and HR record | Parked |
| **Cross-cutting** | Findings and reporting (where the stacked savings tranches live) · Review workbench (the consultant's screen, and the home of the demo) | No spec yet |
| **Supporting** | Model gateway · Evaluation harness · Synthetic document factory · Deployment shell | Partly specified in `specs/` |

## The demo

**Purpose (Kyle, Sept 18):** a viewer sees a raw contract and follows it through the pipeline to see the benefit. The five demo documents are listed in `corpus-sources-and-demo-set.md` section 2. Each component section below says what the demo shows at that step; the review workbench section will say how the viewer sees it.

**Audience (Kyle, Oct 5, 2026): an Early Adopter CIO.** Design every step for a senior technology executive deciding whether to join the consortium: plain language, real documents, one continuous story, the money at the end.

**The story (proposed Oct 5, 2026; Kyle agreed the audience, story to confirm as components are designed):** one contract followed end to end, the Texas DIR Accenture agreement with its pricing exhibit.
1. *The raw contract* on screen: about forty roles, eight years of rates, a dense grid.
2. *Intake:* the seven files appear as one linked family under the master agreement, each labelled.
3. *Extraction:* the rate grid becomes a clean table; clicking any number highlights the exact spot on the original page.
4. *Normalization:* "API Architect Developer" becomes Software Developer, senior, technology tagged, reasoning shown; one uncertain title sits in a review queue to show the system does not guess.
5. *Benchmarking:* that role's rate placed inside the distribution of what eleven other vendors charge for the same role and seniority.
6. *Findings:* savings for that one role stacked into the three tranches, with the contract cap, the vendor's best rate and the market mid-point each shown.
7. *The total:* the same calculation rolled up across the whole contract.
*Open:* whether to add an invoice-to-timesheet reconciliation step (the Texas PUC invoice pair) as a second chapter once group 2 is designed.

---

## 1.1 Intake — **Decided** (Oct 5, 2026)

**What it does.** The front door. Every document a consultant feeds in passes through intake before anything else sees it. Intake establishes what the document is and how it relates to other documents, so everything downstream can trust it.

**What goes in.** Files as they really arrive: native PDFs, scanned PDFs, Word documents, Excel exports, emails with attachments. Large-vendor invoices often arrive as a summary PDF with the detail in a spreadsheet, and timesheets as spreadsheet exports (Cowork handoff, section 4.2), so spreadsheets are first-class inputs.

**What comes out.** One registered record per document with five things settled:

1. **Identity.** A permanent document ID and a content fingerprint, so the same file fed in twice is recognized, and every extracted value can be traced back to its source document, page and location forever (the `source_ref` rule in the task contracts).
2. **True type.** What the file actually is, found by inspecting its contents, never by its name or extension. Rule already in CLAUDE.md after two real cases in the library.
3. **Classification.** Master agreement, statement of work, amendment or change notice, rate card, invoice, timesheet, or unknown. Unknown goes to a person.
4. **Family links.** Which master agreement a SOW sits under, which contract an amendment changes, which SOW an invoice bills against. One contract is often many files (the Texas Accenture set is seven).
5. **Readiness.** Whether the text layer is usable or the file is image-only and needs the document reading stage, with a scan-quality grade.

**Decisions (Kyle, Oct 5, 2026).**
- **Linking follows the flag-then-codify pattern.** Intake links documents on its own only when the evidence is strong, such as a contract number printed on the page. Otherwise it suggests a link and flags it for the consultant to confirm. Confirmed links are recorded and reused. Same pattern as title resolution and location.
- **M2 accepts PDFs and Word documents only.** Spreadsheets and emails are added when the reconciliation work (group 2) begins, but the document record is designed from the start so that adding them changes nothing upstream.

**Build or rent.** Build. Azure supplies storage and the document reading service; nothing off the shelf knows what a SOW is or how it links to a master agreement. The classification and linking logic are TWM's.

**What the demo shows.** The consultant drops in the Texas DIR Accenture files. Intake recognizes seven documents, labels each (master agreement, SOW, pricing exhibit, service-level definitions, key personnel, template, solicitation), links them into one family under the master agreement, and flags that one needs confirmation. First visible value, before any extraction.

**Open for later.** Re-runs on a cadence: the Business Plan promises quarterly or semi-annual refreshes, so intake must recognize a re-submitted family and show what changed since last time.

---

## 1.2 Document reading — **Decided** (Oct 5, 2026)

**What it does.** Turns a registered file into something software can work with: text, tables and layout, with the page and position of every element. Intake decides what a document is; document reading makes its contents usable. Native PDF and Word files read directly; scanned contracts (common for signed copies) need optical character recognition, and quality varies with the scan.

**What goes in.** A registered document from intake, with its readiness grade.

**What comes out.** A structured reading: every paragraph, heading and table cell tagged with page number and position, with a confidence score per element, and with document structure preserved (a rate table inside an appendix is still known to be a table inside that appendix). The position tagging is what lets an extracted number highlight its source on the page (`source_ref`).

**Decisions (Kyle, Oct 5, 2026).**
- **Behind an interface, local first.** Document reading sits behind a simple interface. A basic local reader for native PDFs serves M2 and the Accenture documents; Azure Document Intelligence replaces it when TWM's subscription exists. Scanned documents (e.g. the Oklahoma Deloitte contract) wait for Azure.
- **Scan quality is a tracked attribute.** Every reading carries a quality grade that follows the data to the ledger, so a rate from a poor scan is never trusted as much as one from a native file.

**Build or rent.** Rent: Azure Document Intelligence (Cowork's service map). TWM owns only the training on top: vendor-specific document models (the Technical Approach's "Expert Models"), added only where evaluation shows a vendor's documents reading badly, never up front.

**What the demo shows.** Little, by design; it is plumbing whose value appears at extraction. One worthwhile view: a scanned page beside its reading with uncertain characters marked, to show the system knows what it does not know.

---

## Build sequence — **Decided** (Kyle, Oct 5, 2026)

Kyle asked whether to run the whole library through first to build the skills matrix, then build the demo on one contract. Agreed order:
1. **M2, one contract end to end:** the Texas DIR Accenture set through every stage. The pipeline has to exist before volume is possible.
2. **The volume run:** the whole document library through the same pipeline. Fills the ledger (so benchmarking has eleven vendors to compare against), grows the mapping table (the Business Plan's "skills matrix" is the Role Framework plus the mapping table), and produces per-document extraction scores that show where reading and extraction are weak.
3. **M3, the evaluation harness:** a hand-verified sample becomes the measuring stick. Volume alone does not make the system smarter; volume plus verified answers does. Only the mapping table grows automatically; evaluation and any vendor-specific document models need verified examples.
4. **The demo**, on the Accenture contract, with a populated ledger behind it.

---

## 1.3 Extraction — **Decided** (Oct 5 and 6, 2026)

**What it does.** Reads the structured document and pulls out the commercially important facts: parties, dates, pricing model, every row of every rate table, and commercial terms (discounts, minimum commitments, escalation, invoicing rules). Records each fact exactly as written, with a pointer to its source position. Does not interpret: "Sr. Java Developer, $140/hr, onsite" is captured as those words; normalization decides what they mean. Keeping the two jobs separate is what makes every number auditable.

**What goes in.** The structured reading, plus intake's classification (a rate card and an invoice need different questions).

**What comes out.** Typed records already specified in `specs/extraction-task-contracts.md`: RateCardExtraction, SOWExtraction, and later an invoice and timesheet record for reconciliation. Every field carries a confidence score and its source position.

**Build or rent.** Both. Rent the reasoning: a frontier model (Claude first, GPT benchmarked) reads the document and fills the record. Own everything around it: record definitions, prompts, confidence rules, retries, and validation that rejects an answer that does not fit the record. One model wrapper so the model can be swapped. This is where the API credential is needed.

**Decisions (Kyle, Oct 5, 2026).**
- **Verify every number against the page.** After the model answers, the software checks that each extracted rate and date literally appears in the source text at the claimed position; anything that does not match is rejected. Catches the most dangerous model failure, a plausible invented number. Decided.
- **Big documents in pieces.** Long agreements are split by section using the reading stage's structure, extracted per section, and reassembled. Cross-references between sections may be missed; the evaluation harness will show whether that matters. Decided for M2, revisit with evidence.
- **Abstain rather than guess** when the model is unsure of a field: leave it blank and flag it. **Decided (Kyle, Oct 6).** Note: abstaining makes verification cheaper (only flags plus a sample need a human), whereas guessing makes every field suspect.

**Hand verification effort for the prototype (estimate, Oct 5).** The evaluation spec samples about 20 documents, not the whole library. Rate card 30 to 60 minutes; contract pricing exhibit 1 to 2 hours; agreement terms 1 to 2 hours. Roughly 20 to 30 hours in total, spread over weeks, with Claude drafting every answer sheet so the human checks rather than transcribes. Volume beyond the sample is scored against the sample.

**What the demo shows.** Step 3: the dense pricing grid becomes a clean table and clicking any number lights up the exact cell on the original page.

---


## 1.4 Normalization — **Decided** (Oct 6, 2026); largely built in M1

**What it does.** Turns the words extraction captured into the standard categories the ledger needs: "Sr. Java Developer, onsite" becomes role Software Developer, seniority senior, technology Java, location left for an analyst. Rates stay exactly as stated (own currency, per hour or per day); any conversion is a separate derived column recording the exchange rate and date. Nothing is silently converted.

**What goes in.** Typed extraction records. **What comes out.** The same records with standard fields filled, each carrying how it was resolved, the confidence, and the raw evidence.

**Built and decided already (M1, Sept 13 to 19):** Role Framework (130 roles), seniority crosswalk across ten schemes, technology tags, resolve-once mapping table, unbanded when no seniority evidence, location flagged for an analyst. Spec: `specs/role-framework-v0-spec.md`; results: `taxonomy/REPORT.md`.

**Not yet built.** (1) The model step: similarity search against resolved titles, then model confirmation with the document's context, then flag if still uncertain. (2) The analyst review queue, which belongs to the workbench.

**Decision (Kyle, Oct 6, 2026).** Wire the model step into M2, since the credential exists for extraction anyway. The volume run will meet hundreds of titles the public sources never held; with the model step the mapping table grows during that run and the queue keeps only the hard cases. Precision rules unchanged: a model answer is accepted only above the confidence floor, and the analyst can overturn it.

**Build or rent.** Build; similarity search rents Azure AI Search later; model confirmation uses the same model wrapper as extraction.

**What the demo shows.** Step 4: one Accenture title resolved with its reasoning shown, one uncertain title in the queue.

---

## 1.5 Ledger — **Decided** (Oct 6, 2026)

**What it does.** The Business Plan's "book of record": stores every rate observation permanently with full provenance, inside the client's environment. One row per rate seen: vendor, role and seniority, technology and location, rate in its own currency and unit, effective date, source document and position, how it was resolved and with what confidence. Every later analysis reads from it; it is the audit trail shown to a vendor who challenges a finding.

**Rules already decided:** raw evidence on every row; rates as stated, never converted in place; source class on every row (public, consortium, synthetic) and synthetic never enters; effective date on every row and benchmarks only from recent vintages.

**What leaves the client environment — clarified (Kyle, Oct 6, 2026).** Two things travel: *vocabulary* (framework, mappings, prompts) and *cohort summaries* (for each cut of role, seniority, location and technology: count, p25, median, p75). Individual rows never leave, and nothing linking a named vendor to a client ever leaves. Each client's ledger computes its own cuts; summaries go to TWM's central ledger; TWM combines them with other clients and public data and publishes the combined distribution back. Publish only when a cut has at least three observations and at least two contributing clients; public data pads cohorts while the consortium is small. Vendor identity in the combined view is the class only (Big-4, global SI, boutique, staff-aug); public sources stay named. The CLAUDE.md slogan "vocabulary travels; commerce never does" is corrected to "rows and vendor-client links never leave; vocabulary and cohort summaries do."

**Currency.** Rates stay as stated. A derived column holds the value in the client's reporting currency (CAD for a Canadian bank, per the Technical Approach), converted at a published reference rate on the observation's effective date, with that rate and its source stored beside it. Cuts are by location so most comparisons are within one currency; cross-currency comparison is market context and is labelled as such. Whether a converted foreign rate is truly comparable is an analyst judgment, not a formula.

**Decisions (Kyle, Oct 6, 2026).**
1. **Append, never overwrite.** Re-runs and amendments add rows and mark old ones superseded; history stays; "what changed since last review" becomes a query. Decided.
2. **Observations, not conclusions.** The ledger stores what documents say. Findings ("12 percent above market") are computed by later components and stored separately with the version of the rules that produced them. Decided.
3. **One ledger for public and client data,** distinguished by source class and the vendor-naming rule. Decided.
4. **Confidence gates money.** Every row keeps its extraction confidence and scan quality; benchmark distributions and savings totals count only rows above a threshold set by the evaluation harness; rows below it are kept and visible but excluded until an analyst confirms them. Decided.

**Build or rent.** Rent the database: PostgreSQL on Azure (open source, no per-client licence, portable into each bank's environment); a single-file database on Kyle's machine for the prototype, same schema. Build the schema, versioning and rules.

**What the demo shows.** The Accenture contract as rows, each clickable back to its page: "nothing in here is an estimate."

---

## 1.6 Benchmarking — **Decided** (Oct 6, 2026)

**What it does.** Answers "is this rate reasonable?" by comparing one observation against a population at the same cut (role, seniority, location, technology). Three comparisons, matching the Technical Approach's three analysis modes: *within the client* (same vendor, same role, across the client's own SOWs; the lateral audit, feeding the Operational tranche); *across vendors within the client* (the client's other vendors for the same role); *against the market* (the combined consortium-plus-public distribution from the central ledger, feeding the Market Alignment tranche).

**What goes in.** Ledger rows above the confidence threshold. **What comes out.** Per cut: count, p25, median, p75, and where the observation sits; plus the published benchmark table TWM maintains centrally.

**Decisions (Kyle, Oct 6, 2026).**
1. **Roll up when thin.** A cut below the cohort floor rolls up to the next broader cut: drop technology first, then role to family. The output states which level it rolled to, so a family-level number is never mistaken for a role-level one. (Families exist mainly for this; Cowork handoff 1.7.)
2. **Vintage window of 24 months** for market benchmarks, stated on the published table, adjustable per cut. Older rows stay in the ledger for trend analysis only.
3. **Public first, labelled as such.** Until three clients contribute, the market comparison is labelled public-source only with the sources named; never presented as a consortium benchmark it is not.

**Build or rent.** Build: statistics over the ledger. Power BI dashboards sit on top later.

**What the demo shows.** Step 5: Accenture's senior developer rate on a bar showing where eleven other vendors sit for the same role and seniority.

---

## 2. Reconciliation (invoices to timecards to SOWs) — **Decided** (Oct 6, 2026)

**What it does.** Checks that what was billed matches what was worked and what was contracted: did the invoice charge the agreed rate, for the agreed role, for the hours actually worked? Every mismatch is a candidate finding for the Contractual tranche.

**What goes in.** Through the same intake, reading and extraction as contracts: *invoices* (usually a summary PDF per vendor per month with a resource-level backup, often a spreadsheet); *timesheets* (for large vendors usually not in a vendor management system but in the vendor's monthly usage report attached to the invoice, or a spreadsheet; Cowork handoff 4.3, confirmed by Kyle); and the *contract family* the invoice bills against, already in the ledger. Spreadsheets and email attachments become first-class intake inputs at this point (the extension deferred in 1.1).

**What it does with them.** Matches each invoice line to a timesheet line and a contract rate, then tests the match against a fixed list of discrepancy types: rate above contract; role not on the rate card; wrong seniority billed; location premium charged for offshore work; invoice hours not matching the timesheet; duplicate billing; inconsistent billing periods or quantities; SOW rate exceeding the MSA rate without an amendment; escalation applied with no contractual basis (handoff 4.5; Fulton County audit).

**What comes out.** One candidate finding per discrepancy with the three source documents pinned, the amount, and a confidence. Only confident findings become money claims; the rest go to the analyst. Precision matters most here: a wrong leakage claim in front of a vendor is the existential risk.

**Decisions (Kyle, Oct 6, 2026).**
1. **The SOW rate is the enforceable rate** for a finding; a SOW rate above the MSA rate is reported separately as its own discrepancy type, so both facts are visible.
2. **People are matched without the HR link:** on vendor, person name as the documents give it, role and period. Ambiguous matches go to the analyst, never guessed. This is what lets priority two work without priority three.
3. **The discrepancy list is fixed and versioned.** The nine types above are version one; new types are added by decision, not discovered ad hoc, so every finding has a type a consultant can explain and a vendor can be shown.
4. **Synthetic first, real to prove.** Built and tested on synthetic contract-timesheet-invoice triplets with planted discrepancies (the synthetic factory, M4), then proven on the Texas PUC pair and the first Early Adopter's real data. Never claimed as validated on synthetic data alone.

**Build or rent.** Build entirely: matching logic over the ledger. Nothing to rent.

**What the demo shows.** The optional second chapter: the real Texas invoice beside its timesheets, lines matched, one mismatch lit up with the three documents behind it.

---

## Cross-cutting: Findings and reporting — to design (stacked savings tranches decided Sept 20)

## Cross-cutting: Review workbench — to design (home of the demo)
