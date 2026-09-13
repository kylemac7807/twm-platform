# EDGAR Exhibit Extraction: Statement of Work (nib / wellteq, 2022) — modern SaaS support SOW with cloud pass-through pricing

- **Source URL (raw exhibit HTML):** https://www.sec.gov/Archives/edgar/data/1815436/000121390023007932/f20f2022ex4-44_advanced.htm
- **Filing:** Advanced Health Intelligence Ltd (formerly wellteq) Form 20-F, **filed 2023-02-03** (accession 0001213900-23-007932, EX-4.44)
- **Effective Date:** October 1, 2022 (under Master Services Agreement dated 2021-10-01); engagement to 2023-09-30
- **Retrieved:** 2026-09-01 via WebFetch structured extraction (raw download blocked by sandbox egress policy — re-download from Source URL)
- **License/status:** US SEC public filing — public record. **NO REDACTIONS.**
- **Rate data:** YES — actual fee constructs: AWS pass-through + 30% management fee, $3,000 + 30% DevSecOps fee, $5,000 fixed account management; user-block pricing. Rate card lives in the parent MSA.
- **MODERN CONSTRUCTION MARKERS:** cloud-consumption pass-through pricing, 99.9% uptime SLA, data-residency clause, user-tier rebaselining.

---

## Identity
- **Title:** Statement of Work — service delivery and support
- **Parties:** nib (Australian health insurer — Client) and wellteq (Supplier)
- **Scope:** Two mobile apps ("Well with nib", "Well with GU") + support, hosted in CMD-managed AWS infrastructure; app maintenance, member support, content updates, infrastructure monitoring, acceptance testing

## Section Structure
1 Engagement; 2 Engagement Outcomes; 3 Commencement/Termination Dates; 4 Services; 5 Professional Services; 6 Service Level Requirements; 7 Schedule of Charges; 8 Delivery Dates/Completion; 9 Special Conditions; Signatures.

## Pricing (unredacted)
| Charge Category | Details |
|---|---|
| User Charges | Pre-purchase (advance, annual); block pricing monthly for additional users |
| AWS hosting | Direct pass-through of AWS invoice |
| wellteq Management Fee | **30% of AWS invoice** |
| CMD DevSecOps | **$3,000 + 30% of AWS invoice** |
| wellteq Account Management | **$5,000 fixed** |
| Professional services | Per "Rate Card included in the Master Services Agreement" |

## Key Commercial Terms
- Uptime 99.9% excluding planned maintenance; daily backups; business-hours support
- **Data residency:** all data stored and processed in Australia
- User classifications: Engaged (login within 90 days) / Dormant / Disengaged
- New microservices require separate SOWs; **contract rebaselines at 5,000 users**

## Why useful to TWM
A current-generation SOW showing cloud-consumption economics inside a services relationship: hyperscaler pass-through with percentage management fees, fixed platform fees, per-user block pricing, and volume rebaselining triggers — the "cloud terms" pattern Kyle wants represented in the corpus.
