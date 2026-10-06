"""Pipeline records shared across stages (M2). Every record carries provenance; nothing here is a conclusion."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field

TrueType = Literal["pdf", "docx", "xlsx", "html", "text", "zip", "image", "unknown"]
DocClass = Literal["msa", "sow", "amendment", "rate_card", "invoice", "timesheet", "solicitation", "template", "sla", "unknown"]
Readiness = Literal["text", "scan", "web", "spreadsheet", "unreadable"]


class SourceRef(BaseModel):
    """Where a value came from: the audit coordinate every extracted number must carry."""

    document_id: str
    page: Optional[int] = None          # 1-based
    bbox: Optional[tuple[float, float, float, float]] = None  # x0, top, x1, bottom in PDF points
    section: Optional[str] = None
    table: Optional[str] = None
    quote: Optional[str] = None         # the verbatim text the value was read from


class FamilyLink(BaseModel):
    """A relationship between two registered documents."""

    parent_id: str                      # the document this one sits under (e.g. the MSA for a SOW)
    relation: Literal["under_msa", "amends", "exhibit_of", "bills_against", "duplicate_of"]
    evidence: str                       # what the link rests on, e.g. "contract number DIR-STS-TSS-699 on page 1"
    confirmed: bool = False             # True once an analyst confirmed it, or evidence was strong enough to auto-link
    suggested: bool = False             # True when intake could only suggest; the analyst decides


class DocumentRecord(BaseModel):
    """One registered document. Identity, true type, classification, family, readiness. Never edited in place."""

    document_id: str                    # stable id: sha256 of content, first 16 hex chars, prefixed "doc_"
    fingerprint: str                    # full sha256 of the bytes
    path: str                           # where it was read from (local tier)
    filename: str
    size_bytes: int
    true_type: TrueType
    declared_extension: str
    extension_mismatch: bool = False    # e.g. ".pdf" that is really HTML
    doc_class: DocClass = "unknown"
    class_confidence: float = 0.0
    class_evidence: str = ""            # the phrase or feature the classification rests on
    contract_numbers: list[str] = Field(default_factory=list)
    title_guess: str = ""
    page_count: Optional[int] = None
    readiness: Readiness = "unreadable"
    text_chars_first_pages: int = 0
    family_id: Optional[str] = None     # id of the family root (normally the MSA's document_id)
    links: list[FamilyLink] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)   # anything an analyst must look at
    registered_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))
    source_class: Literal["public", "consortium", "synthetic"] = "public"
    notes: list[str] = Field(default_factory=list)
