# TWM Corpus — 01 Skills Frameworks: Acquisition Manifest

Date: 2026-09-01. Researcher: Claude (research session for Kyle McNamara / TWM).

**IMPORTANT STATUS NOTE:** This research session ran inside a sandbox whose egress
proxy denies direct HTTPS downloads to all external hosts (curl/wget CONNECT → 403
policy denial; confirmed via the agent-proxy status log). Web research tools worked,
so every source below was located and verified on the **official issuer's site**, with
exact download URLs and licensing terms captured. **No binary files could be saved in
this environment.** Run `fetch_frameworks.sh` (in this directory) from any normal
machine to pull the whole queue in one pass, then verify per the checklist at the end.

---

## A. Verified download queue (public, no login — blocked only by this sandbox)

### 1. O*NET Database 31.0 — U.S. Dept of Labor / O*NET Center
- Issuer: National Center for O*NET Development, USDOL/ETA. Located via https://www.onetcenter.org/database.html
- Full Excel archive (all ~35 files): https://www.onetcenter.org/dl_files/database/db_31_0_excel.zip
- Key individual files (pattern `https://www.onetcenter.org/dl_files/database/db_31_0_excel/<Name>.xlsx`):
  - `Occupation Data.xlsx` — SOC-based occupation titles + descriptions
  - `Job Titles.xlsx` — alternate/lay job titles per occupation (v31.0 successor to "Alternate Titles"; THE key file for vendor-title → occupation matching)
  - `Sample of Reported Titles.xlsx` — incumbent-reported titles
  - `Essential Skills.xlsx`, `Transferable Skills.xlsx` — skill ratings per occupation (31.0 skills model)
  - `Software Skills.xlsx` — technology/software (e.g., Java, AWS) per occupation ("hot technology" flags)
  - `Knowledge.xlsx`, `Abilities.xlsx`, `Work Activities.xlsx`
- File dictionary: https://www.onetcenter.org/dictionary/31.0/excel/
- Why useful: the largest public title-synonym corpus (tens of thousands of alternate titles mapped to occupations) plus per-occupation skill/technology vectors — ideal training/seed data for mapping raw vendor role titles.
- License: **CC BY 4.0** — commercial use permitted with attribution to "O*NET 31.0 Database, U.S. Department of Labor, Employment and Training Administration". No fees. O*NET® is a registered trademark (don't imply endorsement).

### 2. NICE Workforce Framework for Cybersecurity — NIST
- SP 800-181 Rev.1 PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-181r1.pdf (DOI: 10.6028/NIST.SP.800-181r1)
- NICE Framework Components **v2.2.0** (current, Apr 2026):
  - JSON (direct): https://csrc.nist.gov/csrc/media/Projects/cprt/documents/nice/v2-2-0_nf_components.json
  - XLSX (via landing page): https://www.nist.gov/document/nice-framework-components-v220
  - Index of current versions: https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/nice-framework-current-versions
- Why useful: 50+ cyber work roles decomposed into Task/Knowledge/Skill statements with stable IDs — a ready-made role→skill matrix for the security slice of the taxonomy.
- License: **US Government work — public domain (17 U.S.C. §105)**. Free commercial use; attribution is good practice.

### 3. UK Government Digital and Data capability framework (formerly DDaT) — CDDO/GDS
- Framework site (redirect target of the gov.uk collection page): https://ddat-capability-framework.service.gov.uk/
- CSV export page: https://ddat-capability-framework.service.gov.uk/download — three CSVs (timestamped S3 exports, links rotate; re-grab from this page):
  - "Role and skill content" (~2.3 MB): role families, roles, role levels, required skills, skill proficiency levels
  - "Skills Content" (~198 KB): skill definitions + proficiency-level descriptors (awareness→expert)
  - "Changelog" (~73 KB)
- 53 roles in 8 families (software development, architecture ×7, data ×9, IT operations ×12, product & delivery, QA testing, user-centred design, chief digital roles); each role has multi-level definitions (e.g., junior/mid/senior/lead/principal developer) — an excellent public seniority-ladder model with skills-at-level.
- License: **Open Government Licence v3.0** — free commercial use with attribution ("Contains public sector information licensed under OGL v3.0").

### 4. ENISA European Cybersecurity Skills Framework (ECSF)
- Role Profiles PDF (direct): https://www.enisa.europa.eu/sites/default/files/publications/European%20Cybersecurity%20Skills%20Framework%20Role%20Profiles.pdf
- User Manual + landing: https://www.enisa.europa.eu/topics/skills-and-competences/skills-development/european-cybersecurity-skills-framework-ecsf
- 12 cybersecurity role profiles (title, alt titles, mission, tasks, skills, knowledge, e-CF mapping) — bridges e-CF and cyber roles; complements NICE with EU vocabulary.
- License: ENISA publications are free to reproduce with source acknowledgement (most under CC BY 4.0 — check the PDF's imprint page on download).

### 5. CEN ICT Professional Role Profiles — CWA 16458 (free CWA PDFs from CEN-CENELEC)
- CWA 16458-1:2018 (30 European ICT role profiles, e-CF-mapped): https://www.cencenelec.eu/media/CEN-CENELEC/AreasOfWork/CEN%20sectors/Digital%20Society/CWA%20Download%20Area/ICT_SkillsWS/16458-1.pdf
- CWA 16458-2 (user guides) and 16458-4 (case studies): https://www.cencenelec.eu/media/CEN-CENELEC/AreasOfWork/CEN%20sectors/Digital%20Society/CWA%20Download%20Area/ICT_SkillsWS/16458-2.pdf and .../16458-4.pdf (part 2 also mirrored at https://itprofessionalism.org/wp-content/uploads/2025/03/ICT-professionals-role-profiles-Pt-2-CWA-16458-2-User-guides.pdf)
- Browse the whole free CWA area (also holds legacy e-CF 3.0 CWA 16234 parts): CEN "ICT Skills Workshop" download area under https://www.cencenelec.eu/ → CWA Download Area → ICT_SkillsWS
- Why useful: 30 canonical European ICT role profiles (Developer, Systems Architect, DevOps Expert, etc.) each mapped to e-CF competences + proficiency levels — the free on-ramp to the e-CF world.
- License: CWAs in the CEN free-download area are free to download/use; CEN copyright applies — reproduction/redistribution beyond internal use needs CEN permission (flag for embedding text verbatim in a product).

### 6. Singapore Skills Framework for Infocomm Technology (IMDA/SkillsFuture)
- Consolidated career maps PDF (direct, IMDA): https://www.imda.gov.sg/-/media/imda/images/programmes/skills-framework-for-ict/consolidated-career-maps.pdf
- Portal with per-role skills maps (title, tasks, technical skills + proficiency 1–6): https://www.skillsfuture.gov.sg/skills-framework/ict
- Why useful: ~100+ ICT job roles with explicit seniority tracks and skill-proficiency levels; strong third reference point (APAC) alongside SFIA/e-CF.
- License: Singapore Government material — free for personal/non-commercial informational use by default; commercial redistribution should be cleared with IMDA (info@imda.gov.sg). Treat as reference/dev corpus, not redistributable content.

---

## B. Leads NOT downloadable without registration/licensing (Kyle action needed)

### SFIA 9 — Skills Framework for the Information Age (THE intended backbone)
- Docs page: https://sfia-online.org/en/sfia-9/documentation — SFIA 9 framework reference (PDF), About SFIA (PDF), visual chart (PDF), **full Excel spreadsheet** (all 147 skills × 7 levels + generic attributes), RDF/Turtle file, cyber & cloud views.
- All downloads require **free registration + login** ("All the documents are free to get if you are registered on this site"). Browsable without login: skills A–Z (https://sfia-online.org/en/sfia-9/skills/all-skills-a-z), levels of responsibility (https://sfia-online.org/en/sfia-9/responsibilities).
- **ACTION: Kyle registers (free) at sfia-online.org and downloads the PDF + Excel + RDF.** Registration grants a personal-use licence.
- **LICENSING — CRITICAL FOR TWM (commercial use):**
  - Free: personal career development; most *internal* corporate HR/workforce use.
  - **Fee-bearing (per https://sfia-online.org/en/about-sfia/licensing-sfia):** "using SFIA to support the sale or marketing of any product or service", rate cards, recruitment-as-a-service, redistribution of SFIA material to other organisations, large-organisation internal use, translations.
  - TWM's use (embedding SFIA in a commercial SaaS for clients) ⇒ **SFIA Partner Licence** (https://sfia-online.org/en/about-sfia/licensing-sfia/accredited-partners-licence-new): annual base fee **£2,000 single-country / £4,000 global**, plus **5% royalty on products dependent on SFIA data**; obligation to keep public mappings accurate/current and to use SFIA Accredited Consultants for relevant activities (accreditation: £200 assessment + £300/yr consultant). Apply via the SFIA Foundation Business Administrator.
  - Fee pages: .../standard-fees, .../pay-for-a-licence, .../ratecard-licences, .../corporate-user-licence.
  - Budget flag: at TWM's stage this is cheap relative to value, but the **5% royalty** wording needs legal review — clarify with SFIA Foundation what "dependent on SFIA data" means for a taxonomy that is *seeded from* but not *reproducing* SFIA.

### ESCO v1.2.1 (EU occupations/skills, incl. ICT)
- Download portal: https://esco.ec.europa.eu/en/use-esco/download — free, **no account**, but requires an interactive flow: choose version (v1.2.1)/content/language/format (CSV), accept terms, enter an email, receive download link by mail. Not automatable from here.
- **ACTION: Kyle runs the 2-minute email flow (select "classification", CSV, EN).** Also free Local API package via same portal; live API: https://ec.europa.eu/esco/api (docs: https://ec.europa.eu/esco/api/doc/esco_api_doc.html).
- License: **EUPL 1.2 — commercial use permitted**; attribute "© European Union, ESCO". ~3,000 occupations / ~13,900 skills with rich non-preferred-term (synonym) lists — second-best title-synonym source after O*NET, and the best multilingual one.

### e-CF / EN 16234-1 (European e-Competence Framework, current v4.x)
- The current EN 16234-1 standard text is a **paid purchase** from CEN national standards bodies (e.g., BSI, NEN; typically €100–200). Overview/materials: https://itprofessionalism.org and https://www.ecompetences.eu (the latter 403'd our fetcher but is the official e-CF site; free e-CF 3.0-era PDFs historically hosted there and in the CEN CWA area above).
- ACTION (optional): buy EN 16234-1 from a national standards body if e-CF becomes a formal mapping axis; the free CWA 16458 profiles + ECSF give most of the practical content meanwhile.

### Government of Canada IT classification (lower priority)
- IT qualification standard (HTML): https://www.canada.ca/en/treasury-board-secretariat/services/staffing/qualification-standards/core.html (IT group; CS→IT conversion notes at TBS). Mostly education/certification gates, not a skills matrix — modest taxonomy value.
- Related: Canada National Occupational Standard for Cybersecurity Workforce (Digital Governance Standards Institute via https://scc-ccn.ca) — check availability.
- Canada Crown copyright: non-commercial reproduction permitted; commercial reuse requires permission — another reason this stays low priority.

---

## C. Verification checklist (run after fetching)
For each file: `file <f>`; PDFs: `pdftotext <f> - | head -30`; xlsx/csv: open with python/pandas and check headers + row counts (expect e.g. O*NET Job Titles ≈ tens of thousands of rows; NICE JSON parses with ~2,200 T/K/S statements; DDaT roles CSV ≈ 53 roles). Delete anything that `file` reports as HTML.

## D. Suggested canonical filenames
- ONET_31.0_full_excel.zip; ONET_31.0_Job_Titles.xlsx; ONET_31.0_Occupation_Data.xlsx; ONET_31.0_Software_Skills.xlsx; ONET_31.0_Essential_Skills.xlsx
- NIST_SP800-181r1_NICE_Framework.pdf; NICE_Framework_Components_v2.2.0.xlsx / .json
- UK_GDD_DDaT_Roles_and_Skills.csv; UK_GDD_DDaT_Skills_Content.csv
- ENISA_ECSF_Role_Profiles.pdf; ENISA_ECSF_User_Manual.pdf
- CEN_CWA16458-1_2018_ICT_Role_Profiles.pdf (+ parts 2/4)
- SG_SFw_ICT_Consolidated_Career_Maps.pdf
- SFIA9_Framework_Reference.pdf; SFIA9_Skills_Levels.xlsx (post-registration)
- ESCO_v1.2.1_classification_en_csv.zip (post-email-flow)
