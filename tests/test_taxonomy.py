from pathlib import Path
"""Structural integrity of taxonomy/*.csv and the mapping table contract."""
from collections import Counter

import pytest

from twm.pipeline.mapping_table import MappingTable
from twm.taxonomy import BANDS, TaxonomyStore, TitleMapping, title_key


@pytest.fixture(scope="module")
def store():
    return TaxonomyStore.load()


def test_sizes_within_spec_targets(store):
    assert 120 <= len(store.roles) <= 180
    assert 40 <= len(store.tech) <= 60
    assert len(store.families) >= 16
    assert sum(1 for m in store.mappings if m.status == "active") >= 250


def test_ids_unique_and_snake_case(store):
    ids = [r.role_id for r in store.roles]
    assert len(ids) == len(set(ids))
    for rid in ids:
        assert rid == rid.lower() and " " not in rid and "-" not in rid


def test_every_family_has_roles(store):
    counts = Counter(r.family_id for r in store.roles)
    for f in store.families:
        assert counts[f.family_id] >= 1, f.family_id


def test_every_role_has_definition_and_disambiguation(store):
    for r in store.roles:
        assert len(r.definition) > 20, r.role_id
        assert len(r.disambiguation_notes) > 10, r.role_id


def test_no_sfia_content_in_taxonomy_tables():
    """SFIA is excluded from the product (requirements 3.1, decided Oct 6, 2026). The only permitted occurrence is the
    G-Cloud 14 vendor level-label scheme in band_crosswalk, which reads a public vendor document, not SFIA content."""
    tax = Path(__file__).resolve().parents[1] / "taxonomy"
    allowed = {"band_crosswalk.csv": ["G-Cloud 14 vendor level label (SFIA-numbered)", "not SFIA content"]}
    for csv_file in sorted(tax.glob("*.csv")):
        text = csv_file.read_text(encoding="utf-8")
        for phrase in allowed.get(csv_file.name, []):
            text = text.replace(phrase, "")
        assert "sfia" not in text.lower(), csv_file.name


def test_technology_not_in_role_names_outside_packaged(store):
    tech_words = {"java", "python", ".net", "sap", "salesforce", "oracle", "aws", "azure", "cobol", "mainframe"}
    for r in store.roles:
        if r.family_id == "pkg":
            continue
        assert not (set(title_key(r.name).split()) & tech_words), r.name


def test_band_values_are_valid(store):
    for b in store.bands:
        assert b.twm_band in BANDS


def test_spec_draft_band_mappings_present(store):
    expect = {
        ("TBIPS", "Level 1"): "junior", ("TBIPS", "Level 2"): "intermediate", ("TBIPS", "Level 3"): "senior",
        ("Texas DIR", "Intern Level 1"): "junior", ("Texas DIR", "Level 1"): "intermediate", ("Texas DIR", "Level 2"): "senior", ("Texas DIR", "Level 3"): "lead_principal",
        ("G-Cloud 14 vendor level label (SFIA-numbered)", "1"): "junior", ("G-Cloud 14 vendor level label (SFIA-numbered)", "3"): "intermediate", ("G-Cloud 14 vendor level label (SFIA-numbered)", "5"): "senior", ("G-Cloud 14 vendor level label (SFIA-numbered)", "7"): "lead_principal",
        ("DDaT", "Junior"): "junior", ("DDaT", "Senior"): "senior", ("DDaT", "Principal"): "lead_principal",
        ("NY HBITS", "Junior"): "junior", ("NY HBITS", "Mid-Level"): "intermediate", ("NY HBITS", "Senior"): "senior", ("NY HBITS", "Expert"): "lead_principal",
    }
    for (scheme, level), band in expect.items():
        row = store.band_for(scheme, level)
        assert row is not None, (scheme, level)
        assert row.twm_band == band


def test_mapping_rows_reference_valid_roles_and_tech(store):
    for m in store.mappings:
        if m.status == "deprecated":
            continue  # history may reference a retired role
        if m.canonical_role_id:
            assert m.canonical_role_id in store.role_by_id, m.observed_title
        if m.attr_technology:
            assert m.attr_technology in store.tech_by_tag, m.observed_title


def test_no_same_title_mapped_to_two_roles_within_one_source(store):
    # The same words may mean different jobs in different sources ("IT Manager" is a line manager in NY HBITS and a
    # consulting grade in Deloitte's price list); that is allowed and the resolver uses the observation's source to
    # choose. Within ONE source a title must map to one role.
    by_key = {}
    for m in store.mappings:
        if m.status != "active":
            continue
        k = (m.source, title_key(m.observed_title))
        by_key.setdefault(k, set()).add(m.canonical_role_id)
    conflicts = {k: v for k, v in by_key.items() if len(v) > 1}
    assert not conflicts, conflicts


def test_mapping_table_append_and_deprecate(store):
    mt = MappingTable(store)
    row = TitleMapping(observed_title="Quantum Widget Wrangler", source="unit-test", canonical_role_id="software_developer",
                       confidence=0.9, method="human", reviewer="test", status="active", version_added="test")
    mt.append(row)
    assert mt.has("quantum widget wrangler")
    with pytest.raises(ValueError):
        mt.append(row)  # no silent overwrite
    assert mt.deprecate("Quantum Widget Wrangler", source="unit-test") == 1
    assert not mt.has("Quantum Widget Wrangler")
    with pytest.raises(ValueError):
        mt.append(TitleMapping(observed_title="x", source="unit-test", canonical_role_id="no_such_role"))
