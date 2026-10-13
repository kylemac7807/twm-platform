"""Workbench (work/workbench/spec.md): page rendering with the row's box, and the screens on a fixture ledger."""
from pathlib import Path

import pytest
from PIL import Image

from twm.workbench.render import draw_box, render_row

ROOT = Path(__file__).resolve().parents[1]
PRICING = ROOT / "corpus/manifests/v3_downloads/v3_gov/085_Texas_DIR_Accenture_LLP_rate_exhibit.pdf"
TEXAS_ROW = dict(path=str(PRICING), true_type="pdf", source_page=8, source_bbox="[65.0, 128.0, 553.8, 132.6]",
                 source_quote="Advanced Systems Engineer | Hourly Rate | $83.00")


def _has_red(img: Image.Image, x0, y0, x1, y1) -> bool:
    px = img.load()
    for x in range(max(0, int(x0)), min(img.width, int(x1))):
        for y in range(max(0, int(y0)), min(img.height, int(y1))):
            r, g, b = px[x, y][:3]
            if r > 170 and g < 90 and b < 90:
                return True
    return False


def test_box_is_drawn_where_the_stored_coordinates_say():
    """A 50 x 100 pt page rendered at 100 x 200 px: a box at (10, 20, 30, 40) pt must appear at (20..60, 40..80) px, nowhere else."""
    blank = Image.new("RGB", (100, 200), "white")
    out = draw_box(blank, (10, 20, 30, 40), 50, 100, pad=0, width=2)
    assert _has_red(out, 20, 38, 60, 44)         # top edge
    assert _has_red(out, 18, 40, 24, 80)         # left edge
    assert not _has_red(out, 0, 100, 100, 200)   # nothing in the lower half
    assert not _has_red(blank, 0, 0, 100, 200)   # the original is untouched


@pytest.mark.skipif(not PRICING.exists(), reason="pricing exhibit not on disk")
def test_texas_row_renders_page_8_with_the_box_on_the_right_line(tmp_path):
    out = render_row(TEXAS_ROW, cache_dir=tmp_path)
    assert out["kind"] == "pdf" and out["page"] == 8 and out["bbox"] == (65.0, 128.0, 553.8, 132.6)
    img = out["image"]
    w_pt, h_pt = out["page_size_pt"]
    sx, sy = img.width / w_pt, img.height / h_pt
    assert _has_red(img, 65 * sx, 128 * sy - 6, 553.8 * sx, 128 * sy + 2)      # the top edge of the box, where the line sits
    assert not _has_red(img, 65 * sx, 300 * sy, 553.8 * sx, 320 * sy)          # not on an unrelated line further down
    assert out["closeup"].height < img.height and out["closeup"].width <= img.width
    cached = list(Path(tmp_path).glob("*_p8_r*.png"))
    assert len(cached) == 1                                                     # the page is cached for the next row on it
    again = render_row(TEXAS_ROW, cache_dir=tmp_path)
    assert again["image"].size == img.size


# ---------------------------------------------------------------- the screens, headless
APP = ROOT / "src/twm/workbench/app.py"


def _fixture_ledger(tmp_path):
    """Same shape as tests/test_ledger.py: two flagged 'Operations' rows queued twice, a resolved row, a flagged place name."""
    from decimal import Decimal
    from twm.pipeline.contracts import RateRow
    from twm.pipeline.ingest import register
    from twm.pipeline.ledger import Ledger
    from twm.pipeline.models import SourceRef
    from twm.pipeline.normalize import resolve
    from twm.taxonomy import TaxonomyStore

    def row(title, rate, conf=0.95):
        return RateRow(observed_title=title, rate_value=Decimal(rate), rate_as_stated=f"${rate}", currency="USD", rate_unit="hour", period_raw="Year 1",
                       confidence=conf, source_ref=SourceRef(document_id="d", page=2, bbox=(10, 20, 30, 40), quote=f"{title} | Hourly Rate | ${rate}"))
    store = TaxonomyStore.load()
    p = tmp_path / "exhibit.txt"; p.write_text("rate card exhibit", encoding="utf-8")
    rec = register(p)
    path = tmp_path / "ledger.sqlite"
    led = Ledger(path); led.upsert_document(rec); led.start_run("run1", "local", "fake", "0.1")
    flagged = resolve("Operations", store)
    for rate in ("99.50", "101.00"):
        led.add_observation("run1", rec, row("Operations", rate), flagged, vendor="Acme", client="bank-a", effective_date=None, scan_quality="native")
        led.queue("run1", rec.document_id, "title", "Operations", "no rule match; needs model/human resolution")
    led.add_observation("run1", rec, row("Senior Java Developer", "140.00"), resolve("Senior Java Developer", store), vendor="Acme", client="bank-a", effective_date=None, scan_quality="native")
    place = resolve("Developer (Buffalo)", store)
    led.add_observation("run1", rec, row("Developer (Buffalo)", "120.00"), place, vendor="Acme", client="bank-a", effective_date=None, scan_quality="native")
    led.queue("run1", rec.document_id, "location", "Developer (Buffalo)", "place 'buffalo' needs an analyst decision")
    led.close()
    return path


def _app(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("TWM_LEDGER", str(_fixture_ledger(tmp_path)))
    at = AppTest.from_file(str(APP), default_timeout=60)
    return at


def test_documents_screen_lists_the_contract_set_with_the_systems_own_words(tmp_path, monkeypatch):
    at = _app(tmp_path, monkeypatch).run()
    assert not at.exception
    assert any("Open queue items: 3" in m.value for m in at.sidebar.markdown)
    assert any(h.value.startswith("Contract set: exhibit.txt") for h in at.subheader)
    table = at.dataframe[0].value
    assert list(table["file"]) == ["exhibit.txt"] and table["type"][0] == "rate_card"
    assert "rate card" in table["evidence"][0]                     # the classification evidence, verbatim


def test_inspect_screen_traces_a_row_to_its_quote_and_resolution(tmp_path, monkeypatch):
    at = _app(tmp_path, monkeypatch)
    at.run()
    at.sidebar.radio[0].set_value("Inspect").run()
    assert not at.exception
    assert any("4 rows" in c.value for c in at.caption)
    at.radio[0].set_value("not counted").run()
    assert any("2 rows" in c.value for c in at.caption)           # the two flagged Operations rows
    picks = at.selectbox[1].options
    assert all("Operations" in p for p in picks)
    at.selectbox[1].set_value(picks[0]).run()
    assert not at.exception
    assert any("Operations | Hourly Rate | $99.50" in c.value for c in at.code)   # the quote, since a text file has no page image
    shown = " ".join(t.value.to_string() for t in at.table)
    assert "flagged" in shown and "no" in shown                   # status flagged, counted: no


def test_web_rows_and_missing_files_are_reported_not_guessed():
    web = render_row(dict(path="x.html", true_type="html", source_page=1, source_bbox="[0.0, 0.0, 0.0, 0.0]", source_quote="Trainee business architect | £750.00 | £195.00"))
    assert web["kind"] == "web" and "£750.00" in web["quote"]
    nobox = render_row(dict(path="x.pdf", true_type="pdf", source_page=3, source_bbox=None, source_quote="q"))
    assert nobox["kind"] == "nobox"
    missing = render_row(dict(path="does-not-exist.pdf", true_type="pdf", source_page=3, source_bbox="[1, 2, 3, 4]", source_quote="q"))
    assert missing["kind"] == "missing" and "not on disk" in missing["note"]
