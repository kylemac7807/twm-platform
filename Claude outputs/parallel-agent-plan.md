# Running two Claude Code sessions in parallel: the plan

**Phase 1 output, October 6, 2026.** Written by Claude Code for Kyle. Nothing in the project has been changed to make it: no branches, no worktrees, no code. It proposes; Kyle decides. Phase 2 (setting it up) starts only on his approval.

## 1. What this is, in one paragraph

Today one Claude Code session works in the project folder. The idea is to run two at once, each in its own copy of the project (a git "worktree": a second folder on disk that shares the same version history, so each session can commit on its own branch without touching the other's files). The main session, the one Kyle talks to in this folder, stays the coordinator: it keeps the action list and the decision log, owns the taxonomy, merges each worker's branch when its work is done and tested, and runs the walkthroughs with Kyle. Example: while one worker teaches the pipeline to read the commercial terms of a master agreement, the other builds the analyst's screens, and neither waits for the other.

## 2. What is open that involves code

From `docs/action-items.md` and `work/m2-thin-thread/review.md`, mapped to the files each item would touch.

| Item | What it is | Files it touches |
|---|---|---|
| B16 (second row of that number) | M2 follow-ups: SOW and MSA term extraction against the real model; vendor and contract number from intake into ledger rows; year-by-year escalation rows; a reference exchange-rate source; AI Search later | `extract.py`, `run.py`, `ingest.py`, `contracts.py`, `ledger.py`, new `fx.py` |
| Workbench | The analyst's web screens (design record, cross-cutting: review workbench, decided Oct 6): documents and families, the queues, click-through to the source page | new `src/twm/workbench/`, reads the ledger, small additions to `ledger.py` |
| M3 evaluation harness | Field-level scoring against hand-verified answer sheets (`specs/eval-harness-spec.md`), gold-set tooling, Claude-versus-GPT baseline later | new `src/twm/evals/`, reads `contracts.py` and `evals/gold/` |
| B17 (second row) | Hand-verify the two drafted answer sheets | a person; tooling to export a draft to Word for marking belongs with M3 |
| B16 to B19 (first rows: SFIA scrub) | Remove the SFIA field and column, rename the crosswalk scheme, reword standing docs and skills, rename the 13 G-Cloud 15 files | `taxonomy/*.csv`, `src/twm/taxonomy/models.py`, `heldout.py`, `acceptance.py`, `contracts.py`, `ingest.py`, `CLAUDE.md`, `docs/`, `.claude/skills/`, `corpus/gc15_ratecards/` |
| A9 | Raw-contract walkthrough with Kyle | nothing; a conversation |

Note: the action list now has two B16 rows and two B17 rows (Cowork numbered the SFIA items into numbers already used). The main session renumbers the SFIA items B20 to B23 in Phase 2.

## 3. Hotspots: files more than one stream would want

| File | Why it is shared | Rule |
|---|---|---|
| `src/twm/pipeline/contracts.py` (task contracts) | Every extractor and the evaluation harness read these shapes | Add fields and classes only; never rename or remove; list every addition in the status file |
| `src/twm/pipeline/models.py` (DocumentRecord, SourceRef) | Intake, ledger and workbench all use them | Same: additive only |
| `src/twm/pipeline/ledger.py` (the SQLite schema) | Terms extraction wants new tables; the workbench wants new queries and a way to record a decision | New tables go at the end of `SCHEMA`; new methods at the end of the class; no existing line is edited |
| `src/twm/pipeline/normalize.py`, `resolve_model.py` | The normalizer is the most intricate code and is tied to the taxonomy | Main session only |
| `taxonomy/*.csv` | Changing a CSV regenerates `REPORT.md`; two streams doing that conflict every time | Main session only. Workers never edit the taxonomy; a worker that needs a rule change writes it in its status file for the main session |
| `docs/action-items.md`, `docs/requirements-and-rationale.md`, `docs/architecture-components.md`, `CLAUDE.md` | One running list, one decision log, one design record | Main session only; workers propose in `work/<task>/status.md` |
| `pyproject.toml` | The shared Python environment is installed from it | Main session only; a worker that needs a package asks in its status file. The one package the workbench needs is added before the worktrees are created |
| `src/twm/llm.py` | The one model wrapper | Main session only unless a stream finds a bug, which goes in the status file |

The SFIA scrub touches `models.py`, `contracts.py` and `ingest.py`, which stream A also edits. So the scrub is done first, by the main session, and the worktrees branch from the commit after it. That removes the only predictable conflict.

## 4. The streams

Two now. A third (the evaluation harness) is ready to start the day either finishes, or now if Kyle wants three sessions.

### Stream A: contract terms (`work/contract-terms/`, branch `contract-terms`)

**Problem.** The pipeline reads rate tables but not the words around them. A master agreement's financial provisions (discounts, escalation, invoicing terms, most-favoured-customer clauses), the parties, the term and the contract number are what a vendor challenge is argued from, and the code to extract them (`extract_sow`) has never been run against the real model.

**Scope, in order.**
1. Run `extract_sow` against the real model on the Texas DIR Accenture master agreement (081) and Exhibit 2 financial provisions (084), then the Michigan Deloitte MiIntegrate contract (Kyle's hand-downloaded original). Fix what breaks, the way M2 fixed the rate-card path: schema in the prompt, every quoted term verified on the page, abstain rather than guess.
2. Route documents classified `sow`, `msa` and `amendment` through it in `run.py`; store the results in two new ledger tables, `contract_terms` and `named_resources`, each row with page, box and quote.
3. Intake derives the vendor (counterparty) and contract number from the first pages; the run passes them into every observation row, with the command-line `--vendor` and `--client` kept as overrides. `DocumentRecord` gains `counterparty_guess` (additive).
4. Escalation rows: the Texas exhibit prices eight contract years; today only year 1 is kept. One observation per title per period, with `period_raw` set, kept behind a flag so the run report still reads clearly.
5. If time remains: a reference exchange-rate module (`fx.py`) that reads a Bank of Canada daily rate for a date and feeds the existing derived column. No conversion is ever applied silently.

**Owns.** `src/twm/pipeline/extract.py`, `run.py`, `ingest.py`, `contracts.py` (additive), `ledger.py` (additive), `models.py` (additive), new `fx.py`, the tests for each, `work/contract-terms/`, new draft answer sheets in `evals/gold/`.

**Off limits.** Everything in section 3 marked main session only; `normalize.py`; `resolve_model.py`; `src/twm/workbench/`; `src/twm/evals/`.

**Done when.** A plain run report on the Texas family lists the parties, contract number, term and every commercial term found, each traceable to a page; the Michigan Deloitte contract goes through the same code unchanged; the ledger holds the terms; tests pass; `work/contract-terms/review.md` is written; the status file lists every field added to a shared module.

**Model spend.** Permitted on those three documents only. Expected 30 to 60 calls per full pass; the content-hash cache makes repeat runs free. Hard stop and report to Kyle if the call log passes 200 calls in a day. (Kyle's $100 monthly limit in the console is the backstop.) Needs `.env`: yes.

### Stream B: review workbench (`work/workbench/`, branch `workbench`)

**Problem.** The only place a person touches the system is a set of screens that does not exist. Today the queues and the traced rows live in a SQLite file and a run report. The demo for an Early Adopter CIO runs inside the workbench (design record, decision 3), so it is on the critical path to the demo, and the analyst's decisions have nowhere to be recorded.

**Scope, in order.** Three of the workbench's four jobs; the executive views wait for findings, which do not exist yet.
1. Documents and families: every registered document, its class, confidence, evidence, readiness and family, with flags shown as the system wrote them.
2. The queues: every open item by kind (title, location, intake, extraction, reading). Resolving a title records a mapping decision in the ledger with the analyst's name, the role, the band or "unbanded", and a written reason; the queue item closes. Locations and document links the same way. The decision is **not** written to the taxonomy CSVs by the workbench: it writes an export, "decisions to codify", that the main session applies with the `twm-change-the-taxonomy` skill. Resolve once, by a human, with an audit record designed so a second reviewer role can be added later without changing the data (decision 2).
3. Inspect: click any ledger row and see the source page as an image with the box highlighted, the quote, and the row's resolution and confidence. Web-page sources show the table row and column instead.

**Technology.** Python only (no Node on this machine). Recommendation: Streamlit, one dependency, screens in days rather than weeks, runs on Kyle's machine and later in TWM's Azure environment. It is a prototype for the consultants and the demo; the production workbench is rebuilt in Azure. If Kyle prefers a plainer stack, Flask is the alternative at roughly three times the code.

**Owns.** New `src/twm/workbench/`, `tests/test_workbench.py`, `ledger.py` (additive: read queries, `resolve_queue_item`, `pending_codification`), `work/workbench/`.

**Off limits.** The pipeline modules (stream A's), the taxonomy, the model wrapper. The workbench reads the ledger and writes only through `ledger.py` methods.

**Done when.** Kyle can open the workbench on the existing `ledger.sqlite`, see the Texas and G-Cloud families, work the 16 open title items and one location item, see each decision land in the ledger with his name and reason, click the traced Texas row and see page 8 with the box drawn; tests cover the ledger methods and the codification export; review written.

**Model spend.** None. Needs `.env`: no. Needs a copy of `ledger.sqlite` from the main folder (the file is not in version history; the main session copies it in Phase 2).

### Stream C, later: evaluation harness (`work/eval-harness/`, branch `eval-harness`)

`src/twm/evals/metrics.py` per the spec (field-level precision and recall, precision-weighted), a gold-set loader, a comparison report, and the tool that exports a draft answer sheet to Word so Kyle or an analyst can mark it (B17). No model calls until the Claude-versus-GPT baseline, which is a separate decision. No hotspots; it could run as a third stream now. Recommendation: not yet. Two streams produce two plans, two reviews and two merges for Kyle to read; three is a lot for the first attempt.

## 5. What the main session keeps

The SFIA scrub (first), the hook fix (below), the taxonomy, the action list and decision log, merges, the A9 walkthrough with Kyle, and the memory of the project. Also: fixing the duplicate numbers in the action list, adding the workbench dependency, and copying `.env` and `ledger.sqlite` into the worktrees that need them.

## 6. Two things that must be fixed before any worktree exists

**The test hook breaks in a worktree.** `scripts/git-hooks/pre-commit` runs the tests with `$ROOT/.venv/Scripts/python.exe`. A worktree has no `.venv`, so the hook falls back to whatever `python` is on the path, the tests fail to import, and every commit is refused. Worse, the package is installed in "editable" mode, which points the environment at the **main** folder's `src/`: a worker's tests would silently run against the main folder's code, not its own. Both fixed by three lines in the hook:

```
COMMON="$(git rev-parse --git-common-dir)"       # the main repository's .git, even from a worktree
MAIN="$(cd "$COMMON/.." && pwd)"
PY="$MAIN/.venv/Scripts/python.exe"
export PYTHONPATH="$ROOT/src"                     # this checkout's code wins over the editable install
```

Hooks live in the shared `.git`, so one installed copy serves every worktree. Tested by committing in a throwaway worktree before any worker starts.

**Secrets and the ledger do not travel.** `.env` and `ledger.sqlite` are excluded from version history, so a new worktree has neither. The main session copies them as files (never reading or printing the key) into the worktrees that need them: `.env` to stream A, `ledger.sqlite` to stream B.

## 7. Where the worktrees go

Kyle's prompt said sibling folders on the Desktop (`twm-wt-<name>`). Recommendation: put them **outside OneDrive**, at `C:\Users\kylem\twm-worktrees\contract-terms` and `...\workbench`. OneDrive syncs every file a test run or a git operation writes; a second and third checkout doubles and triples that, and worktree folders on the Desktop look like extra projects. The version history is unaffected: a worktree's `.git` is a pointer to the main folder's repository, which stays in OneDrive and on GitHub. If Kyle prefers them beside the project, the only cost is sync noise.

## 8. Rules every worker follows (the eight changes, plus two)

1. **Merging is the main session's job.** A worker commits on its branch and pushes it to GitHub; it never merges into `main` or touches another branch. The main session merges after running the tests on the merged result, on Kyle's say-so per stream.
2. **Workers never edit** `docs/action-items.md`, `docs/requirements-and-rationale.md`, `docs/architecture-components.md`, `CLAUDE.md`, `taxonomy/`, `pyproject.toml` or `src/twm/llm.py`. Proposals go in `work/<task>/status.md`, which the worker updates at every commit: done, in progress, blocked, questions for Kyle, additions to shared modules, packages needed, rules to codify.
3. **The artifact chain applies**: `work/<task>/intent.md` (drafted below, accepted by Kyle with this plan), `spec.md`, `plan.md` (Kyle reads it before code is written), build with tests, `review.md`. The `twm-build-task` skill in `.claude/skills/` is the procedure.
4. The hook fix (section 6) lands before the worktrees are created.
5. `.env` is copied by the main session, by file copy only, into worktrees permitted to call the model. A worker never creates, prints, logs or moves it.
6. Shared modules (`contracts.py`, `models.py`, `ledger.py`): additive only, listed in the status file. Taxonomy changes go to the main session as a request.
7. Two streams to start; the third when one finishes.
8. Model spend is stated in each brief: which documents, an expected range, a hard stop. Stream B has none.
9. Every brief points the worker at `CLAUDE.md`, `docs/how-we-build.md`, `.claude/skills/README.md` and the relevant design-record section, because a worker session starts with no memory of this conversation. Kyle's personal skills (`sdlc-*`, `writing-for-kyle`) load in every folder on this machine; the project skills come with the checkout.
10. A worker that is blocked for more than one working step writes the question in its status file and stops; it does not guess past a design decision.

## 9. Phase 2, if approved: what happens and who does it

Main session (Claude Code, this folder), in order:
1. SFIA scrub in code, taxonomy and standing docs (B16 to B19, renumbered B20 to B23); commit; push.
2. Hook fix; prove it in a throwaway worktree; commit; push.
3. Add `streamlit` to `pyproject.toml`, install it into the shared environment; commit.
4. `git worktree add C:\Users\kylem\twm-worktrees\contract-terms -b contract-terms` and the same for `workbench`.
5. Copy `.env` into `contract-terms`, `ledger.sqlite` and the `.cache/llm` folder into both (the cache makes stream A's repeat calls free).
6. Write `work/contract-terms/intent.md` and `work/workbench/intent.md` from the drafts below, on `main`, so both worktrees inherit them.
7. Record the parallel-session practice in `docs/how-we-build.md` (it is currently listed under "deferred") and the decision log; update the action list with the two streams.

Kyle, once:
1. In the Claude app's Code tab, start a new session and choose the folder `C:\Users\kylem\twm-worktrees\contract-terms`. Paste kickoff brief A as the first message.
2. Same for `...\workbench` with brief B.
3. Read each stream's `plan.md` when the worker says it is ready, in the worker's own session, and say "go".
4. When a worker reports done, tell the main session to merge it.

Time: the main session's steps are about an hour of work, most of it the SFIA scrub.

## 10. Kickoff briefs (paste as the first message in the worker's session)

### Brief A: contract terms

> You are a worker session on the TWM platform, in the git worktree `contract-terms` (branch `contract-terms`). The main session in `C:\Users\kylem\OneDrive - Straight Line Advisory\Desktop\twm-platform` coordinates; Kyle McNamara decides.
>
> Read first, in this order: `CLAUDE.md`; `docs/how-we-build.md`; `.claude/skills/README.md` and the skills `twm-build-task`, `twm-precision-first`, `twm-rates-and-money`, `twm-run-a-document`, `twm-write-for-kyle`; `docs/architecture-components.md` sections 1.1, 1.3 and 1.5; `specs/extraction-task-contracts.md`; `work/m2-thin-thread/review.md` (known limits: this task closes several); `work/contract-terms/intent.md`; `Claude outputs/parallel-agent-plan.md` section 4, stream A, which is your scope and definition of done.
>
> Rules. You commit only on this branch and push it (`git push -u origin contract-terms`); you never merge or touch `main`. You never edit `docs/action-items.md`, `docs/requirements-and-rationale.md`, `docs/architecture-components.md`, `CLAUDE.md`, anything under `taxonomy/`, `pyproject.toml`, `src/twm/llm.py`, `src/twm/pipeline/normalize.py`, `src/twm/pipeline/resolve_model.py`, `src/twm/workbench/` or `src/twm/evals/`. In `contracts.py`, `models.py` and `ledger.py` you add; you never rename, remove or edit existing lines; new tables go at the end of `SCHEMA` and new methods at the end of the class. Keep `work/contract-terms/status.md` current at every commit: done, in progress, blocked, questions for Kyle, every field or table added to a shared module, any package you need, any taxonomy rule you want codified. If blocked on a design decision, write the question there and stop.
>
> Artifact chain: write `work/contract-terms/spec.md` and `plan.md` first and tell Kyle the plan is ready; write no code until he says go. Build with tests (`.venv` is the main folder's; the pre-commit hook finds it). Finish with `review.md`, an independent pass.
>
> Model calls: permitted, through `twm.llm` only, on the Texas DIR Accenture family (`corpus/manifests/v3_downloads/v3_gov/081*` to `087*`) and the Michigan Deloitte MiIntegrate contract (find it under `corpus/twm_corpus/`; confirm the file is a real PDF by its first bytes). The `.env` in this folder holds the key: never print, log, copy or mention its contents. Expected 30 to 60 calls per pass; the cache in `.cache/llm` makes repeats free. Hard stop and report if the call log passes 200 calls in a day.
>
> Writing: plain language, one example per new term, no jargon; "contracted rate", never "cap"; "document library", never "corpus" in anything Kyle reads.

### Brief B: review workbench

> You are a worker session on the TWM platform, in the git worktree `workbench` (branch `workbench`). The main session in `C:\Users\kylem\OneDrive - Straight Line Advisory\Desktop\twm-platform` coordinates; Kyle McNamara decides.
>
> Read first, in this order: `CLAUDE.md`; `docs/how-we-build.md`; `.claude/skills/README.md` and the skills `twm-build-task`, `twm-precision-first`, `twm-flag-then-codify`, `twm-data-boundary`, `twm-write-for-kyle`; `docs/architecture-components.md`, the sections "The demo", 1.5 Ledger and "Cross-cutting: Review workbench"; `src/twm/pipeline/ledger.py` (the schema you read from); `work/workbench/intent.md`; `Claude outputs/parallel-agent-plan.md` section 4, stream B, which is your scope and definition of done.
>
> Rules. You commit only on this branch and push it (`git push -u origin workbench`); you never merge or touch `main`. You never edit `docs/action-items.md`, `docs/requirements-and-rationale.md`, `docs/architecture-components.md`, `CLAUDE.md`, anything under `taxonomy/`, `pyproject.toml`, `src/twm/llm.py` or anything under `src/twm/pipeline/` except `ledger.py`, where you add read queries and the methods `resolve_queue_item` and `pending_codification` at the end of the class and never edit existing lines. The workbench writes to the ledger only through `ledger.py` methods and never to the taxonomy CSVs; analyst decisions that should become rules are exported for the main session to codify. Keep `work/workbench/status.md` current at every commit. If blocked on a design decision, write the question there and stop.
>
> Artifact chain: write `work/workbench/spec.md` and `plan.md` first and tell Kyle the plan is ready; write no code until he says go. Build with tests; finish with `review.md`.
>
> Technology: Python and Streamlit (already installed in the shared environment); no Node on this machine; no other new packages without asking in the status file. Data: `ledger.sqlite` in this folder is a copy of the main folder's ledger with the Texas DIR Accenture and Accenture G-Cloud 15 runs in it; work against it. Page images come from `pdfplumber` on the PDFs under `corpus/manifests/v3_downloads/`.
>
> No model calls in this stream. There is no `.env` in this folder and you do not need one.
>
> Writing: plain language, one example per new term; screens are for a consultant first and a CIO second; "contracted rate", never "cap"; "document library", never "corpus".

## 11. Draft intents (Kyle accepts these with the plan; the worker starts from them)

**`work/contract-terms/intent.md`.** A vendor challenge is argued from the contract's words, not only its rate table: the discount schedule, the escalation clause, the invoicing terms, who the parties are and which master agreement governs. The pipeline reads rate tables well (M2) and reads none of this. Teach it to read the commercial terms of a master agreement, statement of work or amendment with the same discipline as the rate tables: every term quoted from the page with its position, nothing guessed, abstentions explained; store them in the ledger beside the rates; and stop asking the operator to type the vendor and contract number, which the document states. Prove it on the Texas DIR Accenture agreement and the Michigan Deloitte contract. Precision first: a term the model is not sure of is flagged, never recorded.

**`work/workbench/intent.md`.** The platform abstains on purpose and asks a person: titles it could not place, places it would not classify, documents it would not link, extractions it did not trust. Today those questions sit in a database table nobody can see, and the one person who could answer them has no screen to do it on. Build the first version of the review workbench: see the documents and their families as intake sorted them, work the queues and record each decision with a reason so it is never asked again, and click any rate through to the page it came from with the spot highlighted. The demo for an Early Adopter CIO will run on these screens, so they must be honest: what the system found, what it declined to decide, and why.

## 12. Risks

- **Kyle's reading load doubles.** Two plans, two reviews, two sets of questions. Mitigation: streams write short plans; the main session summarizes both status files at every session start.
- **Both streams add to `ledger.py`.** Additive-only rule and separate table and method names keep the merge mechanical; the main session resolves any overlap.
- **Worker sessions have no memory of the decisions.** The briefs and the committed docs carry them; a worker that contradicts a decision is caught at plan review and at merge.
- **Streamlit is a prototype choice.** Right for the next two months; it will be rebuilt for Azure. Recorded as such so nobody mistakes it for the product.
- **OneDrive.** If the worktrees stay inside it, expect sync noise and occasional file-lock errors during test runs.

## 13. For Kyle to decide

1. Approve the two streams and their scope (section 4), or change them.
2. Worktree location: outside OneDrive (recommended) or beside the project.
3. Streamlit for the workbench prototype (recommended) or Flask.
4. Stream A's spend rule: the three documents, hard stop at 200 calls a day. Change the numbers if you want.
5. Start stream C now as a third session, or wait (recommended: wait).

On "approved", the main session runs Phase 2, section 9, and reports back with the two folders ready and the briefs to paste.
