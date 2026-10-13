"""The ledger (M2 step 6): every rate observation, permanently, with provenance, inside the client's environment.

Design: docs/architecture-components.md section 1.5 (decided Oct 6, 2026):
- append, never overwrite: a re-run supersedes earlier rows for the same document and keeps them;
- observations, not conclusions: findings live elsewhere, with the rule version that produced them;
- one ledger for public and client data, distinguished by source_class;
- confidence and scan quality on every row, gating what counts in benchmarks and savings;
- rates as stated; the reporting-currency value is a derived column with the reference rate and date beside it.
SQLite file for the prototype; the same schema moves to PostgreSQL on Azure.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Optional

from .contracts import RateRow
from .contracts import NamedResource   # added Oct 13, 2026 (stream A)
from .models import DocumentRecord
from .models import SourceRef        # added Oct 13, 2026 (stream A)

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
  document_id TEXT PRIMARY KEY, fingerprint TEXT, filename TEXT, path TEXT, true_type TEXT, doc_class TEXT,
  class_confidence REAL, contract_numbers TEXT, family_id TEXT, readiness TEXT, source_class TEXT,
  registered_at TEXT, record_json TEXT);
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY, started_at TEXT, finished_at TEXT, reader TEXT, model TEXT, rule_version TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS observations (
  obs_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL, document_id TEXT NOT NULL, family_id TEXT,
  vendor TEXT, client TEXT, source_class TEXT NOT NULL,
  observed_title TEXT NOT NULL, level_raw TEXT, location_raw TEXT, period_raw TEXT, qualifier TEXT,
  rate_value TEXT NOT NULL, rate_as_stated TEXT, currency TEXT, rate_unit TEXT,
  effective_date TEXT, vintage_note TEXT,
  reporting_currency TEXT, reporting_value TEXT, fx_rate TEXT, fx_date TEXT, fx_source TEXT,
  canonical_role_id TEXT, twm_band TEXT, band_source TEXT, attr_technology TEXT, attr_location TEXT,
  resolution_status TEXT, resolution_confidence REAL, needs_band_review INTEGER, needs_location_review INTEGER,
  extraction_confidence REAL, scan_quality TEXT, counted INTEGER NOT NULL DEFAULT 0,
  source_page INTEGER, source_bbox TEXT, source_quote TEXT,
  superseded_by TEXT, created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS ix_obs_doc ON observations(document_id);
CREATE INDEX IF NOT EXISTS ix_obs_cut ON observations(canonical_role_id, twm_band, attr_location, attr_technology);
CREATE TABLE IF NOT EXISTS mapping_decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, observed_title TEXT, canonical_role_id TEXT, twm_band TEXT,
  method TEXT, confidence REAL, reasoning TEXT, decided_by TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS review_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, document_id TEXT, kind TEXT, item TEXT, detail TEXT,
  status TEXT DEFAULT 'open', created_at TEXT);
CREATE TABLE IF NOT EXISTS queue_decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, queue_id INTEGER, kind TEXT NOT NULL, client TEXT, item TEXT NOT NULL,
  decision_json TEXT NOT NULL, reason TEXT NOT NULL, decided_by TEXT NOT NULL, decided_at TEXT NOT NULL,
  reviewed_by TEXT, reviewed_at TEXT, applied_to_taxonomy INTEGER NOT NULL DEFAULT 0, applied_at TEXT, superseded_by INTEGER);
CREATE TABLE IF NOT EXISTS contract_terms (
  term_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL, document_id TEXT NOT NULL, family_id TEXT,
  vendor TEXT, client TEXT, source_class TEXT NOT NULL,
  kind TEXT NOT NULL, term_type TEXT NOT NULL, condition_key TEXT, condition_group TEXT,
  value TEXT NOT NULL,
  extraction_confidence REAL, verified INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL, note TEXT,
  source_page INTEGER, source_bbox TEXT, source_quote TEXT, source_section TEXT,
  superseded_by TEXT, created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS ix_terms_doc ON contract_terms(document_id);
CREATE TABLE IF NOT EXISTS named_resources (
  resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL, document_id TEXT NOT NULL, family_id TEXT,
  vendor TEXT, client TEXT, source_class TEXT NOT NULL,
  name_or_role TEXT NOT NULL, observed_title TEXT, location_raw TEXT,
  extraction_confidence REAL, verified INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL,
  source_page INTEGER, source_bbox TEXT, source_quote TEXT,
  superseded_by TEXT, created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS ix_resources_doc ON named_resources(document_id);
CREATE TABLE IF NOT EXISTS vendor_names (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  observed_name TEXT NOT NULL, name_key TEXT NOT NULL, vendor TEXT NOT NULL, vendor_class TEXT,
  evidence TEXT, decided_by TEXT NOT NULL, created_at TEXT NOT NULL, deprecated_at TEXT);
CREATE INDEX IF NOT EXISTS ix_vendor_names_key ON vendor_names(name_key);
"""
# queue_decisions (workbench, Oct 13, 2026): the analyst's audit record. One row per queue item decided; a later decision on the
# same item supersedes the earlier one and both stay. reviewed_by / reviewed_at are reserved for a second reviewer role (decided
# Oct 6: not now, no data change later). applied_to_taxonomy is set by the main session once the rule is appended to taxonomy/.

TITLE_MAPPING_COLUMNS = ["observed_title", "source", "source_url", "canonical_role_id", "twm_band", "attr_technology", "attr_location",
                         "attr_level_code_raw", "attr_years_raw", "confidence", "method", "reviewer", "status", "version_added", "source_class"]
LOCATION_RULE_COLUMNS = ["client_key", "place", "classification", "decided_by", "decided_on", "reason", "status"]
BANDS = ("junior", "intermediate", "senior", "lead_principal")
USABLE_SCANS = ("native", "good_scan", "web")

CONFIDENCE_FLOOR = 0.90   # rows below this exist and are visible but are not counted until an analyst confirms (decided Oct 6)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ledger:
    def __init__(self, path: Path | str = "ledger.sqlite"):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)

    # ------------------------------------------------------------ runs and documents
    def start_run(self, run_id: str, reader: str, model: str, rule_version: str, notes: str = "") -> None:
        self.conn.execute("INSERT OR REPLACE INTO runs(run_id, started_at, reader, model, rule_version, notes) VALUES (?,?,?,?,?,?)",
                          (run_id, _now(), reader, model, rule_version, notes))
        self.conn.commit()

    def finish_run(self, run_id: str, notes: str = "") -> None:
        self.conn.execute("UPDATE runs SET finished_at=?, notes=COALESCE(notes,'')||? WHERE run_id=?", (_now(), notes, run_id))
        self.conn.commit()

    def upsert_document(self, rec: DocumentRecord) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (rec.document_id, rec.fingerprint, rec.filename, rec.path, rec.true_type, rec.doc_class, rec.class_confidence,
             json.dumps(rec.contract_numbers), rec.family_id, rec.readiness, rec.source_class, rec.registered_at, rec.model_dump_json()))
        self.conn.commit()

    # ------------------------------------------------------------ observations
    def supersede_document(self, document_id: str, new_run_id: str) -> int:
        """A re-run supersedes earlier live rows for the document; they stay, marked with the run that replaced them."""
        cur = self.conn.execute("UPDATE observations SET superseded_by=? WHERE document_id=? AND superseded_by IS NULL AND run_id<>?",
                                (new_run_id, document_id, new_run_id))
        self.conn.commit()
        return cur.rowcount

    def add_observation(self, run_id: str, rec: DocumentRecord, row: RateRow, resolution, *, vendor: Optional[str], client: Optional[str],
                        effective_date: Optional[str], scan_quality: str, reporting_currency: Optional[str] = None,
                        fx: Optional[tuple[Decimal, str, str]] = None) -> int:
        """fx = (rate, date, source) for the derived reporting-currency column; None means no conversion recorded."""
        rv = row.rate_value
        rep_val = None
        if fx and reporting_currency and row.currency and rv is not None and row.currency != reporting_currency:
            rep_val = str((rv * fx[0]).quantize(Decimal("0.01")))
        elif reporting_currency and row.currency == reporting_currency and rv is not None:
            rep_val = str(rv)
        counted = int((row.confidence or 0) >= CONFIDENCE_FLOOR and scan_quality in ("native", "good_scan", "web")
                      and resolution is not None and resolution.status == "resolved")
        cur = self.conn.execute(
            """INSERT INTO observations(run_id, document_id, family_id, vendor, client, source_class, observed_title, level_raw, location_raw,
               period_raw, qualifier, rate_value, rate_as_stated, currency, rate_unit, effective_date, vintage_note, reporting_currency,
               reporting_value, fx_rate, fx_date, fx_source, canonical_role_id, twm_band, band_source, attr_technology, attr_location,
               resolution_status, resolution_confidence, needs_band_review, needs_location_review, extraction_confidence, scan_quality,
               counted, source_page, source_bbox, source_quote, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (run_id, rec.document_id, rec.family_id, vendor, client, rec.source_class, row.observed_title, row.level_raw, row.location_raw,
             row.period_raw, row.rate_qualifier, str(rv), row.rate_as_stated, row.currency, row.rate_unit, effective_date,
             f"period as stated: {row.period_raw}" if row.period_raw else None, reporting_currency,
             rep_val, str(fx[0]) if fx else None, fx[1] if fx else None, fx[2] if fx else None,
             getattr(resolution, "canonical_role_id", None), getattr(resolution, "twm_band", None), getattr(resolution, "band_source", None),
             getattr(resolution, "attr_technology", None), getattr(resolution, "attr_location", None),
             getattr(resolution, "status", None), getattr(resolution, "confidence", None),
             int(bool(getattr(resolution, "needs_band_review", False))), int(bool(getattr(resolution, "needs_location_review", False))),
             row.confidence, scan_quality, counted, row.source_ref.page, json.dumps(row.source_ref.bbox) if row.source_ref.bbox else None,
             row.source_ref.quote, _now()))
        self.conn.commit()
        return cur.lastrowid

    def queue(self, run_id: str, document_id: Optional[str], kind: str, item: str, detail: str) -> None:
        self.conn.execute("INSERT INTO review_queue(run_id, document_id, kind, item, detail, created_at) VALUES (?,?,?,?,?,?)",
                          (run_id, document_id, kind, item, detail, _now()))
        self.conn.commit()

    def record_mapping_decision(self, run_id: str, title: str, role: Optional[str], band: Optional[str], method: str,
                                confidence: float, reasoning: str, decided_by: str) -> None:
        self.conn.execute("INSERT INTO mapping_decisions(run_id, observed_title, canonical_role_id, twm_band, method, confidence, reasoning, decided_by, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                          (run_id, title, role, band, method, confidence, reasoning, decided_by, _now()))
        self.conn.commit()

    # ------------------------------------------------------------ queries
    def live_rows(self, document_id: Optional[str] = None) -> list[sqlite3.Row]:
        self.conn.row_factory = sqlite3.Row
        q = "SELECT * FROM observations WHERE superseded_by IS NULL"
        args: tuple = ()
        if document_id:
            q += " AND document_id=?"; args = (document_id,)
        return list(self.conn.execute(q + " ORDER BY obs_id", args))

    def counts(self) -> dict:
        self.conn.row_factory = None
        c = self.conn.execute
        return {
            "documents": c("SELECT COUNT(*) FROM documents").fetchone()[0],
            "observations_live": c("SELECT COUNT(*) FROM observations WHERE superseded_by IS NULL").fetchone()[0],
            "observations_superseded": c("SELECT COUNT(*) FROM observations WHERE superseded_by IS NOT NULL").fetchone()[0],
            "counted": c("SELECT COUNT(*) FROM observations WHERE superseded_by IS NULL AND counted=1").fetchone()[0],
            "queue_open": c("SELECT COUNT(*) FROM review_queue WHERE status='open'").fetchone()[0],
        }

    def close(self) -> None:
        self.conn.close()

    # ------------------------------------------------------------ workbench: queues and analyst decisions (spec: work/workbench/spec.md)
    def _rows(self, q: str, args: tuple = ()) -> list[dict]:
        self.conn.row_factory = sqlite3.Row
        return [dict(r) for r in self.conn.execute(q, args)]

    def _client_of(self, document_id: str) -> Optional[str]:
        r = self.conn.execute("SELECT client FROM observations WHERE document_id=? LIMIT 1", (document_id,)).fetchone()
        return r[0] if r else None

    def queue_summary(self) -> dict:
        """Open items by kind, for the workbench's front page."""
        return {k: n for k, n in self.conn.execute("SELECT kind, COUNT(*) FROM review_queue WHERE status='open' GROUP BY kind ORDER BY kind")}

    def queue_items(self, kind: Optional[str] = None, status: str = "open") -> list[dict]:
        q = "SELECT q.*, d.filename FROM review_queue q LEFT JOIN documents d USING(document_id) WHERE q.status=?"
        args: list = [status]
        if kind:
            q += " AND q.kind=?"; args.append(kind)
        return self._rows(q + " ORDER BY q.id", tuple(args))

    def title_queue_groups(self) -> list[dict]:
        """Open title items grouped by (title, client): one decision per group resolves every row with that title for that
        client (resolve once, applied to humans). Sorted by rows_unlocked, the live uncounted rows the decision would free."""
        groups: dict[tuple, dict] = {}
        for it in self.queue_items("title"):
            client = self._client_of(it["document_id"])
            g = groups.setdefault((it["item"], client), dict(title=it["item"], client=client, queue_ids=[], details=set(), documents=set()))
            g["queue_ids"].append(it["id"]); g["details"].add(it["detail"] or ""); g["documents"].add(it["filename"] or "")
        out = []
        for g in groups.values():
            obs = self._rows("SELECT obs_id, rate_as_stated, currency, rate_unit, period_raw, location_raw, level_raw, source_quote, source_page, counted "
                             "FROM observations WHERE superseded_by IS NULL AND observed_title=? AND client IS ? ORDER BY obs_id", (g["title"], g["client"]))
            g["rows_affected"] = len(obs)
            g["rows_unlocked"] = sum(1 for o in obs if not o["counted"])
            g["examples"] = obs[:3]
            g["details"] = sorted(g["details"]); g["documents"] = sorted(g["documents"])
            out.append(g)
        return sorted(out, key=lambda g: (-g["rows_unlocked"], g["title"]))

    def _record_decision(self, queue_id: int, kind: str, client: Optional[str], item: str, decision: dict, reason: str, decided_by: str) -> int:
        if not (reason or "").strip():
            raise ValueError("a decision needs a reason")
        if not (decided_by or "").strip():
            raise ValueError("a decision needs the analyst's name")
        cur = self.conn.execute("INSERT INTO queue_decisions(queue_id, kind, client, item, decision_json, reason, decided_by, decided_at) VALUES (?,?,?,?,?,?,?,?)",
                                (queue_id, kind, client, item, json.dumps(decision), reason.strip(), decided_by.strip(), _now()))
        new_id = cur.lastrowid
        self.conn.execute("UPDATE queue_decisions SET superseded_by=? WHERE queue_id=? AND id<>? AND superseded_by IS NULL", (new_id, queue_id, new_id))
        self.conn.execute("UPDATE review_queue SET status='resolved' WHERE id=?", (queue_id,))
        return new_id

    def _queue_item(self, queue_id: int, kind: str) -> dict:
        rows = self._rows("SELECT * FROM review_queue WHERE id=?", (queue_id,))
        if not rows or rows[0]["kind"] != kind:
            raise ValueError(f"queue item {queue_id} is not a {kind} item")
        return rows[0]

    def decide_title(self, queue_ids: Iterable[int], *, role_id: Optional[str], band: Optional[str], reason: str, decided_by: str,
                     technology: Optional[str] = None, run_id: str = "workbench") -> list[int]:
        """One analyst decision for one or more title queue items. role_id None means "leave flagged": the decision is recorded
        and nothing else changes. band None means unbanded, the default (no band without evidence). The decision applies to every
        live row with that title for that client; counted is recomputed by the same gate as add_observation. Returns decision ids."""
        if band is not None and band not in BANDS:
            raise ValueError(f"unknown band {band!r}")
        ids, applied = [], set()
        for qid in queue_ids:
            q = self._queue_item(qid, "title")
            client = self._client_of(q["document_id"])
            ids.append(self._record_decision(qid, "title", client, q["item"], dict(canonical_role_id=role_id, twm_band=band, attr_technology=technology), reason, decided_by))
            if role_id and (q["item"], client) not in applied:
                applied.add((q["item"], client))
                self.conn.execute(
                    "UPDATE observations SET canonical_role_id=?, twm_band=?, band_source='analyst', attr_technology=COALESCE(?, attr_technology), "
                    "resolution_status='resolved', resolution_confidence=1.0, needs_band_review=?, "
                    "counted=CASE WHEN COALESCE(extraction_confidence,0)>=? AND scan_quality IN ('native','good_scan','web') THEN 1 ELSE 0 END "
                    "WHERE superseded_by IS NULL AND observed_title=? AND client IS ?",
                    (role_id, band, technology, int(band is None), CONFIDENCE_FLOOR, q["item"], client))
                self.record_mapping_decision(run_id, q["item"], role_id, band, "analyst", 1.0, reason.strip(), decided_by.strip())
        self.conn.commit()
        return ids

    def decide_location(self, queue_ids: Iterable[int], *, classification: str, reason: str, decided_by: str) -> list[int]:
        """An analyst classifies a flagged place name for one client. Applies to the rows that raised the flag (same document and
        title); other rows with the same place follow once the rule is codified in taxonomy/location_rules.csv and the set is re-run."""
        if classification not in ("onshore", "nearshore", "offshore"):
            raise ValueError(f"classification must be onshore, nearshore or offshore, not {classification!r}")
        ids = []
        for qid in queue_ids:
            q = self._queue_item(qid, "location")
            client = self._client_of(q["document_id"])
            m = re.search(r"place '([^']+)'", q["detail"] or "")
            place = m.group(1) if m else None
            ids.append(self._record_decision(qid, "location", client, q["item"], dict(place=place, classification=classification), reason, decided_by))
            self.conn.execute("UPDATE observations SET attr_location=?, needs_location_review=0 "
                              "WHERE superseded_by IS NULL AND document_id=? AND observed_title=? AND needs_location_review=1",
                              (classification, q["document_id"], q["item"]))
        self.conn.commit()
        return ids

    def decide_intake(self, queue_id: int, *, decision: dict, reason: str, decided_by: str) -> int:
        """decision = {"doc_class": "msa"} confirms or corrects a classification (the document record is updated, confidence 1.0);
        {"link": "confirm" | "reject"} answers a suggested contract-set link (recorded; the link itself is re-made on the next run)."""
        q = self._queue_item(queue_id, "intake")
        did = self._record_decision(queue_id, "intake", self._client_of(q["document_id"]), q["item"], decision, reason, decided_by)
        if decision.get("doc_class"):
            self.conn.execute("UPDATE documents SET doc_class=?, class_confidence=1.0 WHERE document_id=?", (decision["doc_class"], q["document_id"]))
        self.conn.commit()
        return did

    def decision_history(self, item: str) -> list[dict]:
        return self._rows("SELECT * FROM queue_decisions WHERE item=? ORDER BY id", (item,))

    def pending_codification(self) -> dict[str, list[dict]]:
        """Decisions not yet applied to the taxonomy, in the exact column order of the taxonomy CSVs (plus decision_id first),
        so the main session can append them with the twm-change-the-taxonomy skill. The workbench never writes to taxonomy/."""
        out: dict[str, list[dict]] = {"title_mappings": [], "location_rules": []}
        seen = set()
        for d in self._rows("SELECT * FROM queue_decisions WHERE applied_to_taxonomy=0 AND superseded_by IS NULL ORDER BY id"):
            dec = json.loads(d["decision_json"])
            if d["kind"] == "title" and dec.get("canonical_role_id") and (d["item"], d["client"]) not in seen:
                seen.add((d["item"], d["client"]))
                out["title_mappings"].append(dict(decision_id=d["id"], observed_title=d["item"], source=d["client"] or "", source_url="",
                                                  canonical_role_id=dec["canonical_role_id"], twm_band=dec.get("twm_band") or "",
                                                  attr_technology=dec.get("attr_technology") or "", attr_location="", attr_level_code_raw="",
                                                  attr_years_raw="", confidence="1.00", method="human", reviewer=d["decided_by"], status="active",
                                                  version_added="", source_class="observed"))
            elif d["kind"] == "location" and dec.get("place"):
                out["location_rules"].append(dict(decision_id=d["id"], client_key=d["client"] or "", place=dec["place"], classification=dec["classification"],
                                                  decided_by=d["decided_by"], decided_on=d["decided_at"][:10], reason=d["reason"], status="active"))
        return out

    def mark_applied(self, decision_id: int) -> int:
        """Mark a decision as appended to the taxonomy. Sibling decisions that say the same thing for the same item and client
        (a group decided in one go produces one decision row per queue item) are the same rule and are marked with it."""
        d = self._rows("SELECT * FROM queue_decisions WHERE id=?", (decision_id,))
        if not d:
            raise ValueError(f"no decision {decision_id}")
        d = d[0]
        cur = self.conn.execute("UPDATE queue_decisions SET applied_to_taxonomy=1, applied_at=? WHERE applied_to_taxonomy=0 AND superseded_by IS NULL "
                                "AND kind=? AND item=? AND client IS ? AND decision_json=?", (_now(), d["kind"], d["item"], d["client"], d["decision_json"]))
        self.conn.commit()
        return cur.rowcount

    def observation(self, obs_id: int) -> Optional[dict]:
        rows = self._rows("SELECT o.*, d.filename, d.path, d.true_type FROM observations o JOIN documents d USING(document_id) WHERE obs_id=?", (obs_id,))
        return rows[0] if rows else None

    def observations_for(self, document_id: str) -> list[dict]:
        return self._rows("SELECT * FROM observations WHERE superseded_by IS NULL AND document_id=? ORDER BY obs_id", (document_id,))

    def documents_by_set(self) -> list[dict]:
        """Documents grouped by contract set (family_id in the code); unlinked documents form sets of one."""
        docs = self._rows("SELECT * FROM documents ORDER BY filename")
        sets: dict[str, dict] = {}
        for d in docs:
            key = d["family_id"] or d["document_id"]
            s = sets.setdefault(key, dict(root_id=key, root_filename=None, documents=[]))
            s["documents"].append(d)
            if d["document_id"] == key:
                s["root_filename"] = d["filename"]
        return sorted(sets.values(), key=lambda s: (-len(s["documents"]), s["root_filename"] or ""))
    # ------------------------------------------------------------ contract terms and named resources (stream A, Oct 13, 2026)
    def supersede_terms(self, document_id: str, new_run_id: str) -> int:
        """A re-run supersedes earlier live term and named-resource rows for the document; they stay, marked."""
        n = 0
        for table in ("contract_terms", "named_resources"):
            cur = self.conn.execute(f"UPDATE {table} SET superseded_by=? WHERE document_id=? AND superseded_by IS NULL AND run_id<>?",
                                    (new_run_id, document_id, new_run_id))
            n += cur.rowcount
        self.conn.commit()
        return n

    def add_term(self, run_id: str, rec: DocumentRecord, *, kind: str, term_type: str, value: str, source_ref: SourceRef,
                 confidence: float, verified: bool, vendor: Optional[str], client: Optional[str], condition_key: Optional[str] = None,
                 note: Optional[str] = None, status: Optional[str] = None) -> int:
        """One fact ('fact') or commercial term ('term') the document states, verbatim, with its page, box and quote.
        Status: 'recorded' when verified on the page and at or above the confidence floor; 'flagged' when verified but
        below it (kept, visible, not relied on). An unverified quote is the caller's to queue, not to store."""
        if not verified:
            raise ValueError("a term that was not verified on its page is not stored; queue it instead")
        if status is None:
            status = "recorded" if (confidence or 0) >= CONFIDENCE_FLOOR else "flagged"
        group = None
        if condition_key:
            from .conditions import condition_group
            group = condition_group(condition_key)
        cur = self.conn.execute(
            """INSERT INTO contract_terms(run_id, document_id, family_id, vendor, client, source_class, kind, term_type, condition_key,
               condition_group, value, extraction_confidence, verified, status, note, source_page, source_bbox, source_quote,
               source_section, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (run_id, rec.document_id, rec.family_id, vendor, client, rec.source_class, kind, term_type, condition_key, group, value,
             confidence, int(bool(verified)), status, note, source_ref.page, json.dumps(source_ref.bbox) if source_ref.bbox else None,
             source_ref.quote, source_ref.section, _now()))
        self.conn.commit()
        return cur.lastrowid

    def add_named_resource(self, run_id: str, rec: DocumentRecord, res: NamedResource, *, verified: bool, vendor: Optional[str],
                           client: Optional[str], status: Optional[str] = None) -> int:
        """A person or role the document names (key personnel). Local tier only: names never leave the client's environment."""
        if not verified:
            raise ValueError("a named resource not found on its page is not stored; queue it instead")
        conf = getattr(res, "confidence", 0.0) or 0.0
        if status is None:
            status = "recorded" if conf >= CONFIDENCE_FLOOR else "flagged"
        cur = self.conn.execute(
            """INSERT INTO named_resources(run_id, document_id, family_id, vendor, client, source_class, name_or_role, observed_title,
               location_raw, extraction_confidence, verified, status, source_page, source_bbox, source_quote, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (run_id, rec.document_id, rec.family_id, vendor, client, rec.source_class, res.name_or_role, res.observed_title, res.location_raw,
             conf, int(bool(verified)), status, res.source_ref.page, json.dumps(res.source_ref.bbox) if res.source_ref.bbox else None,
             res.source_ref.quote, _now()))
        self.conn.commit()
        return cur.lastrowid

    def live_terms(self, document_id: Optional[str] = None, kind: Optional[str] = None) -> list[sqlite3.Row]:
        self.conn.row_factory = sqlite3.Row
        q = "SELECT * FROM contract_terms WHERE superseded_by IS NULL"
        args: list = []
        if document_id:
            q += " AND document_id=?"; args.append(document_id)
        if kind:
            q += " AND kind=?"; args.append(kind)
        return list(self.conn.execute(q + " ORDER BY term_id", tuple(args)))

    def live_named_resources(self, document_id: Optional[str] = None) -> list[sqlite3.Row]:
        self.conn.row_factory = sqlite3.Row
        q = "SELECT * FROM named_resources WHERE superseded_by IS NULL"
        args: tuple = ()
        if document_id:
            q += " AND document_id=?"; args = (document_id,)
        return list(self.conn.execute(q + " ORDER BY resource_id", args))

    def term_counts(self) -> dict:
        self.conn.row_factory = None
        c = self.conn.execute
        return {
            "facts_live": c("SELECT COUNT(*) FROM contract_terms WHERE superseded_by IS NULL AND kind='fact'").fetchone()[0],
            "terms_live": c("SELECT COUNT(*) FROM contract_terms WHERE superseded_by IS NULL AND kind='term'").fetchone()[0],
            "terms_flagged": c("SELECT COUNT(*) FROM contract_terms WHERE superseded_by IS NULL AND status='flagged'").fetchone()[0],
            "terms_superseded": c("SELECT COUNT(*) FROM contract_terms WHERE superseded_by IS NOT NULL").fetchone()[0],
            "named_resources_live": c("SELECT COUNT(*) FROM named_resources WHERE superseded_by IS NULL").fetchone()[0],
            "vendor_names": c("SELECT COUNT(*) FROM vendor_names WHERE deprecated_at IS NULL").fetchone()[0],
        }

    # ------------------------------------------------------------ vendor names, resolved once (stream A, Oct 13, 2026)
    def lookup_vendor(self, observed_name: str) -> Optional[sqlite3.Row]:
        """The vendor an observed party name stands for, if a person (or an operator override) has decided it before."""
        self.conn.row_factory = sqlite3.Row
        return self.conn.execute("SELECT * FROM vendor_names WHERE name_key=? AND deprecated_at IS NULL ORDER BY id DESC LIMIT 1",
                                 (vendor_name_key(observed_name),)).fetchone()

    def record_vendor_name(self, observed_name: str, vendor: str, decided_by: str, evidence: str = "",
                           vendor_class: Optional[str] = None) -> int:
        """Append a decision: this printed name is this vendor. Never edits an earlier row; a changed mind deprecates it."""
        existing = self.lookup_vendor(observed_name)
        if existing is not None and existing["vendor"] == vendor:
            return existing["id"]
        if existing is not None:
            self.conn.execute("UPDATE vendor_names SET deprecated_at=? WHERE id=?", (_now(), existing["id"]))
        cur = self.conn.execute(
            "INSERT INTO vendor_names(observed_name, name_key, vendor, vendor_class, evidence, decided_by, created_at) VALUES (?,?,?,?,?,?,?)",
            (observed_name, vendor_name_key(observed_name), vendor, vendor_class, evidence, decided_by, _now()))
        self.conn.commit()
        return cur.lastrowid


def vendor_name_key(name: str) -> str:
    """Lookup key for a printed party name: case, punctuation and spacing do not matter; the words (including a
    corporate suffix) do, so 'Accenture LLP' and 'Accenture Inc.' are two names that may resolve to one vendor."""
    import re as _re
    return " ".join(_re.sub(r"[^a-z0-9]+", " ", name.lower()).split())
