"""The M1 acceptance thresholds, run against the live seed sources (slow-ish: a few seconds)."""
from collections import defaultdict
from statistics import mean

import pytest

from twm.taxonomy import BANDS, TaxonomyStore
from twm.taxonomy.acceptance import load_observations, run


@pytest.fixture(scope="module")
def results():
    store = TaxonomyStore.load()
    return store, run(store, load_observations())


def test_round_trip_resolves_at_least_90_percent(results):
    _, res = results
    seen, resolved, total = set(), 0, 0
    for o, r in res:
        if o.source == "Deloitte GC15 grades":
            continue
        k = (o.source, o.title, o.level)
        if k in seen:
            continue
        seen.add(k)
        total += 1
        resolved += r.status == "resolved"
    assert total > 1000
    assert resolved / total >= 0.90


def test_no_ambiguous_titles(results):
    _, res = results
    assert not [o.title for o, r in res if r.status == "ambiguous"]


def test_bands_monotonic_in_every_rate_grid(results):
    store, res = results
    grids = defaultdict(lambda: defaultdict(list))
    for o, r in res:
        if not o.grid or o.rate is None:
            continue
        band = r.twm_band
        if o.source == "Deloitte GC15 grades":
            b = store.band_for("Deloitte CS grade", o.level)
            band = b.twm_band if b else None
        if band:
            grids[o.grid][band].append(o.rate)
    assert len(grids) >= 25
    for g, by_band in grids.items():
        means = [mean(by_band[b]) for b in BANDS if by_band.get(b)]
        assert all(means[i] <= means[i + 1] for i in range(len(means) - 1)), (g, means)
