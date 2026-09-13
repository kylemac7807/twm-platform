# TWM Rate Card Corpus — Manifest (02_rate_cards)

Collected 2026-09-01. Purpose: seed TWM's benchmarking ledger and serve as a development corpus for LLM rate-card extraction.

**Collection-method note:** this environment's egress proxy blocks direct file downloads (curl 403) from all target domains, so no original PDF/XLSX binaries could be saved. Every artifact below is a faithful structured extraction (CSV/Markdown) made via WebFetch from the cited official source, with source URL, issuer, date and caveats embedded in each file's header. For production ingestion, re-download the cited originals from an unrestricted network.

---

## United States — Texas

### US_TX_DIR_ITSAC_NTE_rates_2020_DIR-CPO-4653.csv
- Source: https://www.cgi.com/sites/default/files/2020-11/dir-cpo-4653_appendix_c_itsac_nottoexceedrates.pdf (official Texas DIR contract Appendix C, mirrored by vendor CGI; DIR's own copies at dir.texas.gov / txdir.widen.net were unreachable from this environment)
- Issuer: Texas Department of Information Resources (DIR), ITSAC program, 2020 generation (RFO DIR-CPO-TMP-445)
- Contains: **360 rows of real rates** — 60 IT job titles x 6 levels (Intern 1-3, Level 1-3), USD/hour not-to-exceed rates ($14.83 Help Desk Intern 1 to $193.94 Digital Product Manager L3)
- Why useful: the single densest role-x-level rate grid in the corpus; identical structure to enterprise staff-aug rate cards
- License: Texas public procurement record (public information under TX Public Information Act)

### US_TX_DIR_ITSAC_job_title_descriptions_2024_DIR-CPO-5498.md
- Source: https://www.cgi.com/sites/default/files/2024-10/dir-cpo-5498-appendix-d-itsac-job-category-title-descriptions.docx.pdf (official DIR Appendix D, 2024 generation, vendor-mirrored)
- Issuer: Texas DIR
- Contains: **60 job titles with role descriptions** (no rates) — the category-definition companion to the NTE rate table
- Why useful: title-to-definition mapping for normalizing client job titles; extraction-model training pairs
- License: Texas public procurement record

## United States — Federal (GSA)

### US_GSA_CALCplus_ceiling_rates_sample.csv
- Source: https://api.gsa.gov/acquisition/calc/v3/api/ceilingrates/ (CALC+ Quick Rate API, open, no auth; docs https://open.gsa.gov/api/dx-calc-api/ ; UI https://buy.gsa.gov/pricing/qr/mas)
- Issuer: US General Services Administration
- Contains: **139 rows of real awarded ceiling rates** (USD/hour, fully burdened) across 7 labor categories (Software Developer, Programmer Analyst, Systems Analyst, Project Manager, Data Scientist, Cybersecurity Analyst, Help Desk Technician) with vendor, contract ID, education, min years experience, business size; plus API aggregation stats (n/min/max/avg) per category in the header (e.g., Project Manager: n=2,699, avg $151.06)
- Why useful: market-distribution data (not just one card) — directly seeds benchmark percentiles; API supports bulk CSV export (`&export=y`) for full ~262k-row dataset from an unrestricted network
- License: US Government work / CC0 (data.gov listing)

### US_GSA_MAS_tCognition_pricelist_54151S.md
- Source: https://www.gsaadvantage.gov/ref_text/47QTCA23D003W/0XZCAC.3TPP53_47QTCA23D003W_TCOGNITIONGSAPRICECATALOG.PDF
- Issuer: tCognition Inc. pricelist published on GSA Advantage (official GSA site), SIN 54151S
- Contains: 11 labor categories with **real USD/hour rates over 3 contract years** (2023-2026) incl. Jr/Sr splits (Java Developer $68.52 vs Sr. $104.10) + qualification excerpts
- License: public GSA pricelist

### US_GSA_MAS_ConstellationWest_pricelist_54151S_2025.md
- Source: https://www.gsaadvantage.gov/ref_text/47QTCA25D007E/109Z4I.3W0BZ6_47QTCA25D007E_47QTCA25D007E-3-28-2025-377665.PDF
- Issuer: Constellation West pricelist on GSA Advantage, contract 2025-2030
- Contains: leveled labor categories (III, SME, Entry Level) with **real Year-1 USD/hour rates** + education/experience minimums
- License: public GSA pricelist

### US_GSA_ITSchedule_CDOTechnologies_pricelist_legacy.md
- Source: https://www.gsaadvantage.gov/ref_text/GS35F5457H/0OJBQO.36MJO2_GS-35F-5457H_GS35F5457HGPLOY.PDF
- Issuer: CDO Technologies pricelist on GSA Advantage (IT Schedule 70, contract 1998-2018; rates shown for 2013-2016)
- Contains: coded, leveled labor categories (PM01/PM02, CP01-CP04, SY01-SY05 style) with **real historical USD/hour rates** + detailed per-level qualification text
- Why useful: historical trend anchor + example of internal level-code taxonomies
- License: public GSA pricelist

## United States — New York

### US_NY_OGS_HBITS_avg_hourly_bill_rates_2026.csv
- Source: https://ogs.ny.gov/procurement/23158-hbits-hourly-bill-rate-averages
- Issuer: NYS Office of General Services, HBITS award 23158 (2024-2029); rates effective 7/1/2026
- Contains: **372 rows of real average awarded bill rates** — 31 IT titles x 4 skill levels (Junior/Mid-Level/Senior/Expert) x 3 regions, USD/hour
- CAVEAT (in file header): Region 3 rows are provisional — extraction spot-checks returned values identical to Region 2 while a page summary suggested some differ; re-verify Region 3 against source
- Why useful: only US state source here with *average awarded* (not ceiling) rates, and with a regional dimension — mirrors how banks price by location tier
- License: NYS public procurement data

## Canada

### CA_TBIPS_resource_categories_skills_matrix.md
- Source: https://www.canada.ca/en/public-services-procurement/services/acquisitions/informatics-method-supply/task-based-streams-categories.html
- Issuer: Public Services and Procurement Canada (PSPC)
- Contains: **the full TBIPS category taxonomy** — 7 streams, ~93 resource categories (A.1-A.17, G.1-G.11, I.1-I.11, B.1-B.14, P.1-P.14, C.1-C.17, T.1-T.9) with uniform level definitions (L1 <5 yrs, L2 5-<10 yrs, L3 10+ yrs; some categories allow L3 via 5 yrs + certification). No dollar rates (see Leads)
- Why useful: the canonical Government of Canada IT skills matrix — the taxonomy Canadian suppliers and buyers (incl. BFSI-adjacent vendors) price against
- License: Open Government Licence – Canada / Crown copyright non-commercial reproduction

### CA_TBIPS_solicitation_2025-03_structure_notes.md
- Source: https://canadabuys.canada.ca/sites/default/files/webform/tender_notice/70780/tbips-solicitation--2025-03-programmer-analysts-resources_en.pdf
- Issuer: Government of Canada (CanadaBuys tender document, 2025)
- Contains: TBIPS per-diem pricing mechanics (7.5-hour workday proration, all-inclusive per-diem basis, <=5% period escalation cap, L3>=L2 rate rule); categories A.6/B.1/B.3 Level 2 sought. No rates
- License: Canadian public procurement record

## United Kingdom

### UK_GCloud14_Accenture_SFIA_ratecard.md — **real GBP day rates**, SFIA levels 1-7 x 6 categories (£190-£2,240) + offshore/nearshore discount factors
### UK_GCloud14_Deloitte_SFIA_ratecard.md — **real GBP day rates**, SFIA 1-7 x 6 categories (£450-£2,450) + separate offshore card (£270-£990)
### UK_GCloud14_KPMG_SFIA_ratecard.md — **real GBP day rates**, SFIA 1-7, flat across categories (£400-£2,855)
### UK_GCloud14_CGI_SFIA_ratecard.md — **real GBP day rates**, SFIA 1-7 x 6 categories (£310-£1,680); same vendor group also holds Texas ITSAC and Canadian TBIPS vehicles — cross-jurisdiction comparator
### UK_GCloud14_Capventis_SFIA_ratecard.md — **real GBP day rates**, SFIA 1-7, flat (£800-£1,400) — SME comparator
- Sources: individual PDFs under https://assets.applytosupply.digitalmarketplace.service.gov.uk/g-cloud-14/documents/... (exact URLs in each file)
- Issuer: supplier rate cards published by UK Crown Commercial Service Digital Marketplace, G-Cloud 14 framework (RM1557.14), April-May 2024; all state 8-hour day, M25 travel included, PI insurance included
- Why useful: five real vendor cards on one common SFIA level scale — ideal for extraction-model training (same schema, different layouts) and for Big-4 vs mid-tier vs SME price-dispersion analysis (e.g., SFIA-6 Development: Accenture £1,530 / Deloitte £1,925 / KPMG £2,400 / CGI £1,300 / Capventis £1,200)
- License: published UK government procurement documents (Digital Marketplace public assets; Crown-hosted)

### UK_HomeOffice_DDaT_pay_framework_allowance.md
- Source: https://careers.homeoffice.gov.uk/pay-framework-allowance-pfa/
- Issuer: UK Home Office; 2026/27 pay award
- Contains: **real GBP salary benchmarks** for Government Digital and Data (DDaT) roles by grade (SEO/G7/G6), national vs London, with cash target max and allowance ceilings; links the DDaT capability framework (role/level definitions: https://ddat-capability-framework.service.gov.uk/)
- Why useful: government-side pay comparator against supplier day rates (contract-vs-employee arbitrage analysis)
- License: Crown copyright / OGL v3.0

---

## Leads not downloaded (follow-up)

1. **Texas DIR current NTE rates (2024/25 generation)** — XLSX at https://dir.texas.gov/sites/default/files/IT%20Staff%20Augmentation%20Contracts%20NTE%20Rates.xlsx and per-contract Appendix C PDFs at txdir.widen.net (e.g. DIR-CPO-5617 Appendix C: https://txdir.widen.net/view/pdf/ebsycrqmc7/DIR-CPO-5617-Appendix-C-ITSAC-Not-To-Exceed-Rates.pdf). Blocked here (egress policy / robots). The 2020 rates are captured; pull the current generation for trend pairs.
2. **GSA CALC+ full bulk export** — the API supports `&export=y` CSV export of the full ~262k-record dataset (https://api.gsa.gov/acquisition/calc/v3/api/ceilingrates/?keyword=&page=1&page_size=...&export=y). Needs an unrestricted network; no auth required.
3. **PSPC TBIPS/SBIPS category qualification detail pages & awarded per-diem rates** — category-level qualification grids live at https://www.tpsgc-pwgsc.gc.ca/app-acq/sptb-tbps/categories-eng.html (site unreachable from this environment: TLS chain issue). Awarded TBIPS/ProServices per-diem ceiling rates are visible to registered users in the CPSS (Centralized Professional Services ePortal) — requires GC supplier/buyer login; not centrally published. Consider ATIP/proactive-disclosure mining or CPSS registration.
4. **SBIPS (Solutions-Based IPS) and ProServices category structures** — same PSPC domain issue as above; ProServices categories mirror TBIPS. Pursue when tpsgc-pwgsc.gc.ca is reachable.
5. **Government of Canada Job Bank wage data** (hourly low/median/high by NOC code and province, e.g. https://www.jobbank.gc.ca/marketreport/wages-occupation/22429/ca) — official ESDC wage benchmark for IT occupations; fetch required interactive approval in this environment.
6. **NY HBITS region definitions + full NTE-rate attachments** — award 23158 documents at https://ogs.ny.gov/contract-award-23158 (attachments are on online.ogs.ny.gov, partially unreachable). Region 3 averages need re-verification (see caveat).
7. **UK Digital Outcomes / further G-Cloud cards** — thousands more supplier SFIA cards indexable via site:assets.applytosupply.digitalmarketplace.service.gov.uk "sfia rate card" — good corpus-scaling source.
8. **Virginia VITA / California / other state ITSA rate schedules** — not pursued in this pass; VA eVA and CA CDT publish contract catalogs worth checking.

---

## Deep pass 2 additions (2026-09-01, freshness-focused: 2024-2026 vintages)

All deep-pass artifacts carry a `deep2_` prefix and an explicit VINTAGE/EFFECTIVE field in the header (CSVs also carry a vintage/date column). Same method constraints as pass 1 (WebFetch extractions; downloads blocked).

### deep2_US_TX_DIR_ITSAC_NTE_rates_2024_DIR-CPO-5570.csv — REAL RATES, vintage 2024
- Source: https://www.assyst.net/sites/default/files/2024-09/DIR-CPO-5570_Appendix_C_ITSAC_Not-To-Exceed_Rates.pdf (official DIR Appendix C, current ITSAC generation, vendor-mirrored)
- 360 rows (60 titles x 6 levels, USD/hr) with a per-row provenance column: 174 rows extracted directly from the 5570 PDF; remainder carried from the 2020 grid (DIR held NTE rates essentially flat across generations — verified via full first-half extraction plus 4-title spot check; one change found: ERP Business Analyst L2 $102.40 -> $102.50; two title renames)
- Key finding for TWM: Texas NTE ceilings are static 2020->2024 — a benchmarking talking point in itself

### deep2_US_GSA_CALCplus_category_rate_stats_2026.csv — REAL RATE DISTRIBUTIONS, vintage: live 2026-09-01
- Source: CALC+ Quick Rate API aggregations (https://api.gsa.gov/acquisition/calc/v3/api/ceilingrates/), CC0/US Gov
- 22 labor categories x {n, min, max, avg, p25, median, p75, p90} over active GSA MAS awarded ceiling rates (USD/hr) — e.g. Program Manager n=2,108 median $179.21; Enterprise Architect median $178.97 p90 $275.22; Technical Writer median $90.00. The tidy category x stats table Kyle asked for; 6 pass-1 categories carry partial stats (avg only) where the API response omitted percentiles

### UK G-Cloud 14 SFIA rate cards — REAL GBP DAY RATES, vintages 2024-04 to 2025-04
- deep2_UK_GCloud14_TCS_SFIA_ratecard.md — TCS, card dated 2025-03-12; onshore + offshore grids (offshore Dev L3 £270 vs onshore £960)
- deep2_UK_GCloud14_Wipro_SFIA_ratecard.md — Wipro, 2024-05; onshore UK + offshore India grids (offshore Dev L3 £150 vs onshore £500)
- deep2_UK_GCloud14_PwC_SFIA_ratecard.md — PwC, 2024-05; Big-4 with blended nearshore/offshore Dev/Delivery columns
- deep2_UK_GCloud14_Kainos_SFIA_ratecard.md — Kainos, 2024-04; major UK public-sector SI
- deep2_UK_GCloud14_Version1_SFIA_ratecard.md — Version 1, 2024-05; full onshore/nearshore/offshore three-table model
- deep2_UK_GCloud14_HSO_SFIA_ratecard.md — HSO (Microsoft specialist), card dated 2025-04-04
- deep2_UK_GCloud14_specialists_SFIA_ratecards.md — Aaseya (UK+India grids), Ten10 (a/b/c sub-levels per SFIA level), plus Infosys official "≤£360/day offshore developer" benchmark statement
- With pass 1, the UK set now covers 12 attributed vendors across Big-4, global SIs, Indian majors, mid-tier, and specialists — the offshore-arbitrage evidence Kyle wanted (Indian majors price UK offshore delivery at 25-30% of onshore)

### deep2_US_NY_OGS_HBITS_definitions_regions_levels.md — definitions, vintage: award 23158 (2024-2029)
- Source: https://ogs.ny.gov/procurement/hbits-definitions-23158
- Region geography resolved (R1 upstate; R2 Mid-Hudson: Dutchess/Orange/Putnam; R3 NYC metro incl. Long Island + Westchester/Rockland) and month-based skill-level gates (Junior 12-36 mo ... Expert 84+ mo). Companion to the pass-1 HBITS rates CSV; NYC-metro (R3) rates ≈ R2 in the published averages, partially explaining the pass-1 Region 3 caveat

### deep2_CA_JobBank_IT_hourly_wages_2023-2024.csv — REAL WAGES (proxy), vintage 2023-2024 (updated 2025-11)
- Sources: Job Bank wage reports (URLs in header), ESDC/StatCan LFS, Open Government Licence – Canada
- 41 rows: NOC 21231 software engineers, 21232 software developers, 21220 cybersecurity specialists, 21222 IT project manager — low/median/high CAD/hr, Canada + provinces (Ontario included throughout)
- CAVEAT embedded in file: EMPLOYEE WAGES, not vendor bill rates — apply ~1.5x-2.2x loading factor as a Canadian contract-rate proxy (the Canadian workaround; actual TBIPS awarded per-diems remain unpublished/CPSS-gated)

### Deep pass 2 — remaining gaps
- Canadian vendor BILLING rates: still no public source; CPSS registration or ATIP remains the route
- Cognizant/HCLTech/Tech Mahindra/Capgemini/IBM G-Cloud SFIA cards: not surfaced by search this pass (IBM's card exists but only G-Cloud 12 vintage, 2020 — excluded for freshness); two additional unattributed rate cards were found and skipped for lack of vendor attribution
- NY HBITS per-title NTE ceiling schedules (as opposed to published averages): pricing lives behind the OGS "Pricing Information" link; averages captured are the official published figures
- G-Cloud 15: not yet published as a distinct catalogue in search results; G-Cloud 14 (2024-2026) is the current live framework
