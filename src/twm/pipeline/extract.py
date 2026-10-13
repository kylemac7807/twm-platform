"""Extraction (M2 step 4): the model reads a section and fills a typed record; the software checks it.

Design: docs/architecture-components.md section 1.3. Decided rules:
- abstain rather than guess: an uncertain field is null and listed under `abstained`;
- verify every number against the page: a rate that does not literally appear on the claimed page is rejected;
- big documents in pieces: one model call per section (a table, or a run of pages), reassembled afterwards;
- verbatim capture only; normalization happens later.

Term reading (contract-terms stream, Oct 13, 2026; spec in work/contract-terms/spec.md): the words of a master agreement,
statement of work or amendment. Pages are chosen by a signal vocabulary (kept as data below), grouped into sections, and
the model fills SOWExtraction: identity facts, commercial terms typed with a key from the rate-conditions inventory
(specs/rate-conditions.md), named resources, rate rows found in prose. Every quote is checked word by word on its page
and carries the position of the lines that hold it; a quote the software cannot find is rejected, never stored.
Everything here works on the reading interface, never on a PDF library, so Azure Document Intelligence drops in behind it.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from twm import llm
from twm.llm import Model, ModelConfig

from .conditions import prompt_lines
from .contracts import CommercialTerm, ContractFact, NamedResource, RateCardExtraction, RateRow, SOWExtraction
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


def system_terms() -> str:
    """The term-reading prompt. Built from the rate-conditions inventory so the model types every term with a known key."""
    keys = chr(10).join("  - " + ln for ln in prompt_lines())
    return (
        "You read the commercial words of an IT services contract (master agreement, statement of work, amendment, pricing exhibit)"
        " for an audit. You are given a section of the document as page-tagged text (each page starts with 'PAGE n:'). Fill the JSON"
        " schema exactly. A later software step checks every quote against the page; anything it cannot find is thrown away, so"
        " precision matters more than coverage." + chr(10) + chr(10) +
        "Rules you must follow:" + chr(10) +
        "1. QUOTE, never paraphrase. Every fact and every term carries source_ref.page (the PAGE number the passage is on) and"
        " source_ref.quote: one contiguous passage copied exactly from that page, at most about 300 characters, the operative"
        " sentence rather than the whole clause. A quote must not span two pages." + chr(10) +
        "2. facts: the document's identity, one entry per fact, value exactly as printed (do not reformat dates or numbers):"
        " party (one entry per party), document_type (MSA, SOW, task_order, amendment, subcontract, exhibit, other), effective_date,"
        " expiry, term (the passage that fixes the term), governing_msa_ref (the master agreement this sits under), contract_number,"
        " pricing_model (time_and_materials, fixed_fee, milestone, capacity, consumption, resource_unit, mixed), amendment_number,"
        " amends (what an amendment changes), contract_value. For document_type and pricing_model the value is your typing and the"
        " quote is the evidence; for every other fact the value itself must appear on the page." + chr(10) +
        "3. commercial_terms: one entry per distinct condition that changes what is paid, when, how much, or whether the rate is"
        " comparable with another vendor's. verbatim_short is the quote (same text as source_ref.quote). term_type is the coarse"
        " type (discount, minimum_commitment, volume_tier, mfc, escalation, expense_policy, invoicing, credit, other). condition_key"
        " is one of the keys below; if none fits, use 'other' and describe the condition in condition_note in your own words." + chr(10) +
        "   Keys (key: meaning (group)):" + chr(10) + keys + chr(10) +
        "4. Skip tables of contents, definitions, cross-references, signature blocks and anything that does not change money, time"
        " or identity. Do not record the same condition twice from one section." + chr(10) +
        "5. rate_table: any printed rate for a role (an amount per hour, day, month or year) found in prose or a small table, one"
        " row per role x period x location, values verbatim as for a rate card (rate_as_stated is the exact string, rate_value the"
        " decimal). named_resources: people named with a role (key personnel), with the page and the line they appear on." + chr(10) +
        "6. If you are not certain of an item, leave it out and say so in `abstained` in one short sentence. Never infer a value"
        " that is not printed. Emit at most 25 commercial_terms per answer; if the section holds more, list the rest under"
        " abstained as 'more terms on PAGE n not emitted'." + chr(10) +
        "7. document_meta summarises the facts (parties, document_type, effective_date, term, governing_msa_ref, contract_number);"
        " the facts list is where the page and quote for each of them live. confidence (0 to 1) is your honest estimate that an"
        " item is exactly right." + chr(10) +
        "8. Answer with JSON only. No prose."
    )


@dataclass
class Section:
    page_start: int
    page_end: int
    kind: str                      # "table" | "text" | "terms"
    text: str
    table: Optional[TableBlock] = None
    pages: list[int] = field(default_factory=list)   # the pages in the section (term sections need not be contiguous)


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
    # term reading (Oct 13, 2026)
    facts: list[ContractFact] = field(default_factory=list)
    terms: list[CommercialTerm] = field(default_factory=list)
    resources: list[NamedResource] = field(default_factory=list)
    rejected_items: list[tuple[str, dict, str]] = field(default_factory=list)   # (kind, the item as the model gave it, why)
    corrections: list[str] = field(default_factory=list)                        # page corrections made by verification
    pages_selected: list[int] = field(default_factory=list)
    pages_unread: int = 0                                                       # signal pages left out by the section cap


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


# ---------------------------------------------------------------- term reading: which pages carry commercial terms
# The signal vocabulary is data: a name and a pattern. A page is sent to the model when it carries enough of them.
# On Azure, Document Intelligence's section headings replace this as the first choice; the vocabulary stays as the fallback.
TERM_SIGNALS: dict[str, str] = {
    "invoice": r"\binvoic",
    "payment": r"\bpayment terms\b|\bnet \d{2}\b|\bpayment due\b|\bpayable within\b|\bprompt pay",
    "discount": r"\bdiscount",
    "escalation": r"\bescalat|\bcost of living\b|\bcpi\b|\bconsumer price|\bannual (increase|adjustment)",
    "credit": r"\bcredits?\b[^.]{0,80}\b(service level|sla|invoice|due)|\b(service level|sla)\b[^.]{0,40}\bcredit",
    "minimum": r"\bminimum (fee|commitment|hours|spend|purchase|order)|\bno minimum\b|\btake[- ]or[- ]pay\b",
    "mfc": r"\bmost favou?red\b|\bno less favou?rable\b",
    "expenses": r"\bexpenses?\b|\btravel\b|\bper diem\b|\blodging\b|\bout[- ]of[- ]pocket\b",
    "hours": r"\bovertime\b|\bholiday|\bhours per (day|week|month)\b|\bproductive hours\b|\bbillable hours\b",
    "nte": r"\bnot[- ]to[- ]exceed\b|\bceiling\b|\bcap(ped)? at\b",
    "rates": r"\bhourly rate|\bday rate|\bdaily rate|\brate card|\brate schedule|\blabou?r categor|\bbill(ing)? rate",
    "term": r"\binitial term\b|\brenewal term\b|\bterm of (this|the) (agreement|contract)\b|\boption (year|period)s?\b|\bextension period\b",
    "dates": r"\beffective date\b|\bcommencement date\b|\bexpiration date\b|\bexpiry date\b",
    "parties": r"\bby and between\b|\bbetween\b[^.]{0,120}\band\b[^.]{0,80}\b(inc\.?|llp|llc|ltd\.?|limited|corporation|corp\.?|plc)\b",
    "contract_no": r"\bcontract (no\.?|number|#)|\bagreement (no\.?|number)|\bcontract id\b",
    "amendment": r"\bchange notice\b|\bamendment (no|number|#)|\bchange order\b|\bmodification (no|number)",
    "pricing_model": r"\bblended rate\b|\bfixed[- ](fee|price)\b|\btime and materials\b|\bt&m\b|\bmilestone\b|\bresource unit\b",
    "volume": r"\bvolume\b[^.]{0,60}\b(tier|discount|band)",
    "passthrough": r"\bpass[- ]through\b|\bmark[- ]?ups?\b|\bat cost\b",
    "personnel": r"\bkey personnel\b|\bnamed (resource|personnel|individual)",
    "value": r"\bcontract value\b|\baggregate (contract )?value\b|\btotal (contract )?value\b|\bnot to exceed \$",
}
# Three classes, tuned on the whole library (work/contract-terms/rehearsal.md), not on one document:
# a DECISIVE signal is rare and valuable enough to choose a page on its own (a most-favoured-customer clause stands alone);
# STRONG signals need company (two of them, or one with two supporting); SUPPORTING signals never choose a page by
# themselves (a contract number sits in the running header of every page of a Texas contract).
DECISIVE_SIGNALS = {"discount", "escalation", "mfc", "minimum", "volume", "nte", "credit", "hours"}
STRONG_SIGNALS = {"invoice", "payment", "rates", "term", "amendment", "value", "parties", "dates", "pricing_model", "expenses", "personnel"}
SUPPORTING_SIGNALS = {"contract_no", "passthrough"}
_SIGNAL_RX = {k: re.compile(v, re.I) for k, v in TERM_SIGNALS.items()}


def page_signals(text: str) -> list[str]:
    """The signal names a page carries."""
    return [k for k, rx in _SIGNAL_RX.items() if rx.search(text)]


def page_score(hits: list[str]) -> tuple[bool, int]:
    """(chosen, score) for a page's signals: decisive alone, or two strong, or one strong with two supporting."""
    decisive = sum(1 for h in hits if h in DECISIVE_SIGNALS)
    strong = sum(1 for h in hits if h in STRONG_SIGNALS)
    supporting = sum(1 for h in hits if h in SUPPORTING_SIGNALS)
    chosen = decisive >= 1 or strong >= 2 or (strong >= 1 and supporting >= 2)
    return chosen, decisive * 3 + strong * 2 + supporting


def select_term_pages(reading: Reading, *, always_first: int = 2, min_chars: int = 80, max_pages: int = 120,
                      exclude: Optional[set[int]] = None) -> tuple[list[int], int]:
    """Pages worth sending for term reading, in page order, and how many signal pages the cap left out.
    The first pages are always chosen (parties and the contract number live there); pages with no usable text never;
    `exclude` drops pages another path already reads (a page holding a rate table goes through the rate-card path)."""
    scored = []
    exclude = exclude or set()
    for p in reading.pages:
        if p.page in exclude:
            continue
        txt = reading.page_text(p.page)
        if len(txt.strip()) < min_chars:
            continue
        chosen, score = page_score(page_signals(txt))
        if p.page <= always_first:
            scored.append((-1000, p.page))
        elif chosen:
            scored.append((-score, p.page))
    scored.sort()
    chosen_pages = sorted(pg for _, pg in scored[:max_pages])
    return chosen_pages, max(0, len(scored) - max_pages)


def sections_for_terms(reading: Reading, pages: list[int], pages_per_section: int = 6, max_chars: int = 24000) -> list[Section]:
    """Group chosen pages, in order, into sections of at most pages_per_section pages and about max_chars characters.
    Pages need not be contiguous; each is tagged 'PAGE n:' so the model can cite it."""
    out: list[Section] = []
    buf: list[tuple[int, str]] = []
    for pg in pages:
        txt = f"PAGE {pg}:" + chr(10) + reading.page_text(pg)
        if buf and (len(buf) >= pages_per_section or sum(len(t) for _, t in buf) + len(txt) > max_chars):
            out.append(Section(buf[0][0], buf[-1][0], "terms", chr(10).join(t for _, t in buf), pages=[p for p, _ in buf]))
            buf = []
        buf.append((pg, txt))
    if buf:
        out.append(Section(buf[0][0], buf[-1][0], "terms", chr(10).join(t for _, t in buf), pages=[p for p, _ in buf]))
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


_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(s: str) -> list[str]:
    return _TOKEN.findall(s.lower().replace("’", "'").replace("‘", "'"))


def quote_on_page(reading: Reading, page: int, quote: str) -> tuple[bool, Optional[tuple[float, float, float, float]], str]:
    """True if the quote's words appear, in order and contiguously, on that page. Punctuation, case, line breaks and
    hyphenation at line ends do not matter; the words do. Returns the box around the lines that carry the quote."""
    q = "".join(_tokens(quote))
    if not q:
        return False, None, "empty quote"
    lines = [ln for p in reading.pages if p.page == page for ln in p.lines]
    # the page as one run of letters and digits, each character remembering its line, with token boundaries marked, so
    # "U.S. Dollars" and "us dollars" meet, a hyphenated line break does not matter, and "art" never matches inside "part"
    chars: list[tuple[str, int]] = []
    starts: set[int] = set()
    ends: set[int] = set()
    for i, ln in enumerate(lines):
        for t in _tokens(ln.text):
            starts.add(len(chars))
            chars.extend((c, i) for c in t)
            ends.add(len(chars))
    joined = "".join(c for c, _ in chars)
    pos = joined.find(q)
    while pos >= 0:
        if pos in starts and (pos + len(q)) in ends:
            first, last = chars[pos][1], chars[pos + len(q) - 1][1]
            boxes = [lines[i].bbox for i in range(first, last + 1)]
            bbox = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
            return True, bbox, "quote found on page"
        pos = joined.find(q, pos + 1)
    return False, None, "quote not found on the claimed page"


def locate_quote(reading: Reading, page: Optional[int], quote: Optional[str], candidate_pages: list[int]) -> tuple[Optional[int], Optional[tuple], str]:
    """Find a quote on its claimed page, else on another page of the same section. Returns (page, bbox, note)."""
    if not quote:
        return None, None, "no quote given"
    order = ([page] if page else []) + [p for p in candidate_pages if p != page]
    for pg in order:
        ok, bbox, why = quote_on_page(reading, pg, quote)
        if ok:
            note = "" if pg == page else f"quote claimed on page {page} found on page {pg}; page corrected"
            return pg, bbox, note
    return None, None, "quote not found on the claimed page or in its section"


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


_FACTS_TYPED_NOT_QUOTED = {"document_type", "pricing_model"}   # the value is the model's typing; the quote is the evidence


def _verify_rate_row(reading: Reading, row: RateRow, pages: list[int]) -> Optional[str]:
    """A rate row found in prose: the value and the title must be on the page. Returns a rejection reason or None."""
    if row.rate_value is None:
        return "abstained: no rate value"
    page = row.source_ref.page or (pages[0] if pages else 1)
    ok, why = value_on_page(reading, page, row.rate_as_stated, row.rate_value)
    if not ok:
        return why
    if not title_on_page(reading, page, row.observed_title.split("(")[0].strip()[:40]):
        return "title not found on the claimed page"
    hits = reading.find(row.observed_title.split("(")[0].strip()[:40], page=page)
    best = next((h for h in hits if row.rate_as_stated and row.rate_as_stated in h.text), hits[0] if hits else None)
    if best is not None:
        row.source_ref.bbox = best.bbox
        if not row.source_ref.quote:
            row.source_ref.quote = best.text[:200]
    row.source_ref.page = page
    return None


_RATE_HEADER = re.compile(r"\brate\b|\brates\b|\bper (hour|day|month|year)\b|/\s*(hr|hour|day)\b|\bhourly\b|\bdaily\b", re.I)


def rate_table_pages(reading: Reading) -> set[int]:
    """Pages holding a table of rates (money cells under a heading that says rate, hourly, per day); the rate-card path
    reads those, so term reading leaves them out. A money table with no such heading (a volume-discount tier table) stays
    with term reading, because its meaning is a condition, not a rate."""
    out = set()
    for s in sections_for_rate_card(reading):
        head = " ".join(" ".join(r) for r in s.table.rows()[:8]) if s.table else ""   # headings and the first rows (a unit column says "Hourly Rate")
        if _RATE_HEADER.search(head):
            out.add(s.page_start)
    return out


def extract_sow(record: DocumentRecord, reading: Reading, model: Model, config: Optional[ModelConfig] = None,
                max_sections: Optional[int] = 20, pages: Optional[list[int]] = None, exclude: Optional[set[int]] = None) -> ExtractionOutcome:
    """Term reading for a master agreement, statement of work, amendment or pricing exhibit.
    Pages are chosen by signals (or given), grouped into sections, read by the model into SOWExtraction, and every
    fact, term, named resource and rate row is verified on its page before it is kept."""
    out = ExtractionOutcome(record.document_id, "SOWExtraction", 0)
    if pages is None:
        pages, out.pages_unread = select_term_pages(reading, exclude=exclude)
    out.pages_selected = list(pages)
    secs = sections_for_terms(reading, pages)
    if max_sections and len(secs) > max_sections:
        dropped = secs[max_sections:]
        out.pages_unread += sum(len(s.pages) for s in dropped)
        out.flags.append(f"section cap {max_sections}: {len(dropped)} section(s), {sum(len(s.pages) for s in dropped)} signal page(s) not read")
        secs = secs[:max_sections]
    out.sections = len(secs)
    if not secs:
        out.flags.append("no page with commercial-term signals; nothing to read")
        return out
    schema = json.dumps(SOWExtraction.model_json_schema(), separators=(",", ":"))
    system = system_terms()
    merged: Optional[SOWExtraction] = None
    for s in secs:
        user = (f"Document: {record.filename}. Classified as {record.doc_class}. Section pages {', '.join(str(p) for p in s.pages)}:" + chr(10)
                + s.text + chr(10) + chr(10) + "Required JSON schema (answer must validate against it; source_ref.document_id may be omitted, the pipeline fills it):"
                + chr(10) + schema)
        res = llm.call(SOWExtraction, system, user, model, config)
        if res.flagged or res.output is None:
            out.flags.append(f"pages {s.page_start}-{s.page_end}: {res.flag_reason}")
            continue
        part: SOWExtraction = res.output
        out.abstained.extend(part.abstained)
        # facts: the quote must be on the page; for most fact types the value itself must be too
        for f in part.facts:
            f.source_ref.document_id = record.document_id
            pg, bbox, note = locate_quote(reading, f.source_ref.page, f.source_ref.quote or f.value, s.pages)
            if pg is None:
                out.rejected_items.append(("fact", f.model_dump(mode="json"), note)); continue
            if f.fact_type not in _FACTS_TYPED_NOT_QUOTED:
                ok, _, _ = quote_on_page(reading, pg, f.value)
                if not ok:
                    out.rejected_items.append(("fact", f.model_dump(mode="json"), "fact value not printed on the page")); continue
            if note:
                out.corrections.append(f"fact {f.fact_type}: {note}")
            f.source_ref.page, f.source_ref.bbox = pg, bbox or f.source_ref.bbox
            if not f.source_ref.quote:
                f.source_ref.quote = f.value
            out.facts.append(f)
        # commercial terms: verbatim_short is the quote
        for t in part.commercial_terms:
            t.source_ref.document_id = record.document_id
            quote = t.verbatim_short or t.source_ref.quote
            pg, bbox, note = locate_quote(reading, t.source_ref.page, quote, s.pages)
            if pg is None:
                out.rejected_items.append(("term", t.model_dump(mode="json"), note)); continue
            if note:
                out.corrections.append(f"term {t.condition_key or t.term_type}: {note}")
            t.source_ref.page, t.source_ref.bbox, t.source_ref.quote = pg, bbox or t.source_ref.bbox, quote
            out.terms.append(t)
        # named resources: the name must be on the page
        for r in part.named_resources:
            r.source_ref.document_id = record.document_id
            pg, bbox, note = locate_quote(reading, r.source_ref.page, r.name_or_role, s.pages)
            if pg is None:
                out.rejected_items.append(("named_resource", r.model_dump(mode="json"), note)); continue
            if note:
                out.corrections.append(f"named resource {r.name_or_role}: {note}")
            r.source_ref.page, r.source_ref.bbox = pg, bbox or r.source_ref.bbox
            if not r.source_ref.quote:
                r.source_ref.quote = r.name_or_role
            out.resources.append(r)
        # rate rows in prose: same checks as a rate card
        for row in part.rate_table:
            row.source_ref.document_id = record.document_id
            why = _verify_rate_row(reading, row, s.pages)
            (out.rejected if why else out.rows).append((row, why) if why else row)
        if merged is None:
            merged = part
        else:
            for k, v in part.document_meta.model_dump().items():
                if k != "source_ref" and getattr(merged.document_meta, k) in (None, [], "") and v not in (None, [], ""):
                    setattr(merged.document_meta, k, v)
            if merged.pricing_model in (None, "unstated") and part.pricing_model:
                merged.pricing_model = part.pricing_model
            merged.redactions_present = merged.redactions_present or part.redactions_present
            merged.amendment_number = merged.amendment_number or part.amendment_number
            merged.amendment_chain_amends = merged.amendment_chain_amends or part.amendment_chain_amends
    if merged:
        merged.facts, merged.commercial_terms, merged.named_resources, merged.rate_table = out.facts, out.terms, out.resources, out.rows
        out.sow = merged
        out.meta = merged.document_meta.model_dump()
    if out.rejected_items or out.rejected:
        out.flags.append(f"{len(out.rejected_items)} item(s) and {len(out.rejected)} rate row(s) rejected by page verification; see rejected_items")
    return out


extract_terms = extract_sow   # the plain name; `extract_sow` is the name the thin thread used
