"""Document reading (M2 step 2): positions for every line, tables with cells, a quality grade, and find() for verification."""
from pathlib import Path

import pytest

from twm.pipeline.ingest import register
from twm.pipeline.read import HtmlReader, LocalPdfReader, reader_for

ROOT = Path(__file__).resolve().parents[1]
PRICING = ROOT / "corpus/manifests/v3_downloads/v3_gov/085_Texas_DIR_Accenture_LLP_rate_exhibit.pdf"
GC15 = ROOT / "corpus/twm_corpus/UK_GCloud15_Accenture_service_page_ORIGINAL.html"


@pytest.mark.skipif(not PRICING.exists(), reason="pricing exhibit not on disk")
def test_pricing_exhibit_reads_with_positions_and_tables():
    rec = register(PRICING)
    rd = LocalPdfReader().read(rec)
    assert rd.quality == "native" and len(rd.pages) == 11
    # a rate in the exhibit can be located by page and position
    hits = rd.find("API Architect Developer")
    assert hits, "the first labour category must be findable"
    ln = hits[0]
    assert ln.page >= 1 and ln.bbox[2] > ln.bbox[0] and ln.bbox[3] > ln.bbox[1]
    assert "$" in ln.text   # the rate sits on the same visual line as the title
    tables = rd.all_tables()
    assert tables and any(t.n_rows > 5 for t in tables)


@pytest.mark.skipif(not GC15.exists(), reason="G-Cloud page not on disk")
def test_gcloud_page_reads_html_tables():
    rec = register(GC15)
    rd = reader_for(rec).read(rec)
    assert isinstance(reader_for(rec), HtmlReader)
    assert rd.quality == "web"
    big = [t for t in rd.all_tables() if t.n_rows >= 4]
    assert big, "the service page carries rate tables"
    rows = [r for t in big for r in t.rows()]
    assert any("developer" in " ".join(r).lower() and "£" in " ".join(r) for r in rows)


def test_scan_without_text_layer_is_graded_none(tmp_path):
    # a minimal PDF with no text objects at all
    p = tmp_path / "blank.pdf"
    p.write_bytes(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
                  b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF")
    rec = register(p)
    rd = LocalPdfReader().read(rec)
    assert rd.quality == "none" and "OCR" in rd.quality_note


def test_unsupported_type_is_explicit(tmp_path):
    p = tmp_path / "x.txt"; p.write_text("plain text", encoding="utf-8")
    with pytest.raises(NotImplementedError):
        reader_for(register(p))
