# EDGAR Full-Text Search Harvest v3 — Method Notes
Date: 2026-09-13. Output: `manifest.csv` (223 rows).

## Method
- Used the EDGAR full-text search JSON API directly: `https://efts.sec.gov/LATEST/search-index?q=%22<phrase>%22[&forms=...][&from=N]` via WebFetch. FTS covers filings from ~2001 onward only — anything older is invisible to this method.
- Each API page returned 100 hits (`from=` paginates). For vendor-name queries, `forms=8-K,10-K,10-Q,S-1,F-1,20-F,S-4` was essential to suppress fund/proxy noise (485BPOS Talcott flood, N-CSR, DEF 14A).
- Direct URLs constructed as `https://www.sec.gov/Archives/edgar/data/<CIK>/<accession-no-dashes>/<filename>` from each hit's `_id` (`accession:filename`) and CIK.
- Curated to exhibit-type hits (EX-10.x, EX-4.x, EX-99.x agreements); excluded whole 10-K/10-Q documents, press releases, proxies, and pharma/CRO/clinical agreements that matched only on boilerplate phrases.
- Counterparty column: filled only where the filename, the query that surfaced the hit, or spot-verification supports it; parenthesized entries are inferences to confirm at extraction time.
- `redaction_era`: pre/post the April 2019 Reg S-K Item 601(b)(10) redaction-regime change, keyed on filing date.

## Queries run (vein → total FTS hits → state)
| Vein | Hits | State |
|---|---|---|
| "master services agreement" + "statement of work" | 4,356 | Mined pages 1–2 (200 hits). **Very deep — ~4,150 hits unpaged.** |
| "information technology services agreement" | 1,439 | Page 1 mined. Deep. |
| "rate card" + "master services agreement" | 273 | Page 1 mined; remainder is largely Talcott 485BPOS duplicates. Mostly exhausted for quality. |
| "labor category" + "hourly rate" | 320 | Page 1 mined; mostly govcon/pharma; low residual value. |
| "task order" + "time and materials" | 2,371 | Page 1 mined; heavy govcon/press-release noise; medium residual value. |
| "professional services agreement" + "offshore" | 925 | Page 1 mined; mostly 10-K body text; low-medium residual. |
| "offshore development center" + "agreement" | 312 | Page 1 mined; good ODC exhibits captured. Mostly exhausted. |
| "information technology outsourcing agreement" | 161 | Mined; exhibits captured (D&B/CSC, NAVL, Westar/KG&E); rest is body text. Exhausted. |
| "applications development and maintenance" + "agreement" | 176 | Mined; good ADM exhibits (Orbitz, Affinion, Dollar Thrifty, MIVA, HealthAxis). Mostly exhausted. |
| "business process outsourcing" + "master services agreement" | 989 | Page 1 mined; StarTek/WNS/EXL/Exela body-text heavy. Medium residual. |
| Vendor: Tata Consultancy + SOW | 308 | Mined; mostly Talcott/Allianz fund exhibits + Nielsen (held). Exhausted. |
| Vendor: Infosys + MSA | 1,183 | Page 1 mined → Molina, Gap, Netegrity. Deep but noisy (proxies/N-PX). |
| Vendor: Wipro + SOW (forms-filtered) | 162 | Mined → Levi, Harte-Hanks, CoSine, Tangoe. Mostly exhausted. |
| Vendor: Accenture + SOW (filtered) | 558 | Page 1 mined → Hawaiian Telcom, WGL, XL, Affirmative, Spirit. Deep. |
| Vendor: Cognizant + SOW (filtered) | 931 | Page 1 mined → Health Net, Voya, Aspen. Deep but pharma-noisy. |
| Vendor: IBM (full name) + SOW (filtered) | 743 | Page 1 mined → CDI, ABM, Juniper, Broadridge, ServiceMaster. Deep (Brocade OEM noise). |
| Vendor: HCL + SOW (filtered) | 169 | Mined. Mostly exhausted. |
| Vendor: Capgemini + SOW (filtered) | 133 | Mined; TIAA-CREF Life EX-10.J best find. Mostly exhausted. |
| Vendor: CSC (full name) + MSA (filtered) | 199 | Mined → Sears, Textron amendments, D&B, Marconi. Mostly exhausted. |
| Vendor: Atos + MSA (filtered) | 72 | Mined; QTS 8-K exhibit turned out to be a real-estate contract (dropped). Exhausted. |
| Vendor: EPAM + MSA (filtered) | 133 | Mined; mostly EPAM's own 10-K body text. Exhausted. |
| Vendor: Tech Mahindra + MSA | 86 | Mined; Comverse/TechM (held) + Quadrant 4. Exhausted. |
| Vendor: Genpact + MSA (filtered) | — | 500 error twice (rate limit); GE-family agreements captured via other veins. Retry later. |

## Residual depth (where a v4 pass should dig)
1. **"master services agreement" + "statement of work"** — ~4,150 hits unpaged (pages 3–44). Add `forms=` filter and page `from=200...` onward.
2. **Perot Systems 2002 8-K contract dumps** (accessions 0000950134-02-007532, -007954, -007966/7): several hundred EX-99.x client IT contracts in three accessions; manifest samples 6. Enumerate the accession index pages directly for a bulk win.
3. **"information technology services agreement"** pages 2+ (~1,340 hits unpaged).
4. Accenture/Cognizant/IBM/Infosys vendor veins, pages 2+.
5. Untried: "service level credit", "full-time equivalent" + "offshore", "managed services agreement" + "service levels", "resource unit" (classic ITO pricing term), "ARC/RRC".

## Spot verification (10 fetches)
1. Molina/Infosys `moh-09302019ex101.htm` — VERIFIED: First Amendment to MSA (base MSA 2019-02-04), signed, pricing/Azure charge clauses. (Row updated to amendment.)
2. Broadridge/IBM `ex101ibmitagmtamdt12.htm` — VERIFIED: Amendment No. 12 to IT Services Agreement, IBM/Broadridge, term extension + SOW/pricing attachments.
3. Levi/Wipro `lvis11302014ex-1025.htm` — VERIFIED: Master Services Agreement dated 2014-11-07, Levi Strauss & Co. / Wipro Ltd (HR, F&A, IT, CS towers); rate exhibits referenced.
4. Health Net/Cognizant `d58702dex101.htm` — VERIFIED: Amendment No. 1 to A&R MSA, Cognizant Healthcare Services LLC + CTS US Corp / Health Net.
5. Genpact/GE `a2178844zex-10_5.htm` — VERIFIED: Third Amendment to GE MSA (GE / Genpact International S.a.r.l.), full clause set.
6. Graphic Packaging/NTT `exhibit1033-nttmasterservi.htm` — VERIFIED: A&R MSA dated 2023-12-15, Graphic Packaging International LLC / NTT DATA Americas; charges/invoicing articles.
7. Sears/CSC `c87419exv10wxcy.htm` — VERIFIED: Master Services Agreement dated 2004-06-01, CSC / Sears Roebuck; full ITO clause set.
8. QTS/Atos `d752202dex101.htm` — **FAILED**: resolves to a McGraw Hill/QTS real-estate Contract of Sale, not the Atos MSA. Row removed. (Atos MSA may be a sibling exhibit in the same accession — check the accession index.)
9. Luxoft `a2215656zex-10_7.htm` — VERIFIED: Amended & Restated Global Framework Agreement #6481, UBS AG (Stamford) / Luxoft USA — marquee BFSI framework with schedules.
10. UnitedHealth `dex10c.htm` — VERIFIED: Amendment No. 4 to Information Technology Services Agreement, Unisys / United HealthCare Services (base agreement 1996-06-01).

Verification rate: 9/10 URLs resolve to genuine agreement text. Expect ~90%+ of manifest URLs to be genuine; parenthesized counterparties need confirmation at extraction time.

## Exclusions / already-held handling
Prior-pass documents recognized and either excluded or flagged in notes: Nielsen/TCS (base — amendments listed as new), Sabre/HP (base — 2017 amendment + 2004 EDS agreement listed as new), Talcott/Cognizant (excluded — 485BPOS duplicate flood), CoreLogic/NTT (base — 2019–20 amendments listed), Textron/CSC (base — 2005/2007/2011 amendments listed), Comverse/TechMahindra (flagged already-held), Symetra/ACS (excluded), Express Scripts/Omada (related Cigna-Evernorth docs listed as new).
