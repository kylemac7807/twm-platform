# TWM Platform — AI/LLM Architecture Design Decisions

**Version:** 0.1 (working draft) · **Date:** September 1, 2026 · **Prepared by:** Kyle McNamara
*(Repo snapshot of the canonical doc in the Claude "TWM" project. Later decisions — taxonomy axes, four bands, technology-as-attribute, benchmark publication, training-vs-benchmark data — are in `requirements-and-rationale.md`.)*

---

## Purpose

This document records the architectural decisions taken for the TWM Phase 1 AI/LLM platform, together with the reasoning behind each. Several decisions here supersede or correct language in *TWM Summary Technical Approach v1.2 (January 29, 2026)*; those are flagged in Section 9.

## 1. Platform: Azure, with models deployed through Microsoft Foundry

**Decision.** Standardize on Azure as the deployment environment for all client-facing components, with frontier models deployed through Microsoft Foundry inside the client's own Azure subscription.

**Rationale.** The constraint that matters most is not technical capability but CISO acceptance. Target clients (BFSI, telecom) overwhelmingly run Azure, have existing governance and procurement paths for it, and have in most cases already cleared Azure OpenAI for internal use. That precedent is the single most valuable asset in a security review.

**Important distinction.** "Azure" is the deployment environment; the models are a catalog. Microsoft Foundry hosts OpenAI's GPT models, Microsoft's Phi family, Mistral, Llama, and — GA since July 2026 — Anthropic's Claude models. The platform decision and the model decision are independent.

## 2. Model strategy: agnostic by design, opinionated by evaluation

**Decision.** No architectural commitment to a single model vendor. Each pipeline stage is defined by a **task contract** — a typed input/output schema — with the model serving that contract selected by measured performance against TWM's evaluation harness.

**Known limitation — do not overstate externally.** Prompts are **not** portable between models; swapping a model means re-tuning its prompt and re-scoring against the harness. The honest claim is "model-portable in weeks, not quarters."

**Starting posture (settled by evaluation, not preference):** Document structure/OCR — Azure Document Intelligence (not an LLM decision). Extraction & interpretation — Claude via Foundry, GPT as benchmarked alternate. Normalization — frontier model, resolve-once (§4). Analytics — classical statistics + Azure AI Search embeddings.

## 3. The pipeline is four layers, not one model choice

1. **Document structure** (OCR, tables, layout) — Azure Document Intelligence.
2. **Extraction and interpretation** — where frontier model quality matters most; long-document extraction with complex nested tables is a genuine differentiator between models.
3. **Normalization** — high volume, moderate difficulty; mostly NOT a live model call (§4).
4. **Analytics** — rate variance, outliers, benchmarking: classical statistics and vector similarity.

## 4. Normalization: resolve once, look up thereafter

**Decision reversed.** An earlier assumption that normalization should run on small/cheap models for unit economics **is wrong and discarded** — the cost is a rounding error against a $1.5MM engagement.

**The real issue is determinism.** If "Senior Java Developer, Toronto" maps to one code on Tuesday and another on Thursday, the Master Benchmark Ledger is silently corrupt, and TWM cannot reproduce its numbers across the table from a vendor.

**Architecture.** Each distinct title is resolved once by a frontier model with full context → durable mapping table (reasoning + confidence) → all later occurrences are deterministic lookups; new titles check embedding similarity first; only novelty escalates to a model; low confidence routes to a consultant, whose corrections write back. The mapping table is an auditable client-facing artifact: *every title we normalized, and why*.

## 5. Data boundary: two tiers and a promotion gate

Cross-client comparability requires that something travel; the design goal is that what travels is the **vocabulary**, never the **commerce**.

**Local tier (client tenant, never moves):** SOW/document identifiers and audit coordinates; vendor names bound to roles; rates, currency, dates; location, seniority, counts and mix; extracted reasoning text.

**Global tier (TWM's taxonomy):** title-pattern string, role/band mapping, disambiguation rules, confidence. No rate, no vendor-client linkage, no client identifier, no document reference.

**Promotion gate:** (1) k-anonymity by origin — promote only after independent observation at 3+ clients; (2) sanitization — reject project/programme names, cost-centre codes, numerals, vendor-proprietary grade nomenclature; (3) human review. Bootstrap: global tier seeded from public sources (O*NET, DDaT, TBIPS, government rate cards, published MSAs, job postings). *(Amended Oct 6, 2026: SFIA removed — excluded from the product, see requirements §3.1.)*

## 6. Evaluation harness — federated, and a first-class deliverable

Field-level metrics, not document-level. Precision weighted far above recall: a demonstrated false leakage claim loses the engagement and potentially the consortium; missed leakage is caught next refresh — so the harness rewards *flag only when confident, escalate the rest*, and consultants are the recall mechanism. **Federated execution:** gold sets are built and stored in each client's tenant; only scores return to TWM. Gold-set construction is billable Value Acceleration work captured in structured form — the concrete mechanism by which the consortium solves the cold-start problem. Strategic note: a hand-verified eval set across real enterprise SOWs cannot be bought or synthesized by a competitor, appreciates with every engagement, and survives every model generation — a stronger moat claim than model weights.

## 7. What TWM owns versus what TWM rents

**Supersedes the "anonymized neural weights" language in Technical Approach v1.2.** Hosted frontier models cannot be fine-tuned into weights TWM extracts and carries between tenants; that claim will not survive diligence.

**TWM owns (portable, improve with data):** Azure Document Intelligence custom extraction models (the real "Expert Models per vendor"), fine-tuned embedding models, anomaly/leakage classifiers. **TWM rents:** the frontier reasoning layer. **What actually travels between clients:** extraction schemas, tuned prompts, the validated taxonomy, the eval methodology, the aggregated ledger.

## 8. Confidentiality posture

**Decision.** Replace "differential-privacy weight smudging" with **k-anonymity on the aggregated ledger** (minimum cohort sizes; no individual client's vendor/role rate recoverable) — equivalent guarantee, buildable in weeks, explainable to a CISO in one sentence.

**Client-facing commitment:** TWM never takes custody of client data — consultants work in-client, models run in the client tenant, the local ledger stays there; TWM retains a taxonomy and aggregated statistics. Consortium agreement language: *"TWM may retain role taxonomy mappings that are not unique to your organization. TWM does not retain rates, commercial terms, vendor relationships, or documents."*

## 9. Open items and required document changes

Open: Foundry data-handling terms in writing; air-gapped open-weight fallback definition; public bootstrap corpus (**done — see corpus catalog**); confidence thresholds; cohort size k (working assumption 3).

Document changes: Technical Approach v1.2 — replace neural-weights/differential-privacy language with §7–§8, keep "Expert Models" scoped to Document Intelligence; Pitch Deck v1.1 — moat narrative leads with taxonomy/eval set/ledger; both remove GPT-4o references for model-agnostic language.
