---
name: twm-build-task
description: The artifact chain for any build task: intent, spec, plan, build, review, done. Use whenever starting new code or a new component, including M2.
---
# Build task chain (docs/how-we-build.md)

1. **Intent** `work/<task>/intent.md`: the problem in plain language, half a page, written with Kyle and accepted by him.
2. **Spec** `work/<task>/spec.md`: from `docs/architecture-components.md` and the decision log. Inputs, outputs, rules it must obey (precision first, rates and money, data boundary), out of scope.
3. **Plan** `work/<task>/plan.md`: files to create or change in order, the tests that prove it, risks. **Kyle reads the plan before any code is written.** Keep it to five minutes of reading; split bigger work.
4. **Build**: code and tests. Run the tests before reporting anything done. Update the plan if the build departs from it.
5. **Review** `work/<task>/review.md`: an independent pass for bugs, security, and rule violations; fix what is found; list what was left.
6. **Done**: update `docs/action-items.md`; log decisions; commit with a plain message.
