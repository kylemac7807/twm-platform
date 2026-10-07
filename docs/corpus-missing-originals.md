# Corpus originals still to retrieve

**Status as of:** October 6, 2026 (browser batch run; see results section) · **Owner:** Kyle (manual browser download) · **Requested by:** Kyle McNamara

The first full corpus fetch ran on Kyle's machine on September 13 (Python `urllib` and `curl`, retried with a browser user agent). Everything below still refused scripted clients after three passes: HTTP 403 and 404 rows need a real browser session; the HTTP 429 rows (Contracts Finder) are rate-limited, not blocked, and a retry after a day should collect them. Kyle decided to proceed with M1 (Role Framework v0) without these; they become useful at **M2** (the Michigan Deloitte contract is the named second thin-thread document) and **M3** (contract volume for gold sets).

## Totals

| Set | Fetched | Missing | Notes |
|---|---|---|---|
| Corpus v3 (388 URLs) | 368 | 20 | listed in section 2; errors also in `corpus/manifests/v3_downloads/failures.csv` |
| Sept 1 package (48 URLs) | 47 | 1 | listed in section 1 |
| Skills frameworks (14 URLs) | 14 | 0 | SFIA 9 and ESCO remain manual (registration / email); ESCO zip is already in Kyle's Downloads |

**Missing v3 by site:** www.michigan.gov (13), www.sec.gov (1), www.mass.gov (1), www.gsa.gov (1), canadabuys.canada.ca (1), www.courtlistener.com (1), www.dcaa.mil (1), omh.ny.gov (1)  
**Missing v3 by doc type:** signed contract (13), template (4), MSA (1), solicitation package (1), SOW-exhibit (1)  
**Missing v3 by error:** HTTP 403 (16), HTTP 404 (3), error page (1)

## Oct 6, 2026 browser batch — results

Cowork fetched the list through the Claude desktop app's browser pane (Kyle's browser identity; each file verified by magic bytes before saving). **Everything landed in Kyle's Downloads folder under the destination filename below.** Claude Code: move them into the destination folders listed in this document, then re-run `v3_download.py` and `download_originals.sh` so the manifests record them as present.

| Outcome | Files |
|---|---|
| **Retrieved (19)** | Sept 1 package: `MI_DTMB_Deloitte_MiIntegrate_Contract_SOW_Rates_2013-2026_ORIGINAL.pdf` (5.57 MB), `deep2_MI_DTMB_Accenture_ITTraining_Contract_2025_MA250000000723_ORIGINAL.pdf`. v3_gov: all 13 Michigan DTMB contracts `049`–`061` (0.76–16 MB each, all `%PDF-`); `110_Massachusetts_OSD_multiple_ITS75_vendors_template.bin` (**it is a .docx**, 237 KB — content sniffing will catch it); `129_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf` (amendment 001 FR, 181 KB; the manifest URL had a corrupted hash, correct link taken from the notice page). v3_invoices: `007_CourtListener_opinion_..._v_Ho.bin` (the opinion page HTML, 100 KB). |
| **Bonus (2)** | `007_CourtListener_opinion_..._v_Ho_RECAP_opinion.pdf` (159 KB) — the court's own PDF of the opinion linked from the page; better source than the HTML. `129_PSPC_ISC_A0416-183262_TBIPS_solicitation_attachments_2020-04-06.zip` (145 KB) — the full bilingual solicitation package for the same tender. Both go beside their numbered file; catalog as Kyle decides. |
| **Failed (4) — need a new source** | `024_DCAA_Manual_7641_90...pdf`: dcaa.mil returns a 404 page; the manual has moved. `025_NY_State_OMH...pdf`: omh.ny.gov `/omhweb/vendorinfo/` no longer exists (404 on the file and the directory). `115_GSA_n_a_template.pdf` (Alliant 2 ordering guide): gsa.gov served its "We apologize for the inconvenience" error page for both the file and the Alliant 2 program page. `013_Virtusa_Corp_client_MSA.htm`: the filing index lists the exhibit, but sec.gov returns `NoSuchKey` for every file in accession 0001047469-15-004926, including the complete submission `.txt` — try again later or use another Virtusa filing. |
| **Failed (1) — URL gone, as expected** | `US_GSA_MAS_ConstellationWest_pricelist_54151S_2025_ORIGINAL.PDF`: 404; search GSA eLibrary for contract 47QTCA25D007E. |

Remaining after this batch: **5** (DCAA, NY OMH, GSA Alliant 2, SEC Virtusa, GSA Constellation West).

## How to deliver retrieved files

- **v3 rows:** save each file under `corpus/manifests/v3_downloads/<folder>/` using the exact *destination filename* in the table (that is the name the downloader would have used, so re-runs skip it). A zip with those paths is fine.
- **Sept 1 rows:** save beside `corpus/twm_corpus/download_originals.sh` using the filename shown.
- Both downloaders are re-runnable and skip files already present, so partial deliveries are fine.
- Contracts Finder attachment URLs carry no file extension, so the downloader names them `.bin`; every one fetched so far is a PDF. If the 429s persist, open the notice page in a browser and save the attachment. Michigan DTMB: the PDF links 403 to scripts but open normally in a browser.

## 1. Sept 1 package (3 files)

| # | Save as | URL | Error | Notes |
|---|---|---|---|---|
| 1 | `US_GSA_MAS_ConstellationWest_pricelist_54151S_2025_ORIGINAL.PDF` | https://www.gsaadvantage.gov/ref_text/47QTCA25D007E/109Z4I.3W0BZ6_47QTCA25D007E_47QTCA25D007E-3-28-2025-377665.PDF | 404 | GSA MAS price list, Constellation West, SIN 54151S, 2025. URL gone; search GSA Advantage / GSA eLibrary for contract 47QTCA25D007E. |
| ~~2~~ (retrieved Oct 6) | `MI_DTMB_Deloitte_MiIntegrate_Contract_SOW_Rates_2013-2026_ORIGINAL.pdf` | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/006/180000000078.pdf | 403 | Michigan DTMB contract 180000000078 (Deloitte, MiIntegrate). Named in CLAUDE.md as the second M2 thin-thread document. |
| ~~3~~ (retrieved Oct 6) | `deep2_MI_DTMB_Accenture_ITTraining_Contract_2025_MA250000000723_ORIGINAL.pdf` | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/MiDEAL/002/250000000723.pdf | 403 | Michigan DTMB MiDEAL contract 250000000723 (Accenture, IT training, 2025). |

## 2. Corpus v3 (20 files)

### Government contracts — `v3_gov` (16)

| # | Save as (in `v3_downloads/v3_gov/`) | Parties | Doc type | Date | URL | Error | Manifest notes |
|---|---|---|---|---|---|---|---|
| 1 | `049_State_of_Michigan_DTMB_MDHHS_Appriss_Inc_Equifax_signed_contract.pdf` | State of Michigan DTMB/MDHHS / Appriss Inc / Equifax | signed contract |  | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/007/1300025.pdf | 403 | 071B1300025 MI-VINE victim notification system sw maint+enhancements; annual fees $688k/yr, total $10.7M visible |
| 2 | `050_State_of_Michigan_DTMB_MDOT_Datix_USA_Inc_Ecteon_signed_contract.pdf` | State of Michigan DTMB/MDOT / Datix (USA) Inc (Ecteon) | signed contract |  | https://www.michigan.gov/-/media/Project/Websites/dtmb/Procurement/Contracts/Folder13/2200046.pdf?rev=79fd8d728f1245f48b1fa8bd61e39432 | 403 | 071B2200046 CONTRAXX contract mgmt system; hourly rates visible ($200-271/hr by role, on/off-site) |
| 3 | `051_State_of_Michigan_DTMB_Accenture_signed_contract.pdf` | State of Michigan DTMB / Accenture | signed contract |  | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/002/2200168.pdf | 403 | 071B2200168 MiECC contact center + Salesforce CRM; $60.6M value, milestone pricing visible in change notices |
| 4 | `052_State_of_Michigan_DTMB_Deloitte_Consulting_LLP_signed_contract.pdf` | State of Michigan DTMB / Deloitte Consulting LLP | signed contract |  | https://www.michigan.gov/-/media/Project/Websites/dtmb/Procurement/Contracts/inactive/Folder3/8200018.pdf?rev=37824fec97f64eee9d0e25769a08ac2e | 403 | 071B8200018 SAP Commerce eServices tax portal; SOWs + change notices, fixed-fee pricing visible, aggregate $96.7M |
| 5 | `053_State_of_Michigan_DTMB_MDHHS_LexisNexis_VitalChek_signed_contract.pdf` | State of Michigan DTMB/MDHHS / LexisNexis VitalChek | signed contract |  | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/008/190000000305.pdf | 403 | MA190000000305 VERA vital records system; $200/hr dev/QA/BA rates visible, SOWs in change notices |
| 6 | `054_State_of_Michigan_DTMB_IDEMIA_Identity_Security_USA_signed_contract.pdf` | State of Michigan DTMB / IDEMIA Identity & Security USA | signed contract |  | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/002/7700122.pdf | 403 | 071B7700122 ABIS biometric ID system in Azure Gov; $15.7M aggregate, change-notice pricing visible |
| 7 | `055_State_of_Michigan_DTMB_Knowledge_Services_signed_contract.pdf` | State of Michigan DTMB / Knowledge Services | signed contract |  | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/MiDEAL-Media/002/210000000322.pdf | 403 | MA210000000322 IT Staff Augmentation MSP, $800M; full hourly rate card by job classification ($24-114/hr) + MSP fees |
| 8 | `056_State_of_Michigan_unknown_signed_contract.pdf` | State of Michigan / unknown | signed contract |  | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/008/210000000604.pdf | 403 | search-indexed DTMB contract PDF, not fetched |
| 9 | `057_State_of_Michigan_unknown_signed_contract.pdf` | State of Michigan / unknown | signed contract |  | https://www.michigan.gov/-/media/Project/Websites/dtmb/Procurement/Contracts/Folder10/1300256.pdf?rev=c23f8781228c494baedade617190b5ed | 403 | search-indexed enterprise procurement contract PDF, not fetched |
| 10 | `058_State_of_Michigan_unknown_signed_contract.pdf` | State of Michigan / unknown | signed contract |  | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/004/7700072.pdf | 403 | search-indexed contract PDF, not fetched |
| 11 | `059_State_of_Michigan_unknown_signed_contract.pdf` | State of Michigan / unknown | signed contract |  | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/005/180000000572.pdf | 403 | search-indexed contract PDF w/ SOW, not fetched |
| 12 | `060_State_of_Michigan_MiDEAL_Cyber_Defense_Technologies_LLC_signed_contract.pdf` | State of Michigan MiDEAL / Cyber Defense Technologies LLC | signed contract |  | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/MiDEAL-Media/008/220000001402.pdf | 403 | search-indexed MiDEAL cybersecurity contract, not fetched |
| 13 | `061_State_of_Michigan_MiDEAL_unknown_signed_contract.pdf` | State of Michigan MiDEAL / unknown | signed contract |  | https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/MiDEAL/002/250000001260.pdf | 403 | search-indexed contract PDF w/ SOW, not fetched |
| 14 | `110_Massachusetts_OSD_multiple_ITS75_vendors_template.bin` | Massachusetts OSD / multiple ITS75 vendors | template |  | https://www.mass.gov/doc/its75/download | 403 | ITS75 software & services statewide contract user guide; URL resolves (binary Office doc; WebFetch could not parse text) |
| 15 | `115_GSA_n_a_template.pdf` | GSA / n/a | template |  | https://www.gsa.gov/system/files/Alliant%202%20Ordering%20Guide%20(2025).pdf | 404 | Alliant 2 ordering guide (task order process); search-indexed |
| 16 | `129_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf` | PSPC / Indigenous Services Canada / n/a (pre-award) | solicitation package |  | https://canadabuys.canada.ca/documents/pub/att/2020/03/10/8d7836bae7b41b758753d0/ABES.PROD.PW__ZM.B622.F37474.EBSU001.PDF | 404 | TBIPS Application Services A0416-183262 (amendment 001 FR); link extracted from fetched tender notice pw-zm-622-37474; / |

### EDGAR filings — `v3_edgar` (1)

| # | Save as (in `v3_downloads/v3_edgar/`) | Parties | Doc type | Date | URL | Error | Manifest notes |
|---|---|---|---|---|---|---|---|
| 1 | `013_Virtusa_Corp_client_MSA.htm` | Virtusa Corp / (client) | MSA | 2015-05-20 | https://www.sec.gov/Archives/edgar/data/1047469/000104746915004926/a2224790zex-10_43.htm | 403 | Offshore professional services agreement (CIK in URL is filer agent; see accession) |

### Invoices and timesheets — `v3_invoices` (3)

| # | Save as (in `v3_downloads/v3_invoices/`) | Parties | Doc type | Date | URL | Error | Manifest notes |
|---|---|---|---|---|---|---|---|
| 1 | `007_CourtListener_opinion_W_D_N_C_3_18_cv_00273_CS_Technology_Inc_Sitehands_Inc_v_Ho.bin` | CS Technology Inc & Sitehands Inc v. Horizon River Technologies LLC | SOW-exhibit | 2018-2021 | https://www.courtlistener.com/opinion/9789482/cs-technology-inc-v-horizon-river-technologies-llc/ | error page | IT infrastructure billing dispute (~$1.6M invoiced; $1.08M claimed). Opinion quotes SOW unit pricing ($11,465/site build |
| 2 | `024_DCAA_Manual_7641_90_DoD_contractors_template.pdf` | DoD contractors | template | 2023-11-14 | https://www.dcaa.mil/Portals/88/Documents/Guidance/CAM/Information%20For%20Contractors%20DCAAM%207641_90.pdf | 403 | Enclosure 6 Figures 7-10: sample SF-1034/1035 interim and completion vouchers plus required invoice data elements and ti |
| 3 | `025_NY_State_Office_of_Mental_Health_vendor_guidance_NYS_vendors_NYS_agencies_templa.pdf` | NYS vendors -> NYS agencies | template | 2018 example | https://omh.ny.gov/omhweb/vendorinfo/example-proper-nys-invoice.pdf | 404 | Annotated example of a proper NYS invoice: invoice #, NYS vendor ID, PO ref, line item '50 Hours @ $30.00 = $1,500', ter |

