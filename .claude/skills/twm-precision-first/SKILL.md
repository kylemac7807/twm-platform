---
name: twm-precision-first
description: Abstain, flag, never guess. Apply whenever any TWM component or script must decide something it is not certain of: a field, a title, a location, a link, a match, a number.
---
# Precision first: abstain, flag, never guess

Why: a false leakage claim in front of a vendor can lose the engagement and the consortium (architecture decision 5). A missed finding is caught at the next refresh. So every component prefers a blank plus a flag over a plausible guess.

Do this, in every component:
1. If a value is uncertain, leave it empty and set the flag for that kind of value (`needs_band_review`, `needs_location_review`, extraction confidence below the floor, `status=flagged`).
2. Record why in the notes field, in one sentence a consultant can read.
3. Never fill a default. No "intermediate" seniority, no "onshore", no nearest role, no rounded number. (Kyle, Sept 19 and Oct 6, 2026.)
4. Money is gated by confidence: rows below the threshold are kept and visible but excluded from benchmark distributions and savings totals until an analyst confirms them.
5. Extracted numbers must literally appear in the source text at the claimed position; otherwise reject them.

Do not: invent, interpolate, or "lean toward" an answer because it is likely. Likely is not evidence.
