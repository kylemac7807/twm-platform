// Builds the short pitch deck narrative (6 to 8 pages) for Kyle's review: docs/story/pitch-deck-narrative.docx.
// The fuller version with visuals and sources per slide is built by build_pitch_narrative_docx.js.
// Usage: node build_pitch_narrative_short_docx.js <output.docx>   (needs the npm package "docx")
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, LevelFormat,
  ShadingType, BorderStyle, Footer, Header, PageNumber,
} = require("docx");

const OUT = process.argv[2] || "pitch-deck-narrative.docx";
const DATE = "November 22, 2026";

const decisions = [
  ["Fee.", " Early Adopter fee: $300k, $500k or $1.5MM? Your three documents give different figures."],
  ["Dates.", " Every milestone in the documents has passed. A new timeline is needed."],
  ["Profitability.", " Q3 2027 (Business Plan) or 2026 (Pitch Deck)?"],
  ["Target market.", " $100MM+ or $200MM+ in third-party labour spend?"],
  ["The ask.", " Still a $1MM SAFE, with a Series A in early 2027?"],
  ["Team.", " Names for the additional leadership, or “to be announced”?"],
  ["The real example.", " Show the Texas contract with Accenture by name, or as “a global systems integrator”?"],
  ["“Train”.", " No model has been trained, so the draft says the system is taught, through the role framework and analyst decisions. Agree?"],
  ["Name.", " Akerlow throughout, as the working name?"],
];

// slide: n, title, headline, points (string | [bold, rest]), flag
const core = [
  { n: "1", title: "Title",
    visual: "The name and tagline over a faint crop of the real Texas page with its boxed row.",
    headline: "Akerlow (working name). Every rate you pay, traced to the page it came from.",
    points: ["An AI platform and specialist consulting practice that cuts third-party technology labour spend by 10 to 15%."] },
  { n: "2", title: "The short version",
    visual: "Four boxes: the problem, what we do, the prize, the proof.",
    headline: "Enterprises overpay for technology contractors because the vendor sees every price and the client sees one contract at a time. Akerlow closes that gap.",
    points: [
      "Third-party technology labour costs each large Canadian bank over $1.5B a year, and the leakage is buried in contracts, invoices and timesheets that nobody links.",
      "Akerlow reads them, builds one traceable record of every rate, benchmarks each rate, and finds savings of 10 to 15%.",
      "Consultants deliver it first; the software takes on more each year. Early Adopters join a consortium of 4 to 5 organizations.",
      "Already built: a library of 438 real contracts, a framework of 129 roles, and a working prototype.",
    ] },
  { n: "3", title: "A large spend, managed in spreadsheets",
    visual: "An infographic: the 50/50 split, the $1.5B, and the thousands, hundreds and 20+.",
    headline: "Third-party technology labour is one of the largest and least managed lines in a technology budget.",
    points: [
      "Labour is 50 to 75% of technology cost, and about half of it is bought from vendors: 25 to 40% of the whole technology budget.",
      "Thousands of contractors, hundreds of contracts, 20 or more vendors, managed in spreadsheets.",
      "Procurement, finance, HR and technology each see a slice. Nobody sees the whole.",
    ] },
  { n: "4", title: "Why: an information gap",
    visual: "Two panels: the vendor\u2019s view of every client\u2019s rates; the client\u2019s view of one contract.",
    headline: "The vendor sees everything; the client sees fragments.",
    points: [
      "George Akerlof, the Nobel economist, showed that when one side of a market knows far more than the other, that side sets the price. Akerlow is a nod to him.",
      "The vendor knows what every client pays. The client sees one statement of work at a time, each defining roles, seniority, rate units and price increases in its own way.",
      "So the client cannot tell a fair rate from an inflated one, and fair pricing cannot win. Nobody has to behave badly; the gap does it on its own.",
    ] },
  { n: "5", title: "Where the money leaks, and what it is worth",
    visual: "Price \u00d7 mix, with the leaks under each; the $150MM+ as the hero number.",
    headline: "10 to 15% of third-party spend: $150MM or more a year for one large bank.",
    points: [
      ["Price:", " rates negotiated one contract at a time, premiums for roles “not on the rate card”, inflated seniority, and invoices never reconciled to timecards or to the contract."],
      ["Mix:", " the balance of employees and contractors, onshore and offshore, senior and junior drifts away from strategy through thousands of local decisions."],
      "The first 5 to 10% comes from price, a further 5 to 15% from mix. For a $150MM opportunity, every week of delay costs about $3MM.",
    ] },
  { n: "6", title: "Why existing tools do not fix it",
    visual: "Columns for each kind of tool and its gap, with Akerlow spanning them.",
    headline: "Every tool sees one slice. None links the timecard to the invoice to the contracted rate.",
    points: [
      "HR, procurement and IT finance systems (Workday, SAP Ariba, Fieldglass, Apptio) hold pieces of the picture, but not comparable rates or the leakage.",
      "Benchmark providers (ISG, Gartner) cannot be lined up against your own statements of work.",
      "General-purpose AI does not hold your contracts, a role framework or peer benchmarks, and it cannot be allowed to guess.",
    ] },
  { n: "7", title: "What Akerlow does",
    visual: "Documents in, the ledger in the middle, benchmarks and savings out.",
    headline: "It turns contracts, invoices and timesheets into one traceable record of every rate, and that record into savings.",
    points: [
      "Reads every document as it arrives and records each rate exactly as written, with its page and position.",
      "Maps every vendor title to one role framework, so rates become comparable, then benchmarks them against your own contracts, your other vendors and the market.",
      "Stacks the savings so nothing is counted twice: contractual, then operational, then market alignment.",
    ] },
  { n: "8", title: "Follow one rate from the page to the ledger",
    visual: "The follow-one-rate page: six stages, the boxed row on page 8.",
    headline: "One real rate from a signed Texas contract, through six stages.",
    points: [
      "“Advanced Systems Engineer, $83.00 per hour”, on page 8 of a seven-file contract set.",
      "Read, checked against the page, mapped to Systems Engineer, senior, and stored with its page and position.",
      "Nothing in the ledger is an estimate. A vendor who challenges a rate is shown the page.",
    ] },
  { n: "9", title: "What it refuses to guess",
    visual: "The flagged row from the follow-one-rate page.",
    headline: "When the system is not sure, it asks.",
    points: [
      "“Operations, $99.50 per hour” names no role. The model abstained, and the row waits for an analyst: stored, but not counted.",
      "No default seniority and no guessed location. Every analyst decision becomes a rule, so no question is asked twice.",
      "One false claim of overbilling can lose an engagement; a missed saving is caught at the next refresh.",
    ] },
  { n: "10", title: "What the client gets",
    visual: "The two executive views beside one traced ledger row.",
    headline: "A book of record, benchmarks at the right cut, and savings that hold up in a negotiation.",
    points: [
      "The ledger: every contracted rate, every contract year and every clause that changes a rate, each traced to its page.",
      "Benchmarks by role, seniority, location and technology, shown as ranges and published only above a confidentiality floor.",
      "Two executive views: the Role Composition Heatmap and the Total Potential Dashboard, with observed and projected savings kept separate.",
    ],
    flag: "The dashboards are designed, not built. Any mock-up must be labelled illustrative." },
  { n: "11", title: "Your data stays home",
    visual: "Two zones, the client\u2019s environment and the shared tier, with the gate between.",
    headline: "Akerlow is installed inside each client’s own Azure environment.",
    points: [
      "Contracts, rates and vendor relationships never leave it.",
      "Only the shared vocabulary and anonymized benchmark summaries leave, each backed by at least three observations from at least two clients; vendors appear only as a class.",
      "Every contract set is checked for disclosure restrictions before anything is benchmarked.",
    ] },
  { n: "12", title: "What we own, what we rent",
    visual: "Two columns, rent and own, and the flywheel of clients, vocabulary and benchmark.",
    headline: "We rent the best AI models and own what makes them reliable.",
    points: [
      ["Rented:", " frontier models through Microsoft Foundry, with Claude primary and GPT benchmarked, so there is no lock-in to one AI vendor."],
      ["Owned:", " the role framework, the mapping table, the page checks, the inventory of rate-changing fine print, the evaluation sets and the consortium benchmark."],
      ["The moat:", " a benchmark built from data no one else can see, improving with every client."],
    ] },
  { n: "13", title: "Built so far (1 of 3): the document library",
    headline: "Before any client data, we assembled 438 real public documents to build and test against.",
    visual: "A grid of the sources with their counts and one sample page from each.",
    points: [
      "About 240 contracts that US public companies filed with the securities regulator: master agreements, amendments and statements of work.",
      "Government contracts with rates visible: five Texas contract sets and thirteen Michigan contracts, including a $109M, 13-year Deloitte contract and an $800M staff-augmentation programme.",
      "UK: 48 signed government contracts and the rate cards of 13 major vendors (about 2,600 priced rows, January 2026). Canada: federal TBIPS packages, 12 of them French or bilingual.",
      "The rarest find: a public invoice with the timesheets behind it, the raw material for checking billing against work done.",
    ] },
  { n: "14", title: "Built so far (2 of 3): teaching the system the language of technology labour",
    headline: "We built our own role framework and taught the system to place any vendor title in it, or to ask.",
    visual: "The framework as families and bands; the unseen-title test as before-and-after bars.",
    points: [
      "129 roles in 18 families and four seniority bands, built from open public sources (US O*NET, the UK government\u2019s job ladders, Canada\u2019s TBIPS categories). Location and technology are recorded beside the role.",
      "547 vendor titles mapped, each with its reasoning, who decided, and a version.",
      "On 113 titles it had never seen: 40.7% placed by the rules alone, 95.6% after one review pass by Kyle. It learns from decisions, not from retraining a model.",
    ] },
  { n: "15", title: "Built so far (3 of 3): a working prototype",
    headline: "The whole pipeline runs end to end on real contracts today, before any cloud spend.",
    visual: "A screenshot of the workbench beside the traced Texas row.",
    points: [
      "Three real contract sets through every stage: Texas Accenture (seven files), Accenture UK and Michigan Deloitte. Every rate is traced to its page; one Texas pricing table alone yields 1,648 verified rates across eight contract years.",
      "1,034 contract terms read (escalation, discounts, expenses), each quote proven word for word on its page.",
      "An analyst workbench: the review queue, any rate clicked through to its page, every answer recorded with who and why.",
      "About $6.50 of model spend for the full Texas and Michigan runs; 166 automated tests.",
    ] },
  { n: "16", title: "What comes next, and what we do not claim yet",
    headline: "The core works. These are the next steps, and the numbers we will not claim until they are measured.",
    visual: "A simple timeline: built, next, then.",
    points: [
      ["Next:", " the whole library through the pipeline; accuracy measured against hand-checked answer sheets; benchmarking, findings and savings; then TWM\u2019s Azure environment and the first client installation."],
      ["Not claimed yet:", " no accuracy figure until the answer sheets are hand-checked, and no savings figure until the findings are built."],
    ] },
  { n: "17", title: "Roadmap",
    visual: "A three-phase arc.",
    headline: "From an audit to the whole technology workforce.",
    points: [
      ["Phase 1:", " the audit and the Master Benchmark Ledger."],
      ["Phase 2:", " workforce planning: the demand pipeline, scenarios for the mix, and forecasts linked to approvals."],
      ["Later:", " all labour, financial management, onboarding and vendor compliance. Consulting-led first, self-serve over time."],
    ] },
  { n: "18", title: "The team",
    visual: "Kyle\u2019s photo with three career facts; the Year 1 organization chart.",
    headline: "Led by an executive who has managed this problem from the inside.",
    points: [
      "Kyle McNamara: TD Bank (6,200+ staff, $1.8B+ budget); National Australia Bank, Chief Transformation Officer ($1B+ in cost reductions, much of it third-party labour); Scotiabank ($1.5B+ IT budget, 5,000+ staff).",
      "A consulting practice of ex-McKinsey and ex-BCG consultants in engagement pods, and a platform team in AI, software, security and product.",
      "Additional leadership to be announced.",
    ] },
];

const endingA = [
  { n: "A1", title: "The Early Adopter consortium",
    visual: "The consortium as a ring of members around the shared benchmark.",
    headline: "Four to five leading organizations, transforming their technology workforce together.",
    points: [
      "Savings of 10 to 15%, and a prioritized list of value levers from your own contracts and workforce data.",
      "Proprietary benchmarks of labour rates and workforce mix against peers, and consortium workshops on leading practice.",
      "A seat at the table: members shape the product\u2019s features and priorities.",
      "Confidential by design: no member sees another\u2019s data.",
    ] },
  { n: "A2", title: "How it runs",
    headline: "Value Validation in 4 to 6 months, then Execution, then Capability Development.",
    visual: "The three-phase framework from the Consortium Approach.",
    points: [
      ["Value Validation:", " an opportunity assessment that quantifies the full potential; benchmarking against peers; quick wins such as renegotiating statements of work; a target state for the workforce and a roadmap."],
      ["Execution:", " deeper analysis, recommendations on contracts and mix, and progress tracked on dashboards."],
      ["Capability Development:", " tools in place, processes standardized, internal capability built, benchmarks refreshed."],
    ] },
  { n: "A3", title: "What we ask, what we bring",
    visual: "Two columns: the member, Akerlow.",
    headline: "A committed sponsor and access to the documents; in return, a dedicated team and the platform.",
    points: [
      ["Members:", " a CIO sponsor and a dedicated leader; procurement, HR and finance at the table; access to statements of work, invoices and timecards."],
      ["Akerlow:", " hands-on leadership, a pod for each member, and the platform running inside your environment."],
    ] },
  { n: "A4", title: "Commercials, and why join now",
    visual: "An offer box and a timeline.",
    headline: "Founding members get the deepest discount, the earliest benchmarks and the most influence.",
    points: [
      "Fee: [decision 1], heavily discounted against a McKinsey team (about $1.5MM a month).",
      "Why now: shape the product, see the benchmarks first, and start saving within months. Every week of delay costs about $3MM on a $150MM opportunity.",
    ] },
];

const endingB = [
  { n: "B1", title: "The market",
    visual: "Market rings and the top seven providers by headcount.",
    headline: "A very large spend with no purpose-built solution.",
    points: [
      "IT services spend of $1.87 trillion in 2026 (Gartner, IDC); the top seven providers employ about 3 million people.",
      "1,500+ organizations with large third-party labour spend, half of them in North America and 400+ in North American financial services and telecom [threshold: decision 4]. Goal: 50+ clients.",
    ] },
  { n: "B2", title: "Business model",
    headline: "Revenue tied to the savings we create.",
    visual: "Revenue per client as a share of savings; the shift from consulting to software over time.",
    points: [
      "$20MM of savings generates $2 to 3MM of revenue; 50 clients at an average of $4MM is $200MM of recurring revenue.",
      "Recurring because savings must be sustained: refreshes, benchmark access, then Phase 2 workflows built into how clients plan their workforce.",
      "Consulting-led first, software-led as the platform matures.",
    ] },
  { n: "B3", title: "Go-to-market",
    headline: "Early Adopters first, then a sales-led expansion.",
    visual: "A two-stage timeline.",
    points: [
      ["Months 1 to 12:", " the Early Adopter consortium, through the leadership team\u2019s executive network."],
      ["Years 2 to 3:", " enterprise sales with 4 to 8 week pilots across North American financial services and telecom; CIOs first, chief procurement officers second; case studies from the Early Adopters."],
    ] },
  { n: "B4", title: "Financial model",
    visual: "Revenue and client ramp to 2030; the cost stack.",
    headline: "Profitable early, on a path to $200MM.",
    points: [
      "Profitable in Q3 2027 on 8 clients, and profitable at 5 [decision 3]. 2030 run rate: $200MM revenue, $100MM+ profit before tax, 50 clients.",
      "First two years: $30MM of costs in the base case, $10 to 12MM in the leaner case, paced to traction.",
    ] },
  { n: "B5", title: "The ask",
    visual: "Use of funds and the milestones the round buys.",
    headline: "[Amount, decision 5] to take a working prototype into the first consortium.",
    points: [
      "The Pitch Deck’s $1MM SAFE funded Value Validation with 4 to 5 Early Adopters and the first two engagement pods.",
      "The prototype already exists, so the money goes into the first engagements, not into proving the idea.",
    ] },
];

// ---------------------------------------------------------------- layout
const FONT = "Arial";
const children = [];
const run = (text, o = {}) => new TextRun({ text, font: FONT, ...o });
const bullet = (item) => new Paragraph({
  children: Array.isArray(item) ? [run(item[0], { bold: true }), run(item[1])] : [run(item)],
  numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 },
});
function slide(s) {
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [run(`${s.n}. ${s.title}`)] }));
  children.push(new Paragraph({ children: [run(s.headline, { bold: true, color: "1F3864" })], spacing: { after: 60 } }));
  s.points.forEach((p) => children.push(bullet(p)));
  if (s.visual) children.push(new Paragraph({ children: [run("Visual: ", { bold: true, size: 18, color: "666666" }), run(s.visual, { italics: true, size: 18, color: "666666" })], spacing: { before: 40, after: 60 } }));
  if (s.flag) children.push(new Paragraph({
    children: [run("For Kyle: ", { bold: true }), run(s.flag)],
    shading: { type: ShadingType.CLEAR, color: "auto", fill: "FFF2CC" },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: "BF9000", space: 6 } },
    spacing: { before: 60, after: 80 }, indent: { left: 120 },
  }));
}
const h1 = (t) => children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [run(t)] }));

children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [run("Akerlow: pitch deck narrative")] }));
children.push(new Paragraph({ spacing: { after: 120 }, children: [run(
  `Draft for Kyle’s review, ${DATE}. One deck, two audiences: a shared core, then a short ending for an Early Adopter CIO and one for investors. ` +
  "Each slide has its headline, its points and a suggested visual. A fuller version, with the sources for every slide, is in pitch-deck-narrative-detailed.docx.",
  { color: "444444" })] }));

h1("Decisions for Kyle");
decisions.forEach((d) => children.push(new Paragraph({ children: [run(d[0], { bold: true }), run(d[1])], numbering: { reference: "decisions", level: 0 }, spacing: { after: 40 } })));

h1("The core (both audiences)");
core.forEach(slide);
h1("Ending A: the Early Adopter CIO");
endingA.forEach(slide);
h1("Ending B: investors");
endingB.forEach(slide);

children.push(new Paragraph({ spacing: { before: 240 }, children: [run(
  "Sources: Business Plan v1.5 (January 27, 2026); Consortium Approach v1.7 (January 20, 2026); Pitch Deck v1.1 (March 1, 2026); Early Adopter Presentation v2 (November 10, 2025); " +
  "the project folder for everything built, measured November 22, 2026. Where the business documents and later architecture decisions disagree, the architecture decisions win.",
  { italics: true, size: 18, color: "666666" })] }));

const doc = new Document({
  creator: "Claude Code for Kyle McNamara",
  title: "Akerlow pitch deck narrative",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 40, bold: true, color: "1F3864" }, paragraph: { spacing: { before: 0, after: 100 }, keepNext: true } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 30, bold: true, color: "1F3864" }, paragraph: { spacing: { before: 300, after: 120 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 24, bold: true, color: "2E75B6" }, paragraph: { spacing: { before: 200, after: 40 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: "decisions", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [run(`Akerlow pitch narrative, draft for Kyle, ${DATE}. Confidential.`, { size: 16, color: "888888" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [run("Page ", { size: 16, color: "888888" }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "888888" })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes"); });
