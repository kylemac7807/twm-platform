# Review queue — titles the rules could not place (held-out test, October 6, 2026)

**For Kyle.** These 61 distinct titles come from the held-out test (`HELDOUT.md`): sources the Role Framework was never built from. The rules alone could not place them. In production they would go to the model step and then to an analyst; here Claude has drafted the analyst's answer for each. **Confirm, change, or reject each row**, and Claude will codify the confirmed ones into `title_mappings.csv` with you as reviewer. Nothing below is in the table yet. Rows marked *new role?* suggest the framework may be missing a role, not just an alias.

Legend for band: the band the title itself implies; blank means the title states no seniority and the observation's own level evidence decides.

## Deloitte GSA MAS price list (33)

The Deloitte list prices the consulting pyramid, with a practice prefix (IT, Cybersecurity IT, Health IT) and a project-delivery ladder. The prefix is a tech or domain tag, not a role.

| Title | Suggested role | Band | Tag | Note |
|---|---|---|---|---|
| IT Partner/Principal/Director | consulting_director_partner | lead_principal | | |
| IT Sr. Manager | engagement_manager | lead_principal | | consulting "senior manager" grade |
| IT Manager | engagement_manager | senior | | consulting "manager" grade; not the IT-management role |
| IT Sr. Consultant | technology_consultant | senior | | |
| IT Consultant | technology_consultant | intermediate | | |
| IT Analyst | technology_consultant | junior | | consulting "analyst" grade |
| Cybersecurity IT Partner/Principal/Director | consulting_director_partner | lead_principal | cyber | same ladder, cyber practice |
| Cybersecurity IT Sr. Manager | engagement_manager | lead_principal | cyber | |
| Cybersecurity IT Manager | engagement_manager | senior | cyber | |
| Cybersecurity IT Sr. Consultant | technology_consultant | senior | cyber | or security_grc_analyst; the catalogue text decides |
| Cybersecurity IT Consultant | technology_consultant | intermediate | cyber | |
| Cybersecurity IT Analyst | technology_consultant | junior | cyber | |
| Health IT Partner/Principal/Director | consulting_director_partner | lead_principal | health | |
| Health IT Senior Manager | engagement_manager | lead_principal | health | |
| Health IT Manager | engagement_manager | senior | health | |
| Health IT Senior Consultant | technology_consultant | senior | health | |
| Health IT Consultant | technology_consultant | intermediate | health | |
| Health IT Analyst | technology_consultant | junior | health | |
| IT Project Delivery Manager II | project_manager | senior | | |
| IT Project Delivery Manager | project_manager | senior | | |
| IT Project Delivery Specialist | project_coordinator | intermediate | | |
| IT Project Delivery Senior Analyst | project_coordinator | intermediate | | |
| IT Project Delivery Analyst | project_coordinator | junior | | |
| IT Project Delivery Coordinator | project_coordinator | junior | | |
| Cybersecurity IT Project Delivery Manager II | project_manager | senior | cyber | |
| Cybersecurity IT Project Delivery Manager | project_manager | senior | cyber | |
| Cybersecurity IT Project Delivery Specialist | project_coordinator | intermediate | cyber | |
| Cybersecurity IT Project Delivery Senior Analyst | project_coordinator | intermediate | cyber | |
| Cybersecurity IT Project Delivery Analyst | project_coordinator | junior | cyber | |
| Cybersecurity IT Project Delivery Coordinator | project_coordinator | junior | cyber | |
| Project Controller III (Senior Project Controller) | project_coordinator | senior | | PMO controller |
| Project Controller II (Project Controller) | project_coordinator | intermediate | | |
| Project Controller I (Project Analyst) | project_coordinator | junior | | |
| IT Center Associate Lead / Health IT Center Associate Lead | service_desk_analyst | lead_principal | | *uncertain*: "center associate" reads as a delivery-centre staff role; check the catalogue text |

**Two tag decisions hidden in this block.** "cyber" and "health" are not in the tech vocabulary. Cyber is a practice, not a technology; health is an industry. Options: (a) add a small *domain* tag set beside the tech tags (health, public sector, insurance), (b) ignore the prefix. Claude suggests (a), kept separate from technology tags.

## Texas DIR TSS-699 Accenture exhibit (24)

| Title | Suggested role | Band | Tag | Note |
|---|---|---|---|---|
| API Architect Developer | integration_developer | senior | | "architect developer" is Accenture's label for a senior integration developer |
| Advanced Systems Engineer | systems_engineer | senior | | "advanced" as a seniority word |
| Business Intelligence Analyst (BIA) | business_intelligence_analyst | | | now resolves after the acronym fix |
| Senior Business Intelligence Analyst (BIA) | business_intelligence_analyst | senior | | now resolves |
| Business Process Engineer | business_process_analyst | | | |
| Senior Business Process Engineer | business_process_analyst | senior | | |
| Cloud Application Architect | application_architect | | cloud? | or cloud_architect; the SOW text decides. Suggest "cloud" is not a tech tag (aws/azure/gcp are); treat as application_architect |
| Infrastructure Application Architect | infrastructure_architect | | | |
| Cloud ERP Developer | packaged_application_developer | | erp | |
| Creative Director | graphic_designer | lead_principal | | *new role?* creative direction sits in Design & UX; a "design lead" role may be warranted |
| Customer Technical Advisor | technology_consultant | | | |
| Implementation Manager | project_manager | senior | | |
| Project Manager I / Test Leads | project_manager | junior | | combined titles: Accenture prices PM grades I to V with test-role equivalents; suggest a rule: resolve the part before the slash, keep the whole string as the alias |
| Project Manager II / Test Manager | project_manager | intermediate | | |
| Project Manager III / Test Program Manager | project_manager | senior | | |
| Project Manager IV / Product Owner | project_manager | senior | | |
| Project Manager V / Program Manager | program_manager | lead_principal | | |
| SaaS / Low Code Developer | software_developer | | | *new tag?* "low code" (Power Apps, OutSystems, Mendix) is a real platform family; suggest adding tag `low_code` |
| Senior Automation / Performance Tester | test_automation_engineer | senior | | |
| Senior Documentation Specialist | technical_writer | senior | | |
| Senior Manager | engagement_manager | lead_principal | | consulting grade used as a billing title |
| Technical Application Lead | software_developer | lead_principal | | |
| Technical Specialist | *flag* | | | too generic to place without the SOW text; keep flagged |
| Training Specialist | it_trainer | | | |
| Web Security Administrator | security_administrator | | | |
| Web Software Developer | web_developer | | | |

## Texas DIR ITSAC 2020 (1)

| Title | Suggested role | Band | Note |
|---|---|---|---|
| Artificial Intelligence/Machine Learning Engineer | machine_learning_engineer | | the 2024 grid shortened it to "AI/Machine Learning Engineer", which is mapped |

## Canada Job Bank NOC occupations (4)

These are statistical occupation groups, not job titles, so they map to roles for the wage-proxy use only.

| Title | Suggested role | Note |
|---|---|---|
| Software engineers and designers | software_developer | NOC 21231 |
| Software developers and programmers | software_developer | NOC 21232 |
| Cybersecurity specialists | security_analyst | NOC 21220 |
| IT Project Manager (Information systems specialists) | project_manager | NOC 21222 |

## Three generic rules worth adding (Kyle to agree; they are rules, not aliases)

1. **Combined titles with a slash** ("Project Manager II / Test Manager"): resolve the part before the slash, record the whole string as the observed title, and note the alternate. Accenture and others price dual-use grades this way.
2. **Practice prefixes** ("IT", "Cybersecurity IT", "Health IT") on consulting-pyramid grades: strip the prefix, resolve the grade, keep the prefix as a domain tag.
3. **"Advanced" as a seniority word** (Accenture): treat like "senior".

Each would be tested on the held-out set after it is added, and the HELDOUT.md history line updated, so the score stays honest.
