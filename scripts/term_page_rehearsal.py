"""The library rehearsal for term reading (work/contract-terms/plan.md step 2): run the page selector over every PDF in the
document library through the reading interface, with no model and no spend, and write the counts to a markdown table.

    .venv/Scripts/python.exe scripts/term_page_rehearsal.py [library_root] [out.md]

Re-run this with the Azure reader before term reading goes live there; the counts must be as good or better.
Very long files are read up to --max-pages (default 400) so the rehearsal finishes in minutes; the table says when that bit.
"""
from __future__ import annotations

import argparse
import sys
import time
from collections import Counter
from datetime import date
from pathlib import Path
from statistics import median

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from twm.pipeline.extract import page_signals, rate_table_pages, sections_for_terms, select_term_pages  # noqa: E402
from twm.pipeline.ingest import register  # noqa: E402
from twm.pipeline.read import LocalPdfReader  # noqa: E402

NL = chr(10)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("library", nargs="?", default=str(ROOT / "corpus"))
    ap.add_argument("out", nargs="?", default=str(ROOT / "work/contract-terms/rehearsal.md"))
    ap.add_argument("--max-pages", type=int, default=400)
    a = ap.parse_args()
    lib = Path(a.library)
    files = sorted(p for p in lib.rglob("*.pdf") if p.read_bytes()[:5].startswith(b"%PDF"))
    t0 = time.time()
    rows = []
    for i, f in enumerate(files, 1):
        try:
            rec = register(f)
            rd = LocalPdfReader(max_pages=a.max_pages).read(rec)
        except Exception as e:  # a broken file is a finding, not a crash
            rows.append(dict(file=f.relative_to(lib), cls=rec.doc_class if "rec" in dir() else "?", pages=0, text=0, chosen=0, sections=0, unread=0, capped=False, signals="", error=f"{type(e).__name__}: {str(e)[:60]}"))
            continue
        text_pages = sum(1 for p in rd.pages if len(rd.page_text(p.page).strip()) >= 80)
        tables = rate_table_pages(rd)
        chosen, unread = select_term_pages(rd, exclude=tables)
        secs = sections_for_terms(rd, chosen)
        sig = Counter()
        for pg in chosen:
            sig.update(page_signals(rd.page_text(pg)))
        top = " ".join(f"{k}:{v}" for k, v in sig.most_common(4))
        rows.append(dict(file=f.relative_to(lib), cls=rec.doc_class, pages=rec.page_count or len(rd.pages), text=text_pages, chosen=len(chosen),
                         sections=len(secs), unread=unread, capped=len(rd.pages) >= a.max_pages and (rec.page_count or 0) > a.max_pages,
                         signals=top, error=""))
        if i % 10 == 0:
            print(f"{i}/{len(files)} after {time.time() - t0:.0f}s", flush=True)
    done = [r for r in rows if not r["error"]]
    with_text = [r for r in done if r["text"] > 0]
    fr = sorted(r["chosen"] / r["text"] for r in with_text) or [0]
    by_class = {}
    for r in with_text:
        c = by_class.setdefault(r["cls"], dict(n=0, pages=0, chosen=0, sections=0))
        c["n"] += 1; c["pages"] += r["text"]; c["chosen"] += r["chosen"]; c["sections"] += r["sections"]
    L = [f"# Term-reading rehearsal over the document library", "",
         f"Run {date.today().isoformat()} by `scripts/term_page_rehearsal.py` with the local reader, no model, no spend. "
         f"{len(files)} PDFs under `{lib}`; {len(done)} read, {len(files) - len(done)} failed to read. "
         f"Files longer than {a.max_pages} pages were read up to that page (marked capped).", "",
         "## What it says", "",
         f"- Share of text pages chosen for term reading: median {median(fr):.0%}, lower quartile {fr[len(fr)//4]:.0%}, upper quartile {fr[3*len(fr)//4]:.0%}, highest {max(fr):.0%}.",
         f"- Model calls a full term-reading pass over the library would make: {sum(r['sections'] for r in with_text)} (median {median(r['sections'] for r in with_text):.0f} per document, most {max(r['sections'] for r in with_text)}).",
         f"- Documents that would send every text page: {sum(1 for r in with_text if r['text'] >= 4 and r['chosen'] == r['text'])}.",
         f"- Documents of ten or more text pages that would send only the first two: {sum(1 for r in with_text if r['text'] >= 10 and r['chosen'] <= 2)} (listed below; a skills framework or a solicitation sending nothing is right).",
         "", "## By document class", "", "| Class | Documents | Text pages | Pages chosen | Calls |", "|---|---|---|---|---|"]
    for cls, c in sorted(by_class.items(), key=lambda kv: -kv[1]["n"]):
        L.append(f"| {cls} | {c['n']} | {c['pages']} | {c['chosen']} ({c['chosen'] / max(1, c['pages']):.0%}) | {c['sections']} |")
    L += ["", "## Every document", "", "| File | Class | Pages | Text pages | Chosen | Calls | Left unread by cap | Top signals |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["error"]:
            L.append(f"| {r['file']} | | | | | | | read failed: {r['error']} |"); continue
        L.append(f"| {r['file']} | {r['cls']} | {r['pages']}{' (capped)' if r['capped'] else ''} | {r['text']} | {r['chosen']} | {r['sections']} | {r['unread']} | {r['signals']} |")
    Path(a.out).write_text(NL.join(L) + NL, encoding="utf-8")
    print(f"wrote {a.out}: {len(rows)} files in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
