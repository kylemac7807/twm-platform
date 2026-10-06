---
name: twm-new-document-source
description: Adding a new source of documents to the library: a download, a vendor card, a government contract set, a file Kyle collected. Use whenever files enter corpus/.
---
# Add a new document source

1. **Sniff content**, never trust the extension or the downloader's "ok" count (`%PDF`, `PK`, `<html`). Texas DIR's CDN served HTML viewer pages as `.pdf`; see `corpus/scripts/widen_recover.py`.
2. Record **provenance**: URL, issuer, date retrieved, vintage or effective date, licence or terms, and whether rates are visible. A README beside the files, tracked in git; the third-party files themselves are gitignored.
3. Classify its **use**: training structure, benchmark seed (only if true, sourced, recent), taxonomy seed, synthetic template. Training data and benchmark data are different assets.
4. Update `docs/corpus-sources-and-demo-set.md` (counts and the set description) and, if it changes what is missing, `docs/corpus-missing-originals.md`.
5. SFIA material stays out until the licence decision. Nothing from a client ever enters the shared library.
