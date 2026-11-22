"""Task contracts (specs/extraction-task-contracts.md): the typed records a model must fill. Verbatim capture only;
normalization is a separate stage. Every value carries a source_ref. Uncertain fields are null, never guessed."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

from .models import SourceRef
from .conditions import ConditionKey   # rate-conditions vocabulary (specs/rate-conditions.md), Oct 13, 2026


class RateRow(BaseModel):
    observed_title: str
    level_raw: Optional[str] = None            # "Level 2", "SFIA 4" (a vendor's level label), "Senior" — verbatim
    rate_value: Optional[Decimal] = None       # null when the model is not certain (abstain)
    rate_as_stated: Optional[str] = None       # the exact string on the page, e.g. "$122.00"
    currency: Optional[str] = None             # ISO code as stated or implied by the symbol
    rate_unit: Optional[Literal["hour", "day", "month", "year", "other"]] = None
    rate_qualifier: Optional[str] = None       # "NTE", "ceiling", "offshore", "Year 1"
    location_raw: Optional[str] = None         # verbatim location/tier column label
    years_experience_raw: Optional[str] = None
    period_raw: Optional[str] = None           # "Year 1 (FY27)", "2025-2026"
    conditions: Optional[str] = None
    confidence: float = Field(ge=0, le=1, default=0.0)
    source_ref: SourceRef


class DocumentMeta(BaseModel):
    issuer: Optional[str] = None
    counterparty: Optional[str] = None
    effective_date: Optional[str] = None
    expiry: Optional[str] = None
    currency: Optional[str] = None
    rate_unit: Optional[Literal["hour", "day", "month", "year", "other"]] = None
    contract_number: Optional[str] = None
    source_ref: SourceRef


class RateCardExtraction(BaseModel):
    document_meta: DocumentMeta
    rows: list[RateRow] = Field(default_factory=list)
    abstained: list[str] = Field(default_factory=list)   # things the model saw but would not commit to, in its words


class NamedResource(BaseModel):
    name_or_role: str
    observed_title: Optional[str] = None
    location_raw: Optional[str] = None
    source_ref: SourceRef
    confidence: float = Field(ge=0, le=1, default=0.0)   # added Oct 13, 2026 (stream A)


class CommercialTerm(BaseModel):
    term_type: Literal["discount", "minimum_commitment", "volume_tier", "mfc", "escalation", "expense_policy", "invoicing", "credit", "other"]
    verbatim_short: str
    source_ref: SourceRef
    confidence: float = Field(ge=0, le=1, default=0.0)
    condition_key: Optional[ConditionKey] = None   # which rate condition this is (specs/rate-conditions.md); 'other' when not listed. Added Oct 13, 2026
    condition_note: Optional[str] = None            # the model's own words when condition_key is 'other'


class SOWDocumentMeta(BaseModel):
    parties: list[str] = Field(default_factory=list)
    document_type: Optional[Literal["MSA", "SOW", "task_order", "amendment", "subcontract", "exhibit", "other"]] = None
    effective_date: Optional[str] = None
    term: Optional[str] = None
    governing_msa_ref: Optional[str] = None
    contract_number: Optional[str] = None
    source_ref: SourceRef


class SOWExtraction(BaseModel):
    document_meta: SOWDocumentMeta
    pricing_model: Optional[Literal["time_and_materials", "fixed_fee", "milestone", "capacity", "consumption", "resource_unit", "mixed", "unstated"]] = None
    rate_table: list[RateRow] = Field(default_factory=list)
    named_resources: list[NamedResource] = Field(default_factory=list)
    commercial_terms: list[CommercialTerm] = Field(default_factory=list)
    amendment_chain_amends: Optional[str] = None
    amendment_number: Optional[str] = None
    redactions_present: bool = False
    confidence_overall: float = Field(ge=0, le=1, default=0.0)
    abstained: list[str] = Field(default_factory=list)
    facts: list[ContractFact] = Field(default_factory=list)   # identity facts with page and quote each; added Oct 13, 2026 (stream A)


# ---------------------------------------------------------------- contract terms (stream A, Oct 13, 2026): additions only
FactType = Literal["party", "document_type", "effective_date", "expiry", "term", "governing_msa_ref", "contract_number",
                   "pricing_model", "amendment_number", "amends", "contract_value"]


class ContractFact(BaseModel):
    """One identity fact a document states, verbatim, with its page and quote: a party, the contract number, the effective
    date, the term, the governing agreement, the pricing model, an amendment number, what it amends, the contract value.
    Shaped so that either the frontier model or Azure's prebuilt contract model can fill it."""

    fact_type: FactType
    value: str                                   # exactly as printed
    source_ref: SourceRef
    confidence: float = Field(ge=0, le=1, default=0.0)


# Records above were extended with fields that reference classes defined later in this file; resolve them now.
SOWExtraction.model_rebuild()
