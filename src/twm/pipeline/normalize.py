"""Title normalization: the deterministic rules that run before any model call.

Implements specs/role-framework-v0-spec.md rules 1-6:
  1. strip and capture seniority modifiers (Sr/Senior/Jr/Lead/Principal/Staff, roman numerals, trailing digits, "Level N")
  2. strip and capture location tokens (onshore/offshore/nearshore/remote, a few country/city names)
  3. strip and capture technology tokens against taxonomy/tech_vocab.csv
  4. exact/alias match against the mapping table -> deterministic hit
  5. no match -> embedding similarity against resolved titles (pluggable; no model is wired in v0)
  6. still unresolved or confidence < 0.75 -> status=flagged (human queue)

Band precedence when resolving an observation:
  source level code (via band_crosswalk) > stated years > title modifier > default 'intermediate'
The band_source field on the result records which one applied, so the acceptance
report can count how many resolutions leaned on the default.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional, Protocol

from pydantic import BaseModel

from twm.taxonomy.models import Band
from twm.taxonomy.store import TaxonomyStore, title_key

CONFIDENCE_FLOOR = 0.75  # below this -> flagged (spec rule 6; calibrate on gold later)

# --------------------------------------------------------------------------- rule 1: seniority
# Leading modifiers. Order matters: longer phrases first.
_LEAD_MODIFIERS = [
    ("head of", "lead_principal"), ("chief", "lead_principal"), ("principal", "lead_principal"),
    ("lead", "lead_principal"), ("staff", "lead_principal"), ("expert", "lead_principal"),
    ("senior", "senior"), ("sr", "senior"),
    ("mid level", "intermediate"), ("intermediate", "intermediate"),
    ("junior", "junior"), ("jr", "junior"), ("associate", "junior"), ("trainee", "junior"),
    ("apprentice", "junior"), ("intern", "junior"), ("entry level", "junior"), ("graduate", "junior"),
    ("assistant", "junior"),
]
# Trailing modifiers (after title_key normalisation, so "- SME" becomes "sme", "(Senior)" -> "senior").
_TRAIL_MODIFIERS = [
    ("sme", "lead_principal"), ("subject matter expert", "lead_principal"), ("expert", "lead_principal"),
    ("principal", "lead_principal"), ("lead", "lead_principal"), ("head", "lead_principal"),
    ("senior", "senior"), ("sr", "senior"), ("mid level", "intermediate"), ("intermediate", "intermediate"),
    ("junior", "junior"), ("jr", "junior"), ("entry level", "junior"), ("entry", "junior"),
    ("associate", "junior"), ("trainee", "junior"), ("intern", "junior"),
    ("management", None),  # DDaT "- management" suffix: same band, management track
]
_ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5}
_ROMAN_RE = re.compile(r"^(?P<core>.+?) (?P<num>i{1,3}|iv|v)$")
_LEVEL_RE = re.compile(r"^(?P<core>.+?) (?:level|lvl|l|grade|band|tier) ?(?P<num>[1-5])$")
_DIGIT_RE = re.compile(r"^(?P<core>.+?[a-z]) (?P<num>[1-5])$")
_VENDOR_CODE_RE = re.compile(r"^(?P<core>.+?) (?P<code>[a-z]{2}\d{2})$")  # e.g. "program manager pm02"

_NUMERIC_BAND = {1: "junior", 2: "intermediate", 3: "senior", 4: "lead_principal", 5: "lead_principal"}

# --------------------------------------------------------------------------- rule 2: location
# Explicit delivery-location words state the classification outright.
_EXPLICIT_LOCATION = {
    "offshore": "offshore", "nearshore": "nearshore", "onshore": "onshore", "onsite": "onshore",
    "on site": "onshore", "remote": None,
}
# Place names only tell us a COUNTRY. Whether that country is onshore, nearshore or offshore
# depends on where the client is (decided Sept 19, 2026): for a Canadian bank a US resource is
# nearshore, not onshore. Classification happens in resolve() against client_country.
_PLACE_COUNTRY = {
    "uk": "GB", "united kingdom": "GB", "london": "GB", "usa": "US", "us": "US", "united states": "US",
    "new york": "US", "buffalo": "US", "charlotte": "US", "dallas": "US", "canada": "CA", "toronto": "CA", "montreal": "CA", "india": "IN", "bangalore": "IN",
    "bengaluru": "IN", "hyderabad": "IN", "pune": "IN", "chennai": "IN", "philippines": "PH", "manila": "PH",
    "poland": "PL", "mexico": "MX", "ireland": "IE", "romania": "RO", "portugal": "PT",
}
_LOCATION_TOKENS = {**_EXPLICIT_LOCATION, **{k: None for k in _PLACE_COUNTRY}}
# Which countries count as nearshore for a client in a given country. Per-deployment config in
# production; this default table covers the first target markets.
NEARSHORE: dict[str, set[str]] = {
    "CA": {"MX"},
    "US": {"CA", "MX"},          # Kyle, Sept 19: a US bank developing in Canada is almost always nearshore
    "GB": {"IE", "PL", "PT", "RO"},
}
# Pairs where geography alone cannot decide, because the label is really about cost (Kyle, Sept 19, 2026):
# for a Canadian bank, New York is an expensive onshore-equivalent market while Buffalo might be nearshore.
# These are never auto-classified. The city and country are kept, the observation is flagged, and the
# rule is refined per client as real data arrives.
LOCATION_REVIEW_PAIRS: set[tuple[str, str]] = {("CA", "US")}   # (client_country, resource_country)


def location_needs_review(country: Optional[str], client_country: Optional[str]) -> bool:
    return bool(country and client_country and (client_country, country) in LOCATION_REVIEW_PAIRS)


def suggest_location(country: Optional[str], client_country: Optional[str]) -> Optional[str]:
    """A NON-BINDING hint for the analyst. Never written to attr_location.

    Kyle, Sept 19, 2026: place names are examples for an analyst to categorize, not business rules.
    Even a city in the client's own country is not always onshore, so same-country gets no hint at all.
    """
    if not country or not client_country or country == client_country:
        return None
    if location_needs_review(country, client_country):
        return None
    if country in NEARSHORE.get(client_country, set()):
        return "nearshore"
    return "offshore"


def location_rule_key(client_key: str, place: str) -> tuple[str, str]:
    return (client_key.strip().lower(), title_key(place))


@dataclass
class NormalizedTitle:
    raw: str
    key: str                       # title_key(raw)
    core: str                      # key with seniority/location/tech tokens stripped
    seniority_token: Optional[str] = None
    band_from_title: Optional[str] = None
    level_code_raw: Optional[str] = None   # roman numeral / "level 3" / vendor grade code, verbatim-ish
    location_token: Optional[str] = None
    location: Optional[str] = None          # only set when the title says onshore/nearshore/offshore outright
    location_country: Optional[str] = None  # ISO country implied by a place name; classified later
    tech_tags: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _strip_seniority(key: str) -> tuple[str, Optional[str], Optional[str], Optional[str]]:
    """Return (core, seniority_token, band, level_code_raw)."""
    core, token, band, level_code = key, None, None, None
    # trailing structured levels first (they never conflict with the role name)
    m = _LEVEL_RE.match(core)
    if m:
        core, level_code = m.group("core"), core[len(m.group("core")) + 1:]
        band = _NUMERIC_BAND[int(m.group("num"))]
        return core, level_code, band, level_code
    m = _VENDOR_CODE_RE.match(core)
    if m:
        core, level_code = m.group("core"), m.group("code")
        # vendor grade codes are opaque; band left to source-level evidence
    m = _ROMAN_RE.match(core)
    if m:
        core, level_code = m.group("core"), m.group("num")
        band = _NUMERIC_BAND[_ROMAN[m.group("num")]]
        return core, level_code, band, level_code
    m = _DIGIT_RE.match(core)
    if m and not core.endswith(("web 3", "d365 1")):
        core, level_code = m.group("core"), m.group("num")
        band = _NUMERIC_BAND[int(m.group("num"))]
        return core, level_code, band, level_code
    # trailing word modifiers (allow one)
    for tok, b in _TRAIL_MODIFIERS:
        if core.endswith(" " + tok) and len(core) > len(tok) + 1:
            core = core[: -len(tok) - 1].strip()
            if b is not None:
                token, band = tok, b
            break
    # leading word modifiers (allow one)
    for tok, b in _LEAD_MODIFIERS:
        if core.startswith(tok + " ") and len(core) > len(tok) + 1:
            core = core[len(tok) + 1:].strip()
            if token is None:
                token, band = tok, b
            break
    return core, token, band, level_code


def _strip_location(key: str) -> tuple[str, Optional[str], Optional[str]]:
    words = key.split()
    for phrase, loc in sorted(_LOCATION_TOKENS.items(), key=lambda kv: -len(kv[0])):
        p = phrase.split()
        n = len(p)
        for i in range(len(words) - n + 1):
            if words[i:i + n] == p and len(words) > n:
                rest = words[:i] + words[i + n:]
                return " ".join(rest), phrase, loc
    return key, None, None


def _strip_tech(key: str, store: TaxonomyStore) -> tuple[str, list[str]]:
    words = key.split()
    found: list[str] = []
    changed = True
    while changed and len(words) > 1:
        changed = False
        # longest alias first so "sql server" beats "sql"
        for alias_key, tag in sorted(store.tech_alias_index.items(), key=lambda kv: -len(kv[0])):
            p = alias_key.split()
            n = len(p)
            if n == 0 or n >= len(words):
                continue
            for i in range(len(words) - n + 1):
                if words[i:i + n] == p:
                    words = words[:i] + words[i + n:]
                    if tag not in found:
                        found.append(tag)
                    changed = True
                    break
            if changed:
                break
    return " ".join(words), found


def normalize_title(raw: str, store: TaxonomyStore) -> NormalizedTitle:
    """Apply rules 1-3 and return the stripped core plus everything captured."""
    key = title_key(raw)
    nt = NormalizedTitle(raw=raw, key=key, core=key)
    # location first so a leading "Offshore ..." does not mask a seniority word
    core, loc_tok, loc = _strip_location(key)
    nt.location_token, nt.location = loc_tok, loc
    nt.location_country = _PLACE_COUNTRY.get(loc_tok) if loc_tok else None
    core, tok, band, level_code = _strip_seniority(core)
    nt.seniority_token, nt.band_from_title, nt.level_code_raw = tok, band, level_code
    core, tags = _strip_tech(core, store)
    nt.tech_tags = tags
    if tok is None and tags:
        # "Java Senior Developer": the modifier only becomes visible once the tech token is gone
        core, tok, band, level_code2 = _strip_seniority(core)
        nt.seniority_token, nt.band_from_title = tok, band
        nt.level_code_raw = nt.level_code_raw or level_code2
    nt.core = core.strip()
    return nt


# --------------------------------------------------------------------------- rule 5: embedding hook
class EmbeddingResolver(Protocol):
    """Pluggable similarity search over resolved titles. v0 ships no implementation."""

    def candidates(self, title: str, k: int = 5) -> list[tuple[str, float]]:
        """Return [(canonical_role_id, cosine_similarity), ...] sorted descending."""
        ...


# --------------------------------------------------------------------------- resolution
class ResolutionResult(BaseModel):
    observed_title: str
    source: Optional[str] = None
    canonical_role_id: Optional[str] = None
    family_id: Optional[str] = None
    twm_band: Optional[Band] = None
    band_source: Optional[str] = None      # source_level | source_level_derived | years | title_modifier
    needs_band_review: bool = False        # role resolved but no level evidence: left unbanded on purpose
    attr_technology: Optional[str] = None
    attr_location: Optional[str] = None
    attr_location_raw: Optional[str] = None      # the token as written ("toronto", "offshore")
    attr_location_country: Optional[str] = None  # ISO country when the token was a place name
    location_source: Optional[str] = None        # explicit_word | analyst_rule
    needs_location_review: bool = False          # a place name with no analyst decision yet
    location_suggestion: Optional[str] = None    # non-binding hint shown to the analyst; never used as the answer
    attr_level_code_raw: Optional[str] = None
    attr_years_raw: Optional[str] = None
    candidates: list[str] = []
    status: str = "flagged"                # resolved | ambiguous | flagged
    method: str = "rule"
    matched_on: Optional[str] = None       # full_title | core | role_name | embedding
    confidence: float = 0.0
    notes: list[str] = []


def band_from_years(years: Optional[float], store: TaxonomyStore) -> Optional[str]:
    """Spec: <3 junior, 3-7 intermediate, 7-12 senior, 12+ lead_principal."""
    if years is None:
        return None
    if years < 3:
        return "junior"
    if years < 7:
        return "intermediate"
    if years < 12:
        return "senior"
    return "lead_principal"


# When the technology IS the practice (spec: Packaged Applications family), a generic core
# like "developer" or "consultant" carrying a packaged-platform tag routes to the packaged role.
PACKAGED_CATEGORY_PREFIX = "packaged"
PACKAGED_CORE_ROLES: dict[str, str] = {
    "developer": "packaged_application_developer",
    "programmer": "packaged_application_developer",
    "programmer analyst": "packaged_application_developer",
    "technical developer": "packaged_application_developer",
    "consultant": "packaged_application_functional_consultant",
    "functional consultant": "packaged_application_functional_consultant",
    "functional analyst": "packaged_application_functional_consultant",
    "business analyst": "packaged_application_functional_consultant",
    "analyst": "packaged_application_functional_consultant",
    "system analyst": "packaged_application_functional_consultant",
    "systems analyst": "packaged_application_functional_consultant",
    "technical consultant": "packaged_application_technical_consultant",
    "technical analyst": "packaged_application_technical_consultant",
    "basis administrator": "packaged_application_technical_consultant",
    "basis consultant": "packaged_application_technical_consultant",
    "architect": "packaged_application_architect",
    "solution architect": "packaged_application_architect",
    "solutions architect": "packaged_application_architect",
    "technical architect": "packaged_application_architect",
    "administrator": "packaged_application_administrator",
    "admin": "packaged_application_administrator",
    "specialist": "packaged_application_functional_consultant",
}


def band_from_level_label(label: str) -> Optional[str]:
    """Derive a band from a free-text level label (e.g. DDaT/G-Cloud 'Senior operations analyst').

    Used only when band_crosswalk has no explicit row for (scheme, label). Leading/trailing
    seniority words decide; labels containing manager/head/chief/lead/principal are lead_principal;
    any other non-empty label is the working ('standard') level -> intermediate.
    """
    if not label or not label.strip():
        return None
    key = title_key(label)
    _, _, band, _ = _strip_seniority(key)
    if band:
        return band
    words = set(key.split())
    if words & {"manager", "head", "chief", "lead", "principal", "director", "expert"}:
        return "lead_principal"
    return "intermediate"


def _lookup(store: TaxonomyStore, key: str) -> tuple[list[str], list]:
    """Return (distinct role ids, matching mapping rows) for a title key."""
    rows = store.mapping_index.get(key, [])
    active = [r for r in rows if r.status == "active" and r.canonical_role_id]
    ids = sorted({r.canonical_role_id for r in active})
    if not ids and key in store.role_by_name_key:
        return [store.role_by_name_key[key]], []
    return ids, active


def resolve(
    observed_title: str,
    store: TaxonomyStore,
    *,
    source: Optional[str] = None,
    source_scheme: Optional[str] = None,
    source_level: Optional[str] = None,
    years: Optional[float] = None,
    client_country: Optional[str] = None,
    client_key: Optional[str] = None,
    location_rules: Optional[dict[tuple[str, str], str]] = None,
    embedder: Optional[EmbeddingResolver] = None,
) -> ResolutionResult:
    """Resolve one observed title (plus optional level evidence) to (role, band) deterministically.

    Location (decided with Kyle, Sept 19, 2026) follows the same resolve-once pattern as titles:
      1. the words onshore / nearshore / offshore in the title classify directly;
      2. a place name is classified ONLY if an analyst has already decided it for this client
         (location_rules, keyed by client_key + place; see pipeline/location_rules.py);
      3. otherwise the city and country are kept, the observation is flagged for an analyst, and a
         non-binding suggestion is attached. Once the analyst decides, the rule is recorded and every
         later occurrence is a deterministic lookup.
    client_key identifies whose rules apply (defaults to client_country).
    """
    nt = normalize_title(observed_title, store)
    res = ResolutionResult(observed_title=observed_title, source=source, attr_level_code_raw=nt.level_code_raw,
                           attr_years_raw=(str(years) if years is not None else None))
    res.attr_location_raw, res.attr_location_country = nt.location_token, nt.location_country
    ckey = client_key or client_country
    if nt.location:
        res.attr_location, res.location_source = nt.location, "explicit_word"
    elif nt.location_token and nt.location_token in _PLACE_COUNTRY:
        decided = (location_rules or {}).get(location_rule_key(ckey, nt.location_token)) if ckey else None
        if decided:
            res.attr_location, res.location_source = decided, "analyst_rule"
        else:
            res.needs_location_review = True
            res.location_suggestion = suggest_location(nt.location_country, client_country)
            res.notes.append(f"place '{nt.location_token}' has no analyst decision for client '{ckey or 'unset'}': "
                             "kept as city and country, flagged for review, not classified")
    res.attr_technology = nt.tech_tags[0] if nt.tech_tags else None
    if len(nt.tech_tags) > 1:
        res.notes.append("multiple tech tokens: " + ",".join(nt.tech_tags))

    # rule 4: exact/alias match — full title first, then the stripped core
    ids, rows = _lookup(store, nt.key)
    matched_on = "full_title" if ids else None
    row_band = None
    if ids and rows:
        # a full-title mapping row may carry its own band/tech/location
        r0 = rows[0]
        row_band = r0.twm_band
        if r0.attr_technology and not res.attr_technology:
            res.attr_technology = r0.attr_technology
        if r0.attr_location and not res.attr_location:
            res.attr_location = r0.attr_location
    packaged = any(
        store.tech_by_tag[t].category.startswith(PACKAGED_CATEGORY_PREFIX) for t in nt.tech_tags if t in store.tech_by_tag
    )
    if not ids and packaged and nt.core in PACKAGED_CORE_ROLES:
        ids, matched_on = [PACKAGED_CORE_ROLES[nt.core]], "core"
        res.notes.append("packaged-platform tag routed generic core to Packaged Applications family")
    if not ids and nt.core and nt.core != nt.key:
        ids, rows = _lookup(store, nt.core)
        matched_on = "core" if ids else None
        if ids and rows:
            row_band = rows[0].twm_band
    if not ids and nt.core in store.role_by_name_key:
        ids, matched_on = [store.role_by_name_key[nt.core]], "role_name"

    # rule 5: embedding candidates (no implementation in v0 -> skipped)
    if not ids and embedder is not None:
        cands = embedder.candidates(nt.core or nt.key)
        if cands and cands[0][1] >= 0.85:
            ids, matched_on = [cands[0][0]], "embedding"
            res.method = "model"
            res.notes.append(f"embedding sim={cands[0][1]:.3f}")
        elif cands:
            res.candidates = [c[0] for c in cands]

    if len(ids) > 1:
        res.status, res.candidates = "ambiguous", ids
        res.notes.append("multiple mapping rows disagree on role")
        return res
    if not ids:
        res.status = "flagged"
        res.notes.append("no rule match; needs model/human resolution")
        return res

    role_id = ids[0]
    res.canonical_role_id = role_id
    res.family_id = store.role_by_id[role_id].family_id
    res.matched_on = matched_on
    res.confidence = {"full_title": 0.95, "core": 0.85, "role_name": 0.80, "embedding": 0.75}[matched_on]

    # band precedence
    band, band_source = None, None
    if source_scheme and source_level:
        b = store.band_for(source_scheme, source_level)
        if b:
            band, band_source = b.twm_band, "source_level"
            res.attr_level_code_raw = source_level
        else:
            derived = band_from_level_label(source_level)
            if derived:
                band, band_source = derived, "source_level_derived"
                res.attr_level_code_raw = source_level
                res.notes.append(f"level '{source_level}' not in band_crosswalk for '{source_scheme}'; derived from label wording")
            else:
                res.notes.append(f"unknown level '{source_level}' for scheme '{source_scheme}'")
    if band is None and years is not None:
        band, band_source = band_from_years(years, store), "years"
    if band is None and (nt.band_from_title or row_band):
        # an authored full-title row knows better than the generic modifier rule ("Associate Director")
        chosen = row_band if (matched_on == "full_title" and row_band) else (nt.band_from_title or row_band)
        band, band_source = chosen, "title_modifier"
    if band is None:
        # Decided Sept 19, 2026: never invent seniority. With no level code, no stated years and no
        # modifier, the role stands and the band stays empty; the observation is excluded from
        # band-level benchmark cuts and the band alone goes to the review queue.
        res.needs_band_review = True
        res.notes.append("no level evidence: left unbanded; band to review queue")
    res.twm_band, res.band_source = band, band_source

    res.status = "resolved" if res.confidence >= CONFIDENCE_FLOOR else "flagged"
    return res
