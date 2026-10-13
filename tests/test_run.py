"""The end-to-end run consults the analyst's saved answers before asking the model or a person (resolve once, applied to people;
decided with Kyle, Oct 13, 2026)."""
from twm.llm import ModelConfig
from twm.pipeline.run import resolve_title
from twm.taxonomy import TaxonomyStore

from test_ledger import _ledger_with_queue


def test_a_saved_answer_is_used_on_a_re_run_and_the_model_is_not_asked(tmp_path):
    led, rec, store = _ledger_with_queue(tmp_path)
    cfg = ModelConfig(model="none")
    before = resolve_title(led, store, None, cfg, "Operations", context="", source="bank-a / Acme", vendor="Acme", set_id=rec.document_id)
    assert before.result.status == "flagged" and not before.used_model                     # no answer yet, no model: stays flagged
    qids = led.title_queue_groups()[0]["queue_ids"]
    led.decide_title(qids, role_id="systems_engineer", band="senior", reason="the SOW says so", decided_by="Kyle McNamara", technology="java", scope="vendor")
    after = resolve_title(led, store, None, cfg, "Operations", context="", source="bank-a / Acme", vendor="Acme", set_id="a-later-contract-set")
    r = after.result
    assert r.status == "resolved" and r.method == "analyst" and r.canonical_role_id == "systems_engineer" and r.twm_band == "senior"
    assert r.attr_technology == "java" and r.confidence == 1.0 and not after.used_model
    assert any("saved answer" in n and "Kyle McNamara" in n for n in r.notes)              # provenance travels with the row
    other = resolve_title(led, store, None, cfg, "Operations", context="", source="bank-b / Other", vendor="Other", set_id=None)
    assert other.result.status == "flagged"                                                 # another vendor's documents are not touched
    rules = resolve_title(led, store, None, cfg, "Senior Java Developer", context="", source="bank-a / Acme", vendor="Acme", set_id=None)
    assert rules.result.status == "resolved" and rules.result.method != "analyst"            # the rules still come first
    led.close()
