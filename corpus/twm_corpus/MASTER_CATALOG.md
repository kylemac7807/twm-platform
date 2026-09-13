# TWM Public Bootstrap Corpus — Master Catalog

**Assembled:** September 1, 2026 (v2 — includes the deep pass)
**Purpose:** Seed material for TWM's global taxonomy tier, benchmark ledger, and LLM extraction development corpus, per §5 and §6 of *AI Architecture Design Decisions v0.1* ("Public bootstrap corpus" open item).

**Vintage policy (v2):** rate data and contract structure have different freshness requirements. Every rate artifact carries an explicit VINTAGE/EFFECTIVE header; deep-pass rate artifacts (prefix `deep2_`) are all 2024–2026. Older contract documents are retained deliberately — they train the extraction pipeline on document structures, and never feed the benchmark ledger. The ledger design should carry an effective-date on every rate row and publish benchmarks only from recent vintages.

---

## How this corpus was collected — read this first

This research environment can read the web but is blocked from downloading original files (PDFs, spreadsheets) directly. So the corpus takes two forms:

1. **Structured extractions (ready to use now).** Every file in `02_rate_cards/` and `03_contracts_sows/` is a faithful extraction of the original document — real rate tables as CSV, contract structures and pricing terms as Markdown — with the source URL, issuer, date, currency, and licensing embedded in each file's header. The rate data is usable immediately for taxonomy and benchmark seeding.
2. **Download scripts for the originals (run on your machine).** For production ingestion and extraction-model training you want the original PDFs/XLSX. Two scripts fetch everything in one pass from any normal machine:
   - `01_skills_frameworks/fetch_frameworks.sh` — 13 framework files (O*NET, NIST/NICE, ENISA, CEN, etc.)
   - `download_originals.sh` (corpus root) — 29 original rate cards and contracts

Every manifest also lists each URL, so nothing depends on the scripts.

---

## 01 — Skills frameworks (taxonomy backbone)

Full detail in `01_skills_frameworks/manifest.md`. Verified sources, queued for download:

| Framework | What it gives TWM | Commercial licensing |
|---|---|---|
| **O*NET 31.0** (US DoL) | Largest public synonym corpus mapping lay/vendor job titles to occupations; skills files | CC BY 4.0 — fully commercial-safe |
| **UK DDaT capability framework** | Best free role × seniority-level × skill-proficiency matrix (53 roles, junior→principal ladders) | OGL v3.0 — commercial OK with attribution |
| **NICE / NIST SP 800-181r1** | Machine-readable role→task/skill decomposition with stable IDs (cyber roles) | US public domain |
| **ESCO v1.2.1** (EU) | Best multilingual title-synonym source | EUPL 1.2 — commercial OK; needs 2-min email registration to download |
| **CEN CWA 16458 + ENISA ECSF** | 30 European ICT role profiles; free entry into the e-CF ecosystem | Free CWAs; EN 16234 itself is a paid standard (~€100–200, optional) |
| **Singapore SFw-ICT** | Career maps with levels | Clear IMDA permission before any redistribution |

### ⚠ SFIA 9 — the flag that needs your decision

SFIA is the intended backbone of the taxonomy, and it is the one framework with real licensing consequences:

- The SFIA 9 documents (PDF, Excel, RDF) require **free registration** at sfia-online.org — but that grants **personal/internal use only**.
- Embedding SFIA in a commercial product requires the **SFIA Partner Licence: £2,000/yr (single country) or £4,000/yr (global), plus a 5% royalty on products "dependent on SFIA data,"** with obligations to keep mappings current (accredited-consultant costs are small).
- **The 5% royalty scope is the material question.** Whether a taxonomy *seeded from* SFIA makes the TWM platform "dependent on SFIA data" needs a legal read and likely a direct conversation with the SFIA Foundation — before SFIA is hard-wired into the product. The fallback if terms are unattractive: build the internal taxonomy on O*NET + DDaT (both commercially free) with an SFIA crosswalk kept internal.

---

## 02 — Rate cards (15 artifacts, 11 with real rates)

Full detail in `02_rate_cards/manifest.md`. Highlights:

| Artifact | Real rates? | Shape |
|---|---|---|
| **Texas DIR ITSAC NTE rates** (DIR-CPO-4653) | ✔ USD/hr | **360 rows: 60 IT titles × 6 levels** — the densest grid; same structure as enterprise staff-aug rate cards |
| **NY OGS HBITS average awarded rates** (2026) | ✔ USD/hr | 372 rows: 31 titles × 4 levels × 3 regions — the only *average awarded* (vs ceiling) source, with a regional dimension |
| **GSA CALC+ sample + API notes** | ✔ USD/hr | 139 awarded ceiling rates; the open API supports a full ~262k-row export — the natural US market-distribution seed (e.g., Project Manager: n=2,699, avg $151.06) |
| **5 UK G-Cloud 14 SFIA day-rate cards** — Accenture, Deloitte, KPMG, CGI, Capventis | ✔ GBP/day | Roles × SFIA levels 1–7 on one common scale — ideal extraction-training set, and Big-4 vs SME dispersion (SFIA-6 dev: £1,200–£2,400/day) |
| **3 GSA vendor price lists** (54151S) | ✔ USD/hr | Multi-year leveled rates with labor-category qualification descriptions |
| **Canada TBIPS resource categories** | Definitions | ~93 categories with L1/L2/L3 experience gates — Canada's canonical IT category/level matrix; per-diem rates are CPSS-gated (the main Canadian gap) |
| Texas title descriptions, TBIPS solicitation mechanics, Home Office DDaT pay bands | Definitions/salary | Category-definition and qualification text |

Notable: **CGI appears in the UK, Texas, and Canada vehicles** — a ready-made cross-jurisdiction, same-vendor comparison.

---

## 03 — Contracts: MSAs, SOWs, task orders (15 documents, 6 with unredacted pricing)

Full detail in `03_contracts_sows/manifest.md`. Nine SEC EDGAR material-contract exhibits (banking, insurance, telecom, travel, aerospace verticals), five US government contract documents, one Canadian TBIPS solicitation with SOW annex.

**With real, unredacted pricing:**

- **Michigan DTMB / Deloitte "MiIntegrate"** ($109M, 2013–2026) — signed contract + agile SOW + role × rate × hours table ($90–$265/hr), ~30 change notices: a complete 13-year amendment chain.
- **Oklahoma / Deloitte (2018)** — full Big-4 rate card, Partner $350 → Consultant $150.
- **ProQuest / IBM transition SOW (2006)** — unredacted onshore/offshore split: $97 US / $73 onshore / $22.20 offshore.
- **SAIC T&M subcontract (2001)** — complete labor-category rate table with NTE and burn-rate triggers.
- **Comverse / Tech Mahindra (2015)** — multi-year base-fee ramp ($212M) + rate-card-for-additional-volume construct.
- **Texas DIR ITSAC 579 rate card (2024)** — ~50 titles × 6 levels, current generation.

**Structurally valuable even without rates:** Sabre/HP (the most complete public Resource-Unit/ARC-RRC ITO charging taxonomy — exactly the construct in large bank ITO deals), Talcott/Cognizant 2019 (modern insurance BPO/ITO framework MSA with SOW template — the genus TWM's clients hold), CoreLogic/NTT Data, Textron/CSC, First Midwest/FIS (bank/vendor agreement), GSA PWS template, TBIPS task-authorization structure.

---

## Deep pass 2 additions (September 1, 2026 — `deep2_` prefix)

### Rate cards — 11 new artifacts, 10 with real money figures, all 2024–2026 vintage

- **Texas DIR current generation** (DIR-CPO-5570, 2024) — the current NTE grid with per-row provenance. Notable finding: rates are essentially **unchanged since 2020** (one $0.10 change, two title renames) — static state ceilings amid wage inflation is itself a benchmarking story.
- **GSA CALC+ distribution statistics** (live database, queried 2026-09-01) — 22 TWM-relevant labor categories × n/min/max/avg/p25/median/p75/p90 over active GSA MAS awards (e.g., Program Manager: n=2,108, median $179.21, p90 $252.05). Open API, no auth, CC0.
- **7 more UK G-Cloud SFIA cards** — TCS, Wipro, PwC, Kainos, Version 1, HSO, plus a specialists file (Aaseya, Ten10, Infosys offshore benchmark). **Offshore arbitrage now quantified:** TCS offshore developer SFIA-3 £270/day vs £960 onshore; Wipro £150 vs £500; Version 1 publishes full onshore/nearshore/offshore triple grids. Twelve attributed UK vendors total across both passes.
- **Canada Job Bank IT wages** (NOC 2021; LFS 2023–24, published Nov 2025) — official low/median/high hourly wages for software engineers/developers, cybersecurity, IT PM across Canada and all provinces. Explicitly flagged: these are *employee wages*, not vendor billing rates — apply a ~1.5–2.2× loading factor as a bill-rate proxy.
- **NY HBITS region and level definitions** — completes the pass-1 rates CSV.

### Contracts — 8 new documents (23 total)

- **With unredacted pricing:** US Army IDIQ (2006, full CLIN pricing structure); **Michigan/Accenture (2025–27)** — modern signed contract with fixed-fee-per-milestone pricing and key-personnel credits; **nib/wellteq (2022)** — cloud-consumption pricing (AWS pass-through +30% management fee, user-block pricing); a telecom tiered-volume addendum.
- **Structure-rich (BFSI/SI focus):** **Nielsen/TCS A&R MSA (2007)** — the deep pass's crown jewel: 31 articles, 15 schedules, 3 SOW archetypes, offshore-leverage formula, minimum-commitment and most-favored-customer constructs; Symetra/ACS 8-tower insurance ITO; **Express Scripts (Cigna)/Omada MSA** (eff. 2020, filed 2025 — modern buyer-side paper with rate-card attachment and cloud-provider clauses); Scottish Re/ING transition-services agreement (cost-plus-zero-profit genus).
- Date range now 2001–2026, with modern (2020+) construction represented: agile/milestone pricing, cloud consumption, post-2019 redaction conventions.
- CoreLogic/Dell original MSA located but too large to extract here — exact URL recorded for direct download.

## Why this corpus fits the architecture

- **Taxonomy seeding (§5 bootstrap):** O*NET titles + DDaT levels + TBIPS categories + SFIA (pending licensing) give the global tier its pre-client-one vocabulary.
- **Benchmark ledger seeding:** Texas/NY/GSA/G-Cloud rates provide market reference distributions before any consortium data exists.
- **Extraction training & eval (§6 development corpus):** the EDGAR MSAs and state SOWs are exactly the document genus the pipeline must parse — including amendment chains, redactions, offshore splits, and Resource-Unit charging, the hard cases.
- **Synthetic document generation:** the contract structures give templates for generating synthetic SOWs that mimic real construction without any client data.

## Your action list

1. Run the two download scripts from your own machine (they verify each file as it lands).
2. Register (free) at sfia-online.org and pull the SFIA 9 PDF/Excel/RDF for internal use.
3. Get a legal read on the SFIA Partner Licence 5%-royalty scope before SFIA is embedded in the product; open a conversation with the SFIA Foundation.
4. Complete the short ESCO registration for the v1.2.1 CSV bundle.
5. The main remaining gap: **Canadian vendor billing rates** (TBIPS awarded per-diems sit behind the CPSS supplier portal; the Job Bank wage proxy with a loading factor is now in the corpus as an interim). Options: CPSS registration, or an ATIP request.
6. Each manifest's "Leads not downloaded" section lists what remains — G-Cloud 15 when it goes live, current SFIA cards for Cognizant/HCL/TechM/Capgemini/IBM (not published on G-Cloud 14), NY per-title ceiling schedules (only averages are public), the CoreLogic/Dell MSA (URL recorded, needs direct download), and the tails of the EDGAR query veins.
