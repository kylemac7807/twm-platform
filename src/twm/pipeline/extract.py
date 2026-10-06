"""Extraction (M2 step 4): the model reads a section and fills a typed record; the software checks it.

Design: docs/architecture-components.md section 1.3. Decided rules:
- abstain rather than guess: an uncertain field is null and listed under `abstained`;
- verify every number against the page: a rate that does not literally appear on the claimed page is rejected;
- big documents in pieces: one model call per section (a table, or a run of pages), reassembled afterwards;
- verbatim capture only; normalization happens later.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from twm import llm
from twm.llm import Model, ModelConfig

from .contracts import RateCardExtraction, RateRow, SOWExtraction
from .models import DocumentRecord, SourceRef
from .read import Reading, TableBlock

SYSTEM_RATE_CARD = """You extract rate tables from procurement documents for an audit. You are given one section of a document
(a table rendered as rows, or page text) with its page number. Fill the JSON schema exactly.

Rules you must follow:
1. Copy values VERBATIM. observed_title is the title as written; rate_as_stated is the exact rate string on the page
   (e.g. "$122.00"); rate_value is that number as a decimal with no currency symbol.
2. One row per title x period x location present in the section. If a table has one column per contract year, emit one
   row per year with period_raw set to that column header (e.g. "Year 1 (FY27)"). If the table has an onsite and a
   remote block, set location_raw to the block label.
3. If you are not certain of a value, set it to null and add a short note to `abstained`. Never estimate, round, or
   infer a number that is not printed.
4. Set source_ref.page to the page number given and source_ref.quote to the exact text fragment the row came from.
5. confidence is your honest estimate (0 to 1) that the row is exactly right.
6. Answer with JSON only. No prose."""

SYSTEM_SOW = """You extract contract facts from a section of an IT services agreement for an audit. Fill the JSON schema exactly.
Copy values verbatim; set anything uncertain to null and note it under `abstained`; never infer. Capture: parties,
document type, effective date, term, the governing master agreement reference, the contract number, the pricing model,
any rate rows, named resources, and commercial terms (discounts, minimum commitments, volume tiers, most-favoured-customer,
escalation, expense policy, invoicing, credits) with a short verbatim quote each. Set source_ref.page and quote for every
item. Answer with JSON only."""


@dataclass
class Section:
    page_start: int
    page_end: int
    kind: str                      # "table" | "text"
    text: str
    table: Optional[TableBlock] = None


@dataclass
class ExtractionOutcome:
    record_id: str
    contract: str
    sections: int
    rows: list[RateRow] = field(default_factory=list)
    rejected: list[tuple[RateRow, str]] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    abstained: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    sow: Optional[SOWExtraction] = None


# ---------------------------------------------------------------- sectioning
_PLACEHOLDER = re.compile(r"^\s*[$£€]?\s*(-|0(\.00)?|n/?a)?\s*$", re.I)


def _real_money_cells(rows: list[list[str]]) -> int:
    """Cells that carry an actual amount, not '$ -', '$0.00' or blanks."""
    n = 0
    for r in rows:
        for c in r:
            if ("$" in c or "£" in c or "€" in c or re.search(r"\d+\.\d{2}", c)) and not _PLACEHOLDER.match(c):
                n += 1
    return n


def sections_for_rate_card(reading: Reading, min_rows: int = 3, min_money_cells: int = 3) -> list[Section]:
    """Each substantive table becomes one section, rendered as pipe-separated rows with the page number.
    Tables whose money cells are all placeholders ('$ -', '$0.00') are skipped: nothing to extract, nothing to spend."""
    out = []
    for p in reading.pages:
        for t in p.tables:
            if t.n_rows < min_rows:
                continue
            rows = t.rows()
            if _real_money_cells(rows) < min_money_cells:
                continue
            body = chr(10).join(" | ".join(c for c in r) for r in rows)
            out.append(Section(p.page, p.page, "table", f"PAGE {p.page}, TABLE {t.index}:" + chr(10) + body, table=t))
    return out


def sections_for_text(reading: Reading, pages_per_section: int = 6, max_chars: int = 24000) -> list[Section]:
    out, buf, start = [], [], None
    for p in reading.pages:
        txt = reading.page_text(p.page)
        if start is None:
            start = p.page
        buf.append(f"PAGE {p.page}:" + chr(10) + txt)
        if len(buf) >= pages_per_section or sum(len(b) for b in buf) > max_chars:
            out.append(Section(start, p.page, "text", chr(10).join(buf)))
            buf, start = [], None
    if buf:
        out.append(Section(start, reading.pages[-1].page, "text", chr(10).join(buf)))
    return out


# ---------------------------------------------------------------- verification against the page
_NUM = re.compile(r"[-+]?\d[\d,]*\.?\d*")


def value_on_page(reading: Reading, page: int, rate_as_stated: Optional[str], rate_value: Optional[Decimal]) -> tuple[bool, str]:
    """True if the stated rate string, or the number, literally appears on that page."""
    page_text = " ".join(reading.page_text(page).split())
    if rate_as_stated and " ".join(rate_as_stated.split()) in page_text:
        return True, "rate string found on page"
    if rate_value is not None:
        v = f"{rate_value:,.2f}"
        v2 = f"{rate_value:.2f}"
        if v in page_text or v2 in page_text:
            return True, "rate number found on page"
        # tolerate "1,250" vs "1250" and ".00" trimmed
        bare = f"{rate_value:f}".rstrip("0").rstrip(".")
        if re.search(r"(?<![\d.])" + re.escape(bare) + r"(?![\d])", page_text.replace(",", "")):
            return True, "rate number found on page (no separators)"
    return False, "value not found on the claimed page"


def title_on_page(reading: Reading, page: int, title: str) -> bool:
    return bool(reading.find(title, page=page))


# ---------------------------------------------------------------- extraction
def extract_rate_card(record: DocumentRecord, reading: Reading, model: Model, config: Optional[ModelConfig] = None,
                      min_confidence: float = 0.0) -> ExtractionOutcome:
    out = ExtractionOutcome(record.document_id, "RateCardExtraction", 0)
    secs = sections_for_rate_card(reading)
    out.sections = len(secs)
    if not secs:
        out.flags.append("no rate-bearing table found in the reading; nothing to extract")
        return out
    schema = json.dumps(RateCardExtraction.model_json_schema(), separators=(",", ":"))
    for s in secs:
        user = (f"Document: {record.filename}. Classified as {record.doc_class}. Section ({s.kind}, pages {s.page_start}-{s.page_end}):"
                + chr(10) + s.text + chr(10) + chr(10)
                + "Required JSON schema (answer must validate against it; source_ref.document_id may be omitted, the pipeline fills it):"
                + chr(10) + schema)
        res = llm.call(RateCardExtraction, SYSTEM_RATE_CARD, user, model, config)
        if res.flagged or res.output is None:
            out.flags.append(f"pages {s.page_start}-{s.page_end}: {res.flag_reason}")
            continue
        rc: RateCardExtraction = res.output
        out.abstained.extend(rc.abstained)
        if not out.meta:
            out.meta = rc.document_meta.model_dump()
        for row in rc.rows:
            row.source_ref.document_id = record.document_id
            page = row.source_ref.page or s.page_start
            row.source_ref.page = page
            ok, why = value_on_page(reading, page, row.rate_as_stated, row.rate_value)
            if row.rate_value is None:
                out.rejected.append((row, "abstained: no rate value"))
                continue
            if not ok:
                out.rejected.append((row, why))
                continue
            if not title_on_page(reading, page, row.observed_title.split("(")[0].strip()[:40]):
                out.rejected.append((row, "title not found on the claimed page"))
                continue
            if row.confidence < min_confidence:
                out.rejected.append((row, f"confidence {row.confidence:.2f} below floor"))
                continue
            # pin the position: the line on the page that carries the title (and, when possible, the rate)
            hits = reading.find(row.observed_title.split("(")[0].strip()[:40], page=page)
            best = next((h for h in hits if row.rate_as_stated and row.rate_as_stated in h.text), hits[0] if hits else None)
            if best is not None:
                row.source_ref.bbox = best.bbox
                if not row.source_ref.quote:
                    row.source_ref.quote = best.text[:200]
            out.rows.append(row)
    if out.rejected:
        out.flags.append(f"{len(out.rejected)} row(s) rejected by page verification or abstention; see rejected")
    return out


def extract_sow(record: DocumentRecord, reading: Reading, model: Model, config: Optional[ModelConfig] = None,
                max_sections: Optional[int] = None) -> ExtractionOutcome:
    out = ExtractionOutcome(record.document_id, "SOWExtraction", 0)
    secs = sections_for_text(reading)
    if max_sections:
        secs = secs[:max_sections]
    out.sections = len(secs)
    merged: Optional[SOWExtraction] = None
    schema = json.dumps(SOWExtraction.model_json_schema(), separators=(",", ":"))
    for s in secs:
        user = (f"Document: {record.filename}. Classified as {record.doc_class}. Pages {s.page_start}-{s.page_end}:" + chr(10) + s.text
                + chr(10) + chr(10) + "Required JSON schema (source_ref.document_id may be omitted):" + chr(10) + schema)
        res = llm.call(SOWExtraction, SYSTEM_SOW, user, model, config)
        if res.flagged or res.output is None:
            out.flags.append(f"pages {s.page_start}-{s.page_end}: {res.flag_reason}")
            continue
        part: SOWExtraction = res.output
        for item in [*part.rate_table, *part.named_resources, *part.commercial_terms]:
            item.source_ref.document_id = record.document_id
            item.source_ref.page = item.source_ref.page or s.page_start
        out.abstained.extend(part.abstained)
        if merged is None:
            merged = part
        else:
            # fill meta gaps from later sections; append lists
            for k, v in part.document_meta.model_dump().items():
                if k != "source_ref" and getattr(merged.document_meta, k) in (None, [], "") and v not in (None, [], ""):
                    setattr(merged.document_meta, k, v)
            merged.rate_table.extend(part.rate_table)
            merged.named_resources.extend(part.named_resources)
            merged.commercial_terms.extend(part.commercial_terms)
            if merged.pricing_model in (None, "unstated") and part.pricing_model:
                merged.pricing_model = part.pricing_model
            merged.redactions_present = merged.redactions_present or part.redactions_present
    if merged:
        verified = []
        for row in merged.rate_table:
            ok, why = value_on_page(reading, row.source_ref.page or 1, row.rate_as_stated, row.rate_value)
            (verified if ok and row.rate_value is not None else out.rejected).append(row if ok and row.rate_value is not None else (row, why))
        merged.rate_table = verified
        out.rows = verified
        out.sow = merged
        out.meta = merged.document_meta.model_dump()
    return out
