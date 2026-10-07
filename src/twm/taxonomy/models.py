"""Pydantic models for the TWM Role Framework tables (taxonomy/*.csv).

One model per CSV row type. The CSVs are the versioned artifacts; these models
validate them on load and are the types the pipeline passes around.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Band = Literal["junior", "intermediate", "senior", "lead_principal"]
BANDS: tuple[str, ...] = ("junior", "intermediate", "senior", "lead_principal")
BAND_ORDER: dict[str, int] = {b: i for i, b in enumerate(BANDS)}

Location = Literal["onshore", "nearshore", "offshore"]
MappingMethod = Literal["rule", "model", "human"]
MappingStatus = Literal["active", "flagged", "deprecated"]


def _blank_to_none(v):
    if isinstance(v, str) and v.strip() == "":
        return None
    return v


class RoleFamily(BaseModel):
    """taxonomy/role_families.csv"""

    family_id: str
    name: str
    definition: str
    scope_notes: str = ""


class CanonicalRole(BaseModel):
    """taxonomy/canonical_roles.csv"""

    role_id: str
    family_id: str
    name: str
    definition: str
    disambiguation_notes: str = ""
    crosswalk_ddat: str = ""
    crosswalk_tbips: str = ""
    crosswalk_onet_soc: str = ""


class BandCrosswalkRow(BaseModel):
    """taxonomy/band_crosswalk.csv — maps a source scheme's level label to a TWM band."""

    source_scheme: str
    source_level: str
    twm_band: Band
    notes: str = ""


class TechTag(BaseModel):
    """taxonomy/tech_vocab.csv — controlled technology vocabulary (observation attribute)."""

    tag: str
    label: str
    category: str
    aliases: list[str] = Field(default_factory=list)

    @field_validator("aliases", mode="before")
    @classmethod
    def _split_aliases(cls, v):
        if isinstance(v, str):
            return [a.strip() for a in v.split("|") if a.strip()]
        return v or []


class TitleMapping(BaseModel):
    """taxonomy/title_mappings.csv — the seeded resolve-once mapping table."""

    observed_title: str
    source: str
    source_url: str = ""
    canonical_role_id: Optional[str] = None
    twm_band: Optional[Band] = None  # band implied by the title string itself; None = unmodified title
    attr_technology: Optional[str] = None
    attr_location: Optional[Location] = None
    attr_level_code_raw: Optional[str] = None
    attr_years_raw: Optional[str] = None
    confidence: float = 1.0
    method: MappingMethod = "rule"
    reviewer: str = ""
    status: MappingStatus = "active"
    version_added: str = "0.0"
    source_class: Literal["observed", "authored"] = "observed"  # observed in a source document vs written by TWM as an alias

    _norm = field_validator(
        "canonical_role_id", "twm_band", "attr_technology", "attr_location",
        "attr_level_code_raw", "attr_years_raw", mode="before",
    )(_blank_to_none)

    @field_validator("confidence", mode="before")
    @classmethod
    def _conf(cls, v):
        if v in ("", None):
            return 1.0
        return float(v)
