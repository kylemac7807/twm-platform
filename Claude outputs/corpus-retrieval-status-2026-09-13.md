# TWM Corpus — Retrieval Status & the 31 Missing Originals

**Date:** September 13, 2026 · Companion to the Corpus Catalog and to Claude Code's `corpus-missing-originals.md`.

## Where the corpus stands

Claude Code ran all download scripts on Kyle's machine. **419 of 450 originals fetched** (v3: 360/388; Sept 1 package: 45/48; frameworks: 14/14). SFIA 9 and ESCO remain manual (registration/email); the ESCO zip is already in Kyle's Downloads. M1 (Role Framework v0) is proceeding without the missing files — correct call: they add no new source type, and M1 works from title vocabulary, not document volume. They matter at **M2** (the Deloitte MiIntegrate contract is the named second thin-thread document) and **M3** (contract volume for gold sets).

## Why Cowork can't just fetch the 31

Tested empirically: this cloud environment's web tool returns **parsed text, not binary PDFs** — the same wall that created the download-script approach. Delivering text extractions renamed as `*_ORIGINAL.pdf` would corrupt the ingestion training, whose whole purpose is real, messy PDFs. So the 31 are retrieved by a **real browser on Kyle's machine**, not from here.

## The 31, by required action

**A. Contracts Finder rate-limited (8 files, HTTP 429) — no action needed.** Not blocked, just throttled. Claude Code's retry after ~24h collects them unattended. These are the `041–048` UK template/SOW/framework files.

**B. Browser-only (≈20 files, HTTP 403) — need Kyle's Chrome.** The 15 Michigan DTMB contracts (incl. the priority **Deloitte MiIntegrate `180000000078`** and the two Sept 1 Michigan files), plus singles: SEC Virtusa exhibit, mass.gov ITS75, DCAA voucher manual, CourtListener opinion. All open normally in a browser; they refuse scripted clients only. Fastest path: Kyle opens each link and saves it, or Cowork drives his Chrome to batch them. Claude Code then renames to the exact destination filenames in `corpus-missing-originals.md` (both downloaders skip files already present, so re-running confirms).

**C. Dead-URL 404s — RE-FOUND, all three recoverable:**

| File | Status | How to get it |
|---|---|---|
| GSA Alliant 2 Ordering Guide (2025) | Live at a variant URL | `https://www.gsa.gov/system/files?file=Alliant%202%20Ordering%20Guide%20(2025).pdf` (note `?file=` form), or the GSA Alliant 2 page → "Ordering Guide" |
| GSA Constellation West price list (47QTCA25D007E) | Still indexed live | Original URL resolves again on retry; otherwise GSA eLibrary → contract 47QTCA25D007E → "View Catalog/Pricing" |
| NY OMH "proper NYS invoice" example | Landing page live | From `https://omh.ny.gov/omhweb/vendorinfo` → "example of a proper NYS invoice" (the direct `.pdf` path 404s intermittently; the vendorinfo page carries the link) |
| CanadaBuys TBIPS A0416-183262 FR amendment | Notice page live | From the tender notice `https://canadabuys.canada.ca/en/tender-opportunities/tender-notice/pw-zm-622-37474` → Documents/attachments (the direct file path 404s; the notice page is the entry) |

## Two ingest findings from Claude Code — fold into the pipeline, not just the catalog

1. The NY HBITS averages file saves with an `.html` extension but **is a PDF**.
2. Contracts Finder attachments save with **no extension but are PDFs**.

**Consequence:** the ingest stage must **sniff content (magic bytes), never trust the extension.** This belongs in `src/twm/pipeline/ingest.py` as a hard rule, and is exactly the kind of real-world messiness the engine must handle in the wild — a small validation of the whole approach.

## Recommended division of labor

- **Claude Code:** retry the 8 Contracts Finder 429s tomorrow; rename browser-fetched files per the destination table; add the content-sniffing rule to ingest. Continue M1 now regardless.
- **Kyle:** a 2–3 minute browser pass on the ~20 Section-B links (or ask Cowork to drive Chrome), plus the 3 re-found 404s above. None are on the M1 critical path; the Deloitte MiIntegrate is the only one needed before M2.
- **Cowork (here):** re-found the dead URLs (done); can drive Kyle's Chrome to batch the browser-only files if he prefers not to click.
