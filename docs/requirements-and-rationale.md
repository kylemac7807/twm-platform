# TWM Platform — Requirements & Rationale

**A living document.** v0.1 — September 12, 2026 · Owner: Kyle McNamara
**Canonical copy:** TWM project (this file). Word snapshots produced on request for offline editing.

**Purpose.** This document records what TWM has decided, why, and in what order — so a future team member, a technical due-diligence reviewer, or a client architect can trace the platform's shape back to its reasons. It is the companion to *AI Architecture Design Decisions v0.1* (the architectural specification): that document says *what we build*; this one carries the requirements and the narrative of *why*.

**Status labels used throughout:** **Decided** · **Directional** (agreed in principle, detail open) · **Proposed** (recommended, awaiting Kyle's call) · **Parked** (deliberately deferred).

---

## 1. Product intent (context)

TWM helps large enterprises optimize third-party technology labor spend — targeting 10–15% savings by linking timecards to invoices to contracts, benchmarking normalized rates, and optimizing workforce mix. Phase 1 is an AI-driven audit producing a Master Benchmark Ledger, delivered through a consulting-led Early Adopter consortium that also supplies the data foundation. (Full detail: Business Plan v1.5; Pitch Deck v1.1.)

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

### 3.5 Role Framework v0 built — **Decided** (Sept 13, 2026), with two **Proposed** items

**What exists.** `taxonomy/` in the twm-platform repo: 18 families, 130 canonical roles, 137 band-crosswalk rows across 10 schemes, a 56-tag technology vocabulary, and 472 seeded title mappings drawn from Texas DIR, NY HBITS, TBIPS, all 12 G-Cloud 15 vendor cards, the DDaT framework and GSA labor categories. Deterministic rules (`src/twm/pipeline/normalize.py`) round-trip 99.3% of 1,355 observed title×level pairs to exactly one role and band with zero ambiguity, and the four-band crosswalk is rate-monotonic in all 29 public rate grids tested (`taxonomy/REPORT.md`).

**Decided as built.** Band precedence when resolving an observation: the source's own level code → stated years → title modifier → default *intermediate* (counted separately; 2.6% of cases). DDaT/G-Cloud role-specific level labels derive their band from wording rather than being enumerated. No GIS roles: geomatics titles are generic roles tagged `gis`.

**Proposed — awaiting Kyle's call.**
1. *Two families added to the spec's 16:* Technology Leadership (C-level roles G-Cloud prices separately) and Change, Training & Communications (OCM/trainer/comms titles present in TBIPS and Texas that are not delivery management).
2. *Packaged Applications uses five generic roles* (functional consultant, developer, technical consultant, architect, administrator) with the platform as the tech tag, instead of platform-named roles such as "SAP Consultant". The normalizer routes generic cores into this family whenever a packaged-platform tag is present. Reverting to platform-named roles is a point release (add roles, re-point mappings).

**Parked from M0.** 31 corpus originals could not be fetched by script (Michigan DTMB 403s, UK Contracts Finder rate limits, one dead GSA link); listed with URLs in `docs/corpus-missing-originals.md` and handed to the Cowork project. Needed for M2 (the Michigan Deloitte contract) and M3, not M1.

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

---

## 4. Architecture requirements (recorded in the Design Decisions doc; one-line rationale here)

- **Azure, models via Microsoft Foundry** — clients' CISOs have already approved this posture; platform and model choices are independent. *(Decided)*
- **Model-agnostic by design, opinionated by evaluation** — task contracts per pipeline stage; models win stages by measured performance; "portable in weeks, not quarters." *(Decided)*
- **Resolve-once normalization** — frontier model resolves each distinct title once into a durable, auditable mapping table; everything after is deterministic lookup. Determinism protects the ledger; auditability survives vendor challenge. *(Decided)*
- **Two-tier data boundary with a promotion gate** — commerce stays in the client tenant; only sanitized vocabulary promotes (k≥3 clients, human review). "Vocabulary travels, commerce never does." *(Decided)*
- **Federated, precision-weighted evaluation** — gold sets live in client tenants, only scores leave; false-positive leakage claims are the existential risk, so precision outranks recall and consultants are the recall mechanism. *(Decided)*
- **Own vs rent model split** — TWM owns document-extraction models, embeddings, classifiers; rents the frontier reasoning layer. Replaces the earlier "exported neural weights" narrative, which does not survive diligence. *(Decided)*
- **k-anonymity ledger publication** — benchmarks publish only above minimum cohort sizes; replaces "differential-privacy weight smudging." *(Decided)*

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
| Sept 13, 2026 | Role Framework v0 built: 18 families / 130 roles / 472 mappings; 99.3% round-trip, all rate grids band-monotonic (§3.5) | Decided |
| Sept 13, 2026 | Two added families (Technology Leadership; Change, Training & Communications) | Proposed |
| Sept 13, 2026 | Packaged Applications as generic roles + platform tech tag (not "SAP Consultant"-style roles) | Proposed |
| Sept 13, 2026 | Band precedence: source level > stated years > title modifier > default intermediate | Decided |

## 6. Open questions

1. SFIA — the dedicated discussion, then legal read (royalty scope; consulting-use question), then Foundation conversation.
2. Extraction prototype scope (approved in principle; discussion pending).
3. CPSS data-use rights: registering and *reading* is one thing; republishing or embedding portal-sourced rates in a commercial product needs a legal read of the ePortal terms of use and Crown-copyright position. ATIP-released records are the cleaner-reuse path. See §2.5.
4. Minimum cohort size k (working assumption 3) and confidence thresholds (needs real documents).
5. **Parked:** Foundry data-handling terms in writing. **Queued:** revise Technical Approach + Pitch Deck per Design Decisions §9.
