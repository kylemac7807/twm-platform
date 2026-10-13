"""Suggestions on the task card (work/workbench/plan-v3.md step 4, retrained Oct 13, 2026 after Kyle's first answer).
Kyle's rule: a seniority word must never pick the role; 'analyst' on its own means business analyst; 'Associate' means junior;
and the analyst's own earlier answers come first."""
from twm.taxonomy import TaxonomyStore
from twm.workbench.suggest import band_from_words, load_core_defaults, suggest

store = TaxonomyStore.load()


def test_associate_analyst_is_a_junior_business_analyst_not_a_test_analyst():
    """Kyle's first answer, Oct 13: 'Associate means junior and analyst typically refers to business analyst.'"""
    s = suggest("Associate analyst", store)
    assert s["core"] == "analyst" and s["band"] == "junior" and s["band_word"] == "Associate"
    assert s["suggestions"][0]["id"] == "business_analyst" and "usually means" in s["suggestions"][0]["why"]
    assert "test_analyst" not in {x["id"] for x in s["suggestions"][:2]}


def test_the_analysts_own_answers_come_first():
    saved = [dict(observed_title="Associate analyst", canonical_role_id="data_analyst", twm_band="junior", scope="client")]
    s = suggest("Senior analyst", store, saved=saved)
    assert s["suggestions"][0]["id"] == "data_analyst" and "you answered" in s["suggestions"][0]["why"]
    assert s["band"] == "senior"
    s2 = suggest("Associate analyst", store, saved=saved)
    assert s2["suggestions"][0]["id"] == "data_analyst" and s2["suggestions"][1]["id"] == "business_analyst"


def test_rules_dual_titles_and_similarity_keep_their_places():
    s = suggest("Senior Java Developer", store)
    assert s["suggestions"][0]["id"] == "software_developer" and s["suggestions"][0]["why"] == "the rules place it here"
    assert s["tech_found"] == ["java"] and s["band"] == "senior"
    s = suggest("Project Manager I / Test Leads", store)
    assert {x["id"] for x in s["suggestions"][:2]} == {"project_manager", "test_manager"}
    s = suggest("Lead cyber security governance and risk manager", store)
    assert s["band"] == "lead_principal" and s["suggestions"] and all("similar to" in x["why"] or "usually" in x["why"] for x in s["suggestions"])


def test_core_defaults_file_is_well_formed_and_points_at_real_roles():
    d = load_core_defaults()
    assert d["analyst"]["canonical_role_id"] == "business_analyst" and d["analyst"]["decided_by"].startswith("Kyle")
    for core, row in d.items():
        assert row["canonical_role_id"] in store.role_by_id, core
        for alt in (row.get("alternatives") or "").split(";"):
            assert not alt.strip() or alt.strip() in store.role_by_id, (core, alt)


def test_band_from_words_uses_the_crosswalk_not_a_guess():
    assert band_from_words("Associate consultant", store) == ("junior", "Associate")
    assert band_from_words("Principal engineer", store)[0] == "lead_principal"
    assert band_from_words("Data engineer", store) == (None, None)
