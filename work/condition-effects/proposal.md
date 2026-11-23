# Proposal: what each rate condition does to the rate we benchmark

**Drafted November 22, 2026, by Claude Code, for Kyle to mark up. Nothing here is built.** Kyle's question: should we be more definitive about whether a condition changes the rates we use? This gives every one of the 54 conditions in the inventory (`specs/rate-conditions.md`) one proposed class. The last column is yours: leave it blank to agree, or write the class you want.

## The rule this rests on (decided October 13, 2026)

A condition never changes a stored rate. The ledger keeps the rate as printed, with its page. Anything worked out from it is a second figure, labelled derived, that cites the clause.

## The four classes

| Class | In plain words | What happens to the rate in a benchmark | Conditions |
|---|---|---|---|
| 1 | Changes the number, and the contract (or a published, dated source) gives everything needed | A derived effective rate sits beside the printed rate | 8 |
| 2 | Changes the number only if something we cannot see is true (the client's spend, paying early, an extension) | Never applied to a benchmark. Used in that client's own finding, where the fact is known | 4 |
| 3 | Changes what the number buys | The rate is flagged (10), compared separately (2), or left out of role comparisons (2) | 14 |
| 4 | Does not touch the rate | Used for invoice and timesheet checks, as evidence in a finding, or in the disclosure check | 28 |
| | **Total** | | **54** |

The benchmark's main figure stays the printed contracted rate for its contract year. The derived rate is a second figure, for class 1 only.

## The 54 rows

### A. Expenses and pass-throughs

| Condition | What it is | Proposed class | What happens to the rate | Kyle |
|---|---|---|---|---|
| **Expenses included** | Travel, lodging and incidentals are inside the rate | 3 Flag | The rate stays in the benchmark, marked "all-in": it carries travel, so it reads high beside rates that bill travel separately | |
| **Expenses extra** | Expenses billed on top of the rate, at cost or capped | 3 Flag | The rate stays, marked "expenses on top": the true cost is higher than the rate. Also an invoice check later | |
| **Expenses refused** | The client pays no expenses at all | 3 Flag | Marked "all-in", the same side as expenses included: the vendor absorbs travel inside the rate | |
| **Travel time** | Whether hours spent travelling are billable | 4 | No effect on the rate. An invoice and timesheet check | |
| **Passthrough markup** \* | A handling fee on third-party costs passed through | 4 | No effect on the labour rate: it concerns third-party costs. An invoice check. Today's inventory calls it a label; I propose dropping that | |
| **Tooling fees** \* | Platform, licence or tool charges billed beside labour | 3 Flag | Marked "fees beside the rate": part of the cost sits outside the rate, so the rate reads low | |
| **Onboarding fees** \* | Background checks, equipment, badges, set-up charged separately | 3 Flag | Marked "fees beside the rate", as tooling fees. Also an invoice check | |

### B. What an hour, a day or a month is

| Condition | What it is | Proposed class | What happens to the rate | Kyle |
|---|---|---|---|---|
| **Billing increment** | The smallest unit billed (hour, quarter hour, half day) | 4 | No effect on the rate. A timesheet check | |
| **Day definition** | How many hours a day rate buys | 1 | When the hours in a day are printed, a derived hourly figure (day rate divided by those hours) sits beside the day rate. With no hours printed, a day rate is compared only with day rates and never converted | |
| **Monthly hours max** | A ceiling on billable hours in a month | 4 | No effect on the rate. A timesheet check | |
| **Nonproductive excluded** | Time that may not be billed: commuting, holidays, training, meetings | 4 | No effect on the rate. A timesheet check | |
| **Overtime** \* | Whether overtime is billable and at what multiple | 4 | No effect on the base rate. A timesheet check. Today's inventory also calls it a label; I propose dropping that | |
| **Holidays** | Whether statutory holidays are billed | 4 | No effect on the rate. A timesheet check | |
| **Capacity formula** \* | A team-month price built from a formula rather than hours worked | 3 Leave out | A team-month price is not a rate for a role, so it stays out of role comparisons. Any per-role rates printed inside the formula are ordinary rates. Also an invoice check | |

### C. The structure of the rate itself

| Condition | What it is | Proposed class | What happens to the rate | Kyle |
|---|---|---|---|---|
| **Rate ceiling** \* | The printed rate is a not-to-exceed figure, not a price | 3 Flag | The rate stays in the benchmark, marked "not-to-exceed". What was actually paid comes from invoices later | |
| **Escalation in grid** | Each contract year's rate is printed; the increase is visible | 4 | Nothing to do: each contract year's rate is already its own row in the ledger. Kept as evidence of the increase | |
| **Escalation fixed pct** | One rate plus a stated yearly percentage | 1 | A derived rate for each later year (the printed rate raised by the stated percentage), citing the clause | |
| **Escalation index** \* | The increase tied to an index | 1 | A derived rate for each later year, once the published index is loaded with its date and source, as exchange rates are. Until then a flag only | |
| **Escalation open** | Rates "subject to annual review", no figure | 3 Flag | Marked "later years not fixed": the printed rate is good for its first year only | |
| **Rate flat** | Rates stated flat across several years | 1 | The printed rate is carried to each stated year, as a derived figure citing the clause. No arithmetic, no assumption | |
| **Extension rate** | What rate applies if the contract is extended | 2 | Applies only if the contract is extended. Never in the benchmark; cited in a client's own finding | |
| **Blended rate** | One rate for a team regardless of who does the work | 3 Leave out | One rate for a whole team is not a rate for a role, so it stays out of role comparisons | |
| **Level definition** | Whether the document says what "Senior" means | 4 | No effect on the rate. It is evidence for the seniority band the rate is filed under | |
| **Service type split** | Different rates for the same title by service type | 3 Split | Already stored on each rate. Staff augmentation and managed services are compared separately | |
| **Location split** | Different rates by delivery location | 3 Split | Already stored on each rate. Onshore, nearshore and offshore are compared separately | |
| **Billing currency** | The currency billed and who carries exchange risk | 1 | Already built: a converted figure beside the printed one, with the exchange rate, its date and source | |
| **Taxes** | Whether taxes are inside or on top of the rate | 3 Flag | Marked "tax inside" or "tax on top". Not netted out unless the percentage is printed | |

### D. Discounts, credits and commitments

| Condition | What it is | Proposed class | What happens to the rate | Kyle |
|---|---|---|---|---|
| **Volume tier** | A discount that grows with spend | 2 | Depends on the client's spend, which the contract does not hold. Never in the benchmark; applied in a client's own finding where the spend is known | |
| **Period discount** | A discount for a stated period | 1 | A derived rate for the stated period (the printed rate less the discount), citing the clause | |
| **Prompt pay discount** \* | A discount for paying early | 2 | Depends on the client paying early. Never in the benchmark; an invoice check and a finding. Today's inventory calls it a derivation; I propose this instead | |
| **Payment terms** | When payment is due | 4 | No effect on the rate. An invoice check | |
| **Signing credit** \* | A one-off credit that lowers the headline price | 2 | The amount is printed but spreading it across the rate needs the total hours or spend. Never in the benchmark; applied in a client's own finding | |
| **SLA credit** | Credits for missed service levels | 4 | Applies only when a service level is missed. No effect on the rate. An invoice check | |
| **Minimum commitment** \* | Spend, hours or headcount the client must buy | 3 Flag | Marked "committed volume": a rate bought with a commitment is not like for like with one that has none | |
| **No minimum** | The contract says there is none | 4 | No effect on the rate. Evidence for a finding | |
| **Most-favoured customer** | Most-favoured-customer or no-less-favourable pricing | 4 | No effect on the rate. Evidence for a finding | |
| **List discount** | A rate quoted as a percentage off a published list | 1 | When the list price and the percentage are both in hand, a derived rate (list less the discount). Otherwise a flag only | |

### E. Scope, change and exit

| Condition | What it is | Proposed class | What happens to the rate | Kyle |
|---|---|---|---|---|
| **Change pricing** | How new or changed work is priced | 4 | No effect on the rate. Evidence for a finding | |
| **Termination fees** | Charges on early termination or wind-down | 4 | No effect on the rate. Evidence for a finding | |
| **Transition charges** \* | Front-loaded set-up or transition fees | 3 Flag | Marked "fees up front": cost moved ahead of the rate, so the rate reads low | |
| **Knowledge transfer** | Whether hand-over time is billed | 4 | No effect on the rate. A timesheet check | |
| **Personnel substitution** | Replacement of named people, and whether ramp-up is billed | 4 | No effect on the rate. A timesheet check | |
| **Productivity commitment** \* | A promised year-on-year reduction | 1 | When a yearly percentage is printed, a derived rate for each later year. With no figure (as in Texas) it is evidence only | |

### F. Transparency and governance

| Condition | What it is | Proposed class | What happens to the rate | Kyle |
|---|---|---|---|---|
| **Invoice detail** | Whether invoices show people, hours and rates, or only milestones | 4 | No effect on the rate. It decides what the invoice checks can see | |
| **Audit rights** | The client's right to audit rates and time | 4 | No effect on the rate. Evidence for a finding | |
| **Benchmark clause** | The client's right to benchmark rates and the adjustment that follows | 4 | No effect on the rate. Evidence for a finding; it also counts toward clearing the disclosure check | |
| **Subcontractor passthrough** \* | Subcontracted labour billed at the prime's rate | 4 | No effect on the rate. An invoice check and a finding. Today's inventory calls it a label; I propose dropping that | |
| **Common categories** | A client rule that every vendor uses the same rate-card categories | 4 | No effect on the rate. Evidence for a finding | |

### G. Disclosure and benchmarking rights

| Condition | What it is | Proposed class | What happens to the rate | Kyle |
|---|---|---|---|---|
| **Confidentiality scope** | What the contract treats as confidential, and whether pricing is inside it | 4 | No effect on the rate. Part of the disclosure check | |
| **Advisor disclosure** | Whether the client may show the contract to advisors, auditors or consultants under confidentiality | 4 | No effect on the rate. Counts toward clearing the disclosure check | |
| **Disclosure bar** | A clause that forbids the client sharing pricing or terms with any third party | 4 | No effect on the rate. Restricts: the whole contract set stays out of benchmarks until a person clears it | |
| **Benchmark conditions** | What a benchmark must do and what the vendor need not give: an independent benchmarker under NDA, a minimum number of comparables, the factors to normalize, no internal costs or other-customer data | 4 | No effect on the rate. Counts toward clearing the disclosure check | |
| **Benchmark data use** | A limit on using the contract's data beyond this contract or for other clients | 4 | No effect on the rate. Restricts: the whole contract set stays out of benchmarks until a person clears it | |
| **Public record** | The contract is public under a freedom-of-information or procurement law | 4 | No effect on the rate. Counts toward clearing the disclosure check | |

\* A judgement call; see below.

## The 13 judgement calls

These are the rows where a reasonable person could choose differently. Each line says what I chose and what the other choice would be.

1. **Passthrough markup.** Class 4. The other choice: flag the rate, on the view that a vendor with no mark-up on pass-through costs may recover it in the rate.
2. **Tooling fees.** Flag. The other choice: class 4, treating tool charges as a separate purchase that says nothing about the labour rate.
3. **Onboarding fees.** Flag, for the same reason as tooling fees. The other choice: class 4.
4. **Overtime.** Class 4. The other choice: flag the rate when overtime is billed above the base rate, because the effective hourly cost is then higher than the rate.
5. **Capacity formula.** Left out of role comparisons. The other choice: derive an implied hourly rate from the formula (class 1). I held back because the formula prices a team, and the mix of people is not fixed.
6. **Rate ceiling.** Kept in the benchmark, flagged. The other choice: compare not-to-exceed rates only with other not-to-exceed rates. Most public-sector rate cards are ceilings, so splitting would leave thin groups.
7. **Escalation index.** Class 1 once the index is loaded with its date and source, as exchange rates are. The other choice: class 2, never derived, because the figure comes from outside the contract.
8. **Prompt pay discount.** Class 2. The other choice: class 1, assuming the client always pays early. I would not assume it.
9. **Signing credit.** Class 2. The other choice: class 1 when the contract also prints total hours or value, so the credit can be spread without a guess.
10. **Minimum commitment.** Flag. The other choice: class 4, evidence only. I flagged it because a price bought with a volume commitment is a different deal.
11. **Transition charges.** Flag. The other choice: class 4, evidence only.
12. **Productivity commitment.** Class 1 only when a percentage is printed. Texas prints none, so there it is evidence. The other choice: class 2 always, because such promises are often tied to conditions.
13. **Subcontractor passthrough.** Class 4. The other choice: flag the rate, because the rate then includes the prime's margin on someone else's labour.

## Two rules that follow, for you to confirm

1. **A flag does not remove a rate.** A flagged rate is still counted; the flag travels with it so a reader sees "all-in" or "not-to-exceed" beside the number. Only the two "leave out" conditions and a restricted disclosure check keep a rate out.
2. **A new condition must be given a class when it is proposed.** The workbench would ask for it alongside the name and group.

## If you agree, what gets built (backlog item B41)

The class added to the inventory as a fifth column, kept identical to the code by the existing test. The class shown in plain words on every condition in the workbench. Each rate showing the conditions that apply to it. The derived rate for class 1. The benchmark honouring flags, splits and leave-outs. None of this is started.
