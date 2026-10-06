# Intent: M2, the thin thread

**Drafted** October 6, 2026 by Claude Code for Kyle to accept or change. Status: **draft, not yet accepted.**

## The problem

Every stage of the platform has now been designed, and one of them (normalization) is built. Nothing yet runs end to end. Until one real contract goes from a file on disk to rows in a ledger, with every number traceable back to its page, we have a design and a dictionary, not a system. We also cannot start the volume run, the evaluation harness or the demo, because all three need a pipeline to run through.

## What we want

One real contract family, the Texas DIR Accenture agreement (DIR-STS-TSS-699: master agreement, statement of work, pricing exhibit and their attachments), pushed through intake, document reading, extraction, normalization and the ledger, on Kyle's machine, with:

- every stage behind the interface the design record describes, so Azure services can replace local ones later without touching the pipeline;
- every extracted number verified against its page, uncertain fields left blank and flagged, titles resolved by rules then the model step then flagged, place names flagged for the analyst;
- ledger rows that carry rate as stated, currency, unit, effective date, source position, confidence, scan quality and raw evidence;
- a plain report Kyle can read: what the documents were, how many rates, how many flags and why, and one row traced back to its page.

## What success looks like

Kyle runs one command (or asks Claude to) and sees the Accenture pricing exhibit's roughly 74 labour categories and 8 years of rates as ledger rows, with a handful of flags he can understand, and can click or point from any row to the exact cell in the PDF. A second document family, the Accenture G-Cloud 15 card, goes through the same pipeline with no code changes, which proves it is a skeleton of the system and not a one-off script.

## Out of scope

Invoices and timesheets (group 2); the workbench screens (a plain text or spreadsheet view is enough); Azure; benchmarking across vendors (the ledger exists but the comparison comes after the volume run); any synthetic data.

## What it needs from Kyle

An API credential in a `.env` file (action item C8), and acceptance of this intent and the plan that follows it.
