---
name: twm-rates-and-money
description: Rules for any code, table or document that holds a rate, price or savings figure. Use before writing or changing anything that stores, converts, aggregates or reports money.
---
# Rates and money

1. Store every rate **as stated**: decimal value, currency, unit (hour or day), and the as-written text. Never convert in place.
2. Conversions are **derived columns** with the reference exchange rate, its source and the observation's effective date recorded beside them. Client reporting currency is a per-deployment setting (CAD for a Canadian bank).
3. Every rate observation carries: effective date, source document and position (`source_ref`), source class (public, consortium, synthetic), extraction confidence, scan quality, raw seniority evidence.
4. **Synthetic never enters the ledger.** Stale data never enters a current benchmark (24-month window, stated on the table).
5. Savings are **stacked, never double counted**: contracted rate first, then the vendor's own best rate for the role, then the market mid-point. A missing reference yields zero and a stated reason, never a guess or a negative.
6. **Observed and projected** are two labelled numbers, never one blended total.
7. Findings are recomputed under new rule versions, never hand-edited; the old set is kept.
8. Say "contracted rate", not "cap".
