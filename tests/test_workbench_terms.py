"""Terms in the workbench (work/workbench-terms/plan.md): a contract set's facts and conditions are shown with the disclosure
check first; an analyst names a clause the engine could not place, says which vendor a printed name is, and clears or keeps a
disclosure flag. Every answer is recorded with a name, applies only where its scope says, and changes no inventory file."""
import hashlib
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
CLAUSE = "If delivered hours fall below 93 percent of plan the Contractor credits the State $400,000"
NOTE = "Capacity shortfall credit of $400,000 if delivered hours fall below 93 percent of plan"


def _terms_ledger(tmp_path, vendor="Acme"):
    """Two contracts from one vendor, each its own contract set, each holding the same unplaced clause; the first also holds
    a clause that limits data use, a public-record clause, a confidently typed condition, an unsure one, and two facts."""
    from twm.pipeline.ingest import register
    from twm.pipeline.ledger import Ledger
    from twm.pipeline.models import SourceRef

    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "ledger.sqlite"
    led = Ledger(path); led.start_run("run1", "local", "fake", "0.1")
    recs = []
    for name in ("contract_one.txt", "contract_two.txt"):
        p = tmp_path / name; p.write_text(f"master agreement {name}", encoding="utf-8")
        rec = register(p); led.upsert_document(rec); recs.append(rec)

        def add(kind, ttype, value, conf, key=None, note=None, status=None, page=3, rec=rec):
            return led.add_term("run1", rec, kind=kind, term_type=ttype, value=value, confidence=conf, verified=True, vendor=vendor, client="bank-a",
                                condition_key=key, note=note, status=status, source_ref=SourceRef(document_id=rec.document_id, page=page, quote=value))
        add("term", "credit", CLAUSE, 0.6, key="other", note=NOTE, status="flagged", page=9)
        led.queue("run1", rec.document_id, "condition", NOTE[:120], f'a condition not in the inventory (page 9): "{CLAUSE[:160]}"; name it and add it to specs/rate-conditions.md')
    one = recs[0]

    def add(kind, ttype, value, conf, key=None, page=3):
        return led.add_term("run1", one, kind=kind, term_type=ttype, value=value, confidence=conf, verified=True, vendor=vendor, client="bank-a",
                            condition_key=key, source_ref=SourceRef(document_id=one.document_id, page=page, quote=value))
    add("fact", "contract_number", "MA-1800078", 0.9)
    add("fact", "expiry", "August 31, 2030", 0.9)
    add("term", "expense_policy", "The State pays no travel expenses", 0.85, key="expenses_refused")
    add("term", "other", "Overtime requires prior written approval", 0.6, key="overtime")
    restricting = add("term", "other", "Contractor shall not use State data for any other purpose", 0.8, key="benchmark_data_use", page=44)
    add("term", "other", "This Contract is a public record under the Freedom of Information Act", 0.8, key="public_record", page=50)
    led.queue("run1", one.document_id, "disclosure", "benchmark_data_use", 'page 44: "Contractor shall not use State data for any other purpose"; clear before benchmarking or contributing')
    led.close()
    return path, [r.document_id for r in recs], restricting


def _client(tmp_path, monkeypatch, **kw):
    path, docs, restricting = _terms_ledger(tmp_path, **kw)
    monkeypatch.setenv("TWM_LEDGER", str(path))
    from twm.workbench import api
    return TestClient(api.app), path, docs


def _terms(path):
    c = sqlite3.connect(path)
    rows = c.execute("SELECT term_id, document_id, condition_key, condition_group, status, key_source, value, extraction_confidence FROM contract_terms ORDER BY term_id").fetchall()
    c.close()
    return rows


def _inventory_files():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in ("specs/rate-conditions.md", "src/twm/pipeline/conditions.py")}


def test_a_contract_sets_terms_are_shown_with_the_disclosure_check_first(tmp_path, monkeypatch):
    c, path, (one, two) = _client(tmp_path, monkeypatch)
    v = c.get(f"/api/sets/{one}/terms").json()
    assert v["disclosure"]["status"] == "restricted" and v["disclosure"]["engine"] == "restricted" and len(v["disclosure"]["restricting"]) == 1
    assert [x["condition_key"] for x in v["disclosure"]["clearing"]] == ["public_record"] and len(v["disclosure"]["queue_ids"]) == 1
    assert [(f["label"], [x["value"] for x in f["values"]]) for f in v["facts"]] == [("Contract number", ["MA-1800078"]), ("Expiry", ["August 31, 2030"])]
    assert v["counts"] == dict(facts=2, conditions=5, recorded=3, to_review=1, unnamed=1, set_aside=0, named_people=0)
    by = {g["letter"]: [x["condition_key"] for x in g["conditions"]] for g in v["groups"]}
    assert by["A"] == ["expenses_refused"] and by["B"] == ["overtime"] and by["G"] == ["benchmark_data_use", "public_record"]
    assert [x["shown"] for g in v["groups"] for x in g["conditions"] if x["condition_key"] == "overtime"] == ["to_review"]
    assert v["summary"].startswith("Client pays no expenses") and "public record" in v["summary"] and "overtime" not in v["summary"]   # only what is recorded
    assert c.get(f"/api/sets/{two}/terms").json()["disclosure"]["status"] == "unchecked"       # nothing found is said, not assumed clear
    assert c.get("/api/sets/nope/terms").status_code == 404
    t = c.get(f"/api/terms/{v['unnamed'][0]['term_id']}").json()
    assert t["page"] == 9 and t["value"] == CLAUSE and t["position"]["kind"] == "nobox"         # a text file has no page image: said, not faked
    inv = c.get("/api/conditions").json()
    assert inv["total"] == 54 and [g["letter"] for g in inv["groups"]] == list("ABCDEFG") and sum(len(g["conditions"]) for g in inv["groups"]) == 54


def test_moving_the_floor_re_sorts_the_list_and_rewrites_no_row(tmp_path, monkeypatch):
    c, path, (one, _) = _client(tmp_path, monkeypatch)
    before = _terms(path)
    low = c.get(f"/api/sets/{one}/terms", params=dict(floor=0.5)).json()["counts"]
    high = c.get(f"/api/sets/{one}/terms", params=dict(floor=0.9)).json()["counts"]
    assert (low["recorded"], low["to_review"]) == (4, 0) and (high["recorded"], high["to_review"]) == (0, 4)
    assert low["unnamed"] == high["unnamed"] == 1                                               # an unnamed clause is unnamed at any floor
    assert c.get(f"/api/sets/{one}/terms", params=dict(floor=7)).status_code == 400
    assert _terms(path) == before


def test_a_named_condition_applies_to_its_scope_and_nowhere_else(tmp_path, monkeypatch):
    c, path, (one, two) = _client(tmp_path, monkeypatch)
    q1 = c.get("/api/queue/conditions", params=dict(set_id=one)).json()
    assert len(q1) == 1 and q1[0]["term"]["value"] == CLAUSE and q1[0]["term"]["page"] == 9
    assert {x["key"] for x in q1[0]["closest"]} & {"sla_credit", "signing_credit", "capacity_formula"}   # nearest wording offered, no model
    body = dict(queue_ids=[q1[0]["id"]], condition_key="sla_credit", scope="set", decided_by="Kyle McNamara")
    assert c.post("/api/decisions/condition", json={**body, "decided_by": ""}).status_code == 400
    assert c.post("/api/decisions/condition", json={**body, "condition_key": "not_a_key"}).status_code == 400
    assert c.post("/api/decisions/condition", json={**body, "condition_key": None}).status_code == 400            # nothing chosen
    assert c.post("/api/decisions/condition", json={**body, "proposed_name": "also this"}).status_code == 400     # two answers at once
    r = c.post("/api/decisions/condition", json=body)
    assert r.status_code == 200 and len(r.json()["decision_ids"]) == 1 and r.json()["queue"]["condition"] == 1
    named = {t[1]: t for t in _terms(path) if t[6] == CLAUSE}
    assert named[one][2:6] == ("sla_credit", "D", "recorded", "analyst") and named[two][2:6] == ("other", None, "flagged", None)
    assert c.get("/api/queue/conditions", params=dict(set_id=one)).json() == [] and len(c.get("/api/queue/conditions", params=dict(set_id=two)).json()) == 1
    assert c.get("/api/rules/pending").json()["conditions"] == []                               # an inventory name for one contract set nominates nothing
    # the same answer by a direct call on a fresh copy leaves the same rows
    from twm.pipeline.ledger import Ledger
    other, (o1, _), _ = _terms_ledger(tmp_path / "direct")
    led = Ledger(other)
    led.decide_condition([led.queue_items("condition", set_id=o1)[0]["id"]], condition_key="sla_credit", scope="set", decided_by="Kyle McNamara")
    assert led.saved_condition(CLAUSE, "Acme", o1)["condition_key"] == "sla_credit" and led.saved_condition(CLAUSE, "Acme", "another set") is None
    led.close()
    assert [t[2:] for t in _terms(other)] == [t[2:] for t in _terms(path)]


def test_a_vendor_wide_answer_covers_the_same_clause_in_the_vendors_other_contracts(tmp_path, monkeypatch):
    c, path, (one, two) = _client(tmp_path, monkeypatch)
    q = c.get("/api/queue/conditions", params=dict(set_id=one)).json()[0]
    r = c.post("/api/decisions/condition", json=dict(queue_ids=[q["id"]], condition_key="sla_credit", scope="vendor", decided_by="Kyle McNamara"))
    assert r.status_code == 200 and len(r.json()["decision_ids"]) == 2 and "condition" not in r.json()["queue"]   # both questions answered by one answer
    assert all(t[2:6] == ("sla_credit", "D", "recorded", "analyst") for t in _terms(path) if t[6] == CLAUSE)
    from twm.pipeline.ledger import Ledger
    led = Ledger(path)
    assert led.saved_condition(CLAUSE, "Acme", "a third contract set")["condition_key"] == "sla_credit"          # a later run of this vendor does not ask again
    assert led.saved_condition(CLAUSE, "Someone else", "x") is None
    led.close()


def test_a_proposed_condition_is_recorded_here_and_nominated_without_touching_the_inventory(tmp_path, monkeypatch):
    c, path, (one, two) = _client(tmp_path, monkeypatch)
    files = _inventory_files()
    q = c.get("/api/queue/conditions", params=dict(set_id=one)).json()[0]
    body = dict(queue_ids=[q["id"]], proposed_name="Capacity shortfall credit", proposed_group="D", scope="set", decided_by="Kyle McNamara")
    assert c.post("/api/decisions/condition", json={**body, "proposed_group": None}).status_code == 400
    assert c.post("/api/decisions/condition", json={**body, "proposed_name": "SLA credit"}).status_code == 400    # already in the inventory
    assert c.post("/api/decisions/condition", json=body).status_code == 200
    t = [x for x in _terms(path) if x[1] == one and x[6] == CLAUSE][0]
    assert t[2:6] == ("proposed:capacity_shortfall_credit", "D", "recorded", "analyst")
    d = [x for g in c.get(f"/api/sets/{one}/terms").json()["groups"] if g["letter"] == "D" for x in g["conditions"]]
    assert [x["label"] for x in d] == ["Capacity shortfall credit (proposed)"] and d[0]["shown"] == "recorded"
    pend = c.get("/api/rules/pending").json()["conditions"]
    assert len(pend) == 1 and pend[0]["what"] == "new condition" and pend[0]["name"] == "Capacity shortfall credit" and pend[0]["group"] == "D"
    lines = c.get("/api/rules/pending.csv", params=dict(kind="conditions")).text.splitlines()
    assert lines[0] == "what,condition_key,name,group,group_name,decided_by" and "400,000" not in lines[1] and "bank-a" not in lines[1]   # vocabulary only leaves
    assert c.post("/api/rules/applied", json=dict(decision_ids=[pend[0]["decision_id"]])).json()["marked"] == 1
    assert c.get("/api/rules/pending").json()["conditions"] == []
    assert _inventory_files() == files and c.get("/api/conditions").json()["total"] == 54
    # "not a rate condition": kept, set aside, and no longer asked
    q2 = c.get("/api/queue/conditions", params=dict(set_id=two)).json()[0]
    assert c.post("/api/decisions/condition", json=dict(queue_ids=[q2["id"]], not_a_condition=True, decided_by="Kyle McNamara")).status_code == 200
    v = c.get(f"/api/sets/{two}/terms").json()
    assert v["counts"]["set_aside"] == 1 and v["counts"]["unnamed"] == 0 and all(not g["conditions"] for g in v["groups"])
    assert c.get("/api/queue/conditions").json() == []


def test_an_unsure_condition_is_confirmed_or_corrected_from_the_terms_tab(tmp_path, monkeypatch):
    c, path, (one, _) = _client(tmp_path, monkeypatch)
    rows = [x for g in c.get(f"/api/sets/{one}/terms").json()["groups"] for x in g["conditions"]]
    unsure = next(x for x in rows if x["shown"] == "to_review")
    assert c.post(f"/api/terms/{unsure['term_id']}/confirm", json=dict(decided_by="")).status_code == 400
    assert c.post(f"/api/terms/{unsure['term_id']}/confirm", json=dict(decided_by="Kyle McNamara")).status_code == 200
    again = c.get(f"/api/terms/{unsure['term_id']}", params=dict(floor=0.9)).json()
    assert again["shown"] == "recorded" and again["by_analyst"] and again["condition_key"] == "overtime"        # a person's confirmation stands at any floor
    assert c.post(f"/api/terms/{unsure['term_id']}/confirm", json=dict(decided_by="Kyle McNamara", condition_key="holidays")).status_code == 200
    assert c.get(f"/api/terms/{unsure['term_id']}").json()["condition_key"] == "holidays"
    unnamed = c.get(f"/api/sets/{one}/terms").json()["unnamed"][0]
    assert c.post(f"/api/terms/{unnamed['term_id']}/confirm", json=dict(decided_by="Kyle McNamara")).status_code == 400   # an unnamed clause is named in Review


def test_the_disclosure_check_is_decided_once_per_contract_set_with_a_basis(tmp_path, monkeypatch):
    c, path, (one, two) = _client(tmp_path, monkeypatch)
    before = _terms(path)
    assert c.get(f"/api/sets/{one}").json()["queue"]["disclosure"] == 1
    assert c.post(f"/api/sets/{one}/disclosure", json=dict(outcome="cleared", decided_by="Kyle McNamara")).status_code == 400      # no basis
    assert c.post(f"/api/sets/{one}/disclosure", json=dict(outcome="maybe", basis="x", decided_by="Kyle McNamara")).status_code == 400
    assert c.post(f"/api/sets/{one}/disclosure", json=dict(outcome="cleared", basis="It is a public record", decided_by="")).status_code == 400
    r = c.post(f"/api/sets/{one}/disclosure", json=dict(outcome="cleared", basis="It is a public record", decided_by="Kyle McNamara"))
    assert r.status_code == 200 and r.json()["status"] == "cleared" and "disclosure" not in r.json()["queue"]
    d = c.get(f"/api/sets/{one}/disclosure").json()
    assert d["status"] == "cleared" and d["engine"] == "restricted" and d["decided"]["decided_by"] == "Kyle McNamara" and d["decided"]["basis"] == "It is a public record"
    assert _terms(path) == before                                                                # the decision is read; no clause is rewritten
    r = c.post(f"/api/sets/{one}/disclosure", json=dict(outcome="restricted", reason="the client asked us to hold", decided_by="Kyle McNamara"))
    assert r.status_code == 200 and c.get(f"/api/sets/{one}/disclosure").json()["status"] == "restricted"       # changed later; the earlier decision is kept, replaced
    con = sqlite3.connect(path)
    live = con.execute("SELECT COUNT(*) FROM queue_decisions WHERE kind='disclosure' AND superseded_by IS NULL").fetchone()[0]
    kept = con.execute("SELECT COUNT(*) FROM queue_decisions WHERE kind='disclosure'").fetchone()[0]
    con.close()
    assert (live, kept) == (1, 2)
    assert c.get(f"/api/sets/{two}/disclosure").json()["status"] == "unchecked"                  # the other contract set is untouched


def test_a_printed_name_is_resolved_to_a_vendor_once(tmp_path, monkeypatch):
    from twm.pipeline.ledger import Ledger
    path, (one, two), _ = _terms_ledger(tmp_path, vendor=None)
    led = Ledger(path)
    led.queue("run1", one, "vendor", "ACME CONSULTING LLP", "printed on page 1 ('between the State and ACME CONSULTING LLP'); which vendor is this?")
    led.queue("run1", one, "vendor", "State Department of Technology", "printed on page 1 ('State Department of Technology'); which vendor is this?")
    led.close()
    monkeypatch.setenv("TWM_LEDGER", str(path))
    from twm.workbench import api
    c = TestClient(api.app)
    qs = c.get("/api/queue/vendor", params=dict(set_id=one)).json()
    assert [q["item"] for q in qs] == ["ACME CONSULTING LLP", "State Department of Technology"]
    assert c.post("/api/decisions/vendor", json=dict(queue_ids=[qs[0]["id"]], decided_by="Kyle McNamara")).status_code == 400          # neither answer given
    assert c.post("/api/decisions/vendor", json=dict(queue_ids=[qs[0]["id"]], vendor="Acme", not_the_vendor=True, decided_by="Kyle McNamara")).status_code == 400
    r = c.post("/api/decisions/vendor", json=dict(queue_ids=[qs[0]["id"]], vendor="Acme Consulting", decided_by="Kyle McNamara"))
    assert r.status_code == 200 and "vendor" not in r.json()["queue"]                             # the set's other printed name asked the same thing
    led = Ledger(path)
    assert led.lookup_vendor("Acme Consulting, LLP")["vendor"] == "Acme Consulting" and led.lookup_vendor("State Department of Technology") is None
    assert {t["vendor"] for t in led.terms_for_set(one)} == {"Acme Consulting"} and {t["vendor"] for t in led.terms_for_set(two)} == {None}
    led.close()
    assert "Acme Consulting" in c.get("/api/vendors").json()


def test_questions_are_counted_once_and_the_column_adds_up(tmp_path, monkeypatch):
    c, path, (one, two) = _client(tmp_path, monkeypatch)
    s = {x["root_id"]: x for x in c.get("/api/sets").json()}
    assert s[one]["open"] == 2 and s[two]["open"] == 1                                            # one clause to name and one disclosure check; one clause to name
    comp = c.get(f"/api/sets/{one}/composition").json()
    assert sum(r["questions"] for r in comp["rows"]) == comp["total"]["questions"] == s[one]["open"]
    q = c.get("/api/queue/conditions", params=dict(set_id=one)).json()[0]
    assert c.post("/api/queue/park", json=dict(queue_ids=[q["id"]], note="need the SOW", decided_by="Kyle McNamara")).status_code == 200
    assert c.get("/api/queue/conditions", params=dict(set_id=one)).json() == []
    assert [x["id"] for x in c.get("/api/queue/conditions", params=dict(set_id=one, status="parked")).json()] == [q["id"]]
    after = {x["root_id"]: x for x in c.get("/api/sets").json()}[one]
    assert (after["open"], after["parked"], after["status"]) == (1, 1, "in_review")


def test_an_analyst_corrects_the_kind_of_a_document_and_it_stands_on_a_later_run(tmp_path, monkeypatch):
    """Intake labels a file from its first pages, so a contract file that opens with a change notice reads as an amendment.
    A person says what it is; the contract set regroups, its proposed name follows, and a later run keeps the answer."""
    import json
    from twm.pipeline.ingest import register
    from twm.pipeline.ledger import Ledger
    c, path, (one, two) = _client(tmp_path, monkeypatch)
    s = {x["root_id"]: x for x in c.get("/api/sets").json()}[one]
    assert s["kinds"]["contracts"] == 1 and s["kinds"]["amendments"] == 0 and s["name"].endswith("master agreement")
    assert c.post(f"/api/documents/{one}/kind", json=dict(doc_class="novel", decided_by="Kyle McNamara")).status_code == 400
    assert c.post(f"/api/documents/{one}/kind", json=dict(doc_class="amendment", decided_by="")).status_code == 400
    assert c.post("/api/documents/nope/kind", json=dict(doc_class="amendment", decided_by="Kyle McNamara")).status_code == 400
    assert c.post(f"/api/documents/{one}/kind", json=dict(doc_class="amendment", decided_by="Kyle McNamara")).status_code == 200
    s = {x["root_id"]: x for x in c.get("/api/sets").json()}[one]
    assert s["kinds"]["contracts"] == 0 and s["kinds"]["amendments"] == 1 and s["name"].endswith("amendment")
    led = Ledger(path)
    led.upsert_document(register(tmp_path / "contract_one.txt"))                                 # a later run registers the file again
    d = led._rows("SELECT doc_class, class_confidence, record_json FROM documents WHERE document_id=?", (one,))[0]
    led.close()
    assert d["doc_class"] == "amendment" and d["class_confidence"] == 1.0                        # the person's answer stands
    assert json.loads(d["record_json"])["doc_class"] == "msa"                                    # the engine's own reading is kept beside it
    assert c.post(f"/api/documents/{one}/kind", json=dict(doc_class="msa", decided_by="Kyle McNamara")).status_code == 200
    con = sqlite3.connect(path)
    assert con.execute("SELECT COUNT(*) FROM queue_decisions WHERE kind='intake' AND superseded_by IS NULL").fetchone()[0] == 1   # a changed mind replaces, both kept
    assert con.execute("SELECT COUNT(*) FROM queue_decisions WHERE kind='intake'").fetchone()[0] == 2
    con.close()
