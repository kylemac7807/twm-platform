---
name: twm-flag-then-codify
description: How TWM turns an analyst's judgment into a reusable rule. Use when designing or implementing any place where the platform cannot decide and a human must: titles, locations, document links, person matches, discrepancy types.
---
# Flag, analyst decides, then codify

The pattern (decided Sept 19, 2026 for locations; applies everywhere):
1. The platform recognizes it cannot decide and **flags** the item with the evidence it has (e.g. city and country, candidate roles, candidate documents) and, where useful, a **non-binding suggestion** clearly marked as a hint.
2. An **analyst decides once**, with a reason, in the workbench queue.
3. The decision is **codified**: written to a rules table (`taxonomy/title_mappings.csv`, `taxonomy/location_rules.csv`, document links, person matches) with who decided, when, and why.
4. Every later occurrence for that client is a **deterministic lookup**. The platform never asks the same question twice for the same client.
5. Rules are **appended or deprecated, never edited**, so history survives.

Kyle's domain examples (New York, Buffalo, Toronto) are illustrations of judgment, not rules to hard-code. Never turn an example into a constant.
