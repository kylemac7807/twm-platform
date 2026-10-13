# Intent: the story (visual flow, pitch-deck narrative, naming)

**Accepted by Kyle, October 13, 2026.** Worked in the `story` worktree and branch (stream C of the parallel-session plan), with Kyle dipping in.

## The problem

The pipeline works and nobody can see it. Two contract sets have gone through; 483 rates sit in a ledger with page-and-box evidence; the system abstains and flags exactly as designed. All of that is invisible outside a terminal, and the Pitch Deck still describes an earlier, vaguer idea of the product. An Early Adopter CIO needs to see, in one page, what happens to one rate from the moment a document is dropped in to the moment it can be challenged. And the business and the application are still called "TWM", a working label.

## What we want

1. **The visual flow.** One HTML page, "follow one rate from the page to the ledger": six stages left to right (library, intake, reading, extraction, normalization, ledger) with the review queue beneath, and under each stage the *same real row* from the Texas DIR Accenture pricing exhibit at that stage: page 8 as an image, the contract-set link, the table cell, the extracted "$83.00 per hour" for "Advanced Systems Engineer", the resolution to systems_engineer / senior, the ledger row with its box coordinates. A second strip follows a row that gets flagged instead ("Operations", or a place name), because the abstaining is the point. A closing box marks where savings stacking will appear once findings exist, labelled as coming.
2. **The pitch-deck narrative.** A one-page plain-language account written from the flow, for Cowork's Pitch Deck revision (D3): what the product does, what it refuses to guess, what the CIO gets.
3. **Names.** Options for the business and the application, with the reasoning and the checks done (domain and trademark searches as far as public sources allow), for Kyle to choose from.

Audience: Kyle first, then a CIO; written so the CIO version needs no translation.

## Rules that bind this task

Everything shown is real: real documents, real rows, real abstentions; nothing mocked. Rates and money as stated, "contracted rate" never "cap", "document library" never corpus, "contract set" never family. Nothing that would leave a client's environment is implied to. No code under `src/` changes; the page reads the ledger and the documents as they are. Writing per the `twm-write-for-kyle` skill.
