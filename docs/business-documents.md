# TWM business documents — which ones are current

**Confirmed by Kyle on September 19, 2026.** The business documents live outside this project, in
`C:\Users\kylem\OneDrive - Straight Line Advisory\Desktop\Technology Workforce Management` (126 files, most of them superseded drafts). They stay there because Kyle still edits them in Word and PowerPoint. This index says which ones are authoritative. **Read only the files listed here; ignore everything else in that folder unless Kyle points to it.**

The subfolder `Claude Grounding` is Kyle's own curated set and holds the first four.

## Current set

| Document | File | Dated | What it is for |
|---|---|---|---|
| **Business Plan v1.5** | `Claude Grounding\Business Plan - January 27 2026 v1.5.docx` | Jan 27, 2026 | The business: market, offering, consortium model, economics. Replaces the October 2025 Business Plan slide deck (v1.4), which is no longer in use. |
| **Pitch Deck investor narrative v1.1** | `Claude Grounding\Pitch Deck - Investors Narrative - March 1 2026 v1.1.docx` | Mar 1, 2026 | The investor story. |
| **Consortium Approach v1.7** | `Claude Grounding\TWM - Consortium Approach - January 20 2026 - v1.7.pptx` (and `.pdf`) | Jan 20, 2026 | The Early Adopter consortium proposition. |
| **Summary Technical Approach v1.2** | `Claude Grounding\TWM - Summary Technical Approach - January 29 2026 - v1.2.pptx` (and `.pdf`); Word version `Technical Approach\Technical Approach - TWM - January 29 2026 v1.2.docx` | Jan 29, 2026 | The technical approach as presented to clients. |
| Early Adopter Presentation | `Early Adopter Presentation - November 10th - v2.docx` | Nov 2025 | Talking points for early adopter meetings. |
| Business Model | `TWM - Business Model - October 2nd.xlsx` | Oct 2025 | Financial model spreadsheet. |
| Competitive analysis | `Competitive Analysis\Detailed Competitive Analysis - October 3rd - 2025.docx`, `Competitive Analysis\Competitive Analysis - October 6th - 2025.docx`, `Competitive Analysis\everest-group-vms-peak-matrix-assessment-2025.pdf` | Oct 2025 | Competitors and the VMS market. |
| Things to do | `TWM Things to do - January 29 2026.docx` | Jan 2026 | Kyle's action list at that date. |

## Known to be partly overtaken

The **Technical Approach v1.2** and the **Pitch Deck v1.1** are the current versions but contain language that later decisions replaced. `docs/architecture-decisions.md` sections 7 to 9 record it: "anonymized neural weights" and "differential-privacy weight smudging" are superseded by the own-versus-rent split and k-anonymity on the ledger, and GPT-4o references give way to model-agnostic wording. Where those documents and the architecture decisions disagree, **the architecture decisions win**. Revising both documents is a queued item on the Cowork side.

## Superseded — do not use

- Everything in `Business Plan - Previous Version\` (28 files, August to October 2025).
- Business Plan v1.41 and the v1.4 slide deck, including the password-protected copies.
- Consortium Approach versions 1.0 through 1.6.
- Notes, meeting notes, timelines and to-do lists from June to October 2025.
- Any file whose name starts with "Delete" or contains "for editing".

## Other contents

- `NDA\` — signed and template non-disclosure agreements (RAVL, Sympera, Vedra). Kyle has no objection to these being read; they are not needed for the build.
- `Model Training\` — documents Cowork saved there in January 2026. Copied into this project on September 19, 2026 at `corpus/collected_by_kyle_2026-01/` (see the README there). Kyle may delete the source folder once he has checked the copy.
- `Technical Approach\AI and LLM capabilities - October 6th.docx` and `Pros and cons of short-term decision on consulting vs AI solution.docx` — background thinking from before the architecture decisions; useful history, not authoritative.

## Keeping this index honest

When Kyle issues a new version of any document above, update the row and move the old one to the superseded list. One current version per document, always.
