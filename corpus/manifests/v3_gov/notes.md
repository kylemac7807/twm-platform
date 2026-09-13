# V3 Government Contract Corpus — Harvest Notes (2026-09-13)

138 rows in `manifest.csv`. Method: WebSearch (site:/filetype: queries) to discover candidate URLs, WebFetch to verify and to extract attachment links from live notice/contract pages. No curl/wget used.

**Verification semantics.** `verified=yes` (19 rows) means WebFetch actually read the document. Many `verified=no` rows are still high-confidence: ~75 of them were extracted verbatim from an official page fetched live this session (DWP Synergy notice, dir.texas.gov contract pages, NY OGS bid-documents page, CanadaBuys tender-notice page) — the notes column says which. The remainder are search-engine-indexed official URLs not re-fetched.

## Per-source methods and blockers

### 1. UK Contracts Finder (48 rows)
- Direct search-results URLs on contractsfinder.service.gov.uk are blocked to WebFetch (provenance gate), but individual notice pages and `/Notice/Attachment/{guid}` PDFs fetch fine once discovered via web search.
- Best query patterns: `site:contractsfinder.service.gov.uk "redacted contract" IT`, `... "Notice/Attachment" "order form" OR "statement of work"`, `... "call-off" software awarded`.
- UK transparency rules mean large awards attach the full signed (redacted) contract. The DWP "Synergy" award alone published ~48 schedule PDFs (we manifest 24 of the best; the notice `205ef6e5-7363-42e0-a1f9-805c00ce1f8b` has the rest, including B-supplier duplicates).
- Caveat: pricing/day-rate schedules are usually redacted under FOIA s.43 (e.g., Synergy Schedule 15 Charges, Amido DOS3 day rates). Structure/SOW text survives intact.
- Small awards (<£100k) usually publish no documents — filter for value or for the word "redacted" in the notice.
- Depth remaining: effectively unbounded — thousands of award notices carry attached contracts; the archive on data.gov.uk (Contracts Finder archive) was not mined.

### 2. US states
- **Michigan (13)**: `https://www.michigan.gov/dtmb/-/media/Project/Websites/dtmb/Procurement/Contracts/...` pattern confirmed live; PDFs fetch cleanly. Files are cumulative: master contract + all change notices + SOWs in one PDF, frequently with unredacted hourly rates. Contract List itself is a Power BI dashboard (not scrapeable via WebFetch) — use `site:michigan.gov "Procurement/Contracts" filetype:pdf <vendor>` searches instead.
- **Texas DIR (26)**: dir.texas.gov contract pages fetch fine and enumerate full doc sets (Contract, Appendix A T&Cs, Appendix C Pricing Index, Appendix D service agreement template, originating RFO). The txdir.widen.net CDN blocked WebFetch (provenance/403) — all widen URLs recorded unverified; they download normally in a browser. Vendor index pages (e.g., /contracts/vendors/accenture-llp) are an efficient crawl entry point; Deloitte, IBM, CGI, TCS, Infosys vendor pages not yet walked.
- **Florida DMS (10)**: STC-ITSA per-vendor executed contracts at `dms.myflorida.com/content/download/...`. Whole domain is robots-disallowed for WebFetch, so all unverified — but URLs are Google-indexed official links. Both the 2021 and 2023 ITSA generations found; dozens more vendors exist under the same search (`site:dms.myflorida.com "STC-ITSA" filetype:pdf`).
- **Washington (1)**: DES contract search is an app (apps.des.wa.gov/DESContracts/) — not WebFetch-minable. But agency sites publish signed ITPS work orders, e.g., dshs.wa.gov `/sites/default/files/contracts/...` (verified one with $125/hr rate). Depth here via `site:dshs.wa.gov contracts filetype:pdf` style queries.
- **New York OGS (11)**: two surfaces — `online.ogs.ny.gov/purchase/snt/awardnotes/*.pdf` (award/base-contract PDFs, verified) and `ogs.ny.gov/procurement/biddocuments/23311bid` (HBITS next-gen full solicitation package incl. rate-bid form and task-order forms; friendly URLs redirect to PDFs).
- **Massachusetts (2)**: COMMBUYS attachments not reachable via WebFetch/search; only contract user guides on mass.gov captured. Weakest state.
- **Oklahoma (1)**: OMES contract pages fetch, but underlying docs sit behind an ok.gov PHP solicitation app; thin.
- **Georgia DOAS**: searched; only process docs surfaced, no signed contract PDFs — dropped.

### 3. CanadaBuys (23 rows)
- Two document surfaces: `canadabuys.canada.ca/sites/default/files/webform/tender_notice/{id}/{file}.pdf` (newer webform uploads) and `canadabuys.canada.ca/documents/pub/att/{date}/{hash}/{file}` (legacy buyandsell ABES attachments).
- robots.txt blocking is inconsistent: two webform PDFs fetched fine (verified — SCC TBIPS 2025-03 and DND W6369-23-P5PE, both containing Annex A SOW + Task Authorization form + Annex B Basis of Payment); later attempts on both surfaces hit ROBOTS_DISALLOWED. URLs themselves are stable and browser-downloadable.
- Tender-notice HTML pages under /en/tender-opportunities/tender-notice/ mostly fetch fine and enumerate attachments with language tags — pw-zm-622-37474 yielded a full bilingual EN/FR RFP set (12 PDFs + a zip of SOW/TA/basis-of-payment annexes).
- Many TBIPS/TSPS notices publish NO attachments ("RFP e-mailed to SA holders") — filter for notices with attachment tables.
- French: 8 French-language + 4 bilingual rows captured; every legacy ABES notice carries parallel F-prefixed files, so French volume scales linearly with EN harvest.

### 4. US federal (3 rows)
- FOIA reading rooms (GSA/DHS/VA) surfaced case logs, not contract PDFs. SAM.gov attachment links are not search-indexed in a resolvable form.
- What works: GSA publishes conformed GWAC master contracts directly on gsa.gov — 8(a) STARS III and Alliant 2 verified, both with labor-category/max-rate frameworks. Alliant 3 / Polaris / NITAAC CIO-SP equivalents likely follow the same pattern (not yet mined).

## Richest 5 finds
1. **DWP "Synergy" ERP contract set (UK)** — 48 separately downloadable schedules of a signed £710.9M IBM/Oracle systems-integration contract (services description, requirements matrix, SLAs, charges, exit, benchmarking): a complete anatomy of a mega IT-services deal in machine-readable PDFs.
2. **Michigan DTMB cumulative contract PDFs** — single PDFs containing master contract + every change notice + SOWs, with unredacted hourly rates (e.g., Knowledge Services $800M IT staff-aug MSP with full rate card $24–$114/hr; LexisNexis VERA at $200/hr; Datix CONTRAXX with on/off-site rate split).
3. **Texas DIR-STS-TSS-699 (Accenture)** — MSA + Exhibit 1 SOW + Exhibit 2 financial provisions + Att 2.1 pricing/volumes + SLA definitions: a modern multi-supplier app-dev/maintenance/staff-aug structure, all public.
4. **DND W6369-23-P5PE + SCC TBIPS 2025-03 (Canada)** — verified TBIPS packages containing the exact target trio: Annex A Statement of Work, Appendix B Task Authorization form, Annex B Basis of Payment rate tables; plus a full bilingual EN/FR RFP+amendment set (A0416-183262) for French training data.
5. **GSA Alliant 2 + STARS III conformed contracts (US federal)** — master IDIQ contracts with standardized IT labor-category taxonomies and fully-burdened max-rate mechanics (BLS ECI-indexed), ideal reference schemas for rate-card normalization.

## Remaining depth
- UK: essentially unlimited (every large IT award publishes a redacted signed contract; ~10 more per search query).
- Texas DIR: ~5–7 docs per contract × hundreds of contracts; walk vendor index pages next (IBM, CGI, TCS, Infosys pages exist).
- Florida ITSA: dozens more vendor contracts in the same index.
- CanadaBuys: legacy ABES notices each carry bilingual attachment sets; the Open Government tender-notice dataset (open.canada.ca) could enumerate attachment URLs at scale without robots friction.
- NY OGS: per-vendor HBITS award pages and Project-Based ITCS attachments not yet enumerated.
- Weak/blocked: COMMBUYS (app-gated), WA DES contract search (app), Georgia DOAS (no docs surfaced), SAM.gov (login-ish), agency FOIA reading rooms (logs only).
