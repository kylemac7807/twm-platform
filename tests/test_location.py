"""Location handling (decided with Kyle, Sept 19, 2026).

Place names are never classified by the platform. An analyst categorizes each one once, with a
reason; after that it is a deterministic lookup. Only the words onshore / nearshore / offshore
written in the title classify directly.
"""
import pytest

from twm.pipeline.location_rules import LocationRule, as_lookup, load_location_rules, record_decision, save_location_rules
from twm.pipeline.normalize import resolve
from twm.taxonomy import TaxonomyStore


@pytest.fixture(scope="module")
def store():
    return TaxonomyStore.load()


@pytest.mark.parametrize("title,expected", [
    ("Offshore Java Developer", "offshore"),
    ("Java Developer (Onshore)", "onshore"),
    ("Nearshore Test Analyst", "nearshore"),
])
def test_explicit_words_classify_for_any_client(store, title, expected):
    for client in (None, "CA", "US", "GB"):
        r = resolve(title, store, client_country=client)
        assert r.attr_location == expected
        assert r.location_source == "explicit_word"
        assert r.needs_location_review is False


@pytest.mark.parametrize("title,client", [
    ("Java Developer, New York", "CA"),    # expensive market: likely onshore-equivalent for a Canadian bank
    ("Java Developer, Buffalo", "CA"),     # might be nearshore; it depends
    ("Java Developer, Toronto", "CA"),     # same country is NOT always onshore
    ("Java Developer, Toronto", "US"),     # almost always nearshore, but still the analyst's call
    ("Java Developer, Bangalore", "CA"),   # obviously offshore, and still not decided by the platform
])
def test_place_names_are_flagged_never_classified(store, title, client):
    r = resolve(title, store, client_country=client)
    assert r.attr_location is None
    assert r.needs_location_review is True
    assert r.attr_location_raw and r.attr_location_country       # the evidence is kept
    assert r.canonical_role_id == "software_developer"           # the role still resolves


def test_suggestion_is_a_hint_not_an_answer(store):
    r = resolve("Java Developer, Bangalore", store, client_country="CA")
    assert r.location_suggestion == "offshore" and r.attr_location is None
    assert resolve("Java Developer, Toronto", store, client_country="US").location_suggestion == "nearshore"
    # no hint where Kyle said geography cannot decide
    assert resolve("Java Developer, New York", store, client_country="CA").location_suggestion is None
    assert resolve("Java Developer, Toronto", store, client_country="CA").location_suggestion is None


def test_analyst_decision_becomes_a_deterministic_lookup(store):
    rules: list[LocationRule] = []
    record_decision(rules, "CA", "New York", "onshore", "analyst-1", "Tier-1 US market; rates at or above Toronto")
    record_decision(rules, "CA", "Buffalo", "nearshore", "analyst-1", "Low-cost US market close to the border")
    lookup = as_lookup(rules)
    ny = resolve("Sr. Java Developer, New York", store, client_country="CA", location_rules=lookup)
    assert ny.attr_location == "onshore" and ny.location_source == "analyst_rule" and ny.needs_location_review is False
    assert resolve("Java Developer, Buffalo", store, client_country="CA", location_rules=lookup).attr_location == "nearshore"
    # a rule for one client says nothing about another
    other = resolve("Java Developer, New York", store, client_country="GB", location_rules=lookup)
    assert other.attr_location is None and other.needs_location_review is True


def test_client_specific_key_overrides_country(store):
    rules: list[LocationRule] = []
    record_decision(rules, "bank-a", "Toronto", "nearshore", "analyst-2", "Bank A is headquartered in Vancouver and treats Toronto as a separate market")
    r = resolve("Java Developer, Toronto", store, client_country="CA", client_key="bank-a", location_rules=as_lookup(rules))
    assert r.attr_location == "nearshore"


def test_redeciding_deprecates_never_edits(tmp_path):
    rules: list[LocationRule] = []
    record_decision(rules, "CA", "Buffalo", "nearshore", "analyst-1", "first view")
    record_decision(rules, "CA", "Buffalo", "onshore", "analyst-2", "rates converged with Toronto")
    assert [r.status for r in rules] == ["deprecated", "active"]
    assert as_lookup(rules)[("ca", "buffalo")] == "onshore"
    p = tmp_path / "location_rules.csv"
    assert save_location_rules(rules, p) == 2
    assert [r.classification for r in load_location_rules(p)] == ["nearshore", "onshore"]
