---
name: twm-data-boundary
description: What may leave a client's environment and what never may. Use before writing any output, export, aggregate, log or document that could travel from a client tenant to TWM or to another client.
---
# The data boundary

Local tier (stays in the client's environment, always): documents; individual rate rows; anything linking a named vendor to a client; reasoning text; names of people; the client's location and link rules.

Global tier (may leave): vocabulary (role framework, title mappings, prompts, schemas) through the promotion gate (seen at 3+ clients, sanitized, human-reviewed); **cohort summaries** per cut (count, p25, median, p75), published only above 3 observations and 2 contributing clients; vendor identity as a class only (Big-4, global SI, boutique, staff-aug); public sources may stay named.

Before producing any output that leaves: check each field against the list above; strip project names, cost-centre codes, vendor-proprietary grade codes and person names; state the cohort size and window on anything published.

Wording: "rows and vendor-client links never leave; vocabulary and cohort summaries do" (corrected Oct 6, 2026).
