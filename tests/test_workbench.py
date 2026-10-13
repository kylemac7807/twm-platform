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
    tmp_path.mkdir(parents=True, exist_ok=True)
    p = tmp_path / "exhibit.txt"; p.write_text("rate card exhibit", encoding="utf-8")
    rec = register(p)
    path = tmp_path / "ledger.sqlite"
    led = Ledger(path); led.upsert_document(rec); led.start_run("run1", "local", "fake", "0.1")
    flagged = resolve("Operations", store)
    for rate in ("99.50", "101.00"):
        led.add_observation("run1", rec, row("Operations", rate), flagged, vendor="Acme", client="bank-a", effective_date=None, scan_quality="native")
        led.queue("run1", rec.document_id, "title", "Operations", "no rule match; needs model/human resolution")
    led.add_observation("run1", rec, row("Senior Java Developer", "140.00"), resolve("Senior Java Developer", store), vendor="Acme", client="bank-a", effective_date=None, scan_quality="native")
    spec = resolve("Technical Specialist", store)
    assert spec.status == "flagged"
    led.add_observation("run1", rec, row("Technical Specialist", "110.00"), spec, vendor="Acme", client="bank-a", effective_date=None, scan_quality="native")
    led.queue("run1", rec.document_id, "title", "Technical Specialist", "no rule match; needs model/human resolution")
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
    assert any("Open queue items: 4" in m.value for m in at.sidebar.markdown)
    assert any(h.value.startswith("Contract set: exhibit.txt") for h in at.subheader)
    table = at.dataframe[0].value
    assert list(table["file"]) == ["exhibit.txt"] and table["type"][0] == "rate_card"
    assert "rate card" in table["evidence"][0]                     # the classification evidence, verbatim


def test_inspect_screen_traces_a_row_to_its_quote_and_resolution(tmp_path, monkeypatch):
    at = _app(tmp_path, monkeypatch)
    at.run()
    at.sidebar.radio[0].set_value("Inspect").run()
    assert not at.exception
    assert any("5 rows" in c.value for c in at.caption)
    at.radio[0].set_value("not counted").run()
    assert any("3 rows" in c.value for c in at.caption)           # the two flagged Operations rows and Technical Specialist
    at.text_input(key="inspect_search").input("operations").run()
    assert any("2 rows" in c.value for c in at.caption)
    picks = at.selectbox[1].options
    assert all("Operations" in p for p in picks)
    at.selectbox[1].set_value(picks[0]).run()
    assert not at.exception
    assert any("Operations | Hourly Rate | $99.50" in c.value for c in at.code)   # the quote, since a text file has no page image
    shown = " ".join(t.value.to_string() for t in at.table)
    assert "flagged" in shown and "no" in shown                   # status flagged, counted: no


def _submit(at, label="Record decision"):
    btn = [b for b in at.button if b.label == label]
    assert btn, [b.label for b in at.button]
    return btn[0].click().run()


def _ledger_state(path):
    import sqlite3
    c = sqlite3.connect(path)
    obs = c.execute("SELECT observed_title, canonical_role_id, twm_band, band_source, resolution_status, counted, needs_band_review FROM observations "
                    "WHERE superseded_by IS NULL ORDER BY obs_id").fetchall()
    dec = c.execute("SELECT queue_id, kind, item, decision_json, reason, decided_by, superseded_by FROM queue_decisions ORDER BY id").fetchall()
    q = c.execute("SELECT id, status FROM review_queue ORDER BY id").fetchall()
    c.close()
    return obs, dec, q


def test_a_title_decision_through_the_screen_equals_the_direct_call(tmp_path, monkeypatch):
    from twm.pipeline.ledger import Ledger
    at = _app(tmp_path, monkeypatch)
    import os
    path = os.environ["TWM_LEDGER"]
    at.run()
    at.sidebar.radio[0].set_value("Queues").run()
    assert not at.exception
    groups_shown = at.dataframe[0].value
    assert list(groups_shown["title"]) == ["Operations", "Technical Specialist"]        # sorted by rows unlocked: 2 then 1
    assert list(groups_shown["rows_unlocked"]) == [2, 1]
    # no name yet: the decision is refused and nothing changes
    at.multiselect(key="title_pick").select(at.multiselect(key="title_pick").options[0]).run()
    at.text_area(key="reason").input("Operations on this exhibit is the systems operations role").run()
    _submit(at)
    assert any("name" in w.value for w in at.warning)
    before = _ledger_state(path)
    assert before[1] == []                                          # no decision was written
    # with a name, the default band is unbanded and the reason is required
    at.sidebar.text_input(key="analyst").input("Kyle McNamara").run()
    at.multiselect(key="title_pick").select(at.multiselect(key="title_pick").options[0]).run()
    role_opts = at.selectbox(key="role_label").options
    at.selectbox(key="role_label").set_value([o for o in role_opts if o.endswith("[systems_engineer]")][0])
    at.text_area(key="reason").input("   ")
    _submit(at)
    assert any("reason" in e.value for e in at.error)
    at.multiselect(key="title_pick").select(at.multiselect(key="title_pick").options[0]).run()
    at.selectbox(key="role_label").set_value([o for o in role_opts if o.endswith("[systems_engineer]")][0])
    at.text_area(key="reason").input("Operations on this exhibit is the systems operations role")
    _submit(at)
    assert not at.exception and not at.error, [e.value for e in at.error]
    via_screen = _ledger_state(path)
    # the same decision by the direct call, on a fresh copy of the fixture
    other = _fixture_ledger(tmp_path / "direct")
    led = Ledger(other)
    g = led.title_queue_groups()[0]
    led.decide_title(g["queue_ids"], role_id="systems_engineer", band=None, reason="Operations on this exhibit is the systems operations role", decided_by="Kyle McNamara")
    led.close()
    direct = _ledger_state(other)
    assert via_screen == direct
    ops = [o for o in via_screen[0] if o[0] == "Operations"]
    assert all(o[1] == "systems_engineer" and o[2] is None and o[3] == "analyst" and o[4] == "resolved" and o[5] == 1 for o in ops)


def test_bulk_decision_writes_one_decision_row_per_queue_item(tmp_path, monkeypatch):
    import os
    at = _app(tmp_path, monkeypatch)
    path = os.environ["TWM_LEDGER"]
    at.run()
    at.sidebar.text_input(key="analyst").input("Kyle McNamara").run()
    at.sidebar.radio[0].set_value("Queues").run()
    opts = at.multiselect(key="title_pick").options
    at.multiselect(key="title_pick").set_value(opts).run()
    role_opts = at.selectbox(key="role_label").options
    at.selectbox(key="role_label").set_value([o for o in role_opts if o.endswith("[systems_engineer]")][0])
    at.selectbox(key="band_label").set_value("senior")
    at.text_area(key="reason").input("both are senior operations roles per the SOW")
    _submit(at)                                                    # without the confirmation tick: refused
    assert any("confirmation" in e.value for e in at.error), [e.value for e in at.error]
    at.multiselect(key="title_pick").set_value(opts).run()
    at.selectbox(key="role_label").set_value([o for o in role_opts if o.endswith("[systems_engineer]")][0])
    at.selectbox(key="band_label").set_value("senior")
    at.text_area(key="reason").input("both are senior operations roles per the SOW")
    at.checkbox(key="confirm_bulk").check()
    _submit(at)
    assert not at.exception and not at.error, [e.value for e in at.error]
    obs, dec, q = _ledger_state(path)
    assert len(dec) == 3 and {d[2] for d in dec} == {"Operations", "Technical Specialist"}      # one row per queue item
    assert all(d[5] == "Kyle McNamara" and "senior" in d[3] for d in dec)
    assert [s for _, s in q] == ["resolved", "resolved", "resolved", "open"]                 # the location item (4th) still open
    assert all(o[2] == "senior" and o[5] == 1 for o in obs if o[0] in ("Operations", "Technical Specialist"))


def test_location_decision_through_the_screen(tmp_path, monkeypatch):
    import os
    at = _app(tmp_path, monkeypatch)
    path = os.environ["TWM_LEDGER"]
    at.run()
    at.sidebar.text_input(key="analyst").input("Kyle McNamara").run()
    at.sidebar.radio[0].set_value("Queues").run()
    opts = at.multiselect(key="loc_pick").options
    assert len(opts) == 1 and "buffalo" in opts[0]
    at.multiselect(key="loc_pick").set_value(opts).run()
    at.radio(key="loc_cls").set_value("nearshore")
    at.text_area(key="loc_reason").input("Buffalo is nearshore for this Toronto bank")
    _submit(at)
    assert not at.exception and not at.error, [e.value for e in at.error]
    obs, dec, q = _ledger_state(path)
    assert any(d[1] == "location" and '"nearshore"' in d[3] for d in dec)
    import sqlite3
    c = sqlite3.connect(path)
    assert c.execute("SELECT attr_location, needs_location_review FROM observations WHERE observed_title='Developer (Buffalo)'").fetchone() == ("nearshore", 0)
    c.close()


def test_codify_screen_exports_in_taxonomy_column_order_and_marks_applied(tmp_path, monkeypatch):
    import os
    from twm.pipeline.ledger import Ledger
    from twm.workbench.screens import codification_csv
    at = _app(tmp_path, monkeypatch)
    path = os.environ["TWM_LEDGER"]
    led = Ledger(path)
    g = led.title_queue_groups()[0]
    led.decide_title(g["queue_ids"], role_id="systems_engineer", band=None, reason="r", decided_by="Kyle McNamara")
    led.decide_location([q["id"] for q in led.queue_items("location")], classification="nearshore", reason="r", decided_by="Kyle McNamara")
    pend = led.pending_codification()
    led.close()
    header = (ROOT / "taxonomy/title_mappings.csv").read_text(encoding="utf-8").splitlines()[0]
    csv = codification_csv(pend["title_mappings"]).splitlines()
    assert csv[0] == header and csv[1].startswith("Operations,bank-a,,systems_engineer,,")
    assert codification_csv(pend["location_rules"]).splitlines()[0] == (ROOT / "taxonomy/location_rules.csv").read_text(encoding="utf-8").splitlines()[0]
    at.run()
    at.sidebar.radio[0].set_value("Decisions to codify").run()
    assert not at.exception
    assert [h.value for h in at.subheader] == ["Title mappings: 1 waiting", "Location rules: 1 waiting"]
    assert list(at.dataframe[0].value["observed_title"]) == ["Operations"]
    at.button(key="mark_title_mappings").click().run()
    assert any("Pick" in e.value for e in at.error)                  # nothing picked: refused
    at.multiselect(key="applied_title_mappings").set_value(at.multiselect(key="applied_title_mappings").options)
    at.button(key="mark_title_mappings").click().run()
    assert not at.exception
    after = Ledger(path).pending_codification()
    assert after["title_mappings"] == [] and len(after["location_rules"]) == 1


def test_web_rows_and_missing_files_are_reported_not_guessed():
    web = render_row(dict(path="x.html", true_type="html", source_page=1, source_bbox="[0.0, 0.0, 0.0, 0.0]", source_quote="Trainee business architect | £750.00 | £195.00"))
    assert web["kind"] == "web" and "£750.00" in web["quote"]
    nobox = render_row(dict(path="x.pdf", true_type="pdf", source_page=3, source_bbox=None, source_quote="q"))
    assert nobox["kind"] == "nobox"
    missing = render_row(dict(path="does-not-exist.pdf", true_type="pdf", source_page=3, source_bbox="[1, 2, 3, 4]", source_quote="q"))
    assert missing["kind"] == "missing" and "not on disk" in missing["note"]
