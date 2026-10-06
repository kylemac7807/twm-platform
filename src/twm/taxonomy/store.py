"""Load and index the Role Framework CSVs under taxonomy/.

TaxonomyStore is read-only in-memory state: families, roles, band crosswalk,
tech vocabulary, and the seeded title mappings, plus the lookup indexes the
normalizer needs. Referential integrity is checked on load so a bad CSV edit
fails fast instead of silently corrupting the ledger.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from .models import BandCrosswalkRow, CanonicalRole, RoleFamily, TechTag, TitleMapping

FILES = {
    "families": "role_families.csv",
    "roles": "canonical_roles.csv",
    "bands": "band_crosswalk.csv",
    "tech": "tech_vocab.csv",
    "mappings": "title_mappings.csv",
}

_PUNCT = re.compile(r"[^a-z0-9]+")


def title_key(s: str) -> str:
    """Canonical comparison key for a title string: lowercase, '&'->'and', punctuation->space."""
    s = s.lower().replace("&", " and ").replace("/", " / ")
    # language names whose punctuation is the whole point: keep them distinct before stripping
    s = s.replace("c#", "csharp").replace("c++", "cplusplus").replace(".net", "dotnet").replace("f#", "fsharp")
    s = _PUNCT.sub(" ", s)
    return " ".join(s.split())


def default_taxonomy_dir() -> Path:
    """taxonomy/ at the repo root (two levels above src/twm)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "taxonomy"
        if (cand / FILES["roles"]).exists():
            return cand
    raise FileNotFoundError("taxonomy/ directory with canonical_roles.csv not found above " + str(here))


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@dataclass
class TaxonomyStore:
    families: list[RoleFamily]
    roles: list[CanonicalRole]
    bands: list[BandCrosswalkRow]
    tech: list[TechTag]
    mappings: list[TitleMapping]
    source_dir: Optional[Path] = None

    # indexes (built in __post_init__)
    family_by_id: dict[str, RoleFamily] = field(default_factory=dict, init=False)
    role_by_id: dict[str, CanonicalRole] = field(default_factory=dict, init=False)
    role_by_name_key: dict[str, str] = field(default_factory=dict, init=False)
    band_index: dict[tuple[str, str], BandCrosswalkRow] = field(default_factory=dict, init=False)
    tech_by_tag: dict[str, TechTag] = field(default_factory=dict, init=False)
    tech_alias_index: dict[str, str] = field(default_factory=dict, init=False)  # alias key -> tag
    mapping_index: dict[str, list[TitleMapping]] = field(default_factory=dict, init=False)  # title key -> active rows

    def __post_init__(self) -> None:
        self.family_by_id = {f.family_id: f for f in self.families}
        self.role_by_id = {r.role_id: r for r in self.roles}
        self.role_by_name_key = {title_key(r.name): r.role_id for r in self.roles}
        self.band_index = {(b.source_scheme.lower(), b.source_level.lower()): b for b in self.bands}
        self.tech_by_tag = {t.tag: t for t in self.tech}
        self.tech_alias_index = {}
        for t in self.tech:
            for a in [t.tag, t.label, *t.aliases]:
                self.tech_alias_index[title_key(a)] = t.tag
        idx: dict[str, list[TitleMapping]] = defaultdict(list)
        for m in self.mappings:
            if m.status != "deprecated":
                idx[title_key(m.observed_title)].append(m)
        self.mapping_index = dict(idx)
        self._check_integrity()

    # ------------------------------------------------------------------ load
    @classmethod
    def load(cls, taxonomy_dir: Optional[Path | str] = None) -> "TaxonomyStore":
        d = Path(taxonomy_dir) if taxonomy_dir else default_taxonomy_dir()
        return cls(
            families=[RoleFamily(**r) for r in _read(d / FILES["families"])],
            roles=[CanonicalRole(**r) for r in _read(d / FILES["roles"])],
            bands=[BandCrosswalkRow(**r) for r in _read(d / FILES["bands"])],
            tech=[TechTag(**r) for r in _read(d / FILES["tech"])],
            mappings=[TitleMapping(**r) for r in _read(d / FILES["mappings"])],
            source_dir=d,
        )

    def _check_integrity(self) -> None:
        problems: list[str] = []
        seen: set[str] = set()
        for r in self.roles:
            if r.role_id in seen:
                problems.append(f"duplicate role_id {r.role_id}")
            seen.add(r.role_id)
            if r.family_id not in self.family_by_id:
                problems.append(f"role {r.role_id} references unknown family {r.family_id}")
        for m in self.mappings:
            if m.status == "deprecated":
                continue  # history may point at a retired role (engagement_manager, retired Oct 6, 2026); only live rows must resolve
            if m.canonical_role_id and m.canonical_role_id not in self.role_by_id:
                problems.append(f"mapping '{m.observed_title}' ({m.source}) -> unknown role {m.canonical_role_id}")
            if m.attr_technology and m.attr_technology not in self.tech_by_tag:
                problems.append(f"mapping '{m.observed_title}' uses unknown tech tag {m.attr_technology}")
            if m.status == "active" and not m.canonical_role_id:
                problems.append(f"active mapping '{m.observed_title}' ({m.source}) has no canonical_role_id")
        if problems:
            raise ValueError("taxonomy integrity errors:\n  " + "\n  ".join(problems))

    # ---------------------------------------------------------------- lookups
    def band_for(self, scheme: str, level: str) -> Optional[BandCrosswalkRow]:
        """Look up a band by (scheme, level); level match is case-insensitive."""
        if scheme is None or level is None:
            return None
        return self.band_index.get((scheme.lower(), level.strip().lower()))

    def schemes(self) -> list[str]:
        return sorted({b.source_scheme for b in self.bands})

    def active_mappings(self) -> Iterable[TitleMapping]:
        return (m for m in self.mappings if m.status == "active")

    def roles_in_family(self, family_id: str) -> list[CanonicalRole]:
        return [r for r in self.roles if r.family_id == family_id]
