# Status: the story (stream C)

Worker session in worktree `story`, branch `story`. Updated at every commit. Kyle decides; the main session merges.

## Done

- **Oct 13, 2026 — the visual flow, first version.** `docs/story/follow-one-rate.html`: one self-contained page (opens from disk, no network, 216 KB with the page images embedded). Six stages left to right with the same real row under each (Advanced Systems Engineer, $83.00 per hour, Texas DIR contract DIR-STS-TSS-699, Attachment 2.1, page 8), the review-queue strip, the flagged-row strip ("Operations", $99.50, the model abstained at 0.30), the "coming: savings stacking" box, the seven files as intake labelled them, all 53 rows of the file, and a terms list. Built by two scripts kept beside this file: `collect_facts.py` reads `ledger.sqlite`, renders page 8 with pdfplumber and draws the boxes from the positions the ledger stores; `build_page.py` writes the HTML from those facts. No value on the page was typed by hand. Rebuild after any new run with:

  ```
  .venv/Scripts/python.exe work/story/collect_facts.py ledger.sqlite corpus/manifests/v3_downloads/v3_gov/085_Texas_DIR_Accenture_LLP_rate_exhibit.pdf <image folder> <facts.json>
  .venv/Scripts/python.exe work/story/build_page.py <facts.json> docs/story/follow-one-rate.html
  ```

## In progress

- The pitch narrative (`docs/story/pitch-narrative.md`) and the naming options (`docs/story/naming.md`): first drafts to react to, not deliveries.

## Questions for Kyle

1. **The page.** Is the six-stage layout the one to keep, or should the row read top to bottom? Is the amount of detail under each stage right for a CIO, or should the ledger values move behind a "show the stored row" toggle?
2. **The flagged row.** "Operations" was chosen because it is the clearest abstention in this contract set. Neither contract set names a city, so there is no place-name flag to show yet; the first one will come from the volume run.
3. **Two intake labels are honest but unflattering** (file 084 called a rate card, file 087 a weak "msa"). The page says so in a note. Keep them visible, or drop the file table from the CIO version?

## Observations for the main session (not changed by this stream)

- `band_source` on the Advanced Systems Engineer row reads `title_modifier`, but the band came from the authored mapping row (Kyle's, confidence 1.00), not from a word in the title ("Advanced" is not a seniority modifier in the rules). `normalize.py` files an authored full-title band under the `title_modifier` label. A more precise label (`mapping_row`) would make the ledger self-explanatory. Small; for the main session.
- The review queue stores the model's reasoning cut at 300 characters, so the flagged-row strip shows a sentence that stops mid-way. Worth keeping the full text when the workbench shows it.
- The G-Cloud run queued each unresolved title twice (one entry per rate column, UK and offshore): 14 entries for 7 titles.

## Model calls

None made; none needed.

## Rules followed

Nothing under `src/`, `tests/`, `taxonomy/`, `scripts/`, the action list, the decision log, the design record, `CLAUDE.md` or `pyproject.toml` was edited. Everything new is under `docs/story/` and `work/story/`.
