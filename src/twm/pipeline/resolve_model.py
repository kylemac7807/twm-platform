"""Normalization model step (M2 step 5; decided Oct 6, 2026).

Order for an unknown title: rules and the mapping table first (normalize.resolve); then similarity search over
titles already resolved; then ONE model call with the document context, the candidate roles and their
disambiguation notes; accept only above the confidence floor; write the answer back so it is never asked again;
otherwise flag for the analyst. Resolve once, look up thereafter (architecture decision 3).

v0 similarity is token overlap over the mapping table and role names (no embedding service yet); Azure AI Search
replaces it later behind the same function.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal, Optional

from pydantic import BaseModel, Field

from twm import llm
from twm.llm import Model, ModelConfig
from twm.taxonomy.models import TitleMapping
from twm.taxonomy.store import TaxonomyStore, title_key

from .normalize import ResolutionResult, resolve

CONFIDENCE_FLOOR = 0.75
SIMILARITY_FLOOR = 0.34
MAX_CANDIDATES = 6

_STOP = {"of", "and", "the", "it", "a", "an", "for", "to", "in", "ii", "iii", "iv", "i", "sr", "jr", "senior", "junior", "lead", "principal"}


class TitleResolution(BaseModel):
    """Contract 3 in specs/extraction-task-contracts.md."""

    canonical_role_id: Optional[str] = None
    twm_band: Optional[Literal["junior", "intermediate", "senior", "lead_principal"]] = None
    attr_technology: Optional[str] = None
    attr_location: Optional[Literal["onshore", "nearshore", "offshore"]] = None
    reasoning: str = ""
    confidence: float = Field(ge=0, le=1, default=0.0)
    abstain: bool = False


SYSTEM = """You map an observed job title from an IT services contract to ONE canonical role in the TWM Role Framework.
You are given the title, the surrounding document context, and a short list of candidate roles with the notes that
distinguish each from its neighbours. Rules:
1. Choose a canonical_role_id from the candidates ONLY. If none fits, set abstain=true and canonical_role_id=null.
2. twm_band: only if the title or context states seniority (Senior, Lead, Level 3, '10+ years'); otherwise null.
   Never assume a band. The consulting pyramid (Analyst=junior, Consultant=intermediate, Senior Consultant/Manager=senior,
   Senior Manager=lead_principal) counts as stated seniority.
3. attr_technology: only a tag from the list given, only if the title names that technology; otherwise null.
4. attr_location: only if the title or context says onshore/nearshore/offshore in those words; a city or country is
   NOT enough (an analyst decides those). Otherwise null.
5. reasoning: two sentences a consultant can read, naming the distinguishing note you relied on.
6. confidence: your honest probability the role is right. Below 0.75 the answer will be sent to a human.
Answer with JSON only."""


def _tokens(s: str) -> set[str]:
    return {t for t in title_key(s).split() if t not in _STOP and len(t) > 1}


def similar_roles(store: TaxonomyStore, title: str, k: int = MAX_CANDIDATES) -> list[tuple[str, float, str]]:
    """Candidate roles by token overlap with resolved titles and role names: (role_id, score, matched_text)."""
    q = _tokens(title)
    if not q:
        return []
    best: dict[str, tuple[float, str]] = {}

    def consider(role_id: str, text: str):
        t = _tokens(text)
        if not t:
            return
        score = len(q & t) / len(q | t)
        if score > best.get(role_id, (0.0, ""))[0]:
            best[role_id] = (score, text)

    for m in store.mappings:
        if m.status == "active" and m.canonical_role_id:
            consider(m.canonical_role_id, m.observed_title)
    for r in store.roles:
        consider(r.role_id, r.name)
    ranked = sorted(((rid, sc, tx) for rid, (sc, tx) in best.items()), key=lambda x: -x[1])
    return [(rid, round(sc, 3), tx) for rid, sc, tx in ranked[:k] if sc >= SIMILARITY_FLOOR]


@dataclass
class ModelStepOutcome:
    result: ResolutionResult
    used_model: bool
    candidates: list[tuple[str, float, str]]
    new_mapping: Optional[TitleMapping] = None


def resolve_with_model(title: str, store: TaxonomyStore, model: Optional[Model], *, context: str = "", source: Optional[str] = None,
                       source_scheme: Optional[str] = None, source_level: Optional[str] = None, client_country: Optional[str] = None,
                       config: Optional[ModelConfig] = None, write_back: bool = True) -> ModelStepOutcome:
    """Rules first; if flagged, similarity then the model; accepted answers are written to the mapping table."""
    base = resolve(title, store, source=source, source_scheme=source_scheme, source_level=source_level, client_country=client_country)
    if base.status != "flagged" or model is None:
        return ModelStepOutcome(base, False, [])
    cands = similar_roles(store, title)
    if not cands:
        base.notes.append("model step skipped: no similar resolved titles or role names")
        return ModelStepOutcome(base, False, [])
    cand_text = chr(10).join(
        f"- {rid}: {store.role_by_id[rid].name} — {store.role_by_id[rid].disambiguation_notes[:300]} (nearest known title: '{tx}', similarity {sc})"
        for rid, sc, tx in cands if rid in store.role_by_id
    )
    tech_tags = ", ".join(sorted(store.tech_by_tag))
    user = (f"Observed title: {title}" + chr(10) + f"Source: {source or 'unknown'}; level evidence: {source_level or 'none'}" + chr(10)
            + f"Document context: {context[:1500] or '(none)'}" + chr(10) + chr(10) + "Candidate roles:" + chr(10) + cand_text + chr(10) + chr(10)
            + f"Technology tags allowed: {tech_tags}" + chr(10) + chr(10)
            + "JSON schema: " + json.dumps(TitleResolution.model_json_schema(), separators=(",", ":")))
    res = llm.call(TitleResolution, SYSTEM, user, model, config)
    out = base
    out.method = "model"
    if res.flagged or res.output is None:
        out.notes.append(f"model step failed: {res.flag_reason}")
        return ModelStepOutcome(out, True, cands)
    ans: TitleResolution = res.output
    if ans.abstain or not ans.canonical_role_id or ans.canonical_role_id not in {c[0] for c in cands} or ans.confidence < CONFIDENCE_FLOOR:
        out.candidates = [c[0] for c in cands]
        out.notes.append(f"model abstained or below floor (conf {ans.confidence:.2f}): {ans.reasoning[:200]}")
        return ModelStepOutcome(out, True, cands)
    out.status = "resolved"
    out.canonical_role_id = ans.canonical_role_id
    out.family_id = store.role_by_id[ans.canonical_role_id].family_id
    out.matched_on = "model"
    out.confidence = ans.confidence
    if out.twm_band is None and ans.twm_band:
        out.twm_band, out.band_source, out.needs_band_review = ans.twm_band, "model_from_context", False
    if ans.attr_technology in store.tech_by_tag and not out.attr_technology:
        out.attr_technology = ans.attr_technology
    if ans.attr_location and not out.attr_location and not out.needs_location_review and not out.attr_location_raw:
        # only when the rules saw no place name at all; a flagged place stays with the analyst (Kyle, Sept 19)
        out.attr_location, out.location_source = ans.attr_location, "model_explicit_word"
    out.notes.append("model: " + ans.reasoning[:300])
    new = None
    if write_back:
        new = TitleMapping(observed_title=title, source=source or "model", canonical_role_id=ans.canonical_role_id,
                           twm_band=ans.twm_band, attr_technology=out.attr_technology, confidence=ans.confidence,
                           method="model", reviewer="", status="active", version_added="0.1", source_class="observed")
        store.mappings.append(new)
        store.mapping_index.setdefault(title_key(title), []).append(new)
    return ModelStepOutcome(out, True, cands, new)
