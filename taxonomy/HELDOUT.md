# Role Framework v0 — Held-out generalization test

Generated 2026-10-06 by `python -m twm.taxonomy.heldout`. Titles from sources **not used to seed the mapping table**, resolved by the rules and the existing table with no additions. This is the honest test the acceptance report (a same-source consistency check) is not.

| Source | Titles | Role + band | Role only (unbanded) | Ambiguous | Flagged | % role resolved |
|---|---|---|---|---|---|---|
| Canada Job Bank NOC occupations | 4 | 0 | 0 | 0 | 4 | 0.0% |
| Deloitte GSA MAS price list | 35 | 1 | 1 | 0 | 33 | 5.7% |
| Texas DIR ITSAC 2020 (titles not in 2024) | 24 | 18 | 0 | 0 | 6 | 75.0% |
| Texas DIR TSS-699 Accenture exhibit | 50 | 14 | 12 | 0 | 24 | 52.0% |
| **All** | **113** | **33** | **13** | **0** | **67** | **40.7%** |

**Role resolved on unseen titles: 40.7%** (acceptance report on seed sources: 99.3%). Unbanded is expected here: most of these sources state no seniority level, so the title modifier is the only evidence.

**History.** First run, Oct 6, 2026, before any change: **37.4%** of 115 titles. Two generic rule fixes the same day (seniority words in the middle of a title such as "IT Sr. Manager"; all-caps bracketed acronyms such as "(BIA)" dropped) and two junk rows removed from the Texas extraction gave the figure above. No title-specific aliases were added: that would turn a held-out test back into a consistency check. The flagged titles go to Kyle's review queue (`taxonomy/review-queue-heldout.md`) and are codified only after he decides.

How the role was matched (unseen titles can only hit by full-title coincidence, by the stripped core, or by a role name):

| matched on | count |
|---|---|
| full_title | 31 |
| core | 15 |

## Examples of correct-looking resolutions (spot-check these)

**Deloitte GSA MAS price list**

| title | role | band | tech | via |
|---|---|---|---|---|
| IT Sr. Manager | it_manager | senior |  | core |
| IT Manager | it_manager | unbanded |  | full_title |

**Texas DIR ITSAC 2020 (titles not in 2024)**

| title | role | band | tech | via |
|---|---|---|---|---|
| Enterprise Resource Planning (ERP) Business Analyst | packaged_application_functional_consultant | junior | erp | full_title |
| Enterprise Resource Planning (ERP) Business Analyst | packaged_application_functional_consultant | junior | erp | full_title |
| Enterprise Resource Planning (ERP) Business Analyst | packaged_application_functional_consultant | junior | erp | full_title |
| Enterprise Resource Planning (ERP) Business Analyst | packaged_application_functional_consultant | intermediate | erp | full_title |
| Enterprise Resource Planning (ERP) Business Analyst | packaged_application_functional_consultant | senior | erp | full_title |
| Enterprise Resource Planning (ERP) Business Analyst | packaged_application_functional_consultant | lead_principal | erp | full_title |

**Texas DIR TSS-699 Accenture exhibit**

| title | role | band | tech | via |
|---|---|---|---|---|
| Application Architect | application_architect | unbanded |  | full_title |
| Business Consultant | management_consultant | unbanded |  | full_title |
| Business Intelligence Analyst (BIA) | business_intelligence_analyst | unbanded |  | full_title |
| Business Systems Analyst | business_analyst | unbanded |  | full_title |
| Data Analyst | data_analyst | unbanded |  | full_title |
| Data Engineer | data_engineer | unbanded |  | full_title |

## Flagged titles (the rules could not place these; each is a candidate alias, role or rule)

**Canada Job Bank NOC occupations** (4)

- Software engineers and designers
- Software developers and programmers
- Cybersecurity specialists
- IT Project Manager (Information systems specialists)

**Deloitte GSA MAS price list** (33)

- Cybersecurity IT Partner/Principal/Director
- Cybersecurity IT Sr. Manager
- Cybersecurity IT Manager
- Cybersecurity IT Sr. Consultant
- Cybersecurity IT Consultant
- Cybersecurity IT Analyst
- Cybersecurity IT Project Delivery Manager II
- Cybersecurity IT Project Delivery Manager
- Cybersecurity IT Project Delivery Specialist
- Cybersecurity IT Project Delivery Senior Analyst
- Cybersecurity IT Project Delivery Analyst
- Cybersecurity IT Project Delivery Coordinator
- IT Partner/Principal/Director
- IT Sr. Consultant
- IT Consultant
- IT Analyst
- Project Controller III (Senior Project Controller)
- Project Controller II (Project Controller)
- Project Controller I (Project Analyst)
- IT Project Delivery Manager II
- IT Project Delivery Manager
- IT Project Delivery Specialist
- IT Project Delivery Senior Analyst
- IT Project Delivery Analyst
- IT Project Delivery Coordinator
- IT Center Associate Lead
- Health IT Partner/Principal/Director
- Health IT Senior Manager
- Health IT Manager
- Health IT Senior Consultant
- Health IT Consultant
- Health IT Analyst
- Health IT Center Associate Lead

**Texas DIR ITSAC 2020 (titles not in 2024)** (6)

- Artificial Intelligence/Machine Learning Engineer
- Artificial Intelligence/Machine Learning Engineer
- Artificial Intelligence/Machine Learning Engineer
- Artificial Intelligence/Machine Learning Engineer
- Artificial Intelligence/Machine Learning Engineer
- Artificial Intelligence/Machine Learning Engineer

**Texas DIR TSS-699 Accenture exhibit** (24)

- API Architect Developer
- Advanced Systems Engineer
- Business Process Engineer
- Cloud Application Architect
- Cloud ERP Developer
- Creative Director
- Customer Technical Advisor
- Implementation Manager
- Infrastructure Application Architect
- Project Manager I / Test Leads
- Project Manager II / Test Manager
- Project Manager III / Test Program Manager
- Project Manager IV / Product Owner
- Project Manager V / Program Manager
- SaaS / Low Code Developer
- Senior Automation / Performance Tester
- Senior Business Process Engineer
- Senior Documentation Specialist
- Senior Manager
- Technical Application Lead
- Technical Specialist
- Training Specialist
- Web Security Administrator
- Web Software Developer

## Reading this

- A flagged title is not a failure of the product: in production it goes to the model step (similarity search plus model confirmation, decided Oct 6) and then to the analyst queue, and the answer is kept. The number above is what the *rules alone* achieve on cold titles, which is the floor.
- The gap between this and the acceptance score is the value the model step and the volume run must supply, and the evaluation harness (M3) will measure.
