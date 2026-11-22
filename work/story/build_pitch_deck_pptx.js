// Builds docs/story/twm-pitch-deck.pptx from docs/story/pitch-deck-narrative-v2.docx (Kyle's decisions of Nov 22, 2026 applied).
// Usage: node build_pitch_deck_pptx.js <output.pptx> <pptx skill scripts/apply_theme.js> <image folder from collect_facts.py>
// Needs the npm package "pptxgenjs" on NODE_PATH.
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.argv[3]);
const OUT = process.argv[2] || "twm-pitch-deck.pptx";
const IMG = process.argv[4];

const HEX = {
  dk1: "1B1B1B", lt1: "FFFFFF", dk2: "1E3B33", lt2: "EEF3F0",
  accent1: "C8963E", accent2: "2F6B5A", accent3: "7FA394", accent4: "D9C29A", accent5: "5B6770", accent6: "A44A3F",
};
const THEME = {
  name: "TWM Ledger", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { ...HEX, hlink: "2F6B5A", folHlink: "7FA394" },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "TWM";
pres.author = "Kyle McNamara";
const C = pres.SchemeColor;
const S = pres.shapes;
const W = 13.333, L = 0.6, R = W - 0.6, CW = R - L; // content width 12.133

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "TITLE",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.9, w: 7.0, h: 1.4, fontSize: 66, bold: true, color: C.background1, margin: 0, align: "left", valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "subtitle", type: "body", x: 0.8, y: 3.45, w: 7.0, h: 0.9, fontSize: 24, color: C.accent4, margin: 0, align: "left", valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "SECTION",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.5, w: 11.7, h: 1.2, fontSize: 44, bold: true, color: C.background1, margin: 0, align: "left", valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "subtitle", type: "body", x: 0.8, y: 3.85, w: 11.7, h: 0.8, fontSize: 22, color: C.accent4, margin: 0, align: "left", valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: L, y: 0.35, w: CW, h: 0.7, fontSize: 36, bold: true, color: C.text2, margin: 0, align: "left", valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "headline", type: "body", x: L, y: 1.08, w: CW, h: 0.72, fontSize: 18, color: C.accent2, margin: 0, align: "left", valign: "top" }, text: "" } },
    { text: { text: "TWM  |  Confidential draft", options: { x: L, y: 7.02, w: 6, h: 0.3, fontSize: 10, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: R - 0.6, y: 7.02, w: 0.6, h: 0.3, fontSize: 10, color: C.accent5, align: "right" },
});

// ---------------------------------------------------------------- helpers (fresh option objects on every call)
let section = "";
function content(title, headline, notes) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  s.addText(headline, { placeholder: "headline" });
  if (notes) s.addNotes(notes);
  return s;
}
function divider(title, subtitle) {
  const s = pres.addSlide({ masterName: "SECTION", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  s.addText(subtitle, { placeholder: "subtitle" });
  return s;
}
function txt(s, t, o) {
  s.addText(t, Object.assign({ margin: 0, isTextBox: true, valign: "top", fontSize: 14, color: C.text1 }, o));
}
function card(s, x, y, w, h, name, dark) {
  s.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: dark ? C.text2 : C.background2 }, line: { color: dark ? C.text2 : C.background2 }, objectName: name });
}
function num(s, x, y, n, d) {
  const dd = d || 0.45;
  s.addShape(S.OVAL, { x, y, w: dd, h: dd, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `Number ${n}` });
  s.addText(String(n), { x, y, w: dd, h: dd, fontSize: 16, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
}
function bullets(s, items, o) {
  s.addText(items.map((it, i) => ({ text: it, options: { bullet: true, breakLine: i < items.length - 1 } })),
    Object.assign({ margin: 0, isTextBox: true, valign: "top", fontSize: 14, color: C.text1, paraSpaceAfter: 6 }, o));
}
function stat(s, x, y, w, big, label, o) {
  const opt = o || {};
  txt(s, big, { x, y, w, h: opt.bigH || 0.8, fontSize: opt.size || 40, bold: true, fontFace: "Cambria", color: opt.dark ? C.background1 : C.text2, valign: "bottom" });
  txt(s, label, { x, y: y + (opt.bigH || 0.8) + 0.08, w, h: opt.labelH || 0.8, fontSize: 14, color: opt.dark ? C.background1 : C.text1 });
}
function arrow(s, x, y, w, h) {
  s.addShape(S.RIGHT_ARROW, { x, y, w: w || 0.42, h: h || 0.42, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: "Arrow" });
}
const chartText = { catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt" };

// ================================================================= CORE
section = "Core: both audiences";
pres.addSection({ title: section });

// 1. Title
{
  const s = pres.addSlide({ masterName: "TITLE", sectionTitle: section });
  s.addImage({ path: path.join(IMG, "page8_full.png"), x: 8.3, y: 0.3, w: 5.25, h: 6.79, transparency: 70, altText: "Page 8 of a Texas pricing attachment with one row boxed", objectName: "Page 8" });
  s.addText("TWM", { placeholder: "title" });
  s.addText("Every rate you pay, traced to the page it came from.", { placeholder: "subtitle" });
  txt(s, "An AI platform and specialist consulting practice that cuts third-party technology labour spend by 10 to 15%.", { x: 0.8, y: 4.55, w: 6.6, h: 0.9, fontSize: 18, color: C.background1 });
  txt(s, "Kyle McNamara  |  November 2026  |  Confidential draft", { x: 0.8, y: 6.55, w: 6.6, h: 0.35, fontSize: 12, color: C.accent4 });
  s.addNotes("Sources: tagline new (Nov 22); 10 to 15% from Business Plan v1.5 and Pitch Deck v1.1. The faint page behind the title is the real Texas page 8 with the traced row boxed.");
}

// 2. The short version
{
  const s = content("The short version", "Enterprises overpay because the vendor sees every price and the client sees one contract at a time. TWM closes that gap.",
    "Sources: Business Plan v1.5 executive summary; Pitch Deck v1.1; Consortium Approach v1.7 slide 2; project folder measured Nov 22, 2026.");
  const items = [
    ["The problem", "Third-party technology labour costs each large Canadian bank over $1.5B a year, and the leakage is buried in contracts, invoices and timesheets that nobody links."],
    ["What we do", "TWM reads them, builds one traceable record of every rate, benchmarks each rate, and finds the savings."],
    ["The prize", "Savings of 10 to 15% of third-party spend. Consultants deliver first; the software takes on more each year."],
    ["The proof", "A library of 438 real contracts, a framework of 129 roles, and a working prototype."],
  ];
  const cw = (CW - 0.33) / 2, ch = 2.3;
  items.forEach((it, i) => {
    const x = L + (i % 2) * (cw + 0.33), y = 2.0 + Math.floor(i / 2) * (ch + 0.25);
    card(s, x, y, cw, ch, `Card ${it[0]}`);
    num(s, x + 0.3, y + 0.3, i + 1);
    txt(s, it[0], { x: x + 0.95, y: y + 0.3, w: cw - 1.25, h: 0.45, fontSize: 20, bold: true, color: C.text2, valign: "middle" });
    txt(s, it[1], { x: x + 0.95, y: y + 0.85, w: cw - 1.25, h: ch - 1.05, fontSize: 15 });
  });
}

// 3. A large spend
{
  const s = content("A large spend, managed in spreadsheets", "Third-party technology labour is one of the largest and least managed lines in a technology budget.",
    "Sources: Pitch Deck v1.1 (problem; the Canadian bank benchmark; the 50/50 split; the fragmentation factor); Consortium Approach v1.7 slide 3.");
  const cw = (CW - 2 * 0.3) / 3;
  [["50–75%", "of technology cost is labour"],
   ["25–40%", "of the whole technology budget sits in vendor contracts, at a roughly 50:50 split of employees and contractors"],
   ["$1.5B+", "a year in third-party technology labour at each large Canadian bank"]].forEach((it, i) => {
    const x = L + i * (cw + 0.3);
    card(s, x, 2.0, cw, 2.45, `Stat ${i + 1}`);
    stat(s, x + 0.35, 2.15, cw - 0.7, it[0], it[1], { size: 48, bigH: 0.95, labelH: 1.2 });
  });
  [["Thousands", "of contractors"], ["Hundreds", "of contracts and statements of work"], ["20+", "vendors"]].forEach((it, i) => {
    const x = L + i * (cw + 0.3);
    txt(s, it[0], { x, y: 4.75, w: cw, h: 0.55, fontSize: 28, bold: true, fontFace: "Cambria", color: C.accent1 });
    txt(s, it[1], { x, y: 5.3, w: cw, h: 0.4, fontSize: 14 });
  });
  txt(s, "Managed in spreadsheets. Procurement, finance, HR and technology each see a slice; nobody sees the whole.", { x: L, y: 6.05, w: CW, h: 0.6, fontSize: 18, color: C.text2, bold: true });
}

// 4. Why: an information gap
{
  const s = content("Why: an information gap", "The vendor sees everything; the client sees fragments.",
    "Source: the approved Akerlow description (docs/story/naming.md, Nov 22, 2026), with the name reference removed because the deck says TWM.");
  const cw = (CW - 0.33) / 2;
  card(s, L, 2.0, cw, 3.45, "Vendor view", true);
  txt(s, "What the vendor sees", { x: L + 0.4, y: 2.25, w: cw - 0.8, h: 0.5, fontSize: 22, bold: true, color: C.background1 });
  bullets(s, ["What every client pays for the same role", "How its rates compare across all of them", "The full picture"], { x: L + 0.4, y: 2.95, w: cw - 0.8, h: 2.3, fontSize: 16, color: C.background1 });
  const x2 = L + cw + 0.33;
  card(s, x2, 2.0, cw, 3.45, "Client view");
  txt(s, "What the client sees", { x: x2 + 0.4, y: 2.25, w: cw - 0.8, h: 0.5, fontSize: 22, bold: true, color: C.text2 });
  bullets(s, ["One statement of work at a time", "Roles, seniority, rate units and price increases defined differently in every contract", "Complex terms and conditions: fragments"], { x: x2 + 0.4, y: 2.95, w: cw - 0.8, h: 2.3, fontSize: 16 });
  txt(s, "“When one side of a market knows far more than the other, that side sets the price.”  George Akerlof, Nobel laureate in economics", { x: L, y: 5.6, w: CW, h: 0.75, fontSize: 18, italic: true, fontFace: "Cambria", color: C.text2 });
  txt(s, "So the client cannot tell a fair rate from an inflated one, and fair pricing cannot win. Nobody has to behave badly; the gap does it on its own.", { x: L, y: 6.42, w: CW, h: 0.45, fontSize: 15 });
}

// 5. Where the money leaks
{
  const s = content("Where the money leaks, and what it is worth", "Total cost = price × mix. Both leak, and 10 to 15% of third-party spend is recoverable.",
    "Sources: Business Plan v1.5 (customer need; Phase 1 leakage; initial 5 to 10%, additional 5 to 15%); Early Adopter Presentation (price, quantity and mix); Pitch Deck v1.1 (Canadian bank benchmark; cost of delay $3MM a week on $150MM).");
  const lw = 7.3;
  card(s, L, 2.0, lw, 2.55, "Price");
  txt(s, "Price", { x: L + 0.35, y: 2.15, w: lw - 0.7, h: 0.45, fontSize: 20, bold: true, color: C.text2 });
  bullets(s, ["Rates negotiated one contract at a time", "Premiums for roles “not on the rate card”", "Inflated seniority", "Invoices never reconciled to timecards or to the contract"], { x: L + 0.35, y: 2.65, w: lw - 0.7, h: 1.8, fontSize: 15 });
  card(s, L, 4.75, lw, 1.95, "Mix");
  txt(s, "Mix", { x: L + 0.35, y: 4.9, w: lw - 0.7, h: 0.45, fontSize: 20, bold: true, color: C.text2 });
  txt(s, "The balance of employees and contractors, onshore and offshore, senior and junior drifts away from strategy through thousands of local decisions.", { x: L + 0.35, y: 5.4, w: lw - 0.7, h: 1.2, fontSize: 15 });
  const rx = L + lw + 0.5, rw = R - rx;
  stat(s, rx, 1.95, rw, "$150MM+", "a year for one large bank: 10 to 15% of $1.5B", { size: 54, bigH: 1.0, labelH: 0.6 });
  stat(s, rx, 3.7, rw, "5–10% + 5–15%", "from price first, then a further share from mix", { size: 30, bigH: 0.6, labelH: 0.6 });
  stat(s, rx, 5.05, rw, "$3MM a week", "the cost of delay on a $150MM opportunity", { size: 30, bigH: 0.6, labelH: 0.6 });
}

// 6. Why existing tools do not fix it
{
  const s = content("Why existing tools do not fix it", "Every tool sees one slice. None links the timecard to the invoice to the contracted rate.",
    "Sources: Business Plan v1.5 (competitive landscape; Appendix C); Business Plan deck v1.4 slide 4. The last column answers the Pitch Deck's note on why OpenAI or a consulting firm cannot solve this.");
  const tools = [
    ["HR systems", "Workday, Oracle", "Built around employees; vendor rates mostly absent."],
    ["Procurement and vendor management", "SAP Ariba, Fieldglass, VNDLY", "Hold the contracts, but do not normalize roles or find leakage."],
    ["IT finance", "Clarity, Apptio", "Budgets and allocations, not skills, location or seniority."],
    ["Benchmark providers", "ISG, Gartner", "Cannot be lined up against your own statements of work."],
    ["General-purpose AI", "Chat assistants", "Does not hold your contracts or peer benchmarks, and cannot be allowed to guess."],
  ];
  const gap = 0.22, cw = (CW - 4 * gap) / 5;
  tools.forEach((t, i) => {
    const x = L + i * (cw + gap);
    card(s, x, 2.0, cw, 3.55, `Tool ${i + 1}`);
    txt(s, t[0], { x: x + 0.22, y: 2.18, w: cw - 0.44, h: 0.85, fontSize: 17, bold: true, color: C.text2, valign: "bottom" });
    txt(s, t[1], { x: x + 0.22, y: 3.08, w: cw - 0.44, h: 0.35, fontSize: 12, color: C.accent5 });
    txt(s, t[2], { x: x + 0.22, y: 3.55, w: cw - 0.44, h: 1.85, fontSize: 14 });
  });
  card(s, L, 5.8, CW, 0.85, "Callout", true);
  txt(s, "None links the timecard to the invoice to the contracted rate. TWM does.", { x: L + 0.4, y: 5.8, w: CW - 0.8, h: 0.85, fontSize: 20, bold: true, color: C.background1, valign: "middle" });
}

// 7. What TWM does
{
  const s = content("What TWM does", "It turns contracts, invoices and timesheets into one traceable record of every rate, and that record into savings.",
    "Sources: Business Plan v1.5 (Phase 1 solution); docs/architecture-components.md; Pitch Deck v1.1 (product).");
  const steps = [
    ["Reads", "Contracts, statements of work, rate cards, invoices and timesheets, as they arrive."],
    ["Records", "Every rate exactly as written, with its page and position, in a ledger inside your environment."],
    ["Compares", "Maps every vendor title to one role framework, then benchmarks it against your contracts, your other vendors and the market."],
    ["Finds savings", "Stacked so nothing is counted twice: contractual, then operational, then market alignment."],
  ];
  const aw = 0.42, gap = 0.5, cw = (CW - 3 * gap) / 4;
  steps.forEach((st, i) => {
    const x = L + i * (cw + gap);
    card(s, x, 2.05, cw, 3.3, `Step ${i + 1}`);
    num(s, x + 0.3, 2.3, i + 1);
    txt(s, st[0], { x: x + 0.3, y: 2.9, w: cw - 0.6, h: 0.5, fontSize: 20, bold: true, color: C.text2 });
    txt(s, st[1], { x: x + 0.3, y: 3.45, w: cw - 0.6, h: 1.8, fontSize: 15 });
    if (i < 3) arrow(s, x + cw + (gap - aw) / 2, 3.5, aw, aw);
  });
  txt(s, "Consultants lead each engagement and work the edge cases; the software does more of the work every year.", { x: L, y: 5.75, w: CW, h: 0.6, fontSize: 18, bold: true, color: C.text2 });
}

// 8. Follow one rate
{
  const s = content("Follow one rate from the page to the ledger", "One real rate from a signed State of Texas contract with Accenture, through six stages.",
    "Source: docs/story/follow-one-rate.html and its PDF (pipeline run of Oct 6, 2026). The image is page 8 of Attachment 2.1, Pricing and Volumes, Texas contract DIR-STS-TSS-699; the red box is drawn from the position the ledger stores.");
  const stages = [
    ["Library", "Texas contract DIR-STS-TSS-699, page 8"],
    ["Intake", "Seven files, one contract set"],
    ["Reading", "A 111-row rate table, every cell's position"],
    ["Extraction", "“$83.00 per hour”, checked against the page"],
    ["Normalization", "Systems Engineer, senior, resolved once"],
    ["Ledger", "Stored with page 8 and its box"],
  ];
  const cw = CW / 6;
  stages.forEach((st, i) => {
    const x = L + i * cw;
    s.addShape(S.CHEVRON, { x, y: 2.0, w: i === 5 ? cw : cw + 0.05, h: 0.6, fill: { color: i === 5 ? C.accent1 : C.text2 }, line: { color: C.background1, width: 1 }, objectName: `Stage ${i + 1}` });
    txt(s, `${i + 1}  ${st[0]}`, { x: x + 0.42, y: 2.0, w: cw - 0.6, h: 0.6, fontSize: 14, bold: true, color: C.background1, valign: "middle" });
    txt(s, st[1], { x: x + 0.12, y: 2.72, w: cw - 0.2, h: 0.75, fontSize: 12, color: C.text1 });
  });
  s.addImage({ path: path.join(IMG, "page8_ase.png"), x: L, y: 3.65, w: CW, h: CW / 9.615, altText: "The Advanced Systems Engineer row on page 8, boxed in red", objectName: "Row on page 8" });
  txt(s, "Page 8 of Attachment 2.1, Pricing and Volumes. The red box is drawn from the position the ledger stores.", { x: L, y: 4.98, w: CW, h: 0.35, fontSize: 12, color: C.accent5 });
  card(s, L, 5.6, CW, 1.05, "Result", true);
  txt(s, "“Advanced Systems Engineer, $83.00 per hour” becomes Systems Engineer, senior, stored with page 8 and its box. Nothing in the ledger is an estimate; a vendor who challenges a rate is shown the page.", { x: L + 0.4, y: 5.6, w: CW - 0.8, h: 1.05, fontSize: 17, color: C.background1, valign: "middle" });
}

// 9. What it refuses to guess
{
  const s = content("What it refuses to guess", "When the system is not sure, it asks. Precision comes first.",
    "Sources: docs/story/follow-one-rate.html; the ledger (row 19, review queue item 2); architecture decision 5 (precision first). The image is the same page, fourteen rows down, boxed in amber.");
  const ih = CW / 15.38;
  s.addImage({ path: path.join(IMG, "page8_ops.png"), x: L, y: 2.0, w: CW, h: ih, altText: "The Operations row on page 8, boxed in amber", objectName: "Operations row" });
  const rows = [
    "“Operations, $99.50 per hour” names no role. The model abstained, and the row waits for an analyst: stored, but not counted.",
    "No default seniority and no guessed location. Every analyst decision becomes a rule, so no question is asked twice.",
    "One false claim of overbilling can lose an engagement; a missed saving is caught at the next refresh.",
  ];
  rows.forEach((r, i) => {
    const y = 3.2 + i * 1.15;
    num(s, L, y, i + 1, 0.5);
    txt(s, r, { x: L + 0.75, y: y - 0.02, w: CW - 0.75, h: 0.95, fontSize: 17, valign: "top" });
  });
}

// 10. What the client gets
{
  const s = content("What the client gets", "A book of record, benchmarks at the right cut, and savings that hold up in a negotiation.",
    "Sources: Business Plan v1.5; Pitch Deck v1.1 (dashboards, tranches); decision log (stacking, Sept 20; observed and projected, Oct 6); rate-conditions inventory (Oct 13). FOR KYLE: the dashboards are designed, not built; any mock-up must be labelled illustrative.");
  const items = [
    ["The ledger", "Every contracted rate, every contract year and every clause that changes a rate, each traced to its page."],
    ["Benchmarks", "By role, seniority, location and technology, shown as ranges and published only above a confidentiality floor."],
    ["Executive views", "The Role Composition Heatmap and the Total Potential Dashboard, with observed and projected savings kept separate."],
  ];
  const cw = (CW - 2 * 0.3) / 3;
  items.forEach((it, i) => {
    const x = L + i * (cw + 0.3);
    card(s, x, 2.0, cw, 2.35, it[0]);
    txt(s, it[0], { x: x + 0.3, y: 2.15, w: cw - 0.6, h: 0.45, fontSize: 20, bold: true, color: C.text2 });
    txt(s, it[1], { x: x + 0.3, y: 2.65, w: cw - 0.6, h: 1.6, fontSize: 15 });
  });
  txt(s, "Savings stack in three tranches, never double counted", { x: L, y: 4.55, w: CW, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
  const tr = [["Contractual", "down to the contracted rate", 1.7], ["Operational", "down to the vendor’s own best rate for the role", 1.3], ["Market alignment", "down to the market mid-point", 0.9]];
  const sw = (CW - 2 * 0.15) / 3, base = 6.85;
  tr.forEach((t, i) => {
    const x = L + i * (sw + 0.15);
    s.addShape(S.RECTANGLE, { x, y: base - t[2], w: sw, h: t[2], fill: { color: i === 0 ? C.text2 : i === 1 ? C.accent2 : C.accent3 }, line: { color: C.background1 }, objectName: `Tranche ${i + 1}` });
    txt(s, [{ text: t[0], options: { bold: true, breakLine: true } }, { text: t[1] }], { x: x + 0.2, y: base - t[2] + 0.12, w: sw - 0.4, h: t[2] - 0.2, fontSize: 14, color: C.background1 });
  });
}

// 11. Your data stays home
{
  const s = content("Your data stays home", "TWM is installed inside each client’s own Azure environment. Contracts, rates and vendor relationships never leave it.",
    "Sources: architecture decisions 1, 4 and 7; decision log (data boundary, Oct 6; disclosure gate, Oct 13). Replaces the Pitch Deck's 'Zero-Data-Exit ... exports only anonymized neural weights', which is superseded.");
  card(s, L, 2.0, 7.6, 4.75, "Client environment");
  txt(s, "Your Azure environment: everything stays here", { x: L + 0.35, y: 2.15, w: 7.0, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
  const inner = ["Contracts and documents", "Every individual rate", "Vendor relationships", "Analysts’ reasoning"];
  inner.forEach((t, i) => {
    const x = L + 0.35 + (i % 2) * 3.55, y = 2.85 + Math.floor(i / 2) * 1.55;
    s.addShape(S.ROUNDED_RECTANGLE, { x, y, w: 3.35, h: 1.3, rectRadius: 0.08, fill: { color: C.background1 }, line: { color: C.accent3, width: 1 }, objectName: `Kept ${i + 1}` });
    txt(s, t, { x: x + 0.2, y, w: 2.95, h: 1.3, fontSize: 16, bold: true, color: C.text2, valign: "middle" });
  });
  txt(s, "Every contract set is checked for disclosure restrictions before anything is benchmarked.", { x: L + 0.35, y: 6.0, w: 7.0, h: 0.6, fontSize: 13, color: C.accent5 });
  arrow(s, 8.45, 4.15, 0.6, 0.5);
  card(s, 9.25, 2.6, R - 9.25, 3.55, "Shared tier", true);
  txt(s, "Only this leaves", { x: 9.55, y: 2.8, w: R - 9.85, h: 0.45, fontSize: 18, bold: true, color: C.accent4 });
  bullets(s, ["The shared vocabulary", "Anonymized benchmark summaries, each from at least 3 observations and 2 clients", "Vendors only as a class"], { x: 9.55, y: 3.35, w: R - 9.85, h: 2.7, fontSize: 15, color: C.background1 });
}

// 12. What we own, what we rent
{
  const s = content("What we own, what we rent", "We rent the best AI models and own what makes them reliable.",
    "Sources: architecture decisions 2, 3 and 6; Pitch Deck v1.1 ('The Moat'). Replaces 'neural fine-tuning', 'train our foundational LLM models' and the GPT-4o references (decision 8: taught, not trained).");
  card(s, L, 2.0, 4.5, 3.55, "Rent");
  txt(s, "Rent", { x: L + 0.35, y: 2.2, w: 3.8, h: 0.5, fontSize: 24, bold: true, color: C.text2 });
  bullets(s, ["Frontier models through Microsoft Foundry", "Claude primary, GPT benchmarked", "No lock-in to one AI vendor"], { x: L + 0.35, y: 2.85, w: 3.8, h: 2.5, fontSize: 16 });
  const ox = L + 4.8, ow = R - ox;
  card(s, ox, 2.0, ow, 3.55, "Own", true);
  txt(s, "Own", { x: ox + 0.35, y: 2.2, w: ow - 0.7, h: 0.5, fontSize: 24, bold: true, color: C.accent4 });
  bullets(s, ["The role framework and the mapping table", "The page checks that prove every number", "The inventory of rate-changing fine print", "The evaluation sets", "The consortium benchmark"], { x: ox + 0.35, y: 2.85, w: ow - 0.7, h: 2.6, fontSize: 16, color: C.background1 });
  txt(s, [{ text: "The moat: ", options: { bold: true, color: C.accent1 } }, { text: "a benchmark built from data no one else can see, improving with every client. The system learns from decisions, not from retraining a model." }],
    { x: L, y: 5.85, w: CW, h: 0.8, fontSize: 18, color: C.text2 });
}

// 13. Built so far: the document library
{
  const s = content("Built so far (1 of 3): the document library", "Before any client data, we assembled 438 real public documents to build and test against.",
    "Sources: docs/corpus-sources-and-demo-set.md; action items B30 and B35 (counts measured Nov 22, 2026).");
  txt(s, "438", { x: L, y: 1.95, w: 3.6, h: 1.4, fontSize: 88, bold: true, fontFace: "Cambria", color: C.text2, valign: "bottom" });
  txt(s, "real public documents, gathered before any client data", { x: L, y: 3.4, w: 3.4, h: 0.8, fontSize: 16 });
  txt(s, "About 226 vendor-client pairs, 51 with two or more documents: real contract sets to follow end to end.", { x: L, y: 4.4, w: 3.4, h: 1.2, fontSize: 14, color: C.accent5 });
  const tiles = [
    ["About 240", "contracts filed with the US securities regulator"],
    ["5 and 13", "Texas and Michigan contract sets with rates visible, including a $109M, 13-year Deloitte contract"],
    ["48", "signed UK government contracts"],
    ["13", "major vendors’ UK rate cards, about 2,600 priced rows"],
    ["Canada", "federal TBIPS packages, 12 of them in French or bilingual"],
    ["1", "public invoice with its timesheets: the rarest find"],
  ];
  const gx = 4.45, gw = R - gx, tw = (gw - 0.25) / 2, th = 1.45;
  tiles.forEach((t, i) => {
    const x = gx + (i % 2) * (tw + 0.25), y = 2.0 + Math.floor(i / 2) * (th + 0.2);
    card(s, x, y, tw, th, `Source ${i + 1}`);
    txt(s, t[0], { x: x + 0.3, y: y + 0.15, w: tw - 0.6, h: 0.5, fontSize: 26, bold: true, fontFace: "Cambria", color: C.accent1 });
    txt(s, t[1], { x: x + 0.3, y: y + 0.68, w: tw - 0.6, h: 0.7, fontSize: 14 });
  });
}

// 14. Built so far: teaching the system
{
  const s = content("Built so far (2 of 3): teaching the system", "We built our own role framework and taught the system to place any vendor title in it, or to ask.",
    "Sources: taxonomy/REPORT.md (Oct 13, 2026); taxonomy/HELDOUT.md; decision log (Oct 6, 2026: first analyst review, 65 titles, 72 codified). 'Taught' is the accurate version of 'trained' (decision 8).");
  const stats = [["129", "roles"], ["18", "families"], ["4", "seniority bands"], ["547", "vendor titles mapped"]];
  stats.forEach((st, i) => {
    const x = L + (i % 2) * 2.85, y = 2.0 + Math.floor(i / 2) * 1.6;
    stat(s, x, y, 2.6, st[0], st[1], { size: 44, bigH: 0.85, labelH: 0.45 });
  });
  txt(s, "Built from open public sources: US O*NET, the UK government’s job ladders and Canada’s TBIPS categories. Location and technology are recorded beside the role.", { x: L, y: 5.35, w: 5.6, h: 1.3, fontSize: 14, color: C.accent5 });
  s.addChart(pres.charts.BAR, [{ name: "Placed", labels: ["By the rules alone", "After one review pass"], values: [40.7, 95.6] }], Object.assign({
    x: 6.8, y: 2.0, w: R - 6.8, h: 3.75, barDir: "col", chartColors: [HEX.dk2],
    showTitle: true, title: "113 titles it had never seen: share placed", titleFontSize: 14, titleColor: HEX.dk2,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0"%"', dataLabelFontSize: 16, dataLabelColor: HEX.dk2,
    valAxisMaxVal: 100, valAxisMinVal: 0, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    catAxisLabelColor: HEX.accent5, catAxisLabelFontSize: 14, showLegend: false, barGapWidthPct: 80,
  }, chartText));
  txt(s, "It learns from decisions, not from retraining a model.", { x: 6.8, y: 5.95, w: R - 6.8, h: 0.6, fontSize: 18, bold: true, color: C.text2 });
}

// 15. Built so far: a working prototype
{
  const s = content("Built so far (3 of 3): a working prototype", "The whole pipeline runs end to end on real contracts today, before any cloud spend.",
    "Sources: work/m2-thin-thread/review.md; work/contract-terms/review.md; action items B24, B25 and C12; test suite (Nov 22, 2026). FOR KYLE: a workbench screenshot would strengthen this slide; it needs a fresh capture.");
  const sets = [["Texas, Accenture", "Seven-file government contract set"], ["UK, Accenture", "G-Cloud rate page, read from the web page itself"], ["Michigan, Deloitte", "A 13-year contract with every change notice"]];
  const cw = (CW - 2 * 0.3) / 3;
  sets.forEach((st, i) => {
    const x = L + i * (cw + 0.3);
    card(s, x, 2.0, cw, 1.3, `Set ${i + 1}`, true);
    txt(s, st[0], { x: x + 0.3, y: 2.12, w: cw - 0.6, h: 0.5, fontSize: 20, bold: true, color: C.background1 });
    txt(s, st[1], { x: x + 0.3, y: 2.62, w: cw - 0.6, h: 0.6, fontSize: 14, color: C.accent4 });
  });
  const st4 = [["1,648", "verified rates from one Texas pricing table, across eight contract years"], ["1,034", "contract terms read, each quote proven on its page"], ["~$6.50", "of model spend for the full Texas and Michigan runs"], ["166", "automated tests"]];
  const sw = (CW - 3 * 0.3) / 4;
  st4.forEach((st, i) => stat(s, L + i * (sw + 0.3), 3.55, sw, st[0], st[1], { size: 40, bigH: 0.85, labelH: 1.0 }));
  txt(s, "An analyst workbench: the review queue, any rate clicked through to its page, every answer recorded with who and why.", { x: L, y: 5.9, w: CW, h: 0.7, fontSize: 17, bold: true, color: C.text2 });
}

// 16. What comes next
{
  const s = content("What comes next, and what we do not claim yet", "The core works. These are the next steps, and the numbers we will not claim until they are measured.",
    "Sources: action items B17, B26, B30 and C4; docs/architecture-components.md (build sequence). Dates are on the investor timeline slide.");
  const lw = 7.2;
  card(s, L, 2.0, lw, 4.65, "Next");
  txt(s, "Next", { x: L + 0.35, y: 2.2, w: lw - 0.7, h: 0.5, fontSize: 22, bold: true, color: C.text2 });
  ["The whole library through the pipeline", "Accuracy measured against hand-checked answer sheets", "Benchmarking, findings and savings", "TWM’s Azure environment, then the first client installation"].forEach((t, i) => {
    const y = 2.9 + i * 0.9;
    num(s, L + 0.35, y, i + 1, 0.45);
    txt(s, t, { x: L + 1.0, y: y - 0.02, w: lw - 1.3, h: 0.7, fontSize: 16, valign: "middle" });
  });
  const nx = L + lw + 0.33, nw = R - nx;
  card(s, nx, 2.0, nw, 4.65, "Not claimed", true);
  txt(s, "Not claimed yet", { x: nx + 0.35, y: 2.2, w: nw - 0.7, h: 0.5, fontSize: 22, bold: true, color: C.accent4 });
  bullets(s, ["No accuracy figure until the answer sheets are hand-checked", "No savings figure until the findings are built"], { x: nx + 0.35, y: 2.9, w: nw - 0.7, h: 3.5, fontSize: 16, color: C.background1, paraSpaceAfter: 12 });
}

// 17. Roadmap
{
  const s = content("Roadmap", "From an audit to the whole technology workforce.",
    "Sources: Business Plan v1.5 (phases); Pitch Deck v1.1 section 5.");
  const ph = [["Phase 1", "The audit and the Master Benchmark Ledger", 2.4], ["Phase 2", "Workforce planning: the demand pipeline, scenarios for the mix, and forecasts linked to approvals", 3.2], ["Later", "All labour, financial management, onboarding and vendor compliance", 4.0]];
  const aw = 0.42, gap = 0.55, cw = (CW - 2 * gap) / 3, base = 6.3;
  ph.forEach((p, i) => {
    const x = L + i * (cw + gap);
    card(s, x, base - p[2], cw, p[2], p[0], i === 2);
    txt(s, p[0], { x: x + 0.35, y: base - p[2] + 0.25, w: cw - 0.7, h: 0.5, fontSize: 22, bold: true, color: i === 2 ? C.accent4 : C.text2 });
    txt(s, p[1], { x: x + 0.35, y: base - p[2] + 0.85, w: cw - 0.7, h: p[2] - 1.0, fontSize: 16, color: i === 2 ? C.background1 : C.text1 });
    if (i < 2) arrow(s, x + cw + (gap - aw) / 2, base - 0.9, aw, aw);
  });
  txt(s, "Consulting-led first, self-serve over time.", { x: L, y: 6.4, w: CW, h: 0.45, fontSize: 16, bold: true, color: C.text2 });
}

// 18. The team
{
  const s = content("The team", "Led by an executive who has managed this problem from the inside.",
    "Sources: Business Plan v1.5 (leadership); Business Plan deck v1.4 slide 9; Early Adopter Presentation. Decision 6: additional leadership to be announced.");
  s.addShape(S.OVAL, { x: L, y: 2.05, w: 1.2, h: 1.2, fill: { color: C.text2 }, line: { color: C.text2 }, objectName: "Initials" });
  txt(s, "KM", { x: L, y: 2.05, w: 1.2, h: 1.2, fontSize: 28, bold: true, fontFace: "Cambria", color: C.background1, align: "center", valign: "middle" });
  txt(s, "Kyle McNamara", { x: L + 1.45, y: 2.1, w: 5, h: 0.55, fontSize: 24, bold: true, color: C.text2 });
  txt(s, "Founder", { x: L + 1.45, y: 2.65, w: 5, h: 0.4, fontSize: 16, color: C.accent5 });
  const facts = [["TD Bank", "6,200+ staff, $1.8B+ annual budget"], ["National Australia Bank", "Chief Transformation Officer; $1B+ in cost reductions, much of it third-party labour"], ["Scotiabank", "$1.5B+ IT budget, 5,000+ staff globally"]];
  facts.forEach((f, i) => {
    const y = 3.55 + i * 1.05;
    txt(s, f[0], { x: L, y, w: 6.6, h: 0.4, fontSize: 17, bold: true, color: C.accent1 });
    txt(s, f[1], { x: L, y: y + 0.4, w: 6.6, h: 0.55, fontSize: 15 });
  });
  const rx = 7.75, rw = R - rx;
  card(s, rx, 2.05, rw, 1.9, "Consulting practice");
  txt(s, "Consulting practice", { x: rx + 0.35, y: 2.2, w: rw - 0.7, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
  txt(s, "Ex-McKinsey and ex-BCG consultants in engagement pods, experienced in cost transformation and third-party labour.", { x: rx + 0.35, y: 2.7, w: rw - 0.7, h: 1.1, fontSize: 15 });
  card(s, rx, 4.2, rw, 1.5, "Platform team");
  txt(s, "Platform team", { x: rx + 0.35, y: 4.35, w: rw - 0.7, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
  txt(s, "AI and data engineering, software engineering, security and product.", { x: rx + 0.35, y: 4.85, w: rw - 0.7, h: 0.75, fontSize: 15 });
  txt(s, "Additional leadership to be announced.", { x: rx, y: 5.95, w: rw, h: 0.45, fontSize: 16, italic: true, color: C.accent5 });
}

// ================================================================= ENDING A
section = "Ending A: Early Adopter CIO";
pres.addSection({ title: section });
divider("For an Early Adopter CIO", "Joining the consortium");

// A1. The consortium
{
  const s = content("The Early Adopter consortium", "Four to five leading organizations, transforming their technology workforce together.",
    "Sources: Consortium Approach v1.7 slides 2, 5 and 7; Early Adopter Presentation (benefits; influence and co-development).");
  const cx = 3.25, cy = 4.4, r = 1.85, d = 1.0;
  for (let i = 0; i < 5; i++) {
    const a = (-90 + i * 72) * Math.PI / 180;
    const x = cx + r * Math.cos(a) - d / 2, y = cy + r * Math.sin(a) - d / 2;
    s.addShape(S.OVAL, { x, y, w: d, h: d, fill: { color: C.background2 }, line: { color: C.accent3, width: 1.5 }, objectName: `Member ${i + 1}` });
    txt(s, "Member", { x, y, w: d, h: d, fontSize: 13, bold: true, color: C.text2, align: "center", valign: "middle" });
  }
  s.addShape(S.OVAL, { x: cx - 0.85, y: cy - 0.85, w: 1.7, h: 1.7, fill: { color: C.text2 }, line: { color: C.text2 }, objectName: "Shared benchmark" });
  txt(s, "Shared benchmark", { x: cx - 0.85, y: cy - 0.85, w: 1.7, h: 1.7, fontSize: 15, bold: true, color: C.background1, align: "center", valign: "middle" });
  const ben = [
    "Savings of 10 to 15%, and a prioritized list of value levers from your own contracts and workforce data",
    "Proprietary benchmarks of labour rates and workforce mix against peers, and consortium workshops on leading practice",
    "A seat at the table: members shape the product’s features and priorities",
    "Confidential by design: no member sees another’s data",
  ];
  ben.forEach((b, i) => {
    const y = 2.05 + i * 1.18;
    num(s, 6.55, y, i + 1);
    txt(s, b, { x: 7.2, y: y - 0.03, w: R - 7.2, h: 1.0, fontSize: 16 });
  });
}

// A2. How it runs
{
  const s = content("How it runs", "Value Validation in 4 to 6 months, then Execution, then Capability Development.",
    "Sources: Consortium Approach v1.7 slides 6 and 7.");
  const vw = 5.0, aw = 0.42, gap = 0.5, ow = (CW - vw - 2 * gap) / 2;
  card(s, L, 2.0, vw, 3.9, "Value Validation", true);
  txt(s, "Value Validation", { x: L + 0.35, y: 2.2, w: vw - 0.7, h: 0.5, fontSize: 22, bold: true, color: C.background1 });
  txt(s, "4 to 6 months", { x: L + 0.35, y: 2.7, w: vw - 0.7, h: 0.4, fontSize: 15, color: C.accent4 });
  bullets(s, ["An opportunity assessment that quantifies the full potential", "Benchmarking against peers", "Quick wins, such as renegotiating statements of work", "A target state for the workforce and a roadmap"], { x: L + 0.35, y: 3.25, w: vw - 0.7, h: 2.5, fontSize: 15, color: C.background1 });
  const later = [["Execution", "Deeper analysis, recommendations on contracts and mix, and progress tracked on dashboards."], ["Capability Development", "Tools in place, processes standardized, internal capability built, benchmarks refreshed."]];
  later.forEach((p, i) => {
    const x = L + vw + gap + i * (ow + gap);
    arrow(s, x - gap + (gap - aw) / 2, 3.75, aw, aw);
    card(s, x, 2.0, ow, 3.9, p[0]);
    txt(s, p[0], { x: x + 0.35, y: 2.2, w: ow - 0.7, h: 0.9, fontSize: 22, bold: true, color: C.text2 });
    txt(s, p[1], { x: x + 0.35, y: 3.2, w: ow - 0.7, h: 2.5, fontSize: 15 });
  });
  txt(s, "Throughout: consortium workshops on leading practice and benchmarks.", { x: L, y: 6.15, w: CW, h: 0.5, fontSize: 17, bold: true, color: C.text2 });
}

// A3. What we ask, what we bring
{
  const s = content("What we ask, what we bring", "A committed sponsor and access to the documents; in return, a dedicated team and the platform.",
    "Sources: Consortium Approach v1.7 slide 8; architecture decisions (data boundary).");
  const cw = (CW - 0.33) / 2;
  card(s, L, 2.0, cw, 3.7, "Ask");
  txt(s, "What we ask of each member", { x: L + 0.4, y: 2.2, w: cw - 0.8, h: 0.5, fontSize: 21, bold: true, color: C.text2 });
  bullets(s, ["A CIO sponsor and a dedicated leader", "Procurement, HR and finance at the table", "Access to statements of work, invoices and timecards"], { x: L + 0.4, y: 2.9, w: cw - 0.8, h: 2.6, fontSize: 17, paraSpaceAfter: 10 });
  const x2 = L + cw + 0.33;
  card(s, x2, 2.0, cw, 3.7, "Bring", true);
  txt(s, "What TWM brings", { x: x2 + 0.4, y: 2.2, w: cw - 0.8, h: 0.5, fontSize: 21, bold: true, color: C.accent4 });
  bullets(s, ["Hands-on leadership", "A pod for each member: an engagement manager, a workforce analytics lead and a data analyst", "The platform running inside your environment"], { x: x2 + 0.4, y: 2.9, w: cw - 0.8, h: 2.6, fontSize: 17, color: C.background1, paraSpaceAfter: 10 });
  txt(s, "Your data stays in your environment; only anonymized summaries feed the shared benchmark.", { x: L, y: 5.95, w: CW, h: 0.6, fontSize: 17, bold: true, color: C.text2 });
}

// A4. Commercials
{
  const s = content("Commercials, and why join now", "Founding members get the deepest discount, the earliest benchmarks and the most influence.",
    "Sources: Kyle's decision 1 (Nov 22, 2026): $1.5MM per Early Adopter, contingent on the engagement generating more than $10MM in value for that client. McKinsey comparison and cost of delay: Business Plan v1.5 and Pitch Deck v1.1.");
  card(s, L, 2.0, 5.4, 4.65, "Offer", true);
  txt(s, "$1.5MM", { x: L + 0.4, y: 2.2, w: 4.6, h: 1.2, fontSize: 66, bold: true, fontFace: "Cambria", color: C.background1, valign: "bottom" });
  txt(s, "per Early Adopter", { x: L + 0.4, y: 3.45, w: 4.6, h: 0.45, fontSize: 18, color: C.accent4 });
  txt(s, "Contingent on the engagement generating more than $10MM in value for that client.", { x: L + 0.4, y: 4.1, w: 4.6, h: 1.0, fontSize: 17, color: C.background1 });
  txt(s, "So the fee is never more than 15% of the value created.", { x: L + 0.4, y: 5.25, w: 4.6, h: 0.9, fontSize: 17, bold: true, color: C.accent1 });
  const rx = L + 5.8, rw = R - rx;
  txt(s, "About $1.5MM a month", { x: rx, y: 2.0, w: rw, h: 0.6, fontSize: 28, bold: true, fontFace: "Cambria", color: C.text2 });
  txt(s, "is what a McKinsey engagement team costs, for comparison.", { x: rx, y: 2.6, w: rw, h: 0.45, fontSize: 15 });
  txt(s, "Why join now", { x: rx, y: 3.35, w: rw, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
  ["Shape the product", "See the benchmarks first", "Start saving within months", "Every week of delay costs about $3MM on a $150MM opportunity"].forEach((t, i) => {
    const y = 3.9 + i * 0.68;
    num(s, rx, y, i + 1, 0.42);
    txt(s, t, { x: rx + 0.6, y: y - 0.04, w: rw - 0.6, h: 0.6, fontSize: 16, valign: "middle" });
  });
}

// ================================================================= ENDING B
section = "Ending B: investors";
pres.addSection({ title: section });
divider("For investors", "The business");

// B1. The market
{
  const s = content("The market", "A very large spend with no purpose-built solution.",
    "Sources: Pitch Deck v1.1 section 4 (citing Gartner and IDC; provider headcounts); Business Plan v1.5 (target market analysis). Kyle's decision 4: organizations with $100MM+ in third-party technology labour spend.");
  const tiers = [["$1.87 trillion", "IT services spend, 2026", 6.0], ["1,500+ organizations", "with $100MM+ in third-party technology labour spend", 4.9], ["400+", "in North American financial services and telecom", 3.8]];
  tiers.forEach((t, i) => {
    const w = t[2], x = L + (6.0 - w) / 2, y = 2.0 + i * 1.3;
    s.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h: 1.15, rectRadius: 0.08, fill: { color: i === 0 ? C.accent3 : i === 1 ? C.accent2 : C.text2 }, line: { color: C.background1 }, objectName: `Tier ${i + 1}` });
    txt(s, [{ text: t[0], options: { bold: true, breakLine: true, fontSize: 18 } }, { text: t[1], options: { fontSize: 13 } }], { x: x + 0.2, y, w: w - 0.4, h: 1.15, color: C.background1, align: "center", valign: "middle" });
  });
  txt(s, "Goal: 50+ clients", { x: L, y: 6.0, w: 6.0, h: 0.55, fontSize: 22, bold: true, fontFace: "Cambria", color: C.accent1, align: "center" });
  s.addChart(pres.charts.BAR, [{ name: "Employees (thousands)", labels: ["Accenture", "TCS", "Capgemini", "Cognizant", "Infosys", "IBM Consulting", "HCLTech"], values: [784, 582, 423, 352, 337, 270, 226] }], Object.assign({
    x: 7.1, y: 2.0, w: R - 7.1, h: 4.35, barDir: "bar", chartColors: [HEX.dk2], catAxisOrientation: "maxMin",
    showTitle: true, title: "Top seven IT services providers: employees (thousands)", titleFontSize: 14, titleColor: HEX.dk2,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '#,##0"k"', dataLabelFontSize: 12, dataLabelColor: HEX.dk2,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 13,
    showLegend: false, barGapWidthPct: 60,
  }, chartText));
  txt(s, "Together about 3 million people. Source: Pitch Deck v1.1, citing Gartner and IDC.", { x: 7.1, y: 6.4, w: R - 7.1, h: 0.4, fontSize: 11, color: C.accent5 });
}

// B2. Business model
{
  const s = content("Business model", "Revenue tied to the savings we create.",
    "Sources: Business Plan v1.5 (opportunity; recurring revenue; go-to-market); Pitch Deck v1.1 (business model).");
  const cw = (CW - 2 * 0.3) / 3;
  [["$2–3MM", "of revenue for every $20MM of savings"], ["$4MM", "average annual revenue per client"], ["$200MM", "recurring revenue at 50 clients"]].forEach((it, i) => {
    const x = L + i * (cw + 0.3);
    card(s, x, 2.0, cw, 2.3, `Model ${i + 1}`, i === 2);
    stat(s, x + 0.35, 2.15, cw - 0.7, it[0], it[1], { size: 48, bigH: 0.95, labelH: 0.9, dark: i === 2 });
  });
  [["Recurring", "because savings must be sustained: refreshes, benchmark access, then Phase 2 workflows built into how clients plan their workforce."], ["Software-led over time", "consulting-led first, then the platform carries more of the work as it matures."]].forEach((it, i) => {
    const y = 4.7 + i * 0.95;
    num(s, L, y, i + 1);
    txt(s, [{ text: it[0] + ": ", options: { bold: true, color: C.text2 } }, { text: it[1] }], { x: L + 0.65, y: y - 0.03, w: CW - 0.65, h: 0.85, fontSize: 17 });
  });
}

// B3. Go-to-market
{
  const s = content("Go-to-market", "Early Adopters first, then a sales-led expansion.",
    "Sources: Pitch Deck v1.1 (go-to-market); Business Plan v1.5 (medium and longer-term go-to-market).");
  const aw = 0.5, gap = 0.6, cw = (CW - gap) / 2;
  card(s, L, 2.0, cw, 3.3, "Stage 1", true);
  txt(s, "Months 1 to 12", { x: L + 0.4, y: 2.2, w: cw - 0.8, h: 0.4, fontSize: 15, color: C.accent4 });
  txt(s, "The Early Adopter consortium", { x: L + 0.4, y: 2.6, w: cw - 0.8, h: 0.55, fontSize: 22, bold: true, color: C.background1 });
  txt(s, "Four to five organizations, reached through the leadership team’s executive network.", { x: L + 0.4, y: 3.3, w: cw - 0.8, h: 1.8, fontSize: 17, color: C.background1 });
  arrow(s, L + cw + (gap - aw) / 2, 3.4, aw, aw);
  const x2 = L + cw + gap;
  card(s, x2, 2.0, cw, 3.3, "Stage 2");
  txt(s, "Years 2 to 3", { x: x2 + 0.4, y: 2.2, w: cw - 0.8, h: 0.4, fontSize: 15, color: C.accent2 });
  txt(s, "Sales-led expansion", { x: x2 + 0.4, y: 2.6, w: cw - 0.8, h: 0.55, fontSize: 22, bold: true, color: C.text2 });
  txt(s, "Enterprise sales with 4 to 8 week pilots across North American financial services and telecom.", { x: x2 + 0.4, y: 3.3, w: cw - 0.8, h: 1.8, fontSize: 17 });
  txt(s, [{ text: "Buyers: ", options: { bold: true, color: C.text2 } }, { text: "CIOs first, chief procurement officers second. Case studies from the Early Adopters open the next doors." }], { x: L, y: 5.65, w: CW, h: 0.8, fontSize: 17 });
}

// B4. Timeline
{
  const s = content("Timeline", "Starting now: Early Adopters in the first quarter of 2027, profitability in 2028.",
    "Kyle's decision 2 (Nov 22, 2026): the plan starts today, so every Business Plan milestone moves eight months later. FOR KYLE: the profitability date (Q2 2028) is Claude's proposal from the Business Plan's own model (decision 3); confirm it.");
  const ms = [
    ["Dec 2026", "$1MM SAFE; founding team and first two pods start"],
    ["Mar 2027", "Four Early Adopters begin Value Validation"],
    ["Sep 2027", "Second cohort; Series A in the second half of 2027"],
    ["Late 2027", "First platform version in Early Adopter environments"],
    ["Mar 2028", "Full-fee clients; profitable from Q2 2028"],
    ["2031", "50 clients and a $200MM run rate"],
  ];
  const ly = 4.35, x0 = L + 1.3, x1 = R - 1.3, step = (x1 - x0) / 5;
  s.addShape(S.LINE, { x: x0, y: ly, w: x1 - x0, h: 0, line: { color: HEX.accent3, width: 3 }, objectName: "Timeline line" });
  ms.forEach((m, i) => {
    const x = x0 + i * step, up = i % 2 === 0, lw = 2.6;
    s.addShape(S.OVAL, { x: x - 0.17, y: ly - 0.17, w: 0.34, h: 0.34, fill: { color: i === 4 ? C.accent1 : C.text2 }, line: { color: C.background1, width: 2 }, objectName: `Milestone ${i + 1}` });
    const ty = up ? 2.05 : 4.75;
    txt(s, m[0], { x: x - lw / 2, y: up ? ty + 0.95 : ty, w: lw, h: 0.45, fontSize: 18, bold: true, fontFace: "Cambria", color: C.text2, align: "center", valign: up ? "bottom" : "top" });
    txt(s, m[1], { x: x - lw / 2, y: up ? ty : ty + 0.5, w: lw, h: 0.9, fontSize: 14, align: "center", valign: up ? "bottom" : "top" });
  });
}

// B5. Financial model
{
  const s = content("Financial model", "Profitable in 2028, on a path to $200MM.",
    "Sources: Business Plan v1.5 (preliminary financial model; funding ask), moved eight months to today's start. Costs in the chart are the Business Plan's 'exiting 2030' figures, i.e. at the 50-client run rate. FOR KYLE: Q2 2028 is Claude's proposal (decision 3). The Pitch Deck's 'profitable in 2026' counted only consulting costs; with the platform team, year-one costs are about $9.9MM against about $10MM of Early Adopter revenue, and profit comes when clients pay the full $4MM a year.");
  stat(s, L, 1.95, 5.6, "Q2 2028", "profitable, at about five clients paying the full fee", { size: 44, bigH: 0.85, labelH: 0.5 });
  stat(s, L, 3.45, 5.6, "$200MM", "revenue run rate by 2031, with $100MM+ profit before tax and 50 clients", { size: 44, bigH: 0.85, labelH: 0.7 });
  stat(s, L, 5.1, 5.6, "$30MM", "of costs over the first two years in the base case; $10–12MM in the leaner case", { size: 44, bigH: 0.85, labelH: 0.7 });
  s.addChart(pres.charts.BAR, [{ name: "Annual cost ($MM)", labels: ["AI and software development", "Consulting practice", "Sales", "Other overhead"], values: [26.5, 24, 15, 10] }], Object.assign({
    x: 6.9, y: 2.0, w: R - 6.9, h: 4.5, barDir: "bar", chartColors: [HEX.accent2], catAxisOrientation: "maxMin", valAxisMaxVal: 33, valAxisMinVal: 0,
    showTitle: true, title: "Annual costs at the 50-client run rate ($MM)", titleFontSize: 14, titleColor: HEX.dk2,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '"$"0.0"MM"', dataLabelFontSize: 13, dataLabelColor: HEX.dk2,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 13,
    showLegend: false, barGapWidthPct: 60,
  }, chartText));
}

// B6. The ask
{
  const s = content("The ask", "$1MM through a SAFE to take a working prototype into the first consortium.",
    "Sources: Pitch Deck v1.1 (the ask; traction); Kyle's decision 5 (Nov 22, 2026). FOR KYLE: with the fee contingent on more than $10MM of value, Early Adopter cash arrives only once that value is shown, likely months into Value Validation. At the Business Plan's cost base $1MM is about five weeks of spending; the Pitch Deck sized it for the founding team and two pods for three to four months. Check that it bridges the wait.");
  card(s, L, 2.0, 4.8, 4.65, "Ask", true);
  txt(s, "$1MM", { x: L + 0.4, y: 2.25, w: 4.0, h: 1.3, fontSize: 80, bold: true, fontFace: "Cambria", color: C.background1, valign: "bottom" });
  txt(s, "through a SAFE", { x: L + 0.4, y: 3.6, w: 4.0, h: 0.5, fontSize: 22, color: C.accent4 });
  txt(s, "to take a working prototype into the first consortium", { x: L + 0.4, y: 4.4, w: 4.0, h: 1.2, fontSize: 18, color: C.background1 });
  const rx = L + 5.2, rw = R - rx;
  ["Funds the founding team and the first two engagement pods to launch Value Validation with four Early Adopters", "The prototype already exists, so the money goes into the first engagements, not into proving the idea", "A Series A in the second half of 2027 funds the broader platform"].forEach((t, i) => {
    const y = 2.1 + i * 1.45;
    num(s, rx, y, i + 1, 0.5);
    txt(s, t, { x: rx + 0.75, y: y - 0.03, w: rw - 0.75, h: 1.2, fontSize: 18 });
  });
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
