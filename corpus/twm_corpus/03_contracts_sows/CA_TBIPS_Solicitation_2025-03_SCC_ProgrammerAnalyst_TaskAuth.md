# Canada TBIPS Solicitation Extraction: Standards Council of Canada 2025-03 — Programmer Analyst Resources (Task Authorization RFP under TBIPS)

- **Source URL (raw PDF, 62 pp):** https://canadabuys.canada.ca/sites/default/files/webform/tender_notice/70780/tbips-solicitation--2025-03-programmer-analysts-resources_en.pdf
- **Program:** Task-Based Informatics Professional Services (TBIPS) Supply Arrangement, PSPC RFSO EN578-170432; portal: https://www.tpsgc-pwgsc.gc.ca/app-acq/sptb-tbps/am-sa-eng.html
- **Retrieved:** 2026-09-01 via WebFetch structured extraction (raw download blocked by sandbox egress policy — re-download from Source URL)
- **License/status:** Government of Canada open procurement publication.
- **Rate data:** Pricing template structure (Annex B Basis of Payment, blank per-diem tables) + explicit rate-formula rules; no filled-in rates (solicitation stage).

---

## 1. Issuing Information
- **Issuer:** Standards Council of Canada (SCC); Solicitation 2025-03, issued 2025-07-29, closing 2025-08-14
- **Scope:** Task-based professional services; up to 2 contracts, 1 year + up to two 1-year irrevocable options

## 2. Document Structure (canonical TBIPS RFP anatomy)
| Part | Content |
|---|---|
| Part 1 | General Information |
| Part 2 | Bidder Instructions |
| Part 3 | Bid Preparation (Technical / Financial / Certifications) |
| Part 4 | Evaluation Procedures and Basis of Selection |
| Part 5 | Certifications |
| Part 6 | Security, Financial, Other Requirements |
| Part 7 | Resulting Contract Clauses (Task Authorization, payment, insurance) |
| Attachment A | Bidder Response Form |
| **Annex A** | **Statement of Work (Appendices A-D for TA process)** |
| Attachment B | Evaluation Criteria |
| Attachment C | Disclosure of Resources on Multiple Contracts |
| **Annex B** | **Basis of Payment — Pricing Form (per-diem rate template)** |

## 3. Resource Categories, Levels, Rate Structure
| Stream | TBIPS Category | Level | Qty |
|---|---|---|---|
| Stream 1 (A) | A.6 Programmer/Software Analyst — API Developer | Level 2 (Intermediate) | 1 |
| Stream 1 (A) | A.6 Programmer/Software Analyst — Blazor Developer | Level 2 (Intermediate) | 1 |
| Stream 4 (B) | B.3 Business Consultant — QA Engineer | Level 2 (Intermediate) | 1 |
| Stream 4 (B) | B.1 Business Analyst — Scrum Master | Level 2 (Intermediate) | 1 |

Rate rules:
- Fixed, all-inclusive **per-diem rate in CAD**; partial days prorated on a **7.5-hour workday**
- Rates fixed through Contract Period; period-over-period increases capped at **5%**; later-period rates cannot be lower than first-period rate
- Level monotonicity: Level 3 rate >= Level 2 >= Level 1 for the same category
- Blank price cells scored as $0.00 and cannot be added later
- Refusal to honor bid rates can lead to sanctions up to debarment

## 4. Task Authorization (TA) Mechanism
1. Technical Authority issues **draft TA** describing the task
2. Contractor responds within **5 working days**: proposed total price + cost breakdown, proposed resources per Appendix A of Annex A, quotes per Basis of Payment
3. Fixed-price TAs require supporting cost breakdown
4. TA valid only when signed by Technical Authority AND Client Financial Authority; **no work before validly issued TA**
5. Quarterly usage reports: TA number, resource names/categories, estimated vs actual cost, status

## 5. Evaluation
- Contract award: Rated 50% / Pricing 50%; pricing points = lowest price / bidder price x weighting
- TA-stage resource assessment: Rated 30% (min 60% to advance) / Interview 40% / Pricing 30%
- Payment monthly in arrears for Actual Time Worked, timesheet-supported; total liability capped at contract page-1 amount

## Why useful to TWM
Canonical Canadian TBIPS task-authorization contract anatomy: stream/category/level taxonomy (A.6, B.1, B.3...), per-diem pricing conventions (7.5-hr day, proration), rate-escalation caps and level-monotonicity rules, and the TA workflow — the structures TWM must parse in Canadian telecom/bank vendor agreements modeled on government norms. Note: TBIPS "streams and categories" reference (all streams/categories) at https://www.tpsgc-pwgsc.gc.ca/app-acq/sptb-tbps/categories-eng.html (fetch blocked here — see leads).
