# Review: terms in the workbench

Written November 22, 2026, by Claude Code, after the build. The plan is `plan.md`; Kyle approved it and said to do the steps at once.

## What was asked, and what is there now

| Kyle asked | What the screens do |
|---|---|
| A clearer view of what the contract or rate table says | A rate is shown as its row inside its table, with the column headings and the rows either side, the rate cell marked. A clause is shown in full, with a close-up of the page |
| Where does each job title appear in the contract set | Under the row: every document that prices or names the title, with pages, number of rates, contract years, locations and the range |
| The contract set should look like the library table | Opening a contract set lands on an Overview: one row per kind of document (contracts, amendments, SOWs, rate cards, other), how many the engine has read, rates, facts and conditions, questions; invoices and timesheets listed apart as a later stage. The list of contract sets has the same columns |
| Click through to the actual page | "See the whole page" opens the page with the row or clause boxed. "Open the original document at page N" opens the file itself. Both work today on this machine; Azure is not needed for it |
| Terms (the plan) | A Terms tab per contract set: the disclosure check first, a one-line draft summary, the facts, the conditions in the seven groups. Three new question types in Review: Conditions, Vendor names, Disclosure |

## Proof

| Check | Result |
|---|---|
| Tests | 178 pass (166 before). 10 new ones cover terms; each write path is tested through the service |
| A named condition applies to its scope and nowhere else | Tested: this contract set only, then vendor-wide (the same clause in the vendor's other contract is answered by the one answer) |
| A proposed condition changes no inventory file | Tested by fingerprinting `specs/rate-conditions.md` and `conditions.py` before and after; the nomination appears on Global Framework Updates and its download carries the name and group only |
| Moving the floor rewrites nothing | Tested: the rows are identical before and after; only the "to review" count moves |
| A screen answer equals a direct call | Tested for conditions, as it already was for titles |
| Real data | Texas: 29 facts, 95 conditions (49 recorded, 18 to review, 28 to name), disclosure restricted by one clause. Michigan: 91 facts, 118 conditions (69, 22, 27), disclosure cleared (public record) |
| The save buttons themselves | Clicked through on a throwaway copy of the ledger: disclosure cleared with a basis, a clause named, one proposed, one set aside, one parked and brought back, an unsure condition confirmed, the floor moved. Kyle's own ledger was not written to |
| Spend | None. The replays refuse to call the model |

## Judgement calls to flag

1. **"Not a rate condition" was added.** Many of the 55 unplaced clauses are not about price ("compliance reports provided free of charge"). Forcing a name on them would be wrong, so a third answer sets the clause aside: kept, relied on by nothing.
2. **An unsure condition can be confirmed from the Terms tab.** The plan only covered unnamed clauses. A condition marked "to review" has no question behind it, so the panel offers "Yes, confirm" or "change it to".
3. **Vendor names carry no scope choice.** Who a printed name is does not vary by contract, so the answer applies everywhere in the client's environment.
4. **Clearing a disclosure flag requires a basis; the note stays optional.** Three one-click choices cover the usual cases.
5. **The disclosure decision is recorded and shown, and nothing yet enforces it** (action item B38). Today a restricted set's rates still count.
6. **The "closest by wording" chips are word overlap, not a model.** They are labelled as closest, not suggested, because the engine already said none fits. Expect them to be wrong often.
7. **The one-line summary is a text draft.** It states what a condition's presence says ("client pays no expenses") and lists the rest as topics. It does not read the clause's direction for topics such as overtime.
8. **Questions are now counted once.** Texas shows 35, not 66: 5 job titles, 28 clauses, the disclosure check, one document type.
9. **Michigan still shows under Amendments.** Its file opens with a change notice, so intake called it an amendment. Relabelling it in the engine would change the instruction the model receives and force a paid re-read, so instead a person can correct the kind on the Documents tab ("change"); that answer stands on later runs. Left for Kyle to click (C13).

## Known limits, left

Identical clauses repeated across SOWs are listed once each (B39). Named people are counted, not listed. A re-run looks up saved answers for titles and conditions but not yet for place names or disclosure (B40). No automated test drives the JavaScript; the service tests cover every write path and the browser check was by hand.
