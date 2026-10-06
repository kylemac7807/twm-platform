# Role Framework v0 — Held-out generalization test

Generated 2026-10-06 by `python -m twm.taxonomy.heldout`. Titles from sources **not used to seed the mapping table**, resolved by the rules and the existing table with no additions. This is the honest test the acceptance report (a same-source consistency check) is not.

| Source | Titles | Role + band | Role only (unbanded) | Ambiguous | Flagged | % role resolved |
|---|---|---|---|---|---|---|
| Canada Job Bank NOC occupations | 4 | 0 | 4 | 0 | 0 | 100.0% |
| Deloitte GSA MAS price list | 35 | 35 | 0 | 0 | 0 | 100.0% |
| Texas DIR ITSAC 2020 (titles not in 2024) | 24 | 24 | 0 | 0 | 0 | 100.0% |
| Texas DIR TSS-699 Accenture exhibit | 50 | 25 | 21 | 3 | 1 | 92.0% |
| **All** | **113** | **84** | **25** | **3** | **1** | **96.5%** |

**Role resolved on unseen titles: 96.5%** (acceptance report on seed sources: 99.3%). Unbanded is expected here: most of these sources state no seniority level, so the title modifier is the only evidence.

**History.** First run, Oct 6, 2026, before any change: **37.4%** of 115 titles. Two generic rule fixes the same day (seniority words in the middle of a title such as "IT Sr. Manager"; all-caps bracketed acronyms such as "(BIA)" dropped) and two junk rows removed from the Texas extraction gave the figure above. No title-specific aliases were added: that would turn a held-out test back into a consistency check. The flagged titles go to Kyle's review queue (`taxonomy/review-queue-heldout.md`) and are codified only after he decides. **Later the same day** Kyle reviewed all 65 rows in Word; 51 confirmed rows were codified with him as reviewer (method `human`, version 0.1) and one kept flagged, after which the figure above applies. From that point the titles he confirmed are no longer held out; the figure now measures the rules **plus the analyst queue**, which is how production works. The remaining flags are the rows he questioned (consulting Manager and Analyst grades, slash-combined project-manager/test titles, IT Center Associate Lead).

How the role was matched (unseen titles can only hit by full-title coincidence, by the stripped core, or by a role name):

| matched on | count |
|---|---|
| full_title | 96 |
| core | 13 |

## Examples of correct-looking resolutions (spot-check these)

**Canada Job Bank NOC occupations**

| title | role | band | tech | via |
|---|---|---|---|---|
| Software engineers and designers | software_developer | unbanded |  | full_title |
| Software developers and programmers | software_developer | unbanded |  | full_title |
| Cybersecurity specialists | security_analyst | unbanded |  | full_title |
| IT Project Manager (Information systems specialists) | project_manager | unbanded |  | full_title |

**Deloitte GSA MAS price list**

| title | role | band | tech | via |
|---|---|---|---|---|
| Cybersecurity IT Partner/Principal/Director | consulting_director_partner | lead_principal |  | full_title |
| Cybersecurity IT Sr. Manager | technology_consultant | lead_principal |  | full_title |
| Cybersecurity IT Manager | technology_consultant | senior |  | full_title |
| Cybersecurity IT Sr. Consultant | technology_consultant | senior |  | full_title |
| Cybersecurity IT Consultant | technology_consultant | intermediate |  | full_title |
| Cybersecurity IT Analyst | technology_consultant | junior |  | full_title |

**Texas DIR ITSAC 2020 (titles not in 2024)**

| title | role | band | tech | via |
|---|---|---|---|---|
| Artificial Intelligence/Machine Learning Engineer | machine_learning_engineer | junior |  | full_title |
| Artificial Intelligence/Machine Learning Engineer | machine_learning_engineer | junior |  | full_title |
| Artificial Intelligence/Machine Learning Engineer | machine_learning_engineer | junior |  | full_title |
| Artificial Intelligence/Machine Learning Engineer | machine_learning_engineer | intermediate |  | full_title |
| Artificial Intelligence/Machine Learning Engineer | machine_learning_engineer | senior |  | full_title |
| Artificial Intelligence/Machine Learning Engineer | machine_learning_engineer | lead_principal |  | full_title |

**Texas DIR TSS-699 Accenture exhibit**

| title | role | band | tech | via |
|---|---|---|---|---|
| API Architect Developer | integration_developer | senior |  | full_title |
| Advanced Systems Engineer | systems_engineer | senior |  | full_title |
| Application Architect | application_architect | unbanded |  | full_title |
| Business Consultant | management_consultant | unbanded |  | full_title |
| Business Intelligence Analyst (BIA) | business_intelligence_analyst | unbanded |  | full_title |
| Business Process Engineer | business_process_analyst | unbanded |  | full_title |

## Flagged titles (the rules could not place these; each is a candidate alias, role or rule)

**Texas DIR TSS-699 Accenture exhibit** (1)

- Technical Specialist

## Reading this

- A flagged title is not a failure of the product: in production it goes to the model step (similarity search plus model confirmation, decided Oct 6) and then to the analyst queue, and the answer is kept. The number above is what the *rules alone* achieve on cold titles, which is the floor.
- The gap between this and the acceptance score is the value the model step and the volume run must supply, and the evaluation harness (M3) will measure.
