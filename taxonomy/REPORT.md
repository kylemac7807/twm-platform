# Role Framework v0 — Acceptance Report

Generated 2026-09-13 by `python -m twm.taxonomy.acceptance` from `taxonomy/*.csv` and the corpus seed sources.

## Framework size

- Families: **18** (spec draft 16; two added — see Deviations)
- Canonical roles: **130** (target 120–180)
- Band crosswalk rows: **137** across schemes: Consulting pyramid, DDaT, Deloitte CS grade, NY HBITS, SFIA, TBIPS, Texas DIR, Title modifier, UK G-Cloud 15, Years stated
- Tech vocabulary: **56** tags
- Seeded title mappings: **475** (472 active, 3 flagged; target 250–400)

| Family | Roles |
|---|---|
| Software Engineering (`swe`) | 7 |
| Quality Engineering (`qe`) | 5 |
| Data & Analytics (`data`) | 9 |
| AI & Machine Learning (`ai`) | 5 |
| Cloud & Infrastructure (`infra`) | 9 |
| Cybersecurity (`sec`) | 12 |
| Architecture (`arch`) | 12 |
| Delivery Management (`dm`) | 9 |
| Product Management (`pm`) | 3 |
| Business Analysis (`ba`) | 4 |
| Design & UX (`ux`) | 9 |
| IT Service & Operations (`itops`) | 17 |
| Database & Middleware Administration (`dba`) | 6 |
| Networking & Telecom Engineering (`net`) | 6 |
| Packaged Applications (`pkg`) | 5 |
| Consulting & Advisory (`adv`) | 4 |
| Change, Training & Communications (`chg`) | 4 |
| Technology Leadership (`exec`) | 4 |

## Round-trip test (spec acceptance)

Every distinct (observed title, source level) from the seed sources resolved through rules 1–4 + the mapping table. No model or embedding call is involved; anything the rules cannot place is *flagged* for the human queue.

| Source | Distinct titles×levels | Resolved | Ambiguous | Flagged | % resolved |
|---|---|---|---|---|---|
| Canada TBIPS | 252 | 246 | 0 | 6 | 97.6% |
| GSA pricelist CDO Technologies | 7 | 7 | 0 | 0 | 100.0% |
| GSA pricelist Constellation West | 6 | 6 | 0 | 0 | 100.0% |
| GSA pricelist tCognition | 11 | 11 | 0 | 0 | 100.0% |
| NY OGS HBITS 23158 | 124 | 120 | 0 | 4 | 96.8% |
| Texas DIR ITSAC 2024 | 360 | 360 | 0 | 0 | 100.0% |
| UK DDaT ladders | 206 | 206 | 0 | 0 | 100.0% |
| UK G-Cloud 15 | 367 | 367 | 0 | 0 | 100.0% |
| US GSA CALC+ | 22 | 22 | 0 | 0 | 100.0% |
| **All sources** | **1355** | **1345** | **0** | **10** | **99.3%** |

**Target ≥ 90% resolved to exactly one (role, band): 99.3% → PASS.**

How the band was determined for resolved titles:

| band source | count | share |
|---|---|---|
| source_level | 973 | 72.3% |
| source_level_derived | 326 | 24.2% |
| default | 35 | 2.6% |
| title_modifier | 11 | 0.8% |

How the role was matched:

| matched on | count |
|---|---|
| full_title | 1197 |
| core | 148 |

### Flagged titles (for Kyle's review)

**Canada TBIPS**

| observed title | level | why |
|---|---|---|
| Emanations security (TEMPEST) specialist | Level 1 | no rule match; needs model/human resolution |
| Emanations security (TEMPEST) specialist | Level 2 | no rule match; needs model/human resolution |
| Emanations security (TEMPEST) specialist | Level 3 | no rule match; needs model/human resolution |
| Physical IT security specialist | Level 1 | no rule match; needs model/human resolution |
| Physical IT security specialist | Level 2 | no rule match; needs model/human resolution |
| Physical IT security specialist | Level 3 | no rule match; needs model/human resolution |

**NY OGS HBITS 23158**

| observed title | level | why |
|---|---|---|
| IT Specialist | Expert | no rule match; needs model/human resolution |
| IT Specialist | Junior | no rule match; needs model/human resolution |
| IT Specialist | Mid-Level | no rule match; needs model/human resolution |
| IT Specialist | Senior | no rule match; needs model/human resolution |

### Ambiguous titles (2+ candidate roles — each is a disambiguation bug)

None.

### DDaT ladder consistency

Each DDaT role-level label (e.g. *Senior data engineer*, *Head of data science*) was resolved as a free-standing title; it should land on the same canonical role as its parent DDaT role.

| DDaT role | level label | parent resolves to | label resolves to |
|---|---|---|---|
| Service desk manager | Senior service desk analyst | service_desk_manager | service_desk_analyst |
| Service desk manager | Service desk analyst | service_desk_manager | service_desk_analyst |

2 mismatches. Expected where a DDaT ladder spans two TWM roles (DDaT's *Service desk manager* ladder starts at *Service desk analyst*, which TWM keeps as its own role); any other mismatch is a bug.

## Band sanity check (rate monotonicity)

Within each source's rate grid, the mean rate per TWM band must increase junior → intermediate → senior → lead_principal after mapping. Violations mean the band crosswalk disagrees with the money.

| rate grid | junior | intermediate | senior | lead_principal | n | monotonic? |
|---|---|---|---|---|---|---|
| GC15 Deloitte standard UK card by CS grade (GBP/day) | 978 | 1,148 | 1,378 | 1,910 | 14 | yes |
| GC15 UK rate: Accenture (GBP/day) | 795 | 1,061 | 1,215 | 1,862 | 221 | yes |
| GC15 UK rate: Atos (GBP/day) | 738 | 867 | 1,192 | 1,364 | 205 | yes |
| GC15 UK rate: CGI (GBP/day) | 627 | 817 | 969 | 1,299 | 222 | yes |
| GC15 UK rate: Capgemini (GBP/day) | 664 | 728 | 915 | 1,300 | 222 | yes |
| GC15 UK rate: IBM (GBP/day) | 953 | 1,165 | 1,347 | 1,763 | 222 | yes |
| GC15 UK rate: Infosys (GBP/day) | 546 | 688 | 808 | 1,096 | 196 | yes |
| GC15 UK rate: KPMG (GBP/day) | 942 | 1,090 | 1,219 | 1,957 | 215 | yes |
| GC15 UK rate: Kainos (GBP/day) | 1,011 | 1,258 | 1,390 | 1,723 | 222 | yes |
| GC15 UK rate: Kyndryl (GBP/day) | 722 | 776 | 881 | 1,257 | 198 | yes |
| GC15 UK rate: PwC (GBP/day) | 2,533 | 2,977 | 3,417 | 3,662 | 222 | yes |
| GC15 UK rate: TCS (GBP/day) | 588 | 798 | 951 | 1,305 | 222 | yes |
| GC15 UK rate: Version1 (GBP/day) | 577 | 661 | 753 | 1,043 | 222 | yes |
| GC15 offshore rate: Accenture (GBP/day) | 225 | 317 | 394 | 528 | 221 | yes |
| GC15 offshore rate: Atos (GBP/day) | 460 | 577 | 740 | 833 | 193 | yes |
| GC15 offshore rate: Capgemini (GBP/day) | 256 | 353 | 455 | 527 | 222 | yes |
| GC15 offshore rate: IBM (GBP/day) | 419 | 516 | 579 | 724 | 222 | yes |
| GC15 offshore rate: Infosys (GBP/day) | 382 | 428 | 487 | 665 | 196 | yes |
| GC15 offshore rate: KPMG (GBP/day) | 259 | 317 | 399 | 645 | 215 | yes |
| GC15 offshore rate: Kainos (GBP/day) | 796 | 1,040 | 1,251 | 1,404 | 222 | yes |
| GC15 offshore rate: Kyndryl (GBP/day) | 180 | 248 | 312 | 429 | 66 | yes |
| GC15 offshore rate: PwC (GBP/day) | 1,137 | 1,610 | 1,944 | 2,058 | 222 | yes |
| GC15 offshore rate: TCS (GBP/day) | 400 | 543 | 634 | 882 | 222 | yes |
| GC15 offshore rate: Version1 (GBP/day) | 185 | 211 | 252 | 383 | 222 | yes |
| GSA pricelist tCognition (USD/hr, title-modifier bands) | — | 85 | 109 | — | 11 | yes |
| NY HBITS 2026 region 1 (USD/hr) | 44 | 56 | 71 | 82 | 120 | yes |
| NY HBITS 2026 region 2 (USD/hr) | 47 | 61 | 77 | 89 | 120 | yes |
| NY HBITS 2026 region 3 (provisional) (USD/hr) | 47 | 61 | 77 | 89 | 120 | yes |
| Texas DIR 2024 NTE (USD/hr) | 44 | 74 | 98 | 128 | 360 | yes |

All grids monotonic.

## Deviations from the spec draft (with justification)

1. **Two families added (18 vs 16).** `exec` Technology Leadership: G-Cloud 15 and DDaT publish a 'Chief digital and data' category priced as roles (e.g. £3,200/day); C-level titles are roles, not bands, and belong nowhere else. `chg` Change, Training & Communications: TBIPS stream 5 (change management consultant) and Texas DIR (OCM manager, instructor trainer, communications coordinator) both carry adoption/training/comms titles that are not delivery management. Non-IT adoption work bolts on here.
2. **Packaged Applications uses five generic roles** (functional consultant, developer, technical consultant, architect, administrator) with the platform as the tech tag (`sap`, `salesforce`, `servicenow`…), rather than one role per platform × function. The normalizer routes generic cores (developer/consultant/analyst/architect/administrator) into this family whenever a packaged-platform tag is present. **Proposed — Kyle to confirm**; the alternative (platform-named roles such as 'SAP Consultant') is a point-release change: add roles, re-point mappings.
3. **No GIS roles.** TBIPS stream 2 (11 GIS categories) maps to generic roles with tech tag `gis`, per the technology-as-attribute rule.
4. **DDaT level labels derive bands by wording** when not listed in `band_crosswalk.csv` (band_source = `source_level_derived`), rather than enumerating ~150 role-specific labels. The rule: trainee/apprentice/junior/associate → junior; senior → senior; lead/principal/head/chief/manager → lead_principal; otherwise the working level → intermediate.
5. **Default band.** A title with no level evidence and no modifier resolves to `intermediate` with confidence capped at 0.80 and band_source = `default`; the count above shows how often that happened. The ledger stores the raw evidence, so re-banding is always possible.

## Not yet done / v0.1

- O*NET alternate/reported titles and ESCO multilingual synonyms are downloaded but not folded in (spec: v0.1).
- Embedding similarity (rule 5) is a protocol stub; no model is wired. Everything unresolved goes to the flag queue.
- SFIA crosswalk column is intentionally empty (licensing decision pending).
- TBIPS stream 7 (Telecommunications T.1–T.9) titles were not captured in the corpus extraction; they are absent from the seed.
- G-Cloud 14 cards, Job Bank wages and the contract corpus are not used for the round-trip (spec lists the five seed sources); they are the natural next stress test.
