# Role Framework v0 — Build Specification

Deliverable: four CSVs under `taxonomy/`, plus `taxonomy/REPORT.md` with the ambiguity-rate results. Everything versioned in git; mappings append/deprecate, never silently edit.

## Table 1 — `role_families.csv`

Columns: `family_id, name, definition, scope_notes`

Draft family list (adjust with justification, don't silently drop):

1. Software Engineering
2. Quality Engineering (QA, test automation)
3. Data & Analytics (data engineering, BI, analysts)
4. AI & Machine Learning
5. Cloud & Infrastructure (platform, DevOps/SRE, middleware ops)
6. Cybersecurity
7. Architecture (enterprise, solution, domain)
8. Delivery Management (PM, program, scrum master, agile coach, PMO)
9. Product Management
10. Business Analysis
11. Design & UX
12. IT Service & Operations (helpdesk, desktop, service management)
13. Database & Middleware Administration
14. Networking & Telecom Engineering
15. Packaged Applications (SAP, Salesforce, Guidewire, Workday, ServiceNow specialists)
16. Consulting & Advisory (Partner / Engagement Manager / Consultant genus — distinct band logic)

Structure so future non-IT families (Operations, Contact Centre) bolt on without change.

## Table 2 — `canonical_roles.csv`

Columns: `role_id, family_id, name, definition, disambiguation_notes, crosswalk_ddat, crosswalk_tbips, crosswalk_onet_soc, crosswalk_sfia` (leave `crosswalk_sfia` empty — licensing pending)

Target ~120–180 roles. Build by reconciling: DDaT role list (fetch from ddat-capability-framework.service.gov.uk), TBIPS resource categories (canada.ca TBIPS categories page), Texas DIR job titles (Appendix D), G-Cloud 15 card taxonomies (`corpus/gc15_ratecards/`), GSA labor categories. `disambiguation_notes` is what the resolve-once model reads — write it for a model deciding between neighbours ("Systems Analyst vs Business Analyst: systems analyst specifies technical solutions…").

Technology is NOT in the role name unless the technology is the practice (Packaged Applications family): "Software Developer" not "Java Developer"; but "SAP Consultant" is a role (still tech-tagged `sap`).

## Table 3 — `band_crosswalk.csv`

Columns: `source_scheme, source_level, twm_band, notes`

TWM bands: `junior | intermediate | senior | lead_principal`. Draft mappings to validate against rate data (flag rows where the money disagrees with the mapping):

| Source | Level | TWM band |
|---|---|---|
| TBIPS | L1 (<5 yrs) | junior |
| TBIPS | L2 (5–10 yrs) | intermediate |
| TBIPS | L3 (10+ yrs) | senior |
| Texas DIR | Intern 1–3 | junior |
| Texas DIR | Level 1 | intermediate |
| Texas DIR | Level 2 | senior |
| Texas DIR | Level 3 | lead_principal |
| SFIA | 1–2 | junior |
| SFIA | 3 | intermediate |
| SFIA | 4–5 | senior |
| SFIA | 6–7 | lead_principal |
| DDaT | junior/associate | junior |
| DDaT | mid | intermediate |
| DDaT | senior | senior |
| DDaT | lead/principal/head-of | lead_principal |
| Years stated | <3 | junior |
| Years stated | 3–7 | intermediate |
| Years stated | 7–12 | senior |
| Years stated | 12+ | lead_principal |

NY HBITS (4 levels) and G-Cloud 15 seniority labels: derive from their published definitions during build. These are heuristics — keep the raw source level on every observation (evidence rule), so re-banding is always possible.

## Table 4 — `title_mappings.csv` (the seeded mapping table)

Columns: `observed_title, source, source_url, canonical_role_id, twm_band, attr_technology, attr_location, attr_level_code_raw, attr_years_raw, confidence, method (rule|model|human), reviewer, status (active|flagged|deprecated), version_added`

Seed sources (re-fetchable URLs are in corpus manifests / catalog): Texas DIR titles×levels (~60 titles), NY HBITS titles (~31), TBIPS categories (~93), all 13 G-Cloud 15 vendor card taxonomies, GSA pricelist labor categories. Expect ~250–400 rows.

Normalization rules to implement (in `src/twm/pipeline/normalize.py`) before any model call:
1. Strip and capture seniority modifiers: Sr/Senior/Jr/Junior/Lead/Principal/Staff, roman numerals I–V, trailing digits, "Level N".
2. Strip and capture location tokens: onshore/offshore/nearshore/remote, city/country names.
3. Strip and capture technology tokens against the controlled vocabulary (`taxonomy/tech_vocab.csv` — create it, ~40–60 tags, with aliases: "COBOL"→mainframe, ".NET"/"C#"→dotnet…).
4. Exact/alias match against existing mappings → deterministic hit.
5. No match → embedding similarity against resolved titles (threshold TBD, start 0.85 cosine on a strong embedding model) → candidate + model confirmation.
6. Still unresolved or confidence < 0.75 → status=flagged, human queue.

## Acceptance test (`taxonomy/REPORT.md`)

Round-trip EVERY observed title from the seed sources through the rules+table:
- % resolved to exactly one (role, band) — target ≥90%
- % flagged — list them all for Kyle's review
- % ambiguous (2+ candidates) — each is a disambiguation_notes bug; fix or flag
- Band sanity check: within each source's rate grid, mean rate must increase monotonically junior→lead_principal after mapping; violations listed.

## v0.1 (after Kyle runs framework downloads)

Fold in O*NET alternate/reported titles (tens of thousands of synonyms → bulk `method=rule` mappings at family/role level with confidence tiers) and ESCO multilingual (French titles priority — Canadian bilingual documents). No structural change permitted in a point release.
