"""Intake (M2 step 1): identity from content, true type by sniffing, classification with evidence, family links on evidence."""
from pathlib import Path

import pytest

from twm.pipeline.ingest import classify, family_summary, register, register_family, sniff_type

ROOT = Path(__file__).resolve().parents[1]
ACC = sorted((ROOT / "corpus/manifests/v3_downloads/v3_gov").glob("08[1-7]_Texas_DIR_Accenture_LLP_*.pdf"))
have_accenture = len(ACC) == 7


def test_sniff_never_trusts_the_extension(tmp_path):
    fake = tmp_path / "viewer.pdf"
    fake.write_text("<!DOCTYPE html><html><body>viewer page</body></html>", encoding="utf-8")
    rec = register(fake)
    assert rec.true_type == "html" and rec.extension_mismatch is True
    assert any("content is html" in f for f in rec.flags)
    assert sniff_type(b"%PDF-1.7 ...") == "pdf"
    assert sniff_type(b"PK\x03\x04") == "zip"


def test_identity_is_from_content_not_name(tmp_path):
    a = tmp_path / "a.txt"; b = tmp_path / "b.txt"
    a.write_text("same bytes", encoding="utf-8"); b.write_text("same bytes", encoding="utf-8")
    ra, rb = register(a), register(b)
    assert ra.document_id == rb.document_id and ra.fingerprint == rb.fingerprint
    recs = register_family([a, b])
    assert any(l.relation == "duplicate_of" for l in recs[1].links)


@pytest.mark.parametrize("text,expected", [
    ("STATEMENT OF WORK\nExhibit 1 to the Master Services Agreement", "sow"),
    ("MASTER SERVICES AGREEMENT between the Texas Department of Information Resources and Accenture LLP", "msa"),
    ("Attachment 2.1 Pricing and Volumes\nLabor Category  Hourly Rate", "rate_card"),
    ("Invoice No. 4471\nRemit to: Vendor Inc", "invoice"),
    ("Weekly Timesheet  Week ending 7/25/21  Hours", "timesheet"),
    ("Amendment No. 3 to the Agreement", "amendment"),
    ("Lorem ipsum nothing here", "unknown"),
])
def test_classification_with_evidence(text, expected):
    cls, conf, evidence = classify(text, "x.pdf")
    assert cls == expected
    if expected != "unknown":
        assert conf >= 0.7 and "in first pages" in evidence


def test_unknown_goes_to_a_person(tmp_path):
    p = tmp_path / "mystery.txt"; p.write_text("nothing recognisable at all", encoding="utf-8")
    rec = register(p)
    assert rec.doc_class == "unknown" and any("needs a person" in f for f in rec.flags)


@pytest.mark.skipif(not have_accenture, reason="Accenture family not on disk")
def test_accenture_family_registers_as_one_family():
    recs = register_family(ACC)
    assert len(recs) == 7
    assert all(r.true_type == "pdf" and r.readiness == "text" for r in recs)
    numbers = {n for r in recs for n in r.contract_numbers}
    assert "DIR-STS-TSS-699" in numbers
    roots = {r.family_id for r in recs if r.family_id}
    assert len(roots) == 1, "all seven should link under one root"
    root = next(r for r in recs if r.document_id == r.family_id)
    classes = {r.doc_class for r in recs}
    assert "sow" in classes and "rate_card" in classes
    summary = family_summary(recs)
    assert "7 documents registered" in summary and "DIR-STS-TSS-699" in summary
    print(summary)
