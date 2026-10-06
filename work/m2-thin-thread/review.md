# Review: M2, the thin thread

**Independent review pass, October 6, 2026** (step 8 of the plan; `docs/how-we-build.md`). Written after steps 1 to 7 were built and run. Findings are grouped by what was fixed during the review, what is left and why, and what Kyle should look at.

## What was built and proven

| Stage | Proven by |
|---|---|
| Intake | Seven Texas DIR Accenture files register as one family under contract DIR-STS-TSS-699; a fake PDF (HTML viewer page) is caught by content sniffing; the 3-page key-personnel attachment is flagged as a weak classification rather than guessed |
| Reading | The pricing exhibit's 111-row rate table on page 8 comes through as clean cells; every line carries page and bounding box; a text-less PDF is graded `none` and routed to OCR |
| Model wrapper | Validation, retry at most twice then flag, content-hash cache, call log; offline tests with a fake model |
| Extraction | Real run: 6 model calls, 53 rate rows kept, 0 rejected by page verification, 6 abstentions explained in the model's words; a test proves an invented number ($999.99) is rejected |
| Normalization model step | Known titles never call the model; the model may not pick outside the candidates, set a band without stated seniority, or classify a place name the rules flagged |
| Ledger | Append and supersede; confidence and scan quality gate what counts; currency conversion is a derived column with the reference rate and date |
| End-to-end | `python -m twm.pipeline.run` on the family: 53 rows, 48 resolved (23 unbanded on purpose), 2 titles to the queue, 3 dual-grade titles ambiguous by design, 48 counted; one row traced to page 8, box (65, 128, 554, 133) |

Tests: 118 at the end of the run (the step 5 to 7 commit message said 127; 118 is the measured count).

## Fixed during build and review

1. **The SDK rejects `temperature`.** Current models take no sampling parameters; the wrapper now relies on the content-hash cache for determinism and controls depth with `output_config.effort` (low for extraction). The first real run failed on this before any model answered.
2. **The model omitted `source_ref.document_id`**, a value only the pipeline knows; every valid answer was rejected by validation. The pipeline now fills it and the prompt carries the exact JSON schema. Second run: 6 of 6 validated.
3. **Placeholder tables wasted calls.** Nine of ten tables in the pricing exhibit hold only "$ -" totals. Sectioning now skips tables without real money cells: 10 calls became 6.
4. **The G-Cloud web page classified as a service-level document**: its rate table sits below a long navigation block, outside the first 20,000 characters. Web pages now read 120,000 characters with navigation stripped, and "UK Rate / Offshore Rate" is a rate-card signal.
5. **The model could override a flagged place name** with an onshore/offshore guess. Blocked: a place the rules flagged stays with the analyst (Kyle, Sept 19).

## Known limits, deliberately left

- **Year-1 rates only.** The exhibit prices eight contract years; one row per title per year would be ~900 rows per call. Escalation columns become a follow-up (one row per title with the period rates as a list, or one call per period).
- **Exhibit 2 (084) yields no rows, correctly.** It is prose financial provisions with no rate table; it is a SOW/MSA term-extraction target, which is the next task (`extract_sow` exists and is untested against the real model).
- **Document meta is empty from table sections.** Issuer, counterparty and contract number are known from intake, not from the model; the run passes vendor and client explicitly. Wiring intake's contract numbers into the ledger row is a small follow-up.
- **Similarity is token overlap**, not embeddings. Adequate for candidates; Azure AI Search replaces it behind the same function.
- **No currency conversion rates are fetched.** The derived column works (tested) but the run passes `fx=None`; a reference-rate source (Bank of Canada) is a follow-up before any cross-currency benchmark.
- **The answer sheet is a draft produced by the pipeline itself.** It is not gold until a human checks every row against the PDF (`twm-gold-answer-sheet`). Scoring the pipeline against its own draft would be meaningless, so no score is reported.
- **Vendor and client are command-line arguments.** Intake should derive the vendor from the document (counterparty on page 1); not done.

## Rule compliance checked

- Precision first: no defaults anywhere; abstentions are explicit; 5 of 53 rows are stored but not counted because the title is unresolved.
- Rates and money: stored as stated with currency and unit; conversion only as a derived column; "contracted rate" wording.
- Data boundary: nothing leaves; the ledger is a local SQLite file; the call log holds no document text beyond token counts.
- Flag then codify: 2 flagged titles, 3 ambiguous, 0 location flags on this family (no place names in the exhibit); the model step's write-back is `method=model`, reviewer empty, for the analyst to confirm.
- No secrets: `.env` ignored and refused by the hook; the cache and ledger are ignored.

## For Kyle

1. Read the one traced row in the run report and confirm it is the kind of evidence a vendor challenge needs.
2. The two queued titles, "Operations" and "Technical Specialist", are correctly unplaceable without the SOW text.
3. Decide whether year-by-year escalation rows are wanted in the ledger now or at the volume run.
