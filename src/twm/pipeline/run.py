"""End-to-end run (Thin Thread step 7): a contract set (a document family, in the code) through intake, reading, extraction, normalization and the ledger,
with a plain-language report for Kyle and a drafted answer sheet for the evaluation sample.

    .venv/Scripts/python.exe -m twm.pipeline.run corpus/manifests/v3_downloads/v3_gov/08[1-7]*.pdf --client "Texas DIR"

Contract terms (stream A, Oct 13, 2026; work/contract-terms/spec.md): master agreements, statements of work, amendments and
pricing exhibits also go through term reading; facts, conditions and named resources land in the ledger beside the rates.
The vendor is resolved once through the ledger's vendor-name table from the names intake found on the first pages;
--vendor answers an unknown name and the answer is kept. The client is a setting (--client), never derived.
A persisted daily call count stops the run at DAILY_CALL_STOP model calls.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

from twm import llm
from twm.llm import AnthropicModel, Model, ModelConfig
from twm.taxonomy.store import TaxonomyStore

from .conditions import GATE_GROUP, OTHER
from .extract import ExtractionOutcome, extract_rate_card, extract_sow, rate_table_pages
from .ingest import family_summary, register_family
from .ledger import CONFIDENCE_FLOOR, Ledger, vendor_name_key
from .models import DocumentRecord
from .read import reader_for
from .resolve_model import resolve_with_model

RULE_VERSION = "0.2"            # 0.1: rates only (Oct 6); 0.2: contract terms beside the rates (Oct 13)
TERM_CLASSES = ("msa", "sow", "amendment", "rate_card")
DAILY_CALL_STOP = 200           # the brief's hard stop: no more uncached model calls in one day


@dataclass
class RunReport:
    run_id: str
    documents: list[DocumentRecord]
    rows_kept: int = 0
    rows_rejected: int = 0
    resolved: int = 0
    unbanded: int = 0
    flagged_titles: list[str] = field(default_factory=list)
    ambiguous_titles: list[str] = field(default_factory=list)
    location_review: list[str] = field(default_factory=list)
    model_resolutions: int = 0
    counted: int = 0
    not_counted_reasons: Counter = field(default_factory=Counter)
    example: Optional[dict] = None
    notes: list[str] = field(default_factory=list)
    calls: dict = field(default_factory=dict)
    # contract terms (Oct 13, 2026)
    vendor: Optional[str] = None
    vendor_note: str = ""
    vendor_queued: list[str] = field(default_factory=list)
    term_docs: list[dict] = field(default_factory=list)      # one entry per document read for terms
    facts: int = 0
    terms: int = 0
    terms_flagged: int = 0
    resources: int = 0
    items_rejected: int = 0
    term_example: Optional[dict] = None
    base_rows: int = 0            # rows the model read from the first period column of each grid part
    expanded_rows: int = 0        # rows the software copied from the other period columns (--all-periods)
    disclosure_status: str = ""   # "restricted" | "cleared" | "unchecked": may this contract set be shown, benchmarked, contributed?
    disclosure: list[str] = field(default_factory=list)

    def plain(self) -> str:
        L = [f"Run {self.run_id}", "", family_summary(self.documents), ""]
        if self.vendor_note:
            L.append("Vendor: " + self.vendor_note)
        if self.disclosure_status:
            L.append(f"Disclosure check ({self.disclosure_status.upper()}): " + self.disclosure[0])
            for d in self.disclosure[1:]:
                L.append("  " + d)
        L.append(f"Rates extracted and verified against the page: {self.rows_kept} (rejected by verification or abstention: {self.rows_rejected})."
                 + (f" Of these, {self.base_rows} were read by the model from the first period column and {self.expanded_rows} copied by the software "
                    f"from the other contract-year columns of the same printed row." if self.expanded_rows else ""))
        L.append(f"Titles resolved to a role: {self.resolved} rows, of which {self.unbanded} have no seniority evidence and stay unbanded. "
                 f"Resolved by the model step: {self.model_resolutions}.")
        if self.flagged_titles:
            L.append(f"Titles for the analyst queue ({len(self.flagged_titles)}): " + "; ".join(sorted(set(self.flagged_titles))[:12]))
        if self.ambiguous_titles:
            L.append(f"Ambiguous by design ({len(self.ambiguous_titles)}): " + "; ".join(sorted(set(self.ambiguous_titles))[:8]))
        if self.location_review:
            L.append(f"Place names for the analyst ({len(set(self.location_review))}): " + "; ".join(sorted(set(self.location_review))[:8]))
        L.append(f"Ledger rows that count toward benchmarks: {self.counted} of {self.rows_kept}" + (
            " (not counted: " + ", ".join(f"{k} {v}" for k, v in self.not_counted_reasons.most_common()) + ")" if self.not_counted_reasons else ""))
        if self.example:
            e = self.example
            L.append("")
            L.append(f"One row traced back: '{e['title']}' at {e['rate']} ({e['period']}, {e['location']}) -> {e['role']} / {e['band'] or 'unbanded'}; "
                     f"page {e['page']} of {e['file']}, box {e['bbox']}; the line on the page reads: \"{e['quote'][:120]}\"")
        if self.term_docs:
            L.append("")
            L.append(f"Contract terms: {self.facts} facts, {self.terms} conditions ({self.terms_flagged} flagged below the confidence floor or not in the inventory), "
                     f"{self.resources} named resources, each verified on its page; {self.items_rejected} item(s) the model claimed were not found on the page and were not stored.")
            for d in self.term_docs:
                L.append("")
                L.append(f"{d['file']}: {d['pages']} page(s) read for terms in {d['calls']} call(s)" + (f", {d['unread']} signal page(s) left unread by the cap" if d['unread'] else "")
                         + f"; facts {len(d['facts'])}, conditions {len(d['terms'])}, named resources {d['resources']}, rejected {d['rejected']}, page corrections {d['corrections']}.")
                if d["facts"]:
                    L.append("  Facts: " + "; ".join(f"{f['type']}: {f['value'][:70]} (p{f['page']})" for f in d["facts"][:12]))
                for t in d["terms"][:25]:
                    L.append(f"  - {t['key']}{' [' + t['status'] + ']' if t['status'] != 'recorded' else ''} (p{t['page']}): \"{t['quote'][:110]}\"")
                if len(d["terms"]) > 25:
                    L.append(f"  ... and {len(d['terms']) - 25} more in the ledger")
                for a in d["abstained"][:5]:
                    L.append("  The model would not commit to: " + a[:160])
        if self.term_example:
            e = self.term_example
            L.append("")
            L.append(f"One condition traced back: {e['key']} on page {e['page']} of {e['file']}, box {e['bbox']}; the page reads: \"{e['quote'][:140]}\"")
        if self.calls:
            L.append("")
            L.append(f"Model calls: {self.calls.get('calls')} ({self.calls.get('validated')} validated, {self.calls.get('cached')} from cache); "
                     f"tokens {self.calls.get('input_tokens')} in / {self.calls.get('output_tokens')} out.")
        for n in self.notes:
            L.append("Note: " + n)
        return chr(10).join(L)


# ---------------------------------------------------------------- the daily call budget (persisted beside the cache)
def calls_today(cache_dir: Optional[Path]) -> int:
    """Uncached model calls made today, from the run log beside the cache. No cache dir, no log, no stop."""
    if not cache_dir:
        return 0
    p = Path(cache_dir) / "calls.jsonl"
    if not p.exists():
        return 0
    today = date.today().isoformat()
    n = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("date") == today:
            n += int(d.get("attempts", d.get("uncached", 0)))   # attempts = API requests including retries; older rows carry uncached only
    return n


def _log_calls(cache_dir: Optional[Path], run_id: str, summary: dict) -> None:
    if not cache_dir:
        return
    p = Path(cache_dir); p.mkdir(parents=True, exist_ok=True)
    with (p / "calls.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"date": date.today().isoformat(), "run_id": run_id, "calls": summary.get("calls", 0),
                            "uncached": summary.get("calls", 0) - summary.get("cached", 0),
                            "attempts": sum(l.attempts for l in llm.LOG if not l.cached), "input_tokens": summary.get("input_tokens", 0),
                            "output_tokens": summary.get("output_tokens", 0)}) + chr(10))


def _uncached_so_far() -> int:
    return sum(l.attempts for l in llm.LOG if not l.cached)   # API requests, retries included


# ---------------------------------------------------------------- the vendor, resolved once
def resolve_vendor(led: Ledger, recs: list[DocumentRecord], override: Optional[str], run_id: str) -> tuple[Optional[str], str, list[str]]:
    """The vendor for every row of this contract set: the operator's --vendor if given (and the printed name it answers is
    written to the vendor-name table), else a lookup of the names intake found, else nothing plus a queue item per name."""
    cands = []
    for rec in sorted(recs, key=lambda r: 0 if r.family_id == r.document_id else 1):   # the root document first
        for c in rec.party_candidates:
            cands.append((rec, c))
    if override:
        key = vendor_name_key(override)
        matching = [(r, c) for r, c in cands if vendor_name_key(c.name) == key]
        hinted = [(r, c) for r, c in cands if c.role_hint == "vendor"]
        answered = matching or (hinted if len({vendor_name_key(c.name) for _, c in hinted}) == 1 else [])
        for r, c in answered:
            led.record_vendor_name(c.name, override, "operator --vendor", evidence=f"{r.filename} p{c.page}: {c.evidence}")
        note = f"'{override}' from --vendor" + (f"; the printed name '{answered[0][1].name}' now resolves to it" if answered else "; no printed name answered")
        return override, note, []
    for r, c in sorted(cands, key=lambda rc: 0 if rc[1].role_hint == "vendor" else 1):
        row = led.lookup_vendor(c.name)
        if row is not None:
            return row["vendor"], f"'{row['vendor']}' resolved from the printed name '{c.name}' ({r.filename} p{c.page}; decided by {row['decided_by']})", []
    queued = []
    for r, c in cands:
        if c.role_hint == "client" or vendor_name_key(c.name) in queued:
            continue
        queued.append(vendor_name_key(c.name))
        led.queue(run_id, r.document_id, "vendor", c.name, f"printed on page {c.page} ('{c.evidence[:100]}'); which vendor is this? "
                  f"Answer with --vendor on the next run or in the workbench" + (" (labelled vendor on the page)" if c.role_hint == "vendor" else ""))
    if queued:
        return None, f"not resolved: {len(queued)} printed name(s) queued for a decision ({', '.join(queued[:3])}); rows carry no vendor until then", queued
    return None, "not resolved: no party name with a legal-entity suffix on the first pages; pass --vendor", []


# ---------------------------------------------------------------- the gate: may this contract set be shown, benchmarked, contributed?
RESTRICTING_KEYS = {"disclosure_bar", "benchmark_data_use"}
CLEARING_KEYS = {"public_record", "advisor_disclosure", "benchmark_clause", "benchmark_conditions"}


def disclosure_check(led: Ledger, recs: list[DocumentRecord], run_id: str) -> tuple[str, list[str]]:
    """Read the gate clauses this run stored and say, first thing, what the contract set allows (Kyle, Oct 13, 2026).
    restricted: a clause bars disclosure or limits data use; an analyst clears it before benchmarking or any contribution.
    cleared: a public record, an advisor carve-out or a benchmarking right was found. unchecked: nothing found on the pages
    read; confirm with the client. Restricted and unchecked both go to the review queue (kind 'disclosure')."""
    by_doc = {r.document_id: r for r in recs}
    rows = [t for r in recs for t in led.live_terms(r.document_id, kind="term") if t["run_id"] == run_id
            and (t["condition_group"] == GATE_GROUP or t["condition_key"] in CLEARING_KEYS)]

    def cite(t) -> str:
        return f"{t['condition_key']} ({by_doc[t['document_id']].filename[:40]} p{t['source_page']}): \"{t['value'][:120]}\""

    restricting = [t for t in rows if t["condition_key"] in RESTRICTING_KEYS]
    clearing = [t for t in rows if t["condition_key"] in CLEARING_KEYS]
    other = [t for t in rows if t not in restricting and t not in clearing]
    root = next((r for r in recs if r.family_id == r.document_id), recs[0]) if recs else None
    if restricting:
        lines = ["a clause restricts disclosure or data use; an analyst clears this contract set before it is benchmarked or contributed"] + [cite(t) for t in restricting] + [cite(t) for t in clearing]
        for t in restricting:
            led.queue(run_id, t["document_id"], "disclosure", t["condition_key"], f"page {t['source_page']}: \"{t['value'][:160]}\"; clear before benchmarking or contributing")
        return "restricted", lines
    if clearing:
        return "cleared", ["the contract set may be benchmarked: " + "; ".join(sorted({t["condition_key"] for t in clearing}))] + [cite(t) for t in clearing] + [cite(t) for t in other]
    lines = ["no disclosure, confidentiality or benchmarking clause found on the pages read; confirm with the client before benchmarking"] + [cite(t) for t in other]
    if root is not None:
        led.queue(run_id, root.document_id, "disclosure", root.filename, "no disclosure or benchmarking clause found; confirm the client may share and benchmark this contract set")
    return "unchecked", lines


# ---------------------------------------------------------------- the run
def run_family(paths, *, vendor: Optional[str], client: Optional[str], ledger_path: Path | str, model: Optional[Model],
               reporting_currency: str = "CAD", source_class: str = "public", cache_dir: Optional[Path] = Path(".cache/llm"),
               gold_dir: Optional[Path] = Path("evals/gold"), store: Optional[TaxonomyStore] = None, terms: bool = True,
               max_sections: int = 20, all_periods: bool = True) -> RunReport:   # on by default (Kyle, Oct 13, 2026)
    store = store or TaxonomyStore.load()
    cfg = ModelConfig(model=getattr(model, "name", llm.DEFAULT_MODEL), cache_dir=cache_dir, max_tokens=16000)
    run_id = "run_" + date.today().isoformat() + "_" + uuid.uuid4().hex[:6]
    recs = register_family(paths, source_class)
    rep = RunReport(run_id, recs)
    led = Ledger(ledger_path)
    led.start_run(run_id, "local", cfg.model, RULE_VERSION)
    llm.LOG.clear()
    rep.vendor, rep.vendor_note, rep.vendor_queued = resolve_vendor(led, recs, vendor, run_id)
    vendor = rep.vendor
    spent_before = calls_today(cache_dir)
    if model is not None and spent_before >= DAILY_CALL_STOP:
        rep.notes.append(f"HARD STOP: {spent_before} model calls already made today (limit {DAILY_CALL_STOP}); no model call made in this run")
        model = None

    def over_budget() -> bool:
        return spent_before + _uncached_so_far() >= DAILY_CALL_STOP

    def key_refused() -> Optional[str]:
        """The API refused the key itself (no credit, bad key): every further call would fail the same way, so the run stops."""
        for l in llm.LOG:
            if l.error and ("credit balance" in l.error or "authentication_error" in l.error or "invalid x-api-key" in l.error):
                return "credit balance too low" if "credit balance" in l.error else "key rejected"
        return None

    def store_rows(rec: DocumentRecord, out: ExtractionOutcome, scan_quality: str) -> list[dict]:
        gold_rows = []
        rep.rows_kept += len(out.rows); rep.rows_rejected += len(out.rejected)
        for row in out.rows:
            ctx = row.source_ref.quote or ""
            o = resolve_with_model(row.observed_title, store, model, context=ctx, source=f"{client or 'unknown'} / {vendor or 'unknown'}", config=cfg)
            r = o.result
            if o.used_model and r.status == "resolved":
                rep.model_resolutions += 1
                led.record_mapping_decision(run_id, row.observed_title, r.canonical_role_id, r.twm_band, "model", r.confidence, " ".join(r.notes)[-300:], cfg.model)
            if r.status == "resolved":
                rep.resolved += 1
                if r.twm_band is None:
                    rep.unbanded += 1
            elif r.status == "ambiguous":
                rep.ambiguous_titles.append(row.observed_title)
                led.queue(run_id, rec.document_id, "title", row.observed_title, "ambiguous: " + ", ".join(r.candidates))
            else:
                rep.flagged_titles.append(row.observed_title)
                led.queue(run_id, rec.document_id, "title", row.observed_title, "; ".join(r.notes)[-300:])
            if r.needs_location_review:
                rep.location_review.append(r.attr_location_raw or "")
                led.queue(run_id, rec.document_id, "location", row.observed_title, f"place '{r.attr_location_raw}' needs an analyst decision")
            obs_id = led.add_observation(run_id, rec, row, r, vendor=vendor, client=client, effective_date=None, scan_quality=scan_quality,
                                         reporting_currency=reporting_currency, fx=None)
            live = [x for x in led.live_rows(rec.document_id) if x["obs_id"] == obs_id][0]
            if live["counted"]:
                rep.counted += 1
            else:
                rep.not_counted_reasons["confidence or scan quality" if r.status == "resolved" else "title unresolved"] += 1
            if rep.example is None and r.status == "resolved" and row.source_ref.bbox:
                rep.example = dict(title=row.observed_title, rate=row.rate_as_stated, period=row.period_raw, location=row.location_raw,
                                   role=r.canonical_role_id, band=r.twm_band, page=row.source_ref.page, bbox=row.source_ref.bbox,
                                   quote=row.source_ref.quote or "", file=rec.filename)
            gold_rows.append(row.model_dump(mode="json"))
        return gold_rows

    def store_terms(rec: DocumentRecord, out: ExtractionOutcome) -> dict:
        d = dict(file=rec.filename, pages=len(out.pages_selected), calls=out.sections, unread=out.pages_unread, facts=[], terms=[],
                 resources=len(out.resources), rejected=len(out.rejected_items), corrections=len(out.corrections), abstained=list(out.abstained))
        for f in out.facts:
            led.add_term(run_id, rec, kind="fact", term_type=f.fact_type, value=f.value, source_ref=f.source_ref, confidence=f.confidence,
                         verified=True, vendor=vendor, client=client)
            d["facts"].append(dict(type=f.fact_type, value=f.value, page=f.source_ref.page))
        for t in out.terms:
            key = t.condition_key or OTHER
            status = None
            note = t.condition_note
            if key == OTHER:
                status = "flagged"
                led.queue(run_id, rec.document_id, "condition", (t.condition_note or t.verbatim_short)[:120],
                          f"a condition not in the inventory (page {t.source_ref.page}): \"{t.verbatim_short[:160]}\"; name it and add it to specs/rate-conditions.md")
            tid = led.add_term(run_id, rec, kind="term", term_type=t.term_type, value=t.verbatim_short, source_ref=t.source_ref, confidence=t.confidence,
                               verified=True, vendor=vendor, client=client, condition_key=key, note=note, status=status)
            row = [x for x in led.live_terms(rec.document_id, kind="term") if x["term_id"] == tid][0]
            if row["status"] != "recorded":
                rep.terms_flagged += 1
            d["terms"].append(dict(key=key, page=t.source_ref.page, quote=t.verbatim_short, status=row["status"]))
            if rep.term_example is None and row["status"] == "recorded" and t.source_ref.bbox:
                rep.term_example = dict(key=key, page=t.source_ref.page, bbox=t.source_ref.bbox, quote=t.verbatim_short, file=rec.filename)
        for r in out.resources:
            led.add_named_resource(run_id, rec, r, verified=True, vendor=vendor, client=client)
        for kind, item, why in out.rejected_items:
            ref = item.get("source_ref") or {}
            led.queue(run_id, rec.document_id, "extraction", f"{kind}: {(item.get('condition_key') or item.get('fact_type') or item.get('name_or_role') or '')}",
                      f"{why}; claimed page {ref.get('page')}: \"{(item.get('verbatim_short') or item.get('value') or item.get('name_or_role') or '')[:160]}\"")
        for fl in out.flags:
            led.queue(run_id, rec.document_id, "extraction", rec.filename, fl)
        rep.facts += len(out.facts); rep.terms += len(out.terms); rep.resources += len(out.resources); rep.items_rejected += len(out.rejected_items)
        return d

    def write_gold(rec: DocumentRecord, name: str, payload: dict, what: str) -> None:
        if not gold_dir:
            return
        gd = Path(gold_dir); gd.mkdir(parents=True, exist_ok=True)
        gp = gd / name
        payload.update({"document_id": rec.document_id, "filename": rec.filename, "verified_by": None, "verified_date": None,
                        "note": "DRAFT answer sheet produced by the pipeline itself; a human must check every row against the PDF before it is gold."})
        gp.write_text(json.dumps(payload) + chr(10), encoding="utf-8")
        rep.notes.append(f"Draft answer sheet written to {gp} ({what}, unverified).")

    for rec in recs:
        led.upsert_document(rec)
        for f in rec.flags:
            led.queue(run_id, rec.document_id, "intake", rec.filename, f)
        if model is None or rec.doc_class not in TERM_CLASSES:
            continue
        if over_budget():
            rep.notes.append(f"HARD STOP at {DAILY_CALL_STOP} model calls today; {rec.filename} and later documents were not read")
            led.queue(run_id, rec.document_id, "extraction", rec.filename, "not read: the daily model-call limit was reached")
            break
        refused = key_refused()
        if refused:
            rep.notes.append(f"STOPPED: the API refused the key ({refused}); {rec.filename} and later documents were not read. Nothing was cached, so a re-run costs only what failed")
            led.queue(run_id, rec.document_id, "extraction", rec.filename, f"not read: the API refused the key ({refused})")
            break
        try:
            reading = reader_for(rec).read(rec)
        except NotImplementedError as e:   # a Word file or spreadsheet before their readers exist: flag it, read the rest
            led.queue(run_id, rec.document_id, "reading", rec.filename, str(e))
            continue
        if reading.quality == "none":
            led.queue(run_id, rec.document_id, "reading", rec.filename, "no text layer; needs the document reading service")
            continue
        led.supersede_document(rec.document_id, run_id)
        led.supersede_terms(rec.document_id, run_id)
        if rec.doc_class == "rate_card":
            out = extract_rate_card(rec, reading, model, cfg, expand=all_periods)
            rep.base_rows += out.base_rows; rep.expanded_rows += out.expanded_rows
            for fl in out.flags:
                led.queue(run_id, rec.document_id, "extraction", rec.filename, fl)
            gold_rows = store_rows(rec, out, reading.quality)
            if gold_rows:
                write_gold(rec, f"{rec.document_id}.draft.jsonl", {"contract": "RateCardExtraction", "rows": gold_rows}, f"{len(gold_rows)} rows")
        if terms and rec.readiness != "web":   # a saved web page is a rate card; its commercial terms live in separate documents
            tout = extract_sow(rec, reading, model, cfg, max_sections=max_sections, exclude=rate_table_pages(reading) if rec.doc_class == "rate_card" else None)
            if tout.sections or tout.pages_selected:
                d = store_terms(rec, tout)
                if tout.rows:
                    d["prose_rate_rows"] = len(tout.rows)
                    store_rows(rec, tout, reading.quality)
                rep.term_docs.append(d)
                if tout.facts or tout.terms or tout.resources:
                    write_gold(rec, f"{rec.document_id}.terms.draft.jsonl",
                               {"contract": "SOWExtraction", "facts": [f.model_dump(mode="json") for f in tout.facts],
                                "terms": [t.model_dump(mode="json") for t in tout.terms], "named_resources": [r.model_dump(mode="json") for r in tout.resources],
                                "rate_rows": [r.model_dump(mode="json") for r in tout.rows]},
                               f"{len(tout.facts)} facts, {len(tout.terms)} conditions")
    if model is not None and terms:
        rep.disclosure_status, rep.disclosure = disclosure_check(led, recs, run_id)
    rep.calls = llm.log_summary()
    _log_calls(cache_dir, run_id, rep.calls)
    led.finish_run(run_id, f"rows={rep.rows_kept} counted={rep.counted} facts={rep.facts} terms={rep.terms}")
    led.close()
    return rep


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--vendor", help="answers an unknown printed vendor name; the answer is kept in the ledger's vendor-name table")
    ap.add_argument("--client", help="the client, a setting of the deployment")
    ap.add_argument("--ledger", default="ledger.sqlite")
    ap.add_argument("--no-model", action="store_true", help="intake and reading only")
    ap.add_argument("--no-terms", action="store_true", help="rates only; skip term reading")
    ap.add_argument("--max-sections", type=int, default=20, help="model calls per document for term reading")
    ap.add_argument("--first-period-only", action="store_true", help="keep year 1 of a grid only (shorter report, for the demo); the default copies every contract year")
    ap.add_argument("--reporting-currency", default="CAD")
    a = ap.parse_args(argv)
    model = None if a.no_model else AnthropicModel(llm.DEFAULT_MODEL)
    rep = run_family(a.paths, vendor=a.vendor, client=a.client, ledger_path=a.ledger, model=model, reporting_currency=a.reporting_currency,
                     terms=not a.no_terms, max_sections=a.max_sections, all_periods=not a.first_period_only)
    print(rep.plain())
    return 0


if __name__ == "__main__":
    sys.exit(main())
