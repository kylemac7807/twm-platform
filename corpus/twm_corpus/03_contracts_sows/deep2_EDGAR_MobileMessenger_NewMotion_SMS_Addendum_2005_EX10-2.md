# EDGAR Exhibit Extraction: US MT Billed Premium SMS Service Addendum (Mobile Messenger / NewMotion) — telecom tiered volume pricing, UNREDACTED

- **Source URL (raw exhibit HTML):** https://www.sec.gov/Archives/edgar/data/1022899/000114420407007236/v064884_ex10-2.htm
- **Filing:** MPLC, Inc. Form 8-K, filed 2007-02-13 (accession 0001144204-07-007236, EX-10.2); sibling exhibits v064884_ex10-19.htm, v064884_ex10-20.htm in same filing
- **Agreement date:** April 28, 2005 (addendum to a Master Services Agreement)
- **Retrieved:** 2026-09-01 via WebFetch structured extraction (raw download blocked by sandbox egress policy — re-download from Source URL)
- **License/status:** US SEC public filing — public record. **NO REDACTIONS.**
- **Rate data:** YES — unredacted setup/monthly fees, per-message rates, tiered volume pricing, and an $80/hour development rate.
- **Vertical:** TELECOM (mobile messaging aggregation) — TWM target vertical; illustrates volume-tier pricing formulas.

---

## Identity
- **Title:** US MT Billed Premium SMS Service Addendum (under MSA)
- **Parties:** Mobile Messenger Pty Ltd. and NewMotion Inc
- **Type:** Telecom service addendum (premium SMS delivery + secondary development services)

## Rate/Pricing Data (unredacted)
| Category | Amount |
|---|---|
| Account setup fee | $1,000 |
| Account support fee | $500 |
| Non-premium MT messages | $0.035/message |
| **Development work** | **$80/hour** |
| Short code setup | $2,000 |
| Short code monthly fee | $1,000 |
| End-user tariff (short code 31000) | $0.99 |
| Test code 28444 tariff | $0.30 |
| Verizon per-received-MT charge | $0.02 |

### Premium SMS Out-Payments — tiered by monthly volume (pricing formula)
| Messages/Month | Per-Message Fee | Plus Fixed |
|---|---|---|
| 1–500,000 | $0.03 | $0 |
| 501,000–1,000,000 | $0.02 | $15,000 |
| 1,000,001–2,000,000 | $0.015 | $21,000 |
| 2,000,001+ | $0.01 | $40,000 |

## Key Commercial Terms
- Short code 31000 across AT&T, Cingular, T-Mobile, Verizon, Sprint, Nextel; throughput 2 msg/sec; latency 30 sec
- Payment: setup + first month on signature; out-payments 14 days after receipt from Network Operators (pay-when-paid construct)
- Trivia application engine included at no charge; adult content prohibited (Exhibit 1 Content Standards); test-code traffic earns no out-payments

## Why useful to TWM
Clean, unredacted example of telecom volume-tier pricing (per-unit rate + fixed step amounts by band), pay-when-paid settlement, carrier-specific surcharges, and a mixed services model with an hourly development rate — pricing-formula patterns TWM's extractors must normalize in telecom vendor agreements.
