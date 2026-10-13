# Term-reading rehearsal over the document library

Run 2026-10-13 by `scripts/term_page_rehearsal.py` with the local reader, no model, no spend. 131 PDFs under `C:\Users\kylem\OneDrive - Straight Line Advisory\Desktop\twm-platform\corpus`; 131 read, 0 failed to read. Files longer than 400 pages were read up to that page (marked capped).

## What it says

- Share of text pages chosen for term reading: median 29%, lower quartile 15%, upper quartile 47%, highest 100%.
- Model calls a full term-reading pass over the library would make: 399 (median 1 per document, most 20).
- Documents that would send every text page: 1.
- Documents of ten or more text pages that would send only the first two: 13 (listed below; a skills framework or a solicitation sending nothing is right).

## By document class

| Class | Documents | Text pages | Pages chosen | Calls |
|---|---|---|---|---|
| rate_card | 26 | 347 | 138 (40%) | 32 |
| amendment | 20 | 3451 | 972 (28%) | 171 |
| sow | 19 | 1172 | 230 (20%) | 46 |
| unknown | 18 | 891 | 131 (15%) | 30 |
| solicitation | 17 | 1454 | 132 (9%) | 33 |
| msa | 16 | 2056 | 353 (17%) | 68 |
| template | 8 | 109 | 31 (28%) | 10 |
| timesheet | 4 | 9 | 8 (89%) | 4 |
| sla | 2 | 95 | 10 (11%) | 3 |
| invoice | 1 | 15 | 12 (80%) | 2 |

## Every document

| File | Class | Pages | Text pages | Chosen | Calls | Left unread by cap | Top signals |
|---|---|---|---|---|---|---|---|
| collected_by_kyle_2026-01\Accenture\Accenture - Cloud Hosting Services.pdf | rate_card | 13 | 13 | 6 | 1 | 0 | rates:4 escalation:2 invoice:1 pricing_model:1 |
| collected_by_kyle_2026-01\Cognizant\Cognizant.pdf | rate_card | 22 | 22 | 7 | 2 | 0 | rates:7 expenses:3 hours:3 escalation:2 |
| collected_by_kyle_2026-01\Deloitte\Deloitte - GSA Schedule.pdf | msa | 36 | 36 | 8 | 2 | 0 | discount:3 escalation:3 contract_no:2 minimum:1 |
| collected_by_kyle_2026-01\LTIS4+PWS+draft.pdf | unknown | 27 | 27 | 5 | 1 | 0 | escalation:1 rates:1 personnel:1 invoice:1 |
| collected_by_kyle_2026-01\LTIS4+SSN+Questions.pdf | unknown | 6 | 6 | 3 | 1 | 0 | pricing_model:2 escalation:1 |
| collected_by_kyle_2026-01\Wipro\Wipro - Cloud Hosting Services.pdf | rate_card | 15 | 14 | 5 | 1 | 0 | rates:3 escalation:2 pricing_model:1 expenses:1 |
| manifests\v3_downloads\v3_gov\049_State_of_Michigan_DTMB_MDHHS_Appriss_Inc_Equifax_signed_contract.pdf | amendment | 207 | 189 | 79 | 14 | 0 | contract_no:43 amendment:39 dates:28 payment:26 |
| manifests\v3_downloads\v3_gov\050_State_of_Michigan_DTMB_MDOT_Datix_USA_Inc_Ecteon_signed_contract.pdf | amendment | 116 | 111 | 41 | 7 | 0 | contract_no:30 amendment:18 payment:17 dates:15 |
| manifests\v3_downloads\v3_gov\051_State_of_Michigan_DTMB_Accenture_signed_contract.pdf | amendment | 400 | 400 | 93 | 16 | 0 | contract_no:47 amendment:41 pricing_model:33 escalation:24 |
| manifests\v3_downloads\v3_gov\052_State_of_Michigan_DTMB_Deloitte_Consulting_LLP_signed_contract.pdf | amendment | 400 | 350 | 120 | 20 | 45 | amendment:112 dates:47 pricing_model:36 invoice:35 |
| manifests\v3_downloads\v3_gov\053_State_of_Michigan_DTMB_MDHHS_LexisNexis_VitalChek_signed_contract.pdf | amendment | 388 | 369 | 57 | 10 | 0 | amendment:25 dates:22 invoice:21 payment:17 |
| manifests\v3_downloads\v3_gov\054_State_of_Michigan_DTMB_IDEMIA_Identity_Security_USA_signed_contract.pdf | msa | 3 | 259 | 56 | 10 | 0 | payment:16 dates:16 contract_no:12 amendment:12 |
| manifests\v3_downloads\v3_gov\055_State_of_Michigan_DTMB_Knowledge_Services_signed_contract.pdf | amendment | 238 | 236 | 30 | 5 | 0 | amendment:15 dates:14 payment:12 contract_no:10 |
| manifests\v3_downloads\v3_gov\056_State_of_Michigan_unknown_signed_contract.pdf | amendment | 400 | 397 | 87 | 15 | 0 | amendment:47 contract_no:29 pricing_model:26 value:23 |
| manifests\v3_downloads\v3_gov\057_State_of_Michigan_unknown_signed_contract.pdf | amendment | 283 | 245 | 71 | 12 | 0 | contract_no:49 amendment:27 invoice:24 value:22 |
| manifests\v3_downloads\v3_gov\058_State_of_Michigan_unknown_signed_contract.pdf | amendment | 317 | 311 | 105 | 18 | 0 | amendment:47 dates:39 contract_no:37 value:37 |
| manifests\v3_downloads\v3_gov\059_State_of_Michigan_unknown_signed_contract.pdf | amendment | 78 | 78 | 32 | 6 | 0 | amendment:20 dates:18 payment:11 contract_no:11 |
| manifests\v3_downloads\v3_gov\060_State_of_Michigan_MiDEAL_Cyber_Defense_Technologies_LLC_signed_contract.pdf | amendment | 210 | 196 | 56 | 10 | 0 | invoice:21 expenses:18 escalation:15 contract_no:15 |
| manifests\v3_downloads\v3_gov\061_State_of_Michigan_MiDEAL_unknown_signed_contract.pdf | amendment | 177 | 154 | 65 | 11 | 0 | hours:36 dates:11 amendment:9 expenses:9 |
| manifests\v3_downloads\v3_gov\062_Texas_DIR_Deloitte_Touche_LLP_signed_contract.pdf | rate_card | 14 | 14 | 6 | 1 | 0 | contract_no:6 discount:3 term:2 expenses:2 |
| manifests\v3_downloads\v3_gov\063_Texas_DIR_Deloitte_Touche_LLP_signed_contract.pdf | sow | 38 | 38 | 11 | 2 | 0 | invoice:6 expenses:6 dates:5 hours:2 |
| manifests\v3_downloads\v3_gov\064_Texas_DIR_Deloitte_Touche_LLP_rate_exhibit.pdf | rate_card | 1 | 1 | 1 | 1 | 0 | discount:1 |
| manifests\v3_downloads\v3_gov\065_Texas_DIR_Deloitte_Touche_LLP_template.pdf | template | 3 | 3 | 2 | 1 | 0 | contract_no:2 expenses:1 pricing_model:1 invoice:1 |
| manifests\v3_downloads\v3_gov\066_Texas_DIR_Deloitte_Touche_LLP_solicitation_package.pdf | solicitation | 64 | 64 | 18 | 3 | 0 | discount:13 minimum:3 volume:1 expenses:1 |
| manifests\v3_downloads\v3_gov\067_Texas_DIR_Accenture_LLP_signed_contract.pdf | rate_card | 11 | 11 | 5 | 1 | 0 | contract_no:5 discount:3 term:2 |
| manifests\v3_downloads\v3_gov\068_Texas_DIR_Accenture_LLP_signed_contract.pdf | sow | 38 | 38 | 11 | 2 | 0 | invoice:6 expenses:6 dates:5 hours:2 |
| manifests\v3_downloads\v3_gov\069_Texas_DIR_Accenture_LLP_rate_exhibit.pdf | rate_card | 5 | 5 | 5 | 1 | 0 | discount:5 |
| manifests\v3_downloads\v3_gov\070_Texas_DIR_Accenture_LLP_template.pdf | template | 4 | 4 | 2 | 1 | 0 | pricing_model:2 expenses:1 parties:1 contract_no:1 |
| manifests\v3_downloads\v3_gov\071_Texas_DIR_Accenture_LLP_solicitation_package.pdf | solicitation | 176 | 176 | 2 | 2 | 0 |  |
| manifests\v3_downloads\v3_gov\072_Texas_DIR_Accenture_LLP_signed_contract.pdf | rate_card | 11 | 11 | 5 | 1 | 0 | contract_no:5 discount:3 term:2 |
| manifests\v3_downloads\v3_gov\073_Texas_DIR_Accenture_LLP_signed_contract.pdf | sow | 38 | 38 | 11 | 2 | 0 | invoice:6 expenses:6 dates:5 hours:2 |
| manifests\v3_downloads\v3_gov\074_Texas_DIR_Accenture_LLP_rate_exhibit.pdf | rate_card | 2 | 2 | 2 | 1 | 0 | discount:2 |
| manifests\v3_downloads\v3_gov\075_Texas_DIR_Accenture_LLP_template.pdf | template | 4 | 4 | 2 | 1 | 0 | contract_no:2 pricing_model:2 expenses:1 parties:1 |
| manifests\v3_downloads\v3_gov\076_Texas_DIR_Accenture_LLP_solicitation_package.pdf | solicitation | 103 | 100 | 19 | 5 | 0 | discount:16 volume:3 contract_no:2 minimum:1 |
| manifests\v3_downloads\v3_gov\077_Texas_DIR_Accenture_LLP_signed_contract.pdf | sow | 7 | 7 | 2 | 1 | 0 | term:1 contract_no:1 |
| manifests\v3_downloads\v3_gov\078_Texas_DIR_Accenture_LLP_signed_contract.pdf | sow | 47 | 47 | 15 | 3 | 0 | expenses:9 invoice:8 term:5 dates:3 |
| manifests\v3_downloads\v3_gov\079_Texas_DIR_Accenture_LLP_signed_contract.pdf | msa | 3 | 3 | 2 | 1 | 0 |  |
| manifests\v3_downloads\v3_gov\080_Texas_DIR_Accenture_LLP_solicitation_package.pdf | solicitation | 613 (capped) | 393 | 2 | 1 | 0 |  |
| manifests\v3_downloads\v3_gov\081_Texas_DIR_Accenture_LLP_signed_contract.pdf | msa | 110 | 110 | 24 | 4 | 0 | contract_no:24 expenses:10 escalation:6 dates:6 |
| manifests\v3_downloads\v3_gov\082_Texas_DIR_Accenture_LLP_signed_contract.pdf | solicitation | 31 | 31 | 11 | 2 | 0 | contract_no:11 expenses:4 passthrough:4 invoice:3 |
| manifests\v3_downloads\v3_gov\083_Texas_DIR_Accenture_LLP_SOW.pdf | sow | 191 | 191 | 39 | 7 | 0 | contract_no:39 escalation:18 invoice:11 dates:10 |
| manifests\v3_downloads\v3_gov\084_Texas_DIR_Accenture_LLP_rate_exhibit.pdf | rate_card | 25 | 25 | 20 | 4 | 0 | contract_no:20 invoice:12 expenses:12 pricing_model:9 |
| manifests\v3_downloads\v3_gov\085_Texas_DIR_Accenture_LLP_rate_exhibit.pdf | rate_card | 11 | 11 | 3 | 1 | 0 | contract_no:3 discount:1 volume:1 |
| manifests\v3_downloads\v3_gov\086_Texas_DIR_Accenture_LLP_signed_contract.pdf | sla | 33 | 33 | 3 | 1 | 0 | contract_no:3 invoice:1 pricing_model:1 escalation:1 |
| manifests\v3_downloads\v3_gov\087_Texas_DIR_Accenture_LLP_signed_contract.pdf | msa | 3 | 3 | 2 | 1 | 0 | contract_no:2 personnel:2 |
| manifests\v3_downloads\v3_gov\088_Florida_Dept_of_Management_Services_Remy_Corporation_signed_contract.pdf | msa | 173 | 173 | 25 | 5 | 0 | escalation:13 expenses:7 hours:4 term:3 |
| manifests\v3_downloads\v3_gov\089_Florida_Dept_of_Management_Services_Infosys_Public_Services_signed_contract.pdf | msa | 17 | 17 | 8 | 2 | 0 | expenses:4 hours:3 term:3 contract_no:2 |
| manifests\v3_downloads\v3_gov\090_Florida_Dept_of_Management_Services_Shanu_Tech_LLC_signed_contract.pdf | msa | 174 | 174 | 25 | 5 | 0 | escalation:13 expenses:8 hours:4 contract_no:3 |
| manifests\v3_downloads\v3_gov\091_Florida_Dept_of_Management_Services_Enterprise_24x7_Inc_signed_contract.pdf | msa | 217 | 216 | 36 | 7 | 0 | escalation:13 term:10 expenses:10 hours:7 |
| manifests\v3_downloads\v3_gov\092_Florida_Dept_of_Management_Services_Revolution_Technologies_LLC_signed_contract.pdf | msa | 180 | 179 | 26 | 5 | 0 | escalation:13 expenses:9 term:5 hours:5 |
| manifests\v3_downloads\v3_gov\093_Florida_Dept_of_Management_Services_Paradigm_IT_Group_LLC_signed_contract.pdf | msa | 553 | 183 | 26 | 5 | 0 | escalation:13 expenses:8 hours:5 term:5 |
| manifests\v3_downloads\v3_gov\094_Florida_Dept_of_Management_Services_Softsages_LLC_signed_contract.pdf | solicitation | 598 | 198 | 29 | 5 | 0 | escalation:16 expenses:9 term:6 hours:5 |
| manifests\v3_downloads\v3_gov\095_Florida_Dept_of_Management_Services_EPI_USE_America_Inc_signed_contract.pdf | msa | 586 | 194 | 28 | 5 | 0 | escalation:14 expenses:9 term:6 hours:5 |
| manifests\v3_downloads\v3_gov\096_Florida_Dept_of_Management_Services_Tekbank_Consultants_Inc_signed_contract.pdf | msa | 577 | 191 | 26 | 5 | 0 | escalation:13 expenses:9 term:5 hours:5 |
| manifests\v3_downloads\v3_gov\097_Florida_Dept_of_Management_Services_Spruce_Technology_Inc_signed_contract.pdf | msa | 220 | 196 | 29 | 5 | 0 | escalation:16 expenses:8 hours:5 term:5 |
| manifests\v3_downloads\v3_gov\098_WA_Dept_of_Social_and_Health_Services_Rebecca_Sue_Davidson_sole_prop_task_order.pdf | solicitation | 40 | 40 | 5 | 1 | 0 | term:4 contract_no:2 dates:1 invoice:1 |
| manifests\v3_downloads\v3_gov\099_NY_State_OGS_multiple_awardees_signed_contract.pdf | msa | 38 | 38 | 20 | 4 | 0 | invoice:7 term:7 expenses:6 pricing_model:4 |
| manifests\v3_downloads\v3_gov\100_NY_State_OGS_30_HBITS_vendors_signed_contract.pdf | msa | 13 | 84 | 12 | 2 | 0 | contract_no:10 escalation:6 rates:5 invoice:2 |
| manifests\v3_downloads\v3_gov\113_GSA_8_a_STARS_III_awardees_multiple_signed_contract.pdf | sow | 62 | 62 | 15 | 3 | 0 | nte:5 pricing_model:5 invoice:4 rates:4 |
| manifests\v3_downloads\v3_gov\114_GSA_Alliant_2_awardees_multiple_signed_contract.pdf | sow | 219 | 218 | 34 | 6 | 0 | rates:13 nte:12 pricing_model:11 expenses:8 |
| manifests\v3_downloads\v3_gov\116_Standards_Council_of_Canada_n_a_pre_award_solicitation_package.pdf | sow | 62 | 62 | 10 | 2 | 0 | expenses:4 invoice:3 term:3 hours:2 |
| manifests\v3_downloads\v3_gov\117_Dept_of_National_Defence_n_a_pre_award_solicitation_package.pdf | sow | 58 | 58 | 9 | 2 | 0 | invoice:4 term:4 expenses:3 dates:2 |
| manifests\v3_downloads\v3_gov\118_Dept_of_National_Defence_n_a_pre_award_solicitation_package.pdf | sow | 76 | 76 | 13 | 3 | 0 | invoice:6 expenses:6 term:4 dates:3 |
| manifests\v3_downloads\v3_gov\119_Government_of_Canada_dept_n_a_pre_award_solicitation_package.pdf | solicitation | 72 | 70 | 2 | 1 | 0 |  |
| manifests\v3_downloads\v3_gov\120_Government_of_Canada_dept_n_a_pre_award_solicitation_package.pdf | solicitation | 59 | 59 | 2 | 1 | 0 |  |
| manifests\v3_downloads\v3_gov\121_IRCC_CIC_n_a_pre_award_solicitation_package.pdf | solicitation | 29 | 29 | 2 | 1 | 0 |  |
| manifests\v3_downloads\v3_gov\122_Government_of_Canada_dept_n_a_pre_award_solicitation_package.pdf | sla | 1 | 62 | 7 | 2 | 0 | escalation:3 pricing_model:2 amendment:1 credit:1 |
| manifests\v3_downloads\v3_gov\123_Government_of_Canada_dept_n_a_pre_award_solicitation_package.pdf | sow | 32 | 30 | 7 | 3 | 0 | invoice:4 expenses:2 discount:2 hours:1 |
| manifests\v3_downloads\v3_gov\124_Government_of_Canada_dept_n_a_pre_award_solicitation_package.pdf | sow | 21 | 17 | 6 | 1 | 0 | expenses:3 rates:2 invoice:2 hours:1 |
| manifests\v3_downloads\v3_gov\125_Government_of_Canada_dept_n_a_pre_award_solicitation_package.pdf | sow | 22 | 18 | 6 | 1 | 0 | rates:3 invoice:3 expenses:2 discount:1 |
| manifests\v3_downloads\v3_gov\126_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | sow | 91 | 91 | 4 | 1 | 0 | expenses:1 term:1 invoice:1 dates:1 |
| manifests\v3_downloads\v3_gov\127_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | solicitation | 101 | 101 | 2 | 1 | 0 |  |
| manifests\v3_downloads\v3_gov\128_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | amendment | 2 | 2 | 2 | 1 | 0 | amendment:2 |
| manifests\v3_downloads\v3_gov\129_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | solicitation | 2 | 2 | 2 | 1 | 0 | amendment:1 |
| manifests\v3_downloads\v3_gov\130_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | amendment | 4 | 4 | 2 | 1 | 0 | amendment:2 |
| manifests\v3_downloads\v3_gov\131_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | solicitation | 4 | 4 | 2 | 1 | 0 | amendment:1 |
| manifests\v3_downloads\v3_gov\132_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | amendment | 6 | 6 | 2 | 1 | 0 | amendment:2 |
| manifests\v3_downloads\v3_gov\133_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | solicitation | 6 | 6 | 2 | 1 | 0 | amendment:1 |
| manifests\v3_downloads\v3_gov\134_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | amendment | 6 | 6 | 4 | 1 | 0 | amendment:2 invoice:2 value:1 minimum:1 |
| manifests\v3_downloads\v3_gov\135_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | solicitation | 6 | 6 | 2 | 1 | 0 | amendment:1 |
| manifests\v3_downloads\v3_gov\136_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | amendment | 3 | 3 | 2 | 1 | 0 | amendment:2 |
| manifests\v3_downloads\v3_gov\137_PSPC_Indigenous_Services_Canada_n_a_pre_award_solicitation_package.pdf | solicitation | 3 | 3 | 2 | 1 | 0 | amendment:1 |
| manifests\v3_downloads\v3_invoices\001_Texas_PUC_Interchange_Docket_53815_Staff_RFI_3_55_response_CorTech_LLC_staffing.pdf | timesheet | 3 | 3 | 2 | 1 | 0 | invoice:1 payment:1 credit:1 |
| manifests\v3_downloads\v3_invoices\002_Texas_PUC_Interchange_Docket_53815_same_RFI_series_CorTech_LLC_Corix_Utilities_i.pdf | timesheet | 2 | 2 | 2 | 1 | 0 | invoice:1 payment:1 credit:1 |
| manifests\v3_downloads\v3_invoices\003_Texas_PUC_Interchange_Docket_53815_Corix_Utilities_rate_case_filings_invoice_tim.pdf | unknown | 2 | 1 | 1 | 1 | 0 |  |
| manifests\v3_downloads\v3_invoices\004_Texas_PUC_Interchange_Docket_53815_Corix_Utilities_rate_case_filings_invoice_tim.pdf | unknown | 12 | 11 | 1 | 1 | 0 |  |
| manifests\v3_downloads\v3_invoices\005_Kentucky_PSC_e_filing_Case_2024_00127_HTI_Inc_SCADA_IT_integrator_LabtronX_Overh.pdf | invoice | 15 | 15 | 12 | 2 | 0 | invoice:8 discount:7 payment:2 expenses:1 |
| manifests\v3_downloads\v3_invoices\006_SDNY_1_19_cv_3508_complaint_The_Register_mirror_The_Hertz_Corp_v_Accenture_LLP_S.pdf | unknown | 16 | 16 | 2 | 1 | 0 | expenses:1 |
| manifests\v3_downloads\v3_invoices\007_CourtListener_opinion_W_D_N_C_3_18_cv_00273_CS_Technology_Inc_Sitehands_Inc_v_Ho_RECAP_opinion.pdf | sow | 24 | 24 | 5 | 1 | 0 | invoice:4 expenses:2 nte:1 rates:1 |
| manifests\v3_downloads\v3_invoices\011_Fulton_County_GA_Office_of_County_Auditor_Covendis_Technologies_IT_temp_staffing.pdf | unknown | 9 | 9 | 4 | 1 | 0 | invoice:2 hours:2 expenses:1 |
| manifests\v3_downloads\v3_invoices\012_NYC_Dept_of_Investigation_report_SAIC_Technodyne_consultants_NYC_Office_of_Payro.pdf | unknown | 27 | 26 | 2 | 1 | 0 |  |
| manifests\v3_downloads\v3_invoices\013_Fort_Bend_County_TX_commissioners_court_agenda_attachment_Tyler_Technologies_For.pdf | unknown | 6 | 6 | 5 | 1 | 0 | invoice:5 payment:5 contract_no:5 |
| manifests\v3_downloads\v3_invoices\014_Ogle_County_IL_board_claims_packet_Various_vendors_De_Lage_Landen_2023_01_17.pdf | unknown | 218 | 169 | 41 | 7 | 0 | expenses:22 hours:22 invoice:14 term:2 |
| manifests\v3_downloads\v3_invoices\015_Magna_Water_District_UT_board_packet_Leverage_IT_Solutions_SKM_Inc_SCADA_IPS_All.pdf | sow | 109 | 71 | 17 | 3 | 0 | expenses:8 nte:6 invoice:5 value:3 |
| manifests\v3_downloads\v3_invoices\016_Central_Water_District_CA_board_packet_Exceedio_IT_MSP_Badger_Meter_ESRI_MKN_Eng.pdf | unknown | 86 | 35 | 7 | 2 | 0 | expenses:3 hours:3 nte:2 value:1 |
| manifests\v3_downloads\v3_invoices\020_Ohio_DAS_procurement_RFP_0A1148_State_of_Ohio_MSP_for_IT_Staff_Augmentation_SOW.pdf | solicitation | 177 | 172 | 28 | 5 | 0 | invoice:10 rates:10 term:8 passthrough:7 |
| manifests\v3_downloads\v3_invoices\021_Tennessee_CPO_pro_forma_contract_RFP_32110_38726_State_of_Tennessee_MSP_for_Cont.pdf | rate_card | 75 | 75 | 21 | 4 | 0 | expenses:10 rates:8 invoice:8 dates:7 |
| manifests\v3_downloads\v3_invoices\022_GSA_forms_library_US_federal_contractors_US_government_template.pdf | template | 1 | 1 | 1 | 1 | 0 | invoice:1 discount:1 contract_no:1 |
| manifests\v3_downloads\v3_invoices\023_GSA_forms_library_US_federal_contractors_US_government_template.pdf | template | 1 | 1 | 1 | 1 | 0 |  |
| manifests\v3_downloads\v3_invoices\026_US_DOL_Wage_Hour_Division_Government_contractors_certified_payroll_template.pdf | timesheet | 2 | 2 | 2 | 1 | 0 | contract_no:2 |
| manifests\v3_downloads\v3_invoices\027_Smartsheet_template_library_Generic_contractor_client_template.pdf | timesheet | 2 | 2 | 2 | 1 | 0 |  |
| twm_corpus\01_skills_frameworks\CEN_CWA16458-1_2018_ICT_Role_Profiles.pdf | unknown | 44 | 43 | 3 | 1 | 0 | escalation:1 |
| twm_corpus\01_skills_frameworks\CEN_CWA16458-2_User_Guides.pdf | template | 40 | 40 | 3 | 1 | 0 | escalation:1 |
| twm_corpus\01_skills_frameworks\CEN_CWA16458-4_Case_Studies.pdf | unknown | 35 | 35 | 2 | 1 | 0 |  |
| twm_corpus\01_skills_frameworks\ENISA_ECSF_Role_Profiles.pdf | unknown | 27 | 26 | 1 | 1 | 0 |  |
| twm_corpus\01_skills_frameworks\NIST_SP800-181r1_NICE_Framework.pdf | unknown | 27 | 27 | 2 | 1 | 0 |  |
| twm_corpus\01_skills_frameworks\SG_SFw_ICT_Consolidated_Career_Maps.pdf | unknown | 561 (capped) | 399 | 36 | 6 | 0 | escalation:25 hours:11 |
| twm_corpus\CA_TBIPS_solicitation_2025-03_structure_notes_ORIGINAL.pdf | sow | 62 | 62 | 10 | 2 | 0 | expenses:4 invoice:3 term:3 hours:2 |
| twm_corpus\deep2_MI_DTMB_Accenture_ITTraining_Contract_2025_MA250000000723_ORIGINAL.pdf | amendment | 45 | 45 | 21 | 4 | 0 | invoice:9 dates:8 amendment:5 term:5 |
| twm_corpus\deep2_UK_GCloud14_HSO_SFIA_ratecard_ORIGINAL.pdf | rate_card | 7 | 7 | 3 | 1 | 0 | rates:3 expenses:1 hours:1 pricing_model:1 |
| twm_corpus\deep2_UK_GCloud14_Kainos_SFIA_ratecard_ORIGINAL.pdf | unknown | 13 | 10 | 4 | 1 | 0 | rates:3 expenses:2 payment:1 hours:1 |
| twm_corpus\deep2_UK_GCloud14_PwC_SFIA_ratecard_ORIGINAL.pdf | rate_card | 5 | 4 | 2 | 1 | 0 | rates:2 discount:1 expenses:1 hours:1 |
| twm_corpus\deep2_UK_GCloud14_specialists_SFIA_ratecards_ORIGINAL.pdf | rate_card | 4 | 4 | 3 | 1 | 0 | rates:3 expenses:1 hours:1 |
| twm_corpus\deep2_UK_GCloud14_TCS_SFIA_ratecard_ORIGINAL.pdf | rate_card | 16 | 14 | 6 | 1 | 0 | rates:4 discount:3 escalation:2 expenses:1 |
| twm_corpus\deep2_UK_GCloud14_Version1_SFIA_ratecard_ORIGINAL.pdf | rate_card | 20 | 19 | 5 | 1 | 0 | rates:5 escalation:2 expenses:1 hours:1 |
| twm_corpus\deep2_UK_GCloud14_Wipro_SFIA_ratecard_ORIGINAL.pdf | rate_card | 15 | 14 | 5 | 1 | 0 | rates:3 escalation:2 pricing_model:1 expenses:1 |
| twm_corpus\deep2_US_TX_DIR_ITSAC_NTE_rates_2024_DIR-CPO-5570_ORIGINAL.pdf | rate_card | 13 | 13 | 0 | 0 | 0 |  |
| twm_corpus\GSA_Army_PWS_Template_Structure_ORIGINAL.pdf | template | 15 | 14 | 6 | 1 | 0 | hours:3 personnel:2 nte:2 term:1 |
| twm_corpus\MI_DTMB_Deloitte_MiIntegrate_Contract_SOW_Rates_2013-2026_ORIGINAL.pdf | amendment | 378 | 338 | 99 | 17 | 0 | contract_no:62 amendment:43 value:38 payment:35 |
| twm_corpus\NY_OGS_HBITS_Process_TaskOrder_Mechanics_ORIGINAL.pdf | sow | 24 | 24 | 5 | 1 | 0 | invoice:3 expenses:3 term:2 hours:1 |
| twm_corpus\OK_OMES_Deloitte_Signed_Contract_RateCard_2018_ORIGINAL.pdf | amendment | 11 | 11 | 4 | 1 | 0 | amendment:2 rates:1 invoice:1 expenses:1 |
| twm_corpus\TX_DIR_ITSAC_579_NTE_Rate_Card_2024_ORIGINAL.pdf | unknown | 7 | 7 | 0 | 0 | 0 |  |
| twm_corpus\UK_GCloud14_Accenture_SFIA_ratecard_ORIGINAL.pdf | rate_card | 13 | 13 | 6 | 1 | 0 | rates:4 escalation:2 invoice:1 pricing_model:1 |
| twm_corpus\UK_GCloud14_Capventis_SFIA_ratecard_ORIGINAL.pdf | rate_card | 5 | 4 | 2 | 1 | 0 | rates:2 expenses:1 hours:1 |
| twm_corpus\UK_GCloud14_CGI_SFIA_ratecard_ORIGINAL.pdf | rate_card | 12 | 11 | 5 | 1 | 0 | rates:2 escalation:2 expenses:1 hours:1 |
| twm_corpus\UK_GCloud14_Deloitte_SFIA_ratecard_ORIGINAL.pdf | rate_card | 12 | 11 | 6 | 1 | 0 | rates:6 escalation:4 expenses:2 hours:2 |
| twm_corpus\UK_GCloud14_KPMG_SFIA_ratecard_ORIGINAL.pdf | rate_card | 3 | 2 | 1 | 1 | 0 | expenses:1 hours:1 rates:1 |
| twm_corpus\US_GSA_ITSchedule_CDOTechnologies_pricelist_legacy_ORIGINAL.PDF | unknown | 40 | 38 | 12 | 2 | 0 | discount:6 invoice:4 expenses:3 pricing_model:3 |
| twm_corpus\US_GSA_MAS_tCognition_pricelist_54151S_ORIGINAL.PDF | rate_card | 25 | 25 | 8 | 2 | 0 | discount:3 expenses:3 pricing_model:3 payment:2 |
| twm_corpus\US_TX_DIR_ITSAC_job_title_descriptions_2024_DIR-CPO-5498_ORIGINAL.pdf | template | 42 | 42 | 14 | 3 | 0 | nte:10 escalation:2 |
| twm_corpus\US_TX_DIR_ITSAC_NTE_rates_2020_DIR-CPO-4653_ORIGINAL.pdf | rate_card | 11 | 2 | 0 | 0 | 0 |  |
