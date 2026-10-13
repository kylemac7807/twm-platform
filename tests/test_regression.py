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

    def complete(self, system, user, max_tokens, temperature):
        raise RuntimeError("cache miss: this regression check never calls the model; the prompt or the document has changed")


def _run(path, vendor, client, tmp_path):
    rep = run_family([path], vendor=vendor, client=client, ledger_path=tmp_path / "regression.sqlite", model=CacheOnlyModel(),
                     cache_dir=CACHE, gold_dir=None)
    misses = [l for l in llm.LOG if l.error and "cache miss" in l.error]
    assert not misses, f"{len(misses)} model call(s) were not in the cache; the prompt or the document changed: {misses[0].error}"
    return rep


@pytest.mark.skipif(not (TEXAS.exists() and CACHE.exists()), reason="Texas pricing exhibit or the model cache not on disk")
def test_texas_dir_accenture_pricing_exhibit_gives_the_same_answer_as_on_oct_6(tmp_path):
    """Texas DIR Accenture pricing exhibit (085): 53 verified rates, 0 rejected, 48 resolved (23 unbanded), 2 flagged, 3 ambiguous, 48 counted."""
    rep = _run(TEXAS, "Accenture LLP", "Texas DIR", tmp_path)
    assert (rep.rows_kept, rep.rows_rejected) == (53, 0)
    assert (rep.resolved, rep.unbanded, rep.counted) == (48, 23, 48)
    assert sorted(set(rep.flagged_titles)) == ["Operations", "Technical Specialist"]
    assert len(set(rep.ambiguous_titles)) == 3
    assert rep.example and rep.example["page"] == 8


@pytest.mark.skipif(not (GC15.exists() and CACHE.exists()), reason="G-Cloud page or the model cache not on disk")
def test_accenture_gcloud_15_page_gives_the_same_answer_as_on_oct_6(tmp_path):
    """Accenture G-Cloud 15 page: 430 verified rates, 0 rejected, 416 resolved (90 unbanded, 6 by the model step), 14 flagged, 410 counted."""
    rep = _run(GC15, "Accenture (UK) Ltd", "UK G-Cloud 15", tmp_path)
    assert (rep.rows_kept, rep.rows_rejected) == (430, 0)
    assert (rep.resolved, rep.unbanded, rep.model_resolutions, rep.counted) == (416, 90, 6, 410)
    assert len(rep.flagged_titles) == 14
