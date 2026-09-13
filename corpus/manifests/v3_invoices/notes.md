# V3 Hunt Notes — Public IT Vendor Invoices / Timesheets / SOWs

Date: 2026-09-13. Method: WebSearch + WebFetch only (per rules). Every "verified=yes" row in manifest.csv was fetched and content-checked, not just link-checked.

## Bottom line (blunt)

**Real, matched IT-vendor billing artifacts — an invoice tied to its timecards tied to its SOW — are close to nonexistent on the public web.** We found exactly one public source that produces true invoice↔timesheet pairs (Texas PUC docket 53815: staffing vendor CorTech billing Corix Utilities, with per-person weekly timesheets including clock-in/out times behind each invoice). Everything else public is one leg of the triangle at a time. The synthetic factory must carry essentially the entire load for the core reconciliation task: multi-week runs of contract → rate card → timecards → invoices with seeded discrepancies. Public documents are best used as **format ground truth** (what real invoices, timesheets, SOWs, and fee statements look like) and as **discrepancy-pattern ground truth** (what auditors actually find), not as training pairs.

## What exists publicly, vein by vein

### 1. CourtListener / RECAP — mostly inaccessible to automated hunting
- CourtListener **robots-blocks** its search pages AND all `/docket/` pages to fetch tools; only opinion pages and `storage.courtlistener.com` PDFs are fetchable.
- Google does NOT full-text index storage.courtlistener.com exhibit PDFs (they surface only when cited on social/news sites — invoice disputes never are).
- Net: free RECAP invoice/timesheet exhibits **exist** (staffing collection suits routinely attach unpaid invoices to complaints) but are **undiscoverable without an authenticated CourtListener API token or manual browsing**. Recommendation: a human session (or API key) on courtlistener.com RECAP search with `available_only=on`, query `description:(exhibit invoice)` + nature-of-suit 190, would likely yield the 10–25 exhibits this pass could not reach. Target case type confirmed real: CS Technology v. Horizon River (W.D.N.C. 3:18-cv-00273) — a pure IT billing dispute with SOW unit pricing and disputed labor hours.
- Justia (cases.justia.com) hosts free filing PDFs but almost exclusively orders/opinions, not exhibits.

### 2. Regulatory dockets (the surprise winner)
- State PUC/PSC e-filing systems ARE Google-indexed full text and freely fetchable. Rate cases and staff data-requests ("RFI responses") force utilities to file **actual vendor invoices and contractor timesheets**.
- Texas PUC Interchange docket 53815: invoice + per-person timesheet pairs (verified twice; more attachments in the same series likely — two fetches failed on a transient server error, retry).
- Kentucky PSC: 12+ pages of scanned invoices incl. an IT/SCADA integrator (HTI Inc.) with labor line items.
- This vein is minable at scale: search `interchange.puc.texas.gov` / `psc.ky.gov/pscecf` full text for "timesheet", "week ending", "invoice".

### 3. Bankruptcy fee applications (timecard data at scale)
- Claims-agent sites (Kroll/Stretto/Epiq) host **free, no-login dockets**. Interim fee applications and monthly fee statements contain per-professional hours, rates, and line-item task narratives — thousands of pages of real timecard-grade data (FTX alone: AlixPartners, EY, Paul Hastings, etc., verified).
- Caveat: professional-services (consulting/legal/tax) flavor, not IT staff augmentation; rates $236–$2,300/hr. Excellent for time-entry language, rounding behavior, rate-tier structure.

### 4. Government audits — findings, not artifacts
- Auditors describe exactly the discrepancies TWM detects (Fulton County/Covendis: billed hours ≠ T&A records, $30,875 overpayment; NYC CityTime: blank-timesheet fraud, billing after termination) but **do not reproduce the invoices/timesheets**. Use as discrepancy taxonomy and scenario seeds.

### 5. Municipal board packets — registers, not invoices
- Checked county/district packets across IL, VT, UT, CA, IN: virtually all publish **payment registers** (vendor, invoice #, amount, memo), not invoice images. Exception class: agenda attachments for contract approvals sometimes include vendor billing docs (Fort Bend County: five Tyler Technologies proforma invoices with full line items).

### 6. Contracts/SOWs — abundant
- SEC EDGAR is the deep well: real IT MSAs and SOWs with rate cards (Omnicell–Aditi: offshore monthly rate card $3,000–$4,500/role, SOW template with named consultants), milestone-billing SOWs (Klever–Qualzoom $210K/3 tranches), T&M frameworks (Yak–Convenxia cost+10%).
- State procurement files (Ohio 0A1148, Tennessee 32110-38726) give the MSP/VMS operating model and mandatory invoice field lists — the rules engine TWM validates against.

### 7. Templates — real but blank
- Federal: SF-1034/SF-1035 (the actual federal services invoice + T&M continuation sheet), DCAA 7641.90 with sample vouchers, WH-347 certified weekly payroll (names, daily hours, rates).
- NY OMH publishes a filled example invoice (50 hrs @ $30).
- **TBIPS (Canada): monthly-usage/quarterly report templates are NOT public** — distributed to standing-offer holders only (confirmed on PWGSC standing-offer page; contact-only access). Don't count on them.
- No US state was found publishing its IT staff-augmentation timesheet form publicly (they live inside VMS platforms like Fieldglass/VectorVMS/Beeline — invisible to the public web).

## What genuinely doesn't exist publicly
1. **IT staffing timecards** (the Fieldglass/Beeline/SAP-style weekly timesheet per contractor) — locked in VMS platforms; the only public sightings are the TX PUC pairs and fraud-case exhibits behind PACER.
2. **Matched triplets** (SOW ↔ invoice ↔ timecard for the same engagement) — zero found end-to-end; TX PUC pairs are invoice↔timesheet only, contract not attached.
3. **Enterprise IT services invoices** (Accenture/Infosys/TCS/Wipro-style monthly T&M invoices with role×rate×hours grids) — never public; even litigation (Hertz v. Accenture) files fee totals, not invoices; FOIA releases redact rates under b(4) (verified: IRS/Eastport Analytics release had all pricing redacted).
4. **Rate cards for named enterprise vendors** — redacted in FOIA, sealed in litigation; only aged EDGAR exhibits (2003–2010) leak them.

## 5 best finds
1. **TX PUC docket 53815, item 547** — https://interchange.puc.texas.gov/Documents/53815_547_1242069.PDF — real staffing invoice + two per-person timesheets (hours, rates, daily clock-in/out). The only true public invoice↔timecard reconciliation pair found; a template for the synthetic factory's target output.
2. **KY PSC case 2024-00127 scanned invoices** — https://psc.ky.gov/pscecf/2024-00127/bob.miller@straightlineky.com/09032024050331/1_Scanned_Invoices.pdf — genuine scanned invoice images incl. an IT/SCADA vendor with hardware+labor line items; ideal OCR/format ground truth.
3. **AlixPartners FTX 8th interim fee application** — https://restructuring.ra.kroll.com/FTX/ExternalCall-DownloadPDF?id1=MzI4OTA5OQ%3D%3D&id2=0&cid=0 — 5,807 hours across dozens of named professionals with individual rates; timecard-grade data at scale, and the whole FTX docket is a free library of similar filings.
4. **Omnicell–Aditi MSA (EDGAR)** — https://www.sec.gov/Archives/edgar/data/926326/000104746904006851/a2130043zex-10_27.htm — full IT outsourcing MSA + SOW template + offshore rate card + invoicing terms: the contract side of the reconciliation triangle with actual numbers.
5. **Fulton County Covendis audit** — https://www.fultoncountyga.gov/-/media/Departments/Office-of-the-County-Auditor/Audit-Reports-and-Management-Responses/2018-Audits/CovendisTechnologiesAuditReportFinal11718.pdf — a county auditor doing TWM's exact job by hand on an IT staffing MSP (billed hours vs. time & attendance) and quantifying the misses; the clearest public articulation of the discrepancy classes TWM must catch.

## Manifest stats
- 27 rows; 25 verified by fetch, 2 unverified (transient server errors, same docket series as verified items).
- By doc_type: invoice+timesheet 4 (2 verified), invoice 2, timesheet (fee-app time detail) 3, invoice register 3, audit-with-invoices 2, SOW-exhibit 7, template 6.
