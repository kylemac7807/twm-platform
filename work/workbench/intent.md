# Intent: review workbench, first version

**Accepted by Kyle, October 6, 2026**, with the parallel-session plan (`Claude outputs/parallel-agent-plan.md`, stream B). Worked in the `workbench` worktree and branch.

## The problem

The platform abstains on purpose and asks a person: titles it could not place, places it would not classify, documents it would not link, extractions it did not trust. After two document families those questions number seventeen, and they sit in a database table nobody can see. The one person who could answer them has no screen to do it on, and the answers have nowhere to be recorded with a name and a reason.

The demo for an Early Adopter CIO runs inside the workbench (design record, review workbench, decision 3), so the screens are on the path to the demo.

## What we want

The first version of the review workbench, three of its four jobs:

1. See the documents and their families as intake sorted them, with the system's own evidence and flags.
2. Work the queues. Each decision is recorded with the analyst's name, the answer and a written reason, and the question closes so it is never asked again. The workbench does not write to the taxonomy itself; it exports the decisions for the main session to codify.
3. Click any rate through to the page it came from, with the spot highlighted.

The executive views wait until findings exist.

## Rules that bind this task

The screens must be honest: what the system found, what it declined to decide, and why. Nothing is guessed on the analyst's behalf; nothing is hidden. One analyst role, with an audit record built so a second reviewer role can be added later without changing the data (decision 2). Streamlit, Python only, on Kyle's machine; a prototype for the consultants and the demo, to be rebuilt for Azure. No model calls. Writes to the ledger go through `ledger.py` methods only.
