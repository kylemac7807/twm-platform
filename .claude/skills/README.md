# TWM skills

Written procedures that must be applied the same way in every session (decided with Kyle, Oct 6, 2026; see `docs/how-we-build.md`). Each lives in `<name>/SKILL.md`. When a policy changes, the skill changes with it and Kyle signs off.

| Skill | What it covers |
|---|---|
| `twm-precision-first` | Abstain, flag, never guess. Apply whenever any TWM component or script must decide something it is not certain of: a field, a title, a location, a link, a match, a number.. |
| `twm-flag-then-codify` | How TWM turns an analyst's judgment into a reusable rule. |
| `twm-rates-and-money` | Rules for any code, table or document that holds a rate, price or savings figure. |
| `twm-data-boundary` | What may leave a client's environment and what never may. |
| `twm-run-a-document` | Running one document (contract, rate card, invoice, timesheet) through the TWM pipeline and reading the result. |
| `twm-change-the-taxonomy` | Adding or changing a canonical role, family, title mapping, band crosswalk row, tech tag or location rule in taxonomy/*.csv. |
| `twm-write-a-finding` | Writing or generating a savings or leakage finding for a consultant or a CIO. |
| `twm-gold-answer-sheet` | Building a hand-verified answer sheet (gold record) for one document in the evaluation sample. |
| `twm-new-document-source` | Adding a new source of documents to the library: a download, a vendor card, a government contract set, a file Kyle collected. |
| `twm-session-start` | What to do at the start of every TWM session before any work. |
| `twm-build-task` | The artifact chain for any build task: intent, spec, plan, build, review, done. |
| `twm-write-for-kyle` | How to write anything Kyle or a client CIO will read: chat replies, documents, demo text, findings. |
| `twm-cowork-handoff` | Working with Cowork, the other Claude surface Kyle uses, which shares the project folder. |

## Later

- `twm-deploy-azure`: Installing or tearing down a TWM environment in an Azure subscription with the Bicep scripts. To be written when TWM's subscription exists (action item C4).
- `twm-synthetic-documents`: Generating synthetic contract, timesheet and invoice triplets with planted discrepancies for reconciliation training. To be written with M4.
