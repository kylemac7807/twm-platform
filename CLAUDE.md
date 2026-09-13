# CLAUDE.md — TWM Platform

Standing context for every session in this repo. Deep detail lives in `docs/` and `specs/` — read the relevant one before implementing its area. This file is the map, not the territory.

## What TWM is

Technology Workforce Management: an AI platform + consulting practice that helps large enterprises (Canadian/US banks first) cut third-party technology labor spend 10–15% by linking timecards → invoices → contracts, normalizing rates against an owned taxonomy, and benchmarking across a client consortium. Founder: Kyle McNamara. Phase 1 product: an AI-driven audit producing a **Master Benchmark Ledger**.

## Non-negotiable architecture decisions (full rationale: docs/architecture-decisions.md)

1. **Azure is the deployment target; models come via Microsoft Foundry** (Claude primary, GPT benchmarked). The product deploys **into each client's Azure tenant** — it is a deployable stack (IaC), not a SaaS. Client data never reaches TWM.
2. **Model-agnostic by design, opinionated by evaluation.** Every pipeline stage is a typed **task contract** (see specs/extraction-task-contracts.md); models win stages by measured eval performance. Prompts are per-model, not portable. Never hard-wire a vendor.
3. **Resolve-once normalization.** A distinct title is resolved ONCE by a frontier model with full context → written to a durable mapping table (reasoning + confidence + source + reviewer) → all later occurrences are deterministic lookups. Novel titles go through embedding-similarity first; low confidence routes to a human queue. Determinism protects the ledger; the table is a client-facing audit artifact.
4. **Two-tier data boundary.** Local tier (client tenant, never moves): rates, vendor–role–rate–client linkages, documents, reasoning text. Global tier (TWM's): sanitized vocabulary only, promoted through a gate (observed at k≥3 clients, sanitized, human-reviewed). Vocabulary travels; commerce never does.
5. **Evaluation is federated and precision-weighted.** Gold sets live in client tenants; only field-level scores leave. False-positive leakage claims are existential; recall is the consultants' job. See specs/eval-harness-spec.md.
6. **Own vs rent.** TWM owns: Document Intelligence custom extraction models, embedding fine-tunes, classifiers, schemas, prompts, taxonomy, eval sets. TWM rents: the frontier reasoning layer. Never claim extractable weights from hosted frontier models.
7. **Benchmarks publish as distributions at normalized cuts** (role × band × location × tech): n, p25, median, p75 (p10/p90 when deep), above a k-anonymity floor (working k=3). Named-vendor data never crosses clients; an anonymized vendor-class tag (global SI / Big-4 / boutique / staff-aug) is allowed. Public sources (G-Cloud, Texas DIR) may stay vendor-named, clearly separated.

## Data rules (never violate)

- **Training data ≠ benchmark data.** Training needs realistic documents with known labels (synthetic is ideal). Benchmarks need TRUE, sourced, **vintage-tagged** observations. Synthetic or stale data never enters the ledger. Every rate observation carries: effective date, source, source class (public / consortium / synthetic-never-ledger).
- **Store raw seniority evidence** (stated years, source level codes) on every observation — bands are a view over evidence and can be re-derived.
- SFIA: **crosswalk only, not the spine** (licensing: 5% royalty risk — see docs/requirements-and-rationale.md §3.1). Do not copy SFIA definitions into the taxonomy; build genuinely from O*NET/DDaT/TBIPS.

## The taxonomy (TWM Role Framework — spec: specs/role-framework-v0-spec.md)

Two axes only: **canonical role** (~120–180, in ~16 families) × **seniority band** (4: junior / intermediate / senior / lead-principal). Location (onshore/nearshore/offshore) and technology (controlled ~40–60 tag vocabulary) are **observation attributes, never role multipliers**. Management/executive tiers are roles, not bands. Crosswalks (DDaT, TBIPS, O*NET, SFIA-pending) are views out of one spine — never a second spine. Versioned like software: mappings append/deprecate, never silently edit.

## Corpus (catalog: docs/corpus-catalog.md)

- `corpus/manifests/v3_*/manifest.csv` — 388 classified URLs of ORIGINAL documents (EDGAR MSAs, government signed contracts incl. UK/Canada bilingual, rare invoice/timesheet finds).
- `corpus/gc15_ratecards/` — 13 G-Cloud 15 vendor rate cards (2026 vintage, UK/offshore columns), already extracted.
- `corpus/scripts/v3_download.py` — fetches the 388 originals into `corpus/downloads/` (gitignored). **The Sept 1 package** (framework fetch script + 48-original downloader + earlier extractions) is delivered separately — Kyle drops its contents into `corpus/` before the first download run.
- Known truth: public matched invoice↔timecard pairs barely exist; the synthetic factory (src/twm/synth) carries reconciliation training.

## Build order

- **M0 (Kyle):** git init; drop Sept 1 package into corpus/; run all download scripts (Claude Code can run them — this machine has normal internet).
- **M0 — DONE (Sept 13, 2026).** 419 of 450 originals fetched; the 31 that block scripted clients are listed in `docs/corpus-missing-originals.md` (handed to Cowork). Python 3.12 + `.venv` on Kyle's machine; run everything with `.venv/Scripts/python.exe`.
- **M1: Role Framework v0 — DONE (Sept 13, 2026)** per specs/role-framework-v0-spec.md. `taxonomy/` holds the five CSVs (families, roles, band crosswalk, tech vocab, title mappings) and `REPORT.md` (98% round-trip, 0 ambiguous, all rate grids band-monotonic). Code: `src/twm/taxonomy/` (models, store, acceptance) and `src/twm/pipeline/normalize.py` (rules 1–6) + `mapping_table.py`. Regenerate the report with `python -m twm.taxonomy.acceptance`; the seed script `scripts/seed_taxonomy_v0.py` is provenance only — edit the CSVs directly from now on (append/deprecate). Open for Kyle: two added families and generic Packaged Applications roles (requirements doc §3.5).
- **M2: Thin thread.** One document (a G-Cloud card, then Michigan/Deloitte contract) through ingest → extract (task contract) → normalize (mapping table) → ledger rows, with field-level scoring. A skeleton of the whole system, not a stage demo.
- **M3: Eval harness** per spec; gold-set tooling; baseline Claude-vs-GPT comparison on the public corpus.
- **M4: Synthetic factory** (templates from real structures; planted leakage; labels by construction).
- **M5+: Azure wiring** (Document Intelligence, Foundry endpoints, Bicep/Terraform per-tenant deploy) once the TWM dev subscription exists — keep all of it behind interfaces until then.

## Conventions

Python 3.11+, pydantic models for every task contract and table row; pure functions where possible; every LLM call goes through one thin client wrapper (model name = config); no secrets in repo (.env); tests for normalization rules and eval math from day one. Currency/units: store rates as decimal + currency + unit (hr/day) + as-stated; never silently convert — conversions are derived columns with the rate-date FX noted.

## Working docs

`docs/requirements-and-rationale.md` is the decision log (status labels: Decided/Directional/Proposed/Parked) — update it when a decision lands here. The canonical copy lives in Kyle's Claude "TWM" project; keep them in sync via Kyle.
