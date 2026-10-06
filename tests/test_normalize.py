"""Normalization rules (spec rules 1-6) against the seeded taxonomy."""
import pytest

from twm.pipeline.normalize import band_from_level_label, band_from_years, normalize_title, resolve
from twm.taxonomy import TaxonomyStore


@pytest.fixture(scope="module")
def store():
    return TaxonomyStore.load()


# --- rule 1: seniority modifiers -------------------------------------------------------------
@pytest.mark.parametrize("title,core,band,level", [
    ("Senior Software Developer", "software developer", "senior", None),
    ("Sr. Business Analyst", "business analyst", "senior", None),
    ("Jr Developer", "developer", "junior", None),
    ("Lead DevOps engineer - management", "devops engineer", "lead_principal", None),
    ("Principal Data Scientist", "data scientist", "lead_principal", None),
    ("Head of data science", "data science", "lead_principal", None),
    ("Computer Security Systems Engineer III", "computer security systems engineer", "senior", "iii"),
    ("Programmer Analyst 2", "programmer analyst", "intermediate", "2"),
    ("Systems Analyst Level 3", "systems analyst", "senior", "level 3"),
    ("Software Developer - SME", "software developer", "lead_principal", None),
    ("IT Help Desk Support Services Specialist - Entry Level", "it help desk support services specialist", "junior", None),
    ("Computer Programmer IV CP04", "computer programmer", "lead_principal", "iv"),
])
def test_seniority_capture(store, title, core, band, level):
    nt = normalize_title(title, store)
    assert nt.core == core
    assert nt.band_from_title == band
    if level is not None:
        assert nt.level_code_raw == level


@pytest.mark.parametrize("title,core,band", [
    ("IT Sr. Manager", "it manager", "senior"),
    ("Cybersecurity Senior Consultant", "cybersecurity consultant", "senior"),
    ("Health IT Jr Analyst", "health it analyst", "junior"),
])
def test_mid_title_seniority(store, title, core, band):
    nt = normalize_title(title, store)
    assert nt.core == core and nt.band_from_title == band


def test_mid_title_rule_leaves_short_and_role_titles_alone(store):
    # two-word titles are untouched by the mid-title rule; 'Project Lead' still resolves by its full-title alias
    assert resolve("Project Lead", store).canonical_role_id == "project_manager"
    assert normalize_title("Lead Developer", store).core == "developer"
    assert resolve("Network Operations Center (NOC) Technician", store).canonical_role_id == "network_operations_technician"


def test_bracketed_acronym_dropped(store):
    nt = normalize_title("Senior Business Intelligence Analyst (BIA)", store)
    assert nt.core == "business intelligence analyst" and nt.band_from_title == "senior"
    assert resolve("Business Intelligence Analyst (BIA)", store).canonical_role_id == "business_intelligence_analyst"


def test_dual_grade_title_is_ambiguous_by_design(store):
    r = resolve("Project Manager II / Test Manager", store)
    assert r.status == "ambiguous"
    assert set(r.candidates) == {"project_manager", "test_manager"}
    assert r.twm_band == "intermediate"          # from the 'II'
    assert "SOW context decides" in " ".join(r.notes)


def test_dual_label_agreeing_halves_resolve(store):
    r = resolve("Programmer / Developer", store)
    assert r.status == "resolved" and r.canonical_role_id == "software_developer"


def test_consulting_grades_are_bands_of_the_consultant_role(store):
    # Kyle, Oct 6 2026: Manager and Senior Manager are bands, not a separate role; engagement_manager is retired
    assert "engagement_manager" not in store.role_by_id
    assert resolve("IT Sr. Manager", store).canonical_role_id == "technology_consultant"
    assert resolve("IT Sr. Manager", store).twm_band == "lead_principal"
    assert resolve("IT Analyst", store).twm_band == "junior"
    assert resolve("Engagement Manager", store).canonical_role_id == "technology_consultant"


# --- rule 2: location ------------------------------------------------------------------------
@pytest.mark.parametrize("title,location,core", [
    ("Offshore Java Developer", "offshore", "developer"),
    ("Java Developer (Onshore)", "onshore", "developer"),
    ("Nearshore Test Analyst", "nearshore", "test analyst"),
])
def test_explicit_location_words_classify_directly(store, title, location, core):
    nt = normalize_title(title, store)
    assert nt.location == location
    assert nt.core == core


def test_place_name_gives_country_not_classification(store):
    nt = normalize_title("Senior Java Developer, Toronto", store)
    assert nt.core == "developer"
    assert nt.location is None and nt.location_country == "CA"
    r = resolve("Senior Java Developer, Toronto", store)
    assert r.attr_location is None and r.attr_location_raw == "toronto" and r.attr_location_country == "CA"


# --- rule 3: technology ----------------------------------------------------------------------
@pytest.mark.parametrize("title,tags", [
    ("Java Developer", ["java"]),
    (".NET Developer", ["dotnet"]),
    ("C# Developer", ["dotnet"]),
    ("Mainframe COBOL Developer", ["mainframe"]),
    ("SQL Server DBA", ["sql_server"]),
    ("Oracle DBA", ["oracle"]),
    ("SAP ABAP Developer", ["sap"]),
    ("Wireless Network Engineer", ["wireless"]),
])
def test_tech_capture(store, title, tags):
    assert normalize_title(title, store).tech_tags == tags


def test_tech_is_attribute_not_role(store):
    r = resolve("Sr. Java Developer", store)
    assert r.canonical_role_id == "software_developer"
    assert r.attr_technology == "java"
    assert r.twm_band == "senior"


def test_packaged_platform_routes_to_pkg_family(store):
    for title, role in [("SAP ABAP Developer", "packaged_application_developer"),
                        ("Salesforce Administrator", "packaged_application_administrator"),
                        ("Workday Functional Consultant", "packaged_application_functional_consultant"),
                        ("ServiceNow Architect", "packaged_application_architect")]:
        r = resolve(title, store)
        assert r.canonical_role_id == role, title
        assert r.family_id == "pkg"


# --- rule 4: exact/alias match ---------------------------------------------------------------
def test_full_title_match_beats_core(store):
    # 'Project Lead' is a whole-title alias; the leading word must not be read as a band modifier
    r = resolve("Project Lead", store)
    assert r.canonical_role_id == "project_manager"
    assert r.matched_on == "full_title"


def test_authored_band_beats_modifier_rule(store):
    r = resolve("Associate Director", store)
    assert r.canonical_role_id == "consulting_director_partner"
    assert r.twm_band == "lead_principal"


def test_case_and_punctuation_insensitive(store):
    a = resolve("business analyst", store)
    b = resolve("Business  Analyst.", store)
    assert a.canonical_role_id == b.canonical_role_id == "business_analyst"


# --- rule 6: flagging ------------------------------------------------------------------------
def test_unknown_title_is_flagged_not_guessed(store):
    r = resolve("Chief Happiness Wrangler", store)
    assert r.status == "flagged"
    assert r.canonical_role_id is None


def test_generic_title_flagged_by_seed(store):
    assert resolve("IT Specialist", store).status == "flagged"


# --- band precedence -------------------------------------------------------------------------
def test_source_level_beats_title_modifier(store):
    # Texas prices 'Senior Web Developer' at Intern Level 1 too: the source level wins, evidence is kept
    r = resolve("Senior Web Developer", store, source_scheme="Texas DIR", source_level="Intern Level 1")
    assert r.twm_band == "junior"
    assert r.band_source == "source_level"
    assert r.attr_level_code_raw == "Intern Level 1"


def test_years_beat_modifier_and_default(store):
    assert resolve("Program Manager", store, years=9).twm_band == "senior"
    assert resolve("Program Manager", store, years=13).twm_band == "lead_principal"


def test_no_evidence_means_unbanded_never_a_default(store):
    r = resolve("Program Manager", store)
    assert r.status == "resolved" and r.canonical_role_id == "program_manager"
    assert r.twm_band is None and r.band_source is None
    assert r.needs_band_review is True


def test_derived_band_from_label(store):
    r = resolve("Senior operations analyst", store, source_scheme="UK G-Cloud 15", source_level="Senior operations analyst")
    assert r.canonical_role_id == "it_operations_analyst"
    assert r.twm_band == "senior"
    assert r.band_source == "source_level_derived"


@pytest.mark.parametrize("label,band", [
    ("Trainee business architect", "junior"), ("Associate data analyst", "junior"), ("Data engineer", "intermediate"),
    ("Senior data engineer", "senior"), ("Lead data engineer", "lead_principal"), ("Head of data science", "lead_principal"),
    ("Operational control manager", "lead_principal"), ("Service desk analyst", "intermediate"),
])
def test_band_from_level_label(label, band):
    assert band_from_level_label(label) == band


@pytest.mark.parametrize("years,band", [(0, "junior"), (2.9, "junior"), (3, "intermediate"), (6.9, "intermediate"),
                                        (7, "senior"), (11.9, "senior"), (12, "lead_principal"), (25, "lead_principal")])
def test_band_from_years(store, years, band):
    assert band_from_years(years, store) == band


def test_same_words_different_source_resolve_by_source(store):
    # "IT Manager": a line-management role in NY HBITS, a consulting grade in Deloitte's price list
    assert resolve("IT Manager", store, source="NY OGS HBITS 23158").canonical_role_id == "it_manager"
    assert resolve("IT Manager", store, source="Deloitte GSA MAS price list").canonical_role_id == "technology_consultant"
    r = resolve("IT Manager", store)  # no source: the disagreement is surfaced, never guessed
    assert r.status == "ambiguous" and set(r.candidates) == {"it_manager", "technology_consultant"}
