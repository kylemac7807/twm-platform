"""End-to-end run (M2 step 7): a document family through intake, reading, extraction, normalization and the ledger,
with a plain-language report for Kyle and a drafted answer sheet for the evaluation sample.

    .venv/Scripts/python.exe -m twm.pipeline.run corpus/manifests/v3_downloads/v3_gov/08[1-7]*.pdf --vendor "Accenture LLP" --client "Texas DIR"
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

from .extract import extract_rate_card
from .ingest import family_summary, register_family
from .ledger import Ledger
from .models import DocumentRecord
from .read import reader_for
from .resolve_model import resolve_with_model

RULE_VERSION = "0.1"


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

    def plain(self) -> str:
        L = [f"Run {self.run_id}", "", family_summary(self.documents), ""]
        L.append(f"Rates extracted and verified against the page: {self.rows_kept} (rejected by verification or abstention: {self.rows_rejected}).")
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
        if self.calls:
            L.append("")
            L.append(f"Model calls: {self.calls.get('calls')} ({self.calls.get('validated')} validated, {self.calls.get('cached')} from cache); "
                     f"tokens {self.calls.get('input_tokens')} in / {self.calls.get('output_tokens')} out.")
        for n in self.notes:
            L.append("Note: " + n)
        return chr(10).join(L)


def run_family(paths, *, vendor: Optional[str], client: Optional[str], ledger_path: Path | str, model: Optional[Model],
               reporting_currency: str = "CAD", source_class: str = "public", cache_dir: Optional[Path] = Path(".cache/llm"),
               gold_dir: Optional[Path] = Path("evals/gold"), store: Optional[TaxonomyStore] = None) -> RunReport:
    store = store or TaxonomyStore.load()
    cfg = ModelConfig(model=getattr(model, "name", llm.DEFAULT_MODEL), cache_dir=cache_dir, max_tokens=16000)
    run_id = "run_" + date.today().isoformat() + "_" + uuid.uuid4().hex[:6]
    recs = register_family(paths, source_class)
    rep = RunReport(run_id, recs)
    led = Ledger(ledger_path)
    led.start_run(run_id, "local", cfg.model, RULE_VERSION)
    llm.LOG.clear()
    for rec in recs:
        led.upsert_document(rec)
        for f in rec.flags:
            led.queue(run_id, rec.document_id, "intake", rec.filename, f)
        if rec.doc_class not in ("rate_card",) or model is None:
            continue   # M2: rate cards through extraction; SOW/MSA term extraction is the next task
        reading = reader_for(rec).read(rec)
        if reading.quality == "none":
            led.queue(run_id, rec.document_id, "reading", rec.filename, "no text layer; needs the document reading service")
            continue
        out = extract_rate_card(rec, reading, model, cfg)
        led.supersede_document(rec.document_id, run_id)
        rep.rows_kept += len(out.rows); rep.rows_rejected += len(out.rejected)
        for fl in out.flags:
            led.queue(run_id, rec.document_id, "extraction", rec.filename, fl)
        gold_rows = []
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
            obs_id = led.add_observation(run_id, rec, row, r, vendor=vendor, client=client, effective_date=None, scan_quality=reading.quality,
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
        if gold_dir and gold_rows:
            gold_dir = Path(gold_dir); gold_dir.mkdir(parents=True, exist_ok=True)
            gp = gold_dir / f"{rec.document_id}.draft.jsonl"
            gp.write_text(json.dumps({"document_id": rec.document_id, "filename": rec.filename, "contract": "RateCardExtraction",
                                      "rows": gold_rows, "verified_by": None, "verified_date": None,
                                      "note": "DRAFT answer sheet produced by the pipeline itself; a human must check every row against the PDF before it is gold."}) + chr(10), encoding="utf-8")
            rep.notes.append(f"Draft answer sheet written to {gp} ({len(gold_rows)} rows, unverified).")
    rep.calls = llm.log_summary()
    led.finish_run(run_id, f"rows={rep.rows_kept} counted={rep.counted}")
    led.close()
    return rep


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--vendor"); ap.add_argument("--client")
    ap.add_argument("--ledger", default="ledger.sqlite")
    ap.add_argument("--no-model", action="store_true", help="intake and reading only")
    ap.add_argument("--reporting-currency", default="CAD")
    a = ap.parse_args(argv)
    model = None if a.no_model else AnthropicModel(llm.DEFAULT_MODEL)
    rep = run_family(a.paths, vendor=a.vendor, client=a.client, ledger_path=a.ledger, model=model, reporting_currency=a.reporting_currency)
    print(rep.plain())
    return 0


if __name__ == "__main__":
    sys.exit(main())
