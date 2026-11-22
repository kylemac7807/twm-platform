# Intent: the full run of the document library

**Packaged on November 22, 2026, at Kyle's request, for a later date.** Not started. This file and `BRIEF.md` beside it are what a later session picks the work up from. Action item B30.

## The problem

The engine has read 9 documents from three contract sets. The document library holds 228 contract sets, 363 documents (`docs/library-summary.md`). Until the rest go through, the ledger compares Accenture with itself and little else, the mapping table has met only a few hundred job titles, and the rate-conditions inventory has been tested on two governments' contracts. Benchmarking across vendors, the evaluation sample and the demo all wait on a fuller ledger.

## What we want

Every contract set in the library through the engine: intake, reading, rates, terms, the disclosure check, normalization, the ledger. Kyle answers the questions it raises in the workbench. At the end the library summary's "read by the engine" column says how many documents went through, and its "likely to contain rates" range is replaced by a measured count.

## The estimate (made November 22, 2026)

| Part | Estimate | Measured basis |
|---|---|---|
| Getting ready | 1 to 2 build sessions | the gaps listed below |
| Machine time, unattended | 8 to 12 hours, one call at a time | 12 seconds per model call; about 3,000 calls |
| Kyle's time on questions | 15 to 30 hours, spread out | Texas raised 35 questions, Michigan 49 |
| Model cost | $130 to $180 | about 7 cents per term-reading call, 2 cents per title |

Where the 3,000 calls come from: about 550 to read terms in the PDF contracts, 150 for rate tables, 1,300 to read terms in the 163 company contracts filed with the SEC (web format, about 8 calls each, the least certain figure because none has been read yet), and 500 to 1,500 to place job titles the rules do not know.

The measured runs behind the per-call figures, all on October 13, 2026:

| Run | New calls | Minutes | Cost |
|---|---|---|---|
| Texas DIR and Accenture, 7 documents | 57 | 13.1 | about $2.40 |
| Michigan and Deloitte, 1 document of 378 pages | 34 | 7.0 | about $1.80 |

Kyle's Ultra plan includes a $200 API credit each month, linked to the Console organization that owns the engine's key (claimed November 22; it renews on the 5th and does not roll over). The whole run fits inside one month's credit with little to spare, or comfortably across two.

## What has to happen first

1. **Intake labels for web-format contracts (B35).** Of the 163 SEC master agreements, intake calls 8 a master agreement. About an hour.
2. **Term reading for web-format contracts (B36).** The engine reads terms page by page and skips a saved web page entirely. An SEC agreement is one long web page. It needs splitting by its own headings, and a position that is a section and paragraph instead of a page and a box. About half a day. Nearly half the documents in the contract sets depend on it.
3. **Rate tables inside a contract file (B37).** Today a table goes to the rate-table reader only when intake labels the whole file a rate card. The richest staffing price sheets in the library sit at the back of full contracts: Florida's Exhibit E price sheets, the Michigan Knowledge Services rate card. About an hour. With it, a small fix to party names: "a Delaware limited liability partnership" is read as a party called "Delaware Limited".
4. **The daily stop of 200 model calls.** Set for the contract-terms stream. At that limit this run takes two weeks. Kyle sets the number for the run; 1,500 a day finishes it in two days. The stop at the first credit refusal stays.
5. **Slow ledger writes.** The run re-reads every live row of a document after each row it stores; the 1,648 Texas rows took minutes. A small fix before bulk.
6. **Files with no reader yet.** Three scanned documents, and a small number of spreadsheets, pictures and one Word file, wait for Azure's document reader. They are flagged and skipped, not failed.

## How to stage it, so Kyle's part is as small as it can be

Most questions are conditions the inventory has no name for, about 27 in a large contract. Naming one is a decision for everyone, so each answer removes that question from every later contract. Job titles shrink the same way as the mapping table grows.

1. **A pilot of about 15 contract sets**, chosen to cover the kinds: a staffing rate card, a second vendor at a client we already hold, a second client for a vendor we already hold, an SEC agreement, a UK contract, an invoice set. The first few are named in `BRIEF.md`.
2. **Codify.** Kyle names the common conditions and titles from the pilot; they go into the inventory and the mapping table; the pilot is read again so the model types with the new names.
3. **The full run**, overnight, unattended. The engine never waits for an answer: unanswered rows are held back and everything else proceeds.
4. **Kyle works the questions** over the following days. Rates and job titles can be answered in the workbench today. Term questions need the Terms screens (B32).

## Rules that bind this task

Precision first: nothing guessed, every number and every quote proven on its page. Rates as stated. The disclosure check runs first on every contract set, and a set marked restricted is cleared by a person before it enters a benchmark. Nothing leaves the machine but the model calls themselves. Public documents are a biased sample of what private contracts say; the run measures the engine, not the market.

## For Kyle to decide when this is picked up

1. The daily call limit for the run.
2. Before or after the Terms screens (B32). Before means term questions wait in the ledger; after means everything can be answered as it arrives.
3. One model for everything, as now, or a cheaper model for the stages the Evaluation shows it reads as well.
4. Whether the 163 SEC agreements go in the first full run or a second one. They carry terms, not rates, and are the largest and least certain part of the cost.
