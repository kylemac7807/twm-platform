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
CREATE TABLE IF NOT EXISTS contract_sets (
  set_id TEXT PRIMARY KEY, proposed_name TEXT, confirmed_name TEXT, name_confirmed_by TEXT, name_confirmed_at TEXT,
  client TEXT, vendor TEXT, kind TEXT, year TEXT, created_at TEXT);
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
# Columns added after a table first shipped are applied by Ledger._migrate (additive; an existing file gains them on open):
MIGRATIONS = [("queue_decisions", "scope", "TEXT"), ("mapping_decisions", "scope", "TEXT"),
              ("contract_terms", "key_source", "TEXT")]   # 'analyst' once a person named or confirmed the condition (Nov 22, 2026)
SCOPES = ("set", "vendor", "everyone")   # an answer applies to this contract set (default), this vendor's contracts, or is nominated for everyone
DEFAULT_SCOPE = "set"                    # Kyle, Oct 13: the hierarchy is contract set -> vendor -> everyone; the default is the narrowest
LEGACY_SCOPES = {"client": "vendor"}     # scope names recorded before Oct 13 read as the current ones
# queue_decisions (workbench, Oct 13, 2026): the analyst's audit record. One row per queue item decided; a later decision on the
# same item supersedes the earlier one and both stay. reviewed_by / reviewed_at are reserved for a second reviewer role (decided
# Oct 6: not now, no data change later). applied_to_taxonomy is set by the main session once the rule is appended to taxonomy/.

TITLE_MAPPING_COLUMNS = ["observed_title", "source", "source_url", "canonical_role_id", "twm_band", "attr_technology", "attr_location",
                         "attr_level_code_raw", "attr_years_raw", "confidence", "method", "reviewer", "status", "version_added", "source_class"]
LOCATION_RULE_COLUMNS = ["client_key", "place", "classification", "decided_by", "decided_on", "reason", "status"]
BANDS = ("junior", "intermediate", "senior", "lead_principal")
USABLE_SCANS = ("native", "good_scan", "web")

CONFIDENCE_FLOOR = 0.90   # rows below this exist and are visible but are not counted until an analyst confirms (decided Oct 6)
TERM_CONFIDENCE_FLOOR = 0.75   # contract terms: the quote is proven on the page by software; the model's confidence is about the typing of the
                               # condition, which it puts at 0.8 for most clauses. Below this a term is stored as 'flagged'. (Stream A, Oct 13, 2026; Kyle to confirm.)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ledger:
    def __init__(self, path: Path | str = "ledger.sqlite"):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)
        self._migrate()

    def _migrate(self) -> None:
        for table, column, ctype in MIGRATIONS:
            have = {r[1] for r in self.conn.execute(f"PRAGMA table_info({table})")}
            if column not in have:
                self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ctype}")
        self.conn.commit()

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
        # An analyst's answer about what kind of document this is stands over intake's first-page guess, on every later run
        # (resolve once, applied to people). The engine's own guess stays in record_json, and is what the run itself uses.
        for d in self.conn.execute("SELECT decision_json FROM queue_decisions WHERE kind='intake' AND superseded_by IS NULL ORDER BY id DESC").fetchall():
            dec = json.loads(d[0])
            if dec.get("document_id") == rec.document_id and dec.get("doc_class"):
                self.conn.execute("UPDATE documents SET doc_class=?, class_confidence=1.0 WHERE document_id=?", (dec["doc_class"], rec.document_id))
                break
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
        asked = getattr(self, "_asked", None)
        if asked is not None:   # during a run (ask_each_question_once): one question per document, kind, item and detail
            key = (document_id, kind, item, detail)
            if key in asked:
                return
            asked.add(key)
            if self.conn.execute("SELECT 1 FROM review_queue WHERE document_id IS ? AND kind=? AND item=? AND status='parked' LIMIT 1",
                                 (document_id, kind, item)).fetchone():
                return          # the analyst parked this one; it stays parked rather than being asked again
        self.conn.execute("INSERT INTO review_queue(run_id, document_id, kind, item, detail, created_at) VALUES (?,?,?,?,?,?)",
                          (run_id, document_id, kind, item, detail, _now()))
        self.conn.commit()

    def ask_each_question_once(self) -> None:
        """Called by a run: from here on the same question (document, kind, item, detail) is queued a single time, however many
        rows raise it (a title priced in eight contract years is one question, not eight), and not at all while it is parked."""
        self._asked = set()

    def supersede_queue(self, document_id: str, new_run_id: str, kinds: Optional[tuple] = None) -> int:
        """A re-run of a document closes the open questions an earlier run raised for it; the new run raises its own. Answered
        and parked questions are left as they are (answers are found again through saved_answer). Nothing is deleted."""
        q = "UPDATE review_queue SET status='superseded' WHERE document_id=? AND status='open' AND run_id<>?"
        args: list = [document_id, new_run_id]
        if kinds:
            q += " AND kind IN (" + ",".join("?" for _ in kinds) + ")"; args += list(kinds)
        cur = self.conn.execute(q, args)
        self.conn.commit()
        return cur.rowcount

    def record_mapping_decision(self, run_id: str, title: str, role: Optional[str], band: Optional[str], method: str,
                                confidence: float, reasoning: str, decided_by: str, scope: Optional[str] = None) -> None:
        self.conn.execute("INSERT INTO mapping_decisions(run_id, observed_title, canonical_role_id, twm_band, method, confidence, reasoning, decided_by, created_at, scope) VALUES (?,?,?,?,?,?,?,?,?,?)",
                          (run_id, title, role, band, method, confidence, reasoning, decided_by, _now(), scope))
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

    def _vendor_of(self, document_id: str) -> Optional[str]:
        r = self.conn.execute("SELECT vendor FROM observations WHERE document_id=? LIMIT 1", (document_id,)).fetchone()
        return r[0] if r else None

    def queue_summary(self) -> dict:
        """Open items by kind, for the workbench's front page."""
        return {k: n for k, n in self.conn.execute("SELECT kind, COUNT(*) FROM review_queue WHERE status='open' GROUP BY kind ORDER BY kind")}

    def set_of_document(self, document_id: str) -> Optional[str]:
        """The contract set a document belongs to: its family root, or itself when unlinked (same key as documents_by_set)."""
        r = self.conn.execute("SELECT family_id FROM documents WHERE document_id=?", (document_id,)).fetchone()
        if r is None:
            return None
        return r[0] or document_id

    def _set_filter(self, set_id: Optional[str]) -> tuple[str, tuple]:
        if not set_id:
            return "", ()
        return " AND (d.family_id=? OR d.document_id=?)", (set_id, set_id)

    def queue_items(self, kind: Optional[str] = None, status: str = "open", set_id: Optional[str] = None) -> list[dict]:
        q = "SELECT q.*, d.filename FROM review_queue q LEFT JOIN documents d USING(document_id) WHERE q.status=?"
        args: list = [status]
        if kind:
            q += " AND q.kind=?"; args.append(kind)
        f, fa = self._set_filter(set_id); q += f; args += list(fa)
        return self._rows(q + " ORDER BY q.id", tuple(args))

    def title_queue_groups(self, set_id: Optional[str] = None, status: str = "open") -> list[dict]:
        """Title items grouped by (title, client): one decision per group resolves every row with that title for that
        client (resolve once, applied to humans). Sorted by rows_unlocked, the live uncounted rows the decision would free.
        status='parked' lists the parked groups instead."""
        groups: dict[tuple, dict] = {}
        for it in self.queue_items("title", status=status, set_id=set_id):
            client = self._client_of(it["document_id"]); vendor = self._vendor_of(it["document_id"])
            g = groups.setdefault((it["item"], vendor), dict(title=it["item"], client=client, vendor=vendor, queue_ids=[], details=set(), documents=set(),
                                                             set_id=self.set_of_document(it["document_id"])))
            g["queue_ids"].append(it["id"]); g["details"].add(it["detail"] or ""); g["documents"].add(it["filename"] or "")
        out = []
        for g in groups.values():
            obs = self._rows("SELECT obs_id, document_id, qualifier, rate_as_stated, currency, rate_unit, period_raw, location_raw, level_raw, source_quote, source_page, counted "
                             "FROM observations WHERE superseded_by IS NULL AND observed_title=? AND vendor IS ? ORDER BY obs_id", (g["title"], g["vendor"]))
            g["rows_affected"] = len(obs)
            g["rows_unlocked"] = sum(1 for o in obs if not o["counted"])
            sid = g["set_id"]
            g["rows_in_set"] = self.conn.execute("SELECT COUNT(*) FROM observations WHERE superseded_by IS NULL AND observed_title=? AND vendor IS ? AND (family_id=? OR document_id=?)",
                                                 (g["title"], g["vendor"], sid, sid)).fetchone()[0]
            g["examples"] = obs[:3]
            g["details"] = sorted(g["details"]); g["documents"] = sorted(g["documents"])
            out.append(g)
        return sorted(out, key=lambda g: (-g["rows_unlocked"], g["title"]))

    def _record_decision(self, queue_id: int, kind: str, client: Optional[str], item: str, decision: dict, reason: str, decided_by: str,
                         scope: Optional[str] = None, status: str = "resolved", reason_required: bool = True) -> int:
        if reason_required and not (reason or "").strip():
            raise ValueError("a decision needs a reason")
        if not (decided_by or "").strip():
            raise ValueError("a decision needs the analyst's name")
        if scope is not None and scope not in SCOPES:
            raise ValueError(f"scope must be one of {SCOPES}, not {scope!r}")
        cur = self.conn.execute("INSERT INTO queue_decisions(queue_id, kind, client, item, decision_json, reason, decided_by, decided_at, scope) VALUES (?,?,?,?,?,?,?,?,?)",
                                (queue_id, kind, client, item, json.dumps(decision), (reason or "").strip(), decided_by.strip(), _now(), scope))
        new_id = cur.lastrowid
        self.conn.execute("UPDATE queue_decisions SET superseded_by=? WHERE queue_id=? AND id<>? AND superseded_by IS NULL", (new_id, queue_id, new_id))
        self.conn.execute("UPDATE review_queue SET status=? WHERE id=?", (status, queue_id))
        return new_id

    # ------------------------------------------------------------ park (decided with Kyle, Oct 13: replaces "can't decide" and "skip")
    def park(self, queue_ids: Iterable[int], *, decided_by: str, note: str = "") -> list[int]:
        """Set an item aside with an optional note. It leaves the open list for the parked list and can be brought back."""
        ids = []
        for qid in queue_ids:
            rows = self._rows("SELECT * FROM review_queue WHERE id=?", (qid,))
            if not rows:
                raise ValueError(f"no queue item {qid}")
            q = rows[0]
            ids.append(self._record_decision(qid, q["kind"], self._client_of(q["document_id"]), q["item"], dict(parked=True, note=(note or "").strip()),
                                             note, decided_by, status="parked", reason_required=False))
        self.conn.commit()
        return ids

    def unpark(self, queue_ids: Iterable[int], *, decided_by: str) -> list[int]:
        ids = []
        for qid in queue_ids:
            rows = self._rows("SELECT * FROM review_queue WHERE id=? AND status='parked'", (qid,))
            if not rows:
                raise ValueError(f"queue item {qid} is not parked")
            q = rows[0]
            ids.append(self._record_decision(qid, q["kind"], self._client_of(q["document_id"]), q["item"], dict(parked=False), "", decided_by,
                                             status="open", reason_required=False))
        self.conn.commit()
        return ids

    def _queue_item(self, queue_id: int, kind: str) -> dict:
        rows = self._rows("SELECT * FROM review_queue WHERE id=?", (queue_id,))
        if not rows or rows[0]["kind"] != kind:
            raise ValueError(f"queue item {queue_id} is not a {kind} item")
        return rows[0]

    def decide_title(self, queue_ids: Iterable[int], *, role_id: Optional[str], band: Optional[str], reason: str, decided_by: str,
                     technology: Optional[str] = None, scope: str = DEFAULT_SCOPE, run_id: str = "workbench", suggested: bool = False) -> list[int]:
        """One analyst decision for one or more title queue items. role_id None means "leave flagged": the decision is recorded
        and nothing else changes. band None means unbanded, the default (no band without evidence). technology may hold several
        tags, comma-separated. scope says where the answer applies: this contract set (default), this vendor's contracts, or everyone (a
        nomination for the shared framework). The rows it updates follow the scope; counted is recomputed by the same gate as
        add_observation. `suggested` records that the analyst confirmed a system suggestion. Returns decision ids."""
        if band is not None and band not in BANDS:
            raise ValueError(f"unknown band {band!r}")
        if scope not in SCOPES:
            raise ValueError(f"scope must be one of {SCOPES}, not {scope!r}")
        tech = ",".join(t.strip() for t in (technology or "").split(",") if t.strip()) or None
        ids, applied = [], set()
        for qid in queue_ids:
            q = self._queue_item(qid, "title")
            client = self._client_of(q["document_id"]); vendor = self._vendor_of(q["document_id"])
            set_id = self.set_of_document(q["document_id"])
            ids.append(self._record_decision(qid, "title", client, q["item"],
                                             dict(canonical_role_id=role_id, twm_band=band, attr_technology=tech, scope=scope, set_id=set_id, vendor=vendor, suggested=suggested),
                                             reason, decided_by, scope=scope, reason_required=False))
            key = (q["item"], vendor, set_id if scope == "set" else None)
            if role_id and key not in applied:
                applied.add(key)
                where, args = ("observed_title=? AND vendor IS ?", [q["item"], vendor])
                if scope == "set":
                    where += " AND (family_id=? OR document_id=?)"; args += [set_id, set_id]
                self.conn.execute(
                    "UPDATE observations SET canonical_role_id=?, twm_band=?, band_source='analyst', attr_technology=COALESCE(?, attr_technology), "
                    "resolution_status='resolved', resolution_confidence=1.0, needs_band_review=?, "
                    "counted=CASE WHEN COALESCE(extraction_confidence,0)>=? AND scan_quality IN ('native','good_scan','web') THEN 1 ELSE 0 END "
                    "WHERE superseded_by IS NULL AND " + where,
                    [role_id, band, tech, int(band is None), CONFIDENCE_FLOOR] + args)
                self.record_mapping_decision(run_id, q["item"], role_id, band, "analyst", 1.0, (reason or "").strip() or ("confirmed the suggestion" if suggested else "analyst decision"), decided_by.strip(), scope=scope)
        self.conn.commit()
        return ids

    def analyst_answers(self, vendor: Optional[str] = None) -> list[dict]:
        """Every live title answer with a role, newest first, for the suggestion engine to learn from: this vendor's (and
        everyone-scoped) answers when a vendor is given, otherwise all of them."""
        out = []
        for d in self._rows("SELECT * FROM queue_decisions WHERE kind='title' AND superseded_by IS NULL ORDER BY id DESC"):
            dec = json.loads(d["decision_json"])
            if not dec.get("canonical_role_id"):
                continue
            sc = dec.get("scope") or d.get("scope") or DEFAULT_SCOPE; sc = LEGACY_SCOPES.get(sc, sc)
            if vendor and dec.get("vendor") not in (None, vendor) and sc != "everyone":
                continue
            out.append(dict(observed_title=d["item"], canonical_role_id=dec["canonical_role_id"], twm_band=dec.get("twm_band"),
                            attr_technology=dec.get("attr_technology"), scope=sc, client=d["client"], vendor=dec.get("vendor"), decided_by=d["decided_by"]))
        return out

    def saved_answer(self, title: str, vendor: Optional[str], set_id: Optional[str]) -> Optional[dict]:
        """The analyst's live answer for a title, if any: a set-scoped answer for this contract set first, then a vendor- or
        everyone-scoped answer for this vendor. The engine consults this before asking the model or a person on a re-run
        (resolve once, applied to people). Returns the decision's role, band, tags and provenance, or None."""
        rows = self._rows("SELECT * FROM queue_decisions WHERE kind='title' AND item=? AND superseded_by IS NULL ORDER BY id DESC", (title,))
        best = None
        for d in rows:
            dec = json.loads(d["decision_json"])
            if not dec.get("canonical_role_id"):
                continue
            sc = dec.get("scope") or d.get("scope") or DEFAULT_SCOPE; sc = LEGACY_SCOPES.get(sc, sc)
            if sc == "set" and set_id and dec.get("set_id") == set_id:
                return dict(canonical_role_id=dec["canonical_role_id"], twm_band=dec.get("twm_band"), attr_technology=dec.get("attr_technology"),
                            scope=sc, decided_by=d["decided_by"], decided_at=d["decided_at"], decision_id=d["id"])
            if sc in ("vendor", "everyone") and best is None and (sc == "everyone" or vendor is None or dec.get("vendor") == vendor):
                best = dict(canonical_role_id=dec["canonical_role_id"], twm_band=dec.get("twm_band"), attr_technology=dec.get("attr_technology"),
                            scope=sc, decided_by=d["decided_by"], decided_at=d["decided_at"], decision_id=d["id"])
        return best

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
            ids.append(self._record_decision(qid, "location", client, q["item"], dict(place=place, classification=classification), reason, decided_by, reason_required=False))
            self.conn.execute("UPDATE observations SET attr_location=?, needs_location_review=0 "
                              "WHERE superseded_by IS NULL AND document_id=? AND observed_title=? AND needs_location_review=1",
                              (classification, q["document_id"], q["item"]))
        self.conn.commit()
        return ids

    def decide_intake(self, queue_id: int, *, decision: dict, reason: str, decided_by: str) -> int:
        """decision = {"doc_class": "msa"} confirms or corrects a classification (the document record is updated, confidence 1.0);
        {"link": "confirm" | "reject"} answers a suggested contract-set link (recorded; the link itself is re-made on the next run)."""
        q = self._queue_item(queue_id, "intake")
        decision = {**decision, "document_id": q["document_id"]}
        did = self._record_decision(queue_id, "intake", self._client_of(q["document_id"]), q["item"], decision, reason, decided_by, reason_required=False)
        if decision.get("doc_class"):
            self.conn.execute("UPDATE documents SET doc_class=?, class_confidence=1.0 WHERE document_id=?", (decision["doc_class"], q["document_id"]))
            self._refresh_proposed_name(self.set_of_document(q["document_id"]))
        self.conn.commit()
        return did

    DOC_KINDS = ("msa", "sow", "amendment", "rate_card", "sla", "solicitation", "template", "invoice", "timesheet", "other")

    def set_document_kind(self, document_id: str, doc_class: str, *, decided_by: str, reason: str = "") -> int:
        """An analyst corrects what kind of document a file is, with no question having been asked (a contract file that
        opens with a change notice reads as an amendment to intake). Recorded like any answer; it replaces an earlier one
        for the same document, closes an open "confirm the type" question for it, and stands on later runs."""
        if doc_class not in self.DOC_KINDS:
            raise ValueError(f"the kind is one of {self.DOC_KINDS}, not {doc_class!r}")
        rows = self._rows("SELECT filename FROM documents WHERE document_id=?", (document_id,))
        if not rows:
            raise ValueError(f"no document {document_id}")
        earlier = [d["id"] for d in self._rows("SELECT id, decision_json FROM queue_decisions WHERE kind='intake' AND superseded_by IS NULL")
                   if json.loads(d["decision_json"]).get("document_id") == document_id and json.loads(d["decision_json"]).get("doc_class")]
        asked = self._rows("SELECT id FROM review_queue WHERE kind='intake' AND status IN ('open','parked') AND document_id=? AND detail LIKE '%classification%'", (document_id,))
        did = self._record_decision(asked[0]["id"] if asked else None, "intake", self._client_of(document_id), rows[0]["filename"],
                                    dict(doc_class=doc_class, document_id=document_id, corrected=True), reason, decided_by, reason_required=False)
        for e in earlier:
            self.conn.execute("UPDATE queue_decisions SET superseded_by=? WHERE id=? AND superseded_by IS NULL", (did, e))
        self.conn.execute("UPDATE documents SET doc_class=?, class_confidence=1.0 WHERE document_id=?", (doc_class, document_id))
        self._refresh_proposed_name(self.set_of_document(document_id))
        self.conn.commit()
        return did

    def _refresh_proposed_name(self, set_id: Optional[str]) -> None:
        """A set's proposed name says what kind of contract it is; when a document's kind changes, the proposal follows.
        A name a person confirmed is never touched."""
        s = next((x for x in self.documents_by_set() if x["root_id"] == set_id), None)
        if s is None or not self._rows("SELECT 1 FROM contract_sets WHERE set_id=?", (set_id,)):
            return
        p = self.propose_set_name(s)
        self.conn.execute("UPDATE contract_sets SET proposed_name=?, kind=? WHERE set_id=?", (p["proposed_name"], p["kind"], set_id))

    def decision_history(self, item: str) -> list[dict]:
        return self._rows("SELECT * FROM queue_decisions WHERE item=? ORDER BY id", (item,))

    def pending_codification(self) -> dict[str, list[dict]]:
        """Decisions nominated for the shared framework ("everyone" scope) and not yet applied to the taxonomy, in the exact
        column order of the taxonomy CSVs (plus decision_id first), so the main session can append them with the
        twm-change-the-taxonomy skill. Set- and client-scoped answers live in this database and never need this list.
        The workbench never writes to taxonomy/."""
        from .conditions import GROUP_NAMES, RATE_CONDITIONS
        out: dict[str, list[dict]] = {"title_mappings": [], "location_rules": [], "conditions": []}
        seen = set()
        for d in self._rows("SELECT * FROM queue_decisions WHERE applied_to_taxonomy=0 AND superseded_by IS NULL ORDER BY id"):
            dec = json.loads(d["decision_json"])
            if d["kind"] == "title" and (dec.get("scope") or d.get("scope")) != "everyone":
                continue   # set- and vendor-scoped title answers live here and are consulted on re-runs; place names are always per client
            if d["kind"] == "title" and dec.get("canonical_role_id") and (d["item"], d["client"]) not in seen:
                seen.add((d["item"], d["client"]))
                out["title_mappings"].append(dict(decision_id=d["id"], observed_title=d["item"], source=d["client"] or "", source_url="",
                                                  canonical_role_id=dec["canonical_role_id"], twm_band=dec.get("twm_band") or "",
                                                  attr_technology=dec.get("attr_technology") or "", attr_location="", attr_level_code_raw="",
                                                  attr_years_raw="", confidence="1.00", method="human", reviewer=d["decided_by"], status="active",
                                                  version_added="", source_class="observed"))
            elif d["kind"] == "condition" and dec.get("condition_key") and not dec.get("not_a_condition") and not dec.get("confirmed") \
                    and (dec.get("proposed") or (dec.get("scope") or d.get("scope")) == "everyone") and ("c", dec["condition_key"], dec.get("quote")) not in seen:
                seen.add(("c", dec["condition_key"], dec.get("quote")))
                key = dec["condition_key"]
                out["conditions"].append(dict(
                    decision_id=d["id"], what="new condition" if dec.get("proposed") else "wording for a condition already listed", condition_key=key,
                    name=dec.get("proposed_name") or (RATE_CONDITIONS[key][1] if key in RATE_CONDITIONS else key), group=dec.get("condition_group") or "",
                    group_name=GROUP_NAMES.get(dec.get("condition_group") or "", ""), quote=dec.get("quote") or "", decided_by=d["decided_by"], note=d["reason"]))
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
        for s in sets.values():
            if s["root_filename"] is None:
                s["root_filename"] = s["documents"][0]["filename"]
        return sorted(sets.values(), key=lambda s: (-len(s["documents"]), s["root_filename"] or ""))

    # ------------------------------------------------------------ contract sets: names and status (plan v3, step 1)
    KIND_WORDS = {"msa": "master agreement", "sow": "statement of work", "rate_card": "rate card", "amendment": "amendment", "sla": "service levels",
                  "solicitation": "solicitation", "invoice": "invoice", "timesheet": "timesheet", "template": "template"}

    def _manifest_row(self, path: str) -> dict:
        """The library manifest row a downloaded file came from (v3 files are named <row number>_...), else {}."""
        m = re.search(r"v3_(gov|edgar|invoices)[\\/](\d{3})_", path or "")
        if not m:
            return {}
        import csv
        mf = Path(__file__).resolve().parents[3] / "corpus" / "manifests" / f"v3_{m.group(1)}" / "manifest.csv"
        if not mf.exists():
            return {}
        try:
            rows = list(csv.DictReader(open(mf, encoding="utf-8")))
            return rows[int(m.group(2)) - 1]
        except Exception:
            return {}

    def propose_set_name(self, s: dict) -> dict:
        """A readable name from fields the engine already has: client – vendor · kind · year (no model call)."""
        docs = s["documents"]
        client = vendor = year = None
        for d in docs:
            r = self.conn.execute("SELECT client, vendor, effective_date FROM observations WHERE document_id=? AND superseded_by IS NULL LIMIT 1", (d["document_id"],)).fetchone()
            if r:
                client, vendor = client or r[0], vendor or r[1]
                year = year or (r[2] or "")[:4] or None
        for d in docs:
            mr = self._manifest_row(d.get("path") or "")
            if mr:
                client = client or mr.get("buyer") or mr.get("filer")
                vendor = vendor or mr.get("vendor") or mr.get("counterparty")
                y = re.search(r"(19|20)\d\d", mr.get("date_vintage") or mr.get("filing_date") or mr.get("date") or "")
                year = year or (y.group(0) if y else None)
        classes = {d["doc_class"] for d in docs}
        if "msa" in classes and len(docs) > 1:
            kind = "master agreement and exhibits"
        elif len(classes) == 1:
            kind = self.KIND_WORDS.get(next(iter(classes)), next(iter(classes)))
        else:
            kind = ", ".join(self.KIND_WORDS.get(c, c) for c in sorted(classes))
        parties = " – ".join(p for p in (client, vendor) if p)
        name = " · ".join(p for p in (parties or s["root_filename"], kind, year) if p)
        return dict(proposed_name=name, client=client, vendor=vendor, kind=kind, year=year)

    def contract_sets(self) -> list[dict]:
        """Every contract set in the database with its name (proposed until confirmed), its counts and its review status:
        ready (questions, none answered), in_review (some answered or parked, some left), complete (nothing left)."""
        out = []
        for s in self.documents_by_set():
            row = self._rows("SELECT * FROM contract_sets WHERE set_id=?", (s["root_id"],))
            if not row:
                p = self.propose_set_name(s)
                self.conn.execute("INSERT INTO contract_sets(set_id, proposed_name, client, vendor, kind, year, created_at) VALUES (?,?,?,?,?,?,?)",
                                  (s["root_id"], p["proposed_name"], p["client"], p["vendor"], p["kind"], p["year"], _now()))
                self.conn.commit()
                row = self._rows("SELECT * FROM contract_sets WHERE set_id=?", (s["root_id"],))
            meta = row[0]
            rows = counted = 0
            for d in s["documents"]:
                obs = self.observations_for(d["document_id"])
                rows += len(obs); counted += sum(1 for o in obs if o["counted"])
            qs = self.questions(s["root_id"])
            n_open = sum(1 for v in qs.values() if v["status"] == "open"); n_parked = sum(1 for v in qs.values() if v["status"] == "parked")
            n_done = sum(1 for v in qs.values() if v["status"] == "resolved"); total = len(qs)
            status = "complete" if n_open == 0 and n_parked == 0 else ("ready" if n_done == 0 and n_parked == 0 else "in_review")
            out.append(dict(set_id=s["root_id"], name=meta["confirmed_name"] or meta["proposed_name"], proposed_name=meta["proposed_name"],
                            confirmed=bool(meta["confirmed_name"]), name_confirmed_by=meta["name_confirmed_by"], client=meta["client"], vendor=meta["vendor"],
                            root_filename=s["root_filename"], documents=len(s["documents"]), rows=rows, counted=counted,
                            questions=total, answered=n_done, parked=n_parked, open=n_open, status=status))
        return sorted(out, key=lambda x: ({"ready": 0, "in_review": 1, "complete": 2}[x["status"]], -x["open"], x["name"]))

    def questions(self, set_id: str) -> dict[tuple, dict]:
        """The questions a person answers for a contract set, each counted once: a job title once however many rows or
        documents raise it, the disclosure check once per set, everything else per item. Open wins over parked, parked over
        answered. Each carries the first document that raised it. Engine notes (extraction, reading) are not questions."""
        qs: dict[tuple, dict] = {}
        for st in ("open", "parked", "resolved"):
            for it in self.queue_items(status=st, set_id=set_id):
                if it["kind"] in ("extraction", "reading"):
                    continue
                key = ("title", it["item"]) if it["kind"] == "title" else (("disclosure",) if it["kind"] == "disclosure" else (it["kind"], it["id"]))
                if key not in qs:
                    qs[key] = dict(status=st, kind=it["kind"], document_id=it["document_id"])
        return qs

    def set_name(self, set_id: str, name: str, decided_by: str) -> None:
        if not (name or "").strip():
            raise ValueError("a name is needed")
        if not (decided_by or "").strip():
            raise ValueError("the analyst's name is needed")
        self.contract_sets()   # make sure the row exists
        self.conn.execute("UPDATE contract_sets SET confirmed_name=?, name_confirmed_by=?, name_confirmed_at=? WHERE set_id=?",
                          (name.strip(), decided_by.strip(), _now(), set_id))
        self.conn.commit()

    def set_overview(self, set_id: str) -> dict:
        s = next((x for x in self.contract_sets() if x["set_id"] == set_id), None)
        if not s:
            raise ValueError(f"no contract set {set_id}")
        s["queue"] = {k: n for k, n in self.conn.execute(
            "SELECT q.kind, COUNT(*) FROM review_queue q JOIN documents d USING(document_id) WHERE q.status='open' AND (d.family_id=? OR d.document_id=?) GROUP BY q.kind",
            (set_id, set_id))}
        s["parked_items"] = len(self.queue_items(status="parked", set_id=set_id))
        groups = self.title_queue_groups(set_id)
        s["title_groups"] = len(groups); s["rows_unlocked"] = sum(g["rows_unlocked"] for g in groups)
        return s
    # ------------------------------------------------------------ contract terms and named resources (stream A, Oct 13, 2026)
    # ------------------------------------------------------------ a contract set by kind of document (Kyle, Nov 22, 2026)
    KIND_OF_CLASS = {"msa": "contracts", "amendment": "amendments", "sow": "sows", "rate_card": "rate_cards", "invoice": "invoices", "timesheet": "invoices"}
    KIND_ORDER = (("contracts", "Contracts"), ("amendments", "Amendments"), ("sows", "SOWs"), ("rate_cards", "Rate cards"), ("other", "Other"),
                  ("invoices", "Invoices and timesheets"))

    def set_composition(self, set_id: str) -> dict:
        """What a contract set holds, in the shape of the library table: one row per kind of document, with how many the engine
        has read, the rates, facts and conditions found in them, and the questions waiting. Invoices and timesheets are listed
        apart: matching them to the contract is a later stage (reconciliation), not part of reading the contract set."""
        docs = self._rows("SELECT * FROM documents WHERE family_id=? OR document_id=? ORDER BY filename", (set_id, set_id))
        if not docs:
            raise ValueError(f"no contract set {set_id}")
        have_terms = "contract_terms" in {r[0] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        rows = {k: dict(kind=k, label=label, documents=0, read=0, rates=0, counted=0, facts=0, conditions=0, flagged_conditions=0, resources=0, questions=0, notes=0, docs=[])
                for k, label in self.KIND_ORDER}
        open_by_doc: dict[str, int] = {}
        for v in self.questions(set_id).values():
            if v["status"] == "open":
                open_by_doc[v["document_id"]] = open_by_doc.get(v["document_id"], 0) + 1
        for d in docs:
            k = self.KIND_OF_CLASS.get(d["doc_class"], "other")
            did = d["document_id"]
            rates, counted = self.conn.execute("SELECT COUNT(*), COALESCE(SUM(counted),0) FROM observations WHERE superseded_by IS NULL AND document_id=?", (did,)).fetchone()
            facts = conds = flagged = res = 0
            if have_terms:
                facts = self.conn.execute("SELECT COUNT(*) FROM contract_terms WHERE superseded_by IS NULL AND document_id=? AND kind='fact'", (did,)).fetchone()[0]
                conds, flagged = self.conn.execute("SELECT COUNT(*), COALESCE(SUM(status='flagged'),0) FROM contract_terms WHERE superseded_by IS NULL AND document_id=? AND kind<>'fact'", (did,)).fetchone()
                res = self.conn.execute("SELECT COUNT(*) FROM named_resources WHERE superseded_by IS NULL AND document_id=?", (did,)).fetchone()[0]
            questions = open_by_doc.get(did, 0)   # each question once, under the first document that raised it: the column adds up
            notes = self.conn.execute("SELECT COUNT(*) FROM review_queue WHERE status='open' AND kind IN ('extraction','reading') AND document_id=?", (did,)).fetchone()[0]
            rec = json.loads(d["record_json"]) if d.get("record_json") else {}
            read = int(bool(rates or facts or conds or res))
            r = rows[k]
            r["documents"] += 1; r["read"] += read; r["rates"] += rates; r["counted"] += counted; r["facts"] += facts; r["conditions"] += conds
            r["flagged_conditions"] += flagged; r["resources"] += res; r["questions"] += questions; r["notes"] += notes
            r["docs"].append(dict(document_id=did, filename=d["filename"], doc_class=d["doc_class"], pages=rec.get("page_count"), read=bool(read), rates=rates,
                                  counted=counted, facts=facts, conditions=conds, resources=res, questions=questions, true_type=d["true_type"]))
        ordered = [rows[k] for k, _ in self.KIND_ORDER]
        total = {f: sum(r[f] for r in ordered) for f in ("documents", "read", "rates", "counted", "facts", "conditions", "flagged_conditions", "resources", "questions", "notes")}
        return dict(set_id=set_id, rows=ordered, total=total)

    def title_appearances(self, title: str, vendor: Optional[str], set_id: Optional[str] = None) -> list[dict]:
        """Where a job title appears: each document that prices it or names it, with the pages, how many rates, the periods,
        locations and conditions it is priced under, and the range. A title in a pricing grid appears once per contract year,
        location and service type; a SOW may name a person under the same title."""
        f, fa = ("", ())
        if set_id:
            f, fa = " AND (o.family_id=? OR o.document_id=?)", (set_id, set_id)
        obs = self._rows("SELECT o.*, d.filename, d.doc_class FROM observations o JOIN documents d USING(document_id) "
                         "WHERE o.superseded_by IS NULL AND o.observed_title=? AND o.vendor IS ?" + f + " ORDER BY o.obs_id", (title, vendor) + fa)
        by_doc: dict[str, dict] = {}
        for o in obs:
            a = by_doc.setdefault(o["document_id"], dict(document_id=o["document_id"], filename=o["filename"], doc_class=o["doc_class"], how="priced", rates=0, counted=0,
                                                         pages=set(), periods=[], locations=[], qualifiers=[], values=[], currency=o["currency"], unit=o["rate_unit"], first_obs=o["obs_id"]))
            a["rates"] += 1; a["counted"] += int(bool(o["counted"]))
            if o["source_page"]:
                a["pages"].add(o["source_page"])
            for key, col in (("periods", "period_raw"), ("locations", "location_raw"), ("qualifiers", "qualifier")):
                if o[col] and o[col] not in a[key]:
                    a[key].append(o[col])
            try:
                a["values"].append(Decimal(o["rate_value"]))
            except Exception:
                pass
        out = []
        for a in by_doc.values():
            vals = a.pop("values")
            a["pages"] = sorted(a["pages"])
            a["rate_min"] = str(min(vals)) if vals else None
            a["rate_max"] = str(max(vals)) if vals else None
            out.append(a)
        if "named_resources" in {r[0] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
            g, ga = ("", ())
            if set_id:
                g, ga = " AND (n.family_id=? OR n.document_id=?)", (set_id, set_id)
            for n in self._rows("SELECT n.document_id, n.source_page, n.name_or_role, d.filename, d.doc_class FROM named_resources n JOIN documents d USING(document_id) "
                                "WHERE n.superseded_by IS NULL AND n.observed_title=? AND n.vendor IS ?" + g, (title, vendor) + ga):
                out.append(dict(document_id=n["document_id"], filename=n["filename"], doc_class=n["doc_class"], how="named", rates=0, counted=0, pages=[n["source_page"]] if n["source_page"] else [],
                                periods=[], locations=[], qualifiers=[], rate_min=None, rate_max=None, currency=None, unit=None, first_obs=None, who=n["name_or_role"]))
        return out

    # ------------------------------------------------------------ terms in the workbench (work/workbench-terms/plan.md, Nov 22, 2026)
    def set_documents(self, set_id: str) -> list[dict]:
        return self._rows("SELECT * FROM documents WHERE family_id=? OR document_id=? ORDER BY filename", (set_id, set_id))

    def term(self, term_id: int) -> Optional[dict]:
        rows = self._rows("SELECT t.*, d.filename, d.path, d.true_type, d.doc_class FROM contract_terms t JOIN documents d USING(document_id) "
                          "WHERE t.term_id=?", (term_id,))
        return rows[0] if rows else None

    def terms_for_set(self, set_id: str) -> list[dict]:
        """Every live fact and condition read in a contract set's documents, in document and page order."""
        return self._rows("SELECT t.*, d.filename, d.doc_class FROM contract_terms t JOIN documents d USING(document_id) "
                          "WHERE t.superseded_by IS NULL AND (d.family_id=? OR d.document_id=?) ORDER BY d.filename, t.source_page, t.term_id", (set_id, set_id))

    def resources_for_set(self, set_id: str) -> list[dict]:
        return self._rows("SELECT n.*, d.filename FROM named_resources n JOIN documents d USING(document_id) "
                          "WHERE n.superseded_by IS NULL AND (d.family_id=? OR d.document_id=?) ORDER BY d.filename, n.source_page, n.resource_id", (set_id, set_id))

    def term_of_question(self, q: dict) -> Optional[dict]:
        """The stored condition a 'condition' question is about: the term in the same document whose description (the engine's
        note, else the clause) the question carries, on the page the question names; the still-unnamed one first."""
        rows = self._rows("SELECT t.*, d.filename, d.path, d.true_type, d.doc_class FROM contract_terms t JOIN documents d USING(document_id) "
                          "WHERE t.superseded_by IS NULL AND t.kind='term' AND t.document_id=? ORDER BY t.term_id", (q["document_id"],))
        match = [t for t in rows if (t["note"] or t["value"] or "")[:120] == q["item"]]
        m = re.search(r"\(page (\d+)\)", q.get("detail") or "")
        if m:
            match = [t for t in match if t["source_page"] == int(m.group(1))] or match
        unnamed = [t for t in match if t["condition_key"] == "other" and t["status"] != "dismissed"]
        return (unnamed or match or [None])[0]

    def decide_condition(self, queue_ids: Iterable[int], *, condition_key: Optional[str] = None, proposed_name: Optional[str] = None,
                         proposed_group: Optional[str] = None, not_a_condition: bool = False, scope: str = DEFAULT_SCOPE,
                         reason: str = "", decided_by: str = "") -> list[int]:
        """An analyst names a clause the engine could not place: a condition from the inventory, a proposed new one (a short
        name and its group; kept here at once, nominated for the inventory on Global Framework Updates), or "not a rate
        condition" (kept, set aside, relied on by nothing). The answer covers the same clause wording within the scope: this
        contract set, or this vendor's contracts. Every question about a covered clause is answered with it."""
        from .conditions import GROUP_NAMES, PROPOSED_PREFIX, RATE_CONDITIONS
        name = " ".join((proposed_name or "").split())
        if sum((bool(condition_key), bool(name), bool(not_a_condition))) != 1:
            raise ValueError("choose a condition from the inventory, propose a new one, or say it is not a rate condition")
        if scope not in SCOPES:
            raise ValueError(f"scope must be one of {SCOPES}, not {scope!r}")
        if condition_key:
            if condition_key not in RATE_CONDITIONS:
                raise ValueError(f"unknown condition {condition_key!r}")
            key, group = condition_key, RATE_CONDITIONS[condition_key][0]
        elif name:
            if proposed_group not in GROUP_NAMES:
                raise ValueError("a proposed condition needs its group (A to G)")
            slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            if not slug:
                raise ValueError("a proposed condition needs a name")
            if slug in RATE_CONDITIONS:
                raise ValueError("that name is already in the inventory; choose it from the list")
            key, group = PROPOSED_PREFIX + slug, proposed_group
        else:
            key, group = "other", None
        status = "dismissed" if not_a_condition else "recorded"
        ids, done = [], set()
        for qid in queue_ids:
            if qid in done:
                continue
            q = self._queue_item(qid, "condition")
            term = self.term_of_question(q)
            if term is None:
                raise ValueError(f"the clause behind question {qid} is no longer in the ledger")
            set_id = self.set_of_document(q["document_id"])
            where, args = "t.superseded_by IS NULL AND t.kind='term' AND t.condition_key='other' AND t.value=?", [term["value"]]
            if scope == "set":
                where += " AND (d.family_id=? OR d.document_id=?)"; args += [set_id, set_id]
            else:
                where += " AND t.vendor IS ?"; args.append(term["vendor"])
            targets = self._rows("SELECT t.term_id, t.document_id, t.note, t.value FROM contract_terms t JOIN documents d USING(document_id) WHERE " + where, tuple(args))
            if not any(t["term_id"] == term["term_id"] for t in targets):
                targets.append(term)
            decision = dict(condition_key=key, condition_group=group, proposed=bool(name), proposed_name=name or None, not_a_condition=bool(not_a_condition),
                            quote=term["value"], term_id=term["term_id"], scope=scope, set_id=set_id, vendor=term["vendor"])
            covered = [(qid, q["item"])]
            for t in targets:
                self.conn.execute("UPDATE contract_terms SET condition_key=?, condition_group=?, status=?, key_source='analyst' WHERE term_id=?",
                                  (key, group, status, t["term_id"]))
                for o in self._rows("SELECT id, item FROM review_queue WHERE kind='condition' AND status IN ('open','parked') AND document_id=? AND item=?",
                                    (t["document_id"], (t["note"] or t["value"] or "")[:120])):
                    if o["id"] not in [c[0] for c in covered]:
                        covered.append((o["id"], o["item"]))
            for cid, item in covered:
                ids.append(self._record_decision(cid, "condition", term["client"], item, decision, reason, decided_by, scope=scope, reason_required=False))
                done.add(cid)
        self.conn.commit()
        return ids

    def confirm_term(self, term_id: int, *, decided_by: str, condition_key: Optional[str] = None, reason: str = "") -> int:
        """An analyst confirms the type the engine gave a condition it was unsure of (below the floor), or corrects it to
        another inventory condition. The clause is then relied on whatever the floor. No question need exist for it."""
        from .conditions import RATE_CONDITIONS
        t = self.term(term_id)
        if t is None or t["superseded_by"] is not None or t["kind"] != "term":
            raise ValueError(f"no live condition {term_id}")
        key = condition_key or t["condition_key"]
        if key not in RATE_CONDITIONS and not (condition_key is None and key.startswith("proposed:")):
            raise ValueError("choose a condition from the inventory; an unnamed clause is named in Review")
        group = RATE_CONDITIONS[key][0] if key in RATE_CONDITIONS else t["condition_group"]
        did = self._record_decision(None, "condition", t["client"], (t["note"] or t["value"] or "")[:120],
                                    dict(condition_key=key, condition_group=group, confirmed=True, changed_from=t["condition_key"] if key != t["condition_key"] else None,
                                         quote=t["value"], term_id=term_id, scope="set", set_id=self.set_of_document(t["document_id"]), vendor=t["vendor"]),
                                    reason, decided_by, scope="set", reason_required=False)
        self.conn.execute("UPDATE contract_terms SET condition_key=?, condition_group=?, status='recorded', key_source='analyst' WHERE term_id=?", (key, group, term_id))
        self.conn.commit()
        return did

    def saved_condition(self, value: str, vendor: Optional[str], set_id: Optional[str]) -> Optional[dict]:
        """The analyst's live answer for a clause wording, if any: a set-scoped answer for this contract set first, then a
        vendor- or everyone-scoped answer for this vendor. A re-run consults this before it asks again."""
        best = None
        for d in self._rows("SELECT * FROM queue_decisions WHERE kind='condition' AND superseded_by IS NULL ORDER BY id DESC"):
            dec = json.loads(d["decision_json"])
            if dec.get("quote") != value or not dec.get("condition_key") or dec.get("confirmed"):
                continue
            sc = dec.get("scope") or DEFAULT_SCOPE
            if sc == "set" and set_id and dec.get("set_id") == set_id:
                return dec
            if sc in ("vendor", "everyone") and best is None and (vendor is None or dec.get("vendor") == vendor):
                best = dec
        return best

    def decide_vendor(self, queue_ids: Iterable[int], *, vendor: Optional[str] = None, not_the_vendor: bool = False, reason: str = "",
                      decided_by: str = "") -> list[int]:
        """An analyst says which vendor a printed party name is (written to the vendor-name table, so the name resolves by
        lookup from now on, and this contract set's rows that carry no vendor receive it), or that the name is not the
        vendor. Naming the vendor closes the set's other printed-name questions: they asked the same thing."""
        vendor = " ".join((vendor or "").split())
        if bool(vendor) == bool(not_the_vendor):
            raise ValueError("say which vendor this printed name is, or that it is not the vendor")
        ids = []
        for qid in queue_ids:
            q = self._queue_item(qid, "vendor")
            set_id = self.set_of_document(q["document_id"])
            ids.append(self._record_decision(qid, "vendor", None, q["item"], dict(observed_name=q["item"], vendor=vendor or None, not_the_vendor=bool(not_the_vendor), set_id=set_id),
                                             reason, decided_by, reason_required=False))
            if not vendor:
                continue
            self.record_vendor_name(q["item"], vendor, decided_by.strip(), evidence=(q["detail"] or "")[:200])
            docs = [d["document_id"] for d in self.set_documents(set_id)]
            marks = ",".join("?" for _ in docs)
            for table in ("observations", "contract_terms", "named_resources"):
                self.conn.execute(f"UPDATE {table} SET vendor=? WHERE vendor IS NULL AND superseded_by IS NULL AND document_id IN ({marks})", [vendor] + docs)
            self.contract_sets()   # make sure the set's row exists
            self.conn.execute("UPDATE contract_sets SET vendor=COALESCE(vendor, ?) WHERE set_id=?", (vendor, set_id))
            for o in self._rows("SELECT q.id, q.item FROM review_queue q JOIN documents d USING(document_id) WHERE q.kind='vendor' AND q.status='open' AND q.id<>? "
                                "AND (d.family_id=? OR d.document_id=?)", (qid, set_id, set_id)):
                ids.append(self._record_decision(o["id"], "vendor", None, o["item"], dict(observed_name=o["item"], closed_by=qid, vendor_of_set=vendor, set_id=set_id),
                                                 "", decided_by, reason_required=False))
        self.conn.commit()
        return ids

    def known_vendors(self) -> list[str]:
        names = {r["vendor"] for r in self._rows("SELECT DISTINCT vendor FROM vendor_names WHERE deprecated_at IS NULL")}
        names |= {r["vendor"] for r in self._rows("SELECT DISTINCT vendor FROM observations WHERE vendor IS NOT NULL")}
        return sorted(names)

    def set_disclosure(self, set_id: str) -> dict:
        """The gate, read first: may this contract set be shown, benchmarked, contributed? The engine's reading of the
        clauses (restricted: a clause bars disclosure or limits data use; cleared: a public record, an advisor carve-out or a
        benchmarking right; unchecked: nothing found), then the analyst's decision if one was made, which stands over it."""
        from .conditions import CLEARING_KEYS, GATE_GROUP, RESTRICTING_KEYS
        terms = self.terms_for_set(set_id)
        gate = [t for t in terms if t["kind"] == "term" and t["status"] != "dismissed" and (t["condition_group"] == GATE_GROUP or t["condition_key"] in CLEARING_KEYS)]
        restricting = [t for t in gate if t["condition_key"] in RESTRICTING_KEYS]
        clearing = [t for t in gate if t["condition_key"] in CLEARING_KEYS]
        other = [t for t in gate if t not in restricting and t not in clearing]
        engine = "restricted" if restricting else ("cleared" if clearing else "unchecked")
        decided = None
        for d in self._rows("SELECT * FROM queue_decisions WHERE kind='disclosure' AND superseded_by IS NULL ORDER BY id DESC"):
            dec = json.loads(d["decision_json"])
            if dec.get("set_id") == set_id and dec.get("outcome"):
                decided = dict(outcome=dec["outcome"], basis=dec.get("basis"), note=d["reason"], decided_by=d["decided_by"], decided_at=d["decided_at"], decision_id=d["id"])
                break
        questions = [it for st in ("open", "parked") for it in self.queue_items("disclosure", status=st, set_id=set_id)]
        return dict(set_id=set_id, status=decided["outcome"] if decided else engine, engine=engine, decided=decided, read=any(t["kind"] == "term" for t in terms),
                    restricting=restricting, clearing=clearing, other=other, queue_ids=[it["id"] for it in questions])

    def decide_disclosure(self, set_id: str, *, outcome: str, basis: str = "", reason: str = "", decided_by: str = "") -> list[int]:
        """An analyst clears a contract set for benchmarking (the basis is required: a public record, the client's written
        confirmation, a clause that allows it) or keeps it restricted. One decision per contract set; it answers every open
        disclosure question in the set and replaces an earlier decision. No row changes: the status is read from this."""
        if outcome not in ("cleared", "restricted"):
            raise ValueError("the outcome is cleared or restricted")
        basis = " ".join((basis or "").split())
        if outcome == "cleared" and not basis:
            raise ValueError("say on what basis the contract set is cleared")
        if not self.set_documents(set_id):
            raise ValueError(f"no contract set {set_id}")
        earlier = [d["id"] for d in self._rows("SELECT * FROM queue_decisions WHERE kind='disclosure' AND superseded_by IS NULL")
                   if json.loads(d["decision_json"]).get("set_id") == set_id]
        decision = dict(outcome=outcome, basis=basis or None, set_id=set_id)
        open_ids = self.set_disclosure(set_id)["queue_ids"] or [None]
        ids = []
        for qid in open_ids:
            item = self._rows("SELECT item FROM review_queue WHERE id=?", (qid,))[0]["item"] if qid else "disclosure check"
            ids.append(self._record_decision(qid, "disclosure", None, item, decision, reason, decided_by, reason_required=False))
        for e in earlier:
            self.conn.execute("UPDATE queue_decisions SET superseded_by=? WHERE id=? AND superseded_by IS NULL", (ids[0], e))
        self.conn.commit()
        return ids

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
                 note: Optional[str] = None, status: Optional[str] = None, condition_group: Optional[str] = None,
                 key_source: Optional[str] = None) -> int:
        """One fact ('fact') or commercial term ('term') the document states, verbatim, with its page, box and quote.
        Status: 'recorded' when verified on the page and at or above the confidence floor; 'flagged' when verified but
        below it (kept, visible, not relied on). An unverified quote is the caller's to queue, not to store."""
        if not verified:
            raise ValueError("a term that was not verified on its page is not stored; queue it instead")
        if status is None:
            status = "recorded" if (confidence or 0) >= TERM_CONFIDENCE_FLOOR else "flagged"
        group = condition_group
        if condition_key and group is None:
            from .conditions import condition_group as group_of
            group = group_of(condition_key)
        cur = self.conn.execute(
            """INSERT INTO contract_terms(run_id, document_id, family_id, vendor, client, source_class, kind, term_type, condition_key,
               condition_group, value, extraction_confidence, verified, status, note, source_page, source_bbox, source_quote,
               source_section, created_at, key_source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (run_id, rec.document_id, rec.family_id, vendor, client, rec.source_class, kind, term_type, condition_key, group, value,
             confidence, int(bool(verified)), status, note, source_ref.page, json.dumps(source_ref.bbox) if source_ref.bbox else None,
             source_ref.quote, source_ref.section, _now(), key_source))
        self.conn.commit()
        return cur.lastrowid

    def add_named_resource(self, run_id: str, rec: DocumentRecord, res: NamedResource, *, verified: bool, vendor: Optional[str],
                           client: Optional[str], status: Optional[str] = None) -> int:
        """A person or role the document names (key personnel). Local tier only: names never leave the client's environment."""
        if not verified:
            raise ValueError("a named resource not found on its page is not stored; queue it instead")
        conf = getattr(res, "confidence", 0.0) or 0.0
        if status is None:
            status = "recorded" if conf >= TERM_CONFIDENCE_FLOOR else "flagged"
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
