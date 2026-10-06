# How we build TWM

**Decided by Kyle, October 6, 2026**, after reading Anthropic's "The AI-native SDLC playbook" (claude.com/blog/the-ai-native-sdlc-playbook). This page is the short version of what we adopted. Everything here is enforced by files in the project folder, not by memory.

## The idea

Every stage of work leaves a short written artifact in the project folder, saved in version history, and that artifact is what the next stage starts from. Humans keep decision authority at the gates: Kyle accepts the intent and the plan; the AI does the work and must verify it before saying it is done.

## The artifact chain for every build task

| Stage | Artifact | Who | What it contains |
|---|---|---|---|
| 1. Intent | `work/<task>/intent.md` | written with Kyle, accepted by Kyle | the problem, in plain language, half a page |
| 2. Spec | `work/<task>/spec.md` | Claude, from `architecture-components.md` and the decision log | what will be built, inputs, outputs, rules it must obey, what is out of scope |
| 3. Plan | `work/<task>/plan.md` | Claude; **Kyle reads this before any code is written** | files to be created or changed, in order; the tests that will prove it; risks |
| 4. Build | code and tests | Claude | tests run before anything is reported done |
| 5. Review | `work/<task>/review.md` | Claude, an independent pass | bugs, security, rule violations found and fixed; what was left |
| 6. Done | the action list updated, decisions logged | Claude | |

A task is small enough that Kyle can read its plan in five minutes. Bigger work is several tasks.

## Three guardrails (automatic, in `scripts/git-hooks/pre-commit`)

1. **No secrets in version history.** A commit is refused if a staged file contains something that looks like an API key or password.
2. **Tests before commit.** A commit is refused if the test suite fails.
3. **Taxonomy changes regenerate the acceptance report.** If any `taxonomy/*.csv` is staged, the acceptance report is regenerated and staged with it, so the report can never be stale.

Install once per machine: `cp scripts/git-hooks/pre-commit .git/hooks/pre-commit`. Claude Code does this; Kyle never needs to.

## Skills (project: `.claude/skills/`; generic practice: Kyle's personal library in his user profile, created Oct 6, 2026)

A skill is a written procedure that must be applied the same way in every session. Thirteen now, two later; list and status in `.claude/skills/README.md`. The rule: if doing it inconsistently would damage trust in the product or waste Kyle's time, it is a skill. One-line conventions stay in `CLAUDE.md`.

## Deferred until a client environment exists

Automated deployment through the pipeline (adopted with Azure, as the reinstall-from-scratch rehearsal); monitoring that creates new work from production metrics; scheduled security scans; parallel AI sessions; AI on call in chat channels. Revisit at client one.

## What we already did before naming it

Every decision and change in version history with a reason; a project instruction file every session reads; a self-checking test suite (77 checks at the time of writing); the design record and decision log as the standing spec.
