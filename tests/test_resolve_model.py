"""Normalization model step (M2 step 5): rules first, similarity, one model call, confidence floor, write-back. Offline."""
import json

import pytest

from twm import llm
from twm.llm import FakeModel
from twm.pipeline.resolve_model import resolve_with_model, similar_roles
from twm.taxonomy import TaxonomyStore


@pytest.fixture()
def store():
    return TaxonomyStore.load()   # fresh per test: the model step writes back


def test_known_title_never_calls_the_model(store):
    m = FakeModel([])
    o = resolve_with_model("Sr. Java Developer", store, m)
    assert o.result.status == "resolved" and not o.used_model and m.calls == []


def test_similarity_proposes_sensible_candidates(store):
    c = [rid for rid, _, _ in similar_roles(store, "Principal Cloud Platform Engineer")]
    assert c and ("platform_engineer" in c or "cloud_engineer" in c)


def test_model_answer_above_floor_is_accepted_and_written_back(store):
    def answer(system, user):
        assert "Candidate roles" in user and "platform_engineer" in user
        return json.dumps({"canonical_role_id": "platform_engineer", "twm_band": "lead_principal", "attr_technology": None,
                           "attr_location": None, "reasoning": "Platform engineer per the internal-platform note; 'Principal' states the band.",
                           "confidence": 0.9, "abstain": False})
    m = FakeModel(fn=answer)
    llm.LOG.clear()
    o = resolve_with_model("Principal Cloud Platform Engineer", store, m, context="builds the internal developer platform")
    assert o.used_model and o.result.status == "resolved"
    assert o.result.canonical_role_id == "platform_engineer" and o.result.twm_band == "lead_principal"
    assert o.new_mapping is not None and o.new_mapping.method == "model"
    # resolve once: the second time is a lookup, no model call
    m2 = FakeModel([])
    again = resolve_with_model("Principal Cloud Platform Engineer", store, m2)
    assert again.result.status == "resolved" and not again.used_model


def test_model_below_floor_or_abstaining_stays_flagged(store):
    low = FakeModel(fn=lambda s, u: json.dumps({"canonical_role_id": "platform_engineer", "reasoning": "unsure", "confidence": 0.5, "abstain": False}))
    o = resolve_with_model("Principal Cloud Platform Engineer", store, low)
    assert o.result.status == "flagged" and o.new_mapping is None and o.result.candidates
    ab = FakeModel(fn=lambda s, u: json.dumps({"canonical_role_id": None, "reasoning": "none fit", "confidence": 0.9, "abstain": True}))
    o2 = resolve_with_model("Principal Cloud Platform Engineer", store, ab)
    assert o2.result.status == "flagged"


def test_model_cannot_pick_a_role_outside_the_candidates(store):
    rogue = FakeModel(fn=lambda s, u: json.dumps({"canonical_role_id": "chief_data_officer", "reasoning": "x", "confidence": 0.99, "abstain": False}))
    o = resolve_with_model("Principal Cloud Platform Engineer", store, rogue)
    assert o.result.status == "flagged"


def test_model_never_sets_location_from_a_city(store):
    sneaky = FakeModel(fn=lambda s, u: json.dumps({"canonical_role_id": "platform_engineer", "attr_location": "onshore", "reasoning": "x", "confidence": 0.9, "abstain": False}))
    o = resolve_with_model("Principal Cloud Platform Engineer, Toronto", store, sneaky)
    # the rules captured Toronto as a place; the model's 'onshore' must not override the flag-for-analyst decision
    assert o.result.needs_location_review is True
    assert o.result.attr_location is None
