"""Contract terms (stream A): the rate-conditions inventory and the code cannot drift; facts and terms append and
supersede like rates; an unverified quote is never stored; vendor names are resolved once. Offline, no model."""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from twm.pipeline.conditions import GROUP_NAMES, OTHER, RATE_CONDITIONS, condition_group, load_inventory, prompt_lines
from twm.pipeline.contracts import CommercialTerm, ContractFact, NamedResource, SOWExtraction
from twm.pipeline.ingest import register
from twm.pipeline.ledger import Ledger, vendor_name_key
from twm.pipeline.models import DocumentRecord, PartyCandidate, SourceRef

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "specs/rate-conditions.md"


# ---------------------------------------------------------------- the inventory and the code are one list
def test_inventory_and_code_hold_the_same_48_conditions_in_six_groups():
    """The rate-conditions inventory (specs/rate-conditions.md) and the code's list are identical: 48 keys, six groups, same meanings."""
    inv = load_inventory(INVENTORY)
    assert inv["groups"] == GROUP_NAMES
    assert list(inv["conditions"]) == list(RATE_CONDITIONS), "same keys in the same order"
    for key, (group, meaning, example, use) in inv["conditions"].items():
        assert RATE_CONDITIONS[key] == (group, meaning), f"{key}: group or meaning differs between the spec and the code"
    assert inv["total"] == len(RATE_CONDITIONS) == 48
    per_group = {}
    for key, (g, _) in RATE_CONDITIONS.items():
        per_group[g] = per_group.get(g, 0) + 1
    assert inv["summary"] == per_group, "the group table's counts must match the rows"
    assert OTHER not in RATE_CONDITIONS and condition_group(OTHER) is None
    assert len(prompt_lines()) == 49 and prompt_lines()[-1].startswith("other:")


# ---------------------------------------------------------------- the records
def _ref(page=6, quote="travel and lodging ... are included in the Charges"):
    return SourceRef(document_id="d", page=page, bbox=(1, 2, 3, 4), quote=quote)


def test_sow_extraction_carries_facts_and_typed_conditions():
    """A term-extraction answer carries identity facts and typed rate conditions, each with a page and quote; an unknown key is rejected."""
    sow = SOWExtraction(document_meta={"parties": ["DIR", "Accenture LLP"], "source_ref": _ref(1)},
                        facts=[ContractFact(fact_type="contract_number", value="DIR-STS-TSS-699", source_ref=_ref(1), confidence=0.98)],
                        commercial_terms=[CommercialTerm(term_type="expense_policy", verbatim_short="travel and lodging ... are included in the Charges",
                                                         source_ref=_ref(), confidence=0.95, condition_key="expenses_included")],
                        named_resources=[NamedResource(name_or_role="Jane Doe", observed_title="Account Executive", source_ref=_ref(2), confidence=0.9)])
    assert sow.facts[0].fact_type == "contract_number" and sow.commercial_terms[0].condition_key == "expenses_included"
    assert sow.named_resources[0].confidence == 0.9
    schema = SOWExtraction.model_json_schema()
    assert "ContractFact" in schema["$defs"] and "expenses_included" in str(schema), "the prompt carries the schema; keys must be in it"
    with pytest.raises(ValidationError):
        CommercialTerm(term_type="other", verbatim_short="x", source_ref=_ref(), condition_key="free_lunch")
    with pytest.raises(ValidationError):
        ContractFact(fact_type="colour", value="blue", source_ref=_ref())


def test_document_record_accepts_party_candidates(tmp_path):
    """A document record can carry the party names printed on its first pages, each with the phrase it was read from."""
    p = tmp_path / "a.txt"; p.write_text("MASTER SERVICES AGREEMENT between Big Bank and Acme Consulting Inc.", encoding="utf-8")
    rec = register(p)
    assert rec.party_candidates == []
    rec2 = DocumentRecord(**{**rec.model_dump(), "party_candidates": [PartyCandidate(name="Acme Consulting Inc.", evidence="between Big Bank and Acme Consulting Inc.", page=1)]})
    assert rec2.party_candidates[0].name == "Acme Consulting Inc." and rec2.party_candidates[0].role_hint is None


# ---------------------------------------------------------------- the ledger
def _doc(tmp_path):
    p = tmp_path / "msa.txt"; p.write_text("MASTER SERVICES AGREEMENT", encoding="utf-8")
    return register(p)


def test_terms_append_supersede_and_an_unverified_quote_is_never_stored(tmp_path):
    """Contract terms append and supersede like rates; a low-confidence term is flagged, and a quote not verified on its page is never stored."""
    rec = _doc(tmp_path)
    led = Ledger(tmp_path / "l.sqlite"); led.upsert_document(rec); led.start_run("run1", "local", "fake", "0.1")
    led.add_term("run1", rec, kind="fact", term_type="contract_number", value="DIR-STS-TSS-699", source_ref=_ref(1, "DIR Contract No. DIR-STS-TSS-699"),
                 confidence=0.98, verified=True, vendor="Accenture LLP", client="Texas DIR")
    t = led.add_term("run1", rec, kind="term", term_type="expense_policy", value="travel and lodging ... are included in the Charges", source_ref=_ref(),
                     confidence=0.95, verified=True, vendor="Accenture LLP", client="Texas DIR", condition_key="expenses_included")
    led.add_term("run1", rec, kind="term", term_type="escalation", value="rates subject to annual review", source_ref=_ref(12),
                 confidence=0.6, verified=True, vendor="Accenture LLP", client="Texas DIR", condition_key="escalation_open")
    with pytest.raises(ValueError):
        led.add_term("run1", rec, kind="term", term_type="discount", value="5% off everything", source_ref=_ref(3), confidence=0.99, verified=False,
                     vendor="Accenture LLP", client="Texas DIR", condition_key="volume_tier")
    led.add_named_resource("run1", rec, NamedResource(name_or_role="Jane Doe", observed_title="Delivery Lead", source_ref=_ref(2), confidence=0.92),
                           verified=True, vendor="Accenture LLP", client="Texas DIR")
    c = led.term_counts()
    assert c["facts_live"] == 1 and c["terms_live"] == 2 and c["terms_flagged"] == 1 and c["named_resources_live"] == 1
    row = [r for r in led.live_terms(rec.document_id) if r["term_id"] == t][0]
    assert row["condition_group"] == "A" and row["status"] == "recorded" and row["source_page"] == 6 and json.loads(row["source_bbox"]) == [1, 2, 3, 4]
    assert row["source_quote"].startswith("travel and lodging")
    flagged = [r for r in led.live_terms(rec.document_id, kind="term") if r["status"] == "flagged"][0]
    assert flagged["condition_key"] == "escalation_open" and flagged["condition_group"] == "C"
    # a re-run supersedes, never overwrites
    led.start_run("run2", "local", "fake", "0.1")
    assert led.supersede_terms(rec.document_id, "run2") == 4
    led.add_term("run2", rec, kind="fact", term_type="contract_number", value="DIR-STS-TSS-699", source_ref=_ref(1), confidence=0.98, verified=True,
                 vendor="Accenture LLP", client="Texas DIR")
    c = led.term_counts()
    assert c["facts_live"] == 1 and c["terms_live"] == 0 and c["terms_superseded"] == 3 and c["named_resources_live"] == 0
    led.close()


def test_vendor_names_resolve_once(tmp_path):
    """A printed vendor name is decided once and looked up ever after; case, spacing and punctuation do not matter; a changed mind keeps the old row."""
    led = Ledger(tmp_path / "l.sqlite")
    assert led.lookup_vendor("Accenture LLP") is None
    led.record_vendor_name("Accenture LLP", "Accenture", "Kyle McNamara", evidence="--vendor on the Texas run")
    led.record_vendor_name("ACCENTURE (UK) LTD", "Accenture", "Kyle McNamara", evidence="G-Cloud 15 page")
    assert led.lookup_vendor("accenture llp")["vendor"] == "Accenture"            # case and spacing do not matter
    assert led.lookup_vendor("Accenture (UK) Ltd.")["vendor"] == "Accenture"      # punctuation does not matter
    assert led.lookup_vendor("Accenture Inc.") is None                            # a different printed name is a new question
    assert vendor_name_key("Deloitte Consulting LLP") == "deloitte consulting llp"
    # a changed mind deprecates the old row and keeps it
    led.record_vendor_name("Accenture LLP", "Accenture plc", "analyst", evidence="corrected")
    assert led.lookup_vendor("Accenture LLP")["vendor"] == "Accenture plc"
    assert led.term_counts()["vendor_names"] == 2
    assert led.conn.execute("SELECT COUNT(*) FROM vendor_names").fetchone()[0] == 3
    led.close()
