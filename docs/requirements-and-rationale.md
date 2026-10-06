# TWM Platform — Requirements & Rationale

**A living document.** v0.4 — September 19, 2026 (v0.1 Sept 12; v0.2 Sept 18; v0.3 Sept 19 Cowork; v0.4 merged) · Owner: Kyle McNamara
**The only real copy is this file**, `docs/requirements-and-rationale.md` in the twm-platform project folder (decided Sept 19, 2026). Cowork and Claude Code both read and edit it here; no other copy is kept. Every change is saved in the folder's version history. Word snapshots produced on request for offline reading.

**Purpose.** This document records what TWM has decided, why, and in what order — so a future team member, a technical due-diligence reviewer, or a client architect can trace the platform's shape back to its reasons. It is the companion to *AI Architecture Design Decisions v0.1* (the architectural specification): that document says *what we build*; this one carries the requirements and the narrative of *why*.

**Status labels used throughout:** **Decided** · **Directional** (agreed in principle, detail open) · **Proposed** (recommended, awaiting Kyle's call) · **Parked** (deliberately deferred).

---

## 1. Product intent (context)

TWM helps large enterprises optimize third-party technology labor spend — targeting 10–15% savings by linking timecards to invoices to contracts, benchmarking normalized rates, and optimizing workforce mix. Phase 1 is an AI-driven audit producing a Master Benchmark Ledger, delivered through a consulting-led Early Adopter consortium that also supplies the data foundation. (Full detail: Business Plan v1.5; Pitch Deck v1.1.)


### 1.1 Priority order of the analyses — **Decided** (Kyle, Sept 20, 2026)

The platform does three kinds of analysis. They are built and demonstrated in this order, and a later one never delays an earlier one.

1. **Core SOW analysis — first.** Read the contracts and rate cards, extract the roles, rates and commercial terms, normalize them, and compare: against the client's own other contracts, against the same vendor's other rates, and against the benchmark ledger. This is the heart of the product and stands on its own with nothing but the client's contracts.
2. **Invoices to timecards to SOWs — second.** Check that what was billed matches what was worked and what was contracted: hours, rates, roles, levels, locations, duplicates.
3. **The HR-system link — third, and least important.** Match the people on SOWs and timesheets to records in the client's HR system (such as Workday) or vendor management system (such as Fieldglass). The Technical Approach v1.2 calls this the "Matchmaker" step. It needs an export from those systems as an input, and a step that recognizes the same person across SOW, timesheet, invoice and HR data. It refines headcount and role accuracy; it is not required for the first two.

**Consequence for the savings tranches (see open question 7).** The Technical Approach defines the Contractual tranche as savings from enforcing contract caps "on confirmed headcount", which leans on the HR link. Because that link comes last, the Contractual tranche is first calculated from SOWs and invoices alone, and headcount confirmation is a later refinement.

---

## 2. Data strategy

### 2.1 Training data and benchmark data are different assets — **Decided** (Sept 12, 2026)

**Requirement.** The platform maintains two distinct data quality bars and never confuses them:

- **Training data** teaches the extraction and normalization models. It must be *realistic in structure* and carry *known correct labels*. It does **not** need to reflect true market prices — a plausible rate in a realistic document trains the parser just as well as a real one.
- **Benchmark data** feeds the Master Benchmark Ledger and client-facing claims. It must be *true*, *sourced*, and *vintage-tagged* — and synthetic or stale data must never enter it.

**Rationale & history.** Surfaced Sept 12 when the Canadian-rates gap was re-examined: the original framing treated public awarded rates as the goal, but for building preliminary models the binding need is training documents, not market truth. This distinction reframes several sourcing decisions (see 2.4, 2.5) and underpins the vintage policy: every benchmark observation carries an effective date; benchmarks publish only from recent vintages.

### 2.2 The public bootstrap corpus — **Decided** (built Sept 1–12, 2026)

**History.** Three research passes assembled a public corpus before any client data exists: the initial sweep and same-day deep pass (Sept 1), and a G-Cloud 15 refresh (Sept 12). Contents: skills frameworks (O*NET, DDaT, NICE, ESCO, CEN — verified sources and licensing); ~26 rate-card artifacts including Texas DIR (2020 and 2024 generations), NY HBITS awarded averages, GSA CALC+ distributions, and 18 UK G-Cloud SFIA day-rate cards across two framework generations; and 23 real MSAs/SOWs (SEC EDGAR and state-published contracts, 2001–2026, ten with unredacted pricing). Full inventory: *Public Bootstrap Corpus Catalog* (project).

**Findings worth retaining.** UK onshore rates moved +6–15% between May 2024 and 2026 cards (validates vintage tagging); Texas NTE ceilings sat still 2020→2024 (public ceilings ≠ market); G-Cloud 15 now publishes explicit UK/offshore rate columns per vendor — offshore arbitrage is publicly observable (e.g., Accenture developer £650 UK / £275 offshore; TCS £700/£450).

**Serves:** taxonomy seeding (§3), benchmark reference distributions, extraction training/eval structures, synthetic-document templates (2.4).

### 2.3 O*NET as the title-synonym backbone — **Decided** (Sept 12, 2026)

**Requirement.** Title normalization uses the O*NET alternate/reported-titles files as the primary public synonym source: the layer that maps observed title strings ("Solutions Delivery Specialist III") toward canonical roles.

**Rationale.** O*NET (US Department of Labor) is the largest free dictionary of real-world job-title strings mapped to canonical occupations — tens of thousands of titles, collected from employer surveys and postings, maintained since the 1990s, licensed CC BY 4.0 (fully commercial-safe). It solves the highest-volume normalization function with zero licensing exposure — which also reduces how much of the taxonomy could ever be claimed to "depend on" SFIA (see 3.1).

### 2.4 Synthetic document factory — **Decided** (Sept 12, 2026)

**Requirement.** Build a generator that produces synthetic SOWs, rate cards, invoices, and timecards from the corpus's real document structures — parameterized for difficulty (nested tables, scan quality, amendment chains, off-rate-card items) and with **leakage planted by construction**, so every training document carries perfect, free labels.

**Rationale.** (a) Training labels by construction — no hand-labeling backlog; (b) solves the Canadian training-data need without CPSS: TBIPS vocabulary + Canadian conventions (CAD, per-diem, bilingual titles) + plausible rate distributions from wage proxies produce Canadian-*shaped* documents, which is all training requires per 2.1; (c) reconciliation models (timecard→invoice→SOW) can be trained end-to-end with planted discrepancies before any client data exists; (d) produces demonstration material for Early Adopter pitches with zero confidentiality exposure. Synthetic data never enters the benchmark ledger (2.1). Kyle's note: benchmarks derived from training/public data are interim curiosities — expected to be overridden the moment bank data arrives.

### 2.5 Canadian rate sources — **Decided: pursue both tracks** (Sept 12, 2026)

The synthetic factory covers the training need (critical path); Canadian awarded rates are still pursued **in parallel** as benchmark seeding, since the effort is cheap: register for CPSS when convenient (check portal terms of use before commercial reuse), file one ATIP request as a background lottery ticket, use Job Bank wage data with a ~1.5–2.2× loading factor as the interim proxy. The gap closes structurally at client one. Provincial vehicles (e.g., Ontario VOR) remain unmined.

---

## 3. The TWM Role Framework (taxonomy)

### 3.1 Owned spine, licensed crosswalks — **Directional** (pending the SFIA deep-dive)

**Direction.** TWM builds and owns its canonical taxonomy (the "TWM Role Framework"), constructed from commercially-free sources (O*NET, DDaT, TBIPS, ESCO) and consortium learning. SFIA becomes an optional *crosswalk* — a mapping offered to clients who use SFIA internally — rather than the spine.

**Rationale & history.** SFIA's Partner Licence carries £2–4k/yr plus a **5% royalty on products "dependent on SFIA data"** — ambiguous scope that, read broadly, would tax TWM's whole revenue line. Kyle agreed with the crosswalk direction (Sept 12) with a fuller discussion to come before final commitment. Cautions on record: the owned framework must be genuinely built from the free sources (copying SFIA definitions is a derivative work), and counsel should also check whether consulting deliverables referencing SFIA need a licence. A conversation with the SFIA Foundation is planned — negotiating from a position of not needing them.

### 3.2 Axes design: what × level, with where and how-much as observation attributes — **Decided** (Sept 12, 2026)

**Requirement.** The taxonomy has two axes: **canonical role** (grouped into role families) and **seniority band**. Location (onshore/nearshore/offshore, city) and rate are **not** taxonomy dimensions — they are attributes of individual rate observations that reference the taxonomy. Title strings map into the taxonomy through normalization (seniority modifiers like "Senior"/"III" and location tokens are extracted, not multiplied into the role list).

**Rationale.** Keeps the taxonomy small, stable, and curatable (~15–20 families, ~100–200 roles) while observations scale without bound. Prevents the combinatorial explosion of role × level × location entries, and matches how the ledger must aggregate (any cut of observations by any attribute). Kyle agreed Sept 12 ("not multiplying the taxonomy").

**Band count — Decided (Sept 13, 2026): four bands** — junior / intermediate / senior / lead-principal. Sources range from 3 (TBIPS, and Kyle's prior bank) to 7 (SFIA/DDaT); four is the most that documents reliably signal, and lead/principal is priced distinctly in the sources held (Texas, DDaT, G-Cloud). Management/executive tiers are treated as roles, not bands. **Companion decision:** every observation stores its raw seniority evidence (stated years of experience, the source's own level code — TBIPS L2, SFIA 5, Texas Level 3), so bands are a view over evidence and can be split later without re-extraction. Coarse-but-observable beats fine-but-fabricated.

**Technology-as-attribute — Decided (Sept 13, 2026).** Technology/platform (Java, .NET, mainframe, SAP, Guidewire…) is a third observation attribute alongside location — drawn from a controlled vocabulary of ~40–60 tags — not a role multiplier. "Java Junior Developer, Offshore" = role (Software Developer) + band (junior) + tech (Java) + location (offshore): four fields, one taxonomy entry. Benchmarks cut by tech tag. Exception: where the technology is the practice (SAP consultant, Salesforce developer), the role lives in the Packaged Applications family but still carries its tech tag.

**Related design point.** The spine is **role-based, not skills-based**, because rate cards and SOWs price *roles* — a skills decomposition (SFIA-style: ~147 skills × 7 levels) can attach to roles later, but the unit of commerce is the role. This is the philosophical difference from SFIA and another reason it serves better as crosswalk than spine.

### 3.3 Benchmark publication design — **Decided** (Sept 13, 2026)

**Requirement (Kyle, Sept 12).** Cross-client benchmarks are published at **normalized cuts** — role × band × location (e.g., "Java developer, junior, offshore") — as **distributions**, not vendor-specific points: cohort size (n), percentiles (p25 / median / p75, optionally p10/p90), and a spread measure. Named-vendor benchmarks (e.g., "TCS junior Java developer, offshore") never cross clients.

**Three levels of vendor identity:**

1. **Named — within one client's local tier only.** Bank A sees its own full variability for TCS junior Java offshore across all of Bank A's SOWs (the Lateral Audit). This never leaves Bank A's tenant.
2. **Classed — in the global ledger.** Observations may carry an anonymized vendor class (e.g., global SI / Big-4 / boutique / staff-aug), preserving benchmark usefulness ("global SIs charge X–Y for offshore junior Java") without naming vendors. *(Included in the Sept 13 sign-off.)*
3. **Named public — allowed.** Public sources (G-Cloud, Texas DIR) are already vendor-named in public; the ledger may cite them as such, clearly separated from consortium-derived data.

**Rationale.** Matches what clients will actually permit, aligns with the two-tier boundary and k-anonymity floor (publish only above minimum cohort), and prefers percentiles over min/max — extremes are noisy and can be identifying.

### 3.4 Source stack and licensing

| Source | Contributes | Licence |
|---|---|---|
| O*NET 31.0 | Title synonyms at scale (Layer 1) | CC BY 4.0 — commercial OK |
| UK DDaT | Role × seniority ladder structures | OGL v3.0 — commercial OK, attribution |
| Canada TBIPS | Category definitions, experience gates, Canadian procurement vocabulary | Public procurement record |
| ESCO v1.2.1 | Multilingual synonyms (offshore/global-delivery titles, French) | EUPL 1.2 — commercial OK; registration to download |
| NICE (NIST SP 800-181r1) | Cyber role decomposition | US public domain |
| CEN CWA 16458 / ENISA ECSF | European ICT role profiles | Free CWAs |
| SFIA 9 | Crosswalk only, pending licensing decision | Registration for internal use; Partner Licence for commercial |
| Consortium client data | The long tail of vendor-specific titles (via the promotion gate) | Consortium agreement |

### 3.5 Role Framework v0 built — **Decided** (Sept 13, 2026; reviewed by Cowork and settled with Kyle Sept 19)

**What exists** (`taxonomy/` in the twm-platform project folder): 18 families, 130 canonical roles, 137 band-crosswalk rows across 10 schemes, a 56-tag technology vocabulary, and 475 seeded title mappings — 349 observed in Texas DIR, NY HBITS, TBIPS, the G-Cloud 15 cards, DDaT and GSA sources, plus 126 authored aliases. Deterministic rules (`src/twm/pipeline/normalize.py`) resolve 99.3% of 1,355 observed title×level pairs to exactly one role with zero ambiguity, and 96.7% to both role and band; the four-band crosswalk is rate-monotonic in all 29 public rate grids tested (`taxonomy/REPORT.md`). 73 tests enforce the design rules: technology never appears in a role name outside Packaged Applications; the SFIA column is empty; unknown titles are flagged, not guessed; mappings append or deprecate, never overwrite.

**Decided as built.** Band precedence when resolving an observation: the source's own level code → stated years → title modifier. DDaT and G-Cloud role-specific level labels derive their band from wording rather than being enumerated. No GIS roles: geomatics titles are generic roles tagged `gis`.

**Decided Sept 19, 2026 (Kyle).**
1. *Two families added to the spec's 16 — accepted.* Technology Leadership (`exec`: C-level roles that G-Cloud and DDaT price separately, consistent with "management tiers are roles, not bands") and Change, Training & Communications (`chg`: change-management, trainer and communications titles present in TBIPS and Texas that are not delivery management).
2. *Packaged Applications as five generic roles plus a platform tech tag — accepted.* Functional consultant, developer, technical consultant, architect, administrator; "SAP ABAP Developer" is a packaged application developer tagged `sap`. This is the technology-as-attribute decision applied.
3. *No default band.* A title with no seniority evidence keeps its role and stays unbanded, is excluded from band-level benchmark cuts, and its band alone goes to the review queue. Raised by Cowork's review: a defaulted band is an invented data point.

**Location: flag, let an analyst categorize, then codify — Decided** (Kyle, Sept 19, 2026). Whether a place counts as onshore, nearshore or offshore for a given client is a judgment about cost and context, not geography. Kyle's illustrations, which are examples and not rules: a Canadian bank with development in New York City is paying an expensive onshore-equivalent rate; the same bank in Buffalo might be nearshore, depending; a US bank developing in Canada is almost always nearshore; and a city in the client's own country is not always onshore. So the platform never decides from a place name. The words onshore, nearshore and offshore written in a document classify directly. Any place name is stored as city and country, flagged for an analyst, and shown with a non-binding suggestion. The analyst categorizes it once, with a reason, in a location rules table; every later occurrence for that client is then a deterministic lookup. Rules are appended or deprecated, never edited, and they live in the client's own tenant. This is the same resolve-once pattern used for job titles.

**Known limits (v0.1 targets).** The round-trip is a consistency check, not a generalization test: 1,197 of the hits are exact full-title matches against a table seeded from the same sources. A held-out run on the G-Cloud 14 cards, the Accenture titles in the Texas TSS-699 pricing exhibit, the Cognizant and Deloitte GSA cards Kyle collected, and Job Bank titles is the real check before M2 leans on the normalizer. Years-stated breakpoints and the NY HBITS month-bands disagree at 5 to 7 years (precedence hides it; reconcile in the crosswalk). The consulting-pyramid bands are unvalidated heuristics; the Oklahoma Deloitte contract and Deloitte's G-Cloud grade card can validate them. O*NET and ESCO synonyms and the TBIPS telecom stream are not yet folded in.

**Parked from M0.** 31 document originals could not be fetched by script (Michigan DTMB blocks scripts, UK Contracts Finder rate limits, one dead GSA link). They are listed with URLs in `docs/corpus-missing-originals.md` and prioritized in `docs/corpus-sources-and-demo-set.md`; Kyle will retrieve them by hand. Needed for M2 (the Michigan Deloitte contract) and M3, not M1.

---

## 4. Architecture requirements (recorded in the Design Decisions doc; one-line rationale here)

- **Azure, models via Microsoft Foundry** — clients' CISOs have already approved this posture; platform and model choices are independent. *(Decided)*
- **Model-agnostic by design, opinionated by evaluation** — task contracts per pipeline stage; models win stages by measured performance; "portable in weeks, not quarters." *(Decided)*
- **Resolve-once normalization** — frontier model resolves each distinct title once into a durable, auditable mapping table; everything after is deterministic lookup. Determinism protects the ledger; auditability survives vendor challenge. *(Decided)*
- **Two-tier data boundary with a promotion gate** — commerce stays in the client tenant; only sanitized vocabulary promotes (k≥3 clients, human review). "Vocabulary travels, commerce never does." *(Decided)*
- **Federated, precision-weighted evaluation** — gold sets live in client tenants, only scores leave; false-positive leakage claims are the existential risk, so precision outranks recall and consultants are the recall mechanism. *(Decided)*
- **Own vs rent model split** — TWM owns document-extraction models, embeddings, classifiers; rents the frontier reasoning layer. Replaces the earlier "exported neural weights" narrative, which does not survive diligence. *(Decided)*
- **k-anonymity ledger publication** — benchmarks publish only above minimum cohort sizes; replaces "differential-privacy weight smudging." *(Decided)*

**What the business documents promise, and what real client documents and systems look like,** are distilled in `Claude outputs/cowork-handoff-2026-09-18.md` sections 3 and 4 (Technical Approach, Business Plan, Pitch Deck, Consortium Approach; contract shapes, systems of record, governance constraints, discrepancy classes). Items marked (I) there are general industry knowledge not yet validated by Kyle. One correction: that handoff says the three savings tranches are defined nowhere; the Technical Approach v1.2 Phase 5 does define them, and section 6 item 7 of this document uses those definitions.

---

## 5. Decision log

| Date | Item | Status |
|---|---|---|
| Sept 1, 2026 | Azure + Foundry; model-agnostic; resolve-once; two-tier boundary; federated eval; own-vs-rent; k-anonymity | Decided (Design Decisions v0.1) |
| Sept 1, 2026 | Public bootstrap corpus built (two passes) | Decided |
| Sept 12, 2026 | G-Cloud 15 refresh; vintage policy articulated | Decided |
| Sept 12, 2026 | Training vs benchmark data distinction | Decided |
| Sept 12, 2026 | O*NET as title-synonym backbone | Decided |
| Sept 12, 2026 | SFIA as crosswalk, not spine | Directional — deep-dive pending |
| Sept 12, 2026 | Taxonomy axes (role × band; location/rate as observation attributes) | Decided |
| Sept 12, 2026 | Synthetic document factory; Canadian rates pursued in parallel (both tracks) | Decided |
| Sept 12, 2026 | Benchmark publication: normalized cuts, distributions, three levels of vendor identity | Decided (confirmed Sept 13, incl. vendor-class) |
| Sept 13, 2026 | Seniority bands: four (junior/intermediate/senior/lead-principal) + raw evidence stored per observation | Decided |
| Sept 13, 2026 | Technology as observation attribute (controlled ~40–60 tag vocabulary), not a role multiplier | Decided |
| Sept 13, 2026 | M0 complete: repo initialised, Sept 1 package + Python toolchain in place, 419 of 450 corpus originals fetched (31 parked → Cowork) | Decided |
| Sept 13, 2026 | Role Framework v0 built: 18 families / 130 roles / 475 mappings (349 observed, 126 authored aliases); 99.3% resolve to a role, all 29 rate grids band-monotonic (§3.5) | Decided |
| Sept 13, 2026 | Two added families (Technology Leadership; Change, Training & Communications) | **Decided Sept 19** — accepted by Kyle (Cowork also recommended accept) |
| Sept 13, 2026 | Packaged Applications as generic roles + platform tech tag (not "SAP Consultant"-style roles) | **Decided Sept 19** — accepted by Kyle (Cowork also recommended accept) |
| Sept 13, 2026 | Band precedence: source level > stated years > title modifier (the original "default intermediate" fallback was removed Sept 19) | Decided |
| Sept 19, 2026 | **No default band.** A title with no seniority evidence keeps its role and stays unbanded; it is excluded from band-level benchmark cuts and its band goes to the review queue. Raised by Cowork's repo review; agreed by Kyle. Reason: a defaulted band is an invented data point, against "coarse-but-observable" and precision-first | Decided |
| Sept 19, 2026 | **Location: flag, analyst categorizes, then codify.** Only the words onshore/nearshore/offshore in a document classify directly. Place names are stored as city and country, flagged for an analyst with a non-binding suggestion, and classified only by a recorded analyst decision for that client (resolve-once, append/deprecate, held in the client tenant). Kyle's New York, Buffalo and Canada cases are examples, not rules; same country is not always onshore (§3.5) | Decided |
| Sept 19, 2026 | **One source of truth.** The twm-platform project folder holds the only real copy of every working document. Cowork shares the folder and leaves its outputs in `Claude outputs/`; Claude Code reads anything new there at the start of each session and commits it. The separate "canonical" copy in the Cowork project is to be retired | Decided — Cowork's copy merged into this file and retired Sept 19 |
| Sept 13, 2026 | **Azure build framing:** Azure supplies the commodity layers (document reading, model hosting, database, search, orchestration, dashboards, deployment); TWM's product is the thin custom layer on top: schemas, prompts, task contracts, resolve-once logic, the promotion gate, the evidence model (`Claude outputs/cowork-handoff-2026-09-18.md` section 1.1) | Directional |
| Sept 13, 2026 | **Deployment automation is a product feature:** TWM is a stack that deploys into each client's Azure subscription, so infrastructure-as-code from day one; goal is a complete environment in a fresh subscription in hours (handoff 1.2) | Directional |
| Sept 13, 2026 | **Two environments; TWM's own comes first.** A TWM development subscription is the first physical build step, on Kyle's side (handoff 1.3; action item C4) | Decided |
| Sept 13, 2026 | **Portable pieces first:** schemas, prompts, normalization, mapping logic, eval harness and thin-thread code proceed now as cloud-agnostic Python; Azure wiring waits for the subscription (handoff 1.4) | Decided |
| Sept 13, 2026 | Tooling split: code and data in the project folder with Claude Code; strategy, research and documents with Cowork (handoff 1.5). **Its original sync rule, a canonical requirements copy inside Cowork carried across by Kyle, was replaced Sept 19 by the single shared folder** | Decided, amended Sept 19 |
| Sept 13, 2026 | **Role families exist mainly for roll-up:** when a benchmark cohort is too thin at role level to publish under the minimum cohort size, the ledger rolls up to the family. Families are also the bolt-on point for non-IT work (handoff 1.7) | Directional |
| Sept 13, 2026 | **CPSS data use in three tiers:** reading to calibrate is low risk; internal analysis is gray; republishing portal-sourced rates in the commercial ledger needs a legal read of the portal terms first. ATIP-released records are the cleaner path (handoff 1.8) | Directional |
| Sept 13, 2026 | **ATIP strategy:** request whole contract files, not just rates, for 15 to 20 named TBIPS contracts chosen from the proactive-disclosure register; one request per contracting department; draft request text preserved in handoff 1.9 | Queued (Cowork builds the list; Kyle files) |
| Sept 1, 2026 | **Six inconsistencies across the Business Plan and Pitch Deck** (cover version, launch dates now past, $100MM versus $200MM target threshold, Early Adopter revenue framing, profitability year, undefined tranches) to fix when those documents are revised (handoff 1.10) | Queued (Cowork, action item D3) |
| Sept 1, 2026 | **Air-gapped fallback:** for a client that refuses any hosted model, a self-hosted open-weight model inside the client network, weaker but fully isolated. Keep the model wrapper able to target a local endpoint (handoff 1.11) | Open item |
| Sept 18, 2026 | SFIA licence figures (2,000 or 4,000 pounds a year plus 5 percent royalty) are second-hand; verify from the primary source before anything goes to counsel (handoff 1.13) | Caution |
| Oct 6, 2026 | **Findings and reporting:** stacking edge cases: a missing reference (no contracted rate, no second vendor rate, rate already below market) yields zero for that tranche with the reason stated, never a guess or a negative; a role billed without a contracted rate is its own finding; observed and projected savings always shown as two labelled numbers, never blended; a per-engagement minimum annual value filters executive views without discarding anything; findings recomputed under new rule versions, never hand-edited (`architecture-components.md`, cross-cutting) | Decided |
| Oct 6, 2026 | **Reconciliation:** SOW rate is the enforceable rate, SOW-above-MSA is its own discrepancy type; people matched on vendor, name, role and period with ambiguity to the analyst; fixed, versioned list of nine discrepancy types; built on synthetic triplets, proven on real pairs, never validated on synthetic alone (`architecture-components.md` 2) | Decided |
| Oct 6, 2026 | **Benchmarking:** roll up thin cuts (technology first, then role to family) and say so; 24-month vintage window stated on the table; public-source benchmarks labelled as such until three clients contribute (`architecture-components.md` 1.6) | Decided |
| Oct 6, 2026 | **Ledger:** append never overwrite; confidence and scan quality gate what counts in benchmarks and savings (threshold set by the evaluation harness, analyst can confirm); observations not conclusions; one ledger for public and client data tagged by source class; PostgreSQL on Azure, single-file database for the prototype; currency converted only as a derived column at the effective-date reference rate. **Data boundary clarified:** rows and vendor-client links never leave the client; vocabulary and cohort summaries do, published only above three observations and two contributing clients (`architecture-components.md` 1.5) | Decided |
| Oct 6, 2026 | **Normalization:** the model step (similarity search, then model confirmation above the confidence floor, then flag) is wired into M2 so the mapping table grows during the volume run (`architecture-components.md` 1.4) | Decided |
| Oct 5, 2026 | **Extraction:** every extracted number is verified against the source page and rejected if absent; long documents are split by section for M2 (`architecture-components.md` 1.3). Abstain rather than guess on any uncertain field: leave it blank and flag it (Kyle, Oct 6) | Decided |
| Oct 5, 2026 | **Document reading** rented from Azure Document Intelligence behind an interface, local native-PDF reader first; scan quality tracked as an attribute to the ledger (`architecture-components.md` 1.2) | Decided |
| Oct 5, 2026 | **Build sequence:** M2 one contract end to end (Texas Accenture set), then the whole library through the pipeline, then M3 evaluation from a hand-verified sample, then the demo. Demo audience: an Early Adopter CIO | Decided |
| Oct 5, 2026 | **Intake component designed** (`docs/architecture-components.md` 1.1): intake links documents on its own only on strong evidence, otherwise suggests and flags for the consultant (flag-then-codify); M2 accepts PDF and Word only, spreadsheets and email arrive with reconciliation | Decided |
| Oct 5, 2026 | `docs/architecture-components.md` is the running requirements-and-design record for the component walkthrough; decisions are mirrored here | Decided |
| Sept 20, 2026 | **Priority order of analyses:** core SOW analysis first; invoices to timecards to SOWs second; the HR-system link third and least important (§1.1) | Decided |
| Sept 20, 2026 | **Savings tranches are stacked, never double counted:** Contractual (down to the contracted rate), then Operational (down to the vendor's own best rate for the role), then Market Alignment (down to the benchmark mid-point). Edge cases and confidence thresholds still open (§6 item 7) | Decided |
| Sept 19, 2026 | Current business documents indexed in `docs/business-documents.md`; Word Business Plan v1.5 replaces the October 2025 slide deck | Decided |
| Sept 19, 2026 | The acceptance score is a consistency check; a held-out test on unseen sources (G-Cloud 14 cards, Texas Accenture titles, Cognizant and Deloitte GSA cards) is needed before M2 relies on the normalizer | Proposed (Cowork review; Claude Code agrees) |

## 6. Open questions

1. SFIA — the dedicated discussion, then legal read (royalty scope; consulting-use question), then Foundation conversation.
2. Extraction prototype scope (approved in principle; discussion pending).
3. CPSS data-use rights: registering and *reading* is one thing; republishing or embedding portal-sourced rates in a commercial product needs a legal read of the ePortal terms of use and Crown-copyright position. ATIP-released records are the cleaner-reuse path. See §2.5.
4. Minimum cohort size k (working assumption 3) and confidence thresholds (needs real documents).
5. **Parked:** Foundry data-handling terms in writing. **Queued:** revise Technical Approach + Pitch Deck per Design Decisions §9.
6. **The HR-system link: inputs and identity — lowest priority (section 1.1).** The Technical Approach v1.2, Phase 5, promises to match SOW titles such as "Tech Lead" to HR titles such as "Consultant II" and to tie the audited rate to actual headcount from the client's vendor management system or HR system. No spec covers the two things this needs: an export from those systems as an input, and a step that recognizes the same person across the SOW, the timesheet, the invoice and the HR record. Deliberately left undesigned until the core SOW analysis and the reconciliation work are in place. Raised by Cowork, Sept 20; prioritized by Kyle, Sept 20.
7. **How a finding is assigned to a savings tranche.** The Technical Approach v1.2 and the Pitch Deck promise a "Total Potential" dashboard that adds up savings in three tranches: **Contractual** (immediate savings from enforcing the caps in the client's own contracts), **Operational** (savings from removing price inconsistencies within one vendor, where the same vendor charges the same client different rates for the same role) and **Market Alignment** (longer-term savings from moving rates toward the mid-point of the benchmark ledger). No spec yet says how the platform decides which tranche a given dollar of savings belongs to, or how it avoids counting the same dollar twice. Worked example: a senior developer billed at $140 an hour, where the contract cap is $125, the same vendor bills $110 for that role on another SOW, and the market mid-point is $100. The natural rule is to stack them so nothing is counted twice: $15 Contractual (140 down to 125), $15 Operational (125 down to 110), $10 Market Alignment (110 down to 100). **Decided (Kyle, Sept 20, 2026): stack them in that order** — contract cap first, then the vendor's own best rate for the role, then the market mid-point — so no dollar is ever counted twice. Still open: the edge cases (no contract cap stated; no second rate from the same vendor; a rate already below the mid-point) and how confident the platform must be before a dollar is counted. The first two tranches come from the core SOW analysis and the reconciliation work; none of them needs the HR link.
