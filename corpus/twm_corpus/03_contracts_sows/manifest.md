# TWM Development Corpus — 03_contracts_sows Manifest

**Assembled:** 2026-09-01
**Purpose:** Real, public MSAs, SOWs, task orders, rate cards, and templates for IT/professional services — development corpus for TWM's LLM extraction pipelines (rate cards, role titles, pricing formulas, commercial terms).

**IMPORTANT — retrieval method:** The sandbox's egress proxy blocks direct file downloads (curl/wget CONNECT denied by organization policy for all non-registry hosts, including sec.gov). Raw PDFs/HTML could therefore NOT be saved as binaries. Each corpus file below is a **detailed structured extraction** (parties, document structure, all visible rate/pricing data, commercial terms) captured via the sanctioned WebFetch tool, with the **raw source URL recorded in its header** so the raw original can be re-downloaded in one pass from an unrestricted environment. All sources are official public records (SEC filings, government procurement sites, Canada open procurement).

---

## Files

### SEC EDGAR — public-company material contract exhibits (public records)

| # | File | Parties / Filing | Date | What it is | Rate tables / labor categories? |
|---|---|---|---|---|---|
| 1 | `EDGAR_FNIS_MicroGeneral_IT_Services_Agreement_2001_EX10-55.md` | Fidelity National Information Solutions / Micro General (FNIS 10-K405 2002, EX-10.55) | 2001-08-02 | Full System Development, Maintenance & IT Services Agreement (MSA) | Labor-rate schedule structure (Schedule 6/7 referenced); CPI-capped escalation, MFC pricing clause. **No numeric rates in extraction; check raw exhibit tail** |
| 2 | `EDGAR_Textron_CSC_MSA_Amendment7_2010_EX10-22.md` | Textron / Computer Sciences Corp (Textron 10-K 2011, EX-10.22E) | 2010-09-30 | Amendment 7 to landmark 2004 multi-tower ITO MSA (Contract TXT2004-0020) | Resource Unit pricing by year + LCC discounts — **values redacted [***]**; structure intact |
| 3 | `EDGAR_Sabre_HP_IT_Services_Agreement_Amend1_2012_EX10-42.md` | Sabre / HP Enterprise Services (Sabre S-1/A 2014, EX-10.42) | 2012-09-14 | Amendment 1 to Second A&R IT Services Agreement — full ITO charging architecture | Complete Resource Unit taxonomy (mainframe/midrange/network/EUC), ARC/RRC banding, MRC — **rates redacted** |
| 4 | `EDGAR_Comverse_TechMahindra_MSA_Amendment1_2015_EX10-1.md` | Comverse / Tech Mahindra (Comverse 8-K 2015, EX-10.1) | 2015-06-30 | Amendment 1 to R&D/ITO rebadging MSA | **YES — real multi-year Base Fee table ($41M→$28M, $212M total)**; man-year capacity pricing; references Schedule 4 rate card |
| 5 | `EDGAR_FirstMidwestBank_FIS_IT_Services_Agreement_2011_EX10-30.md` | First Midwest Bank / Fidelity Information Services (10-K 2012, EX-10.30) | 2011-11-30 | Bank-vertical IT services agreement (item processing, print/mail) | Fee constructs visible ($25 non-ACH fee, ECI escalation cap, 1.5%/mo late interest); detailed pricing attachments redacted |
| 6 | `EDGAR_SAIC_ISIS_TM_Subcontract_LaborRates_2001_EX10-1.md` | SAIC / Isis Pharmaceuticals (Isis 8-K 2001, EX-10.1) | 2001-07-20 | T&M/labor-hour subcontract with SOW | **YES — FULLY UNREDACTED labor-category hourly rate table** ($112.15–$395.09/hr); NTE ceiling, burn-rate triggers, 15% material handling |
| 7 | `EDGAR_Talcott_Cognizant_MSA_2019_EX27h.md` | Talcott Resolution / Cognizant (485BPOS 2022, EX-27(h)) | 2019-09-01 | Modern insurance-vertical BPO/BPaaS/ITO/ADM framework MSA + blank SOW template (Exhibit B) | No rates (framework MSA); COLA, pass-through, key-position caps, SOW charging framework |
| 8 | `EDGAR_CoreLogic_NTTData_MSA_Amendment8_2019_EX10-52.md` | CoreLogic Solutions / NTT DATA Services (CoreLogic 10-K 2020, EX-10.52) | 2019-12-01 | Amendment 8 to MSA + Supplement A (ITO) | Rate Card + ARC/RRC + Baseline Charges updated via annual **ECA** adjustment (values in schedules) |
| 9 | `EDGAR_ProQuest_IBM_TransitionSOW_RateCard_2006_EX10-34.md` | ProQuest / IBM (Voyager Learning 10-K 2007, EX-10.34) | 2006-02-15 | IBM project change request — wind-down/transition SOW (staff augmentation) | **YES — UNREDACTED: $97/hr US, $73/hr onshore-India, $22.20/hr offshore; $85,150/mo fixed PMO fee** |

### US government — signed contracts, rate cards, process docs, templates

| # | File | Issuer / Vendor | Date | What it is | Rate tables / labor categories? |
|---|---|---|---|---|---|
| 10 | `OK_OMES_Deloitte_Signed_Contract_RateCard_2018.md` | State of Oklahoma OMES / Deloitte & Touche (Contract 1600000037) | 2018-03 | Full signed professional-services contract (engagement letter + addendum) | **YES — UNREDACTED Deloitte rate card: Partner $350 → Consultant $150/hr; $235,770 fixed fee** |
| 11 | `TX_DIR_ITSAC_579_NTE_Rate_Card_2024.md` | Texas Dept. of Information Resources — ITSAC program | 2024-10 | Statewide IT staff-augmentation NTE rate card | **YES — the richest find: ~50 IT titles x 6 levels with unredacted NTE hourly rates across 16 categories** |
| 12 | `MI_DTMB_Deloitte_MiIntegrate_Contract_SOW_Rates_2013-2026.md` | State of Michigan DTMB / Deloitte Consulting (MA180000000078) | 2013–2026 | Full signed IT services contract + agile SOW + 30 change notices ($109.2M) | **YES — UNREDACTED role x hourly-rate x hours table ($90–$265/hr), fixed monthly capacity pricing, 93% utilization credit** |
| 13 | `NY_OGS_HBITS_Process_TaskOrder_Mechanics.md` | NY State OGS — HBITS program (Attachment 07) | current | Hourly-based IT services task-order process doc | Rate mechanics (bill vs wage rates, 0.75% admin fee, median+5%/+1SD rate-ceiling formulas); numeric per-title rates in separate Attachment 1 (lead) |
| 14 | `GSA_Army_PWS_Template_Structure.md` | GSA buy.gsa.gov (Army PWS template) | n.d. | Federal Performance Work Statement template (7 parts + 3 technical exhibits) | Template only — labor-category x estimated-hours exhibit schema, deliverables schedule, QASP tables |

### Canada — TBIPS

| # | File | Issuer | Date | What it is | Rate tables / labor categories? |
|---|---|---|---|---|---|
| 15 | `CA_TBIPS_Solicitation_2025-03_SCC_ProgrammerAnalyst_TaskAuth.md` | Standards Council of Canada under PSPC TBIPS SA (EN578-170432) | 2025-07 | Complete TBIPS task-authorization RFP: SOW annex, TA process, Basis of Payment pricing form | TBIPS stream/category/level taxonomy (A.6, B.1, B.3, Level 2); per-diem CAD pricing rules (7.5-hr day, 5% escalation cap, level monotonicity); blank pricing template |

**Counts:** 15 corpus documents — 9 SEC EDGAR exhibits, 5 US government, 1 Canadian. 6 contain actual unredacted rate/fee numbers (#4, 6, 9, 10, 11, 12); 4 more contain complete pricing *structures* with redacted values (#2, 3, 5, 8).

---

## Usage notes
- **SEC exhibits:** public filings, free to use. Redactions marked [***]/[*] follow SEC confidential-treatment rules — prefer #4, 6, 9 where numbers survive.
- **State documents:** published public contract records (OK, MI) and official program pricing documents (TX, NY) — free to use.
- **Federal/Canadian templates:** US government works are public domain; Canadian publications are open procurement documents.
- Every file header carries the raw source URL — run a bulk re-download from an unrestricted machine to replace extractions with raw HTML/PDF originals (SEC requests a User-Agent like "TWM research <email>").

---

## Leads not downloaded (blocked or not yet fetched)

### Blocked by sandbox egress policy / robots / errors
- **All raw file downloads** — curl CONNECT denied org-wide (see header note). Raw URLs recorded per file.
- **Texas DIR Accenture DBITS contract family** (robots-blocked host txdir.widen.net):
  - Contract: https://txdir.widen.net/view/pdf/3wh40d5uom/DIR-CPO-6078-Contract.pdf
  - Appendix A Terms: https://txdir.widen.net/view/pdf/b27ghptq7q/DIR-CPO-6078-Appendix-A-Standard-Terms-and-Conditions.pdf
  - Appendix C Awarded Categories: https://txdir.widen.net/view/pdf/3xgi5hrgoo/DIR-CPO-6078-Appendix-C-Awarded-Categories.pdf
  - RFO: https://txdir.widen.net/view/pdf/fvmgjnueqk/DIR-CPO-6078-RFO-DIR-CPO-TMP-593.pdf
  - Vendor page: https://dir.texas.gov/contracts/vendors/accenture-llp (also DIR-CPO-5153 AI services, DIR-CPO-5171 cloud, DIR-STS-TSS-699 app dev/staff aug)
- **IBM Texas Services Rate Card (TX DIR)**: https://www.ibm.com/downloads/cas/LNQ2A4Z9 (fetch error — likely full IBM rate card, high value)
- **Canada TBIPS official pages** (SSL/robots failures on tpsgc-pwgsc.gc.ca):
  - Streams & categories (full labor-category taxonomy): https://www.tpsgc-pwgsc.gc.ca/app-acq/sptb-tbps/categories-eng.html
  - Supply arrangement: https://www.tpsgc-pwgsc.gc.ca/app-acq/sptb-tbps/am-sa-eng.html
- **Transport Canada TBIPS solicitation** (robots): https://canadabuys.canada.ca/sites/default/files/webform/tender_notice/76744/t8080-250224-tbips-solicitation-oct-15.pdf
- **NITAAC PWS resources** (robots timeout): Cybersecurity PWS sample http://nitaac.nih.gov/sites/default/files/2021-08/cybersecuritypwssample-508.docx ; CIO-SP3 PWS template via https://nitaac.nih.gov/resources/tools-and-templates
- **GSA buy.gsa.gov docviewer** (JS app, no static content): IT Services SOW Template (id=2231), USAF Acquisition PM & IT Support PWS (id=2205) — https://buy.gsa.gov/find-samples-templates-tips
- **tech.gsa.gov Agile Contracts PWS / Task Order templates** (DNS failure): https://tech.gsa.gov/guides/Agile_Contracts_PWS_Template/ ; https://tech.gsa.gov/guides/Agile_Contracts_TaskOrder_Template/
- **DHS FOIA-posted contracts** (403): USCG Administrative & Program Support PWS https://www.dhs.gov/sites/default/files/2025-03/25_0303_cpo_USCG-Contract-70Z02324F12700001-Administrative-and-Program-Support-Services.pdf.pdf ; TSA task order https://www.dhs.gov/sites/default/files/2025-05/25_0502_cpo_tsa-contract-70T02024F7500N019-strategic-planning-and-data-analysis.pdf

### Identified but not yet pursued (promising)
- **NY HBITS Attachment 1 — Pricing Schedules** (per-title, per-region bill/wage rates; companion to file #13): locate under https://online.ogs.ny.gov/purchase/snt/awardnotes/ (73012 family) or the HBITS award page on ogs.ny.gov
- **CoreLogic / Dell Services original MSA (July 2010)** with full schedules — in CoreLogic 2010–2012 EDGAR filings (base of the Amendment-8 chain, file #8); also EX-10.53 (2019 10-K) and 10-Q 2019 EX-10.1
- **Textron / CSC original 2004 MSA** (Contract TXT2004-0020) — Textron 2004/2005 EDGAR filings
- **Micro General 10-K405 2002 EX-10.16/10.17** (.txt siblings of file #1): accession 0000892569-02-000691
- **MPLC, Inc. 8-K 2007** exhibits v064884_ex10-2/-19/-20.htm (accession 0001144204-07-007236) — hit on "MSA + rate card" FTS query, unvetted
- **NeuStar 8-K 2006** EX-10.1 (accession 0000950133-06-004150) — SOW/labor-category hit, telecom-adjacent
- **Scottish Re 10-K 2005 ex10-58.txt** — "IT services agreement + hourly rates" FTS hit, unvetted
- **Oklahoma okcommerce.gov** hosts other full signed vendor contracts (pattern: /wp-content/uploads/...Full-Signed-Contract.pdf)
- **EDGAR full-text search** (https://efts.sec.gov/LATEST/search-index?q=...) — remaining hits: 79 for "MSA"+"rate card", 55 for "IT services agreement"+"hourly rates", 60 for "SOW"+"per hour"+"labor category", 52 for Cognizant MSA variants — plenty more to mine

---

## Deep pass 2 additions (2026-09-01)

Same retrieval method as above (WebFetch structured extractions; raw downloads remain policy-blocked; raw source URL in each file header). Per Kyle's guidance: older material kept for structure/unredacted rates; 2020+ material added deliberately (marked MODERN) for current contract construction. Coordination: NY HBITS Attachment 1 pricing was NOT re-pulled here — the rates agent already captured HBITS rates in `02_rate_cards/US_NY_OGS_HBITS_avg_hourly_bill_rates_2026.csv`.

### Files (deep2_ prefix)

| # | File | Parties / Source | Agreement date (filed) | What it is | Real pricing? |
|---|---|---|---|---|---|
| 16 | `deep2_EDGAR_Nielsen_TCS_ARMSA_2007_EX10-16a.md` | ACNielsen / Tata America Intl + TCSL (Nielsen S-1/A 2010, EX-10.16(a), ~2.3MB raw) | 2007-10-01 (2010) | Landmark India-offshore ITO/BPO A&R MSA: 31 articles, 15 schedules, 3 SOW archetypes (Augmentation/Project/Process), offshore-leverage formula, Minimum Commitment, MFC | Structure complete; rates redacted (*) |
| 17 | `deep2_EDGAR_Symetra_ACS_IT_Services_Agreement_2004_EX10-1.md` | Symetra Life Insurance / ACS (Symetra S-1/A 2007, EX-10.1) | 2004-10-28 (2007) | Insurer full-scope 8-tower ITO with Schedule 3/4/5/6 pricing architecture + benchmarking attachment | Structure; rates redacted [***] |
| 18 | `deep2_EDGAR_ExpressScripts_OmadaHealth_MSA_2020_EX10-4a.md` | Express Scripts (Cigna) / Omada Health (Omada S-1 **filed 2025**, EX-10.4(a)) | 2020-01-01 (2025) | **MODERN** buyer-side MSA on Cigna procurement paper: rate-card attachment, performance credits, Technology-Provider/cloud clauses, SOC 2 + SIG audit regime | Framework only; figures redacted [***] |
| 19 | `deep2_EDGAR_ScottishRe_ING_Transition_Services_Agreement_2004_EX10-58.md` | Security Life of Denver (ING) / Scottish Re (10-K 2005, EX-10.58) | 2004-12-31 (2005) | M&A Transition Services Agreement (TSA) genus: cost-plus-zero-profit, loaded-cost + hourly IT rates, seconded-employee economics | Pricing model unredacted; numeric schedules by reference |
| 20 | `deep2_EDGAR_nib_wellteq_SOW_2022_EX4-44.md` | nib (AU health insurer) / wellteq (AHI 20-F 2023, EX-4.44) | 2022-10-01 (2023) | **MODERN** SaaS support SOW: AWS pass-through + 30% mgmt fee, $3,000+30% DevSecOps, $5,000 acct mgmt, user-block pricing, 99.9% SLA, data residency, 5,000-user rebaseline | **YES — unredacted** |
| 21 | `deep2_EDGAR_USArmy_SFA_IDIQ_Contract_2006_EX10-3.md` | US Army RDECOM / SFA Inc. (GDT&S S-1/A 2010, EX-10.3) | 2006-08-31 (2010) | Federal IDIQ (Uniform Contract Format A–J), $180M NTE, task orders T&M + FFP | **YES — unredacted multi-year CLIN pricing by cost element** |
| 22 | `deep2_MI_DTMB_Accenture_ITTraining_Contract_2025_MA250000000723.md` | Michigan DTMB / Accenture LLP (michigan.gov MiDEAL) | 2025-06-25 to 2027 | **MODERN** signed state contract: GenAI upskilling scope, fixed-fee-per-milestone pricing, key-personnel removal credits ($25k/$50k), NET 45 1% 15, 0.75% admin fee | **YES — unredacted milestone fees ($1.65M)** |
| 23 | `deep2_EDGAR_MobileMessenger_NewMotion_SMS_Addendum_2005_EX10-2.md` | Mobile Messenger / NewMotion (MPLC 8-K 2007, EX-10.2) | 2005-04-28 (2007) | Telecom premium-SMS addendum under MSA: tiered volume pricing (per-message + fixed step), $80/hr dev rate, pay-when-paid | **YES — unredacted** |

**Deep pass 2 counts:** 8 documents (7 EDGAR + 1 state). Real unredacted pricing: 4 (#20, 21, 22, 23). Structures with redacted rates: 3 (#16, 17, 18). Date range of underlying agreements now spans **2001–2026** across the full corpus; modern (2020+) construction represented by #18, 20, 22 (plus filing-era redaction conventions per Reg S-K 601(b)(10)).

### Named-lead outcomes
- **CoreLogic/Dell original MSA:** LOCATED — Amended & Restated MSA filed as EX-10.1 to CoreLogic 10-Q, 2012-10-26: https://www.sec.gov/Archives/edgar/data/36047/000003604712000067/clgx-93012xex101.htm — **too large for WebFetch (>50MB serialized); download raw directly.** Also 10-K/A 2013 exhibit clgx-2012xex1085.htm (accession 0000036047-13-000012).
- **Textron/CSC original 2004 MSA (TXT2004-0020):** apparently never filed in full — FTS shows only amendments: 10-Q 2007-10-29 exhibit10-1.htm (accession 0000217346-07-000147) and 10-K 2011 parts exv10w22c/d/e. Amendment C/D URLs: https://www.sec.gov/Archives/edgar/data/217346/000095012311020392/b83538exv10w22c.htm (and ...22d.htm).
- **Nielsen/TCS amendments** (same family as #16): dex1016b/c/d.htm in accession 0001193125-10-155836; Amendments in 10-Q 2008-11-14 (dex102, dex103, accession 0001193125-08-235348); 2017 renewal announced in 8-K 0001193125-17-310923 (no exhibit filed).

### Additional leads (deep pass 2)
- **FL DMS State Term Contract 80101500-25-STC Management Consulting Services (2025)** — robots-blocked: https://www.dms.myflorida.com/content/download/445265/9364007?version=1 ; Deloitte "complete contract" page under dms.myflorida.com alternate contract source
- **GA DOAS IT Tech Matrix** (statewide IT contracts + rates workbook): https://www.doas.ga.gov/sites/default/files/assets/State%20Purchasing/STATEWIDE%20CONTRACTS/IT%20Tech%20Matrix%20v4.xlsx
- **WA DES 16322 IT Development statewide contract** (4 categories x 3 skill levels; 100+ vendors incl. Accenture): summary https://apps.des.wa.gov/DESContracts/Home/ContractSummary/16322 ; SOW template https://apps.des.wa.gov/contracting/Statement_of_Work_Template.docx (fetch needs approval); scope statement + awarded-contractor XLSX lists on same host
- **MN work order contract template** (404 at indexed URL; search mn.gov/admin for current template)
- **EDGAR unvetted from this pass:** Kanbay International S-1/A 2004 (BFSI-focused SI, accession 0001047469-04-022434); EPAM S-1/A 2011 (0001193125-11-194882); Genpact S-1/A 2007 (0001047469-07-005441 — GE MSA family); Waldencast EX-10.39 (3PL rate-card structure, non-IT — skipped deliberately); NeuStar 8-K 2006 EX-10.1 (URL 404, re-derive filename from index 0000950133-06-004150)
