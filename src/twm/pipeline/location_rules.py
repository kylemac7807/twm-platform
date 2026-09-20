"""Analyst-decided location rules: the resolve-once table for onshore / nearshore / offshore.

Kyle, Sept 19, 2026: whether a place is onshore, nearshore or offshore for a given client is a
judgment about cost and context, not geography. New York for a Canadian bank is an expensive
onshore-equivalent market; Buffalo might be nearshore; a city in the client's own country is not
always onshore. So the platform never decides from a place name. It flags the observation, an
analyst categorizes it once with a reason, and from then on the decision is a deterministic lookup.

v0 keeps the decisions in taxonomy/location_rules.csv. In a client deployment this table lives in
the client's tenant (local tier); it describes that client's commercial geography and never leaves.
"""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel

from twm.pipeline.normalize import location_rule_key
from twm.taxonomy.store import default_taxonomy_dir

FILE = "location_rules.csv"
COLUMNS = ["client_key", "place", "classification", "decided_by", "decided_on", "reason", "status"]


class LocationRule(BaseModel):
    client_key: str                 # whose rule this is, e.g. "CA" for all Canadian clients or "bank-a"
    place: str                      # the place as it appears in titles, e.g. "New York"
    classification: Literal["onshore", "nearshore", "offshore"]
    decided_by: str                 # the analyst
    decided_on: str = ""            # ISO date
    reason: str = ""                # why: the audit trail a client can read
    status: Literal["active", "deprecated"] = "active"


def load_location_rules(path: Optional[Path | str] = None) -> list[LocationRule]:
    p = Path(path) if path else default_taxonomy_dir() / FILE
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as f:
        return [LocationRule(**r) for r in csv.DictReader(f)]


def as_lookup(rules: list[LocationRule]) -> dict[tuple[str, str], str]:
    """The dict resolve() takes: (client_key, place) -> classification, active rules only."""
    return {location_rule_key(r.client_key, r.place): r.classification for r in rules if r.status == "active"}


def record_decision(rules: list[LocationRule], client_key: str, place: str, classification: str,
                    decided_by: str, reason: str) -> LocationRule:
    """Append an analyst's decision. An existing active rule for the same client and place is
    deprecated, never edited, so the history of who decided what survives."""
    key = location_rule_key(client_key, place)
    for r in rules:
        if r.status == "active" and location_rule_key(r.client_key, r.place) == key:
            r.status = "deprecated"
    rule = LocationRule(client_key=client_key, place=place, classification=classification,
                        decided_by=decided_by, decided_on=date.today().isoformat(), reason=reason)
    rules.append(rule)
    return rule


def save_location_rules(rules: list[LocationRule], path: Optional[Path | str] = None) -> int:
    p = Path(path) if path else default_taxonomy_dir() / FILE
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rules:
            w.writerow(r.model_dump())
    return len(rules)
