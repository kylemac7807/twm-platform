# TWM action items — the one running list

**Last updated:** September 20, 2026, by Claude Code with Kyle. This is the only action list. It merges Cowork's list of September 20 (pasted in by Kyle) with the items tracked in Claude Code sessions. Whoever finishes or adds an item edits it here. Decisions themselves are recorded in `requirements-and-rationale.md`; this file only tracks who does what.

Status words: **Done**, **Open**, **Waiting** (on someone or something named), **Parked**.

## A. Decisions for Kyle

| # | Item | Status |
|---|---|---|
| A1 | Accept the two added job families (Technology Leadership; Change, Training and Communications) | **Done** Sept 19. Accepted. |
| A2 | Accept Packaged Applications as five generic roles plus a platform tag | **Done** Sept 19. Accepted. |
| A3 | No default seniority: a title with no evidence stays unbanded | **Done** Sept 19. Decided and built. |
| A4 | SFIA: deep-dive before final commitment. The SFIA column stays empty until then | **Open.** Waiting on Cowork's decision memo (D1) and Kyle's time. |
| A5 | Confirm or adjust the M2 "thin thread" scope. Kyle wants to discuss it further; the definition in CLAUDE.md is provisional | **Done** Oct 6. Settled in the walkthrough: first document is the Texas DIR Accenture set; scoring is field-level against a hand-verified answer sheet; audience is an Early Adopter CIO; build order one contract, volume run, evaluation, demo. |
| A6 | Review the five recommended demo documents and confirm or swap them (`corpus-sources-and-demo-set.md` section 2) | **Open.** Overlaps Cowork's C5. |

## B. Claude Code — work in the project folder

| # | Item | Status |
|---|---|---|
| B1 | Held-out test: run the normalizer on sources it was NOT built from (G-Cloud 14 cards, Job Bank titles, the Accenture titles in the Texas pricing exhibit, plus the Cognizant and Deloitte GSA cards Kyle collected). Report results; gate M2 on the number | **Open.** Next build task. Waiting on Kyle's go. |
| B2 | Make "onshore" depend on the client | **Done** Sept 19, and taken further: the platform never classifies a place name. An analyst categorizes it once, then it is a lookup (requirements section 3.5). |
| B3 | Build A3 | **Done** Sept 19. |
| B4 | Reconcile the years-of-experience band table with NY HBITS and TBIPS, or document it as the fallback it is | **Open.** Small. |
| B5 | Validate the consulting-pyramid seniority mapping against the Oklahoma Deloitte contract and Deloitte's G-Cloud grade card | **Open.** Small. |
| B6 | Label the 126 authored title aliases separately from the 349 observed titles | **Open.** Small. The split is already stated in the requirements doc. |
| B7 | Sync the 98 percent versus 99.3 percent mismatch | **Done** Sept 19. After A3 the report reads 96.7 percent to role and band, 99.3 percent to a role. |
| B8 | Add `.gitattributes` and fix line endings | **Done** Sept 20. Cowork's report was correct: two manifest files differed on disk. |
| B9 | Put section 3.5 in the right order and adopt Cowork's copy of the requirements doc | **Done** Sept 19. Merged into v0.4; Cowork's copy retired. The project folder's file is now the only real copy. |
| B10 | Re-run the downloader for the rate-limited UK Contracts Finder files | **Done** Sept 20. All 8 fetched and verified as real PDFs. 368 of 388 now on disk. |
| B11 | Content-sniffing rule (check what a file really is, never trust its extension) | **Partly done.** The rule is in CLAUDE.md and was used to catch 26 fake PDFs. Building it into the intake code happens with M2. |
| B12 | Two gaps between what the business documents promise and what the specs cover. **Kyle set the priority order Sept 20** (requirements section 1.1): first the core SOW analysis (extraction, benchmarking, comparisons); second invoices to timecards to SOWs; third, and least important, the HR-system link. (a) *HR link:* the Technical Approach's "Matchmaker" step needs an HR or vendor-management-system export and a way to recognize the same person across SOW, timesheet, invoice and HR data. Left undesigned until the first two are in place. (b) *Savings tranches:* the promised dashboard totals savings as Contractual (enforce the contract's own caps), Operational (remove one vendor's inconsistent prices for the same role) and Market Alignment (move toward the benchmark mid-point). Nothing yet says how each dollar is assigned to a tranche without double counting; a stacking rule is proposed with a worked example in requirements section 6, item 7 | **Done** Oct 6. Priority order decided Sept 20; stacking rule and its edge cases decided Oct 6; HR link parked by design. |
| B13 | Flag decisions for Kyle to carry to Cowork's canonical copy | **No longer needed.** There is no second copy. |
| B14 | Carry the plain-language descriptions of each document set into the requirements doc, using the wording Kyle approved (`corpus-sources-and-demo-set.md` section 1a) | **Open.** Small. |
| B15 | Extract the rate tables from the Cognizant and Deloitte GSA documents Kyle collected, into the same form as the other rate cards | **Open.** Feeds B1. |

## C. Kyle

| # | Item | Status |
|---|---|---|
| C1 | Download the script-blocked originals by hand. Priority: Michigan Deloitte MiIntegrate (needed for M2), then Michigan Knowledge Services rate card. Exact filenames in `corpus-missing-originals.md`, priority order in `corpus-sources-and-demo-set.md` section 3 | **Open.** 23 documents remain: 13 Michigan DTMB, 7 singles, 3 from the September 1 package. Cowork's alternate links for four of them (`Claude outputs/corpus-retrieval-status-2026-09-13.md`) were tried by script on Sept 20 and all returned not-found, so use them in a browser: they are starting pages to click through from, not direct downloads. |
| C2 | Unpack the ESCO zip into the library | **Done** Sept 20 by Claude Code. Note: it is the **English** edition only. The spec wants French titles for Canadian bilingual documents, so the French edition still needs downloading from the ESCO site (same email registration). |
| C3 | Register at sfia-online.org for the internal-use SFIA 9 files and verify the Partner Licence terms from the primary source | **Open.** |
| C4 | Create the TWM Azure tenant and development subscription, Canada Central; Kyle owns admin and billing | **Open.** Kyle: within about a week of Oct 6. Deployment work waits for M2 regardless. |
| C5 | Read a sample of real documents: Michigan Deloitte, a bilingual TBIPS package, a G-Cloud 15 card, an EDGAR MSA, the Texas invoice and timesheet pair | **Open.** Combine with A6: the five demo documents cover four of these. |
| C6 | Register as a supplier on Canada's CPSS portal when convenient; read the terms of use before reusing any rate data | **Open.** Low priority. |
| C7 | Foundry data-handling terms in writing | **Parked.** |
| C8 | Create a `.env` file with an Anthropic API key in the project folder, needed before M2's extraction step. Claude cannot enter credentials | **Open.** Needed for M2. |
| C9 | Optional: a private GitHub repository as an offsite backup of the project folder | **Open.** Claude will walk Kyle through it. |
| C10 | Validate the technical approach with an outside party (Kyle's January list named RAVL or similar) once M2 runs end to end, so there is something concrete to review | **Open.** After M2. |

## D. Cowork

| # | Item | Status |
|---|---|---|
| D1 | SFIA decision memo, with licence terms verified from the primary source | **Open.** |
| D2 | ATIP: build the list of 15 to 20 TBIPS contracts from open.canada.ca proactive disclosure; Kyle files the requests | **Open.** Draft request text is in Cowork's Sept 18 handoff (see F2). |
| D3 | Draft revised Technical Approach and Pitch Deck (own-versus-rent and k-anonymity wording; remove GPT-4o; fix the six documented inconsistencies) | **Open.** |
| D4 | Update the Design Decisions section 5 after the SFIA decision | **Waiting** on A4. |
| D5 | Synthetic factory (M4) design spec when M3 nears | **Open**, later. |

## E. Discussions Kyle has queued (agenda set Sept 20, 2026, in this order)

| # | Item | Status |
|---|---|---|
| E1 | **Architecture: walk through the components one by one** (nine components plus four supporting ones), reorganized around Kyle's priority order: core SOW analysis, then invoices to timecards to SOWs, then the HR link. Findings and reporting, and the review workbench, have no spec yet. Bring in A5 (M2 scope), the savings-tranche edge cases, and the demo. Cowork's handoff lists the questions Kyle wanted settled for M2: which document goes first, what the field-level scoring should show him, and what must be demonstrable to Early Adopters. Reference: handoff sections 3 and 4 | **Done** Oct 5 to 6. Every component in groups 1 and 2 plus both cross-cutting ones decided; recorded in `architecture-components.md` and the decision log. |
| E2 | **Azure set-up:** how all of this is stood up on TWM's own Azure environment first, then in a client's. Starting point: handoff sections 1.1 to 1.4 (service map, deployment automation as a product feature, TWM's subscription first, portable pieces first). Feeds C4 | **Done** Oct 6. Decisions recorded in `architecture-components.md`; subscription creation (C4) follows within about a week. |
| E3 | **An AI-native way of building software.** Kyle is reading Anthropic's "The AI-native SDLC playbook" (claude.com/blog/the-ai-native-sdlc-playbook, Aug 21, 2026) and wants TWM's build practice consistent with it: intent, spec and plan documents committed at each stage; a short project instruction file; skills and hooks; a self-checking test loop; evaluations that run automatically; AI review with a human approval gate; monitoring that feeds new work back in. Compare what we already do with what it recommends, and decide what to adopt at TWM's size | **Done** Oct 6. `docs/how-we-build.md`, pre-commit guardrails installed and tested, 13 skills in `.claude/skills/`. |
| E4 | Review all outstanding action items, including Kyle's January 2026 Word to-do list | **Done** Oct 6. Decided: business work (Early Adopter pitch, target clients, consulting team, legal structure, funding, contacts) stays in a separate track kept by Kyle and Cowork; only build-facing items appear here (C10 added). Claude runs the small batch B1, B15, B4, B5, B6, B14 before M2; M2 then starts with an intent and a plan for Kyle to read, once C8 exists. |

## F. Keeping both sides in sync

| # | Item | Status |
|---|---|---|
| F1 | One real copy of every document, in this project folder; Cowork leaves its work in `Claude outputs/` | **Done** Sept 19. |
| F2 | Get Cowork's two missing documents into the shared folder | **Done** Sept 20. Both are in `Claude outputs/` and saved in the version history. Their unrecorded decisions were added to the decision log the same day. |
| F3 | Confirm Cowork's instructions carry the single-source-of-truth rule | **Done** Sept 20. Cowork read them back: this folder holds the only real copy, `docs/action-items.md` is the single action list, outputs go to `Claude outputs/`, and Cowork does not edit code folders. It also deleted its own project-knowledge copies. |
