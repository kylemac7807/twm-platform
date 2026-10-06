---
name: twm-run-a-document
description: Running one document (contract, rate card, invoice, timesheet) through the TWM pipeline and reading the result. Use whenever a document is to be processed, for M2, the volume run, the demo or a client engagement.
---
# Run a document through the pipeline

1. **Intake.** Register the file. Sniff its real type from content (`%PDF`, `PK`, HTML), never the extension. Fingerprint it; if already registered, say so and stop. Classify (MSA, SOW, amendment, rate card, invoice, timesheet, unknown). Link to its family only on strong evidence (a contract number on the page); otherwise suggest and flag.
2. **Read.** Through the reading interface (local reader for native PDFs; Azure Document Intelligence when available). Keep page and position for every element. Record the quality grade.
3. **Extract.** Per section, into the typed record for its classification. Abstain on uncertain fields. Verify every number against the page. Retry a malformed answer at most twice, then flag.
4. **Normalize.** Rules first (`twm.pipeline.normalize.resolve`), mapping table lookup, then similarity plus model confirmation above the confidence floor, then flag. Location: explicit words only; place names go to the queue.
5. **Ledger.** Append rows; never overwrite. Supersede old rows on a re-run.
6. **Report** to Kyle in plain language: what the document was, how many rows, how many flags and why, confidence spread, and anything surprising. One example row with its source position.

Always run with `.venv/Scripts/python.exe`. Never commit the document itself (third-party originals stay out of version history).
