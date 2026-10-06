"""Intake (M2 step 1): register a document, establish what it really is, classify it, link it to its family.

Design: docs/architecture-components.md section 1.1. Rules:
- identity from content (sha256), never from the filename;
- true type from the first bytes, never from the extension (Texas DIR served HTML viewer pages as .pdf);
- classification is a hypothesis with its evidence and a confidence; "unknown" goes to a person;
- family links are made only on strong evidence (a contract number printed on the page); otherwise suggested and flagged;
- readiness says whether the text layer is usable, so document reading knows what to do.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Iterable, Optional

from .models import DocumentRecord, FamilyLink

# ---------------------------------------------------------------- true type by magic bytes
def sniff_type(head: bytes) -> str:
    if head.startswith(b"%PDF"):
        return "pdf"
    if head.startswith(b"PK"):
        # a zip container: docx/xlsx are zips with specific parts; decide by name later, call it zip here
        return "zip"
    low = head[:4096].lower()
    if b"<html" in low or b"<!doctype html" in low or b"<document>" in low:
        return "html"
    if head.startswith(b"\xff\xd8") or head.startswith(b"\x89PNG"):
        return "image"
    try:
        head[:2048].decode("utf-8")
        return "text"
    except UnicodeDecodeError:
        return "unknown"


def refine_zip_type(path: Path) -> str:
    import zipfile
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
        if "word/document.xml" in names:
            return "docx"
        if any(n.startswith("xl/") for n in names):
            return "xlsx"
    except Exception:
        pass
    return "zip"


# ---------------------------------------------------------------- text of the first pages
def first_pages_text(path: Path, true_type: str, pages: int = 3) -> tuple[str, Optional[int]]:
    """Return (text of the first pages, page count if known). Uses pdftotext for PDFs; no OCR here."""
    if true_type == "pdf":
        try:
            out = subprocess.run(["pdftotext", "-l", str(pages), "-layout", str(path), "-"],
                                 capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=120)
            text = out.stdout
        except Exception:
            text = ""
        count = None
        try:
            # cheap page count without pdfinfo: count /Type /Page objects (approximate for linearized files)
            data = path.read_bytes()
            count = len(re.findall(rb"/Type\s*/Page[^s]", data)) or None
        except Exception:
            pass
        return text, count
    if true_type == "html":
        raw = path.read_text(encoding="utf-8", errors="ignore")
        raw = re.sub(r"<(script|style|nav|header|footer)\b.*?</\1>", " ", raw, flags=re.S | re.I)
        return re.sub(r"<[^>]+>", " ", raw)[:120000], None
    if true_type == "text":
        return path.read_text(encoding="utf-8", errors="ignore")[:20000], None
    return "", None


# ---------------------------------------------------------------- classification
CONTRACT_NO_RE = re.compile(r"\b(DIR-[A-Z]{2,4}-[A-Z]{2,4}-\d{3,4}|DIR-CPO-\d{4}|MA\d{12}|\d{3}B\d{7}|RM\d{4}\.\d{2}|47QTCA\d{2}D\d{4}|GS-\d{2}F-\d{4}[A-Z])\b")

# (doc_class, confidence, patterns searched in the first pages; first match wins, in this order)
CLASS_RULES: list[tuple[str, float, list[str]]] = [
    ("timesheet", 0.90, [r"\btime\s*sheet\b", r"\btimecard\b", r"\bweek ending\b.*\bhours\b"]),
    ("invoice", 0.85, [r"\binvoice\s*(no|number|#)", r"\bremit to\b", r"\bamount due\b"]),
    ("amendment", 0.85, [r"\bamendment\s+(no\.?|number|#)?\s*\d", r"\bchange notice\b", r"\bchange order\b", r"\bfirst amendment\b|\bsecond amendment\b"]),
    ("rate_card", 0.85, [r"\brate card\b", r"\bpricing (index|and volumes|exhibit)\b", r"\bnot[- ]to[- ]exceed\b.*\brate", r"\bhourly rate\b.*\bhourly rate\b", r"\bsfia\b.*\brate",
                         r"\buk rate\b.*\boffshore rate\b", r"\bday rate\b.*\bday rate\b", r"\brole level\b.*\brate\b"]),
    ("sla", 0.80, [r"\bservice level (definitions?|agreement)\b", r"\bservice levels\b.*\bcredits?\b"]),
    ("sow", 0.85, [r"\bstatement of work\b", r"\bexhibit\s*1\b.*\bstatement of work\b", r"\btask (authorization|order)\b"]),
    ("solicitation", 0.80, [r"\brequest for (offer|proposal|quotation)\b", r"\bsolicitation\b", r"\brfo\b|\brfp\b"]),
    ("template", 0.70, [r"\bservice agreement template\b", r"\btemplate\b.*\bagreement\b", r"\bappendix d\b"]),
    ("msa", 0.85, [r"\bmaster (services?|service) agreement\b", r"\bmaster agreement\b", r"\binformation technology services agreement\b", r"\bcontract\s+(no\.?|number)\b.*\bbetween\b"]),
]


def classify(text: str, filename: str) -> tuple[str, float, str]:
    """Return (doc_class, confidence, evidence). The filename is a weak tie-breaker only."""
    low = text.lower()
    for cls, conf, pats in CLASS_RULES:
        for p in pats:
            m = re.search(p, low, re.S)
            if m:
                snippet = low[max(0, m.start() - 20): m.end() + 20].replace(chr(10), " ")
                return cls, conf, f"'{snippet.strip()}' in first pages"
    fn = filename.lower()
    for cls, key in [("rate_card", "rate_exhibit"), ("sow", "_sow"), ("msa", "signed_contract"), ("template", "template"), ("solicitation", "solicitation")]:
        if key in fn:
            return cls, 0.50, f"filename contains '{key}' (weak; first pages gave no signal)"
    return "unknown", 0.0, "no classification signal in the first pages or filename"


def title_guess(text: str) -> str:
    for line in text.splitlines():
        s = " ".join(line.split())
        if 12 <= len(s) <= 120 and re.search(r"[A-Za-z]{4,}", s) and not re.search(r"\bpage \d", s.lower()):
            return s
    return ""


def readiness_of(true_type: str, text: str, page_count: Optional[int]) -> str:
    if true_type == "pdf":
        chars = len(text.strip())
        if chars < 200:
            return "scan"           # no usable text layer: needs the document reading service (OCR)
        return "text"
    if true_type == "html":
        return "web"
    if true_type in ("xlsx",):
        return "spreadsheet"
    if true_type in ("docx", "text"):
        return "text"
    return "unreadable"


# ---------------------------------------------------------------- registration
def register(path: Path | str, source_class: str = "public") -> DocumentRecord:
    p = Path(path)
    data = p.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    head = data[:8192]
    true_type = sniff_type(head)
    if true_type == "zip":
        true_type = refine_zip_type(p)
    ext = p.suffix.lower().lstrip(".")
    mismatch = (ext in ("pdf",) and true_type != "pdf") or (ext in ("docx",) and true_type != "docx") or (ext in ("xlsx",) and true_type != "xlsx")
    text, pages = first_pages_text(p, true_type)
    cls, conf, evidence = classify(text, p.name)
    rec = DocumentRecord(
        document_id="doc_" + sha[:16], fingerprint=sha, path=str(p), filename=p.name, size_bytes=len(data),
        true_type=true_type, declared_extension=ext, extension_mismatch=mismatch,
        doc_class=cls, class_confidence=conf, class_evidence=evidence,
        contract_numbers=sorted(set(CONTRACT_NO_RE.findall(text))),
        title_guess=title_guess(text), page_count=pages, readiness=readiness_of(true_type, text, pages),
        text_chars_first_pages=len(text.strip()), source_class=source_class,
    )
    if mismatch:
        rec.flags.append(f"extension says .{ext} but content is {true_type}")
    if cls == "unknown":
        rec.flags.append("classification unknown: needs a person")
    elif conf < 0.75:
        rec.flags.append(f"classification '{cls}' is weak ({conf:.2f}): confirm")
    if rec.readiness == "scan":
        rec.flags.append("no usable text layer: needs the document reading service")
    return rec


# ---------------------------------------------------------------- families
def link_family(records: list[DocumentRecord]) -> list[DocumentRecord]:
    """Link documents that share a printed contract number. The MSA (or, failing that, the earliest-classified
    agreement) is the family root. Strong evidence = the same contract number on the page of both documents.
    Documents with no contract number are only SUGGESTED into a family when every other document shares one number."""
    by_number: dict[str, list[DocumentRecord]] = {}
    for r in records:
        for n in r.contract_numbers:
            by_number.setdefault(n, []).append(r)
    if not by_number:
        return records
    dominant, members = max(by_number.items(), key=lambda kv: len(kv[1]))
    root = next((r for r in members if r.doc_class == "msa"), None) or members[0]
    for r in members:
        r.family_id = root.document_id
        if r is root:
            continue
        rel = {"sow": "under_msa", "amendment": "amends", "rate_card": "exhibit_of", "sla": "exhibit_of", "invoice": "bills_against"}.get(r.doc_class, "exhibit_of")
        r.links.append(FamilyLink(parent_id=root.document_id, relation=rel, evidence=f"contract number {dominant} printed in the first pages of both", confirmed=True))
    orphans = [r for r in records if r.family_id is None]
    if orphans and len(members) >= 2:
        for r in orphans:
            r.family_id = None
            r.links.append(FamilyLink(parent_id=root.document_id, relation="exhibit_of", evidence=f"no contract number found; arrived with the {dominant} set", confirmed=False, suggested=True))
            r.flags.append(f"family link to {dominant} is suggested only: confirm")
    return records


def register_family(paths: Iterable[Path | str], source_class: str = "public") -> list[DocumentRecord]:
    recs = [register(p, source_class) for p in paths]
    # duplicates by content
    seen: dict[str, DocumentRecord] = {}
    for r in recs:
        if r.fingerprint in seen:
            r.links.append(FamilyLink(parent_id=seen[r.fingerprint].document_id, relation="duplicate_of", evidence="identical content fingerprint", confirmed=True))
            r.flags.append("duplicate of an already-registered document")
        else:
            seen[r.fingerprint] = r
    return link_family(recs)


def family_summary(recs: list[DocumentRecord]) -> str:
    """Plain-language listing for Kyle: one line per document."""
    lines = []
    counts = Counter(r.doc_class for r in recs)
    roots = {r.family_id for r in recs if r.family_id}
    lines.append(f"{len(recs)} documents registered; classes: " + ", ".join(f"{k} {v}" for k, v in counts.most_common()) + f"; families: {len(roots)}")
    for r in recs:
        role = "ROOT" if r.family_id == r.document_id else ("linked" if r.family_id else "unlinked")
        flag = f"  FLAGS: {'; '.join(r.flags)}" if r.flags else ""
        lines.append(f"- {r.filename}: {r.doc_class} ({r.class_confidence:.2f}), {r.true_type}, {r.readiness}, {r.page_count or '?'} pp, {', '.join(r.contract_numbers) or 'no contract no.'}, {role}{flag}")
    return chr(10).join(lines)
