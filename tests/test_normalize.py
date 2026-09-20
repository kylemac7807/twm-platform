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


@pytest.mark.parametrize("title,client,expected", [
    ("Java Developer, Toronto", "CA", "onshore"),
    ("Java Developer, New York", "CA", "nearshore"),   # a US resource is nearshore for a Canadian bank
    ("Java Developer, New York", "US", "onshore"),
    ("Java Developer, Toronto", "US", "nearshore"),
    ("Java Developer, Bangalore", "CA", "offshore"),
    ("Java Developer, Poland", "GB", "nearshore"),
    ("Java Developer, Poland", "CA", "offshore"),
    ("Offshore Java Developer", "CA", "offshore"),     # an explicit word wins regardless of client
])
def test_location_is_client_relative(store, title, client, expected):
    assert resolve(title, store, client_country=client).attr_location == expected


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
