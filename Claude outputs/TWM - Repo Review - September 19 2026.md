# twm-platform — Cowork Review, September 19, 2026

**Reviewed:** the repo at `Desktop\twm-platform` (6 commits, last `00acfd5`), read directly on Kyle's machine. **Scope:** M0/M1 outputs, code, tests, docs, repo hygiene — checked against the decisions in the requirements doc and CLAUDE.md.

## Verdict

M1 is a strong, faithful build. Every design rule we settled is present **and enforced by tests**, not just documented: four bands; technology as attribute (56-tag vocabulary; a test fails if a technology appears in a role name outside Packaged Applications); SFIA crosswalk column empty (tested); raw evidence stored per mapping (`attr_level_code_raw`, `attr_years_raw`); mapping table that refuses silent overwrite (deprecate first); unknown titles flagged, never guessed. The band crosswalk was validated the right way — **against money**: mean rate rises junior → lead-principal in all 29 public rate grids. Deviations from the spec are documented with reasons and correctly logged as Proposed. The new `corpus-sources-and-demo-set.md` is good product thinking: five public documents chosen so the follow-the-contract demo falls out of the build. Claude Code also solved the Texas DIR CDN block itself (`widen_recover.py`) — 26 documents recovered.

## Decisions for Kyle (three)

1. **Accept the two added families** — Technology Leadership (`exec`) and Change, Training & Communications (`chg`). Both are real categories in the sources (G-Cloud/DDaT price C-level roles separately; TBIPS stream 5 and Texas carry OCM/trainer/comms titles) and `exec` is exactly our "management tiers are roles, not bands" rule. *Recommend: accept.*
2. **Accept Packaged Applications as five generic roles + platform tech tag** (not "SAP Consultant"-style roles). This is the Sept 13 technology-as-attribute decision applied; reverting later is a point release. *Recommend: accept.*
3. **Default-band policy — a real design point the build surfaced.** When a title carries no level evidence (35 cases, 2.6%), v0 assigns *intermediate* at confidence 0.80 — above the 0.75 flag floor, so it flows through as active. That fabricates seniority from no evidence, which contradicts "coarse-but-observable" and the precision-first principle: a defaulted band inside a benchmark cut is an invented data point. *Recommend:* accept the role, leave the band **unbanded**; exclude `band_source=default` from band-level cuts and route band-only to the review queue. Cheap to change now, expensive after client data lands.

## Findings by severity

**Medium — the 99.3% is a consistency check, not a generalization test.** The mapping table was seeded from the same five sources the round-trip resolves; 1,197 of 1,345 hits are exact full-title matches. Only the 148 "core" matches show the *rules* generalizing. Before M2 leans on the normalizer, run a **held-out** test on sources not in the seed: the 12 G-Cloud 14 cards, Job Bank titles, and the ~40 Accenture titles in the Texas TSS-699 pricing exhibit. Claude Code already lists this as the "natural next stress test" — make it M1.1 and gate M2 on the number.

**Medium — "onshore" is absolute in the code; it must be client-relative.** `normalize.py` maps UK/US/Canada tokens to `onshore`. For a Canadian bank, a US resource is nearshore. Onshore = same country as the client, configured per deployment. Small change, but it will corrupt Canadian benchmark cuts if it survives to M2.

**Low — crosswalk internal disagreement.** *Years stated* puts 5–7 years at intermediate and 7–12 at senior; NY HBITS puts 60–84 months (5–7 years) at senior; TBIPS L3 (10+) at senior while *Years* 12+ is lead-principal. The precedence rule (source level > years) hides this operationally, and precedence is right — published labels are what vendors price against. But the years table should be reconciled once (or documented as the fallback it is) so two readings of the same evidence can't both be "correct."

**Low — consulting-pyramid bands are unvalidated heuristics** (the notes say so). The Oklahoma/Deloitte card on disk (Partner $350 → Consultant $150) and the Deloitte G-Cloud grade card can validate them the same way the other grids were validated.

**Low — 126 of 475 mappings are authored aliases, not observed titles.** Legitimate, but label them as a source class (`authored` vs `observed`) so coverage statistics aren't inflated; the honest observed count is 349.

**Low — numbers drift between documents.** REPORT.md says 99.3%; CLAUDE.md and requirements §3.5 say 98%. Sync to the report.

## Repo hygiene

- **Uncommitted whitespace-only diffs** on two manifest CSVs (363 lines each) — line-ending churn from Windows. Add a `.gitattributes` (`* text=auto`, `*.csv text eol=lf`) and commit once; otherwise every touch of a CSV produces an unreadable diff.
- `docs/requirements-and-rationale.md` has §3.5 inserted before §3.4 — renumber. The project's canonical copy now carries §3.5 and the M1 decision-log rows (merged Sept 19, with the default-band item added as Proposed), so the two copies are in sync again except for that ordering.
- `docs/corpus-missing-originals.md` is dated Sept 13 and still shows Contracts Finder at 40/48; the 429s were only rate-limited — **re-run `v3_download.py` now** (six days later) before anyone hand-fetches them.
- `.pytest_cache/lastfailed` is empty — all 29 tests passed at last run. Good.

## What is genuinely good here

The disambiguation notes on canonical roles are written *for the model* ("choose programmer_analyst only when the title says programmer/analyst…") — exactly what the resolve-once call needs and rarely done well. The band-precedence rule is explicit in code, documented, and tested (`test_source_level_beats_title_modifier`, `test_years_beat_modifier_and_default`). The mapping table's `append()` raising on an active duplicate is the versioning discipline we asked for, made mechanical.

## Next

M1.1 (held-out test + onshore fix + default-band policy once Kyle decides) → M2 thin thread. The Deloitte MiIntegrate contract for M2 is still the top manual download; the demo set gives M2 its first document either way (the Accenture G-Cloud card).
