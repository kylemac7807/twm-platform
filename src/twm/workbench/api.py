"""The workbench service (work/workbench/plan-v2.md, step 1): JSON over the ledger's methods, page images over render.py,
and the page itself. One analyst, one local ledger, no network beyond this machine, no model calls.

    .venv/Scripts/python.exe -m uvicorn twm.workbench.api:app --port 8501

The ledger path comes from TWM_LEDGER (default ledger.sqlite). Every request opens and closes the ledger; the ledger is the
only state. Decisions go through Ledger.decide_* and nothing else; the taxonomy is never written here."""
from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from twm.pipeline.ledger import BANDS, LOCATION_RULE_COLUMNS, TITLE_MAPPING_COLUMNS, Ledger
from twm.taxonomy.store import TaxonomyStore
from twm.workbench.render import render_row

STATIC = Path(__file__).parent / "static"
app = FastAPI(title="TWM review workbench", docs_url=None, redoc_url=None)
_store: Optional[TaxonomyStore] = None


def ledger_path() -> str:
    return os.environ.get("TWM_LEDGER", "ledger.sqlite")


def store() -> TaxonomyStore:
    global _store
    if _store is None:
        _store = TaxonomyStore.load()
    return _store


def _bad(e: Exception) -> HTTPException:
    return HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------- request bodies
class TitleDecision(BaseModel):
    queue_ids: list[int] = Field(min_length=1)
    role_id: Optional[str] = None          # None = leave flagged (recorded)
    band: Optional[str] = None             # None = unbanded, the default
    technology: Optional[str] = None
    reason: str = ""
    decided_by: str = ""


class LocationDecision(BaseModel):
    queue_ids: list[int] = Field(min_length=1)
    classification: str
    reason: str = ""
    decided_by: str = ""


class IntakeDecision(BaseModel):
    queue_id: int
    decision: dict
    reason: str = ""
    decided_by: str = ""


class Applied(BaseModel):
    decision_ids: list[int] = Field(min_length=1)


# ---------------------------------------------------------------- overview and queues
@app.get("/api/overview")
def overview() -> dict:
    led = Ledger(ledger_path())
    try:
        counts = led.counts()
        summary = led.queue_summary()
        sets = []
        for s in led.documents_by_set():
            rows = counted = 0
            for d in s["documents"]:
                obs = led.observations_for(d["document_id"])
                rows += len(obs); counted += sum(1 for o in obs if o["counted"])
            sets.append(dict(root_id=s["root_id"], root_filename=s["root_filename"] or s["documents"][0]["filename"],
                             documents=len(s["documents"]), rows=rows, counted=counted,
                             classes=sorted({d["doc_class"] for d in s["documents"]})))
        items = [dict(id=i["id"], kind=i["kind"], item=i["item"], detail=i["detail"], document=i["filename"]) for i in led.queue_items()]
        groups = led.title_queue_groups()
        return dict(ledger=ledger_path(), counts=counts, queue=summary, open_total=sum(summary.values()),
                    title_groups=len(groups), rows_unlocked=sum(g["rows_unlocked"] for g in groups), sets=sets, items=items[:60])
    finally:
        led.close()


@app.get("/api/queue/titles")
def queue_titles() -> list[dict]:
    led = Ledger(ledger_path())
    try:
        groups = led.title_queue_groups()
        for g in groups:
            g["history"] = led.decision_history(g["title"])
        return groups
    finally:
        led.close()


@app.get("/api/queue/{kind}")
def queue_kind(kind: str) -> list[dict]:
    led = Ledger(ledger_path())
    try:
        items = led.queue_items(kind)
        for i in items:
            i["client"] = led._client_of(i["document_id"])
        return items
    finally:
        led.close()


@app.get("/api/taxonomy")
def taxonomy() -> dict:
    s = store()
    fam = {f.family_id: f.name for f in s.families}
    families: dict[str, list] = {}
    for r in sorted(s.roles, key=lambda r: (fam.get(r.family_id, ""), r.name)):
        families.setdefault(fam.get(r.family_id, r.family_id), []).append(dict(id=r.role_id, name=r.name))
    return dict(families=[dict(family=k, roles=v) for k, v in families.items()], bands=list(BANDS),
                tech=sorted(t.tag for t in s.tech), locations=["onshore", "nearshore", "offshore"])


# ---------------------------------------------------------------- decisions
@app.post("/api/decisions/title")
def decide_title(body: TitleDecision) -> dict:
    if body.band is not None and body.band not in BANDS:
        raise _bad(ValueError(f"unknown band {body.band!r}"))
    if body.role_id and body.role_id not in store().role_by_id:
        raise _bad(ValueError(f"unknown role {body.role_id!r}"))
    led = Ledger(ledger_path())
    try:
        ids = led.decide_title(body.queue_ids, role_id=body.role_id, band=body.band, reason=body.reason, decided_by=body.decided_by,
                               technology=body.technology)
        return dict(decision_ids=ids, queue=led.queue_summary())
    except ValueError as e:
        raise _bad(e)
    finally:
        led.close()


@app.post("/api/decisions/location")
def decide_location(body: LocationDecision) -> dict:
    led = Ledger(ledger_path())
    try:
        ids = led.decide_location(body.queue_ids, classification=body.classification, reason=body.reason, decided_by=body.decided_by)
        return dict(decision_ids=ids, queue=led.queue_summary())
    except ValueError as e:
        raise _bad(e)
    finally:
        led.close()


@app.post("/api/decisions/intake")
def decide_intake(body: IntakeDecision) -> dict:
    led = Ledger(ledger_path())
    try:
        did = led.decide_intake(body.queue_id, decision=body.decision, reason=body.reason, decided_by=body.decided_by)
        return dict(decision_ids=[did], queue=led.queue_summary())
    except ValueError as e:
        raise _bad(e)
    finally:
        led.close()


@app.get("/api/history")
def history(item: str) -> list[dict]:
    led = Ledger(ledger_path())
    try:
        return led.decision_history(item)
    finally:
        led.close()


# ---------------------------------------------------------------- documents and rows
def _doc_view(d: dict) -> dict:
    rec = json.loads(d["record_json"]) if d.get("record_json") else {}
    return dict(document_id=d["document_id"], filename=d["filename"], doc_class=d["doc_class"], class_confidence=d["class_confidence"],
                evidence=rec.get("class_evidence", ""), true_type=d["true_type"], extension_mismatch=bool(rec.get("extension_mismatch")),
                readiness=d["readiness"], pages=rec.get("page_count"), contract_numbers=json.loads(d["contract_numbers"] or "[]"),
                family_id=d["family_id"], flags=rec.get("flags", []), source_class=d["source_class"])


@app.get("/api/sets")
def sets() -> list[dict]:
    led = Ledger(ledger_path())
    try:
        out = []
        for s in led.documents_by_set():
            docs = []
            for d in s["documents"]:
                v = _doc_view(d)
                obs = led.observations_for(d["document_id"])
                v["rows"] = len(obs); v["counted"] = sum(1 for o in obs if o["counted"])
                v["role"] = "root" if d["document_id"] == s["root_id"] else ("linked" if d["family_id"] else "unlinked")
                docs.append(v)
            out.append(dict(root_id=s["root_id"], root_filename=s["root_filename"] or docs[0]["filename"], documents=docs))
        return out
    finally:
        led.close()


ROW_FIELDS = ("obs_id", "observed_title", "level_raw", "rate_as_stated", "rate_value", "currency", "rate_unit", "period_raw", "location_raw",
              "qualifier", "vendor", "client", "canonical_role_id", "twm_band", "band_source", "attr_technology", "attr_location",
              "resolution_status", "resolution_confidence", "needs_band_review", "needs_location_review", "extraction_confidence",
              "scan_quality", "counted", "source_page", "source_bbox", "source_quote", "reporting_currency", "reporting_value",
              "fx_rate", "fx_date", "fx_source", "effective_date", "document_id")


@app.get("/api/documents/{document_id}/rows")
def document_rows(document_id: str) -> list[dict]:
    led = Ledger(ledger_path())
    try:
        return [{k: o.get(k) for k in ROW_FIELDS} for o in led.observations_for(document_id)]
    finally:
        led.close()


@app.get("/api/rows/{obs_id}")
def row(obs_id: int) -> dict:
    led = Ledger(ledger_path())
    try:
        o = led.observation(obs_id)
        if not o:
            raise HTTPException(status_code=404, detail="no such row")
        shown = render_row(o)
        view = {k: o.get(k) for k in ROW_FIELDS}
        view.update(filename=o["filename"], true_type=o["true_type"], position=dict(kind=shown["kind"], page=shown.get("page"),
                    bbox=list(shown["bbox"]) if shown.get("bbox") else None, note=shown.get("note"), quote=shown.get("quote")),
                    history=led.decision_history(o["observed_title"]))
        return view
    finally:
        led.close()


def _png(img) -> Response:
    buf = io.BytesIO(); img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png", headers={"Cache-Control": "no-store"})


@app.get("/api/rows/{obs_id}/page.png")
def row_page(obs_id: int) -> Response:
    led = Ledger(ledger_path())
    try:
        o = led.observation(obs_id)
    finally:
        led.close()
    if not o:
        raise HTTPException(status_code=404, detail="no such row")
    shown = render_row(o)
    if shown["kind"] != "pdf":
        raise HTTPException(status_code=404, detail=shown["note"])
    return _png(shown["image"])


@app.get("/api/rows/{obs_id}/closeup.png")
def row_closeup(obs_id: int) -> Response:
    led = Ledger(ledger_path())
    try:
        o = led.observation(obs_id)
    finally:
        led.close()
    if not o:
        raise HTTPException(status_code=404, detail="no such row")
    shown = render_row(o)
    if shown["kind"] != "pdf":
        raise HTTPException(status_code=404, detail=shown["note"])
    return _png(shown["closeup"])


# ---------------------------------------------------------------- rules to codify
def codification_csv(rows: list[dict], columns: list[str]) -> str:
    """Pending decisions as CSV in the exact column order of the taxonomy file they append to."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator=chr(10), extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


@app.get("/api/rules/pending")
def rules_pending() -> dict:
    led = Ledger(ledger_path())
    try:
        return led.pending_codification()
    finally:
        led.close()


@app.get("/api/rules/pending.csv")
def rules_csv(kind: str = "title_mappings") -> PlainTextResponse:
    if kind not in ("title_mappings", "location_rules"):
        raise _bad(ValueError("kind must be title_mappings or location_rules"))
    led = Ledger(ledger_path())
    try:
        rows = led.pending_codification()[kind]
    finally:
        led.close()
    cols = TITLE_MAPPING_COLUMNS if kind == "title_mappings" else LOCATION_RULE_COLUMNS
    return PlainTextResponse(codification_csv(rows, cols), media_type="text/csv",
                             headers={"Content-Disposition": f'attachment; filename="{kind}_to_append.csv"'})


@app.post("/api/rules/applied")
def rules_applied(body: Applied) -> dict:
    led = Ledger(ledger_path())
    try:
        n = 0
        for did in body.decision_ids:
            n += led.mark_applied(did)
        return dict(marked=n)
    except ValueError as e:
        raise _bad(e)
    finally:
        led.close()


# ---------------------------------------------------------------- the page
@app.get("/")
def index() -> FileResponse:
    page = STATIC / "index.html"
    if not page.exists():
        raise HTTPException(status_code=404, detail="the page is not built yet (plan-v2 step 2)")
    return FileResponse(page, headers={"Cache-Control": "no-store"})


if STATIC.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
