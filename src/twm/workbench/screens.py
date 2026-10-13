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


# ---------------------------------------------------------------- 2. Queues
def _role_choices(store: TaxonomyStore) -> dict[str, str | None]:
    """Label -> role id, grouped by family in the label so the pick-list reads 'Software Engineering: Software Developer'."""
    fam = {f.family_id: f.name for f in store.families}
    out: dict[str, str | None] = {"no role: leave flagged (recorded)": None}
    for r in sorted(store.roles, key=lambda r: (fam.get(r.family_id, ""), r.name)):
        out[f"{fam.get(r.family_id, r.family_id)}: {r.name}  [{r.role_id}]"] = r.role_id
    return out


def _need_name(analyst: str) -> bool:
    if not (analyst or "").strip():
        st.warning("Type your name in the sidebar first: every decision is recorded with the analyst's name.")
        return True
    return False


def _title_queue(led: Ledger, store: TaxonomyStore, analyst: str) -> None:
    groups = led.title_queue_groups()
    if not groups:
        st.success("No titles waiting.")
        return
    st.caption(f"{len(groups)} titles waiting, {sum(g['rows_unlocked'] for g in groups)} rows not counted until they are decided. "
               "One decision resolves every row with that title for that client; largest first.")
    summary = pd.DataFrame([dict(title=g["title"], client=g["client"], rows_unlocked=g["rows_unlocked"], rows_affected=g["rows_affected"],
                                 documents=", ".join(g["documents"]), why=" | ".join(g["details"])) for g in groups])
    st.dataframe(summary, width="stretch", hide_index=True, height=min(360, 40 + 35 * len(groups)))
    labels = [f"{g['title']}  ({g['client'] or 'no client'}; {g['rows_unlocked']} rows)" for g in groups]
    chosen = st.multiselect("Titles to decide together (pick several only when they are the same role)", labels, key="title_pick")
    picked = [g for g, lab in zip(groups, labels) if lab in chosen]
    if not picked:
        return
    for g in picked:
        with st.expander(f"Evidence for '{g['title']}'", expanded=len(picked) == 1):
            st.markdown("**Why the system abstained:** " + " | ".join(g["details"]))
            st.dataframe(pd.DataFrame([dict(row=e["obs_id"], rate=e["rate_as_stated"], currency=e["currency"], unit=e["rate_unit"], period=e["period_raw"],
                                            location=e["location_raw"], level=e["level_raw"], page=e["source_page"], quote=e["source_quote"]) for e in g["examples"]]),
                         width="stretch", hide_index=True)
            hist = led.decision_history(g["title"])
            if hist:
                st.markdown("Earlier decisions: " + "; ".join(f"{h['decided_at'][:10]} {h['decided_by']}: {h['decision_json']} ({h['reason']})" for h in hist))
    roles = _role_choices(store)
    with st.form("title_decision", clear_on_submit=True):
        role_label = st.selectbox("Role", list(roles), key="role_label")
        band_label = st.selectbox("Band", BAND_CHOICES, index=0, key="band_label", help="Unbanded unless the document gives seniority evidence (Kyle's rule).")
        tech = st.selectbox("Technology tag (optional)", ["none"] + sorted(t.tag for t in store.tech), key="tech_label")
        reason = st.text_area("Reason (required; it becomes part of the rule)", key="reason")
        n_items = sum(len(g["queue_ids"]) for g in picked); n_rows = sum(g["rows_affected"] for g in picked)
        confirm = st.checkbox(f"Apply this one decision to {len(picked)} title(s), {n_items} queue item(s), {n_rows} ledger row(s)", key="confirm_bulk") if len(picked) > 1 else True
        go = st.form_submit_button("Record decision")
    if go:
        if _need_name(analyst):
            return
        if not reason.strip():
            st.error("A decision needs a reason.")
            return
        if not confirm:
            st.error("Tick the confirmation to apply one decision to several titles.")
            return
        band = None if band_label == BAND_CHOICES[0] else band_label
        ids = led.decide_title([q for g in picked for q in g["queue_ids"]], role_id=roles[role_label], band=band, reason=reason,
                               decided_by=analyst, technology=None if tech == "none" else tech)
        st.success(f"Recorded {len(ids)} decision(s) by {analyst.strip()}; the affected rows are updated and the titles leave the queue. "
                   "Mapping rules are appended to the taxonomy from the 'Decisions to codify' screen.")
        st.rerun()


def _location_queue(led: Ledger, analyst: str) -> None:
    items = led.queue_items("location")
    if not items:
        st.success("No place names waiting.")
        return
    st.caption("The platform never classifies a place name. You decide once, for this client, with a reason; later occurrences are lookups once the rule is codified.")
    df = pd.DataFrame([dict(id=i["id"], title=i["item"], document=i["filename"], why=i["detail"], client=led._client_of(i["document_id"])) for i in items])
    st.dataframe(df, width="stretch", hide_index=True)
    labels = {f"{i['id']}: {i['item']} ({i['detail']})": i["id"] for i in items}
    chosen = st.multiselect("Items to decide together (same place, same client)", list(labels), key="loc_pick")
    if not chosen:
        return
    with st.form("location_decision", clear_on_submit=True):
        cls = st.radio("Classification for this client", ["onshore", "nearshore", "offshore"], horizontal=True, key="loc_cls")
        reason = st.text_area("Reason (required)", key="loc_reason")
        go = st.form_submit_button("Record decision")
    if go:
        if _need_name(analyst):
            return
        if not reason.strip():
            st.error("A decision needs a reason.")
            return
        led.decide_location([labels[c] for c in chosen], classification=cls, reason=reason, decided_by=analyst)
        st.success("Recorded; the flagged rows now carry the location. The rule goes to the taxonomy from 'Decisions to codify'.")
        st.rerun()


def _other_queue(led: Ledger, kind: str, analyst: str) -> None:
    items = led.queue_items(kind)
    if not items:
        st.success(f"No {kind} items waiting.")
        return
    st.dataframe(pd.DataFrame([dict(id=i["id"], document=i["filename"], item=i["item"], detail=i["detail"]) for i in items]), width="stretch", hide_index=True)
    if kind != "intake":
        st.caption("Extraction and reading notes are information for the analyst; the pipeline re-run is the action. Nothing to decide here yet.")
        return
    labels = {f"{i['id']}: {i['item']}: {i['detail']}": i for i in items}
    pick = st.selectbox("Item", list(labels), key="intake_pick")
    item = labels[pick]
    with st.form("intake_decision", clear_on_submit=True):
        if "classification" in (item["detail"] or ""):
            cls = st.selectbox("Document type", ["msa", "sow", "amendment", "rate_card", "sla", "solicitation", "template", "invoice", "timesheet", "other"], key="intake_cls")
            decision = {"doc_class": cls}
        else:
            link = st.radio("Suggested contract-set link", ["confirm", "reject"], horizontal=True, key="intake_link")
            decision = {"link": link}
        reason = st.text_area("Reason (required)", key="intake_reason")
        go = st.form_submit_button("Record decision")
    if go:
        if _need_name(analyst):
            return
        if not reason.strip():
            st.error("A decision needs a reason.")
            return
        led.decide_intake(item["id"], decision=decision, reason=reason, decided_by=analyst)
        st.success("Recorded.")
        st.rerun()


def queues(led: Ledger, store: TaxonomyStore, analyst: str) -> None:
    st.header("Queues: every place the system abstained")
    summary = led.queue_summary()
    tabs = st.tabs([f"Titles ({summary.get('title', 0)})", f"Places ({summary.get('location', 0)})", f"Intake ({summary.get('intake', 0)})",
                    f"Extraction ({summary.get('extraction', 0)})", f"Reading ({summary.get('reading', 0)})"])
    with tabs[0]:
        _title_queue(led, store, analyst)
    with tabs[1]:
        _location_queue(led, analyst)
    with tabs[2]:
        _other_queue(led, "intake", analyst)
    with tabs[3]:
        _other_queue(led, "extraction", analyst)
    with tabs[4]:
        _other_queue(led, "reading", analyst)


# ---------------------------------------------------------------- 4. Decisions to codify
def codification_csv(rows: list[dict]) -> str:
    """The pending decisions as CSV in the exact column order of the taxonomy file they append to (decision_id dropped)."""
    if not rows:
        return ""
    return pd.DataFrame(rows).drop(columns=["decision_id"]).to_csv(index=False, lineterminator="\n")


def codify(led: Ledger) -> None:
    st.header("Decisions to codify")
    st.caption("A decision becomes a permanent rule only when it is appended to the taxonomy files (the main session does that with the "
               "twm-change-the-taxonomy skill; the workbench never writes to taxonomy/). Download the rows, append them, then mark them applied.")
    pend = led.pending_codification()
    for kind, label, fname in (("title_mappings", "Title mappings", "title_mappings_to_append.csv"),
                               ("location_rules", "Location rules", "location_rules_to_append.csv")):
        rows = pend[kind]
        st.subheader(f"{label}: {len(rows)} waiting")
        if not rows:
            continue
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        st.download_button(f"Download {fname}", codification_csv(rows), file_name=fname, mime="text/csv", key=f"dl_{kind}")
        labels = {f"{r['decision_id']}: {r.get('observed_title') or r.get('place')}": r["decision_id"] for r in rows}
        pick = st.multiselect("Rows appended to the taxonomy", list(labels), key=f"applied_{kind}")
        if st.button("Mark applied", key=f"mark_{kind}"):
            if not pick:
                st.error("Pick the rows that were appended.")
            else:
                n = sum(led.mark_applied(labels[p]) for p in pick)
                st.success(f"{n} decision row(s) marked applied.")
                st.rerun()
