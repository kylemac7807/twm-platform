"""Document reading (M2 step 2): turn a registered file into text, tables and layout with positions.

Design: docs/architecture-components.md section 1.2. A Reader is a protocol; LocalPdfReader (pdfplumber) serves
native PDFs now and AzureDocumentIntelligenceReader replaces it when TWM's subscription exists. Every element keeps
page and bounding box so an extracted number can light up its source (source_ref). Each reading carries a quality
grade that follows the data to the ledger (decided Oct 5, 2026).
"""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Literal, Optional, Protocol

from pydantic import BaseModel, Field

from .models import DocumentRecord

Quality = Literal["native", "good_scan", "poor_scan", "web", "none"]


class TextLine(BaseModel):
    page: int
    text: str
    bbox: tuple[float, float, float, float]   # x0, top, x1, bottom in PDF points (web: zeros)
    confidence: float = 1.0                     # per element; OCR readers fill this in


class TableCell(BaseModel):
    row: int
    col: int
    text: str
    bbox: Optional[tuple[float, float, float, float]] = None
    confidence: float = 1.0


class TableBlock(BaseModel):
    page: int
    index: int                                  # nth table on the page
    n_rows: int
    n_cols: int
    cells: list[TableCell]
    bbox: Optional[tuple[float, float, float, float]] = None
    header: list[str] = Field(default_factory=list)

    def rows(self) -> list[list[str]]:
        grid = [["" for _ in range(self.n_cols)] for _ in range(self.n_rows)]
        for c in self.cells:
            if 0 <= c.row < self.n_rows and 0 <= c.col < self.n_cols:
                grid[c.row][c.col] = c.text
        return grid


class PageReading(BaseModel):
    page: int
    width: float
    height: float
    lines: list[TextLine]
    tables: list[TableBlock]
    char_count: int


class Reading(BaseModel):
    document_id: str
    reader: str
    quality: Quality
    quality_note: str = ""
    pages: list[PageReading]

    def text(self) -> str:
        return chr(10).join(ln.text for p in self.pages for ln in p.lines)

    def page_text(self, page: int) -> str:
        return chr(10).join(ln.text for p in self.pages if p.page == page for ln in p.lines)

    def find(self, needle: str, page: Optional[int] = None) -> list[TextLine]:
        """Lines containing the needle (case-insensitive, whitespace-normalized): the verification primitive."""
        key = " ".join(needle.lower().split())
        out = []
        for p in self.pages:
            if page is not None and p.page != page:
                continue
            for ln in p.lines:
                if key in " ".join(ln.text.lower().split()):
                    out.append(ln)
        return out

    def all_tables(self) -> list[TableBlock]:
        return [t for p in self.pages for t in p.tables]


class Reader(Protocol):
    name: str

    def read(self, record: DocumentRecord) -> Reading: ...


# ---------------------------------------------------------------- local native-PDF reader
class LocalPdfReader:
    """pdfplumber over the text layer. No OCR: a scanned PDF comes back with quality 'none' and no lines."""

    name = "local-pdfplumber"

    def __init__(self, max_pages: Optional[int] = None):
        self.max_pages = max_pages

    def read(self, record: DocumentRecord) -> Reading:
        import pdfplumber

        pages: list[PageReading] = []
        total_chars = 0
        with pdfplumber.open(record.path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                if self.max_pages and i > self.max_pages:
                    break
                words = page.extract_words(keep_blank_chars=False, use_text_flow=False, extra_attrs=[])
                lines = _group_words_into_lines(words, i)
                tables = []
                try:
                    for ti, tbl in enumerate(page.find_tables()):
                        data = tbl.extract()
                        cells = []
                        n_rows = len(data)
                        n_cols = max((len(r) for r in data), default=0)
                        for r_i, row in enumerate(data):
                            for c_i, val in enumerate(row):
                                cell_bbox = None
                                try:
                                    cell_bbox = tuple(round(v, 1) for v in tbl.rows[r_i].cells[c_i]) if tbl.rows[r_i].cells[c_i] else None
                                except Exception:
                                    pass
                                cells.append(TableCell(row=r_i, col=c_i, text=" ".join(str(val or "").split()), bbox=cell_bbox))
                        header = [" ".join(str(v or "").split()) for v in (data[0] if data else [])]
                        tables.append(TableBlock(page=i, index=ti, n_rows=n_rows, n_cols=n_cols, cells=cells,
                                                 bbox=tuple(round(v, 1) for v in tbl.bbox), header=header))
                except Exception:
                    pass
                chars = sum(len(ln.text) for ln in lines)
                total_chars += chars
                pages.append(PageReading(page=i, width=float(page.width), height=float(page.height), lines=lines, tables=tables, char_count=chars))
        n_pages = max(1, len(pages))
        if total_chars < 200 * n_pages * 0.2:
            quality, note = "none", "no usable text layer: send to the document reading service (OCR)"
        else:
            quality, note = "native", f"text layer present, {total_chars} characters over {len(pages)} pages"
        return Reading(document_id=record.document_id, reader=self.name, quality=quality, quality_note=note, pages=pages)


def _group_words_into_lines(words: list[dict], page_no: int, y_tol: float = 3.0) -> list[TextLine]:
    """Group pdfplumber words into visual lines by vertical position; keep the line's bounding box."""
    if not words:
        return []
    words = sorted(words, key=lambda w: (round(w["top"] / y_tol), w["x0"]))
    lines: list[TextLine] = []
    cur: list[dict] = []
    cur_top: Optional[float] = None
    for w in words:
        if cur_top is None or abs(w["top"] - cur_top) <= y_tol:
            cur.append(w)
            cur_top = w["top"] if cur_top is None else cur_top
        else:
            lines.append(_line_from(cur, page_no))
            cur, cur_top = [w], w["top"]
    if cur:
        lines.append(_line_from(cur, page_no))
    return lines


def _line_from(ws: list[dict], page_no: int) -> TextLine:
    ws = sorted(ws, key=lambda w: w["x0"])
    text_parts, prev_x1 = [], None
    for w in ws:
        if prev_x1 is not None and w["x0"] - prev_x1 > 12:
            text_parts.append("  ")  # a visible gap: keeps columns distinguishable
        text_parts.append(w["text"])
        if prev_x1 is not None and w["x0"] - prev_x1 <= 12:
            pass
        prev_x1 = w["x1"]
    text = " ".join(text_parts).replace("   ", "  ")
    bbox = (round(min(w["x0"] for w in ws), 1), round(min(w["top"] for w in ws), 1),
            round(max(w["x1"] for w in ws), 1), round(max(w["bottom"] for w in ws), 1))
    return TextLine(page=page_no, text=" ".join(text.split(" ")).strip(), bbox=bbox)


# ---------------------------------------------------------------- web page reader (G-Cloud service pages)
class HtmlReader:
    """A saved web page: text lines and HTML tables. Positions are not meaningful; page=1, bbox zeros.
    Provenance for web pages is the row's position in the table (table index, row), carried in TableCell.row/col."""

    name = "local-html"

    def read(self, record: DocumentRecord) -> Reading:
        raw = Path(record.path).read_text(encoding="utf-8", errors="ignore")
        tables: list[TableBlock] = []
        for ti, tm in enumerate(re.finditer(r"<table\b.*?</table>", raw, re.S | re.I)):
            rows = []
            for rm in re.finditer(r"<tr\b.*?</tr>", tm.group(0), re.S | re.I):
                cells = [" ".join(html.unescape(re.sub(r"<[^>]+>", " ", c)).split()) for c in re.findall(r"<t[hd]\b.*?</t[hd]>", rm.group(0), re.S | re.I)]
                if cells:
                    rows.append(cells)
            if not rows:
                continue
            n_cols = max(len(r) for r in rows)
            cells = [TableCell(row=ri, col=ci, text=val) for ri, r in enumerate(rows) for ci, val in enumerate(r)]
            tables.append(TableBlock(page=1, index=ti, n_rows=len(rows), n_cols=n_cols, cells=cells, header=rows[0]))
        text = html.unescape(re.sub(r"<[^>]+>", chr(10), re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)))
        lines = [TextLine(page=1, text=" ".join(l.split()), bbox=(0, 0, 0, 0)) for l in text.splitlines() if l.strip()]
        page = PageReading(page=1, width=0, height=0, lines=lines, tables=tables, char_count=sum(len(l.text) for l in lines))
        return Reading(document_id=record.document_id, reader=self.name, quality="web", quality_note=f"{len(tables)} HTML tables", pages=[page])


def reader_for(record: DocumentRecord) -> Reader:
    if record.true_type == "pdf":
        return LocalPdfReader()
    if record.true_type == "html":
        return HtmlReader()
    raise NotImplementedError(f"no reader for true_type={record.true_type} yet (spreadsheets and Word arrive with reconciliation)")
