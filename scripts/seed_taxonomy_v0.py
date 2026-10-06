"""Seed the TWM Role Framework v0 CSVs under taxonomy/.

This script is the authored source for v0 (Sept 13, 2026). It writes the five CSVs once;
after that the CSVs are the versioned artifacts and are edited directly (append/deprecate,
never silent edits). Re-running it regenerates v0 exactly, so it doubles as provenance.

    .venv/Scripts/python.exe scripts/seed_taxonomy_v0.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "taxonomy"
VERSION = "0.0"

# =============================================================================
# Table 1 — role families
# =============================================================================
FAMILIES = [
    ("swe", "Software Engineering", "Designs, builds and maintains custom application software.",
     "Any language/framework; technology is a tag, never a role. Packaged-platform customisation lives in pkg."),
    ("qe", "Quality Engineering", "Plans, executes and automates testing and quality assurance of software and processes.",
     "Includes manual, automation, performance testing and process QA."),
    ("data", "Data & Analytics", "Engineers, models, governs and analyses data; builds reporting and analytics.",
     "GIS/geomatics work maps here or to swe with tech tag gis, not to dedicated GIS roles."),
    ("ai", "AI & Machine Learning", "Builds, deploys and governs machine learning and AI systems.",
     "Data science for insight stays in data; ML/AI engineering and MLOps live here."),
    ("infra", "Cloud & Infrastructure", "Builds and runs compute, storage, cloud, platform and DevOps/SRE capabilities.",
     "Per spec: platform, DevOps/SRE and middleware ops. Middleware/database administration is dba."),
    ("sec", "Cybersecurity", "Protects systems and data: security operations, engineering, testing, GRC, IAM, forensics.",
     "Security architecture lives in arch (domain architect). Physical security is out of scope."),
    ("arch", "Architecture", "Enterprise, solution, technical and domain architecture.",
     "All architect roles including data/security/network/cloud/business architects."),
    ("dm", "Delivery Management", "Manages projects, programmes, agile delivery, PMO and delivery risk.",
     "Product ownership is pm; organisational change management is chg."),
    ("pm", "Product Management", "Owns product/service outcomes, roadmaps and backlogs.",
     "Product owner, product manager, service owner."),
    ("ba", "Business Analysis", "Elicits, analyses and specifies business and system requirements and processes.",
     "Packaged-platform functional analysis lives in pkg."),
    ("ux", "Design & UX", "User research, interaction/service/content/graphic design, accessibility, technical writing.",
     "Front-end coding is swe."),
    ("itops", "IT Service & Operations", "Service desk, end-user support, ITSM process roles, IT operations and IT management tiers.",
     "Also holds IT commercial functions (vendor/contract, procurement) and business continuity."),
    ("dba", "Database & Middleware Administration", "Administers and develops on databases, middleware and web platforms.",
     "Data engineering/modelling is data; database architecture is arch."),
    ("net", "Networking & Telecom Engineering", "Designs, builds and operates networks and telecommunications.",
     "Network security roles are sec; network architecture is arch."),
    ("pkg", "Packaged Applications", "Configures, extends, integrates and administers packaged platforms (ERP, CRM, ITSM, insurance cores).",
     "Technology IS the practice here: generic roles carry the platform as a tech tag (sap, salesforce, servicenow...). Kyle to confirm generic-vs-platform-named roles."),
    ("adv", "Consulting & Advisory", "Management and technology consulting delivered through the consulting pyramid.",
     "Distinct band logic: analyst/consultant/manager/senior manager/director/partner (see band_crosswalk 'Consulting pyramid')."),
    ("chg", "Change, Training & Communications", "Organisational change management, training delivery/content and programme communications.",
     "ADDED vs spec draft: TBIPS stream 5 and Texas DIR both carry these titles; they are not delivery management. Non-IT adoption work bolts on here."),
    ("exec", "Technology Leadership", "C-level and head-of technology roles priced as roles, not bands.",
     "ADDED vs spec draft: G-Cloud 15 and DDaT publish a 'Chief digital and data' category with its own rates (e.g. GBP 3,200/day)."),
]

# =============================================================================
# Table 2 — canonical roles
# (role_id, family, name, definition, disambiguation_notes, ddat, tbips, onet_soc)
# =============================================================================
R = []


def role(rid, fam, name, definition, disamb, ddat="", tbips="", onet=""):
    R.append((rid, fam, name, definition, disamb, ddat, tbips, onet))


# --- Software Engineering
role("software_developer", "swe", "Software Developer",
     "Designs, writes, tests and maintains application code across the software lifecycle.",
     "Umbrella for developer / programmer / software engineer titles in any language; a technology in the title becomes a tech tag, not a new role. Choose programmer_analyst only when the title says programmer/analyst; frontend_developer for client-side UI only; web_developer for websites/web apps end to end.",
     "Software developer", "A.6", "15-1252.00")
role("programmer_analyst", "swe", "Programmer Analyst",
     "Combines programming with systems and requirements analysis; a legacy public-sector category.",
     "Pick when the title literally pairs programmer/developer with analyst (Programmer/Analyst, Developer/Programmer Analyst, Software Analyst). Pure coding -> software_developer; no coding -> systems_analyst.",
     "", "A.7", "15-1251.00")
role("frontend_developer", "swe", "Frontend Developer",
     "Builds client-side user interfaces with HTML/CSS/JavaScript frameworks.",
     "Client-side code only. web_developer builds the whole web application; interaction_designer designs but does not code.",
     "Frontend developer", "", "15-1254.00")
role("web_developer", "swe", "Web Developer",
     "Builds and maintains websites and web applications end to end.",
     "Full web application including server side. Front-end-only titles -> frontend_developer; web server operations -> web_administrator.",
     "", "A.14", "15-1254.00")
role("mobile_developer", "swe", "Mobile Developer",
     "Builds native or cross-platform mobile applications.",
     "Any mobile platform; iOS/Android/Flutter become tech tag mobile.",
     "", "", "15-1252.00")
role("integration_developer", "swe", "Integration Developer",
     "Builds APIs, middleware integrations, ESB/iPaaS flows and EDI interfaces.",
     "Writes integration code; middleware_administrator operates the integration platform; integration_architect designs the landscape.",
     "", "", "15-1252.00")
role("engineering_manager", "swe", "Engineering Manager",
     "Manages a software engineering team: people, delivery and technical standards.",
     "Management tier as a role. A hands-on 'Lead Developer' is software_developer at lead_principal; delivery_manager runs delivery without line management.",
     "", "", "11-3021.00")

# --- Quality Engineering
role("test_analyst", "qe", "Test Analyst",
     "Plans and executes functional/manual tests, writes test cases and logs defects.",
     "Default for tester / QA analyst / QA engineer titles. Writes automation frameworks -> test_automation_engineer; process quality (standards, audits of deliverables) -> quality_assurance_analyst.",
     "Quality assurance test analyst", "A.11", "15-1253.00")
role("test_automation_engineer", "qe", "Test Automation Engineer",
     "Designs and builds automated test frameworks and scripts.",
     "Title says automation / SDET / test engineer. Manual or unspecified testing -> test_analyst; load/performance -> performance_test_engineer.",
     "Test engineer", "", "15-1253.00")
role("performance_test_engineer", "qe", "Performance Test Engineer",
     "Designs and runs load, stress and other non-functional tests.",
     "Non-functional testing only. Web/digital analytics 'performance analyst' is a data role.",
     "", "", "15-1253.00")
role("test_manager", "qe", "Test Manager",
     "Leads test teams, strategy, planning and resourcing.",
     "Test coordinator/test lead titles map here (band from evidence). QA/Test Manager combined titles map here.",
     "Test manager", "A.10", "15-1253.00")
role("quality_assurance_analyst", "qe", "Quality Assurance Analyst",
     "Assures process and deliverable quality against standards; audits and improves quality practices.",
     "Process QA, not software testing. Executes tests -> test_analyst.",
     "", "P.11", "15-1253.00")

# --- Data & Analytics
role("data_engineer", "data", "Data Engineer",
     "Builds and operates data pipelines, warehouses and lakes.",
     "Moves and transforms data at scale. Analytics-layer transformation -> analytics_engineer; database operations -> database_administrator; models -> data_scientist.",
     "Data engineer", "", "15-1243.01")
role("data_analyst", "data", "Data Analyst",
     "Analyses data and produces reports, dashboards and insight for decisions.",
     "Consumes and interprets data. Builds BI platforms/semantic models -> business_intelligence_analyst; statistical/ML modelling -> data_scientist.",
     "Data analyst", "G.1|G.2|G.11", "15-2051.01")
role("business_intelligence_analyst", "data", "Business Intelligence Analyst",
     "Builds BI reports, dashboards and semantic models and analyses business trends.",
     "BI developer / BI analyst / report writer titles. General analysis without BI tooling -> data_analyst.",
     "", "", "15-2051.01")
role("data_scientist", "data", "Data Scientist",
     "Applies statistics and machine learning to extract insight and build predictive models.",
     "Insight and modelling. Productionising and serving models -> machine_learning_engineer.",
     "Data scientist", "", "15-2051.00")
role("analytics_engineer", "data", "Analytics Engineer",
     "Transforms warehouse data into tested, documented analytics models (dbt-style).",
     "Sits between data_engineer (pipelines) and data_analyst (consumption).",
     "Analytics engineer", "", "15-1243.01")
role("data_modeler", "data", "Data Modeler",
     "Designs conceptual, logical and physical data models.",
     "Modelling only. Enterprise data strategy -> data_architect; physical DB platform design -> database_architect.",
     "", "I.4", "15-1243.00")
role("data_governance_manager", "data", "Data Governance Manager",
     "Defines and runs data governance, quality and stewardship.",
     "Governance/stewardship/quality policy. Data privacy compliance -> privacy_specialist.",
     "Data governance manager", "", "11-3021.00")
role("performance_analyst", "data", "Performance Analyst",
     "Analyses digital service and marketing performance data (web analytics, KPIs, evaluation).",
     "Digital/web analytics and service evaluation, including digital marketing analyst and digital evaluator titles. System performance testing -> performance_test_engineer.",
     "Performance analyst|Digital evaluator", "", "13-1161.00")
role("data_migration_specialist", "data", "Data Migration Specialist",
     "Plans and executes data conversion and migration between systems.",
     "Conversion/migration projects. Ongoing pipelines -> data_engineer.",
     "", "I.1", "15-1243.01")

# --- AI & Machine Learning
role("machine_learning_engineer", "ai", "Machine Learning Engineer",
     "Builds, trains, deploys and monitors machine learning models and pipelines.",
     "Engineering of models into production, incl. AI/ML engineer titles. Exploratory modelling -> data_scientist; LLM application building -> ai_engineer; ML platform -> mlops_engineer.",
     "Machine learning engineer", "", "15-2051.00")
role("ai_engineer", "ai", "AI Engineer",
     "Builds applications on foundation models and AI services (prompting, RAG, agents, evaluation).",
     "Generative-AI application work. Trains/serves classical ML models -> machine_learning_engineer.",
     "", "", "15-1252.00")
role("mlops_engineer", "ai", "MLOps Engineer",
     "Builds and operates the ML platform: pipelines, model registry, deployment and monitoring.",
     "Platform for ML. General CI/CD -> devops_engineer.",
     "", "", "15-1252.00")
role("data_ai_ethicist", "ai", "Data & AI Ethicist",
     "Assesses and governs ethical and responsible use of data and AI.",
     "Ethics/responsible-AI assessment. Privacy law compliance -> privacy_specialist.",
     "Data and artificial intelligence ethicist", "", "13-1041.00")
role("ai_research_scientist", "ai", "AI Research Scientist",
     "Researches new models, algorithms and methods in AI/ML.",
     "Research, not product engineering. Applied model building -> machine_learning_engineer.",
     "", "", "15-1221.00")

# --- Cloud & Infrastructure
role("cloud_engineer", "infra", "Cloud Engineer",
     "Builds and operates cloud infrastructure and platform services.",
     "Hands-on cloud build/run. Designs the cloud landscape -> cloud_architect; on-prem/hybrid servers -> infrastructure_engineer.",
     "", "", "15-1299.08")
role("infrastructure_engineer", "infra", "Infrastructure Engineer",
     "Designs and builds servers, storage, virtualisation and hybrid infrastructure.",
     "Build/engineering. Day-to-day running -> infrastructure_operations_engineer; OS/account administration -> systems_administrator.",
     "Infrastructure engineer", "", "15-1299.08")
role("infrastructure_operations_engineer", "infra", "Infrastructure Operations Engineer",
     "Runs, monitors and maintains infrastructure in live service.",
     "Operations of infrastructure. Building it -> infrastructure_engineer; monitoring batch/jobs from an ops centre -> it_operations_analyst.",
     "Infrastructure operations engineer", "", "15-1244.00")
role("systems_administrator", "infra", "Systems Administrator",
     "Administers servers, operating systems, accounts and patches.",
     "Sysadmin titles. Network devices -> network_administrator; databases -> database_administrator.",
     "", "I.9", "15-1244.00")
role("systems_engineer", "infra", "Systems Engineer",
     "Engineers and integrates hardware, software and platform components into working systems.",
     "Systems (not software) engineering. Writes application code -> software_developer; requirements analysis -> systems_analyst.",
     "", "", "15-1299.08")
role("devops_engineer", "infra", "DevOps Engineer",
     "Builds CI/CD pipelines, automation and platform tooling bridging development and operations.",
     "Automation/CI-CD focus. Reliability/on-call engineering -> site_reliability_engineer; internal developer platform -> platform_engineer.",
     "Development operations (DevOps) engineer", "", "15-1252.00")
role("site_reliability_engineer", "infra", "Site Reliability Engineer",
     "Applies software engineering to availability, latency, performance and incident response.",
     "SRE titles. Pipeline/tooling focus -> devops_engineer.",
     "", "", "15-1299.08")
role("platform_engineer", "infra", "Platform Engineer",
     "Builds and runs internal platforms (PaaS, Kubernetes, developer platforms).",
     "Platform product for engineers. Single-application CI/CD -> devops_engineer.",
     "", "I.7", "15-1299.08")
role("storage_engineer", "infra", "Storage & Backup Engineer",
     "Engineers and operates storage, backup and recovery platforms.",
     "Storage specialism; storage architecture -> infrastructure_architect.",
     "", "", "15-1244.00")

# --- Cybersecurity
role("security_analyst", "sec", "Security Analyst",
     "Monitors, triages and investigates security events (SOC/monitoring).",
     "Default for information/cyber/network/data security analyst titles. Builds controls -> security_engineer; assesses policy/risk -> security_grc_analyst.",
     "Cyber security monitoring", "C.8", "15-1212.00")
role("security_engineer", "sec", "Security Engineer",
     "Designs, implements and maintains security controls and tooling.",
     "Engineering of controls (firewalls, EDR, SIEM, secure design). Monitoring -> security_analyst; designs the security landscape -> security_architect.",
     "Cyber security secure design", "C.4|C.6|C.14", "15-1299.05")
role("penetration_tester", "sec", "Penetration Tester",
     "Performs authorised offensive security testing of systems and applications.",
     "Offensive testing. Scanning/tracking vulnerabilities -> vulnerability_analyst.",
     "Cyber security testing", "", "15-1299.04")
role("vulnerability_analyst", "sec", "Vulnerability Analyst",
     "Runs vulnerability management: scanning, prioritisation and remediation tracking.",
     "Vulnerability lifecycle. Exploitation testing -> penetration_tester.",
     "Cyber security vulnerability management", "C.11", "15-1212.00")
role("incident_responder", "sec", "Security Incident Responder",
     "Detects, contains and remediates security incidents.",
     "Security incidents only. ITSM incident process -> incident_manager.",
     "Cyber security incident response", "C.12", "15-1212.00")
role("digital_forensics_analyst", "sec", "Digital Forensics Analyst",
     "Collects and analyses digital evidence for investigations.",
     "Forensics/eDiscovery. Live incident handling -> incident_responder.",
     "Cyber security digital forensics", "C.15", "15-1299.06")
role("security_grc_analyst", "sec", "Security GRC Analyst",
     "Governance, risk, compliance, policy, audit and assurance for information security.",
     "Policy/risk/assurance work incl. TRA, C&A, audit & assurance. Technical controls -> security_engineer; IT audit generally -> it_auditor.",
     "Cyber security governance and risk management|Cyber security audit and assurance", "C.1|C.2|C.3", "13-1199.07")
role("security_administrator", "sec", "Security Administrator",
     "Administers security tools, accounts, access and installations.",
     "Operates/administers security systems. Designs them -> security_engineer; identity platforms -> identity_access_management_engineer.",
     "", "C.9|C.10", "15-1212.00")
role("identity_access_management_engineer", "sec", "Identity & Access Management Engineer",
     "Engineers identity, access, directory and PKI services.",
     "IAM/PKI specialism. General security tooling -> security_engineer.",
     "", "C.5", "15-1299.05")
role("information_security_manager", "sec", "Information Security Manager",
     "Manages the information security function, policies and controls.",
     "Management tier role. Executive accountability -> chief_information_security_officer.",
     "", "", "11-3021.00")
role("it_auditor", "sec", "IT Auditor",
     "Audits IT systems, controls and processes against standards and risk.",
     "Audit of IT generally. Security-specific assurance -> security_grc_analyst.",
     "", "A.9", "13-1041.00")
role("privacy_specialist", "sec", "Privacy Specialist",
     "Assesses privacy impact and data-protection compliance.",
     "Privacy/PIA/data protection. Ethics of AI -> data_ai_ethicist.",
     "", "C.16", "13-1041.00")

# --- Architecture
role("enterprise_architect", "arch", "Enterprise Architect",
     "Defines enterprise-wide technology strategy, standards and target architecture.",
     "Enterprise scope. Single solution -> solution_architect; business capability models -> business_architect.",
     "Enterprise architect", "P.2", "15-1299.08")
role("solution_architect", "arch", "Solution Architect",
     "Designs end-to-end solutions across application, data and infrastructure for a programme or product.",
     "Solution scope incl. GIS system architect titles. Enterprise scope -> enterprise_architect; application internals -> application_architect; technology platform -> technical_architect.",
     "Solution architect", "G.9", "15-1299.08")
role("technical_architect", "arch", "Technical Architect",
     "Designs the technical platform and standards a solution is built on.",
     "Platform/technology architecture incl. systems architect and technology architect titles. Application design -> application_architect.",
     "Technical architect", "I.10|I.11", "15-1299.08")
role("application_architect", "arch", "Application Architect",
     "Designs the structure and components of application software.",
     "Software/application/web architect titles. Whole-solution scope -> solution_architect.",
     "", "A.1|A.12|G.4", "15-1299.08")
role("data_architect", "arch", "Data Architect",
     "Designs enterprise data structures, flows, standards and information management.",
     "Enterprise data/information management architecture. Physical database platform -> database_architect; modelling only -> data_modeler.",
     "Data architect", "I.5|G.5", "15-1243.00")
role("database_architect", "arch", "Database Architect",
     "Designs database platforms and physical database structures.",
     "Physical DB design. Enterprise data landscape -> data_architect.",
     "", "", "15-1243.00")
role("security_architect", "arch", "Security Architect",
     "Designs security architecture, patterns and controls across solutions.",
     "Design authority for security. Implements controls -> security_engineer.",
     "Security architect", "C.7", "15-1299.05")
role("network_architect", "arch", "Network Architect",
     "Designs network and connectivity architecture.",
     "Design authority for networks. Builds/configures -> network_engineer.",
     "Network architect", "", "15-1241.00")
role("cloud_architect", "arch", "Cloud Architect",
     "Designs cloud landing zones, services and migration architecture.",
     "Cloud design authority. Hands-on cloud build -> cloud_engineer.",
     "", "", "15-1299.08")
role("infrastructure_architect", "arch", "Infrastructure Architect",
     "Designs infrastructure, storage and hosting architecture.",
     "Incl. storage architect and GIS infrastructure architect. Builds it -> infrastructure_engineer.",
     "", "I.8|G.6", "15-1299.08")
role("business_architect", "arch", "Business Architect",
     "Develops business capability, process and operating-model architecture.",
     "Incl. business transformation architect. Requirements for a system -> business_analyst.",
     "Business architect", "B.2|B.7", "13-1111.00")
role("integration_architect", "arch", "Integration Architect",
     "Designs integration and API landscapes.",
     "Design of integration. Builds interfaces -> integration_developer.",
     "", "", "15-1299.08")

# --- Delivery Management
role("project_manager", "dm", "Project Manager",
     "Plans, runs and reports a project to scope, schedule and budget.",
     "Incl. project lead/leader and task manager titles. Multiple related projects -> program_manager; agile team delivery -> delivery_manager.",
     "", "P.8|P.9|G.8", "15-1299.09")
role("program_manager", "dm", "Program Manager",
     "Directs a programme of related projects toward strategic outcomes.",
     "Programme scope incl. programme delivery manager and project executive. Single project -> project_manager.",
     "Programme delivery manager", "P.5", "15-1299.09")
role("delivery_manager", "dm", "Delivery Manager",
     "Enables agile team delivery: removes blockers, manages flow, risk and stakeholders.",
     "Agile delivery role. Facilitates ceremonies only -> scrum_master; traditional plan-driven -> project_manager.",
     "Delivery manager", "", "15-1299.09")
role("scrum_master", "dm", "Scrum Master",
     "Facilitates Scrum events and coaches one or two teams in agile practice.",
     "Team-level facilitation. Organisation-level coaching -> agile_coach.",
     "", "", "15-1299.09")
role("agile_coach", "dm", "Agile Coach",
     "Coaches teams and leadership in agile ways of working at organisational scale.",
     "Multi-team/organisation coaching. Single team -> scrum_master.",
     "Agile coach", "", "13-1111.00")
role("project_coordinator", "dm", "Project Coordinator",
     "Supports projects with administration, scheduling, tracking and PMO reporting.",
     "Incl. project administrator, scheduler, PMO analyst. Accountable for delivery -> project_manager.",
     "", "P.6|P.7|P.10", "13-1082.00")
role("portfolio_manager", "dm", "Portfolio Manager",
     "Manages a portfolio of programmes/products: prioritisation, funding and benefits.",
     "Portfolio scope. Programme scope -> program_manager.",
     "Digital portfolio manager", "", "11-3021.00")
role("risk_management_specialist", "dm", "Risk Management Specialist",
     "Identifies, assesses and manages project and IT delivery risk.",
     "Delivery/IT risk. Security risk -> security_grc_analyst.",
     "", "P.12", "13-1199.00")
role("project_assurance_reviewer", "dm", "Project Assurance Reviewer",
     "Independently reviews projects and programmes for health and compliance.",
     "Independent review/assurance. Audits IT controls -> it_auditor.",
     "", "P.13|P.14", "13-1111.00")

# --- Product Management
role("product_manager", "pm", "Product Manager",
     "Owns product vision, roadmap and outcomes.",
     "Incl. digital product manager. Backlog ownership for a team -> product_owner; live service ownership -> service_owner.",
     "Product manager", "", "")
role("product_owner", "pm", "Product Owner",
     "Owns and prioritises a team backlog on behalf of stakeholders.",
     "Team-level backlog. Strategy/roadmap -> product_manager.",
     "", "", "")
role("service_owner", "pm", "Service Owner",
     "Accountable for a live digital service end to end.",
     "Service accountability. Product strategy -> product_manager.",
     "Service owner", "", "")

# --- Business Analysis
role("business_analyst", "ba", "Business Analyst",
     "Elicits, analyses and documents business requirements and processes.",
     "Default for business analyst, business systems analyst, requirements/functional analyst titles. Specifies technical solutions -> systems_analyst; packaged-platform configuration -> pkg functional consultant.",
     "Business analyst", "B.1|B.6", "13-1111.00")
role("systems_analyst", "ba", "Systems Analyst",
     "Analyses requirements and specifies technical/system solutions.",
     "Systems analyst specifies technical solutions; business_analyst captures business needs. Codes as well -> programmer_analyst.",
     "", "A.8|G.3", "15-1211.00")
role("business_process_analyst", "ba", "Business Process Analyst",
     "Analyses, re-engineers and improves business processes.",
     "Process re-engineering/improvement, incl. process improvement manager titles. Change adoption -> change_management_consultant.",
     "", "B.5", "13-1111.00")
role("subject_matter_expert", "ba", "Subject Matter Expert",
     "Provides deep domain/business expertise to a delivery.",
     "Domain expert billed as a role (band usually lead_principal). Titles ending '- SME' on another role are that role at lead_principal.",
     "", "", "13-1199.00")

# --- Design & UX
role("interaction_designer", "ux", "Interaction Designer",
     "Designs user interfaces and interaction flows (UX/UI design).",
     "UX/UI designer titles. Whole-service design -> service_designer; visual assets -> graphic_designer; web page layouts -> web_designer.",
     "Interaction designer", "", "15-1255.00")
role("service_designer", "ux", "Service Designer",
     "Designs end-to-end services across channels and touchpoints.",
     "Service-level design. Screen-level -> interaction_designer.",
     "Service designer", "", "")
role("user_researcher", "ux", "User Researcher",
     "Plans and conducts user research to inform design.",
     "Research only. Designs from it -> interaction_designer.",
     "User researcher", "", "19-3022.00")
role("content_designer", "ux", "Content Designer",
     "Creates and manages user-facing content and web content.",
     "Incl. web content specialist/manager and multimedia content consultant. Content strategy -> content_strategist; technical docs -> technical_writer.",
     "Content designer", "A.16", "27-3043.00")
role("content_strategist", "ux", "Content Strategist",
     "Sets content strategy, standards and governance.",
     "Strategy. Writes content -> content_designer.",
     "Content strategist", "", "27-3043.00")
role("graphic_designer", "ux", "Graphic Designer",
     "Creates visual design assets and brand-aligned graphics.",
     "Visual/brand assets incl. web graphics designer. Interface behaviour -> interaction_designer.",
     "Graphic designer", "A.15", "27-1024.00")
role("accessibility_specialist", "ux", "Accessibility Specialist",
     "Assures and advises on accessibility of digital services.",
     "Accessibility only.",
     "Accessibility specialist", "", "")
role("technical_writer", "ux", "Technical Writer",
     "Writes technical and user documentation.",
     "Documentation. Web/user content -> content_designer; training material -> learning_content_developer.",
     "Technical writer", "B.14", "27-3042.00")
role("web_designer", "ux", "Web Designer",
     "Designs web page layouts and visuals.",
     "Designs web pages; does not code -> frontend_developer codes them. Brand assets -> graphic_designer.",
     "", "A.13", "15-1255.00")

# --- IT Service & Operations
role("service_desk_analyst", "itops", "Service Desk Analyst",
     "Provides first/second-line IT support via the service desk.",
     "Help desk / service desk / support specialist titles. Deskside hardware -> desktop_support_technician; application-specific L2/L3 -> application_support_analyst.",
     "Service desk manager", "B.10", "15-1232.00")
role("desktop_support_technician", "itops", "Desktop Support Technician",
     "Supports, repairs and configures end-user devices and peripherals on site.",
     "Deskside/hardware. Remote first-line -> service_desk_analyst; device engineering -> end_user_computing_engineer.",
     "", "", "15-1232.00")
role("end_user_computing_engineer", "itops", "End User Computing Engineer",
     "Engineers end-user device platforms: images, device management, collaboration tools.",
     "EUC engineering. Ticket support -> service_desk_analyst.",
     "End user computing engineer", "", "15-1232.00")
role("application_support_analyst", "itops", "Application Support Analyst",
     "Supports and operates business applications in live service (L2/L3).",
     "Incl. application operations engineer and product support analyst. Infrastructure -> infrastructure_operations_engineer.",
     "Application operations engineer", "", "15-1232.00")
role("it_operations_analyst", "itops", "IT Operations Analyst",
     "Monitors and operates IT services from an operations/command centre; batch, jobs, alerts.",
     "Incl. operations support specialist, command and control roles. Network-specific NOC -> network_operations_technician.",
     "Command and control centre manager", "B.13", "15-1299.00")
role("it_service_manager", "itops", "IT Service Manager",
     "Manages ITSM processes and service delivery to agreed levels.",
     "Service management. Runs the service desk -> service_desk_manager.",
     "IT service manager", "", "11-3021.00")
role("service_desk_manager", "itops", "Service Desk Manager",
     "Manages the service desk function.",
     "Management of the desk (incl. help desk manager). Analyst level -> service_desk_analyst.",
     "Service desk manager", "", "11-3021.00")
role("incident_manager", "itops", "Incident Manager",
     "Owns the ITSM incident process and major incident coordination.",
     "ITSM incidents. Security incidents -> incident_responder.",
     "Incident manager", "", "15-1299.00")
role("problem_manager", "itops", "Problem Manager",
     "Owns root-cause analysis and the problem management process.",
     "Problem process only.",
     "Problem manager", "", "15-1299.00")
role("change_release_manager", "itops", "Change & Release Manager",
     "Owns change, release and configuration management processes.",
     "ITSM change/release/configuration. Organisational change -> change_management_consultant.",
     "Change and release manager", "", "15-1299.00")
role("service_transition_manager", "itops", "Service Transition Manager",
     "Manages transition of services into live operation (readiness, acceptance).",
     "Transition/readiness. Steady-state -> it_service_manager.",
     "Service transition manager", "", "15-1299.00")
role("business_relationship_manager", "itops", "Business Relationship Manager",
     "Manages the relationship between IT and business stakeholders.",
     "IT-to-business liaison. Requirements work -> business_analyst.",
     "Business relationship manager", "", "11-3021.00")
role("it_manager", "itops", "IT Manager",
     "Manages an IT function or team (generic management tier).",
     "Use when the title is simply IT manager. Specific functions -> engineering_manager, database_manager, it_operations_manager, information_security_manager.",
     "", "", "11-3021.00")
role("it_operations_manager", "itops", "IT Operations Manager",
     "Manages IT operations and service delivery teams.",
     "Operations management. Process ownership -> it_service_manager.",
     "", "", "11-3021.00")
role("business_continuity_specialist", "itops", "Business Continuity Specialist",
     "Plans and tests business continuity and disaster recovery.",
     "BC/DR. Security risk -> security_grc_analyst.",
     "", "B.4", "13-1199.00")
role("it_vendor_contract_manager", "itops", "IT Vendor & Contract Manager",
     "Manages IT contracts, vendor performance and compliance.",
     "Contract/vendor management incl. contract administrator. Sourcing/purchasing -> it_procurement_specialist.",
     "", "", "11-3061.00")
role("it_procurement_specialist", "itops", "IT Procurement Specialist",
     "Sources, evaluates and purchases IT goods and services.",
     "Purchasing. Post-award contract management -> it_vendor_contract_manager.",
     "", "", "13-1023.00")

# --- Database & Middleware Administration
role("database_administrator", "dba", "Database Administrator",
     "Installs, secures, tunes, backs up and operates databases.",
     "DBA titles (any engine -> tech tag). Writes database code -> database_developer; designs platforms -> database_architect.",
     "", "I.2", "15-1242.00")
role("database_analyst", "dba", "Database Analyst",
     "Designs, queries and supports databases and information management.",
     "Between DBA and developer; incl. IM administrator. Pure operations -> database_administrator.",
     "", "I.3", "15-1242.00")
role("database_developer", "dba", "Database Developer",
     "Develops stored procedures, SQL/PL-SQL and database-side logic.",
     "Database code. Pipelines -> data_engineer; operations -> database_administrator.",
     "", "", "15-1252.00")
role("middleware_administrator", "dba", "Middleware Administrator",
     "Administers application servers, messaging and integration platforms.",
     "Operates middleware. Builds integrations -> integration_developer.",
     "", "", "15-1244.00")
role("web_administrator", "dba", "Web Administrator",
     "Operates web servers and websites (webmaster).",
     "Incl. webmaster and web manager. Builds sites -> web_developer.",
     "", "A.17", "15-1299.01")
role("database_manager", "dba", "Database Manager",
     "Manages the database administration function.",
     "Management tier role.",
     "", "", "11-3021.00")

# --- Networking & Telecom
role("network_engineer", "net", "Network Engineer",
     "Designs, implements and maintains network infrastructure.",
     "Build/engineering incl. wireless (tech tag). Day-to-day admin -> network_administrator; design authority -> network_architect; security devices -> security_engineer.",
     "", "", "15-1241.00")
role("network_administrator", "net", "Network Administrator",
     "Installs, configures and supports LAN/WAN and network services.",
     "Administration/support. Engineering changes -> network_engineer.",
     "", "", "15-1244.00")
role("network_analyst", "net", "Network Analyst",
     "Analyses, monitors and supports network performance and issues.",
     "Incl. network support specialist. Builds networks -> network_engineer.",
     "", "I.6|B.12", "15-1231.00")
role("network_operations_technician", "net", "Network Operations Technician",
     "Monitors and troubleshoots networks from a NOC.",
     "NOC roles. General IT ops centre -> it_operations_analyst.",
     "", "", "15-1231.00")
role("telecommunications_engineer", "net", "Telecommunications Engineer",
     "Designs, installs and maintains voice, data and telecom systems.",
     "Telecom specialist/technician titles. Data networks -> network_engineer.",
     "", "", "15-1241.01")
role("telecommunications_manager", "net", "Telecommunications Manager",
     "Manages telecom systems and teams.",
     "Management tier role.",
     "", "", "11-3021.00")

# --- Packaged Applications
role("packaged_application_functional_consultant", "pkg", "Packaged Application Functional Consultant",
     "Configures packaged-platform modules to business processes (ERP/CRM/HCM/ITSM functional consultant/analyst).",
     "Functional/business configuration on a platform (tech tag = platform). Custom code -> packaged_application_developer; technical/basis -> packaged_application_technical_consultant.",
     "", "A.2|A.4", "15-1211.00")
role("packaged_application_developer", "pkg", "Packaged Application Developer",
     "Customises and extends packaged platforms in their native languages (ABAP, Apex, etc.).",
     "Platform development. Configuration only -> functional consultant; general software -> software_developer.",
     "", "A.3", "15-1252.00")
role("packaged_application_technical_consultant", "pkg", "Packaged Application Technical Consultant",
     "Handles platform technical/basis, integration, performance and upgrades.",
     "Technical platform specialism. Functional config -> functional consultant.",
     "", "A.5", "15-1299.08")
role("packaged_application_architect", "pkg", "Packaged Application Architect",
     "Designs solutions on a packaged platform.",
     "Platform solution architecture. Custom solution architecture -> solution_architect.",
     "", "", "15-1299.08")
role("packaged_application_administrator", "pkg", "Packaged Application Administrator",
     "Administers a packaged platform (users, security, releases).",
     "Platform admin. Server/OS admin -> systems_administrator.",
     "", "", "15-1244.00")

# --- Consulting & Advisory
role("management_consultant", "adv", "Management Consultant",
     "Advises on strategy, operating model, process and organisation (incl. HR/OD consulting).",
     "Business/HR/OD/call-centre consultant titles. Technology strategy -> technology_consultant; process re-engineering as analysis -> business_process_analyst.",
     "", "B.3|B.8|P.3|P.4", "13-1111.00")
role("technology_consultant", "adv", "Technology Consultant",
     "Advises on technology strategy, selection and transformation.",
     "Advisory, not build. Designs architecture -> arch roles.",
     "", "", "13-1111.00")
role("engagement_manager", "adv", "Engagement Manager",
     "Manages a consulting engagement's scope, team and client relationship.",
     "Consulting-firm manager tier. Client-side project manager -> project_manager.",
     "", "", "11-9199.00")
role("consulting_director_partner", "adv", "Consulting Director / Partner",
     "Director/partner-level consulting leadership and client accountability.",
     "Top of the consulting pyramid incl. associate director. Engagement day-to-day -> engagement_manager.",
     "", "", "11-1011.00")

# --- Change, Training & Communications
role("change_management_consultant", "chg", "Change Management Consultant",
     "Leads organisational change management and adoption (OCM).",
     "People/adoption change. ITSM change process -> change_release_manager.",
     "", "P.1", "13-1111.00")
role("it_trainer", "chg", "IT Trainer",
     "Delivers training and instruction on IT systems.",
     "Delivery of training. Builds materials -> learning_content_developer.",
     "", "B.11", "13-1151.00")
role("learning_content_developer", "chg", "Learning Content Developer",
     "Designs and builds courseware and training materials.",
     "Courseware/training developer titles. Delivers training -> it_trainer; technical docs -> technical_writer.",
     "", "B.9", "13-1151.00")
role("communications_specialist", "chg", "Communications Specialist",
     "Plans and produces programme/IT communications and marketing materials.",
     "Comms coordinator titles. User-facing service content -> content_designer.",
     "", "", "27-3031.00")

# --- Technology Leadership
role("chief_information_officer", "exec", "Chief Information Officer",
     "Executive accountable for information technology (incl. chief digital and information officer).",
     "Executive tier. Technology strategy officer -> chief_technology_officer.",
     "Chief digital and information officer", "", "11-3021.00")
role("chief_technology_officer", "exec", "Chief Technology Officer",
     "Executive accountable for technology strategy and engineering.",
     "Executive tier.",
     "Chief technology officer", "", "11-3021.00")
role("chief_data_officer", "exec", "Chief Data Officer",
     "Executive accountable for data strategy and governance.",
     "Executive tier.",
     "Chief data officer", "", "11-3021.00")
role("chief_information_security_officer", "exec", "Chief Information Security Officer",
     "Executive accountable for information security.",
     "Executive tier. Function management -> information_security_manager.",
     "Chief information security officer", "", "11-3021.00")

# =============================================================================
# Table 3 — band crosswalk
# =============================================================================
B = []


def band(scheme, level, twm, notes=""):
    B.append((scheme, level, twm, notes))


for lv, b, n in [("Level 1", "junior", "<5 yrs"), ("Level 2", "intermediate", "5-<10 yrs"), ("Level 3", "senior", "10+ yrs (or 5+ yrs + certification for some categories)"),
                 ("L1", "junior", "alias"), ("L2", "intermediate", "alias"), ("L3", "senior", "alias")]:
    band("TBIPS", lv, b, n)
for lv, b in [("Intern Level 1", "junior"), ("Intern Level 2", "junior"), ("Intern Level 3", "junior"),
              ("Level 1", "intermediate"), ("Level 2", "senior"), ("Level 3", "lead_principal")]:
    band("Texas DIR", lv, b, "spec draft mapping; validated by NTE rate monotonicity in REPORT.md")
for lv, b in [("1", "junior"), ("2", "junior"), ("3", "intermediate"), ("4", "senior"), ("5", "senior"), ("6", "lead_principal"), ("7", "lead_principal")]:
    band("SFIA", lv, b, "crosswalk only; SFIA is not the spine (licensing pending)")
for lv, b in [("Trainee", "junior"), ("Apprentice", "junior"), ("Junior", "junior"), ("Associate", "junior"),
              ("Mid", "intermediate"), ("Standard", "intermediate"), ("Practitioner", "intermediate"),
              ("Senior", "senior"), ("Lead", "lead_principal"), ("Principal", "lead_principal"), ("Head", "lead_principal"), ("Head of", "lead_principal")]:
    band("DDaT", lv, b, "DDaT ladders; role-specific labels (e.g. 'Senior data engineer') derive via title-modifier rules")
for lv, b in [("<3", "junior"), ("3-7", "intermediate"), ("7-12", "senior"), ("12+", "lead_principal")]:
    band("Years stated", lv, b, "years of experience stated in the source")
for lv, b, n in [("Junior", "junior", "12-36 months"), ("Mid-Level", "intermediate", "36-60 months"), ("Senior", "senior", "60-84 months"), ("Expert", "lead_principal", "84+ months")]:
    band("NY HBITS", lv, b, n)
for lv, b in [("Trainee", "junior"), ("Apprentice", "junior"), ("Junior", "junior"), ("Associate", "junior"), ("Associate analyst", "junior"),
              ("Standard", "intermediate"), ("Analyst", "intermediate"), ("Developer", "intermediate"), ("Engineer", "intermediate"),
              ("Tester", "intermediate"), ("Specialist", "intermediate"),
              ("Senior", "senior"), ("Senior analyst", "senior"), ("Senior (management)", "senior"), ("Senior - management", "senior"),
              ("Lead", "lead_principal"), ("Lead (management)", "lead_principal"), ("Lead - management", "lead_principal"),
              ("Principal", "lead_principal"), ("Principal (management)", "lead_principal"), ("Principal - management", "lead_principal"),
              ("Head", "lead_principal"), ("Head (Agile)", "lead_principal"), ("Chief", "lead_principal"), ("Manager", "lead_principal"),
              ("Senior manager", "lead_principal"), ("Lead manager", "lead_principal"), ("Lead analyst", "lead_principal"),
              ("CDO", "lead_principal"), ("CISO", "lead_principal"), ("CTO", "lead_principal")]:
    band("UK G-Cloud 15", lv, b, "standardised GC15 card labels; role-specific labels (e.g. 'Operational control manager') derive via title-modifier rules")
for lv, b in [("AO and EO", "junior"), ("Administrative Officer (AO) and Executive Officer (EO)", "junior"), ("EO and HEO", "junior"),
              ("Executive Officer (EO) and Higher Executive Officer (HEO)", "junior"), ("HEO", "intermediate"), ("Higher Executive Officer (HEO)", "intermediate"),
              ("HEO and SEO", "intermediate"), ("HEO and Senior Executive Officer (SEO)", "intermediate"), ("SEO", "senior"), ("Senior Executive Officer (SEO)", "senior"),
              ("SEO and G7", "senior"), ("SEO and Grade 7 (G7)", "senior"), ("G7", "lead_principal"), ("Grade 7 (G7)", "lead_principal"),
              ("G7 and G6", "lead_principal"), ("G7 and Grade 6 (G6)", "lead_principal"), ("G6 and G7", "lead_principal"), ("G6", "lead_principal"), ("Grade 6 (G6)", "lead_principal"),
              ("G6 and SCS", "lead_principal"), ("G6 and Senior Civil Service (SCS)", "lead_principal"), ("SCS", "lead_principal"), ("Senior Civil Service (SCS)", "lead_principal"),
              ("Associate Cyber", "junior"), ("Lead Cyber", "lead_principal"), ("Principal Cyber", "lead_principal"), ("Principal (\"Principle\") Cyber", "lead_principal")]:
    band("Deloitte CS grade", lv, b, "Deloitte GC15 Civil Service grade-equivalence bands; 4-band collapse of a 7-grade ladder")
for lv, b in [("Analyst", "junior"), ("Associate", "junior"), ("Consultant", "intermediate"), ("Senior Consultant", "senior"),
              ("Manager", "senior"), ("Senior Manager", "lead_principal"), ("Associate Director", "lead_principal"), ("Director", "lead_principal"),
              ("Principal", "lead_principal"), ("Partner", "lead_principal"), ("Managing Director", "lead_principal")]:
    band("Consulting pyramid", lv, b, "heuristic for Big-4/SI consulting grades; validate against consulting rate cards")
for lv, b in [("Sr", "senior"), ("Senior", "senior"), ("Jr", "junior"), ("Junior", "junior"), ("Lead", "lead_principal"), ("Principal", "lead_principal"),
              ("Staff", "lead_principal"), ("Chief", "lead_principal"), ("Head of", "lead_principal"), ("Expert", "lead_principal"), ("SME", "lead_principal"),
              ("Associate", "junior"), ("Trainee", "junior"), ("Apprentice", "junior"), ("Intern", "junior"), ("Entry Level", "junior"), ("Graduate", "junior"),
              ("Mid-Level", "intermediate"), ("Intermediate", "intermediate"),
              ("I", "junior"), ("II", "intermediate"), ("III", "senior"), ("IV", "lead_principal"), ("V", "lead_principal"),
              ("Level 1", "junior"), ("Level 2", "intermediate"), ("Level 3", "senior"), ("Level 4", "lead_principal"), ("Level 5", "lead_principal")]:
    band("Title modifier", lv, b, "modifier captured from the title string by normalize rule 1; generic Level N (non-Texas)")

# =============================================================================
# tech_vocab.csv  (tag, label, category, aliases)
# =============================================================================
TECH = [
    ("java", "Java", "language", "j2ee|jee|spring|spring boot"),
    ("dotnet", ".NET / C#", "language", ".net|c#|csharp|asp.net|vb.net|dot net"),
    ("python", "Python", "language", "django|flask"),
    ("javascript", "JavaScript / TypeScript", "language", "js|typescript|node|node.js|nodejs"),
    ("react", "React", "framework", "reactjs|react native"),
    ("angular", "Angular", "framework", "angularjs"),
    ("php", "PHP", "language", "laravel"),
    ("ruby", "Ruby", "language", "rails|ruby on rails"),
    ("golang", "Go", "language", "go lang"),
    ("scala", "Scala", "language", ""),
    ("c_cpp", "C / C++", "language", "c++|cpp"),
    ("mainframe", "Mainframe", "platform", "cobol|z/os|zos|cics|jcl|ims|pl/i|assembler"),
    ("sap", "SAP", "packaged_erp", "abap|hana|s/4hana|s4hana|sap basis|sap bw|sap fico"),
    ("oracle_erp", "Oracle ERP / EBS / Fusion", "packaged_erp", "oracle ebs|e-business suite|oracle fusion|oracle cloud erp|peoplesoft|jd edwards|jde"),
    ("workday", "Workday", "packaged_erp", ""),
    ("dynamics", "Microsoft Dynamics 365", "packaged_erp", "dynamics 365|d365|dynamics ax|dynamics crm|navision|dynamics"),
    ("netsuite", "NetSuite", "packaged_erp", ""),
    ("erp", "ERP (unspecified)", "packaged_erp", "enterprise resource planning"),
    ("salesforce", "Salesforce", "packaged_crm", "sfdc|apex|salesforce lightning"),
    ("crm", "CRM (unspecified)", "packaged_crm", "customer relationship management"),
    ("siebel", "Siebel", "packaged_crm", ""),
    ("servicenow", "ServiceNow", "packaged_itsm", "service now"),
    ("guidewire", "Guidewire", "packaged_insurance", ""),
    ("pega", "Pega", "packaged_bpm", "pegasystems"),
    ("mulesoft", "MuleSoft", "integration", "mule"),
    ("kafka", "Kafka", "integration", ""),
    ("informatica", "Informatica", "data", ""),
    ("oracle", "Oracle Database", "database", "oracle db|pl/sql|plsql"),
    ("sql_server", "Microsoft SQL Server", "database", "mssql|t-sql|tsql|sql server"),
    ("db2", "IBM Db2", "database", ""),
    ("postgres", "PostgreSQL", "database", "postgresql"),
    ("mysql", "MySQL", "database", ""),
    ("mongodb", "MongoDB", "database", "mongo"),
    ("aws", "Amazon Web Services", "cloud", "amazon web services"),
    ("azure", "Microsoft Azure", "cloud", ""),
    ("gcp", "Google Cloud", "cloud", "google cloud platform|google cloud"),
    ("kubernetes", "Kubernetes / containers", "platform", "k8s|docker|openshift"),
    ("terraform", "Terraform / IaC", "platform", "ansible|puppet|chef"),
    ("linux", "Linux / Unix", "platform", "unix|redhat|rhel|aix|solaris"),
    ("windows", "Windows Server", "platform", "active directory"),
    ("vmware", "VMware", "platform", "vsphere"),
    ("cisco", "Cisco", "network", ""),
    ("wireless", "Wireless / WiFi", "network", "wifi|wi-fi|802.11"),
    ("voip", "VoIP / Unified communications", "network", "voice|telephony|unified communications"),
    ("snowflake", "Snowflake", "data", ""),
    ("databricks", "Databricks", "data", ""),
    ("hadoop", "Hadoop / Spark", "data", "spark|hive|big data"),
    ("tableau", "Tableau", "analytics", ""),
    ("power_bi", "Power BI", "analytics", "powerbi"),
    ("sharepoint", "SharePoint / Microsoft 365", "platform", "microsoft 365|m365|office 365|o365"),
    ("adobe", "Adobe Experience Cloud", "platform", "aem|adobe experience manager"),
    ("cms", "Web CMS (WordPress/Drupal)", "platform", "wordpress|drupal"),
    ("mobile", "Mobile (iOS/Android)", "platform", "ios|android|swift|kotlin|flutter"),
    ("gis", "GIS / Geomatics", "domain", "esri|arcgis|geomatics"),
    ("genai", "Generative AI / LLM", "ai", "llm|generative ai|openai"),
    ("rpa", "RPA", "automation", "uipath|blue prism|automation anywhere"),
]

# =============================================================================
# Table 4 — title mappings (seed)
# (observed_title, role_id, band_from_title, tech, notes)
# =============================================================================
URL_TX = "https://www.cgi.com/sites/default/files/2024-10/dir-cpo-5498-appendix-d-itsac-job-category-title-descriptions.docx.pdf"
URL_NY = "https://ogs.ny.gov/procurement/23158-hbits-hourly-bill-rate-averages"
URL_TB = "https://www.canada.ca/en/public-services-procurement/services/acquisitions/informatics-method-supply/task-based-streams-categories.html"
URL_GC = "https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud-15"
URL_DD = "https://ddat-capability-framework.service.gov.uk/"
URL_CALC = "https://api.gsa.gov/acquisition/calc/v3/api/ceilingrates/"
URL_CDO = "https://www.gsaadvantage.gov/ref_text/GS35F5457H/0OJBQO.36MJO2_GS-35F-5457H_GS35F5457HGPLOY.PDF"
URL_CW = "https://www.gsaadvantage.gov/ref_text/47QTCA25D007E/109Z4I.3W0BZ6_47QTCA25D007E_47QTCA25D007E-3-28-2025-377665.PDF"
URL_TC = "https://www.gsaadvantage.gov/ref_text/47QTCA23D003W/0XZCAC.3TPP53_47QTCA23D003W_TCOGNITIONGSAPRICECATALOG.PDF"

M: list[tuple] = []  # (source, url, title, role, band, tech, level_raw, years_raw, conf, status)


def mp(source, url, title, role, band="", tech="", level_raw="", years_raw="", conf=0.95, status="active"):
    M.append((source, url, title, role, band, tech, level_raw, years_raw, conf, status))


TX = "Texas DIR ITSAC 2024"
for t, r, *rest in [
    ("AI/Machine Learning Engineer", "machine_learning_engineer"), ("Agile Coach", "agile_coach"), ("Agile Scrum Master", "scrum_master"),
    ("Applications Architect", "application_architect"), ("Application Architect", "application_architect"), ("Business Analyst", "business_analyst"),
    ("Business Continuity Analyst", "business_continuity_specialist"), ("Business Intelligence Analyst", "business_intelligence_analyst"),
    ("Change Management Manager/Organizational Change Management (OCM)", "change_management_consultant"),
    ("Cloud Solutions Architect", "cloud_architect"), ("Communication Coordinators", "communications_specialist"), ("Communications Coordinator", "communications_specialist"),
    ("Customer Relationship Management (CRM)", "packaged_application_functional_consultant", "", "crm"),
    ("Data Analyst/Report Writer", "data_analyst"), ("Data Modeler", "data_modeler"), ("Data Scientist (Big Data Engineer)", "data_scientist"),
    ("Data Security Analyst", "security_analyst"), ("Database Administrator", "database_administrator"), ("Database Architect", "database_architect"),
    ("DevOps Engineer", "devops_engineer"), ("Developer/Programmer Analyst", "programmer_analyst"), ("Digital Marketing Analyst", "performance_analyst"),
    ("Digital Product Manager", "product_manager"), ("ERP Business Analyst", "packaged_application_functional_consultant", "", "erp"),
    ("Enterprise Resource Planning (ERP) Business Analyst", "packaged_application_functional_consultant", "", "erp"),
    ("ERP Developer", "packaged_application_developer", "", "erp"), ("Enterprise Architect", "enterprise_architect"),
    ("Front-End Web Developer/Web Designer", "frontend_developer", "", "", "", "", 0.80), ("Help Desk Technician", "service_desk_analyst"),
    ("Help Desk (Technician)", "service_desk_analyst"), ("IT Auditor", "it_auditor"),
    ("IT Contract Administrator/Technician", "it_vendor_contract_manager", "junior"), ("IT Contract Manager", "it_vendor_contract_manager"),
    ("IT Procurement Technician", "it_procurement_specialist"), ("IT Procurement Specialist/Technician", "it_procurement_specialist"),
    ("Information Security Manager", "information_security_manager"), ("Instructor Trainer", "it_trainer"),
    ("Mobile Applications Developer", "mobile_developer"), ("Network Administrator", "network_administrator"), ("Network Engineer", "network_engineer"),
    ("Network Operations Center (NOC) Technician", "network_operations_technician"), ("Network Security Analyst", "security_analyst"),
    ("Network Security Engineer", "security_engineer"), ("Process Improvement Manager", "business_process_analyst"),
    ("Product Support Analyst", "application_support_analyst"), ("Program Manager", "program_manager"), ("Project Lead", "project_manager"),
    ("Project Manager", "project_manager"), ("QA Associate/Analyst", "test_analyst"), ("QA Engineer Automated", "test_automation_engineer"),
    ("QA Engineer - Automated", "test_automation_engineer"), ("QA/Test Manager", "test_manager"), ("Security Administrator", "security_administrator"),
    ("Senior Web Developer", "web_developer", "senior"), ("Site Reliability Engineer", "site_reliability_engineer"),
    ("Software Developer", "software_developer"), ("Software Engineer", "software_developer"), ("Support Technician", "desktop_support_technician"),
    ("Systems Analyst", "systems_analyst"), ("Technical Writer", "technical_writer"), ("Telecommunications Manager", "telecommunications_manager"),
    ("Telecommunications Technician", "telecommunications_engineer"), ("Telecommunications Specialist/Technician", "telecommunications_engineer"),
    ("Web Administrator", "web_administrator"), ("Web Content Technician/Manager", "content_designer"), ("Web Content Specialist/Manager", "content_designer"),
    ("Web Developer", "web_developer"), ("Wireless Network Engineer", "network_engineer", "", "wireless"),
]:
    b = rest[0] if len(rest) > 0 else ""
    tech = rest[1] if len(rest) > 1 else ""
    conf = rest[4] if len(rest) > 4 else 0.95
    mp(TX, URL_TX, t, r, b, tech, conf=conf)

NY = "NY OGS HBITS 23158"
for t, r in [
    ("Business Analyst", "business_analyst"), ("Cloud Engineer", "cloud_engineer"), ("Database Administrator", "database_administrator"),
    ("Database Architect", "database_architect"), ("Database Manager", "database_manager"), ("Graphic Designer", "graphic_designer"),
    ("Help Desk Manager", "service_desk_manager"), ("IT Manager", "it_manager"), ("Network Administrator", "network_administrator"),
    ("Network Architect", "network_architect"), ("Operations Manager", "it_operations_manager"), ("Programmer", "software_developer"),
    ("Project Manager", "project_manager"), ("Security Analyst", "security_analyst"), ("Security Manager", "information_security_manager"),
    ("Software Analyst", "programmer_analyst"), ("Software Architect", "application_architect"), ("Software Developer", "software_developer"),
    ("Software Manager", "engineering_manager"), ("Systems Administrator", "systems_administrator"), ("Systems Analyst", "systems_analyst"),
    ("Systems Architect", "technical_architect"), ("Systems Developer", "software_developer"), ("Technical Writer", "technical_writer"),
    ("Tester", "test_analyst"), ("Training Developer", "learning_content_developer"), ("Web Administrator", "web_administrator"),
    ("Web Designer", "web_designer"), ("Web Developer", "web_developer"), ("Web Manager", "web_administrator"),
]:
    mp(NY, URL_NY, t, r)
mp(NY, URL_NY, "IT Specialist", "", conf=0.0, status="flagged")  # too generic to resolve without context

TB = "Canada TBIPS"
for code, t, r, *rest in [
    ("A.1", "Application/software architect", "application_architect"), ("A.2", "ERP functional analyst", "packaged_application_functional_consultant", "", "erp"),
    ("A.3", "ERP programmer analyst", "packaged_application_developer", "", "erp"), ("A.4", "ERP system analyst", "packaged_application_functional_consultant", "", "erp"),
    ("A.5", "ERP technical analyst", "packaged_application_technical_consultant", "", "erp"), ("A.6", "Programmer/software developer", "software_developer"),
    ("A.7", "Programmer/analyst", "programmer_analyst"), ("A.8", "System analyst", "systems_analyst"), ("A.9", "System auditor", "it_auditor"),
    ("A.10", "Test coordinator", "test_manager"), ("A.11", "Tester", "test_analyst"), ("A.12", "Web architect", "application_architect"),
    ("A.13", "Web designer", "web_designer"), ("A.14", "Web developer", "web_developer"), ("A.15", "Web graphics designer", "graphic_designer"),
    ("A.16", "Web multi-media content consultant", "content_designer"), ("A.17", "Webmaster", "web_administrator"),
    ("G.1", "Geomatics analyst", "data_analyst", "", "gis"), ("G.2", "Geomatics specialist", "data_analyst", "", "gis"),
    ("G.3", "GIS applications analyst", "systems_analyst", "", "gis"), ("G.4", "GIS application architect", "application_architect", "", "gis"),
    ("G.5", "GIS data architect", "data_architect", "", "gis"), ("G.6", "GIS infrastructure architect", "infrastructure_architect", "", "gis"),
    ("G.7", "GIS programmer/analyst", "programmer_analyst", "", "gis"), ("G.8", "GIS project manager", "project_manager", "", "gis"),
    ("G.9", "GIS system architect", "solution_architect", "", "gis"), ("G.10", "GIS web mapping developer", "web_developer", "", "gis"),
    ("G.11", "Mapping technician", "data_analyst", "junior", "gis"),
    ("I.1", "Data conversion specialist", "data_migration_specialist"), ("I.2", "Database administrator", "database_administrator"),
    ("I.3", "Database analyst/IM administrator", "database_analyst"), ("I.4", "Database modeller/IM modeller", "data_modeler"),
    ("I.5", "Information management architect", "data_architect"), ("I.6", "Network analyst", "network_analyst"), ("I.7", "Platform analyst", "platform_engineer"),
    ("I.8", "Storage architect", "infrastructure_architect"), ("I.9", "System administrator", "systems_administrator"),
    ("I.10", "Technical architect", "technical_architect"), ("I.11", "Technology architect", "technical_architect"),
    ("B.1", "Business analyst", "business_analyst"), ("B.2", "Business architect", "business_architect"), ("B.3", "Business consultant", "management_consultant"),
    ("B.4", "Business continuity/disaster recovery specialist", "business_continuity_specialist"),
    ("B.5", "Business process re-engineering consultant", "business_process_analyst"), ("B.6", "Business system analyst", "business_analyst"),
    ("B.7", "Business transformation architect", "business_architect"), ("B.8", "Call centre consultant", "management_consultant"),
    ("B.9", "Courseware developer", "learning_content_developer"), ("B.10", "Help desk specialist", "service_desk_analyst"),
    ("B.11", "Instructor, information technology", "it_trainer"), ("B.12", "Network support specialist", "network_analyst"),
    ("B.13", "Operations support specialist", "it_operations_analyst"), ("B.14", "Technical writer", "technical_writer"),
    ("P.1", "Change management consultant", "change_management_consultant"), ("P.2", "Enterprise architect", "enterprise_architect"),
    ("P.3", "Human resources consultant", "management_consultant"), ("P.4", "Organizational development consultant", "management_consultant"),
    ("P.5", "Project executive", "program_manager", "lead_principal"), ("P.6", "Project administrator", "project_coordinator"),
    ("P.7", "Project coordinator", "project_coordinator"), ("P.8", "Project leader", "project_manager"), ("P.9", "Project manager", "project_manager"),
    ("P.10", "Project scheduler", "project_coordinator"), ("P.11", "Quality assurance specialist/analyst", "quality_assurance_analyst"),
    ("P.12", "Risk management specialist", "risk_management_specialist"),
    ("P.13", "Independent IT project review team leader", "project_assurance_reviewer", "lead_principal"),
    ("P.14", "Independent IT project reviewer", "project_assurance_reviewer"),
    ("C.1", "Strategic IT security planning and protection consultant", "security_grc_analyst"),
    ("C.2", "IT security methodology, policy and procedures analyst", "security_grc_analyst"), ("C.3", "IT security TRA and C&A analyst", "security_grc_analyst"),
    ("C.4", "IT security product evaluation specialist", "security_engineer"), ("C.5", "Public key infrastructure specialist", "identity_access_management_engineer"),
    ("C.6", "IT security engineer", "security_engineer"), ("C.7", "IT security design specialist", "security_architect"),
    ("C.8", "Network security analyst", "security_analyst"), ("C.9", "IT security systems operator", "security_administrator"),
    ("C.10", "IT security installation specialist", "security_administrator"), ("C.11", "IT security vulnerability analysis specialist", "vulnerability_analyst"),
    ("C.12", "Incident management specialist", "incident_responder"), ("C.14", "IT security research and development specialist", "security_engineer"),
    ("C.15", "Computer forensics specialist", "digital_forensics_analyst"), ("C.16", "Privacy impact assessment specialist", "privacy_specialist"),
]:
    b = rest[0] if len(rest) > 0 else ""
    tech = rest[1] if len(rest) > 1 else ""
    mp(TB, URL_TB, t, r, b, tech, level_raw=code)
mp(TB, URL_TB, "Physical IT security specialist", "", level_raw="C.13", conf=0.0, status="flagged")   # physical security: out of scope
mp(TB, URL_TB, "Emanations security (TEMPEST) specialist", "", level_raw="C.17", conf=0.0, status="flagged")

GC = "UK G-Cloud 15"
DD = "UK DDaT framework"
GC_ROLES = [
    ("Business architect", "business_architect"), ("Data architect", "data_architect"), ("Enterprise architect", "enterprise_architect"),
    ("Network architect", "network_architect"), ("Security architect", "security_architect"), ("Solution architect", "solution_architect"),
    ("Technical architect", "technical_architect"), ("Chief data officer", "chief_data_officer"),
    ("Chief information security officer", "chief_information_security_officer"), ("Chief technology officer", "chief_technology_officer"),
    ("Cyber security audit and assurance", "security_grc_analyst"), ("Cyber security digital forensics", "digital_forensics_analyst"),
    ("Cyber security governance and risk management", "security_grc_analyst"), ("Cyber security incident response", "incident_responder"),
    ("Cyber security monitoring", "security_analyst"), ("Cyber security secure design", "security_engineer"),
    ("Cyber security testing", "penetration_tester"), ("Cyber security vulnerability management", "vulnerability_analyst"),
    ("Analytics engineer", "analytics_engineer"), ("Data analyst", "data_analyst"), ("Data engineer", "data_engineer"),
    ("Data ethicist", "data_ai_ethicist"), ("Data governance manager", "data_governance_manager"), ("Data scientist", "data_scientist"),
    ("Machine learning engineer", "machine_learning_engineer"), ("Performance analyst", "performance_analyst"),
    ("Application operations engineer", "application_support_analyst"), ("Business relationship manager", "business_relationship_manager"),
    ("Change and release manager", "change_release_manager"), ("Command and control centre manager", "it_operations_analyst"),
    ("End user computing engineer", "end_user_computing_engineer"), ("IT service manager", "it_service_manager"),
    ("Incident manager", "incident_manager"), ("Infrastructure engineer", "infrastructure_engineer"),
    ("Infrastructure operations engineer", "infrastructure_operations_engineer"), ("Problem manager", "problem_manager"),
    ("Service desk manager", "service_desk_manager"), ("Service transition manager", "service_transition_manager"),
    ("Business analyst", "business_analyst"), ("Delivery manager", "delivery_manager"), ("Digital portfolio manager", "portfolio_manager"),
    ("Product manager", "product_manager"), ("Programme delivery manager", "program_manager"), ("Service owner", "service_owner"),
    ("QAT analyst", "test_analyst"), ("Test engineer", "test_automation_engineer"), ("Test manager", "test_manager"),
    ("DevOps engineer", "devops_engineer"), ("Frontend developer", "frontend_developer"), ("Software developer", "software_developer"),
    ("Accessibility specialist", "accessibility_specialist"), ("Content designer", "content_designer"), ("Content strategist", "content_strategist"),
    ("Graphic designer", "graphic_designer"), ("Interaction designer", "interaction_designer"), ("Service designer", "service_designer"),
    ("Technical writer", "technical_writer"), ("User researcher", "user_researcher"),
]
for t, r in GC_ROLES:
    mp(GC, URL_GC, t, r)
for t, r in GC_ROLES + [
    ("Chief digital and information officer", "chief_information_officer"), ("Data and artificial intelligence ethicist", "data_ai_ethicist"),
    ("Development operations (DevOps) engineer", "devops_engineer"), ("Quality assurance test analyst", "test_analyst"),
    ("Digital evaluator", "performance_analyst"), ("Agile coach", "agile_coach"),
]:
    if t not in ("QAT analyst", "Data ethicist"):
        mp(DD, URL_DD, t, r)

GSA = "US GSA CALC+"
for t, r in [
    ("Business Analyst", "business_analyst"), ("Cloud Engineer", "cloud_engineer"), ("Cybersecurity Analyst", "security_analyst"),
    ("Data Engineer", "data_engineer"), ("Data Scientist", "data_scientist"), ("Database Administrator", "database_administrator"),
    ("DevOps Engineer", "devops_engineer"), ("Enterprise Architect", "enterprise_architect"), ("Help Desk Technician", "service_desk_analyst"),
    ("Information Security Analyst", "security_analyst"), ("Network Engineer", "network_engineer"), ("Program Manager", "program_manager"),
    ("Programmer Analyst", "programmer_analyst"), ("Project Manager", "project_manager"), ("Quality Assurance Analyst", "test_analyst"),
    ("Scrum Master", "scrum_master"), ("Software Developer", "software_developer"), ("Software Engineer", "software_developer"),
    ("Solutions Architect", "solution_architect"), ("Systems Analyst", "systems_analyst"), ("Systems Engineer", "systems_engineer"),
    ("Technical Writer", "technical_writer"),
]:
    mp(GSA, URL_CALC, t, r)
CDO = "GSA pricelist CDO Technologies"
for t, r, code, yrs in [
    ("Program Manager PM02", "program_manager", "PM02", "10"), ("Task Manager PM01", "project_manager", "PM01", ""),
    ("Data Architect ER03", "data_architect", "ER03", "12"), ("Senior Systems Engineer SY05", "systems_engineer", "SY05", ""),
    ("Computer Programmer IV CP04", "software_developer", "CP04", ""), ("Security Engineer IA03", "security_engineer", "IA03", ""),
    ("Help Desk Coordinator HD01", "service_desk_analyst", "HD01", ""),
]:
    b = "senior" if t.startswith("Senior") else ("lead_principal" if " IV " in t else "")
    mp(CDO, URL_CDO, t, r, b, level_raw=code, years_raw=yrs)
CW = "GSA pricelist Constellation West"
for t, r, b, yrs in [
    ("Computer Security Systems Engineer III", "security_engineer", "senior", "12"),
    ("IT Business SME (Subject Matter Expert)", "subject_matter_expert", "lead_principal", ""),
    ("IT Database Analyst III", "database_analyst", "senior", ""),
    ("IT Help Desk Support Services Specialist - Entry Level", "service_desk_analyst", "junior", "1"),
    ("IT Program Manager", "program_manager", "", ""), ("Software Developer - SME", "software_developer", "lead_principal", "10"),
]:
    mp(CW, URL_CW, t, r, b, years_raw=yrs)
TC = "GSA pricelist tCognition"
for t, r, b, tech, yrs in [
    ("Program Manager", "program_manager", "", "", "9"), ("Project Manager", "project_manager", "", "", ""),
    ("Sr. Project Manager", "project_manager", "senior", "", ""), ("Business Analyst", "business_analyst", "", "", "1"),
    ("Sr. Business Analyst", "business_analyst", "senior", "", ""), ("Java Developer", "software_developer", "", "java", "1"),
    ("Sr. Java Developer", "software_developer", "senior", "java", ""), ("Cloud Engineer", "cloud_engineer", "", "", ""),
    ("Sr. Cloud Engineer", "cloud_engineer", "senior", "", ""), ("Manual Tester", "test_analyst", "", "", ""),
    ("Oracle DBA", "database_administrator", "", "oracle", ""),
]:
    mp(TC, URL_TC, t, r, b, tech, years_raw=yrs)

# Generic aliases the rules fall back to after stripping modifiers/tech (source = TWM alias).
AL = "TWM alias"
for t, r, *rest in [
    ("Developer", "software_developer"), ("Programmer", "software_developer"), ("Coder", "software_developer"),
    ("Software Engineer", "software_developer"), ("Application Developer", "software_developer"), ("Applications Developer", "software_developer"),
    ("Full Stack Developer", "software_developer"), ("Backend Developer", "software_developer"), ("Back End Developer", "software_developer"),
    ("Technical Lead", "software_developer", "lead_principal"), ("Tech Lead", "software_developer", "lead_principal"),
    ("Front End Developer", "frontend_developer"), ("UI Developer", "frontend_developer"),
    ("DBA", "database_administrator"), ("Database Admin", "database_administrator"),
    ("Sysadmin", "systems_administrator"), ("System Administrator", "systems_administrator"), ("Systems Admin", "systems_administrator"),
    ("Help Desk", "service_desk_analyst"), ("Helpdesk", "service_desk_analyst"), ("Service Desk Analyst", "service_desk_analyst"),
    ("Help Desk Analyst", "service_desk_analyst"), ("Support Analyst", "application_support_analyst"),
    ("QA Analyst", "test_analyst"), ("QA Engineer", "test_analyst"), ("Test Analyst", "test_analyst"), ("Tester", "test_analyst"),
    ("Automation Engineer", "test_automation_engineer"), ("SDET", "test_automation_engineer"), ("Test Automation Engineer", "test_automation_engineer"),
    ("Test", "test_manager"), ("Test Lead", "test_manager"),
    ("UX Designer", "interaction_designer"), ("UI Designer", "interaction_designer"), ("UX/UI Designer", "interaction_designer"),
    ("UX Researcher", "user_researcher"), ("Interaction Design", "interaction_designer"), ("Service Design", "service_designer"),
    ("User Research", "user_researcher"), ("Content Design", "content_designer"), ("Graphic Design", "graphic_designer"),
    ("Accessibility", "accessibility_specialist"), ("Frontend Development", "frontend_developer"),
    ("Data Science", "data_scientist"), ("Data Engineering", "data_engineer"), ("Data Governance", "data_governance_manager"),
    ("Analytics Engineering", "analytics_engineer"), ("Data Ethics", "data_ai_ethicist"), ("Data and AI Ethics", "data_ai_ethicist"),
    ("Data and AI Ethicist", "data_ai_ethicist"), ("AI Ethicist", "data_ai_ethicist"), ("Data Ethics Lead", "data_ai_ethicist", "lead_principal"),
    ("Digital Evaluation", "performance_analyst"), ("Performance Analysis", "performance_analyst"),
    ("Business Analysis", "business_analyst"), ("Business Systems Analyst", "business_analyst"), ("Requirements Analyst", "business_analyst"),
    ("Functional Analyst", "business_analyst"), ("System Analyst", "systems_analyst"),
    ("Delivery Management", "delivery_manager"), ("Agile Delivery Management", "delivery_manager"), ("Agile Delivery Manager", "delivery_manager"),
    ("Agile Delivery", "delivery_manager"), ("IT Service", "it_service_manager"), ("Business Relationship", "business_relationship_manager"),
    ("Portfolio", "portfolio_manager"), ("Digital Portfolio Analyst", "portfolio_manager", "intermediate"), ("Product", "product_manager"),
    ("PMO Analyst", "project_coordinator"), ("Project Management Office Analyst", "project_coordinator"),
    ("Programme Manager", "program_manager"), ("Program Director", "program_manager", "lead_principal"),
    ("IT Service Management", "it_service_manager"), ("IT Service Analyst", "it_service_manager", "intermediate"),
    ("Service Desk", "service_desk_manager"), ("Service Desk Manager", "service_desk_manager"),
    ("Command and Control", "it_operations_analyst"), ("Operations Analyst", "it_operations_analyst"), ("Operational Control Manager", "it_operations_analyst", "lead_principal"),
    ("Business Relationship Management", "business_relationship_manager"),
    ("Change and Release Analyst", "change_release_manager", "intermediate"), ("Configuration Analyst", "change_release_manager", "intermediate"),
    ("Service Acceptance Analyst", "service_transition_manager", "intermediate"), ("Service Readiness Analyst", "service_transition_manager", "intermediate"),
    ("Problem Analyst", "problem_manager", "intermediate"), ("Major Incident Manager", "incident_manager", "senior"),
    ("Digital and Information Officer", "chief_information_officer"), ("CIO", "chief_information_officer"), ("CTO", "chief_technology_officer"),
    ("CDO", "chief_data_officer"), ("CISO", "chief_information_security_officer"),
    ("Solutions Architect", "solution_architect"), ("Software Architect", "application_architect"), ("Systems Architect", "technical_architect"),
    ("Architect", "solution_architect", "", "", "", "", 0.70),
    ("Scrum Master", "scrum_master"), ("SRE", "site_reliability_engineer"), ("DevOps", "devops_engineer"),
    ("ML Engineer", "machine_learning_engineer"), ("AI Engineer", "ai_engineer"), ("AI ML Engineer", "machine_learning_engineer"),
    ("AI/ML Engineer", "machine_learning_engineer"), ("Machine Learning", "machine_learning_engineer"),
    ("Network Admin", "network_administrator"), ("System Engineer", "systems_engineer"), ("Systems Engineer", "systems_engineer"),
    ("Infrastructure Analyst", "infrastructure_operations_engineer"),
    ("Information Security Analyst", "security_analyst"), ("Cyber Security Analyst", "security_analyst"), ("Cybersecurity Analyst", "security_analyst"),
    ("SOC Analyst", "security_analyst"), ("Security Engineer", "security_engineer"), ("Cyber Security Engineer", "security_engineer"),
    ("Penetration Tester", "penetration_tester"), ("Pen Tester", "penetration_tester"), ("Ethical Hacker", "penetration_tester"),
    ("Consultant", "management_consultant", "intermediate"), ("Engagement Manager", "engagement_manager"),
    ("Partner", "consulting_director_partner", "lead_principal"), ("Director", "consulting_director_partner", "lead_principal"),
    ("Associate Director", "consulting_director_partner", "lead_principal"), ("Managing Director", "consulting_director_partner", "lead_principal"),
    ("Subject Matter Expert", "subject_matter_expert", "lead_principal"), ("SME", "subject_matter_expert", "lead_principal"),
    ("Technical Writing", "technical_writer"), ("Head of Test", "test_manager", "lead_principal"),
]:
    b = rest[0] if len(rest) > 0 else ""
    conf = rest[4] if len(rest) > 4 else 0.90
    mp(AL, "", t, r, b, conf=conf)


# =============================================================================
# write
# =============================================================================
def write(name, header, rows):
    p = OUT / name
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {name}: {len(rows)} rows")


def main():
    OUT.mkdir(exist_ok=True)
    fams = {f[0] for f in FAMILIES}
    ids = [r[0] for r in R]
    assert len(ids) == len(set(ids)), "duplicate role ids"
    for r in R:
        assert r[1] in fams, f"{r[0]} bad family {r[1]}"
    for m in M:
        assert not m[3] or m[3] in ids, f"mapping '{m[2]}' -> unknown role {m[3]}"
    print(f"families={len(FAMILIES)} roles={len(R)} bands={len(B)} tech={len(TECH)} mappings={len(M)}")
    write("role_families.csv", ["family_id", "name", "definition", "scope_notes"], FAMILIES)
    write("canonical_roles.csv",
          ["role_id", "family_id", "name", "definition", "disambiguation_notes", "crosswalk_ddat", "crosswalk_tbips", "crosswalk_onet_soc", "crosswalk_sfia"],
          [(*r, "") for r in R])
    write("band_crosswalk.csv", ["source_scheme", "source_level", "twm_band", "notes"], B)
    write("tech_vocab.csv", ["tag", "label", "category", "aliases"], TECH)
    write("title_mappings.csv",
          ["observed_title", "source", "source_url", "canonical_role_id", "twm_band", "attr_technology", "attr_location",
           "attr_level_code_raw", "attr_years_raw", "confidence", "method", "reviewer", "status", "version_added", "source_class"],
          [(t, s, u, r, b, tech, "", lvl, yrs, f"{conf:.2f}", "rule", "", status, VERSION, "authored" if s == AL else "observed")
           for (s, u, t, r, b, tech, lvl, yrs, conf, status) in M])


if __name__ == "__main__":
    sys.exit(main())
