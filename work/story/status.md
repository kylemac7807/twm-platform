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

- **Oct 13, 2026, later — naming round three and Kyle's shortlist.** Kyle ruled out contacting anyone (no note to Akerlof, no enquiry to a domain holder) and did not take to Tukey, Akerlov, Akerloft or Akerledger. Checked Akerlo-shaped coinages at four registries (.com, .ai, .ca, .io; the .io lookup validated against known domains). Shortlist recorded at the top of `docs/story/naming.md`: Akerlo (free on .ai, .ca, .io), Akerlow, Akerlio, Akerla, Akerlon, Kerlof (free on all four), and Bowley as the alternative. **Kyle will decide later.**

- **Oct 13, 2026, later — PDF of the page.** `docs/story/follow-one-rate.pdf` (8 pages, Letter): made by `work/story/print_page.py`, which writes a print copy of the HTML with the three toggles opened and print rules added, then headless Chrome prints it:

  ```
  .venv/Scripts/python.exe work/story/print_page.py docs/story/follow-one-rate.html <print copy.html>
  "C:/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --no-pdf-header-footer --print-to-pdf=docs/story/follow-one-rate.pdf file:///<print copy.html>
  ```

  Regenerate the PDF whenever the HTML is rebuilt.

- **Nov 22, 2026 — the pitch deck narrative.** Kyle chose to work on the pitch before the page. One hybrid deck for an Early Adopter CIO and investors: a shared core of 19 slides, an ending of four slides for the CIO and five for investors, and an appendix. First written in point form at 14 pages, now `docs/story/pitch-deck-narrative-detailed.docx` (built by `work/story/build_pitch_narrative_docx.js`); Kyle found it far too detailed and asked for 6 to 8 pages, so the version for his review is `docs/story/pitch-deck-narrative.docx`, 7 pages (built by `work/story/build_pitch_narrative_short_docx.js`; both scripts need the npm package `docx`), drawn from the Business Plan v1.5, Consortium Approach v1.7, Pitch Deck v1.1, Early Adopter Presentation and the Business Plan deck v1.4 (layout), plus the work done as measured Nov 22. Nine decisions for Kyle at the top. Kyle edits the Word file; the PowerPoint is built from his edited version. Kyle said push it to the private repository (Nov 22), but the auto-mode permission check blocks the push as sensitive information, so Kyle runs the push himself.

- **Nov 22, 2026 — Kyle's nine decisions applied.** `docs/story/pitch-deck-narrative-v2.docx` (7 pages; built by `work/story/build_pitch_narrative_short_docx.js`): fee $1.5MM contingent on more than $10MM of value per client; timeline from today, Business Plan milestones moved eight months; profitability proposed Q2 2028 (Business Plan model) for Kyle to confirm; target market $100MM+; $1MM SAFE now, Series A in the second half of 2027; leadership to be announced; Texas Accenture named; “taught”, not “trained”; TWM throughout. The 7-page first version was open in Word and left as is. `docs/story/why-akerlow.pptx` (built by `work/story/build_why_akerlow_pptx.js` with the pptx skill's theme helper): one slide making the case for the name, from the approved description.

- **Nov 22, 2026 — the pitch deck, first draft.** Kyle asked for the PowerPoint to edit and give feedback on; the first 7-page narrative is deleted at his request (v2 is current). `docs/story/twm-pitch-deck.pptx`, 30 slides in three sections (core 18, a divider and four for the Early Adopter CIO, a divider and six for investors), built by `work/story/build_pitch_deck_pptx.js` (pptxgenjs, the pptx skill's theme helper, and the page-8 images from `collect_facts.py`). Ledger-green and brass theme with Cambria headings; real page-8 images on the follow-one-rate and refuses-to-guess slides; native charts for the unseen-title test, provider headcounts and the run-rate costs. Sources and Kyle's open points (profitability date, the contingent-fee bridge, dashboards not built, workbench screenshot) are in the speaker notes, not on the slides. Checked by exporting every slide from PowerPoint; the skill's validator could not run (python-pptx is not installed in the project environment).

- **Nov 22, 2026 — the pitch deck rebuilt in Kyle's house style.** Kyle found the first draft too AI-generated and did not like the fonts; his decks all use Aptos (Aptos Display headings) on the Office palette with blue 0070C0 highlights. `docs/story/twm-pitch-deck.pptx` is now 28 slides (core 17, a divider and four Early Adopter slides, a divider and five investor slides) built by `work/story/build_pitch_deck_pptx.js` in the style of the Consortium Approach v1.7, Business Plan deck v1.4 and Summary Technical Approach v1.2: their cover, sentence titles, blue section headers with a rule, bold key phrases, navy banners, chevrons and blue line icons (react-icons Phosphor, rendered with sharp). Consortium, context, competition, organization and go-to-market slides reuse Kyle's own wording; corrections applied (no neural weights, no GPT-4o, taught not trained, contracted rate) and his Nov 22 decisions. The financial table is his Business Plan model with years counted from the December 2026 start. US spelling 'labor' and 'Value Acceleration' follow his latest decks. Sources and open points are in the speaker notes.

- **Nov 22, 2026 — the pitch deck, Kyle's edits and feedback applied.** Kyle edited `docs/story/twm-pitch-deck.pptx` directly (committed as found) and gave feedback. It was still open in PowerPoint, so `docs/story/twm-pitch-deck-v2.pptx` (23 slides) is built from his saved file by `work/story/revise_pitch_deck_v2.py` (python-pptx), keeping his edits: the ledger benefit on the executive summary in plain words; the information-gap slide's last bullets finished and its closing box right-sized; the competitive analysis dropped for now (D6); the follow-one-rate, precision-first and technical-approach slides made one slide, 'We have built a working prototype that runs each step on real contracts', with one-line callouts for precision first, in-tenant and own versus rent; the three progress slides made one from his trimmed versions, with the library counts he approved (436 documents, 228 contract sets); the self-citation removed from the market slide, every figure there to be re-sourced (D7); go-to-market condensed. Checked by exporting every slide from PowerPoint.

## Proposed for the action list (main session to apply)

- **A11, update.** "Name the business and the application. Shortlist (Oct 13): Akerlof derivatives, in Kyle's order of interest Akerlo, Akerlow, Akerlio, Akerla, Akerlon, Kerlof, with Bowley as the alternative; every candidate checked at the .com, .ai, .ca and .io registries and searched for collisions (`docs/story/naming.md`). Constraints: no outreach to anyone. Next, once Kyle chooses: register the four domains the same day; trademark database searches (USPTO, CIPO) on the choice and the runner-up; corporate-name search. **Waiting on Kyle.**"

## In progress

- Nothing on naming until Kyle decides. Next conversation: the page, then the narrative.

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
