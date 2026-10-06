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


## 1.4 Normalization — built in M1; design to be written up from `specs/role-framework-v0-spec.md` and `taxonomy/REPORT.md`

## 1.5 Ledger — to design

## 1.6 Benchmarking — to design

## 2. Reconciliation — to design

## Cross-cutting: Findings and reporting — to design (stacked savings tranches decided Sept 20)

## Cross-cutting: Review workbench — to design (home of the demo)
