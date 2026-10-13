"""The workbench service (work/workbench/plan-v2.md): the JSON endpoints behave exactly like the ledger methods they wrap,
page images come back with the box drawn, and the rules export matches the taxonomy files."""
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from test_workbench import PRICING, _fixture_ledger, _ledger_state

ROOT = Path(__file__).resolve().parents[1]


def _client(tmp_path, monkeypatch):
    path = _fixture_ledger(tmp_path)
    monkeypatch.setenv("TWM_LEDGER", str(path))
    from twm.workbench import api
    return TestClient(api.app), str(path)


def test_overview_and_queues_show_what_waits_in_the_systems_own_words(tmp_path, monkeypatch):
    c, _ = _client(tmp_path, monkeypatch)
    ov = c.get("/api/overview").json()
    assert ov["queue"] == {"location": 1, "title": 3} and ov["open_total"] == 4
    assert ov["title_groups"] == 2 and ov["rows_unlocked"] == 3
    assert ov["sets"][0]["documents"] == 1 and ov["sets"][0]["rows"] == 5 and ov["sets"][0]["counted"] == 2
    assert any("no rule match" in i["detail"] for i in ov["items"])
    groups = c.get("/api/queue/titles").json()
    assert [g["title"] for g in groups] == ["Operations", "Technical Specialist"] and groups[0]["rows_unlocked"] == 2
    assert groups[0]["examples"][0]["source_quote"].startswith("Operations | Hourly Rate")
    places = c.get("/api/queue/location").json()
    assert len(places) == 1 and places[0]["client"] == "bank-a" and "buffalo" in places[0]["detail"]
    tax = c.get("/api/taxonomy").json()
    assert tax["bands"] == ["junior", "intermediate", "senior", "lead_principal"]
    assert any(r["id"] == "systems_engineer" for f in tax["families"] for r in f["roles"])


def test_a_title_decision_through_the_api_equals_the_direct_call(tmp_path, monkeypatch):
    from twm.pipeline.ledger import Ledger
    c, path = _client(tmp_path, monkeypatch)
    g = c.get("/api/queue/titles").json()[0]
    body = dict(queue_ids=g["queue_ids"], role_id="systems_engineer", band=None, reason="Operations on this exhibit is the systems operations role", decided_by="Kyle McNamara")
    r = c.post("/api/decisions/title", json={**body, "decided_by": ""})
    assert r.status_code == 400 and "name" in r.json()["detail"]
    r = c.post("/api/decisions/title", json={**body, "reason": "  "})
    assert r.status_code == 400 and "reason" in r.json()["detail"]
    r = c.post("/api/decisions/title", json={**body, "role_id": "not_a_role"})
    assert r.status_code == 400 and "unknown role" in r.json()["detail"]
    assert _ledger_state(path)[1] == []                                   # the refusals wrote nothing
    r = c.post("/api/decisions/title", json=body)
    assert r.status_code == 200 and len(r.json()["decision_ids"]) == 2 and r.json()["queue"] == {"location": 1, "title": 1}
    via_api = _ledger_state(path)
    other = _fixture_ledger(tmp_path / "direct")
    led = Ledger(other)
    led.decide_title(led.title_queue_groups()[0]["queue_ids"], role_id="systems_engineer", band=None, reason=body["reason"], decided_by="Kyle McNamara")
    led.close()
    assert via_api == _ledger_state(other)


def test_bulk_and_location_decisions(tmp_path, monkeypatch):
    c, path = _client(tmp_path, monkeypatch)
    groups = c.get("/api/queue/titles").json()
    ids = [q for g in groups for q in g["queue_ids"]]
    r = c.post("/api/decisions/title", json=dict(queue_ids=ids, role_id="systems_engineer", band="senior", reason="both senior ops roles", decided_by="Kyle McNamara"))
    assert r.status_code == 200 and len(r.json()["decision_ids"]) == 3
    place = c.get("/api/queue/location").json()[0]
    r = c.post("/api/decisions/location", json=dict(queue_ids=[place["id"]], classification="abroad", reason="r", decided_by="Kyle McNamara"))
    assert r.status_code == 400
    r = c.post("/api/decisions/location", json=dict(queue_ids=[place["id"]], classification="nearshore", reason="Buffalo is nearshore for this Toronto bank", decided_by="Kyle McNamara"))
    assert r.status_code == 200 and r.json()["queue"] == {}
    obs, dec, q = _ledger_state(path)
    assert len(dec) == 4 and all(s == "resolved" for _, s in q)
    assert all(o[2] == "senior" and o[5] == 1 for o in obs if o[0] in ("Operations", "Technical Specialist"))


def test_rows_and_rules_export(tmp_path, monkeypatch):
    c, path = _client(tmp_path, monkeypatch)
    sets = c.get("/api/sets").json()
    doc = sets[0]["documents"][0]
    assert doc["filename"] == "exhibit.txt" and doc["rows"] == 5 and "rate card" in doc["evidence"]
    rows = c.get(f"/api/documents/{doc['document_id']}/rows").json()
    assert len(rows) == 5 and rows[0]["observed_title"] == "Operations" and rows[0]["counted"] == 0
    one = c.get(f"/api/rows/{rows[0]['obs_id']}").json()
    assert one["position"]["kind"] == "nobox" and one["position"]["quote"].startswith("Operations")
    assert c.get(f"/api/rows/{rows[0]['obs_id']}/page.png").status_code == 404      # a text file has no page image: said, not faked
    assert c.get("/api/rows/999999").status_code == 404
    g = c.get("/api/queue/titles").json()[0]
    c.post("/api/decisions/title", json=dict(queue_ids=g["queue_ids"], role_id="systems_engineer", band=None, reason="r", decided_by="Kyle McNamara", scope="everyone"))
    pend = c.get("/api/rules/pending").json()
    assert len(pend["title_mappings"]) == 1 and pend["title_mappings"][0]["observed_title"] == "Operations"
    csv_text = c.get("/api/rules/pending.csv?kind=title_mappings").text.splitlines()
    assert csv_text[0] == (ROOT / "taxonomy/title_mappings.csv").read_text(encoding="utf-8").splitlines()[0]
    assert csv_text[1].startswith("Operations,bank-a,,systems_engineer,,")
    assert c.get("/api/rules/pending.csv?kind=location_rules").text.splitlines()[0] == (ROOT / "taxonomy/location_rules.csv").read_text(encoding="utf-8").splitlines()[0]
    r = c.post("/api/rules/applied", json=dict(decision_ids=[pend["title_mappings"][0]["decision_id"]]))
    assert r.status_code == 200 and r.json()["marked"] == 2                         # both queue items' decision rows, the same rule
    assert c.get("/api/rules/pending").json()["title_mappings"] == []


def test_sets_names_scope_park_and_suggestions(tmp_path, monkeypatch):
    c, path = _client(tmp_path, monkeypatch)
    sets = c.get("/api/sets").json()
    s = sets[0]
    assert s["name"] == "bank-a – Acme · rate card" and s["status"] == "ready" and s["questions"] == 3 and not s["confirmed"]
    r = c.post(f"/api/sets/{s['root_id']}/name", json=dict(name="Acme rate card for bank-a", decided_by=""))
    assert r.status_code == 400
    r = c.post(f"/api/sets/{s['root_id']}/name", json=dict(name="Acme rate card for bank-a", decided_by="Kyle McNamara"))
    assert r.status_code == 200 and r.json()["name"] == "Acme rate card for bank-a" and r.json()["confirmed"]
    ov = c.get(f"/api/sets/{s['root_id']}").json()
    assert ov["title_groups"] == 2 and ov["rows"] == 5 and ov["up_next"][0]["title"] == "Operations" and ov["queue"] == {"location": 1, "title": 3}
    assert c.get("/api/sets/not-a-set").status_code == 404
    sug = c.get("/api/suggest", params=dict(title="Senior Java Developer", set_id=s["root_id"], client="bank-a")).json()
    assert sug["suggestions"][0]["id"] == "software_developer" and sug["tech_found"] == ["java"] and sug["band"] == "senior"
    sug = c.get("/api/suggest", params=dict(title="Project Manager I / Test Leads")).json()
    assert {x["id"] for x in sug["suggestions"][:2]} == {"project_manager", "test_manager"}      # both halves offered
    sug = c.get("/api/suggest", params=dict(title="Operations")).json()
    assert sug["suggestions"] and sug["saved"] is None and "not from the model" in sug["note"]
    # park and bring back
    g = c.get("/api/queue/titles", params=dict(set_id=s["root_id"])).json()[0]
    r = c.post("/api/queue/park", json=dict(queue_ids=g["queue_ids"], note="need the SOW", decided_by="Kyle McNamara"))
    assert r.status_code == 200 and r.json()["queue"] == {"location": 1, "title": 1}
    parked = c.get("/api/queue/titles", params=dict(set_id=s["root_id"], status="parked")).json()
    assert len(parked) == 1 and parked[0]["title"] == "Operations" and parked[0]["history"][-1]["reason"] == "need the SOW"
    assert c.get("/api/sets").json()[0]["status"] == "in_review"
    r = c.post("/api/queue/unpark", json=dict(queue_ids=g["queue_ids"], decided_by="Kyle McNamara"))
    assert r.status_code == 200 and len(c.get("/api/queue/titles").json()) == 2
    # scope: a set-scoped answer is not exported; the saved answer is reported by suggest afterwards
    r = c.post("/api/decisions/title", json=dict(queue_ids=g["queue_ids"], role_id="systems_engineer", band=None, technology="java,azure", scope="set",
                                                 suggested=True, reason="r", decided_by="Kyle McNamara"))
    assert r.status_code == 200
    assert c.get("/api/rules/pending").json()["title_mappings"] == []
    assert c.get("/api/suggest", params=dict(title="Operations", set_id=s["root_id"], client="bank-a")).json()["saved"]["scope"] == "set"
    r = c.post("/api/decisions/title", json=dict(queue_ids=g["queue_ids"], role_id="systems_engineer", band=None, scope="galaxy", reason="r", decided_by="Kyle McNamara"))
    assert r.status_code == 400


@pytest.mark.skipif(not PRICING.exists(), reason="pricing exhibit not on disk")
def test_page_image_endpoint_returns_the_boxed_page(tmp_path, monkeypatch):
    from decimal import Decimal
    from PIL import Image
    import io
    from twm.pipeline.contracts import RateRow
    from twm.pipeline.ingest import register
    from twm.pipeline.ledger import Ledger
    from twm.pipeline.models import SourceRef
    from twm.pipeline.normalize import resolve
    from twm.taxonomy import TaxonomyStore
    path = tmp_path / "texas.sqlite"
    led = Ledger(path); rec = register(PRICING); led.upsert_document(rec); led.start_run("r", "local", "fake", "0.1")
    row = RateRow(observed_title="Advanced Systems Engineer", rate_value=Decimal("83.00"), rate_as_stated="$83.00", currency="USD", rate_unit="hour",
                  period_raw="Year 1 (FY27)", confidence=0.95, source_ref=SourceRef(document_id=rec.document_id, page=8, bbox=(65.0, 128.0, 553.8, 132.6),
                  quote="Advanced Systems Engineer | Hourly Rate | $83.00"))
    led.add_observation("r", rec, row, resolve("Advanced Systems Engineer", TaxonomyStore.load()), vendor="Accenture LLP", client="Texas DIR", effective_date=None, scan_quality="native")
    led.close()
    monkeypatch.setenv("TWM_LEDGER", str(path))
    from twm.workbench import api
    c = TestClient(api.app)
    one = c.get("/api/rows/1").json()
    assert one["position"]["kind"] == "pdf" and one["position"]["page"] == 8 and one["canonical_role_id"] == "systems_engineer"
    r = c.get("/api/rows/1/page.png")
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    img = Image.open(io.BytesIO(r.content))
    assert img.width > 600 and img.height > img.width
    assert c.get("/api/rows/1/closeup.png").status_code == 200
