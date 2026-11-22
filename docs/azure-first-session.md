# Azure: getting to the first session

**Written November 22, 2026** (action item B28). What Kyle does once, what Claude does the same day, and what is deliberately not decided yet. The decisions behind this are in `architecture-components.md` ("Azure set-up", October 6, 2026): TWM installs into each client's own Azure environment; TWM's own environment is a build, test and demonstration copy of the same installable stack; region Canada Central; installation by Bicep scripts; Kyle owns the subscription, billing and admin account; Claude deploys with a limited identity and never holds admin credentials.

Screens on Microsoft's side change often. Where a step below does not match what you see, stop and tell Claude what is on the screen rather than guessing.

## Part 1. What Kyle does (about 30 minutes, once)

1. **Create the Azure account and its directory.** At azure.microsoft.com choose to start an account and sign in with the email that should own TWM's cloud for good. Use an address you control personally and will keep; this account is the owner of everything.
   - It will ask for a card and a phone number for identity checks. That is normal.
   - **The directory's first name is hard to change later.** It becomes an address ending in `.onmicrosoft.com`. The company is not named yet (action item A11), so pick something neutral you can live with, for example your own name or "straightlineadvisory"; the display name and a proper domain can be added later, the first address cannot be renamed.
2. **Create one subscription** and call it "TWM Development". A subscription is the billing container; everything Claude builds goes inside it. Pay-as-you-go is the right type. If Microsoft offers a free-credit trial, taking it is fine; it converts later.
3. **Turn on two-step sign-in** for the owner account if it is not already on.
4. **Set a spending alert before anything is built.** In the portal: Cost Management, then Budgets, then add a budget on the subscription. Suggested: $200 a month, with emails at 50, 80 and 100 percent. A budget warns; it does not stop spending, which is why Claude will show the price of anything with a standing monthly charge before creating it.
5. **Tell Claude two identifiers**, neither of which is a secret: the directory (tenant) ID and the subscription ID. Both are on the subscription's overview page.

Do not create resources, resource groups or users by hand. Everything after this is done by script so it can be repeated in a client's environment.

## Part 2. What Claude does in the first session (with Kyle present, about two hours)

1. **Install the Azure command-line tool and Bicep** on Kyle's machine (one installer; Kyle approves it).
2. **Kyle signs in** from the command line; a browser window opens for him. Claude never sees the password.
3. **One resource group** in Canada Central for the development environment, and **a deployment identity** limited to that resource group. Kyle, as owner, approves the one role assignment; from then on Claude works as that identity, not as the owner.
4. **Check before building:** which models Microsoft Foundry offers in Canada Central, and under what data-residency terms. This is the one real unknown: if Claude models are offered only through a global or United States data zone, that is a decision for Kyle (and the question C7, Foundry data-handling terms in writing, stops being parked). Nothing else is built until this is known.
5. **Install in this order, each by script, each torn down and reinstalled once to prove the script:**
   1. Storage for documents and Key Vault for secrets (pennies a month).
   2. The database for the ledger (PostgreSQL, the smallest size). *Standing monthly charge; price shown first.*
   3. Document Intelligence for reading scans (pay per page).
   4. The Foundry project and model deployments (pay per use).
   5. Search for similar titles. *Standing monthly charge; price shown first; can wait.*
   6. Somewhere to run the engine and the workbench (Container Apps).
6. **First proof, the goal of the session:** one real document, the Oklahoma Deloitte scanned contract, read by Document Intelligence and compared with what the local reader gets today. That scan is the document the local reader cannot handle, so it is the honest test.

## Part 3. The sessions after that

- **Second:** the engine pointed at the cloud pieces behind its existing interfaces (reader, model wrapper, ledger), one contract set end to end, the same regression replays passing.
- **Third:** the hardening rehearsal: delete everything, reinstall from a clean subscription, time it. The target is under an hour with no manual steps.
- **Before client one, not now:** private networking with no public endpoints, the client's identity provider, audit logging, and whether to convert the scripts to Terraform if a bank's platform team prefers it.

## What is not decided, on purpose

- The company and product names (A11): nothing here depends on them except the directory's first address, handled in step 1.
- Whether the workbench is rebuilt for Azure or the current one is hosted as it is: decided when the terms view (B32) is done and the volume run has shown what the workbench needs.

## The skeleton

`infra/main.bicep` holds the first two pieces (storage and Key Vault) as a starting point. It has **not** been validated: the Bicep tool is not on this machine yet. Validating and running it is the first thing Claude does after step 1 of Part 2.
