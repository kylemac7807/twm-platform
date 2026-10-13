# Status: the story (stream C)

Worker session in worktree `story`, branch `story`. Updated at every commit. Kyle decides; the main session merges.

## Done

- **Oct 13, 2026 — the visual flow, first version.** `docs/story/follow-one-rate.html`: one self-contained page (opens from disk, no network, 216 KB with the page images embedded). Six stages left to right with the same real row under each (Advanced Systems Engineer, $83.00 per hour, Texas DIR contract DIR-STS-TSS-699, Attachment 2.1, page 8), the review-queue strip, the flagged-row strip ("Operations", $99.50, the model abstained at 0.30), the "coming: savings stacking" box, the seven files as intake labelled them, all 53 rows of the file, and a terms list. Built by two scripts kept beside this file: `collect_facts.py` reads `ledger.sqlite`, renders page 8 with pdfplumber and draws the boxes from the positions the ledger stores; `build_page.py` writes the HTML from those facts. No value on the page was typed by hand. Rebuild after any new run with:

  ```
  .venv/Scripts/python.exe work/story/collect_facts.py ledger.sqlite corpus/manifests/v3_downloads/v3_gov/085_Texas_DIR_Accenture_LLP_rate_exhibit.pdf <image folder> <facts.json>
  .venv/Scripts/python.exe work/story/build_page.py <facts.json> docs/story/follow-one-rate.html
  ```

- **Oct 13, 2026 — the pitch narrative, first draft.** `docs/story/pitch-narrative.md`: one page written from the flow, grounded in the Business Plan v1.5, the Early Adopter Presentation (Nov 10, v2), the Consortium Approach v1.7 and the Pitch Deck v1.1, all four read in full. Ends with the wording the deck revision (D3) should retire. A draft to react to, not a delivery.
- **Oct 13, 2026 — naming options, first draft.** `docs/story/naming.md`: 23 candidate names checked two ways (web search for an existing company or product; the .com registry's own lookup), the five strongest also checked at the .ai and .ca registries; reasoning per name; a shortlist of three (Ratetrail, Ratewright, Quorate); the checks that still need a registrar, a trademark database or counsel. A conversation, not a delivery.

- **Oct 13, 2026, later — naming round two.** Kyle asked for names that carry an argument, the way Typesafe's Jev carries Jevons. 48 more names checked at the .com, .ai and .ca registries by script and the plausible ones searched for collisions; added to `docs/story/naming.md` as "Round two". Shortlist: Akerlof, Tukey, Quetelet; Shewhart and Dantzig as runners-up; the .ai and .ca are free for most, every .com is held since the 1990s.

## In progress

- The naming conversation with Kyle (round two is on the table).

## Questions for Kyle

1. **The page.** Is the six-stage layout the one to keep, or should the row read top to bottom? Is the amount of detail under each stage right for a CIO, or should the ledger values move behind a "show the stored row" toggle?
2. **The flagged row.** "Operations" was chosen because it is the clearest abstention in this contract set. Neither contract set names a city, so there is no place-name flag to show yet; the first one will come from the volume run.
3. **Two intake labels are honest but unflattering** (file 084 called a rate card, file 087 a weak "msa"). The page says so in a note. Keep them visible, or drop the file table from the CIO version?
4. **The narrative.** The four documents give three different Early Adopter fees ($300k in the Early Adopter Presentation, $500k in the Pitch Deck, $1.5 to 2MM in the Business Plan). The narrative leaves the fee out and flags it; which figure stands for the deck revision?
5. **Names.** Does one company name plus a plain "Ledger" product name fit how you want to pitch, or do you want two brands? Of the three on the shortlist, which two are worth a counsel's clearance search? Is "Straight Line" in or out of consideration?

## Observations for the main session (not changed by this stream)

- `band_source` on the Advanced Systems Engineer row reads `title_modifier`, but the band came from the authored mapping row (Kyle's, confidence 1.00), not from a word in the title ("Advanced" is not a seniority modifier in the rules). `normalize.py` files an authored full-title band under the `title_modifier` label. A more precise label (`mapping_row`) would make the ledger self-explanatory. Small; for the main session.
- The review queue stores the model's reasoning cut at 300 characters, so the flagged-row strip shows a sentence that stops mid-way. Worth keeping the full text when the workbench shows it.
- The G-Cloud run queued each unresolved title twice (one entry per rate column, UK and offshore): 14 entries for 7 titles.

## Model calls

None made; none needed.

## Rules followed

Nothing under `src/`, `tests/`, `taxonomy/`, `scripts/`, the action list, the decision log, the design record, `CLAUDE.md` or `pyproject.toml` was edited. Everything new is under `docs/story/` and `work/story/`.
