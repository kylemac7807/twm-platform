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
