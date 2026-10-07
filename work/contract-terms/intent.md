# Intent: contract terms

**Accepted by Kyle, October 6, 2026**, with the parallel-session plan (`Claude outputs/parallel-agent-plan.md`, stream A). Worked in the `contract-terms` worktree and branch.

## The problem

A vendor challenge is argued from the contract's words, not only its rate table: the discount schedule, the escalation clause, the invoicing terms, who the parties are and which master agreement governs. The pipeline reads rate tables well (M2: 53 verified rates from the Texas DIR Accenture exhibit, 430 from the Accenture G-Cloud page) and reads none of this. The code that would (`extract_sow`) has never been run against the real model.

Two smaller gaps sit beside it. The operator types the vendor and client on the command line although the document states them on page one. And the Texas exhibit prices eight contract years while the ledger keeps year 1 only.

## What we want

Teach the pipeline to read the commercial terms of a master agreement, statement of work or amendment with the same discipline as the rate tables: every term quoted from the page with its position, nothing guessed, abstentions explained in the model's words. Store the terms in the ledger beside the rates, each row traceable to a page. Derive the vendor and contract number from the document. Keep every contract year's rate as its own observation.

Prove it on the Texas DIR Accenture master agreement (081) and its Exhibit 2 financial provisions (084), then on the Michigan Deloitte MiIntegrate contract, which must go through the same code unchanged.

## Rules that bind this task

Precision first: a term the model is not sure of is flagged, never recorded. Rates and money as stated, with currency and unit; "contracted rate", never "cap". Nothing leaves the client's environment. Shared modules (`contracts.py`, `models.py`, `ledger.py`) are extended, never edited. The taxonomy and the normalizer belong to the main session.
