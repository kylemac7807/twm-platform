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


# ---------------------------------------------------------------- term reading (step 2): page selection and verification on the page
from twm import llm
from twm.llm import FakeModel
from twm.pipeline.extract import extract_sow, page_signals, quote_on_page, rate_table_pages, sections_for_terms, select_term_pages
from twm.pipeline.read import LocalPdfReader

EXHIBIT2 = ROOT / "corpus/manifests/v3_downloads/v3_gov/084_Texas_DIR_Accenture_LLP_rate_exhibit.pdf"
PRICING = ROOT / "corpus/manifests/v3_downloads/v3_gov/085_Texas_DIR_Accenture_LLP_rate_exhibit.pdf"
MICHIGAN = ROOT / "corpus/twm_corpus/MI_DTMB_Deloitte_MiIntegrate_Contract_SOW_Rates_2013-2026_ORIGINAL.pdf"
needs_texas = pytest.mark.skipif(not (EXHIBIT2.exists() and PRICING.exists()), reason="Texas exhibits not on disk")


@pytest.fixture(scope="module")
def exhibit2():
    rec = register(EXHIBIT2)
    return rec, LocalPdfReader().read(rec)


def _sow_answer(facts=(), terms=(), resources=(), rows=(), abstained=()):
    return json.dumps({"document_meta": {"parties": [], "source_ref": {"page": 1}}, "facts": list(facts), "commercial_terms": list(terms),
                       "named_resources": list(resources), "rate_table": list(rows), "abstained": list(abstained)})


@needs_texas
def test_term_pages_are_chosen_by_signals_and_the_pricing_grid_page_is_left_to_the_rate_card_path(exhibit2):
    """Pages go to term reading on commercial-term signals (a most-favoured-customer clause alone is enough; a running header is never enough), and a page holding a rate table is left to the rate-card path."""
    rec, rd = exhibit2
    pages, unread = select_term_pages(rd)
    assert {5, 6, 10, 12, 13, 14, 22, 23} <= set(pages), "the financial pages of Exhibit 2"
    assert not ({3, 4, 25} & set(pages)), "the table of contents and the last page carry only the running header"
    assert unread == 0 and len(sections_for_terms(rd, pages)) <= 5
    assert "mfc" in page_signals(rd.page_text(10)) and "contract_no" in page_signals(rd.page_text(25))
    grid_rec = register(PRICING); grid = LocalPdfReader().read(grid_rec)
    table_pages = rate_table_pages(grid)
    assert 8 in table_pages
    pages, _ = select_term_pages(grid, exclude=table_pages)
    assert 11 in pages and 8 not in pages, "the volume-discount page is read for terms; the grid page is not"


@needs_texas
def test_an_invented_quote_is_rejected_and_a_real_one_carries_its_box(exhibit2):
    """A term whose quote is not on its page is rejected and never stored; a real quote keeps the box of the lines that hold it; a quote claimed on the wrong page of the section is corrected and noted; a fact whose value is not printed is rejected."""
    rec, rd = exhibit2
    real = ("expenses that Successful Respondent incurs in performing the Services (including management, travel and lodging, document "
            "reproduction and shipping, equipment, software required by Successful Respondent personnel, and long-distance telephone) are included in the Charges")
    no_minimum = "The Successful Respondent shall not impose any fixed or monthly required minimum fees or support level pricing for any Service or at the total contract level"
    answer = _sow_answer(
        facts=[{"fact_type": "contract_number", "value": "DIR-STS-TSS-699", "confidence": 0.98, "source_ref": {"page": 5, "quote": "DIR Contract No. DIR-STS-TSS-699"}},
               {"fact_type": "effective_date", "value": "January 1, 2030", "confidence": 0.9, "source_ref": {"page": 5, "quote": "DIR Contract No. DIR-STS-TSS-699"}}],
        terms=[{"term_type": "expense_policy", "condition_key": "expenses_included", "verbatim_short": real, "confidence": 0.95, "source_ref": {"page": 6, "quote": real}},
               {"term_type": "discount", "condition_key": "volume_tier", "verbatim_short": "all rates are discounted by five percent", "confidence": 0.9, "source_ref": {"page": 6}},
               {"term_type": "minimum_commitment", "condition_key": "no_minimum", "verbatim_short": no_minimum, "confidence": 0.93, "source_ref": {"page": 6, "quote": no_minimum}}],
        resources=[{"name_or_role": "Jane Nobody", "observed_title": "Delivery Lead", "confidence": 0.8, "source_ref": {"page": 5}}],
        abstained=["the extension rate on page 12 was outside this section"])
    llm.LOG.clear()
    model = FakeModel([answer])
    out = extract_sow(rec, rd, model, pages=[5, 6])
    assert out.sections == 1 and out.pages_selected == [5, 6]
    system, user = model.calls[0]
    assert "expenses_included: Travel, lodging and incidentals are inside the rate" in system, "the prompt carries the inventory"
    assert "PAGE 5:" in user and "PAGE 6:" in user and '"ContractFact"' in user, "page-tagged text and the schema go to the model"
    assert [f.fact_type for f in out.facts] == ["contract_number"] and out.facts[0].source_ref.page == 5 and out.facts[0].source_ref.bbox is not None
    kept = {t.condition_key: t for t in out.terms}
    assert set(kept) == {"expenses_included", "no_minimum"}
    inc = kept["expenses_included"]
    assert inc.source_ref.page == 6 and inc.source_ref.bbox is not None and inc.source_ref.bbox[3] - inc.source_ref.bbox[1] > 20, "a quote over several lines is boxed over those lines"
    assert kept["no_minimum"].source_ref.page == 5 and any("claimed on page 6 found on page 5" in c for c in out.corrections)
    reasons = {(k, d.get("condition_key") or d.get("fact_type") or d.get("name_or_role")): why for k, d, why in out.rejected_items}
    assert "not found" in reasons[("term", "volume_tier")]
    assert "not printed" in reasons[("fact", "effective_date")]
    assert "not found" in reasons[("named_resource", "Jane Nobody")]
    assert out.abstained == ["the extension rate on page 12 was outside this section"]
    assert out.sow is not None and len(out.sow.commercial_terms) == 2 and any("rejected" in f for f in out.flags)
    assert llm.LOG[-1].validated


@needs_texas
def test_quote_matching_ignores_punctuation_case_and_line_breaks_but_not_words(exhibit2):
    """Quote verification matches the words in order: punctuation, case and line breaks do not matter, a changed word does."""
    rec, rd = exhibit2
    ok, bbox, _ = quote_on_page(rd, 5, "all charges are expressed and shall be paid in us dollars")
    assert ok and bbox is not None
    ok, _, why = quote_on_page(rd, 5, "All Charges are expressed and shall be paid in Canadian Dollars")
    assert not ok and "not found" in why
    ok, _, _ = quote_on_page(rd, 6, "incidental expenses")
    assert ok


@pytest.mark.skipif(not MICHIGAN.exists(), reason="Michigan Deloitte contract not on disk")
def test_michigan_cover_page_facts_and_payment_terms_verify_on_page_one():
    """The Michigan change-notice cover page yields the contract number, the vendor, the contract value, the change-notice number and NET 45, each verified on page 1."""
    rec = register(MICHIGAN)
    rd = LocalPdfReader(max_pages=2).read(rec)
    answer = _sow_answer(
        facts=[{"fact_type": "contract_number", "value": "MA180000000078", "confidence": 0.99, "source_ref": {"page": 1, "quote": "Contract Number MA180000000078"}},
               {"fact_type": "party", "value": "DELOITTE CONSULTING LLP", "confidence": 0.97, "source_ref": {"page": 1, "quote": "DELOITTE CONSULTING LLP"}},
               {"fact_type": "contract_value", "value": "$109,228,476.69", "confidence": 0.95, "source_ref": {"page": 1, "quote": "ESTIMATED AGGREGATE CONTRACT VALUE"}},
               {"fact_type": "amendment_number", "value": "30", "confidence": 0.95, "source_ref": {"page": 1, "quote": "Change Notice Number 30"}},
               {"fact_type": "document_type", "value": "amendment", "confidence": 0.95, "source_ref": {"page": 1, "quote": "CONTRACT CHANGE NOTICE"}}],
        terms=[{"term_type": "invoicing", "condition_key": "payment_terms", "verbatim_short": "NET 45", "confidence": 0.9, "source_ref": {"page": 1, "quote": "NET 45"}}])
    out = extract_sow(rec, rd, FakeModel([answer]), pages=[1])
    assert [f.fact_type for f in out.facts] == ["contract_number", "party", "contract_value", "amendment_number", "document_type"]
    assert out.terms[0].condition_key == "payment_terms" and out.terms[0].source_ref.page == 1
    assert out.rejected_items == [] and rec.contract_numbers == ["MA180000000078"]
