# Kickoff brief (paste-free: tell the session to read this file and follow it)

### Brief B: review workbench

You are a worker session on the TWM platform, in the git worktree `workbench` (branch `workbench`). The main session in `C:\Users\kylem\OneDrive - Straight Line Advisory\Desktop\twm-platform` coordinates; Kyle McNamara decides.

Read first, in this order: `CLAUDE.md`; `docs/how-we-build.md`; `.claude/skills/README.md` and the skills `twm-build-task`, `twm-precision-first`, `twm-flag-then-codify`, `twm-data-boundary`, `twm-write-for-kyle`; `docs/architecture-components.md`, the sections "The demo", 1.5 Ledger and "Cross-cutting: Review workbench"; `src/twm/pipeline/ledger.py` (the schema you read from); `work/workbench/intent.md`; `Claude outputs/parallel-agent-plan.md` section 4, stream B, which is your scope and definition of done.

Rules. You commit only on this branch and push it (`git push -u origin workbench`); you never merge or touch `main`. You never edit `docs/action-items.md`, `docs/requirements-and-rationale.md`, `docs/architecture-components.md`, `CLAUDE.md`, anything under `taxonomy/`, `pyproject.toml`, `src/twm/llm.py` or anything under `src/twm/pipeline/` except `ledger.py`, where you add read queries and the methods `resolve_queue_item` and `pending_codification` at the end of the class and never edit existing lines. The workbench writes to the ledger only through `ledger.py` methods and never to the taxonomy CSVs; analyst decisions that should become rules are exported for the main session to codify. Keep `work/workbench/status.md` current at every commit. If blocked on a design decision, write the question there and stop.

Artifact chain: write `work/workbench/spec.md` and `plan.md` first and tell Kyle the plan is ready; write no code until he says go. Build with tests; finish with `review.md`.

Technology: Python and Streamlit (already installed in the shared environment); no Node on this machine; no other new packages without asking in the status file. Data: `ledger.sqlite` in this folder is a copy of the main folder's ledger with the Texas DIR Accenture and Accenture G-Cloud 15 runs in it; work against it. Page images come from `pdfplumber` on the PDFs under `corpus/manifests/v3_downloads/`.

No model calls in this stream. There is no `.env` in this folder and you do not need one.

Writing: plain language, one example per new term; screens are for a consultant first and a CIO second; "contracted rate", never "cap"; "document library", never "corpus".
