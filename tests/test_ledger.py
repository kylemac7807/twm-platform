"""Ledger (M2 step 6): append never overwrite, supersede on re-run, confidence gates counting, currency as a derived column."""
from decimal import Decimal

import pytest

from twm.pipeline.contracts import RateRow
from twm.pipeline.ingest import register
from twm.pipeline.ledger import Ledger
from twm.pipeline.models import SourceRef
from twm.pipeline.normalize import resolve
from twm.taxonomy import TaxonomyStore


def _row(title, rate, conf=0.95, currency="USD"):
    return RateRow(observed_title=title, rate_value=Decimal(rate), rate_as_stated=f"${rate}", currency=currency, rate_unit="hour",
                   period_raw="Year 1", confidence=conf, source_ref=SourceRef(document_id="d", page=8, bbox=(1, 2, 3, 4), quote="q"))


def test_append_supersede_and_counting(tmp_path):
    store = TaxonomyStore.load()
    p = tmp_path / "doc.txt"; p.write_text("STATEMENT OF WORK rate card", encoding="utf-8")
    rec = register(p)
    led = Ledger(tmp_path / "ledger.sqlite")
    led.upsert_document(rec)
    led.start_run("run1", "local", "fake", "0.1")
    r1 = resolve("Senior Java Developer", store)
    led.add_observation("run1", rec, _row("Senior Java Developer", "140.00"), r1, vendor="Acme", client="bank-a", effective_date="2027-01-01", scan_quality="native")
    led.add_observation("run1", rec, _row("Senior Java Developer", "141.00", conf=0.6), r1, vendor="Acme", client="bank-a", effective_date="2027-01-01", scan_quality="native")
    unb = resolve("Program Manager", store)   # unbanded: resolved role, no band -> still resolved, counted
    led.add_observation("run1", rec, _row("Program Manager", "200.00"), unb, vendor="Acme", client="bank-a", effective_date="2027-01-01", scan_quality="native")
    flagged = resolve("Chief Happiness Wrangler", store)
    led.add_observation("run1", rec, _row("Chief Happiness Wrangler", "99.00"), flagged, vendor="Acme", client="bank-a", effective_date="2027-01-01", scan_quality="native")
    c = led.counts()
    assert c["observations_live"] == 4
    assert c["counted"] == 2   # the 0.6-confidence row and the flagged row exist but do not count
    # re-run supersedes, never overwrites
    led.start_run("run2", "local", "fake", "0.1")
    n = led.supersede_document(rec.document_id, "run2")
    assert n == 4
    led.add_observation("run2", rec, _row("Senior Java Developer", "140.00"), r1, vendor="Acme", client="bank-a", effective_date="2027-01-01", scan_quality="native")
    c = led.counts()
    assert c["observations_live"] == 1 and c["observations_superseded"] == 4
    led.close()


def test_currency_is_derived_never_converted_in_place(tmp_path):
    store = TaxonomyStore.load()
    p = tmp_path / "doc.txt"; p.write_text("rate card", encoding="utf-8")
    rec = register(p)
    led = Ledger(tmp_path / "l.sqlite"); led.upsert_document(rec); led.start_run("r", "local", "fake", "0.1")
    res = resolve("Software Developer", store)
    led.add_observation("r", rec, _row("Software Developer", "650.00", currency="GBP"), res, vendor="Accenture", client=None, effective_date="2026-01-27",
                        scan_quality="web", reporting_currency="CAD", fx=(Decimal("1.72"), "2026-01-27", "Bank of Canada daily rate"))
    row = led.live_rows()[0]
    assert row["rate_value"] == "650.00" and row["currency"] == "GBP"            # as stated
    assert row["reporting_currency"] == "CAD" and row["reporting_value"] == "1118.00"
    assert row["fx_rate"] == "1.72" and row["fx_source"].startswith("Bank of Canada")
    led.close()


# ---------------------------------------------------------------- workbench decisions (work/workbench/spec.md)
def _ledger_with_queue(tmp_path, client="bank-a", name="doc.txt"):
    """A document with: two flagged 'Operations' rows (queued twice, as the pipeline does), one resolved row,
    and one row whose place name 'Buffalo' needs an analyst decision."""
    store = TaxonomyStore.load()
    p = tmp_path / name; p.write_text("rate card " + name, encoding="utf-8")
    rec = register(p)
    led = Ledger(tmp_path / "ledger.sqlite")
    led.upsert_document(rec); led.start_run("run1", "local", "fake", "0.1")
    flagged = resolve("Operations", store)
    assert flagged.status == "flagged"
    for rate in ("99.50", "101.00"):
        led.add_observation("run1", rec, _row("Operations", rate), flagged, vendor="Acme", client=client, effective_date=None, scan_quality="native")
        led.queue("run1", rec.document_id, "title", "Operations", "no rule match; needs model/human resolution")
    ok = resolve("Senior Java Developer", store)
    led.add_observation("run1", rec, _row("Senior Java Developer", "140.00"), ok, vendor="Acme", client=client, effective_date=None, scan_quality="native")
    place = resolve("Developer (Buffalo)", store)
    assert place.needs_location_review
    led.add_observation("run1", rec, _row("Developer (Buffalo)", "120.00"), place, vendor="Acme", client=client, effective_date=None, scan_quality="native")
    led.queue("run1", rec.document_id, "location", "Developer (Buffalo)", "place 'buffalo' needs an analyst decision")
    return led, rec, store


def test_title_decision_resolves_every_row_for_that_client_and_recomputes_counted(tmp_path):
    led, rec, store = _ledger_with_queue(tmp_path)
    groups = led.title_queue_groups()
    assert len(groups) == 1 and groups[0]["title"] == "Operations" and groups[0]["client"] == "bank-a"
    assert len(groups[0]["queue_ids"]) == 2 and groups[0]["rows_affected"] == 2 and groups[0]["rows_unlocked"] == 2
    with pytest.raises(ValueError):
        led.decide_title(groups[0]["queue_ids"], role_id="systems_engineer", band=None, reason="  ", decided_by="Kyle McNamara")
    ids = led.decide_title(groups[0]["queue_ids"], role_id="systems_engineer", band=None, reason="Operations on this exhibit is the systems operations role", decided_by="Kyle McNamara")
    assert len(ids) == 2
    rows = [r for r in led.live_rows(rec.document_id) if r["observed_title"] == "Operations"]
    assert all(r["canonical_role_id"] == "systems_engineer" and r["twm_band"] is None and r["band_source"] == "analyst" for r in rows)
    assert all(r["resolution_status"] == "resolved" and r["counted"] == 1 and r["needs_band_review"] == 1 for r in rows)   # unbanded by default, counted
    assert led.queue_summary() == {"location": 1}                     # both title items closed, the place still waits
    assert led.title_queue_groups() == []
    md = [tuple(r) for r in led.conn.execute("SELECT method, decided_by, canonical_role_id FROM mapping_decisions")]
    assert md == [("analyst", "Kyle McNamara", "systems_engineer")]   # one mapping decision for the group, not one per row
    led.close()


def test_leave_flagged_is_recorded_and_changes_no_row(tmp_path):
    led, rec, _ = _ledger_with_queue(tmp_path)
    qids = led.title_queue_groups()[0]["queue_ids"]
    led.decide_title(qids, role_id=None, band=None, reason="not placeable without the SOW text", decided_by="Kyle McNamara")
    rows = [r for r in led.live_rows(rec.document_id) if r["observed_title"] == "Operations"]
    assert all(r["resolution_status"] == "flagged" and r["counted"] == 0 for r in rows)
    assert led.queue_summary() == {"location": 1} and led.pending_codification()["title_mappings"] == []
    led.close()


def test_a_second_decision_supersedes_the_first_and_both_remain(tmp_path):
    led, rec, _ = _ledger_with_queue(tmp_path)
    qids = led.title_queue_groups()[0]["queue_ids"]
    first = led.decide_title(qids, role_id="systems_engineer", band=None, reason="first look", decided_by="Kyle McNamara")
    second = led.decide_title(qids, role_id="systems_engineer", band="senior", reason="the SOW says 8+ years", decided_by="Kyle McNamara", scope="everyone")
    hist = led.decision_history("Operations")
    assert [h["id"] for h in hist] == first + second
    assert all(h["superseded_by"] in second for h in hist if h["id"] in first)
    assert all(h["superseded_by"] is None for h in hist if h["id"] in second)
    rows = [r for r in led.live_rows(rec.document_id) if r["observed_title"] == "Operations"]
    assert all(r["twm_band"] == "senior" and r["needs_band_review"] == 0 for r in rows)
    assert len(led.pending_codification()["title_mappings"]) == 1   # only the live decision is exported, and only because it is for everyone
    led.close()


def test_location_decision_applies_to_that_client_only(tmp_path):
    led, rec, store = _ledger_with_queue(tmp_path)
    p2 = tmp_path / "other.txt"; p2.write_text("rate card other", encoding="utf-8")
    rec2 = register(p2); led.upsert_document(rec2)
    place = resolve("Developer (Buffalo)", store)
    led.add_observation("run1", rec2, _row("Developer (Buffalo)", "90.00"), place, vendor="Acme", client="bank-b", effective_date=None, scan_quality="native")
    led.queue("run1", rec2.document_id, "location", "Developer (Buffalo)", "place 'buffalo' needs an analyst decision")
    qid = [q["id"] for q in led.queue_items("location") if q["document_id"] == rec.document_id]
    with pytest.raises(ValueError):
        led.decide_location(qid, classification="abroad", reason="x", decided_by="Kyle McNamara")
    led.decide_location(qid, classification="nearshore", reason="Buffalo is nearshore for this Toronto bank", decided_by="Kyle McNamara")
    a = [r for r in led.live_rows(rec.document_id) if r["observed_title"] == "Developer (Buffalo)"][0]
    b = [r for r in led.live_rows(rec2.document_id) if r["observed_title"] == "Developer (Buffalo)"][0]
    assert a["attr_location"] == "nearshore" and a["needs_location_review"] == 0
    assert b["attr_location"] is None and b["needs_location_review"] == 1       # the other client still waits
    exp = led.pending_codification()["location_rules"]
    assert len(exp) == 1 and exp[0]["place"] == "buffalo" and exp[0]["client_key"] == "bank-a" and exp[0]["classification"] == "nearshore"
    led.close()


def test_codification_export_matches_the_taxonomy_columns_and_writes_nothing_to_taxonomy(tmp_path):
    import hashlib
    from pathlib import Path
    tax = Path(__file__).resolve().parents[1] / "taxonomy"
    before = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in tax.glob("*.csv")}
    led, rec, _ = _ledger_with_queue(tmp_path)
    led.decide_title(led.title_queue_groups()[0]["queue_ids"], role_id="systems_engineer", band=None, reason="r", decided_by="Kyle McNamara", scope="everyone")
    led.decide_location([q["id"] for q in led.queue_items("location")], classification="onshore", reason="r", decided_by="Kyle McNamara")
    exp = led.pending_codification()
    t = exp["title_mappings"][0]; l = exp["location_rules"][0]
    assert list(t.keys())[1:] == (tax / "title_mappings.csv").read_text(encoding="utf-8").splitlines()[0].split(",")
    assert list(l.keys())[1:] == (tax / "location_rules.csv").read_text(encoding="utf-8").splitlines()[0].split(",")
    assert t["method"] == "human" and t["reviewer"] == "Kyle McNamara" and t["twm_band"] == ""
    led.mark_applied(t["decision_id"])
    assert led.pending_codification()["title_mappings"] == []
    after = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in tax.glob("*.csv")}
    assert before == after
    led.close()


def test_documents_by_contract_set_and_intake_decision(tmp_path):
    led, rec, _ = _ledger_with_queue(tmp_path)
    led.queue("run1", rec.document_id, "intake", rec.filename, "classification 'sow' is weak (0.50): confirm")
    qid = led.queue_items("intake")[0]["id"]
    led.decide_intake(qid, decision={"doc_class": "msa"}, reason="it is the master agreement", decided_by="Kyle McNamara")
    sets = led.documents_by_set()
    assert len(sets) == 1 and sets[0]["documents"][0]["doc_class"] == "msa" and sets[0]["documents"][0]["class_confidence"] == 1.0
    assert led.queue_summary() == {"location": 1, "title": 2}
    led.close()


# ---------------------------------------------------------------- plan v3 (Oct 13): scope, park, saved answers, contract sets
def test_scope_decides_which_rows_an_answer_reaches(tmp_path):
    """A set-scoped answer touches only that contract set; a client-scoped one every set of the client; neither is exported."""
    led, rec, store = _ledger_with_queue(tmp_path)
    p2 = tmp_path / "other-set.txt"; p2.write_text("rate card other set", encoding="utf-8")
    rec2 = register(p2); led.upsert_document(rec2)
    flagged = resolve("Operations", store)
    led.add_observation("run1", rec2, _row("Operations", "77.00"), flagged, vendor="Acme", client="bank-a", effective_date=None, scan_quality="native")
    led.queue("run1", rec2.document_id, "title", "Operations", "no rule match")
    g = [x for x in led.title_queue_groups(set_id=rec.document_id)][0]
    assert g["rows_in_set"] == 2 and g["rows_affected"] == 3                          # two in this set, three for the client
    led.decide_title(g["queue_ids"], role_id="systems_engineer", band=None, reason="this exhibit only", decided_by="Kyle McNamara", scope="set")
    a = [r for r in led.live_rows(rec.document_id) if r["observed_title"] == "Operations"]
    b = [r for r in led.live_rows(rec2.document_id) if r["observed_title"] == "Operations"]
    assert all(r["canonical_role_id"] == "systems_engineer" for r in a) and all(r["canonical_role_id"] is None for r in b)
    assert led.pending_codification()["title_mappings"] == []
    g2 = led.title_queue_groups(set_id=rec2.document_id)[0]
    led.decide_title(g2["queue_ids"], role_id="systems_engineer", band="senior", reason="whole client", decided_by="Kyle McNamara")   # default: client
    b = [r for r in led.live_rows(rec2.document_id) if r["observed_title"] == "Operations"]
    assert all(r["canonical_role_id"] == "systems_engineer" and r["twm_band"] == "senior" for r in b)
    assert led.pending_codification()["title_mappings"] == []
    with pytest.raises(ValueError):
        led.decide_title(g2["queue_ids"], role_id="systems_engineer", band=None, reason="r", decided_by="Kyle McNamara", scope="galaxy")
    led.close()


def test_saved_answers_are_found_set_first_then_client(tmp_path):
    """A re-run must find the analyst's answer: the set-scoped one for that set, else the client-scoped one, else nothing."""
    led, rec, _ = _ledger_with_queue(tmp_path)
    assert led.saved_answer("Operations", "bank-a", rec.document_id) is None
    qids = led.title_queue_groups()[0]["queue_ids"]
    led.decide_title(qids, role_id="systems_engineer", band=None, reason="client-wide", decided_by="Kyle McNamara", technology="java, azure")
    ans = led.saved_answer("Operations", "bank-a", "some-other-set")
    assert ans["canonical_role_id"] == "systems_engineer" and ans["scope"] == "client" and ans["attr_technology"] == "java,azure"
    assert led.saved_answer("Operations", "bank-b", None) is None                      # another client: not theirs
    led.decide_title(qids, role_id="support_engineer" if "support_engineer" in TaxonomyStore.load().role_by_id else "systems_engineer",
                     band="junior", reason="this set is different", decided_by="Kyle McNamara", scope="set")
    assert led.saved_answer("Operations", "bank-a", rec.document_id)["scope"] == "set"
    assert led.saved_answer("Operations", "bank-a", "some-other-set") is None               # re-answering the same item replaced the client-wide answer
    led.close()


def test_park_sets_an_item_aside_and_brings_it_back(tmp_path):
    led, rec, _ = _ledger_with_queue(tmp_path)
    qids = led.title_queue_groups()[0]["queue_ids"]
    led.park(qids, decided_by="Kyle McNamara", note="need the SOW")
    assert led.title_queue_groups() == [] and len(led.title_queue_groups(status="parked")) == 1
    assert led.queue_summary() == {"location": 1}
    hist = led.decision_history("Operations")
    assert hist[-1]["decision_json"].startswith('{"parked": true') and hist[-1]["reason"] == "need the SOW"
    rows = [r for r in led.live_rows(rec.document_id) if r["observed_title"] == "Operations"]
    assert all(r["counted"] == 0 for r in rows)                                        # parked rates stay held back
    led.unpark(qids, decided_by="Kyle McNamara")
    assert len(led.title_queue_groups()) == 1
    with pytest.raises(ValueError):
        led.unpark(qids, decided_by="Kyle McNamara")                                   # not parked any more
    led.close()


def test_contract_sets_have_a_proposed_name_and_a_review_status(tmp_path):
    led, rec, _ = _ledger_with_queue(tmp_path)
    sets = led.contract_sets()
    assert len(sets) == 1
    s = sets[0]
    assert s["name"] == "bank-a – Acme · rate card" and not s["confirmed"]            # client – vendor · kind (no year known)
    assert s["status"] == "ready" and s["questions"] == 2 and s["answered"] == 0     # one title group + one place
    led.decide_title(led.title_queue_groups()[0]["queue_ids"], role_id="systems_engineer", band=None, reason="r", decided_by="Kyle McNamara")
    s = led.contract_sets()[0]
    assert s["status"] == "in_review" and s["answered"] == 1 and s["open"] == 1
    led.set_name(s["set_id"], "Acme at bank-a, 2027 rate card", "Kyle McNamara")
    s = led.contract_sets()[0]
    assert s["name"] == "Acme at bank-a, 2027 rate card" and s["confirmed"] and s["name_confirmed_by"] == "Kyle McNamara"
    led.decide_location([q["id"] for q in led.queue_items("location")], classification="onshore", reason="r", decided_by="Kyle McNamara")
    assert led.contract_sets()[0]["status"] == "complete"
    ov = led.set_overview(s["set_id"])
    assert ov["rows"] == 4 and ov["title_groups"] == 0
    led.close()
