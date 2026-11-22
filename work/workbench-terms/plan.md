# Plan: terms in the workbench

**For Kyle to read before the screens are built** (`docs/how-we-build.md`). Written November 22, 2026. Step 1 touches no screen and starts at once; steps 2 to 5 wait for his go.

| # | Step | What changes | Proves it |
|---|---|---|---|
| 1 | **Bring the main ledger up to date** (B33) | Back up `ledger.sqlite`. Re-run the Texas set (seven files) and the Michigan Deloitte contract into it from the model cache; the cache-only stand-in refuses to spend if any prompt changed. When a document is re-run, the older run's open questions for it are closed as superseded. Kyle's saved answers on the G-Cloud set are untouched (that set is not re-run) | Counts match the regression replays (Texas 1,648 rates; Michigan 91 facts, 118 conditions); his six answers still in place; no duplicate questions |
| 2 | **The service** | Read endpoints: a contract set's disclosure status, facts, conditions by group, one condition with its page image; the inventory itself. The floor applied on read as a setting. Decision methods on the ledger, additive: name a condition, confirm a vendor name, clear a disclosure flag, each with scope and the analyst's name | Service tests: a named condition leaves the flagged list for the scope chosen and nowhere else; a proposed new condition appears on Global Framework Updates and changes no inventory file; moving the floor re-sorts without rewriting a row |
| 3 | **The Terms tab** | On a contract set: the disclosure check as the first line; facts as a short table; conditions grouped A to G with the clause quoted and a status (recorded, to review); click one for the clause on its page, boxed, beside what the system made of it | Seen on the real Texas and Michigan sets |
| 4 | **Three new question types in Review** | "Conditions" (name this one: suggested inventory rows first, or propose a new name and group), "Vendor names" (is this printed name this vendor), "Disclosure" (read the clauses found, then cleared or restricted, with a note). Same task card, same Save and Park, same scope buttons | A condition named through the screen equals the direct call; the 41 unnamed conditions listed, largest group first |
| 5 | **Review and tidy** | Review addendum; action list; the promises list regenerates itself | |

## Two things I want your view on before step 2

1. **Proposing a new condition.** When none of the 54 fits (a $400,000 credit if delivered hours fall below 93 percent of plan), you type a short name and pick its group. My recommendation: it is saved for this contract set at once and listed on Global Framework Updates as a nomination; I add it to the inventory file after you confirm there, so the inventory grows only on purpose.
2. **How much to show a CIO.** The Terms tab is an analyst's screen. A one-line summary per contract set ("travel included; no overtime; rates fixed for eight years; volume discount to 3.75 percent; public record") would be the CIO's view. Recommendation: build the analyst's tab now and draft that summary line as text you can react to, not as a designed screen yet.

## Not in this plan

Deriving effective rates from conditions (escalation, discounts): that belongs to the findings work. Checking invoices against conditions: reconciliation. Both read what this plan makes visible.

## Time

Step 1 is under an hour and needs nothing from you. Steps 2 to 4 are about a day. Step 5 an hour.
