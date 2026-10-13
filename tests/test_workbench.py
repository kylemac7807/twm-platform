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


def test_web_rows_and_missing_files_are_reported_not_guessed():
    web = render_row(dict(path="x.html", true_type="html", source_page=1, source_bbox="[0.0, 0.0, 0.0, 0.0]", source_quote="Trainee business architect | £750.00 | £195.00"))
    assert web["kind"] == "web" and "£750.00" in web["quote"]
    nobox = render_row(dict(path="x.pdf", true_type="pdf", source_page=3, source_bbox=None, source_quote="q"))
    assert nobox["kind"] == "nobox"
    missing = render_row(dict(path="does-not-exist.pdf", true_type="pdf", source_page=3, source_bbox="[1, 2, 3, 4]", source_quote="q"))
    assert missing["kind"] == "missing" and "not on disk" in missing["note"]
