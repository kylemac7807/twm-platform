# Corpus

- `manifests/v3_*/` — 388 classified URLs of original documents (EDGAR,
  government contracts, invoices/timesheets) + research notes.
- `gc15_ratecards/` — 13 G-Cloud 15 vendor rate cards (2026), extracted.
- `scripts/v3_download.py` — downloads the v3 originals to `downloads/`.
- The **Sept 1 package** (skills-framework fetcher, 48-original downloader,
  earlier rate-card/contract extractions) is delivered separately — unzip it
  here before the first run. Full guide: `../docs/corpus-catalog.md`.
- `downloads/` and `originals/` are gitignored: documents are fetched, not
  committed (size + third-party copyright — corpus stays reproducible from
  manifests).
