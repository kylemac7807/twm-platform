"""The durable title mapping table (resolve-once store).

Architecture decision 3: a distinct title is resolved ONCE and written here with
reasoning, confidence, source, and reviewer; every later occurrence is a lookup.
Rows are appended or deprecated, never edited in place (versioned like software).

v0 backs the table with taxonomy/title_mappings.csv. A client deployment will
back it with a database in the client tenant (local tier); the interface stays.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Optional

from twm.taxonomy.models import TitleMapping
from twm.taxonomy.store import FILES, TaxonomyStore, title_key

COLUMNS = [
    "observed_title", "source", "source_url", "canonical_role_id", "twm_band", "attr_technology",
    "attr_location", "attr_level_code_raw", "attr_years_raw", "confidence", "method", "reviewer",
    "status", "version_added",
]


def write_mappings(rows: Iterable[TitleMapping], path: Path) -> int:
    """Write mapping rows to CSV in the canonical column order. Returns row count."""
    n = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for m in rows:
            d = m.model_dump()
            d["confidence"] = f"{m.confidence:.2f}"
            for k, v in d.items():
                if v is None:
                    d[k] = ""
            w.writerow({k: d.get(k, "") for k in COLUMNS})
            n += 1
    return n


class MappingTable:
    """Append/deprecate view over the mapping rows held by a TaxonomyStore."""

    def __init__(self, store: TaxonomyStore):
        self.store = store

    def lookup(self, observed_title: str) -> list[TitleMapping]:
        return [m for m in self.store.mapping_index.get(title_key(observed_title), []) if m.status == "active"]

    def has(self, observed_title: str) -> bool:
        return bool(self.lookup(observed_title))

    def append(self, row: TitleMapping) -> None:
        """Add a resolved title. Refuses silent overwrite: deprecate the old row first."""
        if row.canonical_role_id and row.canonical_role_id not in self.store.role_by_id:
            raise ValueError(f"unknown role id {row.canonical_role_id}")
        existing = self.lookup(row.observed_title)
        if any(m.source == row.source for m in existing):
            raise ValueError(
                f"active mapping already exists for '{row.observed_title}' from source '{row.source}'; deprecate it first"
            )
        self.store.mappings.append(row)
        self.store.mapping_index.setdefault(title_key(row.observed_title), []).append(row)

    def deprecate(self, observed_title: str, source: Optional[str] = None, reviewer: str = "") -> int:
        n = 0
        for m in self.lookup(observed_title):
            if source is None or m.source == source:
                m.status = "deprecated"
                if reviewer:
                    m.reviewer = reviewer
                n += 1
        return n

    def save(self, path: Optional[Path] = None) -> int:
        p = path or (self.store.source_dir / FILES["mappings"])
        return write_mappings(self.store.mappings, p)
