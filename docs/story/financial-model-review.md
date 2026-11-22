# Financial model review — November 22, 2026

The model reviewed is `TWM - Business Model - October 2nd.xlsx` in Kyle's business-documents folder. Business Plan v1.5 and slide 22 of the pitch deck are drawn from it. All figures are CAD $MM.

`work/story/financial_model_review.py` rebuilds the workbook quarter by quarter and reproduces every figure on slide 22. Each scenario below changes one assumption in that rebuild.

## Bottom line

The workbook's arithmetic is correct. The weak points are four assumptions, plus a mismatch between the model and the Ask:

1. The $1MM SAFE does not fund the model as built.
2. The contingent fee makes the funding gap much deeper.
3. The $4MM a year per client carries the whole model.
4. Clients arrive in jumps.

## How the model works

| Part | What the workbook assumes |
|---|---|
| Early Adopters | 4 at $1.5MM each, then a second cohort of 2 at $2MM each. Fees are booked while the work is done. |
| Full-fee clients | Every client pays $4MM a year from the day it joins, with no ramp and no losses. Clients grow 8 → 12 → 25 → 40 → 50. |
| Consulting | A pod is 1 Engagement Manager ($350K) and 4 Associates ($250K each), $1.35MM a year. A pod covers 2 clients during the Early Adopter period and 4 after. Leadership costs rise from $1.5MM to $7MM a year. |
| Software and AI | Leaders at $750K and engineers at $300K. The team grows from 2 + 6 to 3 + 15, then to 10 + 50 from Year 3. Overhead rises from $1MM to $4MM a year. |
| Sales | $300K a year for every client already signed. |
| Other overhead | Rises from $1.5MM to $10MM a year. |
| Timing | The workbook runs calendar 2026 to 2030. The deck moves everything eight months later for the December 2026 start, so model years run September to August. Year 1 is December 2026 to August 2027, plus $0.75MM of pre-launch cost. |

## Findings, most important first

**1. The Ask does not fund the model.** The model needs $9.4MM before it pays for itself, and its lowest point is the end of February 2028. The first quarter (December 2026 to February 2027) alone costs $2.5MM. $1MM covers about five weeks of the model's costs, or about three months if TWM hires only the two pods and the consulting leadership. The Series A comes in the second half of 2027, so March to August 2027 has no funding.

**2. The contingent fee makes the gap deeper.** The model books Early Adopter fees during the work. If a fee is earned only once the client has seen more than $10MM of value, the cash arrives later:

| If the fee is earned … | Cash needed before TWM pays for itself |
|---|---|
| during the work (model as is) | $9.4MM |
| two quarters later | $16.4MM |
| two quarters later, and only half the Early Adopters reach $10MM | $17.9MM |

"Value" still has to be defined. Value can be savings identified and agreed at the end of Value Acceleration, or savings realized once contracts are renegotiated. Realized savings could push payment out by another 6 to 12 months.

**3. The $4MM per client per year carries the whole model.** The fee starts on day one and recurs every year. Every Early Adopter is assumed to convert the moment its engagement ends. The deck says the fee is never more than 15% of the value created, so $4MM a year needs about $27MM of new value per client every year. A client at the $100MM target-market floor saves $10MM to $15MM once, at 10–15%. The Business Plan itself says $20MM of savings brings TWM $2MM to $3MM.

**4. Clients arrive in jumps.** The count goes from 12 to 25 in one quarter, then from 25 to 40. A bank's buying cycle plus its vendor-risk onboarding takes 6 to 12 months. Sales cost is tied to clients already signed, so nothing is spent ahead of a jump. The workbook's own note says the revenue model is "too lumpy" and needs a finer-grained version.

**5. The consulting numbers imply McKinsey-level prices, or a platform that does most of the work.** One pod costs $1.35MM and serves 4 clients, which is $16MM of revenue a year. McKinsey bills about $18MM a year for the same team (Business Plan: $1.5MM a month). At exit the model earns about $3.2MM per consultant ($200MM over 62 people). That is the platform argument, but it clashes with "materially discounted against McKinsey" unless the deck says the platform carries the work.

**6. The in-tenant design adds costs the model leaves out.** Each client runs its own copy inside its own Azure environment. That means deployment, upgrades, security reviews, vendor-risk questionnaires and support for every client, and the model has no per-client running cost. The model also shows nothing for:

- insurance (cyber and errors-and-omissions, which banks require)
- a SOC 2 audit
- legal work on the consortium agreements
- waiting 60 to 90 days for banks to pay
- exchange rates on US clients
- tax

"Other overhead" may be meant to cover some of these.

**7. The 62% exit margin will draw questions.** Costs stay flat through Years 3 to 5 while revenue grows 2.4 times; the software team stays at 60 people. A margin well above what established software companies report reads as a gap in the model, not a plan.

**8. Smaller items**

- The workbook prices a software leader at $750K. The Business Plan and slide 22 say $700K.
- Labels on the Revenue sheet are half a year off from where the numbers are used. For example, "Year 2 (first half)" clients are used in the second half of the year.
- The software team goes from 18 to 60 people in one quarter.
- Consulting cost falls when clients rise from 6 to 8, because a pod's load doubles overnight.
- "Profitable at 5 clients" holds on the Year 2 cost base. On the Year 3 cost base it takes 10.

## Scenarios

Each row changes one thing unless it says otherwise. "Profitable from" is the first quarter after which every quarter is profitable, in the deck's dates.

| Scenario | Cash needed before self-funding | Profitable from | Year 5 revenue | Exit-rate profit |
|---|---|---|---|---|
| Model as is | $9.4MM | Mar 2028 | $180MM | $125MM (62%) |
| Contingent fee, earned two quarters later | $16.4MM | Mar 2028 | $180MM | $125MM (62%) |
| Contingent, and half the Early Adopters reach $10MM | $17.9MM | Mar 2028 | $180MM | $125MM (62%) |
| Full fee $2.5MM a year, not $4MM | $14.9MM | Mar 2029 | $113MM | $50MM (40%) |
| Clients a year slower, 40 by Year 5 | $10.0MM | Mar 2029 | $144MM | $91MM (57%) |
| $0.4MM a year per client to run each install (illustrative) | $11.4MM | Mar 2028 | $180MM | $105MM (52%) |
| All four above together (fee $3MM) | $29.1MM | Mar 2030 | $108MM | $35MM (29%) |
| Lean launch, contingent fee | $11.0MM, of which $3.5MM before the Series A | Mar 2028 | $180MM | $125MM (62%) |
| Lean launch, a third of each Early Adopter fee at signing | $8.7MM, of which $1.5MM before the Series A | Mar 2028 | $180MM | $125MM (62%) |

In the lean launch, pods are hired only when the Early Adopter work starts (March 2027). The software team waits for the Series A (September 2027), and Year 1 leadership and overhead are halved. The working prototype is what makes this credible.

## Decisions for Kyle

1. **Funding.** Keep $1MM with a lean launch, or raise more now? Recommendation: run lean until the Series A, ask Early Adopters for a third of the fee at signing, and size the SAFE at about $1.5MM. Plan the Series A at about $12MM to $15MM, which covers the $8.7MM need with room to spare.
2. **The contingent fee.** What counts as $10MM of value, and when is the fee paid? Recommendation: savings identified and signed off by the client's CFO or CPO at the end of Value Acceleration, with payment on that sign-off.
3. **Full-fee pricing.** What does a client pay after the Early Adopter phase, and for what? For example, a yearly fee for the benchmark and the platform, plus a share of new savings found. Recommendation: build the price up from that, and model $2.5MM to $3MM as the base case with $4MM as upside.
4. **Client ramp.** Add clients month by month, tied to the number of salespeople and an assumed buying cycle.
5. **Missing costs.** Add a per-client cost to run each install, plus insurance, SOC 2, legal and payment delays.
6. **Calendar.** Rebuild month by month on calendar years from December 2026, so investors read 2027, 2028 and so on.

Once 1 to 3 are decided, the next step is a new version of the workbook. It would be monthly, with every assumption above as an input, and with cash needed, profitable-from and exit margin as outputs.
