"""Ledger (M2 step 6): append never overwrite, supersede on re-run, confidence gates counting, currency as a derived column."""
from decimal import Decimal

from twm.pipeline.contracts import RateRow
from twm.pipeline.ingest import register
from twm.pipeline.ledger import Ledger
from twm.pipeline.models import SourceRef
from twm.pipeline.normalize import resolve
from twm.taxonomy import TaxonomyStore


def _row(title, rate, conf=0.95, currency="USD"):
    return RateRow(observed_title=title, rate_value=Decimal(rate), rate_as_stated=f"${rate}", currency=currency, rate_unit="hour",
                   period_raw="Year 1", confidence=conf, source_ref=SourceRef(document_id="d", page=8, bbox=(1, 2, 3, 4), quote="q"))


def test_append_supersede_and_counting(tmp_path):
    store = TaxonomyStore.load()
    p = tmp_path / "doc.txt"; p.write_text("STATEMENT OF WORK rate card", encoding="utf-8")
    rec = register(p)
    led = Ledger(tmp_path / "ledger.sqlite")
    led.upsert_document(rec)
    led.start_run("run1", "local", "fake", "0.1")
    r1 = resolve("Senior Java Developer", store)
    led.add_observation("run1", rec, _row("Senior Java Developer", "140.00"), r1, vendor="Acme", client="bank-a", effective_date="2027-01-01", scan_quality="native")
    led.add_observation("run1", rec, _row("Senior Java Developer", "141.00", conf=0.6), r1, vendor="Acme", client="bank-a", effective_date="2027-01-01", scan_quality="native")
    unb = resolve("Program Manager", store)   # unbanded: resolved role, no band -> still resolved, counted
    led.add_observation("run1", rec, _row("Program Manager", "200.00"), unb, vendor="Acme", client="bank-a", effective_date="2027-01-01", scan_quality="native")
    flagged = resolve("Chief Happiness Wrangler", store)
    led.add_observation("run1", rec, _row("Chief Happiness Wrangler", "99.00"), flagged, vendor="Acme", client="bank-a", effective_date="2027-01-01", scan_quality="native")
    c = led.counts()
    assert c["observations_live"] == 4
    assert c["counted"] == 2   # the 0.6-confidence row and the flagged row exist but do not count
    # re-run supersedes, never overwrites
    led.start_run("run2", "local", "fake", "0.1")
    n = led.supersede_document(rec.document_id, "run2")
    assert n == 4
    led.add_observation("run2", rec, _row("Senior Java Developer", "140.00"), r1, vendor="Acme", client="bank-a", effective_date="2027-01-01", scan_quality="native")
    c = led.counts()
    assert c["observations_live"] == 1 and c["observations_superseded"] == 4
    led.close()


def test_currency_is_derived_never_converted_in_place(tmp_path):
    store = TaxonomyStore.load()
    p = tmp_path / "doc.txt"; p.write_text("rate card", encoding="utf-8")
    rec = register(p)
    led = Ledger(tmp_path / "l.sqlite"); led.upsert_document(rec); led.start_run("r", "local", "fake", "0.1")
    res = resolve("Software Developer", store)
    led.add_observation("r", rec, _row("Software Developer", "650.00", currency="GBP"), res, vendor="Accenture", client=None, effective_date="2026-01-27",
                        scan_quality="web", reporting_currency="CAD", fx=(Decimal("1.72"), "2026-01-27", "Bank of Canada daily rate"))
    row = led.live_rows()[0]
    assert row["rate_value"] == "650.00" and row["currency"] == "GBP"            # as stated
    assert row["reporting_currency"] == "CAD" and row["reporting_value"] == "1118.00"
    assert row["fx_rate"] == "1.72" and row["fx_source"].startswith("Bank of Canada")
    led.close()
