"""Regression: a document that went through the pipeline must give the same answer it gave before (test strategy, Oct 13, 2026).

These checks replay the model's recorded answers from the content-hash cache (`.cache/llm`, never committed). They never spend:
the model stand-in raises on any cache miss, which fails the check loudly instead of calling the real model. They skip on a
machine that lacks the documents or the cache; on Kyle's machine they run every time."""
from pathlib import Path

import pytest

from twm import llm
from twm.pipeline.run import run_family

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache/llm"
TEXAS = ROOT / "corpus/manifests/v3_downloads/v3_gov/085_Texas_DIR_Accenture_LLP_rate_exhibit.pdf"
GC15 = ROOT / "corpus/twm_corpus/UK_GCloud15_Accenture_service_page_ORIGINAL.html"


class CacheOnlyModel:
    """Answers only from the cache: a miss means the prompt or the document changed, and that is a finding, not a spend."""
    name = llm.DEFAULT_MODEL
    counts_toward_budget = False   # never reaches the API, so the daily call stop neither counts it nor logs it (Oct 13, 2026)

    def complete(self, system, user, max_tokens, temperature):
        raise RuntimeError("cache miss: this regression check never calls the model; the prompt or the document has changed")


def _run(path, vendor, client, tmp_path):
    rep = run_family([path], vendor=vendor, client=client, ledger_path=tmp_path / "regression.sqlite", model=CacheOnlyModel(),
                     cache_dir=CACHE, gold_dir=None)
    misses = [l for l in llm.LOG if l.error and "cache miss" in l.error]
    assert not misses, f"{len(misses)} model call(s) were not in the cache; the prompt or the document changed: {misses[0].error}"
    return rep


@pytest.mark.skipif(not (TEXAS.exists() and CACHE.exists()), reason="Texas pricing exhibit or the model cache not on disk")
def test_texas_dir_accenture_pricing_exhibit_gives_the_same_answer_as_on_oct_13(tmp_path):
    """Texas DIR Accenture pricing exhibit (085), re-based Oct 13, 2026 when the grid was split by block and service type and every contract year copied from the printed row: 1,648 verified rates (206 read by the model, 1,442 copied), 0 rejected, 1,488 resolved (688 unbanded), 2 flagged titles, 3 ambiguous, 1,488 counted; 4 facts and 2 conditions from its term pages. On Oct 6 it was 53 rates, year 1 of one block."""
    rep = _run(TEXAS, "Accenture LLP", "Texas DIR", tmp_path)
    assert (rep.rows_kept, rep.rows_rejected, rep.base_rows, rep.expanded_rows) == (1648, 0, 206, 1442)
    assert (rep.resolved, rep.unbanded, rep.counted) == (1488, 688, 1488)
    assert sorted(set(rep.flagged_titles)) == ["Operations", "Technical Specialist"]
    assert len(set(rep.ambiguous_titles)) == 3
    assert rep.example and rep.example["page"] == 8
    assert (rep.facts, rep.terms, rep.items_rejected) == (4, 2, 0)


MICHIGAN = ROOT / "corpus/twm_corpus/MI_DTMB_Deloitte_MiIntegrate_Contract_SOW_Rates_2013-2026_ORIGINAL.pdf"


@pytest.mark.skipif(not (MICHIGAN.exists() and CACHE.exists()), reason="Michigan Deloitte contract or the model cache not on disk")
def test_michigan_deloitte_miintegrate_contract_gives_the_same_answer_as_on_oct_13(tmp_path):
    """Michigan Deloitte MiIntegrate (378 pages, one cumulative file), Oct 13, 2026: 109 pages read for terms in 19 calls; 91 facts, 118 conditions, 23 named resources, 1 item rejected on the page; 42 prose rate rows, 0 rejected, 6 resolved; disclosure check cleared by the public-record clause."""
    rep = _run(MICHIGAN, "Deloitte Consulting LLP", "State of Michigan DTMB", tmp_path)
    assert (rep.facts, rep.terms, rep.resources, rep.items_rejected) == (91, 118, 23, 1)
    assert (rep.rows_kept, rep.rows_rejected, rep.resolved) == (42, 0, 6)
    assert rep.disclosure_status == "cleared" and "public_record" in rep.disclosure[0]
    assert len(rep.term_docs) == 1 and rep.term_docs[0]["calls"] == 19 and rep.term_docs[0]["pages"] == 109


@pytest.mark.skipif(not (GC15.exists() and CACHE.exists()), reason="G-Cloud page or the model cache not on disk")
def test_accenture_gcloud_15_page_gives_the_same_answer_as_on_oct_6(tmp_path):
    """Accenture G-Cloud 15 page: 430 verified rates, 0 rejected, 416 resolved (90 unbanded, 6 by the model step), 14 flagged, 410 counted."""
    rep = _run(GC15, "Accenture (UK) Ltd", "UK G-Cloud 15", tmp_path)
    assert (rep.rows_kept, rep.rows_rejected) == (430, 0)
    assert (rep.resolved, rep.unbanded, rep.model_resolutions, rep.counted) == (416, 90, 6, 410)
    assert len(rep.flagged_titles) == 14
