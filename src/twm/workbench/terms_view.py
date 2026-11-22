"""How contract terms are shown in the workbench (work/workbench-terms/plan.md): the Terms tab of a contract set and the
"name this condition" question. Views over the ledger only: nothing here writes, calls a model or changes the inventory.

The floor is applied here, on read: a condition whose type the engine was unsure of (confidence below the floor) is shown as
"to review" until a person confirms it. Moving the floor re-sorts the list and rewrites no row.
"""
from __future__ import annotations

import re
from typing import Optional

from twm.pipeline.conditions import CLEARING_KEYS, GROUP_NAMES, OTHER, PROPOSED_PREFIX, RATE_CONDITIONS, RESTRICTING_KEYS
from twm.pipeline.ledger import TERM_CONFIDENCE_FLOOR

LABELS = {"mfc": "Most-favoured customer", "sla_credit": "SLA credit"}
FACT_ORDER = [("party", "Parties"), ("contract_number", "Contract number"), ("document_type", "Document type"), ("effective_date", "Effective date"),
              ("expiry", "Expiry"), ("term", "Term"), ("contract_value", "Contract value"), ("pricing_model", "Pricing model"),
              ("governing_msa_ref", "Governing agreement"), ("amendment_number", "Amendment number"), ("amends", "What an amendment changes")]

# One-line summary for a senior reader (a text draft, Kyle Nov 22, 2026): conditions that say something by being present.
STATEMENTS = {
    "expenses_included": "expenses inside the rate", "expenses_extra": "expenses billed on top", "expenses_refused": "client pays no expenses",
    "rate_ceiling": "rates are not-to-exceed", "rate_flat": "rates flat across years", "escalation_in_grid": "yearly increases printed in the grid",
    "escalation_fixed_pct": "a fixed yearly increase", "escalation_index": "increases tied to an index", "escalation_open": "rates open to annual review",
    "blended_rate": "a blended team rate", "volume_tier": "volume discount", "period_discount": "a discount for a stated period",
    "prompt_pay_discount": "early-payment discount", "signing_credit": "a signing credit", "sla_credit": "service-level credits",
    "minimum_commitment": "a minimum commitment", "no_minimum": "no minimum commitment", "mfc": "most-favoured-customer pricing",
    "list_discount": "a percentage off a list", "audit_rights": "audit rights", "benchmark_clause": "a right to benchmark",
    "public_record": "public record", "disclosure_bar": "disclosure barred", "benchmark_data_use": "use of the data limited",
}

STOP = set("a an the of and or to in on at for by is are be as it its that this with from not no any all may shall will which who whether what how "
           "client vendor contract rate rates successful respondent dir state".split())
TYPE_HINTS = {"invoicing": ("invoice_detail", "payment_terms"), "credit": ("sla_credit", "signing_credit"),
              "discount": ("volume_tier", "period_discount", "prompt_pay_discount", "list_discount"), "expense_policy": ("expenses_extra", "expenses_included", "expenses_refused"),
              "escalation": ("escalation_fixed_pct", "escalation_index", "escalation_open"), "minimum_commitment": ("minimum_commitment", "no_minimum"),
              "mfc": ("mfc",), "volume_tier": ("volume_tier",)}


def label(key: Optional[str]) -> str:
    if not key or key == OTHER:
        return "Not yet named"
    if key.startswith(PROPOSED_PREFIX):
        return key[len(PROPOSED_PREFIX):].replace("_", " ").capitalize() + " (proposed)"
    return LABELS.get(key) or key.replace("_", " ").capitalize()


def inventory() -> dict:
    groups = [dict(letter=g, name=name, conditions=[dict(key=k, label=label(k), meaning=m) for k, (kg, m) in RATE_CONDITIONS.items() if kg == g])
              for g, name in GROUP_NAMES.items()]
    return dict(groups=groups, total=len(RATE_CONDITIONS), floor=TERM_CONFIDENCE_FLOOR)


def _words(text: str) -> set[str]:
    out = set()
    for w in re.findall(r"[a-z]+", (text or "").lower()):
        if len(w) > 2 and w not in STOP:
            out.add(w[:-1] if w.endswith("s") and len(w) > 4 else w)
    return out


def closest_conditions(term_type: Optional[str], text: str, limit: int = 3) -> list[dict]:
    """The inventory rows whose wording is nearest the clause, by shared words (no model). The engine already said none
    fits, so these are offered as the closest, not as a suggestion to accept."""
    have = _words(text)
    scored = []
    for key, (g, meaning) in RATE_CONDITIONS.items():
        score = len(have & (_words(meaning) | _words(key.replace("_", " ")))) + (1.5 if key in TYPE_HINTS.get(term_type or "", ()) else 0)
        if score >= 2:
            scored.append((score, key, g, meaning))
    scored.sort(key=lambda s: -s[0])
    return [dict(key=k, label=label(k), meaning=m, group=g) for _, k, g, m in scored[:limit]]


def shown_status(t: dict, floor: float) -> str:
    """recorded | to_review | unnamed | set_aside, as the screen shows it at this floor."""
    if t["status"] == "dismissed":
        return "set_aside"
    if t["kind"] != "fact" and t["condition_key"] == OTHER:
        return "unnamed"
    if t.get("key_source") == "analyst":
        return "recorded"
    return "recorded" if (t["extraction_confidence"] or 0) >= floor else "to_review"


def term_view(t: dict, floor: float = TERM_CONFIDENCE_FLOOR) -> dict:
    key = t["condition_key"]
    return dict(term_id=t["term_id"], kind=t["kind"], term_type=t["term_type"], condition_key=key, group=t["condition_group"],
                label=label(key) if t["kind"] != "fact" else None, meaning=RATE_CONDITIONS[key][1] if key in RATE_CONDITIONS else None,
                value=t["value"], note=t["note"], confidence=t["extraction_confidence"], shown=shown_status(t, floor),
                by_analyst=t.get("key_source") == "analyst", page=t["source_page"], document_id=t["document_id"], filename=t.get("filename"),
                doc_class=t.get("doc_class"), gate="restricts" if key in RESTRICTING_KEYS else ("clears" if key in CLEARING_KEYS else None))


def summary_line(conditions: list[dict]) -> str:
    """A draft one-line reading of a contract set for a senior reader, built only from recorded conditions."""
    keys = [c["condition_key"] for c in conditions if c["shown"] == "recorded"]
    said = [STATEMENTS[k] for k in RATE_CONDITIONS if k in keys and k in STATEMENTS]
    also = [label(k).lower() for k in RATE_CONDITIONS if k in keys and k not in STATEMENTS]
    if not said and not also:
        return ""
    line = "; ".join(said)
    if also:
        line += ("; " if line else "") + "also covers " + ", ".join(also)
    return line[0].upper() + line[1:] + "."


def set_terms_view(terms: list[dict], resources: list[dict], disclosure: dict, floor: float = TERM_CONFIDENCE_FLOOR) -> dict:
    views = [term_view(t, floor) for t in terms]
    facts_by_type: dict[str, list[dict]] = {}
    for v in views:
        if v["kind"] == "fact":
            same = next((f for f in facts_by_type.setdefault(v["term_type"], []) if f["value"].strip().lower() == v["value"].strip().lower()), None)
            if same:
                same["times"] += 1
            else:
                facts_by_type[v["term_type"]].append(dict(v, times=1))
    order = FACT_ORDER + [(k, k.replace("_", " ").capitalize()) for k in facts_by_type if k not in dict(FACT_ORDER)]
    facts = [dict(type=k, label=lab, values=facts_by_type[k]) for k, lab in order if k in facts_by_type]
    conds = [v for v in views if v["kind"] != "fact"]
    groups = []
    for g, name in GROUP_NAMES.items():
        rows = [c for c in conds if c["group"] == g and c["shown"] in ("recorded", "to_review")]
        rows.sort(key=lambda c: (list(RATE_CONDITIONS).index(c["condition_key"]) if c["condition_key"] in RATE_CONDITIONS else 999, c["filename"] or "", c["page"] or 0))
        groups.append(dict(letter=g, name=name, conditions=rows))
    counts = dict(facts=sum(1 for v in views if v["kind"] == "fact"), conditions=len(conds),
                  recorded=sum(1 for c in conds if c["shown"] == "recorded"), to_review=sum(1 for c in conds if c["shown"] == "to_review"),
                  unnamed=sum(1 for c in conds if c["shown"] == "unnamed"), set_aside=sum(1 for c in conds if c["shown"] == "set_aside"),
                  named_people=len(resources))
    for k in ("restricting", "clearing", "other"):
        disclosure[k] = [term_view(t, floor) for t in disclosure[k]]
    return dict(floor=floor, default_floor=TERM_CONFIDENCE_FLOOR, counts=counts, disclosure=disclosure, summary=summary_line(conds), facts=facts, groups=groups,
                unnamed=[c for c in conds if c["shown"] == "unnamed"], set_aside=[c for c in conds if c["shown"] == "set_aside"],
                people=[dict(name=r["name_or_role"], title=r["observed_title"], page=r["source_page"], filename=r["filename"], document_id=r["document_id"]) for r in resources])
