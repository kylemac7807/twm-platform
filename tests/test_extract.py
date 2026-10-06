"""Extraction (M2 step 4): sectioning, abstention, and page verification that rejects an invented number. Offline via FakeModel."""
import json
from pathlib import Path

import pytest

from twm import llm
from twm.llm import FakeModel
from twm.pipeline.extract import extract_rate_card, sections_for_rate_card, value_on_page
from twm.pipeline.ingest import register
from twm.pipeline.read import LocalPdfReader

ROOT = Path(__file__).resolve().parents[1]
PRICING = ROOT / "corpus/manifests/v3_downloads/v3_gov/085_Texas_DIR_Accenture_LLP_rate_exhibit.pdf"
pytestmark = pytest.mark.skipif(not PRICING.exists(), reason="pricing exhibit not on disk")


@pytest.fixture(scope="module")
def reading():
    rec = register(PRICING)
    return rec, LocalPdfReader().read(rec)


def _answer(rows):
    return json.dumps({"document_meta": {"issuer": "Texas DIR", "counterparty": "Accenture LLP", "currency": "USD", "rate_unit": "hour",
                                         "contract_number": "DIR-STS-TSS-699", "source_ref": {"document_id": "x", "page": 8}},
                       "rows": rows, "abstained": []})


def _row(title, stated, value, page=8, conf=0.95, **extra):
    r = {"observed_title": title, "rate_as_stated": stated, "rate_value": value, "currency": "USD", "rate_unit": "hour",
         "period_raw": "Year 1 (FY27)", "confidence": conf, "source_ref": {"document_id": "x", "page": page}}
    r.update(extra)
    return r


def test_sectioning_finds_the_rate_table(reading):
    rec, rd = reading
    secs = sections_for_rate_card(rd)
    assert any(s.table is not None and s.table.n_rows > 50 and s.page_start == 8 for s in secs)


def test_verified_rows_keep_their_position_and_invented_numbers_are_rejected(reading):
    rec, rd = reading
    secs = sections_for_rate_card(rd)
    answers = []
    for s in secs:
        if s.page_start == 8 and s.table.n_rows > 50:
            answers.append(_answer([
                _row("API Architect Developer", "$122.00", "122.00"),          # real: on page 8
                _row("Business Consultant", "$158.50", "158.50"),              # real
                _row("Business Consultant", "$999.99", "999.99"),              # invented: must be rejected
                _row("Imaginary Role", "$122.00", "122.00"),                   # number real, title not on page: rejected
                _row("Data Scientist", None, None, conf=0.3),                  # abstained: rejected, not guessed
            ]))
        else:
            answers.append(_answer([]))
    model = FakeModel(answers)
    llm.LOG.clear()
    out = extract_rate_card(rec, rd, model)
    kept = {(r.observed_title, str(r.rate_value)) for r in out.rows}
    assert ("API Architect Developer", "122.00") in kept and ("Business Consultant", "158.50") in kept
    reasons = {r.observed_title: why for r, why in out.rejected}
    assert "value not found" in reasons["Business Consultant"] or any("999" in str(r.rate_value) and "not found" in w for r, w in out.rejected)
    assert "title not found" in reasons["Imaginary Role"]
    assert "abstained" in reasons["Data Scientist"]
    api = next(r for r in out.rows if r.observed_title == "API Architect Developer")
    assert api.source_ref.page == 8 and api.source_ref.bbox is not None and "$122.00" in (api.source_ref.quote or "")
    assert out.meta["contract_number"] == "DIR-STS-TSS-699"
    assert any("rejected" in f for f in out.flags)


def test_value_on_page_handles_separators(reading):
    rec, rd = reading
    from decimal import Decimal
    assert value_on_page(rd, 8, "$122.00", Decimal("122.00"))[0]
    assert value_on_page(rd, 8, None, Decimal("122"))[0]
    assert not value_on_page(rd, 8, "$4,321.99", Decimal("4321.99"))[0]


def test_model_failure_flags_the_section_not_the_document(reading):
    rec, rd = reading
    n = len(sections_for_rate_card(rd))
    model = FakeModel(["garbage"] * (3 * n))
    out = extract_rate_card(rec, rd, model)
    assert out.rows == [] and len(out.flags) >= n and all("never fit" in f for f in out.flags[:n])
