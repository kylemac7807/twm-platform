# TWM Public Bootstrap Corpus — Master Catalog

**Assembled:** September 1, 2026 (v2 — includes the deep pass)
**Refreshed:** September 12, 2026 (v2.1 — G-Cloud 15 rate cards; see the Refresh section below)
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

---

## Refresh — September 12, 2026 (v2.1: G-Cloud 15)

G-Cloud 15 went live in mid-August 2026 (awards August 6; G-Cloud 14 expires late October). A refresh pass extracted **13 vendor rate cards, all 2026 vintage** (delivered as the separate `TWM_Corpus_v2.1_GCloud15_Refresh_2026-09-12.zip`, folder `gc15_refresh/`).

**Structural change worth knowing:** G-Cloud 15 replaced free-form SFIA PDF rate cards with a **standardized on-page rate card** — Government Digital and Data role taxonomy × seniority, with explicit **UK Rate / Offshore Rate columns**. Offshore arbitrage is now directly observable per vendor rather than inferred.

**Vendors secured:** Accenture, Atos/Eviden, Capgemini, CGI, Deloitte, IBM, Infosys, Kainos, KPMG, Kyndryl, PwC, TCS, Version 1 — including four majors missing from G-Cloud 14 (Atos, Capgemini, IBM, Kyndryl).

**Key findings:**

- **Offshore postures split cleanly in two:** deep-discount (Accenture £650 UK / £275 offshore developer — ~70–75% discount; KPMG steepest at 72–77%; Capgemini, Version 1 similar) versus flat-ratio (TCS £700/£450, Infosys — offshore ≈65% of UK, compensating with the lowest UK rates). PwC remains the rack-rate outlier (developer £3,010/£1,750).
- **Onshore uplift ~6–15% vs May 2024** across refresh vendors (Kainos hardest at +20–35%; Deloitte entry £600→£765) — a live inflation data point for the ledger's vintage policy.
- **Tech Mahindra is absent from G-Cloud 15** (apparently not awarded — itself a data point). Cognizant and HCLTech are on the framework but their consulting rate cards weren't yet discoverable (marketplace search/indexing lag); Wipro's GC15 card likewise pending. Retry paths in `gc15_refresh/manifest.md`.

---

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
6. Each manifest's "Leads not downloaded" section lists what remains — Cognizant/HCLTech/Wipro G-Cloud 15 cards once the marketplace indexes them (retry paths recorded), NY per-title ceiling schedules (only averages are public), the CoreLogic/Dell MSA (URL recorded, needs direct download), and the tails of the EDGAR query veins.

---

## Corpus v3 — September 13, 2026: the contract-document volume pass

Reframed by the ingestion-engine requirement (training needs ORIGINAL documents at volume, with rates in situ), a three-track hunt produced **388 classified URLs of original documents** with one consolidated downloader (`TWM_Corpus_v3_ContractHunt_2026-09-13.zip`: `v3_edgar/`, `v3_gov/`, `v3_invoices/`, `v3_download.py`).

- **EDGAR (223 rows):** 163 MSAs, 47 amendments; 182 pre-2019 (light redaction), 41 post-2019; ~40% BFSI/insurance/healthcare. Standouts: Luxoft/UBS global framework; Molina/Infosys family incl. a change-request-form exhibit; Levi's/Wipro multi-tower; Broadridge/IBM→Kyndryl 9-document amendment lineage (2010–2026); Sears/CSC and Genpact/GE classic ITO texts. Remaining depth is large (the main vein alone has ~4,150 unpaged hits; Perot Systems' 2002 8-Ks hold hundreds of client contracts in three accessions — cheapest v4 win).
- **Government (138 rows):** UK Contracts Finder 48 (incl. DWP "Synergy" £710.9M IBM/Oracle — 48 schedules of one signed mega-deal); US states 64 (Michigan unredacted rate cards $24–$114/hr; Texas DIR Accenture MSA+SOW+pricing; NY, FL, WA, MA, OK); Canada 23 (verified TBIPS packages with SOW annex + Task Authorization + Basis of Payment; 12 French/bilingual rows — French training documents). Some state CDNs are browser-only (recorded; the downloader writes a failures list for manual clicks).
- **Invoices/timecards (27 rows):** the honest finding — matched public IT billing artifacts are near-nonexistent. Best finds: a true invoice↔timesheet reconciliation pair in a Texas PUC docket (hours, rates, clock-times); KY PSC scanned invoice images; bankruptcy fee applications (timecard-grade detail at named-professional rates); a Fulton County audit that manually performs TWM's exact reconciliation and names the discrepancy classes. **Consequence, confirmed: the synthetic factory carries essentially the entire load for contract→timecard→invoice triplets; public documents supply formats and discrepancy patterns.**

**Consolidated download note:** v3's `v3_download.py` fetches the 388 v3 originals; the v2 zip's two scripts fetch the earlier 48 originals + 13 framework files. Three script runs = the complete raw corpus (~450 original documents) on a local machine.
