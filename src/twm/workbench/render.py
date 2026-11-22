"""Workbench page rendering (work/workbench/plan.md step 2): the page a ledger row came from, as an image with the row's box drawn.

The ledger stores the row's position as pdfplumber gives it: page number and (x0, top, x1, bottom) in PDF points, origin at the
top-left. Web-page rows carry no position (zeros); for them the quoted table cells are the position. Rendered pages are cached
on disk by file content, page and resolution (`.cache/pages/`, ignored by git) because rendering a page is the slow part.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

import pdfplumber
from PIL import Image, ImageDraw

CACHE_DIR = Path(".cache/pages")
RESOLUTION = 110          # dots per inch for the page image: readable, and a letter page stays under 1,000 px wide
BOX_COLOUR = (214, 40, 40)


def page_size(pdf_path: Path | str, page_no: int) -> tuple[float, float]:
    with pdfplumber.open(pdf_path) as pdf:
        p = pdf.pages[page_no - 1]
        return float(p.width), float(p.height)


def page_image(pdf_path: Path | str, page_no: int, resolution: int = RESOLUTION, cache_dir: Path | str = CACHE_DIR) -> Image.Image:
    """The page as an RGB image, from the cache when the same file, page and resolution were rendered before."""
    pdf_path = Path(pdf_path)
    key = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:16]
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{key}_p{page_no}_r{resolution}.png"
    if cached.exists():
        return Image.open(cached).convert("RGB")
    with pdfplumber.open(pdf_path) as pdf:
        img = pdf.pages[page_no - 1].to_image(resolution=resolution).original.convert("RGB")
    img.save(cached)
    return img


def draw_box(img: Image.Image, bbox: tuple[float, float, float, float], page_w_pt: float, page_h_pt: float,
             colour: tuple[int, int, int] = BOX_COLOUR, width: int = 3, pad: float = 2.0) -> Image.Image:
    """Draw the row's box on a copy of the page image. bbox is in PDF points; the image may be any size, so scale by its ratio."""
    sx, sy = img.width / page_w_pt, img.height / page_h_pt
    x0, top, x1, bottom = bbox
    out = img.copy()
    ImageDraw.Draw(out).rectangle([x0 * sx - pad, top * sy - pad, x1 * sx + pad, bottom * sy + pad], outline=colour, width=width)
    return out


def crop_around(img: Image.Image, bbox: tuple[float, float, float, float], page_w_pt: float, page_h_pt: float,
                margin_pt: float = 36.0) -> Image.Image:
    """A strip of the page around the box, for the close-up beside the full page."""
    sx, sy = img.width / page_w_pt, img.height / page_h_pt
    x0, top, x1, bottom = bbox
    box = (max(0, int((x0 - margin_pt) * sx)), max(0, int((top - margin_pt) * sy)),
           min(img.width, int((x1 + margin_pt) * sx)), min(img.height, int((bottom + margin_pt) * sy)))
    return img.crop(box)


def _clean(cell) -> str:
    return " ".join(str(cell or "").split())


def table_context(observation: dict, before: int = 2, after: int = 2) -> dict:
    """The row as it sits in its table: the heading rows, the row itself and a few rows either side, so a rate is seen under
    its column headings rather than as a loose quote (Kyle, Nov 22, 2026). Returns {"kind": "table", "header": [[...]],
    "rows": [{"cells": [...], "hit": bool}], "page": n} or {"kind": "none", "note": ...}. Nothing is inferred: the cells are
    what the page's table holds."""
    path = Path(observation.get("path") or "")
    page = observation.get("source_page")
    if not path.exists():
        return {"kind": "none", "note": f"document not on disk: {path}"}
    if observation.get("true_type") == "html":
        from twm.pipeline.ingest import register
        from twm.pipeline.read import reader_for
        rec = register(path)
        reading = reader_for(rec).read(rec)
        title = _clean(observation.get("observed_title")).lower()
        stated = _clean(observation.get("rate_as_stated"))
        for pg in reading.pages:
            for t in pg.tables:
                rows = [[_clean(c) for c in r] for r in t.rows()]
                for i, r in enumerate(rows):
                    if r and r[0].lower() == title and (not stated or any(stated in c for c in r)):
                        head = [rows[0]] if i > 0 else []
                        lo, hi = max(1 if head else 0, i - before), min(len(rows), i + after + 1)
                        return {"kind": "table", "page": None, "header": head, "rows": [{"cells": rows[j], "hit": j == i} for j in range(lo, hi)], "of_rows": len(rows)}
        return {"kind": "none", "note": "the row was not found in a table on the saved page"}
    bbox = _bbox_of(observation)
    if observation.get("true_type") != "pdf" or not bbox or not page:
        return {"kind": "none", "note": "no page position for this row"}
    cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    with pdfplumber.open(path) as pdf:
        pg = pdf.pages[page - 1]
        best = None
        for t in pg.find_tables():
            x0, top, x1, bottom = t.bbox
            if top - 2 <= cy <= bottom + 2:
                best = t
                break
        if best is None:
            return {"kind": "none", "note": "no table found around this row on the page"}
        cells = [[_clean(c) for c in r] for r in best.extract()]
        tops = [(r.bbox[1] + r.bbox[3]) / 2 for r in best.rows]
    if not cells:
        return {"kind": "none", "note": "the table on this page could not be read"}
    i = min(range(len(tops)), key=lambda k: abs(tops[k] - cy)) if tops else 0
    i = min(i, len(cells) - 1)
    # heading rows: the first row, and the next one or two while the row above them is mostly empty (stacked headings)
    n_head = 1
    while n_head < min(3, len(cells)) and sum(1 for c in cells[n_head - 1] if c) <= max(1, len(cells[n_head - 1]) // 2):
        n_head += 1
    n_head = min(n_head, i) if i > 0 else 0
    lo, hi = max(n_head, i - before), min(len(cells), i + after + 1)
    return {"kind": "table", "page": page, "header": cells[:n_head], "rows": [{"cells": cells[j], "hit": j == i} for j in range(lo, hi)], "of_rows": len(cells)}


def _bbox_of(observation: dict) -> Optional[tuple[float, float, float, float]]:
    raw = observation.get("source_bbox")
    if raw is None:
        return None
    vals = json.loads(raw) if isinstance(raw, str) else raw
    return tuple(float(v) for v in vals) if vals and any(vals) else None


def render_row(observation: dict, resolution: int = RESOLUTION, cache_dir: Path | str = CACHE_DIR) -> dict:
    """What the Inspect screen shows for one ledger row (a dict from Ledger.observation()). Returns a dict with "kind":
    - "pdf": "image" (page with the box), "closeup", "page", "bbox", "quote";
    - "web": no image; the quoted cells are the position ("quote", "page"); web pages store no coordinates on purpose;
    - "nobox": a PDF row with no stored position; "missing": the document is not on disk. Nothing is guessed in any case."""
    quote = observation.get("source_quote") or ""
    page = observation.get("source_page")
    path = Path(observation.get("path") or "")
    if observation.get("true_type") == "html":
        return {"kind": "web", "quote": quote, "page": page, "note": "a web page has no coordinates; the quoted table cells are the position"}
    bbox = _bbox_of(observation)
    if observation.get("true_type") != "pdf" or not bbox or not page:
        return {"kind": "nobox", "quote": quote, "page": page, "note": "no page position for this row (only PDF rows carry one)"}
    if not path.exists():
        return {"kind": "missing", "quote": quote, "page": page, "note": f"document not on disk: {path}"}
    w, h = page_size(path, page)
    img = page_image(path, page, resolution, cache_dir)
    boxed = draw_box(img, bbox, w, h)
    return {"kind": "pdf", "image": boxed, "closeup": crop_around(boxed, bbox, w, h), "page": page, "bbox": bbox, "quote": quote,
            "page_size_pt": (w, h)}
