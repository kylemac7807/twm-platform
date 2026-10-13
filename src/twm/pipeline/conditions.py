"""Rate conditions: the controlled vocabulary for the fine print that changes what a rate really costs
(specs/rate-conditions.md, started Oct 13, 2026 at Kyle's request; six groups and 48 conditions confirmed by him).

The spec file is the human-readable inventory; this module is the copy the code uses (the extraction prompt types
every commercial term with one of these keys, or "other" in the model's words). A test keeps the two identical:
keys, groups, one-line meanings and the count. Keys are appended or deprecated, never silently renamed.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Literal, Optional

GROUP_NAMES: dict[str, str] = {
    "A": "Expenses and pass-throughs",
    "B": "What an hour, a day or a month is",
    "C": "The structure of the rate itself",
    "D": "Discounts, credits and commitments",
    "E": "Scope, change and exit",
    "F": "Transparency and governance",
}

# key -> (group letter, one-line meaning), in the order of the inventory
RATE_CONDITIONS: dict[str, tuple[str, str]] = {
    # A. Expenses and pass-throughs
    "expenses_included": ("A", "Travel, lodging and incidentals are inside the rate"),
    "expenses_extra": ("A", "Expenses billed on top of the rate, at cost or capped"),
    "expenses_refused": ("A", "The client pays no expenses at all"),
    "travel_time": ("A", "Whether hours spent travelling are billable"),
    "passthrough_markup": ("A", "A handling fee on third-party costs passed through"),
    "tooling_fees": ("A", "Platform, licence or tool charges billed beside labour"),
    "onboarding_fees": ("A", "Background checks, equipment, badges, set-up charged separately"),
    # B. What an hour, a day or a month is
    "billing_increment": ("B", "The smallest unit billed (hour, quarter hour, half day)"),
    "day_definition": ("B", "How many hours a day rate buys"),
    "monthly_hours_max": ("B", "A ceiling on billable hours in a month"),
    "nonproductive_excluded": ("B", "Time that may not be billed: commuting, holidays, training, meetings"),
    "overtime": ("B", "Whether overtime is billable and at what multiple"),
    "holidays": ("B", "Whether statutory holidays are billed"),
    "capacity_formula": ("B", "A team-month price built from a formula rather than hours worked"),
    # C. The structure of the rate itself
    "rate_ceiling": ("C", "The printed rate is a not-to-exceed figure, not a price"),
    "escalation_in_grid": ("C", "Each contract year's rate is printed; the increase is visible"),
    "escalation_fixed_pct": ("C", "One rate plus a stated yearly percentage"),
    "escalation_index": ("C", "The increase tied to an index"),
    "escalation_open": ("C", 'Rates "subject to annual review", no figure'),
    "rate_flat": ("C", "Rates stated flat across several years"),
    "extension_rate": ("C", "What rate applies if the contract is extended"),
    "blended_rate": ("C", "One rate for a team regardless of who does the work"),
    "level_definition": ("C", 'Whether the document says what "Senior" means'),
    "service_type_split": ("C", "Different rates for the same title by service type"),
    "location_split": ("C", "Different rates by delivery location"),
    "billing_currency": ("C", "The currency billed and who carries exchange risk"),
    "taxes": ("C", "Whether taxes are inside or on top of the rate"),
    # D. Discounts, credits and commitments
    "volume_tier": ("D", "A discount that grows with spend"),
    "period_discount": ("D", "A discount for a stated period"),
    "prompt_pay_discount": ("D", "A discount for paying early"),
    "payment_terms": ("D", "When payment is due"),
    "signing_credit": ("D", "A one-off credit that lowers the headline price"),
    "sla_credit": ("D", "Credits for missed service levels"),
    "minimum_commitment": ("D", "Spend, hours or headcount the client must buy"),
    "no_minimum": ("D", "The contract says there is none"),
    "mfc": ("D", "Most-favoured-customer or no-less-favourable pricing"),
    "list_discount": ("D", "A rate quoted as a percentage off a published list"),
    # E. Scope, change and exit
    "change_pricing": ("E", "How new or changed work is priced"),
    "termination_fees": ("E", "Charges on early termination or wind-down"),
    "transition_charges": ("E", "Front-loaded set-up or transition fees"),
    "knowledge_transfer": ("E", "Whether hand-over time is billed"),
    "personnel_substitution": ("E", "Replacement of named people, and whether ramp-up is billed"),
    "productivity_commitment": ("E", "A promised year-on-year reduction"),
    # F. Transparency and governance
    "invoice_detail": ("F", "Whether invoices show people, hours and rates, or only milestones"),
    "audit_rights": ("F", "The client's right to audit rates and time"),
    "benchmark_clause": ("F", "The client's right to benchmark rates and the adjustment that follows"),
    "subcontractor_passthrough": ("F", "Subcontracted labour billed at the prime's rate"),
    "common_categories": ("F", "A client rule that every vendor uses the same rate-card categories"),
}

OTHER = "other"   # the model's escape hatch: a condition not in the inventory, described in its own words, queued for a person

ConditionKey = Literal[tuple(RATE_CONDITIONS) + (OTHER,)]  # type: ignore[valid-type]


def condition_group(key: Optional[str]) -> Optional[str]:
    """Group letter for a key ('A'..'F'); None for 'other' or unknown."""
    if key in RATE_CONDITIONS:
        return RATE_CONDITIONS[key][0]
    return None


def condition_meaning(key: Optional[str]) -> Optional[str]:
    if key in RATE_CONDITIONS:
        return RATE_CONDITIONS[key][1]
    return None


def prompt_lines() -> list[str]:
    """One line per condition for the extraction prompt: 'key: meaning (group name)'."""
    out = []
    for key, (g, meaning) in RATE_CONDITIONS.items():
        out.append(f"{key}: {meaning} ({GROUP_NAMES[g]})")
    out.append(f"{OTHER}: a condition not listed above; describe it in condition_note")
    return out


# ---------------------------------------------------------------- the inventory file, parsed (for the drift test and reports)
_GROUP_HEADING = re.compile(r"^### ([A-F])\. (.+?)\s*$")
_ROW = re.compile(r"^\| `([a-z_]+)` \| (.+?) \| (.+?) \| (.+?) \|\s*$")
_SUMMARY_ROW = re.compile(r"^\| ([A-F])\. (.+?) \| (.+?) \| (\d+) \|\s*$")
_TOTAL_ROW = re.compile(r"^\| \| \*\*Total\*\* \| \*\*(\d+)\*\* \|\s*$")


def load_inventory(path: Path | str = Path("specs/rate-conditions.md")) -> dict:
    """Read the spec: {'groups': {letter: name}, 'conditions': {key: (group, meaning, example, use)},
    'summary': {letter: count}, 'total': int}."""
    groups: dict[str, str] = {}
    conditions: dict[str, tuple[str, str, str, str]] = {}
    summary: dict[str, int] = {}
    total: Optional[int] = None
    current: Optional[str] = None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = _GROUP_HEADING.match(line)
        if m:
            current = m.group(1)
            groups[current] = m.group(2)
            continue
        m = _SUMMARY_ROW.match(line)
        if m and current is None:
            summary[m.group(1)] = int(m.group(4))
            continue
        m = _TOTAL_ROW.match(line)
        if m:
            total = int(m.group(1))
            continue
        m = _ROW.match(line)
        if m and current:
            conditions[m.group(1)] = (current, m.group(2), m.group(3), m.group(4))
    return {"groups": groups, "conditions": conditions, "summary": summary, "total": total}
