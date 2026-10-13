# Rate conditions: the fine print that changes what a rate really costs

**Started October 13, 2026** by the contract-terms stream at Kyle's request. A living inventory; additions carry a date and a source document. The label "rate conditions" is proposed (Kyle asked for one); the alternative is "comparability terms". The point of the list: vendors keep their costs opaque and hard to compare, and every device they use should be named, found on the page, and shown beside the rate.

## The rules (decided by Kyle, October 13, 2026)

1. **A condition never changes a stored rate.** The ledger holds the rate as printed, with its page. A condition is stored beside it as a term with its own page and quote.
2. **Effective rates are derived, labelled derived, and built in the findings work,** not in extraction. Example: a contract that prints "$122 an hour, escalating 3 percent a year" gets a derived column for year 3 of $129.43 that cites the clause; the stored rate stays $122. The same pattern as currency conversion.
3. **A condition the model is not sure of is flagged, not recorded.** Every stored condition is a quote found on its page.

## What TWM does with a condition (the "use" column below)

- **Label**: an attribute shown beside the rate so two rates are compared like for like, or not compared (travel included versus travel extra).
- **Derive**: an arithmetic effect on the effective rate for a stated period or volume, as a derived column (an escalation percentage, a volume discount).
- **Check**: a rule an invoice or timesheet is tested against in reconciliation (no overtime, no travel, hours per month).
- **Evidence**: a clause cited in a finding (the extension runs at the prior year's rate).

## The six groups (confirmed by Kyle, October 13, 2026)

A condition is one row: one thing a contract can say that changes what the printed rate really costs, or whether it can be compared with another vendor's rate. The groups are the six headings the rows sit under. Each key carries its group in the code as well, so a screen or a report can show the inventory the same way.

| Group | What its rows have in common | Rows |
|---|---|---|
| A. Expenses and pass-throughs | Costs that ride on top of, or hide inside, the hourly rate | 7 |
| B. What an hour, a day or a month is | How time is counted before the rate is applied | 7 |
| C. The structure of the rate itself | How the number on the page is built | 13 |
| D. Discounts, credits and commitments | Money off, or money the client must spend | 10 |
| E. Scope, change and exit | What happens when work changes or ends | 6 |
| F. Transparency and governance | What the client is allowed to see and check | 5 |
| | **Total** | **48** |

## The inventory

Keys are the controlled vocabulary the extraction prompt uses to type a term; a test keeps this table, including the groups and the count, identical to the code's list. "Seen" says where the library already shows the condition; "typical wording" rows are expected and not yet seen.

### A. Expenses and pass-throughs

| Key | What it is, in one line | Seen, or typical wording | Use |
|---|---|---|---|
| `expenses_included` | Travel, lodging and incidentals are inside the rate | Texas Exhibit 2, 2.1.1.4 (page 6): travel and lodging "are included in the Charges"; 6.4 (page 22): the rate "is inclusive of all travel expenses" | Label |
| `expenses_extra` | Expenses billed on top of the rate, at cost or capped | Typical: "reasonable travel expenses reimbursed at cost, not to exceed 10 percent of fees" | Label, Check |
| `expenses_refused` | The client pays no expenses at all | Michigan SOW 4.30.3 and 7.20: "No travel or expenses will be reimbursed" | Label, Check |
| `travel_time` | Whether hours spent travelling are billable | Michigan SOW: "Travel time will not be reimbursed"; Texas 6.4: travel is non-productive time, not charged | Check |
| `passthrough_markup` | A handling fee on third-party costs passed through | Texas Exhibit 2, 6.3 (pages 20 to 21): "no mark-up or margin"; software "at cost with no markup" | Label, Check |
| `tooling_fees` | Platform, licence or tool charges billed beside labour | Typical: "a platform fee of $x per user per month" | Label |
| `onboarding_fees` | Background checks, equipment, badges, set-up charged separately | Typical: "onboarding fee per resource" | Label, Check |

### B. What an hour, a day or a month is

| Key | What it is, in one line | Seen, or typical wording | Use |
|---|---|---|---|
| `billing_increment` | The smallest unit billed (hour, quarter hour, half day) | Typical: "billed in half-day increments" | Check |
| `day_definition` | How many hours a day rate buys | G-Cloud 15 cards: day rates with no working-day definition on the page (Atos card note) | Label |
| `monthly_hours_max` | A ceiling on billable hours in a month | Texas 6.4 item 3 (page 22): business days in the month times eight hours | Check |
| `nonproductive_excluded` | Time that may not be billed: commuting, holidays, training, meetings | Texas 6.4 items 1 and 5 (pages 22 to 23) | Check |
| `overtime` | Whether overtime is billable and at what multiple | Texas 6.4 item 3: overtime only if approved and "at the same rate"; Michigan 4.30.2: "No overtime will be authorized or paid" | Label, Check |
| `holidays` | Whether statutory holidays are billed | Michigan 4.30.2: "The State does not compensate for holiday pay" | Check |
| `capacity_formula` | A team-month price built from a formula rather than hours worked | Michigan SOW: staff times rate times 45 hours times 52 weeks less 96 holiday hours, divided by 12 | Derive, Check |

### C. The structure of the rate itself

| Key | What it is, in one line | Seen, or typical wording | Use |
|---|---|---|---|
| `rate_ceiling` | The printed rate is a not-to-exceed figure, not a price | Michigan Table 5 "Not-to-Exceed Hourly Rate": Technical Lead $175 | Label |
| `escalation_in_grid` | Each contract year's rate is printed; the increase is visible | Texas pricing exhibit (page 8): $122.00, $125.66, $129.43 for years 1 to 3 | Label |
| `escalation_fixed_pct` | One rate plus a stated yearly percentage | Typical: "rates increase 3 percent on each anniversary" | Derive |
| `escalation_index` | The increase tied to an index | Typical: "adjusted annually by CPI, capped at 4 percent" | Derive (needs the index) |
| `escalation_open` | Rates "subject to annual review", no figure | Typical | Label (not comparable across years) |
| `rate_flat` | Rates stated flat across several years | GSA Deloitte pricelist: flat across option years 6 to 10 | Label |
| `extension_rate` | What rate applies if the contract is extended | Texas Exhibit 2, 2.1.6 (page 12): the prior contract year's rates | Evidence |
| `blended_rate` | One rate for a team regardless of who does the work | Michigan SOW (page 122): "a blended rate of $150 per hour" | Label (hides mix) |
| `level_definition` | Whether the document says what "Senior" means | Texas 6.4 item 2: role descriptions and experience "documented in the SMM"; GSA pricelists carry years of experience per category | Label (feeds banding) |
| `service_type_split` | Different rates for the same title by service type | Texas grid: staff augmentation and managed services columns | Label |
| `location_split` | Different rates by delivery location | Texas grid: onsite and remote blocks; G-Cloud 15: UK and offshore columns | Label |
| `billing_currency` | The currency billed and who carries exchange risk | Texas Exhibit 2, 1 item 7 (page 5): "paid in U.S. Dollars" | Label |
| `taxes` | Whether taxes are inside or on top of the rate | Texas Exhibit 2, 2.1.1.7 (pages 7 to 8) | Label |

### D. Discounts, credits and commitments

| Key | What it is, in one line | Seen, or typical wording | Use |
|---|---|---|---|
| `volume_tier` | A discount that grows with spend | Texas pricing exhibit (page 11): incremental tiers from 0.75 to 3.75 percent of monthly charges | Derive (needs spend) |
| `period_discount` | A discount for a stated period | Michigan change notice, 2020: "a 10% monthly discount ... valid until December 31, 2022" | Derive |
| `prompt_pay_discount` | A discount for paying early | Michigan SOW: 1 percent "if paid within 15 business days" | Derive, Check |
| `payment_terms` | When payment is due | Michigan cover page: NET 45; Texas Exhibit 2, 3.1 (page 13): invoiced in arrears | Check |
| `signing_credit` | A one-off credit that lowers the headline price | Typical: "transition credit of $x applied to the first invoices" | Derive |
| `sla_credit` | Credits for missed service levels | Texas Exhibit 2, 3.1.3 (page 14) | Check |
| `minimum_commitment` | Spend, hours or headcount the client must buy | Typical: "minimum annual commitment of $x" | Label, Evidence |
| `no_minimum` | The contract says there is none | Texas Exhibit 2, 1 item 6 (page 5): no "minimum fees or support level pricing" | Evidence |
| `mfc` | Most-favoured-customer or no-less-favourable pricing | Texas Exhibit 2, 2.1.2.1 item 9 (page 10): new services "no less favorable to DIR than the pricing and labor rates set forth herein" | Evidence |
| `list_discount` | A rate quoted as a percentage off a published list | Typical on GSA schedules: "x percent off commercial list" | Label |

### E. Scope, change and exit

| Key | What it is, in one line | Seen, or typical wording | Use |
|---|---|---|---|
| `change_pricing` | How new or changed work is priced | Texas 2.1.2 (page 9); Michigan: change requests priced "by position and the associated position-specific rates" (page 201) | Evidence |
| `termination_fees` | Charges on early termination or wind-down | Typical: "termination for convenience fee equal to x months of charges" | Evidence |
| `transition_charges` | Front-loaded set-up or transition fees | Texas Exhibit 2, 6.5 Transition Charges (page 23) | Label |
| `knowledge_transfer` | Whether hand-over time is billed | Texas 6.4 item 5f (page 23): knowledge transfer is not charged | Check |
| `personnel_substitution` | Replacement of named people, and whether ramp-up is billed | Typical: "replacement at no additional cost; overlap not billed" | Check |
| `productivity_commitment` | A promised year-on-year reduction | Texas Exhibit 2, 6.2.3 (page 19): charges "must include year-on-year reductions related to the AMS productivity improvements" | Derive, Evidence |

### F. Transparency and governance

| Key | What it is, in one line | Seen, or typical wording | Use |
|---|---|---|---|
| `invoice_detail` | Whether invoices show people, hours and rates, or only milestones | Michigan SOW (page 122): payment "on a Deliverable basis" with hours; Texas 3.1 (page 13): invoices carry the data used to establish the charges | Check (what reconciliation can see) |
| `audit_rights` | The client's right to audit rates and time | Texas Exhibit 2, 4 item 5 (page 16): right to "access, audit, and validate" | Evidence |
| `benchmark_clause` | The client's right to benchmark rates and the adjustment that follows | Typical: "either party may request a benchmark after year 2" | Evidence |
| `subcontractor_passthrough` | Subcontracted labour billed at the prime's rate | Typical | Label |
| `common_categories` | A client rule that every vendor uses the same rate-card categories | Texas 6.4 item 6 (page 23): "All Successful Respondents shall have the same rate card categories" | Evidence (a lever a bank can copy) |

## How the inventory grows

Flag, then codify. The model types each term it finds with a key from this list, or `other` with its own words. Every `other` lands in the review queue; when an analyst names it, the key is added here with the date and the document, and to the code's list, and the prompt example is written. The inventory is versioned like the taxonomy: keys are appended or deprecated, never silently renamed.
