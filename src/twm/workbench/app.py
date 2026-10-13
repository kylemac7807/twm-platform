"""The review workbench (work/workbench/spec.md). One analyst, one local ledger, no network.

    .venv/Scripts/python.exe -m streamlit run src/twm/workbench/app.py -- --ledger ledger.sqlite

The ledger path can also come from the TWM_LEDGER environment variable (the headless tests use it). Every click re-runs this
script; nothing is held in memory between runs except the analyst's name and the chosen screen. The ledger is the only state.
"""
from __future__ import annotations

import argparse
import os
import sys

import streamlit as st

from twm.pipeline.ledger import Ledger
from twm.taxonomy.store import TaxonomyStore
from twm.workbench import screens

SCREENS = ["Documents", "Queues", "Inspect", "Decisions to codify"]


def ledger_path() -> str:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--ledger", default=None)
    args, _ = ap.parse_known_args(sys.argv[1:])
    return args.ledger or os.environ.get("TWM_LEDGER") or "ledger.sqlite"


@st.cache_resource
def taxonomy() -> TaxonomyStore:
    return TaxonomyStore.load()


def main() -> None:
    st.set_page_config(page_title="TWM review workbench", layout="wide")
    path = ledger_path()
    led = Ledger(path)
    try:
        st.sidebar.title("Review workbench")
        st.sidebar.caption(f"Ledger: `{path}`")
        analyst = st.sidebar.text_input("Your name (recorded on every decision)", key="analyst")
        summary = led.queue_summary()
        open_total = sum(summary.values())
        st.sidebar.markdown("**Open queue items: %d**" % open_total + ("" if not summary else "  \n" + "  \n".join(f"{k}: {v}" for k, v in summary.items())))
        screen = st.sidebar.radio("Screen", SCREENS, key="screen")
        if screen == "Documents":
            screens.documents(led)
        elif screen == "Queues":
            screens.queues(led, taxonomy(), analyst)
        elif screen == "Inspect":
            screens.inspect(led)
        else:
            screens.codify(led)
    finally:
        led.close()


main()
