// Builds docs/story/pitch-deck-narrative.docx: the point-form narrative for the hybrid deck
// (Early Adopter CIO + investors), for Kyle to review and edit before the PowerPoint is built.
// Usage: node build_pitch_narrative_docx.js <output.docx>   (needs the npm package "docx")
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, LevelFormat,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, Footer, Header, PageNumber,
} = require("docx");

const OUT = process.argv[2] || "pitch-deck-narrative.docx";
const DATE = "November 22, 2026";

// ---------------------------------------------------------------- content
const decisions = [
  ["Early Adopter fee.", " The documents give three figures: $300k CAD for a 4-month Value Validation (Early Adopter Presentation), $500k CAD for 4 to 6 months then $1.0 to 1.5MM for a further 6 months (Pitch Deck), and $1.5MM per Early Adopter (Business Plan financial model). Which stands?"],
  ["Dates.", " Every dated milestone in the documents has passed or is stale: team start April 1, 2026; launch June 1 or July 1, 2026; MVP Q1 2027 (a working prototype now exists). A new timeline is needed for slides 17, B4 and B5."],
  ["Profitability.", " Q3 2027 on 8 clients (Business Plan) or 2026 with 4 to 5 clients (Pitch Deck)?"],
  ["Target market threshold.", " $100MM+ third-party labour spend, about 500 resources (Pitch Deck) or $200MM+, about 800 (Business Plan); and 400+ North American banking, insurance and telecom organizations (Pitch Deck) or 250+ in financial services (Business Plan)?"],
  ["The ask.", " Is the $1MM SAFE (Pitch Deck) still the ask, and a Series A in early 2027 still the plan? What has been built changes what the money is for."],
  ["Team.", " The documents say additional leadership is to be announced. Names, or keep “to be announced”? The Business Plan and the Pitch Deck also describe your past roles slightly differently; pick one wording."],
  ["The real example.", " Slides 9 and 10 use a public Texas contract with Accenture, named. Our rules allow public sources to stay named, but a CIO may be a client of the same vendor. Keep the names, or show it as “a global systems integrator”?"],
  ["The word “train”.", " You asked to describe training the model. Accurately, no model has been trained or fine-tuned: the frontier model is rented, and the system improves through our role framework, the mapping table and every analyst decision becoming a rule. The draft says it that way (slides 13 and 15). The Pitch Deck’s “train our foundational LLM models”, “neural fine-tuning” and “anonymized neural weights” need to go."],
  ["The name.", " The draft uses Akerlow throughout as the working name, and “TWM” nowhere. Confirm, or keep TWM until the name is final."],
];

// A slide: id, title, headline, points (string | [bold, rest] | {label} | {sub: [...]}), visual, source, flag
const core = [
  { id: "1", title: "Title",
    headline: "Akerlow (working name). Every rate you pay, traced to the page it came from.",
    points: [
      "Subtitle: an AI platform and a specialist consulting practice that cut third-party technology labour spend by 10 to 15%.",
      "Prepared by Kyle McNamara. Month and year. Confidential.",
    ],
    visual: "The name and tagline, with a faint crop of the real Texas page 8 and its boxed row in the background.",
    source: "Tagline new. 10 to 15%: Business Plan v1.5; Pitch Deck v1.1.",
    flag: "The tagline is new. Confirm or replace." },

  { id: "2", title: "The short version",
    headline: "Large enterprises overpay for technology contractors because the vendor sees every price and the client sees one contract at a time. Akerlow closes that gap.",
    points: [
      "Technology labour is 50 to 75% of technology cost, and more than 40% of it goes to third parties: over $1.5B a year at each large Canadian bank.",
      "The leakage is hidden in hundreds of statements of work, invoices and timesheets that nobody can link together.",
      "Akerlow reads them, builds one traceable record of every rate, benchmarks each rate against peers, and finds the savings: 10 to 15% of third-party spend.",
      "A specialist consulting team delivers it first; the software takes on more of the work every year.",
      "Early Adopters join a consortium of 4 to 5 organizations: discounted consulting, shared benchmarks and a seat at the table on the product.",
      "Already built: a document library of 438 real contracts and rate cards, a role framework of 129 roles, and a working prototype that has read real government contracts end to end.",
    ],
    visual: "Four boxes: the problem, what we do, the prize, the proof.",
    source: "Business Plan v1.5 (executive summary); Pitch Deck v1.1; Consortium Approach v1.7 slide 2; project folder (measured Nov 22, 2026)." },

  { id: "3", title: "A large spend, managed in spreadsheets",
    headline: "Third-party technology labour is one of the largest lines in a technology budget, and one of the least managed.",
    points: [
      "Labour is 50 to 75% of total technology cost.",
      "Organizations run close to 50:50 employees to third parties, so 25 to 40% of the entire technology budget sits in vendor contracts.",
      "Third-party technology labour exceeds $1.5B a year at each of the large Canadian banks.",
      "The spend is fractured: thousands of resources, hundreds of contracts and statements of work, 20 or more vendors.",
      "It is managed in spreadsheets. Decisions are decentralized, reporting is inconsistent, and procurement, finance, HR and technology each see part of the picture.",
    ],
    visual: "The infographic the Pitch Deck asks for: the 50/50 split, the $1.5B, the fragmentation (thousands of people, hundreds of contracts, 20+ vendors).",
    source: "Pitch Deck v1.1 (problem; the Canadian bank benchmark; the 50/50 split; the fragmentation factor); Consortium Approach v1.7 slide 3." },

  { id: "4", title: "Why: the vendor sees everything, the client sees fragments",
    headline: "This is an information problem before it is a cost problem.",
    points: [
      "George Akerlof, the Nobel economist, showed that when one side of a market knows far more than the other, the side with the information sets the price. The name Akerlow is a nod to him.",
      "The vendor knows what every client pays for the same role.",
      "The client sees one statement of work at a time, and every contract defines roles, seniority, rate units and price increases in its own way, inside complex terms and conditions.",
      "So the client cannot tell a fair rate from an inflated one, and a vendor that prices fairly cannot win on price.",
      "Nobody has to behave badly for this to happen. The gap does it on its own.",
    ],
    visual: "Two panels: the vendor’s view (every client, every rate) and the client’s view (one contract, dense fine print).",
    source: "The approved Akerlow description (docs/story/naming.md, Nov 22, 2026)." },

  { id: "5", title: "Where the money leaks",
    headline: "Total cost = price × quantity and mix. Both levers leak.",
    points: [
      { label: "Price (leakage)" },
      ["Non-competitive rates.", " Each statement of work is negotiated locally for one programme, procurement arrives late, and the scale of the whole organization is never used."],
      ["Stale skill matrices.", " A role “not on the rate card” is billed off-card at a premium; “super niche” skills and inflated seniority do the same."],
      ["No usable benchmark.", " Every vendor names and levels roles differently, so rates cannot be compared across vendors or with industry data."],
      ["Inconsistent billing.", " The timecard, the invoice and the contract are rarely reconciled; spot checks, when done, find errors."],
      { label: "Quantity and mix" },
      "The mix of employees and contractors, onshore and offshore, senior and junior, and skills drifts away from strategy through thousands of local decisions.",
      "Forecasts are detached from approvals, so teams ramp up and down and people churn.",
    ],
    visual: "The equation, with the leakage points under each lever.",
    source: "Business Plan v1.5 (customer need; Phase 1 leakage); Early Adopter Presentation (price, quantity and mix); Consortium Approach v1.7 slide 4." },

  { id: "6", title: "The size of the prize",
    headline: "10 to 15% of third-party spend is realistic and conservative.",
    points: [
      "10 to 15% of $1.5B is $150MM or more a year for one large Canadian bank.",
      "For any organization: $100 to $150MM for each $1B of third-party labour spend.",
      "The first 5 to 10% comes from price: every statement of work and the invoices against it. A further 5 to 15% comes from changing the mix.",
      "The cost of delay: for an organization with $150MM in potential savings, about $3MM every week.",
      "Time to value is months, not years.",
    ],
    visual: "Hero number: $150MM+ per bank. A bar split into price and mix; the weekly cost of delay.",
    source: "Pitch Deck v1.1 (Canadian bank benchmark; cost of delay); Business Plan v1.5 (opportunity; “10 to 15% cost savings are realistic”; initial 5 to 10%, additional 5 to 15%)." },

  { id: "7", title: "Why existing tools don’t fix it",
    headline: "Every existing tool sees one slice. None links the timecard to the invoice to the contracted rate.",
    points: [
      ["HR systems (Workday, Oracle).", " Built around employees; vendor rates and benchmarks mostly absent."],
      ["Procurement and vendor management (SAP Ariba, Fieldglass, Workday VNDLY).", " The book of record for contracts and contingent workers, but they do not normalize roles or find leakage, and are rarely used for the large vendors."],
      ["IT financial management (Clarity, Apptio).", " Budgets and allocations, with little categorization of skills, location or seniority."],
      ["Benchmark providers (ISG, Gartner).", " Useful data points, but statements of work are structured differently from their datasets, so the comparison stays academic, and they do not find leakage."],
      ["New AI contract tools.", " Legal review, drafting and compliance; none focused on pricing technology labour."],
      ["General-purpose AI cannot do it alone.", " It does not hold your contracts, a role framework or a peer benchmark, and it cannot be allowed to guess."],
    ],
    visual: "Five columns, each with what it covers and its gap; Akerlow spanning the gap.",
    source: "Business Plan v1.5 (competitive landscape; Appendix C); Business Plan deck v1.4 slide 4.",
    flag: "The Pitch Deck asks for a line on why OpenAI or a consulting firm cannot solve this. The last point is a draft answer; slide 13 carries the rest." },

  { id: "8", title: "What Akerlow does",
    headline: "An AI platform and a specialist consulting team that turn contracts, invoices and timesheets into one traceable record of every rate, and that record into savings.",
    points: [
      ["Reads", " master agreements, statements of work, rate cards, amendments, invoices and timesheets, as they actually arrive."],
      ["Records", " every rate exactly as written, with the page and position it came from, in a ledger inside the client’s own environment."],
      ["Normalizes", " every vendor title to one role framework (role and seniority), so rates become comparable."],
      ["Benchmarks", " each rate against the client’s other contracts, its other vendors and the market."],
      ["Finds savings,", " stacked so that nothing is counted twice: contractual, operational, market alignment."],
      "Consultants lead each engagement and work the edge cases; the software does more of the work every year.",
    ],
    visual: "Documents in, the ledger in the middle, benchmarks and savings out; the consultant beside the review queue.",
    source: "Business Plan v1.5 (Phase 1 solution); docs/architecture-components.md; Pitch Deck v1.1 (product)." },

  { id: "9", title: "Follow one rate from the page to the ledger",
    headline: "One real rate from a signed State of Texas contract with Accenture, through all six stages.",
    points: [
      ["The document library:", " Attachment 2.1, Pricing and Volumes, of Texas contract DIR-STS-TSS-699, page 8."],
      ["Intake:", " seven files recognized as one contract set, because the contract number is printed in each."],
      ["Reading:", " a 111-row rate table, with the position of every cell."],
      ["Extraction:", " “Advanced Systems Engineer, $83.00 per hour, year 1, onsite”, recorded exactly as written, then checked against the page."],
      ["Normalization:", " Systems Engineer, senior. The title was resolved once, by a person, with reasoning; every later occurrence is a lookup."],
      ["The ledger:", " one row with the vendor, the rate as stated, role, seniority, confidence, and page 8 with the box. Nothing in it is an estimate."],
    ],
    visual: "The follow-one-rate page: six stages left to right, the boxed row on page 8 under the first.",
    source: "docs/story/follow-one-rate.html and its PDF (pipeline run of Oct 6, 2026).",
    flag: "See decision 7: show Accenture and Texas by name, or not." },

  { id: "10", title: "What it refuses to guess",
    headline: "When the system is not sure, it says so and asks. Precision comes first.",
    points: [
      "Same page, fourteen rows down: “Operations, $99.50 per hour”. The title names no role; the model was asked, answered with low confidence, and abstained. The row is stored but not counted until an analyst decides.",
      "23 of the 53 titles on that page state no seniority. They keep their role and stay without a band; nothing defaults to “intermediate”.",
      "The software never decides from a place name whether work is onshore or offshore; an analyst decides once for each client.",
      "Every abstention comes with one sentence a consultant can read, and every decision becomes a rule, so the same question is never asked twice.",
      "Why it matters: one false claim of overbilling in front of a vendor can lose the engagement. A missed saving is caught at the next refresh.",
    ],
    visual: "The flagged-row strip from the follow-one-rate page.",
    source: "docs/story/follow-one-rate.html; the ledger; architecture decision 5 (precision first)." },

  { id: "11", title: "What the client gets",
    headline: "A book of record, a queue instead of a black box, benchmarks at the right cut, and savings that hold up in a negotiation.",
    points: [
      ["The ledger:", " every contracted rate in the estate, each traceable to its page, including every contract year and the fine print that changes a rate (volume discounts, escalation, expenses)."],
      ["The review queue:", " every place judgement was applied, by whom, and why."],
      ["Benchmarks", " by role, seniority, location and technology, shown as a range (25th percentile, median, 75th percentile), published only when enough data stands behind a cut to protect confidentiality."],
      ["Savings in three tranches, never double counted:", " Contractual (down to the contracted rate), Operational (down to the vendor’s own best rate for the role at this client), Market Alignment (down to the market mid-point)."],
      ["Two executive views:", " the Role Composition Heatmap (rate variance against spend, so procurement knows where to negotiate first) and the Total Potential Dashboard (savings by tranche, observed and projected always shown separately)."],
    ],
    visual: "The two executive views beside one traced ledger row.",
    source: "Business Plan v1.5; Pitch Deck v1.1 (dashboards, tranches); decision log (stacking, Sept 20; observed and projected, Oct 6); rate-conditions inventory (Oct 13).",
    flag: "The dashboards are designed, not built. Any mock-up on this slide must be labelled illustrative." },

  { id: "12", title: "The client’s data never leaves",
    headline: "Akerlow is installed inside each client’s own Azure environment. Contracts, rates and vendor relationships stay there.",
    points: [
      "Deployed into the client’s own Microsoft Azure tenant, in Canada for Canadian clients. It is an installable stack, not a website clients log into.",
      ["Never leaves:", " documents, individual rates, anything linking a named vendor to the client, people’s names, the analysts’ reasoning."],
      ["May leave:", " the shared vocabulary (role framework, title mappings) and benchmark summaries by role and seniority (count, 25th percentile, median, 75th percentile), only when at least three observations from at least two clients stand behind them."],
      "In the consortium benchmark, vendors appear only as a class: global systems integrator, Big-4, boutique, staff augmentation.",
      "Every contract set is first checked for clauses that restrict disclosure; a restricted one is held for a person before anything is benchmarked.",
    ],
    visual: "Two zones: the client’s tenant (everything) and the shared tier (vocabulary and summaries only), with the gate between.",
    source: "Architecture decisions 1, 4 and 7; decision log (data boundary, Oct 6; disclosure gate, Oct 13).",
    flag: "Replaces the Pitch Deck’s “Zero-Data-Exit … exports only anonymized neural weights”, which is superseded." },

  { id: "13", title: "What we own, what we rent",
    headline: "We rent the best AI models and own everything that makes them reliable for this problem.",
    points: [
      ["Rented:", " the frontier reasoning models, through Microsoft Foundry on Azure. Claude is primary and GPT is benchmarked; each step uses whichever model measures best. No vendor is hard-wired."],
      ["Owned:", " the role framework and its crosswalks, the mapping table of resolved titles, the task definitions and prompts, the checks that prove every number against the page, the rate-conditions inventory, the evaluation sets, and the consortium benchmark."],
      "The system improves without retraining a model: every analyst decision becomes a rule, the mapping table grows, and the vocabulary sharpens across clients.",
      ["The moat:", " a consortium benchmark built from real statements of work and invoices that others cannot see; a vocabulary refined across clients; and a consulting playbook that becomes software."],
    ],
    visual: "Two columns, rent and own; the flywheel (more clients, better vocabulary, deeper benchmark, more savings).",
    source: "Architecture decisions 2, 3 and 6; Pitch Deck v1.1 (“The Moat”).",
    flag: "Replaces “neural fine-tuning”, “train our foundational LLM models” and the GPT-4o references in the Pitch Deck and Technical Approach (decision 8)." },

  { id: "14", title: "Built so far (1 of 3): the document library",
    headline: "Before any client data existed, we assembled 438 real public contracts, rate cards, invoices and frameworks to build and test against.",
    points: [
      "Why public documents: the product has to work on real contracts from the first engagement, and no client data exists before then.",
      { label: "What we gathered" },
      { sub: [
        "About 240 contracts that US public companies filed with the securities regulator: master agreements, amendments and statements of work.",
        "Government contracts with rates visible: five Texas contract sets (four Accenture, one Deloitte); thirteen Michigan contracts, including a $109M, 13-year Deloitte contract and an $800M staff-augmentation programme; plus Florida, New York, Oklahoma and federal contracts.",
        "UK government: 48 signed contracts, and the G-Cloud rate cards of 13 major vendors (about 2,600 priced rows, January 2026).",
        "Canadian federal TBIPS packages, 12 of them French or bilingual.",
        "The rarest material: a public invoice with the timesheets behind it, and audits that reconcile billing by hand.",
      ] },
      "About 226 vendor-client pairs, 51 of them with two or more documents: real contract sets to follow end to end.",
      "Hard-won: scripts fetched most of it; government sites that block scripts were downloaded by hand; every file is checked for what it really is, not what its name says.",
    ],
    visual: "A grid of sources with counts, and one sample page from each type.",
    source: "docs/corpus-sources-and-demo-set.md; action items B30 and B35 (counts measured Nov 22, 2026)." },

  { id: "15", title: "Built so far (2 of 3): teaching the system the language of technology labour",
    headline: "We built our own role framework and taught the system to place any vendor title in it, or to ask.",
    points: [
      ["The role framework:", " 129 roles in 18 families, and four seniority bands (junior, intermediate, senior, lead or principal). Location and technology are recorded beside the role, never multiplied into it."],
      "Built from open public sources: the US O*NET database, the UK government’s digital job ladders and Canada’s TBIPS categories. 140 crosswalk rows translate ten published seniority schemes into our four bands.",
      ["The mapping table:", " 547 vendor titles resolved, 417 of them seen in real public documents, each with its reasoning, who decided, and a version."],
      ["Consistency check:", " 96.7% of 1,355 title-and-level pairs from the seed sources resolve to exactly one role and band, and seniority rises with rate in every public rate grid tested."],
      ["The real test, on 113 titles the system had never seen:", " 40.7% placed by the rules alone; 95.6% after one review pass by Kyle, with 72 titles codified. That is how it learns: each decision becomes a rule."],
    ],
    visual: "The framework as families and bands; the unseen-title test as before-and-after bars.",
    source: "taxonomy/REPORT.md (Oct 13, 2026); taxonomy/HELDOUT.md; decision log (Oct 6, 2026).",
    flag: "“Teaching” is the accurate version of “training the model” (decision 8)." },

  { id: "16", title: "Built so far (3 of 3): a working prototype",
    headline: "The whole pipeline runs end to end on real contracts today, before any cloud spend.",
    points: [
      ["Three real contract sets through every stage:", " the Texas Accenture contract (seven files), Accenture’s UK G-Cloud rate page, and Michigan’s 13-year Deloitte contract."],
      ["Every rate traced to its page:", " 483 rates from the first two sets, with no number rejected by the page check. Reading every contract year as its own row, the Texas pricing table alone yields 1,648 verified rates."],
      ["Contract terms read too:", " 1,034 facts and conditions (parties, dates, escalation, discounts, expenses), each quote proven word for word on its page and boxed, and typed against a 54-item inventory of the fine print that makes rates hard to compare."],
      ["An analyst workbench:", " contract sets, the review queue as task cards, any row clicked through to its page with the box drawn, and answers that apply to one contract set, one vendor or everyone."],
      ["Cheap to run:", " the full Texas and Michigan runs cost about $6.50 in model calls; repeat runs are free from a cache."],
      ["Built with discipline:", " 166 automated tests, each listed as a plain-English promise; no secret can be committed; every decision is logged."],
    ],
    visual: "A screenshot of the workbench beside the traced Texas row; three contract-set tiles with their counts.",
    source: "work/m2-thin-thread/review.md; work/contract-terms/review.md; action items B24, B25 and C12; test suite (Nov 22, 2026).",
    flag: "The workbench screenshot needs a fresh capture." },

  { id: "17", title: "What is next, and what we do not claim yet",
    headline: "The core works. Here is what comes next, and what we will not claim until it is measured.",
    points: [
      { label: "Next" },
      ["The volume run:", " every contract set in the library through the pipeline, filling the ledger and growing the mapping table."],
      ["The evaluation:", " hand-checked answer sheets as the measuring stick, then field-by-field accuracy and a Claude-versus-GPT comparison."],
      ["Benchmarking, findings and savings stacking", " on top of the ledger; then invoice-to-timesheet reconciliation."],
      ["Azure:", " TWM’s own environment in Canada Central, then the same installation in a client’s tenant."],
      { label: "Not claimed yet" },
      "No extraction accuracy figure: the answer sheets for the first two contract sets (53 and 430 rows) are drafted but not yet hand-checked.",
      "No savings figure from Akerlow itself: findings come after benchmarking.",
    ],
    visual: "A simple timeline: built, next, then.",
    source: "Action items B17, B26, B30 and C4; docs/architecture-components.md (build sequence).",
    flag: "Dates for “next” follow decision 2." },

  { id: "18", title: "Roadmap: from an audit to the whole technology workforce",
    headline: "Start with the money that is leaking; grow into how the workforce is planned.",
    points: [
      ["Phase 1, the audit and the Master Benchmark Ledger:", " rate leakage, non-competitive agreements and inconsistent billing; consultants and software together."],
      ["Phase 2, strategic workforce alignment:", " the demand pipeline (3, 6 and 12 months), what-if planning of the mix (employee and contractor, onshore and offshore, seniority, skills), and workflows linking forecasts to approvals to onboarding."],
      ["Future phases:", " all labour, not only technology; financial management (capitalization, the general ledger); ready-on-day-one provisioning and vendor compliance; delivery productivity."],
      "The path: white-glove consulting first, then a self-serve product as the platform matures.",
    ],
    visual: "A three-phase arc.",
    source: "Business Plan v1.5 (phases); Pitch Deck v1.1 section 5." },

  { id: "19", title: "The team",
    headline: "Led by an executive who has managed this problem from the inside, at scale.",
    points: [
      ["Kyle McNamara.", " At TD Bank, led 6,200+ technology professionals with a $1.8B+ annual budget. At National Australia Bank, Chief Transformation Officer reporting to the CEO, with cost reductions of $1B+, a large portion from third-party labour. At Scotiabank, oversaw a $1.5B+ IT budget and 5,000+ staff globally."],
      ["Consulting practice:", " led and staffed by ex-McKinsey and ex-BCG consultants experienced in cost transformation and third-party labour, in pods led by engagement managers."],
      ["Platform team:", " AI and data engineering, software engineering, security, and product management."],
      "Additional leadership to be announced.",
    ],
    visual: "Kyle’s photo with three career facts; the Year 1 organization chart from the Business Plan deck.",
    source: "Business Plan v1.5 (leadership); Business Plan deck v1.4 slide 9; Early Adopter Presentation.",
    flag: "See decision 6." },
];

const endingA = [
  { id: "A1", title: "The Early Adopter consortium",
    headline: "An exclusive group of 4 to 5 leading organizations, transforming their technology workforce together.",
    points: [
      "Savings of 10 to 15%, delivered quickly and measurably.",
      "A prioritized list of value levers from your own contracts and workforce data.",
      "Proprietary benchmarks: labour rates and workforce mix against peers.",
      "Peer learning: consortium workshops on leading practice and the operating model for the AI era.",
      "A seat at the table: members shape the product’s features and priorities.",
      "Confidential by design: no member sees another’s data; everything shared is sanitized and anonymized.",
    ],
    visual: "The consortium as a ring of 4 to 5 members around the shared benchmark.",
    source: "Consortium Approach v1.7 slides 2, 5 and 7; Early Adopter Presentation (benefits; influence and co-development)." },

  { id: "A2", title: "How it runs",
    headline: "Value Validation in 4 to 6 months, then Execution, then Capability Development.",
    points: [
      ["Value Validation:", " an opportunity assessment that quantifies full-potential savings; a preliminary target state for the workforce (resource type, location, seniority, skills); benchmarking of rates and mix against peers; quick wins (renegotiating statements of work, updating skill matrices); a roadmap and action plan."],
      ["Execution:", " deeper analysis; recommendations on contracts and mix; alignment across HR, finance, procurement and technology; progress tracked on dashboards."],
      ["Capability Development:", " tools deployed, processes standardized (demand forecasting, workforce planning), internal capability built, benchmarks refreshed."],
      "Throughout: consortium workshops.",
    ],
    visual: "The three-phase framework from Consortium Approach v1.7 slide 6.",
    source: "Consortium Approach v1.7 slides 6 and 7." },

  { id: "A3", title: "What we ask, what we bring",
    headline: "A committed sponsor and access to the documents. In return, a dedicated team and the platform.",
    points: [
      ["From each member:", " CIO sponsorship and a dedicated internal leader; leaders from procurement, HR and finance; access to statements of work, invoices, contracts and timecards, with help validating them; subject-matter experts for workshops."],
      ["From Akerlow:", " hands-on leadership; a pod for each member (an engagement manager covering two members, a workforce analytics lead, a data analyst); the platform running inside your own environment."],
      "Your data stays in your environment; only anonymized summaries feed the shared benchmark.",
    ],
    visual: "Two columns: the member, Akerlow.",
    source: "Consortium Approach v1.7 slide 8; architecture decisions." },

  { id: "A4", title: "Commercials, and why join now",
    headline: "Founding members get the deepest discount, the earliest benchmarks and the most influence.",
    points: [
      "Participation fee for Value Validation: [to be decided, decision 1].",
      "Discounted against a McKinsey engagement team (an engagement manager and four associates, about $1.5MM a month) and against the value created.",
      "Why now: shape the product; earliest access to benchmarks; savings start within months; the cost of delay is about $3MM a week for $150MM of potential savings.",
      "Next step: [how to join, key contacts].",
    ],
    visual: "A simple offer box and timeline.",
    source: "Early Adopter Presentation ($300k; why join now); Pitch Deck v1.1 ($500k; cost of delay); Business Plan v1.5 (McKinsey comparison; $1.5MM).",
    flag: "See decision 1." },
];

const endingB = [
  { id: "B1", title: "The market",
    headline: "A very large spend with no purpose-built solution.",
    points: [
      ["Total addressable:", " Gartner and IDC put 2026 IT services spend at $1.87 trillion, up 8.7% on the year; the top seven providers employ about 3 million people."],
      ["Serviceable:", " organizations with $100MM+ in third-party labour spend [or $200MM+; decision 4]."],
      ["Obtainable:", " 1,500+ such companies globally, about half in North America, and 400+ in North American banking, financial services, insurance and telecom. Goal: 50+ clients."],
    ],
    visual: "Market rings; the table of the top seven providers by headcount.",
    source: "Pitch Deck v1.1 section 4 (citing Gartner and IDC); Business Plan v1.5 (target market analysis).",
    flag: "See decision 4." },

  { id: "B2", title: "Business model",
    headline: "Revenue tied to the savings we create.",
    points: [
      "Tiered, value-based pricing: $20MM in savings generates $2 to 3MM in revenue; $50 to 100MM+ in savings generates $5 to 10MM.",
      "Target: 50 organizations at an average of $4MM a year, about $200MM in recurring revenue, at considerable margins.",
      "Recurring because savings must be sustained: benchmark access, quarterly or semi-annual refreshes, ongoing tracking, then Phase 2 workflows built into how the client plans its workforce.",
      "Consulting-led first, software-led as the platform matures, which keeps Akerlow a software company rather than a boutique consultancy.",
    ],
    visual: "Revenue per client as a share of savings; the shift from consulting to software over time.",
    source: "Business Plan v1.5 (opportunity; recurring revenue; go-to-market); Pitch Deck v1.1 (business model)." },

  { id: "B3", title: "Go-to-market",
    headline: "Early Adopters first, then a sales-led expansion.",
    points: [
      ["Months 1 to 12:", " the Early Adopter consortium, through the leadership team’s executive network (4 to 5 organizations)."],
      ["Years 2 to 3:", " enterprise sales (account executives, sales engineers, customer success) running 4 to 8 week proof-of-concept pilots across the North American banking, insurance and telecom market."],
      ["Buyers:", " CIOs first, chief procurement officers second."],
      ["Demand:", " thought leadership, white papers and case studies from the Early Adopters; possible channel partners (for example Everest Group, boutique cost-reduction firms)."],
    ],
    visual: "A two-stage timeline.",
    source: "Pitch Deck v1.1 (go-to-market); Business Plan v1.5 (medium and longer-term go-to-market)." },

  { id: "B4", title: "Financial model",
    headline: "Profitable within [year], on a path to $200MM in revenue.",
    points: [
      "Business Plan v1.5 (CAD): profitable in Q3 2027 on 8 clients at $4MM each; profitable at 5 clients.",
      "2030 exit run rate: revenue $200MM; profit before tax $100MM+; 50 clients.",
      "Costs exiting 2030: consulting practice about $24MM, AI and software development about $26.5MM, sales about $15MM, other overhead about $10MM.",
      "Base case: $30MM in costs over the first two years; sensitivity suggests $10 to 12MM. Investment is paced to Early Adopter traction.",
    ],
    visual: "Revenue and client ramp to 2030; the cost stack.",
    source: "Business Plan v1.5 (preliminary financial model; funding ask); Business Plan deck v1.4 slide 12.",
    flag: "See decisions 2 and 3. The model’s start date (July 1, 2026) has passed." },

  { id: "B5", title: "The ask",
    headline: "[Amount] to take a working prototype into the first consortium.",
    points: [
      "Pitch Deck v1.1: $1MM through a SAFE (pre-seed), funding a 3 to 4 month runway for Value Validation with 4 to 5 Early Adopters and generating $2 to 2.5MM in revenue that is reinvested; it funds the founding team and the first two engagement pods (2 engagement managers, 4 associates).",
      "What has changed since: the prototype exists, the document library is assembled, and TWM’s Azure environment is being set up. The money goes to the first engagements, not to proving the idea.",
      "Next round: a Series A to build the broader platform [timing; decision 5].",
    ],
    visual: "Use of funds; the milestones the round buys.",
    source: "Pitch Deck v1.1 (the ask; traction); project folder.",
    flag: "See decision 5." },
];

const appendix = [
  { id: "X1", title: "How the pipeline works (for technical readers)",
    points: [
      ["Six stages:", " intake (identity, true file type, label, contract-set links, readiness); reading (text and tables with positions); extraction (typed records, every number verified against the page, abstain when unsure); normalization (role framework, resolve once, a model step only above a confidence floor, otherwise the queue); the ledger (append, never overwrite; confidence decides what counts); benchmarking and findings."],
      "Rates are stored as stated, in their own currency and unit; any conversion is a separate column with the exchange rate and its date.",
      "Every rate carries its effective date, its source and its source class (public, consortium, synthetic); synthetic data never enters the ledger.",
      "Evaluation is federated: answer sheets stay in client tenants and only scores leave. Precision is weighted over recall.",
    ],
    source: "CLAUDE.md; docs/architecture-components.md; docs/architecture-decisions.md." },
  { id: "X2", title: "The Azure stack",
    points: [
      "Blob Storage for documents; Document Intelligence for scanned files; Foundry for the models; PostgreSQL for the ledger; AI Search for similar titles; Container Apps or Functions for the pipeline; Key Vault for secrets; Bicep scripts install it all, in Canada Central.",
      "Rehearsed in TWM’s own environment until a clean subscription becomes a working environment in under an hour.",
    ],
    source: "docs/architecture-components.md (Azure set-up)." },
  { id: "X3", title: "Terms used",
    points: [
      ["Contracted rate:", " the price a statement of work or master agreement says a vendor may charge for a role. Example: $83.00 per hour for an Advanced Systems Engineer, onsite, year 1."],
      ["Contract set:", " the documents that belong to one contract. Example: the seven Texas Accenture files."],
      ["Document library:", " the real public documents gathered to build and test the platform."],
      ["Ledger:", " the book of record of every rate seen, with its source."],
      ["Mapping table:", " vendor titles already resolved to a role and seniority, with the reasoning and who decided."],
      ["Benchmark cut:", " one combination of role, seniority, location and technology."],
    ],
    source: "CLAUDE.md terms; docs/story/follow-one-rate.html." },
];

// ---------------------------------------------------------------- layout helpers
const FONT = "Arial";
const children = [];
const run = (text, o = {}) => new TextRun({ text, font: FONT, ...o });
const para = (runs, o = {}) => new Paragraph({ children: Array.isArray(runs) ? runs : [runs], spacing: { after: 100 }, ...o });

function bullet(item, level = 0) {
  const runs = Array.isArray(item) ? [run(item[0], { bold: true }), run(item[1])] : [run(item)];
  return new Paragraph({ children: runs, numbering: { reference: "bullets", level }, spacing: { after: 60 } });
}
function points(list) {
  for (const p of list) {
    const isObj = p !== null && typeof p === "object" && !Array.isArray(p);  // strings have a built-in .sub(), so test the type first
    if (isObj && p.label) children.push(new Paragraph({ children: [run(p.label, { bold: true, color: "1F3864" })], spacing: { before: 80, after: 40 }, keepNext: true }));
    else if (isObj && p.sub) p.sub.forEach((s) => children.push(bullet(s, 1)));
    else children.push(bullet(p, 0));
  }
}
function labelLine(label, text, o = {}) {
  return new Paragraph({ children: [run(label + " ", { bold: true, ...o }), run(text, o)], spacing: { before: 60, after: 60 } });
}
function flagBox(text) {
  return new Paragraph({
    children: [run("For Kyle: ", { bold: true }), run(text)],
    shading: { type: ShadingType.CLEAR, color: "auto", fill: "FFF2CC" },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: "BF9000", space: 6 } },
    spacing: { before: 80, after: 120 }, indent: { left: 120 },
  });
}
function slide(s) {
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [run(`Slide ${s.id}: ${s.title}`)] }));
  if (s.headline) children.push(labelLine("Headline:", s.headline, { color: "1F3864" }));
  points(s.points);
  if (s.visual) children.push(labelLine("Visual:", s.visual, { size: 20 }));
  if (s.source) children.push(new Paragraph({ children: [run("Source: " + s.source, { italics: true, size: 18, color: "666666" })], spacing: { after: 80 } }));
  if (s.flag) children.push(flagBox(s.flag));
}
const h1 = (t) => children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [run(t)] }));

// ---------------------------------------------------------------- document body
children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [run("Akerlow: pitch deck narrative")] }));
children.push(para(run(`Draft for Kyle to review and edit, ${DATE}. Working name: Akerlow.`, { color: "444444" })));
children.push(para([
  run("One deck for two audiences: an Early Adopter CIO and investors. A shared core (slides 1 to 19) is followed by two short endings, one for each audience (A1 to A4, B1 to B5), and an appendix. Everything is in point form, slide by slide: the headline each slide must land, its points, the visual, and where the material comes from. "),
  run("Yellow boxes", { bold: true }), run(" mark decisions only Kyle can make; they are collected in the first section. Once Kyle has edited this document, the PowerPoint is built from it."),
]));
children.push(para(run("Sources: Business Plan v1.5 (Word, January 27, 2026); Consortium Approach v1.7 (January 20, 2026); Pitch Deck investor narrative v1.1 (March 1, 2026); Early Adopter Presentation v2 (November 10, 2025); the Business Plan slide deck v1.4 (October 2025, for layout only); and the project folder for everything built, measured on November 22, 2026. Where the business documents and later architecture decisions disagree, the architecture decisions win.", { size: 20, color: "444444" })));

h1("Decisions needed before the deck is built");
decisions.forEach((d) => children.push(new Paragraph({ children: [run(d[0], { bold: true }), run(d[1])], numbering: { reference: "decisions", level: 0 }, spacing: { after: 80 } })));

h1("The deck at a glance");
const mapRows = [
  ...core.map((s) => [s.id, s.title, "Both"]),
  ...endingA.map((s) => [s.id, s.title, "Early Adopter CIO"]),
  ...endingB.map((s) => [s.id, s.title, "Investors"]),
  ...appendix.map((s) => [s.id, s.title, "Appendix"]),
];
const W = [900, 6260, 2200];
const cell = (text, i, header) => new TableCell({
  width: { size: W[i], type: WidthType.DXA },
  shading: header ? { type: ShadingType.CLEAR, color: "auto", fill: "D9E2F3" } : undefined,
  margins: { top: 40, bottom: 40, left: 100, right: 100 },
  children: [new Paragraph({ children: [run(text, { bold: !!header, size: 20 })] })],
});
children.push(new Table({
  width: { size: W.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: W,
  rows: [new TableRow({ tableHeader: true, children: ["#", "Slide", "For"].map((t, i) => cell(t, i, true)) }),
         ...mapRows.map((r) => new TableRow({ children: r.map((t, i) => cell(t, i, false)) }))],
}));

h1("The core: slides 1 to 19 (both audiences)");
core.forEach(slide);
h1("Ending A: the Early Adopter CIO");
endingA.forEach(slide);
h1("Ending B: investors");
endingB.forEach(slide);
h1("Appendix");
appendix.forEach(slide);

// ---------------------------------------------------------------- document
const doc = new Document({
  creator: "Claude Code for Kyle McNamara",
  title: "Akerlow pitch deck narrative",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 44, bold: true, color: "1F3864" }, paragraph: { spacing: { before: 0, after: 120 }, keepNext: true } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 32, bold: true, color: "1F3864" }, paragraph: { spacing: { before: 360, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 26, bold: true, color: "2E75B6" }, paragraph: { spacing: { before: 280, after: 80 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bullets", levels: [
      { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
      { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 270 } } } },
    ] },
    { reference: "decisions", levels: [
      { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } },
    ] },
  ] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [run(`Akerlow pitch narrative, draft for Kyle, ${DATE}. Confidential.`, { size: 16, color: "888888" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [run("Page ", { size: 16, color: "888888" }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "888888" })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes"); });
