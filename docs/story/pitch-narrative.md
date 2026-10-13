# One rate, followed: the product in one page

**Draft for conversation, October 13, 2026.** Written from the visual flow (`docs/story/follow-one-rate.html`) for Cowork's revision of the Pitch Deck (action item D3). Grounded in the Business Plan v1.5, the Early Adopter Presentation (November 10, v2), the Consortium Approach v1.7 and the Pitch Deck v1.1. Where those documents and the architecture decisions disagree, the architecture decisions win, and the last section says what to retire. Audience: an Early Adopter CIO. Every number below is from the ledger or the page.

## The problem, in the deck's own words

At a large enterprise, labour is 50 to 75 percent of technology cost, and more than 40 percent of that labour is bought from third parties: thousands of people, hundreds of statements of work, twenty or more vendors. Nobody can link the timecard billed to the invoice charged to the contracted rate. Skill matrices go stale, "off-rate-card" roles are billed at a premium, and reconciliation is done by sampling, if at all. The documents hold the answer; the organisation cannot read them at scale.

## What the product does

It reads the documents and keeps a book of record. Here is what happens to one rate.

1. **A contract set arrives.** The State of Texas signed a technology services agreement with Accenture: a master agreement, a statement of work, exhibits and attachments, seven files. The platform recognises them as one contract set because the contract number is printed in each. One file is labelled weakly; the platform says so rather than guessing.
2. **The page is read with positions.** Page 8 of the pricing attachment holds a rate table of 111 rows. Every cell is read with its position on the page.
3. **The rate is extracted and checked against the page.** The model returns the row exactly as written: "Advanced Systems Engineer", $83.00 per hour, year 1, onsite. The software then confirms that those words and that number are on page 8 at the claimed spot. An invented number is thrown out.
4. **The title is normalised once.** "Advanced Systems Engineer" becomes Systems Engineer, senior, in a role framework of 130 roles and four seniority bands. The decision was made once by a person, with reasoning, and every later occurrence is a lookup. The rate itself is never changed, converted or rounded.
5. **The row enters the ledger.** Vendor, client, rate as stated, role, band, confidence, scan quality, page and box. A vendor who challenges the row is shown page 8 with the line lit.

That is the Master Benchmark Ledger the deck promises, one row at a time. The same code ran unchanged on a second contract set, Accenture's UK G-Cloud rate page.

| What the two runs produced | |
|---|---|
| Rate rows in the ledger, each traceable to a page | 483 |
| Rows that count toward benchmarks | 458 |
| Items waiting for an analyst | 21 |

## What it refuses to guess

Precision comes first, because a false leakage claim in front of a vendor can lose the engagement and the consortium; a missed row is caught at the next refresh. So the platform never fills a default. On the Texas page, 23 of 53 titles state no seniority, and they stay unbanded rather than being called "intermediate". The title "Operations" names no role; the model was asked, answered with low confidence, and abstained, so the row is stored but not counted until an analyst decides. No place name is ever classified as onshore or offshore by the software; an analyst decides once per client. Every abstention is one sentence a consultant can read, and every analyst decision becomes a rule, so the same question is never asked twice.

## What the CIO gets

- **A ledger of every contracted rate** in their estate, each row traceable to a page, inside their own Azure environment. Documents, rows and vendor names never leave it. Only vocabulary and cohort summaries do.
- **A queue, not a black box:** every place judgment was applied, by whom, with the reason.
- **Benchmarks at the right cut:** role by seniority by location by technology, against public sources now and consortium cohorts as members join, published only when a cut has at least three observations and two contributing clients.
- **Savings stacked, never double-counted:** Contractual (billed against the contracted rate), Operational (the vendor's own best rate at this client), Market Alignment (the market mid-point), rolled up into the Role Composition Heatmap and the Total Potential Dashboard, with observed and projected shown as two numbers.
- **Consultants first, software behind them:** in the Value Validation phase, TWM's engagement pod feeds the documents in and works the queue; the CIO sees findings, not a tool.

## What is true today, and what comes next

Two contract sets have gone through every stage. Benchmarking, findings and the invoice-to-timecard reconciliation are designed and not yet built; they follow the volume run of the whole document library. The platform is deployed into each client's tenant as an installable stack, not a service clients log into.

## For the deck revision: wording to retire

- "Exports only anonymized neural weights" and "differential-privacy weight smudging": replaced by the own-versus-rent split (TWM owns prompts, schemas, the role framework, mapping table and evaluation sets; the reasoning model is rented) and by k-anonymity on published cohorts.
- "GPT-4o": the platform is model-agnostic; Claude is primary and GPT is benchmarked, by measured evaluation.
- "Normalized into standard hourly rates": rates are stored as stated, in their own currency and unit; any conversion is a derived column with the exchange rate and date beside it.
- "Contract cap" anywhere: say "contracted rate".
- The Early Adopter fee appears as three different figures across the four documents (Business Plan, Early Adopter Presentation, Pitch Deck). Kyle to confirm one before the revision.
