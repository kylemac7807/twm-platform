"""The workbench screens (work/workbench/spec.md). Each is a function of the ledger; they read through Ledger methods and write
through Ledger methods, nothing else. Honest screens: the system's own words for what it found and why it abstained, verbatim;
no field prefilled with a guess; the band default is unbanded."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from twm.pipeline.ledger import BANDS, Ledger
from twm.taxonomy.store import TaxonomyStore
from twm.workbench.render import render_row

BAND_CHOICES = ["unbanded (no seniority evidence)"] + list(BANDS)


# ---------------------------------------------------------------- 1. Documents
def documents(led: Ledger) -> None:
    st.header("Documents, as intake sorted them")
    sets = led.documents_by_set()
    if not sets:
        st.info("No documents in this ledger yet. Run a contract set with `python -m twm.pipeline.run`.")
        return
    st.caption(f"{sum(len(s['documents']) for s in sets)} documents in {len(sets)} contract sets. A contract set is the documents that belong to one contract; "
               "intake links them by the contract number printed on the page.")
    for s in sets:
        docs = s["documents"]
        title = s["root_filename"] or docs[0]["filename"]
        st.subheader(f"Contract set: {title}" + (f" ({len(docs)} documents)" if len(docs) > 1 else " (one document, no set found)"))
        rows = []
        for d in docs:
            rec = json.loads(d["record_json"]) if d.get("record_json") else {}
            rows.append(dict(
                file=d["filename"], type=d["doc_class"], confidence=d["class_confidence"],
                evidence=rec.get("class_evidence", ""), content=d["true_type"] + ("" if not rec.get("extension_mismatch") else " (extension says otherwise)"),
                readiness=d["readiness"], pages=rec.get("page_count"), contract_numbers=", ".join(json.loads(d["contract_numbers"] or "[]")),
                role="root" if d["document_id"] == s["root_id"] else ("linked" if d["family_id"] else "unlinked"),
                flags="; ".join(rec.get("flags", [])),
            ))
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


# ---------------------------------------------------------------- 3. Inspect
def _as_table(pairs: list[tuple[str, object]]) -> None:
    st.table(pd.DataFrame([{"field": k, "value": "" if v is None else str(v)} for k, v in pairs]).set_index("field"))


def inspect(led: Ledger) -> None:
    st.header("Inspect a rate: from the ledger row to the page it came from")
    docs = led._rows("SELECT document_id, filename FROM documents ORDER BY filename")
    with_rows = [d for d in docs if led.observations_for(d["document_id"])]
    if not with_rows:
        st.info("No ledger rows yet.")
        return
    names = {d["filename"]: d["document_id"] for d in with_rows}
    doc_name = st.selectbox("Document", list(names), key="inspect_doc")
    obs = led.observations_for(names[doc_name])
    c1, c2 = st.columns([1, 2])
    which = c1.radio("Show", ["all rows", "counted", "not counted"], horizontal=True, key="inspect_filter")
    needle = c2.text_input("Title contains", key="inspect_search").strip().lower()
    if which == "counted":
        obs = [o for o in obs if o["counted"]]
    elif which == "not counted":
        obs = [o for o in obs if not o["counted"]]
    if needle:
        obs = [o for o in obs if needle in (o["observed_title"] or "").lower()]
    st.caption(f"{len(obs)} rows")
    if not obs:
        return
    table = pd.DataFrame([dict(row=o["obs_id"], title=o["observed_title"], rate=o["rate_as_stated"], currency=o["currency"], unit=o["rate_unit"],
                               period=o["period_raw"], location=o["location_raw"], role=o["canonical_role_id"], band=o["twm_band"] or ("unbanded" if o["canonical_role_id"] else ""),
                               status=o["resolution_status"], counted=bool(o["counted"]), page=o["source_page"]) for o in obs])
    st.dataframe(table, width="stretch", hide_index=True, height=min(400, 40 + 35 * len(obs)))
    labels = {f"{o['obs_id']}: {o['observed_title']} at {o['rate_as_stated']}": o["obs_id"] for o in obs}
    pick = st.selectbox("Row to trace", list(labels), key="inspect_row")
    o = led.observation(labels[pick])
    st.subheader(f"Row {o['obs_id']}: {o['observed_title']}")
    left, right = st.columns([3, 2])
    with right:
        st.markdown("**As stated on the page**")
        _as_table([("quote", o["source_quote"]), ("rate", o["rate_as_stated"]), ("currency", o["currency"]), ("unit", o["rate_unit"]),
                   ("period", o["period_raw"]), ("location label", o["location_raw"]), ("level label", o["level_raw"]),
                   ("extraction confidence", o["extraction_confidence"]), ("scan quality", o["scan_quality"])])
        st.markdown("**Resolution**")
        _as_table([("role", o["canonical_role_id"]), ("band", o["twm_band"] or ("unbanded: no seniority evidence" if o["canonical_role_id"] else "")),
                   ("band from", o["band_source"]), ("technology", o["attr_technology"]), ("location", o["attr_location"]),
                   ("status", o["resolution_status"]), ("resolution confidence", o["resolution_confidence"]),
                   ("counted toward benchmarks", "yes" if o["counted"] else "no"), ("vendor", o["vendor"]), ("client", o["client"])])
        if o["reporting_value"] is not None and o["reporting_currency"] and o["currency"] != o["reporting_currency"]:
            _as_table([(f"in {o['reporting_currency']} (derived)", o["reporting_value"]), ("exchange rate", o["fx_rate"]), ("rate date", o["fx_date"]), ("rate source", o["fx_source"])])
        hist = led.decision_history(o["observed_title"])
        if hist:
            st.markdown("**Decisions on this title**")
            st.dataframe(pd.DataFrame([dict(when=h["decided_at"][:16], by=h["decided_by"], decision=h["decision_json"], reason=h["reason"],
                                            superseded=bool(h["superseded_by"])) for h in hist]), width="stretch", hide_index=True)
    with left:
        shown = render_row(o)
        if shown["kind"] == "pdf":
            st.markdown(f"**Page {shown['page']} of {o['filename']}**, box {tuple(round(v, 1) for v in shown['bbox'])} in PDF points")
            st.image(shown["closeup"], caption="close-up around the row")
            st.image(shown["image"], caption=f"page {shown['page']}, the row boxed")
        else:
            st.markdown(f"**{o['filename']}**: {shown['note']}")
            st.code(shown["quote"] or "(no quote stored)")


# ---------------------------------------------------------------- 2. Queues (step 4) and 4. Decisions to codify (step 5)
def queues(led: Ledger, store: TaxonomyStore, analyst: str) -> None:
    st.header("Queues: every place the system abstained")
    st.info("Built in step 4 of the plan.")


def codify(led: Ledger) -> None:
    st.header("Decisions to codify")
    st.info("Built in step 5 of the plan.")
