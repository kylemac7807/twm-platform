# Kickoff brief (paste-free: tell the session to read this file and follow it)

### Brief A: contract terms

You are a worker session on the TWM platform, in the git worktree `contract-terms` (branch `contract-terms`). The main session in `C:\Users\kylem\OneDrive - Straight Line Advisory\Desktop\twm-platform` coordinates; Kyle McNamara decides.

Read first, in this order: `CLAUDE.md`; `docs/how-we-build.md`; `.claude/skills/README.md` and the skills `twm-build-task`, `twm-precision-first`, `twm-rates-and-money`, `twm-run-a-document`, `twm-write-for-kyle`; `docs/architecture-components.md` sections 1.1, 1.3 and 1.5; `specs/extraction-task-contracts.md`; `work/m2-thin-thread/review.md` (known limits: this task closes several); `work/contract-terms/intent.md`; `Claude outputs/parallel-agent-plan.md` section 4, stream A, which is your scope and definition of done.

Rules. You commit only on this branch and push it (`git push -u origin contract-terms`); you never merge or touch `main`. You never edit `docs/action-items.md`, `docs/requirements-and-rationale.md`, `docs/architecture-components.md`, `CLAUDE.md`, anything under `taxonomy/`, `pyproject.toml`, `src/twm/llm.py`, `src/twm/pipeline/normalize.py`, `src/twm/pipeline/resolve_model.py`, `src/twm/workbench/` or `src/twm/evals/`. In `contracts.py`, `models.py` and `ledger.py` you add; you never rename, remove or edit existing lines; new tables go at the end of `SCHEMA` and new methods at the end of the class. Keep `work/contract-terms/status.md` current at every commit: done, in progress, blocked, questions for Kyle, every field or table added to a shared module, any package you need, any taxonomy rule you want codified. If blocked on a design decision, write the question there and stop.

Artifact chain: write `work/contract-terms/spec.md` and `plan.md` first and tell Kyle the plan is ready; write no code until he says go. Build with tests (`.venv` is the main folder's; the pre-commit hook finds it). Finish with `review.md`, an independent pass.

Model calls: permitted, through `twm.llm` only, on the Texas DIR Accenture family (`corpus/manifests/v3_downloads/v3_gov/081*` to `087*`) and the Michigan Deloitte MiIntegrate contract (find it under `corpus/twm_corpus/`; confirm the file is a real PDF by its first bytes). The `.env` in this folder holds the key: never print, log, copy or mention its contents. Expected 30 to 60 calls per pass; the cache in `.cache/llm` makes repeats free. Hard stop and report if the call log passes 200 calls in a day.

Writing: plain language, one example per new term, no jargon; "contracted rate", never "cap"; "document library", never "corpus" in anything Kyle reads.
