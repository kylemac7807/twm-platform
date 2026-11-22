# Review: contract terms

**Independent review pass, October 13, 2026** (step 7 of the plan; `docs/how-we-build.md`). Written after steps 1 to 5 were built, tested and run against the real model on the Texas master agreement, Exhibit 2 and the Michigan Deloitte contract. Findings are grouped by what was fixed during the review, what is left and why, and what Kyle should look at.

## What was built and proven

| Step | Proven by |
|---|---|
| Shared-module additions | 177 added lines, no existing line changed; a test keeps the 48-condition inventory and the code's key list identical (keys, groups, meanings, counts) |
| Term reading | Pages chosen by a three-class signal vocabulary tuned on 131 library PDFs; every quote verified word by word on its page and boxed over the lines that hold it; wrong-page quotes corrected within the section; invented quotes rejected (offline tests); on the real model: Texas 081 and 084, 8 calls, 0 rejected; Michigan, 15 of 17 sections, 0 rejected |
| Vendor resolved once | Intake finds "Accenture LLP" (unlabelled) and "DELOITTE CONSULTING LLP" (labelled CONTRACTOR); the run queues an unknown name, `--vendor` answers it once, the next run resolves from the table without a flag (offline test; real run on Texas) |
| The ledger | `contract_terms` (facts and conditions), `named_resources`, `vendor_names`: append and supersede, confidence on every row, a verified flag, status recorded or flagged, page, box and quote; a term not verified on its page raises rather than stores |
| The run report | Facts per document, conditions by key with page and quote, the model's abstentions in its own words, where the vendor came from, one condition traced to its box, model calls; draft answer sheets per document, marked unverified |
| Every contract year | The Texas grid splits into four parts by its own block rows and column groups; a year-1 row expands to years 2 to 8 with the cell's own box, every value found on the page; the rules do nothing on the G-Cloud and Michigan tables (offline tests); the real run of the split grid is pending credit |
| Daily call stop | A persisted log beside the cache; a run refuses to spend at 200 (offline test); a run and its extractors stop at the first credit or key refusal (offline test) |
| The gate (added after the review, Oct 13) | Inventory group G, six disclosure and benchmarking keys; pages with those words chosen on their own signal; every run report opens with the contract set marked restricted, cleared or unchecked, with restricted and unchecked queued (two offline tests) |
| The library rehearsal | 131 PDFs through the reading interface, no spend: 399 calls for a full pass, median 1 per document, 20 at most; `rehearsal.md` |

Tests: 151 pass, 1 expected failure (the Texas regression replay, pending re-base), from 118 at the start of the stream (23 added by this stream, the rest by the workbench merge).

## Fixed during build and review

1. **The money confidence floor flagged 92 percent of the terms.** The model puts 0.8 on most clauses; the software has already proved the quote on the page, so the floor for a term is about its typing, not its number. A separate `TERM_CONFIDENCE_FLOOR = 0.75` records 33 of 61 Texas terms and flags 28 (17 of those for want of an inventory key). Kyle to confirm.
2. **A running header is not a signal.** "DIR Contract No." sits on every page of a Texas contract and inflated the first page scores; a most-favoured-customer clause standing alone on page 10 was missed. The vocabulary now has three classes: decisive alone, strong in company, supporting never alone.
3. **The volume-discount tier table went to the rate-card path**, which cannot read a discount. A money table with no rate heading now stays with term reading; a table whose heading or unit column says rate, hourly or per day goes to the rate-card path.
4. **"U.S. Dollars" did not match "us dollars".** Quote verification now compares the page as one run of letters and digits with token boundaries marked, so punctuation inside a word does not matter and "art" never matches inside "part".
5. **Facts repeated across sections** (the contract number from every running header). Deduplicated per document by type and value, earliest page kept, highest confidence kept.
6. **Form feeds were lost when counting pages** in the party finder (`splitlines()` eats them). Fixed; a party on page 2 reports page 2.
7. **Review: a base row could match the wrong printed row.** "$22.00" was a substring of "$122.00". Exact title and exact first-period cell now match first; containment only against whole cell tokens as a fallback.
8. **Review: retries were free in the daily stop.** The log and the stop now count API requests including retries, not only call invocations; older log rows without the field fall back to the call count.

## Known limits, deliberately left

- **Three real runs are waiting on API credit** (the key's balance ran out during the Michigan run): the two Michigan sections that did not come back and its 22 title resolutions; Texas 083, 085 and 087; the re-base of the Texas regression replay, which is marked expected-to-fail with the reason in the test. The 15 good Michigan sections and the 8 Texas sections are cached, so re-runs cost only what failed.
- **A saved web page is not read for terms.** The G-Cloud vendor pages are rate cards; their commercial terms live in separate service-definition documents. Term reading applies to PDF and Word documents.
- **Term reading follows intake's class.** Master agreements, statements of work, amendments and rate cards are read; service-level documents, templates, solicitations and unknowns are not. A misclassified document (Texas 082, the MSA definitions attachment classified as a solicitation) is skipped until its class is corrected in the workbench.
- **Rows priced from year 2 only are lost by the split**: a part sends only rows whose first-period cell holds money. Not seen in the library; noted.
- **The party finder needs a legal-entity suffix** and plain words: "Accenture (UK) Limited" on the G-Cloud page is not captured because of the parentheses. The `--vendor` answer covers it; a name rule for brackets is a later refinement.
- **"escalat" also matches "escalate"** in process text, so a skills-framework PDF sends 36 pages it need not. Bounded by the cap; a word-boundary refinement later.
- **The facts carry the effective date, but observation rows still have `effective_date` empty.** Linking a document's effective date into its rate rows is a small follow-up once the facts are hand-checked.
- **An answer sheet is a draft produced by the pipeline itself.** Not gold until a human checks every row against the PDF (`twm-gold-answer-sheet`); no score is claimed.
- **The inventory stayed at 48.** 41 conditions came back as `other` with the model's note and are queued; the proposed keys are in `status.md` for Kyle to name.
- **fx.py (step 6) was not started**; time went to the real runs and their findings.

## Rule compliance checked

- Precision first: no defaults; every stored quote is proven on its page; what the model claimed but the page does not show is queued, never stored; abstentions in the model's words; a condition the inventory cannot name is flagged and queued, not forced into a key; contract-year rows are copies of printed cells, never computed.
- Rates and money: prose rate rows stored as stated with currency and unit through the same verification as table rows; the expanded rows carry the printed cell text and a note that the software copied them; "contracted rate" wording; no conversion applied.
- Data boundary: everything stays in the local ledger; named resources (people's names) are local-tier rows, not exported, not summarised; draft answer sheets are ignored by version history; the call log holds counts and tokens, no document text.
- Flag then codify: the vendor-name table and the inventory both grow only from a decision, recorded with who and when; the operator's `--vendor` is one such decision.
- Shared modules: `contracts.py`, `models.py`, `ledger.py` gained lines only, listed in `status.md`; the taxonomy, the normalizer, the model wrapper and the standing documents were not touched. The branch was synced with main once (the workbench merge); two adjacent-insertion conflicts in `ledger.py` were resolved by keeping both streams' additions.
- No secrets: `.env` never read by the stream's code beyond the wrapper that already existed; nothing printed.

## For Kyle

1. Top up the API credit in the Anthropic console; then one run each of the Texas set and Michigan finishes the pending work (about 30 calls).
2. Read one traced condition in the run report ("One condition traced back") and say whether that is the evidence a vendor challenge needs: the clause, the page, the box.
3. Confirm the term confidence floor of 0.75, or say 0.90.
4. Name the conditions you want in the inventory from the candidates in `status.md`; each becomes a key with its example, and the model types with it from then on.
5. Decide, at merge, whether `--all-periods` goes on for the volume run.
