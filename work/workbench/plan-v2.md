# Plan v2: the workbench rebuilt as a designed web application

**Why a v2.** Kyle saw the Streamlit screens on Oct 13 and rejected them: ugly, and not intuitive. Streamlit cannot produce the shape he wants (a top bar, a work list with the decision beside the evidence, a side panel, a sticky action bar), so the screens are rebuilt; everything underneath (ledger decisions, page renderer, tests, promises, regression replays) stays.

**Decided with Kyle, Oct 13, 2026.** Rebuild in the style of his Vedra prototype (one self-contained page, plain HTML, CSS and JavaScript, no framework, no Node) but with **none of Vedra's colours, words or logo**. Colour system: **Option 1, "Ledger"**: deep teal-green (`#0F6E56`) as the one accent, cool grey canvas (`#F4F6F6`), ink text, conventional status colours (green counted, amber waiting on the analyst, red refused, grey unbanded). Type: **IBM Plex Sans**, with **Plex Mono** for rates and quotes. Nothing to keep out. The tokens are CSS variables so the naming work can re-skin later.

## Shape

- **A small Python service** (`FastAPI`, run with `uvicorn`) exposing the ledger methods as JSON and serving the page, page images and the codification CSV. No network beyond the machine; no model calls.
- **One page** (`src/twm/workbench/static/index.html` + `app.css` + `app.js`) with four screens in a top bar, built around the analyst's loop:
  1. **Overview**: what needs you (titles, places, documents), stat tiles (rows, counted, waiting, contract sets), the open items in the system's words, contract sets as cards.
  2. **Queue**: one list, grouped titles sorted by rows unlocked, with why the system abstained. Click a row: a side panel with the evidence (quote, rate, page close-up) and the decision inline (role, band defaulting to unbanded, technology, reason), **Record and next**. Select several rows for one decision with a count-bearing confirmation. Keyboard: arrows and Enter. Tabs for places and intake.
  3. **Documents**: contract sets as cards; open one to its documents and rate rows; click a row to see the page with the box, the as-stated fields and the resolution.
  4. **Rules**: decisions waiting to be codified, download, mark applied; decision history.
  - A sticky bottom bar: decisions this session, titles left, the analyst's name.

## Steps

| # | Step | Files | Proves it |
|---|---|---|---|
| 1 | The service: JSON endpoints over the existing ledger methods, page-image endpoints over `render.py`, static files | `src/twm/workbench/api.py` | `tests/test_workbench_api.py` with FastAPI's test client on the fixture ledger: a title decision through the API equals the direct call; bulk writes one row per item; name and reason required; page image endpoint returns a PNG with the box; CSV export matches the taxonomy header |
| 2 | The page: tokens, top bar, Overview and Queue with the side panel and keyboard loop | `static/index.html`, `app.css`, `app.js` | Opened on the real ledger in the browser pane; Kyle's reaction |
| 3 | Documents and Rules screens, sticky bar | same | same |
| 4 | Retire Streamlit: delete `app.py`, `screens.py`, the Streamlit screen tests; remove the dependency; update the launch entry and `twm-run-a-document` | | suite passes; `PROMISES.md` regenerates |
| 5 | Review addendum | `review.md` | |

## Run it

```bash
.venv/Scripts/python.exe -m uvicorn twm.workbench.api:app --port 8501 --reload
```

Opens at `http://localhost:8501`. The ledger path comes from `TWM_LEDGER` (default `ledger.sqlite`).

## Risks

- Fonts load from Google Fonts; offline the page falls back to the system sans. Bundle the font files later if that matters for a demo room.
- The page-image endpoint renders on first request; cached after (same cache as before).
- Keyboard-driven lists need care with focus; tested by hand with Kyle in step 2.
