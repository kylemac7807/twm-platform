# G-Cloud 15 Rate Card Extraction — Manifest

*Files renamed `_SFIA_` to `_GC15_` on Oct 6, 2026: G-Cloud 15 cards are a standard role × level grid, not SFIA-based.*

**Extraction date:** 12 September 2026
**Framework:** UK G-Cloud 15 (RM1557.15), Crown Commercial Service / GCA Digital Marketplace (applytosupply.digitalmarketplace.service.gov.uk). Awards 6 August 2026; catalogue live mid-August 2026. Supplier pricing documents dated January 2026 (submission window).
**Licensing:** All sources are public UK government procurement documents (Crown copyright / Open Government Licence context); factual pricing data.

**Key structural finding:** G-Cloud 15 replaced free-form SFIA 1-7 PDF rate cards with a **standardized on-page rate card** per service: Government Digital and Data role taxonomy (9 categories, role x seniority level) with explicit **"UK Rate" and "Offshore Rate"** columns, GBP per day. This makes offshore arbitrage directly observable for the first time. Deloitte additionally publishes a grade-band PDF (Civil Service grade equivalence). Seniority labels (Trainee/Apprentice/Associate -> Standard -> Senior -> Lead -> Principal/Head) map approximately to SFIA levels 2-7.

## Files (12 vendors secured)

| File | Vendor | Source URL (service) | Vintage | Offshore tiers? |
|---|---|---|---|---|
| UK_GCloud15_Accenture_GC15_ratecard.md | Accenture (UK) Ltd | /g-cloud/services/509180438095337 | GC15, docs 2026-01-27 | YES — all categories, ~70-75% below UK (£150-£650) |
| UK_GCloud15_Atos_GC15_ratecard.md | Atos IT Services UK Ltd (Eviden) | /g-cloud/services/369277872364400 | GC15, docs 2026-01-28 | YES — most categories (£206-£1,034); cyber UK-only |
| UK_GCloud15_Capgemini_GC15_ratecard.md | Capgemini UK PLC | /g-cloud/services/161137653449191 | GC15, docs 2026-01-02/26 | YES — all categories incl. cyber (£110-£874) |
| UK_GCloud15_CGI_GC15_ratecard.md | CGI IT UK Ltd | /g-cloud/services/348660027537594 | GC15, docs 2026-01-16 | NO — offshore column empty (onshore-only) |
| UK_GCloud15_Deloitte_GC15_ratecard.md | Deloitte LLP | PDF 92485/955980530648874-pricing-document-2026-01-21 | GC15, Jan 2026 | YES — separate 9-band offshore card £355-£840 |
| UK_GCloud15_IBM_GC15_ratecard.md | IBM United Kingdom Ltd | /g-cloud/services/581735173557880 | GC15, docs 2026-01-06/13 | YES — uniform ladder £350-£1,065 |
| UK_GCloud15_Infosys_GC15_ratecard.md | Infosys Ltd | /g-cloud/services/148821255751177 | GC15, docs 2026-01-27/28 | YES — flat ~60-70% of UK (offshore priced high relative to UK) |
| UK_GCloud15_Kainos_GC15_ratecard.md | Kainos Software Ltd | /g-cloud/services/875574385541164 | GC15, docs 2026-01-20/26 | YES but shallow (~15-25% off; EU nearshore posture) |
| UK_GCloud15_KPMG_GC15_ratecard.md | KPMG LLP | /g-cloud/services/598757140562990 | GC15, docs 2026-01-29 | YES — steepest spread: £195-£780 vs UK £840-£2,808 (72-77% off) |
| UK_GCloud15_Kyndryl_GC15_ratecard.md | Kyndryl UK Ltd | /g-cloud/services/818008502756382 | GC15, docs 2026-01-13/29 | PARTIAL — IT ops + product/delivery only (£180-£609); rest UK-only |
| UK_GCloud15_PwC_GC15_ratecard.md | PricewaterhouseCoopers LLP | /g-cloud/services/177376838415896 | GC15, docs 2026-01-27/30 | YES — £960-£2,075 (offshore alone above many peers' UK rates) |
| UK_GCloud15_TCS_GC15_ratecard.md | Tata Consultancy Services Ltd | /g-cloud/services/815269997919354 | GC15, docs 2026-01-27/29 | YES — flat ~35% discount (offshore = 0.65 x UK) |

All service URLs relative to https://www.applytosupply.digitalmarketplace.service.gov.uk; asset PDFs under https://assets.applytosupply.digitalmarketplace.service.gov.uk/g-cloud-15/documents/<supplierId>/.

Supplier IDs (stable across GC14->GC15): Accenture 92191, Atos 92212, Capgemini 92224, CGI 92304, Deloitte 92485, IBM 92284, Infosys 93227, Kainos 92437, KPMG 93303, Kyndryl 718994, PwC 92454, TCS 92599, Cognizant 92235, HCL 93308, Wipro 721741 (GC14).

## Not found / leads

- **Cognizant** — IS on G-Cloud 15 (supplier page https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud-15/supplier/92235 confirmed), but no GC15 service page located: the catalogue's keyword search ignores URL query parameters (JS-only filtering), supplier profile pages carry no service links, ~30 catalogue listing pages scanned without a Cognizant hit, and search engines still index only their GC14 pages (e.g. /g-cloud/services/634917915449274, "£415 to £1,550 a unit a day"). LEAD: re-run a site search for "Cognizant" once Google indexes GC15 service pages, or browse the catalogue with a JS-capable browser; assets will sit under g-cloud-15/documents/92235/.
- **Wipro** — GC15 services exist (seen transiently in catalogue listings: "Wipro Data testing integrated with CICD", "Wipro Adobe Commerce Cloud", supplier WIPRO IT SERVICES UK SOCIETAS) but the listing order re-shuffles between fetches and the entries could not be re-located to capture URLs; search engines only return their GC14 twins (services/209968911261896, /712392082603449, both framework-marked G-Cloud 14, price band £120-£1,745/day). LEAD: same as Cognizant; GC14 supplier ID 721741.
- **HCL Technologies (HCLTech)** — ON G-Cloud 15 (supplier ID 93308): GC15 service found ("BigFix Unified Endpoint Management", /g-cloud/services/807713284260192) but it is licence-priced only (£1.07-£139.39 per unit subscription) with **no role rate card**; no consulting/support-type HCL GC15 service located in scans. LEAD: HCL's GC15 Lot-3 consulting services under g-cloud-15/documents/93308/ once indexed.
- **Tech Mahindra** — NOT found in the G-Cloud 15 supplier A-Z (checked prefix=T pages 1-2 covering the alphabetical range where it would sit); appears not to have been awarded GC15 (was present on GC13/GC14 as supplier 701890). LEAD: verify via GCA RM1557.15 award list; if truly absent, this is itself a data point (major offshore vendor exiting the framework).

## Observed movement vs G-Cloud 14 (May 2024)

- Broad onshore uplift of ~6-15% across refresh vendors (CGI £400-£1,550 -> £450-£1,650; KPMG ~8-20%; TCS/Infosys ~8-12%; Deloitte entry band £600 -> £765). Kainos moved hardest: ~20-35% up.
- The big structural change is offshore transparency: GC14 offshore tiers were rare/free-form; GC15 forces an Offshore Rate column, revealing spreads from ~15% (Kainos nearshore) to ~75% (Accenture, KPMG, Capgemini's £110-£150 offshore floors).
- Two pricing postures visible: deep-discount offshore (Accenture, KPMG, Capgemini, Version 1, Kyndryl ops: offshore 25-35% of UK) vs flat-ratio offshore (TCS, Infosys: offshore ~60-70% of UK, with the lowest UK rack rates instead).
- PwC is the rack-rate outlier (UK £2,120-£3,940; offshore £960-£2,075), consistent with its GC14 posture of high published rates discounted at call-off.
- CGI remains onshore-only in public pricing; Kyndryl publishes offshore only for ops/delivery roles.
