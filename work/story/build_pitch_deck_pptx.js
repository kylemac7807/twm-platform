// Builds docs/story/twm-pitch-deck.pptx in the house style of Kyle's own decks (Consortium Approach v1.7,
// Business Plan deck v1.4, Summary Technical Approach v1.2): Aptos, navy and blue, sentence titles, blue section
// headers with a rule, bold key phrases, navy banners, chevrons and blue line icons. Content reuses those decks'
// wording where it exists, with Kyle's decisions of Nov 22, 2026 and the architecture decisions applied.
// Usage: node build_pitch_deck_pptx.js <output.pptx> <pptx skill scripts/apply_theme.js> <image folder>
// Needs pptxgenjs, react, react-dom, react-icons and sharp on NODE_PATH.
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const RDS = require("react-dom/server");
const sharp = require("sharp");
const PI = require("react-icons/pi");
const { applyTheme } = require(process.argv[3]);
const OUT = process.argv[2] || "twm-pitch-deck.pptx";
const IMG = process.argv[4];

const H = { navy: "0E2841", blue: "0070C0", mid: "4A90D9", dblue: "1E3C8C", lblue: "A9C9EC", grey: "7F7F7F", lgrey: "F2F2F2",
  rule: "BFBFBF", cyan: "00B0F0", pale: "DAE8F5", teal: "1F5C99", hdr: "1F4E79", body: "D6DCE4", red: "C00000", text: "000000" };
const THEME = { name: "TWM", headFontFace: "Aptos Display", bodyFontFace: "Aptos",
  colors: { dk1: "000000", lt1: "FFFFFF", dk2: H.navy, lt2: "E8E8E8", accent1: H.blue, accent2: H.mid, accent3: H.dblue, accent4: H.lblue,
    accent5: H.grey, accent6: H.cyan, hlink: H.blue, folHlink: H.teal } };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in, the same 16:9 page as the Consortium and Technical Approach decks
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Technology Workforce Management (TWM)";
pres.author = "Kyle McNamara";
const S = pres.shapes;
const L = 0.45, R = 12.88, CW = R - L;

// ---------------------------------------------------------------- layouts
const frame = [
  { rect: { x: 0.08, y: 0.08, w: 13.173, h: 7.34, fill: { type: "none" }, line: { color: H.navy, width: 2.25 } } },
  { rect: { x: 0.16, y: 0.16, w: 13.013, h: 7.18, fill: { type: "none" }, line: { color: H.navy, width: 0.75 } } },
];
pres.defineSlideMaster({ title: "COVER", background: { color: "FFFFFF" }, objects: frame });
pres.defineSlideMaster({ title: "DIVIDER", background: { color: "FFFFFF" }, objects: frame });
pres.defineSlideMaster({
  title: "CONTENT", background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: L, y: 0.3, w: CW, h: 1.05, fontSize: 30, color: H.navy, margin: 0, align: "left", valign: "top" }, text: "" } }],
  slideNumber: { x: 12.4, y: 7.05, w: 0.5, h: 0.3, fontSize: 10, color: H.grey, align: "right" },
});

// ---------------------------------------------------------------- text helpers
// Markup inside strings: **bold**, __bold italic__, [[blue bold]]
function parse(str, base) {
  const out = []; const re = /(\*\*.+?\*\*|__.+?__|\[\[.+?\]\])/g; let last = 0, m;
  while ((m = re.exec(str))) {
    if (m.index > last) out.push({ text: str.slice(last, m.index), options: { ...base } });
    const t = m[0];
    if (t.startsWith("**")) out.push({ text: t.slice(2, -2), options: { ...base, bold: true } });
    else if (t.startsWith("__")) out.push({ text: t.slice(2, -2), options: { ...base, bold: true, italic: true } });
    else out.push({ text: t.slice(2, -2), options: { ...base, bold: true, color: H.blue } });
    last = re.lastIndex;
  }
  if (last < str.length) out.push({ text: str.slice(last), options: { ...base } });
  return out;
}
// items: string (bullet) or { t, nob (no bullet), lvl, after, size, color, align }
function paras(items, o) {
  const opt = o || {}; const runs = [];
  items.forEach((it, i) => {
    const p = typeof it === "string" ? { t: it } : it;
    const base = {}; if (p.size) base.fontSize = p.size; if (p.color) base.color = p.color;
    const r = parse(p.t, base);
    const f = r[0].options;
    if (!p.nob) f.bullet = { indent: p.lvl ? 12 : 13 };
    if (p.lvl) f.indentLevel = p.lvl;
    if (p.align) f.align = p.align;
    f.paraSpaceAfter = p.after !== undefined ? p.after : (opt.after !== undefined ? opt.after : 4);
    r[r.length - 1].options.breakLine = i < items.length - 1;
    runs.push(...r);
  });
  return runs;
}
function txt(s, content, o) {
  const body = Array.isArray(content) ? content : parse(content, {});
  s.addText(body, Object.assign({ margin: 0, isTextBox: true, valign: "top", fontSize: 14, color: H.text, fontFace: "Aptos" }, o));
}
function list(s, items, o, po) { txt(s, paras(items, po), o); }
function header(s, text, x, y, w, o) {
  const opt = o || {};
  const iw = opt.icon ? 0.45 : 0;
  txt(s, text, { x, y, w: w - iw, h: opt.h || 0.42, fontSize: opt.size || 16, bold: true, color: opt.color || H.blue, valign: "bottom" });
  s.addShape(S.LINE, { x, y: y + (opt.h || 0.42) + 0.04, w, h: 0, line: { color: opt.color || H.blue, width: 1 } });
  if (opt.icon) icon(s, opt.icon, x + w - 0.4, y + (opt.h || 0.42) - 0.38, 0.36, opt.iconColor);
}
function box(s, x, y, w, h, o) {
  const opt = o || {};
  s.addShape(opt.rounded ? S.ROUNDED_RECTANGLE : S.RECTANGLE, Object.assign({ x, y, w, h,
    fill: opt.fill ? { color: opt.fill } : { type: "none" }, line: opt.noLine ? { type: "none" } : { color: opt.line || H.navy, width: opt.lineW || 1 },
    objectName: opt.name || "Box" }, opt.rounded ? { rectRadius: opt.radius || 0.12 } : {}));
}
function banner(s, text, x, y, w, h, o) {
  const opt = o || {};
  box(s, x, y, w, h, { fill: opt.fill || H.navy, noLine: true, rounded: opt.rounded, radius: 0.06, name: "Banner" });
  txt(s, text, { x: x + 0.2, y, w: w - 0.4, h, fontSize: opt.size || 15, bold: opt.bold !== false, color: "FFFFFF", align: "center", valign: "middle" });
}
function chevrons(s, labels, y, h, colors, o) {
  const opt = o || {}; const n = labels.length; const w = CW / n + 0.08;
  labels.forEach((lb, i) => {
    const x = L + i * (CW / n);
    const style = colors[i];
    s.addShape(i === 0 ? S.PENTAGON : S.CHEVRON, { x, y, w: i === n - 1 ? CW / n : w, h,
      fill: style === "outline" ? { color: "FFFFFF" } : { color: style }, line: { color: H.navy, width: style === "outline" ? 1 : 0.5 }, objectName: `Chevron ${i + 1}` });
    txt(s, lb, { x: x + (i === 0 ? 0.15 : 0.42), y, w: CW / n - (i === 0 ? 0.35 : 0.6), h, fontSize: opt.size || 14, bold: true,
      color: style === "outline" ? H.navy : "FFFFFF", align: "center", valign: "middle" });
  });
}
const icons = {};
function icon(s, name, x, y, size, color) {
  const key = name + (color || H.blue);
  if (!icons[key]) throw new Error("icon not rendered: " + key);
  s.addImage({ data: icons[key], x, y, w: size, h: size, objectName: `Icon ${name}` });
}
async function renderIcons(list) {
  for (const [name, color] of list) {
    const key = name + color;
    if (icons[key]) continue;
    if (!PI[name]) throw new Error("no such icon " + name);
    const svg = RDS.renderToStaticMarkup(React.createElement(PI[name], { color: "#" + color, size: 256 }));
    const buf = await sharp(Buffer.from(svg)).png().toBuffer();
    icons[key] = "image/png;base64," + buf.toString("base64");
  }
}
function content(title, notes) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function divider(title, subtitle) {
  const s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: section });
  txt(s, title, { x: 1, y: 2.6, w: 11.33, h: 1.3, fontSize: 54, bold: true, fontFace: "Aptos Display", color: H.navy, align: "center", valign: "middle" });
  txt(s, subtitle, { x: 1, y: 3.95, w: 11.33, h: 0.7, fontSize: 26, fontFace: "Aptos Display", color: "2E74B5", align: "center", valign: "top" });
}
let section = "";

(async () => {
  await renderIcons([
    ["PiCurrencyDollar", H.blue], ["PiFileText", H.blue], ["PiUsersThree", H.blue], ["PiEye", H.blue], ["PiBank", H.blue], ["PiScissors", H.blue],
    ["PiTarget", H.blue], ["PiArrowsOutSimple", H.blue], ["PiGauge", H.blue], ["PiMedal", H.blue], ["PiBrain", H.blue], ["PiCoins", H.blue],
    ["PiFileText", "FFFFFF"], ["PiFileText", H.navy], ["PiCpu", "FFFFFF"], ["PiTreeStructure", "FFFFFF"], ["PiClipboardText", "FFFFFF"], ["PiArrowsClockwise", "FFFFFF"],
    ["PiWarningCircle", H.blue], ["PiListChecks", H.blue], ["PiArrowsClockwise", H.blue], ["PiLockKey", H.blue], ["PiPuzzlePiece", H.blue],
    ["PiBooks", H.blue], ["PiTreeStructure", H.blue], ["PiDesktop", H.blue], ["PiRocketLaunch", H.blue], ["PiHandshake", H.blue], ["PiChartBar", H.blue],
    ["PiStrategy", H.blue], ["PiLightbulb", H.blue],
  ]);

  // ======================================================= CORE
  section = "Core";
  pres.addSection({ title: section });

  // 1. Cover
  {
    const s = pres.addSlide({ masterName: "COVER", sectionTitle: section });
    txt(s, "Technology Workforce Management (TWM)", { x: 1.2, y: 1.15, w: 10.93, h: 2.0, fontSize: 54, bold: true, fontFace: "Aptos Display", color: H.navy, align: "center", valign: "bottom" });
    txt(s, "Overview document", { x: 1.2, y: 3.2, w: 10.93, h: 0.8, fontSize: 32, fontFace: "Aptos Display", color: "2E74B5", align: "center" });
    txt(s, [{ text: "Prepared by:", options: { bold: true, color: "2E74B5", breakLine: true } }, { text: "Kyle McNamara", options: { bold: true, breakLine: true } },
      { text: "KyleFMcNamara@gmail.com", options: { bold: true, breakLine: true } }, { text: "647-965-1920", options: { bold: true } }],
      { x: 0.6, y: 5.0, w: 4.5, h: 1.2, fontSize: 13 });
    txt(s, [{ text: "Date: ", options: { bold: true, color: "2E74B5" } }, { text: "November 22nd, 2026" }], { x: 8.4, y: 5.85, w: 4.3, h: 0.4, fontSize: 15, align: "right" });
    txt(s, [{ text: "Confidentiality Notice:", options: { breakLine: true } }, { text: "This document contains confidential and proprietary information intended solely for the recipient. Do not distribute or reproduce without written permission from Technology Workforce Management." }],
      { x: 2.0, y: 6.55, w: 9.33, h: 0.65, fontSize: 10, align: "center" });
    s.addNotes("Cover in the style of the Consortium Approach v1.7 and Summary Technical Approach v1.2 covers. Contact details as on the Consortium Approach v1.7 cover.");
  }

  // 2. Executive Summary
  {
    const s = content("Executive Summary", "Sources: Consortium Approach v1.7 slide 2 (structure and wording); Business Plan v1.5; work done measured Nov 22, 2026. The information-gap line comes from the approved Akerlow description.");
    header(s, "Why …", L, 1.4, 6.1);
    list(s, [
      { t: "Technology Workforce Management (TWM) helps **large organizations cut their third-party technology labor spend and restructure their workforce for the future**", nob: true, after: 8 },
      "**Targeting inefficiencies, lack of visibility, and cost leakage** plaguing current workforce management processes—most of which rely on manual spreadsheets and disjointed tools",
      "**The vendor sees every rate; the client sees one SOW at a time** – TWM closes that information gap with one traceable record of every rate",
      "A consortium of an **exclusive network of 4-5 leading organizations** committed to transforming their technology workforce",
      "**AI platform already working on real contracts** – every rate traced to the page it came from, inside the client’s own Azure environment",
    ], { x: L + 0.05, y: 1.95, w: 6.0, h: 4.95, fontSize: 15 }, { after: 8 });
    header(s, "Impact and benefits", 6.95, 1.4, 5.93);
    list(s, [
      "__10-15% cost savings__ in a rapid, measurable and scalable way",
      "__Clear list of prioritized Value Levers:__ analysis of workforce and contract data to pinpoint opportunities",
      "__Access to Proprietary Benchmarks and Analytics:__ insights into industry labor rates and workforce mix",
      "__An auditable Master Benchmark Ledger:__ every contracted rate traceable to its source page – evidence that holds up with vendors",
      "__Peer Learning and Workshops:__ leading best practices and access to collective intelligence",
      "__Implementation Roadmap:__ action plan sequencing quick wins, contract improvements and AI-enabled monitoring over the long term",
    ], { x: 7.0, y: 1.95, w: 5.85, h: 4.95, fontSize: 15 }, { after: 8 });
  }

  // 3. Context
  {
    const s = content("Context: 3rd party labor cost can account for up to 40% of Tech cost, and is a challenge for most organizations",
      "Source: Consortium Approach v1.7 slide 3, wording kept; Pitch Deck v1.1 for the same figures.");
    header(s, "25-40% of Total Tech costs is 3rd party labor spread across numerous vendors…", 0.55, 1.55, 4.15, { h: 0.7, size: 15 });
    list(s, [
      { t: "**50-75%** of Tech cost is labor (employees, contractors, SOW resources, etc.)", nob: true, after: 16 },
      { t: "**50:50** ratio of employees vs. 3rd party", nob: true, after: 16 },
      { t: "**1,000s** of 3rd party resources through 100s of contracts across 20+ vendors", nob: true, after: 16 },
      { t: "Third-party technology labor spend **exceeds $1.5B** at each of the large Canadian Banks", nob: true },
    ], { x: 0.6, y: 2.4, w: 4.0, h: 4.3, fontSize: 15 });
    s.addShape(S.CHEVRON, { x: 4.85, y: 2.4, w: 0.38, h: 4.3, fill: { color: H.navy }, line: { color: H.navy }, objectName: "Arrow" });
    header(s, "… however, most organizations struggle with effective Tech workforce mgmt.", 5.45, 1.55, 7.4, { h: 0.7, size: 15 });
    list(s, [
      { t: "**Fragmented process and accountabilities** across different parts of the organization", nob: true },
      { t: "$B+ workforces largely **managed on spreadsheets,** not leveraging organization’s scale" },
      { t: "Decisions **decentralized**, reporting is **inconsistent**" },
      { t: "**Hand-offs** across procurement, operations, finance, and different levels of management", after: 8 },
      { t: "**Limited Visibility and Alignment** with future workforce needs", nob: true },
      { t: "**Data buried** in spreadsheets, invoices, contracts, and disparate platforms" },
      { t: "**Difficulty benchmarking**, and optimizing labor mix", after: 8 },
      { t: "**Inconsistent Tooling** - Local teams build their own workforce views – typically in MS-Excel", nob: true },
    ], { x: 5.55, y: 2.4, w: 7.3, h: 4.4, fontSize: 15 });
  }

  // 4. Ineffective workforce management
  {
    const s = content("Ineffective workforce management leads to higher labor cost, disparate vendor terms, & suboptimal resource mix",
      "Source: Consortium Approach v1.7 slide 4, wording kept.");
    const cols = [
      ["Skills and cost", "PiCurrencyDollar", [
        "**Inability to link** the timecard billed, to the invoice charged, to the contract/MSA/SOW",
        "Rate cards in decentralized SOWs **do not leverage scale** and benchmarks",
        "View of **resources and costs are rarely consolidated** in a clear, timely fashion",
        "**Non-standard Skill Matrices become dated** across SOWs - vendors exploit blind spots for extra revenue / margin",
        "**Workforce Churn** - deficient forecasts result in the ramp-up/down of teams – and a poor experience for resources"]],
      ["Vendor terms", "PiFileText", [
        "**Patchwork of SOWs:** usually tied to a specific business case; procurement involved too late",
        "Excessive **“off-rate card” or “niche” skills are premium billed**",
        "**Lack of visibility to benchmark rates** allows material leakage",
        "**Reconciliation between complex invoices** and custom SOWs seldom completed",
        "Sampling and spot-checks reveal **billing inconsistencies**"]],
      ["Resource mix", "PiUsersThree", [
        "**Labor mix is inconsistent** with strategic objectives: **Resource type** (employees vs 3rd party), **Location** (onshore, offshore, etc.), **Seniority** mix (senior, intermediate, junior)",
        "**Limited visibility** into pipeline of open and upcoming roles",
        "**Forecasts detached from approvals** (prevents “what-if” scenario planning)",
        "**IT, HR and Finance not aligned** on forecast and often current state"]],
    ];
    cols.forEach((c, i) => {
      const x = 0.55 + i * 4.18;
      header(s, c[0], x, 1.5, 3.9, { icon: c[1], size: 18 });
      list(s, c[2], { x: x + 0.05, y: 2.15, w: 3.85, h: 4.7, fontSize: 14 }, { after: 6 });
    });
  }

  // 5. Root cause: the information gap
  {
    const s = content("The root cause is an information gap: the vendor sees every rate, while the client sees one SOW at a time",
      "Source: the approved Akerlow description (docs/story/naming.md, Nov 22, 2026), in the deck's own voice; the name reference is left out because the deck says TWM.");
    banner(s, "“When one side of a market knows far more than the other, that side sets the price” – George Akerlof, Nobel laureate in economics", 0.9, 1.5, 11.53, 0.62, { rounded: true, size: 15 });
    const colsV = [
      [0.55, "What the vendor sees", "PiEye", ["**What every client pays** for the same role", "How its rates **compare across all of its clients**", "**What an off-rate card role really involves**", "**The full picture**"]],
      [6.98, "What the client sees", "PiFileText", ["**One statement of work at a time**", "Roles, seniority, rate units and price increases **defined differently in every contract**", "Rates buried in **complex terms and conditions**", "**Fragments**"]],
    ];
    colsV.forEach((c) => {
      box(s, c[0], 2.4, 5.8, 2.85, { rounded: true, lineW: 1.5 });
      header(s, c[1], c[0] + 0.3, 2.5, 5.2, { icon: c[2], size: 18 });
      list(s, c[3], { x: c[0] + 0.35, y: 3.15, w: 5.15, h: 2.0, fontSize: 15 }, { after: 6 });
    });
    box(s, 0.9, 5.5, 11.53, 1.3, { rounded: true, lineW: 1.5 });
    txt(s, [
      ...parse("The client cannot tell a fair rate from an inflated one – so **fair pricing cannot win**. Nobody has to behave badly; the gap does it on its own.", {}),
      { text: "", options: { breakLine: true } },
      ...parse("**TWM closes the gap:** one traceable record of every rate, benchmarked against peers.", {}),
    ], { x: 1.2, y: 5.5, w: 10.93, h: 1.3, fontSize: 16, align: "center", valign: "middle" });
  }

  // 6. Opportunity
  {
    const s = content("Opportunity: 10-15% cost savings are realistic and conservative",
      "Sources: Business Plan v1.5 and deck v1.4 slide 5 (layout and wording); Pitch Deck v1.1 (the Canadian bank benchmark; cost of delay $3MM a week on $150MM); Business Plan v1.5 (initial 5-10% from price, additional 5-15% from mix).");
    const rows = [
      ["PiBank", "**Tech labor is 50–75% of total tech costs** – typically 40%+ spent on external vendors", "Third-party technology labor spend exceeds $1.5B at each of the large Canadian Banks"],
      ["PiScissors", "**Cost savings of 10-15%** – achievable, conservative, and material", "**$150MM+** a year for one large Canadian bank; $100-150MM for every $1B of third-party spend"],
      ["PiTarget", "**Price** – targeting leakage: rates negotiated SOW by SOW, off-rate card premiums, inconsistent billing", "Initial 5-10% from analyzing each SOW and the related invoices"],
      ["PiArrowsOutSimple", "**Quantity/Mix** – resource type, location, seniority and skills", "Additional 5-15% from optimizing the labor mix"],
      ["PiGauge", "**Cost of delay** – for $150MM in potential savings, about $3MM per week", "Time to value is months, not years"],
    ];
    rows.forEach((r, i) => {
      const y = 1.5 + i * 0.95;
      icon(s, r[0], 0.7, y + 0.12, 0.6);
      list(s, [{ t: r[1], size: 16 }, { t: r[2], lvl: 1, size: 14 }], { x: 1.75, y: y + 0.08, w: 10.9, h: 0.85, fontSize: 16 }, { after: 2 });
      if (i < rows.length - 1) s.addShape(S.LINE, { x: 1.6, y: y + 0.92, w: 11.1, h: 0, line: { color: H.rule, width: 1 } });
    });
    banner(s, "Targeting Cost Savings of 10-15%", 4.17, 6.35, 5.0, 0.55, { rounded: true, size: 17 });
  }

  // 7. Competitive Analysis
  {
    const s = content("Competitive Analysis",
      "Sources: Business Plan deck v1.4 slide 4 and Business Plan v1.5 Appendix C (wording condensed; logos replaced by names). The general-purpose AI point answers the Pitch Deck's note on why OpenAI cannot solve this.");
    txt(s, "Current solutions related to technology workforce management are highly fragmented, with each tool only addressing a narrow slice. Patchwork approach results in inefficiencies, data inconsistencies, and gaps in oversight.",
      { x: L, y: 1.15, w: CW, h: 0.6, fontSize: 14, align: "center" });
    const cols = [
      ["HRIS Solutions", "Workday, Oracle, Rippling", ["Focus on the employee lifecycle (recruitment, onboarding, payroll, benefits)", "Some functionality for third-party mgmt (i.e. compliance tracking)", "Gaps – rates and benchmarking of rates typically not captured", "Limited role in price or the quantity/mix of third-party labor"]],
      ["Procurement Solutions", "SAP Ariba, SAP Fieldglass, Workday VNDLY", ["SAP Ariba – likely the book of record for contracts/MSAs/SOWs", "Not exclusively focused on 3rd party labor", "Does not design skill matrices, benchmark, or check compliance with rates", "Fieldglass & VNDLY focus on contingent labor – not typically used for larger vendors"]],
      ["Financial Management", "Clarity, Apptio", ["Budget tracking, cost allocation, and IT financial mgmt", "Complex configuration and limited integration with HR/Procurement systems", "Limited categorization of skills, location, labor type – benchmarking"]],
      ["Benchmarking Datasets", "ISG, Gartner", ["SOWs and MSAs typically structured differently than ISG/Gartner datasets", "Standardizing skills across a volume of SOWs makes them often academic", "Do not attack leakage – the inability to link the invoice charged to the SOW"]],
      ["Newer AI Solutions", "Contract analysis tools; general-purpose AI", ["Contract analysis, third-party risk, legal review and drafting", "General-purpose AI does not hold your contracts, a role framework or peer benchmarks – and cannot be allowed to guess", "**To date, an AI solution for pricing or benchmarking third-party labor has not been identified**"]],
    ];
    const gap = 0.2, w = (CW - 4 * gap) / 5;
    cols.forEach((c, i) => {
      const x = L + i * (w + gap);
      txt(s, c[0], { x, y: 1.85, w, h: 0.45, fontSize: 16, bold: true, color: H.blue, align: "center", valign: "bottom" });
      txt(s, c[1], { x, y: 2.32, w, h: 0.5, fontSize: 12, bold: true, color: H.grey, align: "center" });
      list(s, c[2], { x: x + 0.02, y: 2.85, w: w - 0.04, h: 3.3, fontSize: 12.5 }, { after: 5 });
      if (i < 4) s.addShape(S.LINE, { x: x + w + gap / 2, y: 1.95, w: 0, h: 4.1, line: { color: H.rule, width: 0.75 } });
    });
    box(s, 1.6, 6.25, 10.13, 0.62, { rounded: true, lineW: 1.5 });
    txt(s, "There are tools and solutions adjacent to this problem statement. However, there is **no approach that tackles it directly.**", { x: 1.8, y: 6.25, w: 9.73, h: 0.62, fontSize: 15, bold: true, align: "center", valign: "middle" });
  }

  // 8. Approach and Opportunity
  {
    const s = content("Approach and Opportunity", "Source: Consortium Approach v1.7 slide 5, wording kept; the AI line updated to what exists today.");
    box(s, 0.55, 1.45, 6.3, 2.35, { rounded: true, lineW: 1.5 });
    header(s, "Industry & Consulting Expertise", 0.85, 1.5, 5.7, { icon: "PiMedal" });
    list(s, ["**Deep industry experience** (Banking & Technology)", "**Specialized Consulting Practice** - exclusively on technology workforces", "**Thought partnership** - hands-on support and rapid results", "**Rapid ROI** - high impact; lower cost than big consulting"],
      { x: 0.9, y: 2.1, w: 5.75, h: 1.6, fontSize: 13.5 }, { after: 3 });
    s.addShape(S.MATH_PLUS, { x: 3.4, y: 3.83, w: 0.6, h: 0.6, fill: { color: H.teal }, line: { color: H.teal }, objectName: "Plus" });
    box(s, 0.55, 4.45, 6.3, 2.45, { rounded: true, lineW: 1.5 });
    header(s, "Consortium & Analytics", 0.85, 4.5, 5.7, { icon: "PiBrain" });
    list(s, ["**Actionable Benchmarks** - across internal SOWs and peers", "**Analytics** - identification of leakage, overbilling, and workforce mix relative to peers", "**Best Practices** - trusted network, shared insights, and collective intelligence", "**AI platform** - working prototype today; every rate traced to its source page"],
      { x: 0.9, y: 5.1, w: 5.75, h: 1.75, fontSize: 13.5 }, { after: 3 });
    s.addShape(S.MATH_EQUAL, { x: 7.1, y: 3.7, w: 0.7, h: 0.6, fill: { color: H.teal }, line: { color: H.teal }, objectName: "Equals" });
    box(s, 8.05, 1.45, 4.83, 5.45, { rounded: true, lineW: 1.5 });
    header(s, "Opportunity & Impact", 8.35, 1.5, 4.25, { icon: "PiCoins" });
    list(s, [
      { t: "**10-15% cost savings** (against baseline of 3rd party labor cost)", after: 14 },
      { t: "**Access to Proprietary Benchmarks and Analytics** (industry labor rates and workforce mix)", after: 14 },
      { t: "**Peer Learning and Workshops** (leading best practices and access to collective intelligence)", after: 14 },
      { t: "**Leading Partner** to guide the development of an AI utility for workforce mgmt." },
    ], { x: 8.4, y: 2.2, w: 4.25, h: 4.5, fontSize: 15 });
  }

  // 9. Summary of Technical Approach
  {
    const s = content("Summary of Technical Approach",
      "Sources: Summary Technical Approach v1.2 slide 2 and Consortium Approach v1.7 slide 11 (tiles and labels). The closing lines are corrected per the architecture decisions: what improves globally is the shared vocabulary and anonymized benchmark summaries, not model weights.");
    const tiles = [["Document Ingestion", "PiFileText", H.lblue], ["Automated Extraction", "PiCpu", H.mid], ["Master Benchmark Ledger", "PiTreeStructure", "4472C4"], ["Compare Skill Matrices", "PiClipboardText", "2E5C9A"], ["Quantify Spend Savings", "PiArrowsClockwise", H.dblue]];
    const tw = 1.95, gap = 0.27, x0 = (13.333 - (5 * tw + 4 * gap)) / 2;
    tiles.forEach((t, i) => {
      const x = x0 + i * (tw + gap);
      box(s, x, 1.5, tw, 2.05, { rounded: true, fill: t[2], noLine: true, radius: 0.15 });
      const dark = i === 0;
      txt(s, t[0], { x: x + 0.1, y: 1.62, w: tw - 0.2, h: 0.75, fontSize: 15, bold: true, color: dark ? H.navy : "FFFFFF", align: "center", valign: "top" });
      icon(s, t[1], x + (tw - 0.8) / 2, 2.55, 0.8, dark ? H.navy : "FFFFFF");
    });
    s.addShape(S.LINE, { x: x0, y: 3.9, w: 5 * tw + 4 * gap, h: 0, line: { color: H.teal, width: 1.5 } });
    txt(s, "Data Sovereignty\nIn-Tenant Deployment", { x: x0 + 0.1, y: 4.05, w: 3.6, h: 0.8, fontSize: 18, bold: true, color: H.navy });
    txt(s, "End-to-End Solution", { x: 4.9, y: 4.05, w: 3.5, h: 0.4, fontSize: 18, bold: true, color: H.navy, align: "center" });
    txt(s, "Audit Trails\nExpert Validation", { x: 8.5, y: 4.05, w: x0 + 5 * tw + 4 * gap - 8.6, h: 0.8, fontSize: 18, bold: true, color: H.navy, align: "right" });
    txt(s, [
      ...parse("Utilizes Azure solutions to extract and normalize unstructured vendor contracts into a **standardized Master Benchmark Ledger** – every rate traced to its source page.", {}),
      { text: "", options: { breakLine: true } },
      ...parse("Employs a **federated, in-tenant architecture**: only the shared vocabulary and anonymized benchmark summaries leave – **sensitive data never moves** outside the corporate firewall.", {}),
    ], { x: 1.2, y: 5.2, w: 10.93, h: 1.5, fontSize: 17, align: "center" });
  }

  // 10. Follow one rate
  {
    const s = content("Follow one rate from the page to the ledger: a real State of Texas contract with Accenture",
      "Source: docs/story/follow-one-rate.html and its PDF (pipeline run of Oct 6, 2026). Image: page 8 of Attachment 2.1, Pricing and Volumes, Texas contract DIR-STS-TSS-699; the red box is drawn from the position the ledger stores. Kyle's decision 7: Accenture and Texas shown by name.");
    chevrons(s, ["Document Library", "Intake", "Reading", "Extraction", "Normalization", "Ledger"], 1.5, 0.6, [H.navy, H.navy, H.navy, H.navy, H.navy, H.mid], { size: 13 });
    const caps = ["Texas contract DIR-STS-TSS-699, page 8", "Seven files recognized as one contract set", "111-row rate table – every cell’s position", "“$83.00 per hour” – checked against the page", "Systems Engineer, senior – resolved once", "Stored with page 8 and its position"];
    caps.forEach((c, i) => txt(s, c, { x: L + i * (CW / 6) + 0.08, y: 2.2, w: CW / 6 - 0.16, h: 0.75, fontSize: 12, align: "center" }));
    const ih = CW / 9.615;
    s.addImage({ path: path.join(IMG, "page8_ase.png"), x: L, y: 3.1, w: CW, h: ih, altText: "The Advanced Systems Engineer row on page 8, boxed in red", objectName: "Row on page 8" });
    box(s, L, 3.1, CW, ih, { line: H.rule, lineW: 0.75, name: "Image border" });
    txt(s, "Page 8 of Attachment 2.1, Pricing and Volumes. The red box is drawn from the position the ledger stores.", { x: L, y: 3.1 + ih + 0.05, w: CW, h: 0.3, fontSize: 11, color: H.grey, italic: true });
    banner(s, "“Advanced Systems Engineer, $83.00 per hour” becomes Systems Engineer, senior – stored with page 8 and its position. Nothing in the ledger is an estimate: a vendor who challenges a rate is shown the page.", L, 5.45, CW, 1.05, { size: 16, bold: false });
  }

  // 11. Precision first
  {
    const s = content("Precision first: when the platform is not sure, it asks – and every answer becomes a rule",
      "Sources: docs/story/follow-one-rate.html; the ledger (row 19; review queue); architecture decision 5 (precision first). Image: the same page, fourteen rows down, boxed in amber.");
    const ih = CW / 15.38;
    s.addImage({ path: path.join(IMG, "page8_ops.png"), x: L, y: 1.5, w: CW, h: ih, altText: "The Operations row on page 8, boxed in amber", objectName: "Operations row" });
    box(s, L, 1.5, CW, ih, { line: H.rule, lineW: 0.75, name: "Image border" });
    txt(s, "Same page, fourteen rows down.", { x: L, y: 1.5 + ih + 0.05, w: CW, h: 0.3, fontSize: 11, color: H.grey, italic: true });
    const bx = [
      ["Abstain, don’t guess", "PiWarningCircle", "“Operations, $99.50 per hour” names no role. The model abstained; the row is **stored, but not counted** until an analyst decides."],
      ["No defaults", "PiListChecks", "No default seniority and no guessed location. **23 of the 53 titles** on this page state no seniority – they keep their role and stay unbanded."],
      ["Resolve once", "PiArrowsClockwise", "Every analyst decision becomes a rule, so **no question is asked twice** – the same title is never resolved two ways."],
    ];
    const w = (CW - 2 * 0.3) / 3;
    bx.forEach((b, i) => {
      const x = L + i * (w + 0.3);
      box(s, x, 2.85, w, 2.65, { rounded: true, lineW: 1.5 });
      header(s, b[0], x + 0.3, 2.95, w - 0.6, { icon: b[1], size: 17 });
      txt(s, b[2], { x: x + 0.3, y: 3.6, w: w - 0.6, h: 1.8, fontSize: 15 });
    });
    banner(s, "One false claim of overbilling in front of a vendor can lose the engagement; a missed saving is caught at the next refresh", L, 5.8, CW, 0.8, { rounded: true, size: 16 });
  }

  // 12. Technical approach: in-tenant, own vs rent
  {
    const s = content("Technical Approach: in-tenant by design – we rent the best AI models and own what makes them reliable",
      "Sources: architecture decisions 1, 2, 3, 4 and 6; decision log (data boundary, Oct 6; disclosure gate, Oct 13). Replaces 'Confidential Weight Management ... only Neural Weights ... Differential Privacy Smudging' and the GPT-4o references in the Summary Technical Approach v1.2. Kyle's decision 8: taught, not trained.");
    header(s, "In-Tenant Architecture", L, 1.45, 6.0, { icon: "PiLockKey", size: 18 });
    list(s, [
      "**Installed inside each client’s own Azure environment** (Canada Central for Canadian clients) – an installable stack, not a website",
      "**Never leaves:** documents, individual rates, vendor–client relationships, analysts’ reasoning",
      "**Only leaves:** the shared vocabulary and anonymized benchmark summaries – each from at least 3 observations and 2 clients; vendors shown only as a class",
      "**Disclosure check** on every contract set before anything is benchmarked",
      "**Audit trail** linking every rate back to the original page and position",
      "**Human-in-the-loop** review queue for anything uncertain",
    ], { x: L + 0.05, y: 2.1, w: 5.95, h: 4.8, fontSize: 15 }, { after: 7 });
    header(s, "Own vs. Rent", 6.88, 1.45, 6.0, { icon: "PiPuzzlePiece", size: 18 });
    list(s, [
      "**Rent** the frontier reasoning models through Microsoft Foundry – Claude primary, GPT benchmarked; no lock-in to one AI vendor",
      "**Own** the role framework, the mapping table, the page checks, the inventory of rate-changing fine print, the evaluation sets, and the consortium benchmark",
      "**Taught, not retrained:** every analyst decision becomes a rule, and the vocabulary sharpens across clients",
      "**The moat:** a benchmark built from data no one else can see, improving with every client",
    ], { x: 6.93, y: 2.1, w: 5.95, h: 4.8, fontSize: 15 }, { after: 7 });
  }

  // 13. Progress (1/3): document library
  {
    const s = content("Progress to date (1/3): a document library of 438 real public contracts, rate cards and invoices",
      "Sources: docs/corpus-sources-and-demo-set.md; action items B30 and B35 (counts measured Nov 22, 2026). Thumbnails: Texas DIR Accenture pricing page 8; Texas DIR ITSAC not-to-exceed rate card, page 1; Michigan DTMB Deloitte MiIntegrate contract, page 6; Oklahoma OMES Deloitte signed contract, page 4.");
    header(s, "Contracts, rate cards and invoices (largely government and SEC sourcing)", L, 1.45, 6.85, { size: 15 });
    const thumbs = ["page8_full.png", "lib_tx_nte.png", "lib_mi_deloitte.png", "lib_ok_deloitte.png"];
    thumbs.forEach((t, i) => {
      const w = 2.45, h = w / 0.7727, x = 0.6 + i * 1.38, y = 2.15 + (i % 2) * 0.3;
      s.addImage({ path: path.join(IMG, t), x, y, w, h, altText: "A page from a public contract or rate card in the document library", objectName: `Library page ${i + 1}` });
      box(s, x, y, w, h, { line: H.grey, lineW: 0.75, name: "Page border" });
    });
    box(s, L, 6.25, 6.85, 0.62, { rounded: true, lineW: 1.5 });
    txt(s, "Preliminary models built with **public data before securing access to client information**", { x: L + 0.15, y: 6.25, w: 6.55, h: 0.62, fontSize: 14, bold: true, align: "center", valign: "middle" });
    header(s, "What we gathered", 7.65, 1.45, 5.23, { icon: "PiBooks", size: 15 });
    list(s, [
      "**About 240** contracts US public companies filed with the securities regulator – MSAs, amendments, SOWs",
      "**5 Texas and 13 Michigan** contract sets with rates visible – including a **$109M, 13-year Deloitte** contract",
      "**48** signed UK government contracts and **13** major vendors’ UK rate cards (about 2,600 priced rows)",
      "**Canadian federal TBIPS** packages – 12 in French or bilingual",
      "**A public invoice with its timesheets** – the rarest find",
      "About **226 vendor-client pairs**, 51 with two or more documents – real contract sets to follow end to end",
    ], { x: 7.7, y: 2.1, w: 5.15, h: 4.8, fontSize: 14 }, { after: 7 });
  }

  // 14. Progress (2/3): role framework
  {
    const s = content("Progress to date (2/3): TWM’s own role framework – the platform places any vendor title in it, or asks",
      "Sources: taxonomy/REPORT.md (Oct 13, 2026); taxonomy/HELDOUT.md; decision log (Oct 6, 2026: first analyst review, 65 titles, 72 codified). Kyle's decision 8: taught, not trained.");
    header(s, "TWM Role Framework", L, 1.45, 6.2, { icon: "PiTreeStructure", size: 18 });
    list(s, [
      "**129 roles** in **18 families**, with **4 seniority bands** (junior, intermediate, senior, lead/principal)",
      "Built from open public sources: **US O*NET, UK government job ladders and Canada’s TBIPS categories**",
      "Location and technology recorded beside the role – **never multiplied into it**",
      "**547 vendor titles** mapped, each with its reasoning, who decided, and a version",
      "Versioned like software – mappings are added or retired, never silently edited",
    ], { x: L + 0.05, y: 2.1, w: 6.15, h: 4.7, fontSize: 15 }, { after: 8 });
    header(s, "Tested on 113 titles it had never seen", 7.1, 1.45, 5.78, { size: 18 });
    s.addChart(pres.charts.BAR, [{ name: "Placed", labels: ["By the rules alone", "After one review pass"], values: [40.7, 95.6] }], {
      x: 7.1, y: 2.1, w: 5.78, h: 3.6, barDir: "col", chartColors: [H.navy],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0"%"', dataLabelFontSize: 16, dataLabelColor: H.navy, dataLabelFontFace: "+mn-lt",
      valAxisMaxVal: 110, valAxisMinVal: 0, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      catAxisLabelColor: "000000", catAxisLabelFontSize: 14, catAxisLabelFontFace: "+mn-lt", showLegend: false, barGapWidthPct: 80,
    });
    txt(s, "The platform learns from analyst decisions, not from retraining a model", { x: 7.1, y: 5.85, w: 5.78, h: 0.7, fontSize: 16, bold: true, color: H.navy, align: "center" });
  }

  // 15. Progress (3/3): working prototype
  {
    const s = content("Progress to date (3/3): the full pipeline runs end to end on real contracts today",
      "Sources: work/m2-thin-thread/review.md; work/contract-terms/review.md; action items B17, B24, B25, B26, B30, C4 and C12; test suite (Nov 22, 2026). FOR KYLE: a workbench screenshot would strengthen this slide; it needs a fresh capture.");
    const sets = [["Texas – Accenture", "Seven-file government contract set; **1,648 verified rates** from one pricing table across eight contract years"], ["UK – Accenture", "G-Cloud rate page read straight from the web page – **430 rates**"], ["Michigan – Deloitte", "13-year contract with every change notice, read through **the same code**"]];
    const w = (CW - 2 * 0.3) / 3;
    sets.forEach((st, i) => {
      const x = L + i * (w + 0.3);
      box(s, x, 1.45, w, 0.5, { fill: H.navy, noLine: true });
      txt(s, st[0], { x, y: 1.45, w, h: 0.5, fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
      box(s, x, 1.95, w, 1.25, { lineW: 1 });
      txt(s, st[1], { x: x + 0.2, y: 2.05, w: w - 0.4, h: 1.1, fontSize: 14 });
    });
    list(s, [
      "**1,034 contract terms** read – escalation, discounts, expenses – each quote proven word for word on its page",
      "**Analyst workbench** – the review queue; click any rate through to its page; every answer recorded with who and why",
      "**About $6.50** of model spend for the full Texas and Michigan runs; repeat runs are free",
      "**166 automated tests**, each listed as a plain-English promise",
    ], { x: L + 0.05, y: 3.55, w: 7.1, h: 3.3, fontSize: 15 }, { after: 9 });
    box(s, 7.95, 3.5, 4.93, 3.35, { fill: H.lgrey, line: H.grey, lineW: 0.75 });
    list(s, [
      { t: "**Next**", nob: true, color: H.navy },
      "The whole library through the pipeline",
      "Accuracy measured against hand-checked answer sheets",
      "Benchmarking, findings and savings",
      { t: "TWM’s Azure environment, then the first client installation", after: 10 },
      { t: "[[Not claimed yet]]", nob: true },
      "No accuracy figure until the answer sheets are hand-checked",
      "No savings figure until the findings are built",
    ], { x: 8.2, y: 3.65, w: 4.5, h: 3.1, fontSize: 13.5 }, { after: 3 });
  }

  // 16. Platform roadmap
  {
    const s = content("Technology Workforce Management Platform",
      "Source: Business Plan deck v1.4 slide 6 (layout and wording, condensed); Business Plan v1.5 (phases). Phase 1 bullets updated to what the platform does today.");
    txt(s, "A platform to manage third-party labor – implemented in phases", { x: L, y: 0.85, w: CW, h: 0.45, fontSize: 18, bold: true, italic: true, color: H.navy });
    // Phase 2, top
    box(s, 3.7, 1.45, 5.93, 1.1, { rounded: true, fill: H.cyan, line: H.navy, lineW: 0.75 });
    list(s, [{ t: "**Forecasting and Forward-Looking Demand**", nob: true }, "One view of open and upcoming roles, replacing manual (often MS-Excel) workforce processes", "Forecasts alongside financial projections, linked to approvals; rapid “what-if” scenario planning"],
      { x: 3.9, y: 1.5, w: 5.55, h: 1.0, fontSize: 11.5 }, { after: 1 });
    // Phase 1, centre
    box(s, 3.7, 2.8, 5.93, 2.3, { rounded: true, fill: "000000", noLine: true });
    list(s, [{ t: "**Third Party Technology Workforce Management**", nob: true, size: 15, align: "center", after: 4 },
      "AI structures labor rates from numerous SOWs into one traceable Master Benchmark Ledger",
      "Skill matrices standardized against TWM’s role framework to identify pricing anomalies and benchmark",
      "Compares the timecard billed, the invoice charged and the contracted rate",
      "A Consulting Practice turns findings into savings, negotiations and labor mix changes"],
      { x: 3.9, y: 2.9, w: 5.55, h: 2.1, fontSize: 12.5, color: "FFFFFF" }, { after: 3 });
    // Future phases
    const fut = [
      [L, 2.8, 3.0, 2.3, "Financial Management", ["Track labor rates and unit costs", "Monitor assumptions vs. actuals (i.e. capitalization rates)", "Link workforce and labor to the G/L", "Timesheet capture"]],
      [9.88, 2.8, 3.0, 2.3, "Delivery Program Productivity", ["Align to Agile and Waterfall delivery programs", "Team and POD visualizations and analytics", "Track feature velocity and releases"]],
      [3.7, 5.35, 5.93, 1.5, "Ready Day-One and Ongoing Compliance", ["New hires and labor moves ready on their first day", "Provision computers, tools and access with approval workflows", "Labor lifecycle mgmt; track third-party compliance with policies"]],
    ];
    fut.forEach((f) => {
      box(s, f[0], f[1], f[2], f[3], { rounded: true, fill: H.pale, line: H.navy, lineW: 0.75 });
      list(s, [{ t: `**${f[4]}**`, nob: true }, ...f[5]], { x: f[0] + 0.15, y: f[1] + 0.1, w: f[2] - 0.3, h: f[3] - 0.2, fontSize: 11.5 }, { after: 1 });
    });
    s.addShape(S.UP_ARROW, { x: 6.47, y: 2.56, w: 0.4, h: 0.23, fill: { color: "000000" }, line: { color: "000000" }, objectName: "Arrow up" });
    s.addShape(S.DOWN_ARROW, { x: 6.47, y: 5.11, w: 0.4, h: 0.23, fill: { color: "000000" }, line: { color: "000000" }, objectName: "Arrow down" });
    s.addShape(S.LEFT_ARROW, { x: 3.46, y: 3.75, w: 0.23, h: 0.4, fill: { color: "000000" }, line: { color: "000000" }, objectName: "Arrow left" });
    s.addShape(S.RIGHT_ARROW, { x: 9.64, y: 3.75, w: 0.23, h: 0.4, fill: { color: "000000" }, line: { color: "000000" }, objectName: "Arrow right" });
    box(s, L, 5.5, 2.75, 1.35, { rounded: true, lineW: 1 });
    [["000000", "Phase 1"], [H.cyan, "Phase 2"], [H.pale, "Future Phases and Considerations"]].forEach((lg, i) => {
      box(s, L + 0.15, 5.65 + i * 0.38, 0.45, 0.25, { fill: lg[0], line: H.navy, lineW: 0.5 });
      txt(s, lg[1], { x: L + 0.7, y: 5.62 + i * 0.38, w: 2.0, h: 0.32, fontSize: 11, bold: true, valign: "middle" });
    });
  }

  // 17. Organization structure
  {
    const s = content("TWM Organization Structure – Year 1",
      "Source: Business Plan deck v1.4 slide 9 (layout and wording); Business Plan v1.5 (leadership). Kyle's decision 6: additional leadership to be announced.");
    box(s, L, 1.5, 3.6, 0.75, { rounded: true, fill: H.navy, noLine: true });
    txt(s, "TWM Leadership (1-2 teammates)", { x: L, y: 1.5, w: 3.6, h: 0.75, fontSize: 15, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    box(s, L, 2.75, 3.6, 0.7, { rounded: true, fill: H.teal, noLine: true });
    txt(s, "Consulting Practice Leadership (1-2 teammates)", { x: L + 0.1, y: 2.75, w: 3.4, h: 0.7, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    [0, 1].forEach((i) => {
      const x = L + i * 1.85;
      box(s, x, 3.52, 1.75, 0.42, { fill: H.teal, noLine: true });
      txt(s, "Engagement Manager", { x, y: 3.52, w: 1.75, h: 0.42, fontSize: 11.5, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
      box(s, x, 4.0, 1.75, 0.42, { fill: H.teal, noLine: true });
      txt(s, "+ 3-4 Associates", { x, y: 4.0, w: 1.75, h: 0.42, fontSize: 11.5, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    });
    box(s, L, 4.7, 3.6, 0.6, { rounded: true, fill: H.pale, line: H.navy, lineW: 1 });
    txt(s, "AI and Software Team Leadership (~2 teammates)", { x: L + 0.1, y: 4.7, w: 3.4, h: 0.6, fontSize: 12.5, bold: true, color: H.navy, align: "center", valign: "middle" });
    ["AI/ML & Data Engineering (2-4 teammates)", "Software Engineering (2-4 teammates)", "Security & Compliance (1-2 teammates)", "Product & Project Mgmt (1-2 teammates)"].forEach((t, i) => {
      box(s, L + 0.35, 5.38 + i * 0.37, 3.25, 0.32, { rounded: true, fill: H.pale, line: H.navy, lineW: 0.75, radius: 0.06 });
      txt(s, t, { x: L + 0.4, y: 5.38 + i * 0.37, w: 3.15, h: 0.32, fontSize: 10.5, bold: true, color: H.navy, align: "center", valign: "middle" });
    });
    list(s, [
      { t: "**TWM leadership tackled problem statement across numerous organizations**", nob: true },
      "Additional leadership to be announced",
      "**Kyle McNamara** - global tech leader - large teams in Canada, the US, South America, and Australia",
      { t: "At TD Bank, **led 6,200+** with a $1.8B+ annual budget", lvl: 1 },
      { t: "At National Australia Bank - Chief Transformation Officer – executed **cost reductions of $1B+** - large portion through third-party labor", lvl: 1 },
      { t: "At Scotiabank, oversaw a $1.5B+ annual budget and **5,000+ staff globally**", lvl: 1 },
    ], { x: 4.4, y: 1.45, w: 8.45, h: 1.95, fontSize: 13 }, { after: 2 });
    s.addShape(S.LINE, { x: 4.4, y: 3.42, w: 8.45, h: 0, line: { color: H.rule, width: 1 } });
    list(s, [
      "Focus exclusively on **optimizing third-party labor**",
      "Led by **ex-McKinsey or ex-BCG leaders** – experienced in optimizing third-party labor",
      "**Organized in Pods** led by Engagement Managers managing client relationships",
      "**Gather real-world data, insights, and requirements** from Early Adopters",
    ], { x: 4.4, y: 3.55, w: 8.45, h: 1.1, fontSize: 13 }, { after: 2 });
    s.addShape(S.LINE, { x: 4.4, y: 4.72, w: 8.45, h: 0, line: { color: H.rule, width: 1 } });
    list(s, [
      "Includes **roles in AI/ML engineering, software engineering, security, and product management**",
      "**Owns the product roadmap** – and the sequencing and prioritization of features",
      "**Builds the extraction, normalization and benchmarking pipeline**, the review workbench and the analytics",
      "Implements encryption, conducts security audits, and **adopts stringent standards**, especially for sensitive data",
    ], { x: 4.4, y: 4.85, w: 8.45, h: 2.0, fontSize: 13 }, { after: 2 });
  }

  // ======================================================= ENDING A
  section = "Early Adopter Consortium";
  pres.addSection({ title: section });
  divider("Early Adopter Consortium", "For Early Adopter CIOs");

  // A1. Consortium Framework (1/2)
  {
    const s = content("Consortium Framework (1/2)", "Source: Consortium Approach v1.7 slide 6, wording kept.");
    chevrons(s, ["Value Acceleration (4-6 Months)", "Execution (TBD)", "Capability Development (TBD)"], 1.4, 0.65, [H.navy, H.mid, H.mid], { size: 16 });
    box(s, 0.6, 2.35, 6.85, 3.8, { lineW: 1 });
    list(s, [
      { t: "**Value Acceleration Deliverables:**", nob: true },
      { t: "**Opportunity Assessment Report and Presentation**", nob: true },
      "Quantification of “full potential” cost savings", "Preliminary identification of inefficiencies, cost leakage, and waste", "Clear articulation of findings, opportunities, and next steps",
      { t: "**Preliminary Target State Definition**", nob: true }, "Vision for future workforce (resources, locations, seniority, skills)",
      { t: "**Benchmarking Analysis**", nob: true }, "Sampling of current labor rates and mix against industry peers",
      { t: "**Quick Wins Identification**", nob: true }, "List of immediate actions (e.g., renegotiating SOWs, skill matrices)", "Prioritization of high-impact opportunities",
      { t: "**Initial Roadmap & Action Plan**", nob: true }, "Next steps for value realization and strategic workforce alignment", "Timeline and milestones for subsequent phases",
    ], { x: 0.75, y: 2.45, w: 6.6, h: 3.65, fontSize: 12 }, { after: 0 });
    box(s, 7.75, 2.35, 5.1, 3.3, { lineW: 1 });
    list(s, [
      { t: "**Supported by Consortium Workshops**", nob: true },
      { t: "__Sharing Leading Practices & Industry Insights__", nob: true, after: 3 },
      "**Facilitate Peer Learning:** Highlight best practices, proven methods & lessons learned",
      "**Industry Benchmarking:** Sampling of anonymized benchmarking data and insights to compare performance",
      "**Interactive Problem-Solving:** Co-create new approaches tailored to evolving the org and operating model in the Age of AI",
      "**Networking & Relationship Building:** Informal networking, fostering trust and long-term relationships",
    ], { x: 7.9, y: 2.45, w: 4.85, h: 3.15, fontSize: 12.5 }, { after: 3 });
    banner(s, "Confidential information - Each Member’s data will be separate, ensuring no organization can view another’s confidential information. All views and analytics will be sanitized and anonymized", 0.6, 6.3, 12.25, 0.62, { size: 13, bold: false });
  }

  // A2. Consortium Framework (2/2)
  {
    const s = content("Consortium Framework (2/2)", "Source: Consortium Approach v1.7 slide 7, wording kept.");
    chevrons(s, ["Value Acceleration (4-6 Months)", "Execution (TBD)", "Capability Development (TBD)"], 1.4, 0.65, ["outline", H.navy, H.mid], { size: 16 });
    box(s, L, 2.3, 6.55, 3.05, { lineW: 1 });
    list(s, [
      { t: "**Execution – Action Value Acceleration Outcomes**", nob: true },
      { t: "__Key Activities and Deliverables:__", nob: true },
      "**Detailed Opportunity Analysis:** Deeper insights into cost drivers, inefficiencies, and areas for improvement",
      "**Actionable Recommendations:** Strategies for updating skill matrices, renegotiating contracts, & optimizing labor mix",
      "**Stakeholder Engagement:** Facilitate ongoing alignment (i.e. across HR, Finance, Procurement, Tech)",
      "**Implementation Roadmap:** Comprehensive plan with actions, timelines, and responsibilities",
      "**Progress Tracking:** Establish metrics and dashboards to monitor implementation progress and savings",
      "**Consortium Collaboration:** Continue sharing insights and innovations to drive collective progress",
    ], { x: L + 0.15, y: 2.4, w: 6.3, h: 2.9, fontSize: 12 }, { after: 1 });
    box(s, 7.2, 2.3, 5.68, 3.05, { line: H.blue, lineW: 1 });
    list(s, [
      { t: "[[Capability Development – Sustainable long-term tools, processes, and capabilities]]", nob: true },
      { t: "__Key Activities and Deliverables:__", nob: true },
      "[[Tool Implementation:]] Deploy analytics, reporting, and related tools, etc.",
      "[[Process Standardization:]] Processes for demand forecasting, workforce planning, etc.",
      "[[Capability Building:]] Develop internal expertise to ensure sustainable adoption of new tools and processes",
      "[[Continuous Improvement Framework:]] Mechanisms for regular review, benchmarking refreshes, and iterative enhancements",
      "[[Consortium Collaboration:]] Continue sharing insights and innovations to drive collective progress",
    ], { x: 7.35, y: 2.4, w: 5.43, h: 2.9, fontSize: 12 }, { after: 1 });
    box(s, L, 5.55, CW, 1.35, { fill: H.lgrey, line: H.navy, lineW: 0.75 });
    list(s, [
      { t: "[[Benefits of Consortium Approach]]", nob: true },
      "[[Collective Intelligence:]] Pooling anonymized data and insights creates a richer, more accurate picture of industry norms and opportunities for improvement",
      "[[Innovation:]] Adopt Best Practices for a future-ready operating model to thrive in the AI era",
      "[[Faster ROI:]] Executable solutions lead to faster realization of cost savings and operational improvements",
      "[[Industry Leadership:]] Establish new norms for transparency, efficiency, and strategic workforce management",
    ], { x: L + 0.15, y: 5.62, w: CW - 0.3, h: 1.25, fontSize: 12 }, { after: 0 });
  }

  // A3. Team and approach for value acceleration
  {
    const s = content("Team and approach for value acceleration", "Source: Consortium Approach v1.7 slide 8, wording kept; additional leadership to be announced (Kyle's decision 6).");
    box(s, L, 1.4, 3.95, 0.55, { fill: H.navy, noLine: true });
    txt(s, "Consortium Member", { x: L, y: 1.4, w: 3.95, h: 0.55, fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    box(s, L, 1.95, 3.95, 4.95, { lineW: 1 });
    list(s, [
      { t: "**Leadership Support**", nob: true }, "CIO sponsorship and leadership", "Hands-on internal alignment", "Assign primary/dedicated leader", "Leadership from Procurement and other critical areas (i.e. HR, Finance)",
      { t: "**Data**", nob: true }, "Provide access to relevant data sets (e.g., SOWs, invoices, timecards)", "Ensure data is accurate and timely - participate in data validation sessions",
      { t: "**Stakeholder Engagement**", nob: true }, "Align subject matter experts and key stakeholders for workshops/meetings",
      { t: "**Workshop Participation**", nob: true }, "Consortium workshops to share leading practices, industry insights, and collaborative problem-solving",
    ], { x: L + 0.12, y: 2.05, w: 3.75, h: 4.8, fontSize: 12 }, { after: 1 });
    box(s, 4.6, 1.4, 8.28, 0.55, { fill: H.mid, noLine: true });
    txt(s, "TWM Team", { x: 4.6, y: 1.4, w: 8.28, h: 0.55, fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
    box(s, 4.6, 1.95, 8.28, 4.95, { line: H.mid, lineW: 1 });
    const inner = [
      [4.75, 2.1, 3.95, 1.85, [{ t: "[[TWM Leadership]]", nob: true }, "Hands on TWM leadership team - strategic oversight and SME knowledge", "Lead workshops with each member and across the consortium", "Methodology, ensure consistency, and benchmarking across members"]],
      [4.75, 4.1, 3.95, 2.65, ["[[Kyle McNamara]] – managed large teams in Canada, USA, South America, and Australia (with over 5,000 staff & budgets greater than $1.5B)", "[[Additional Leadership]] – to be announced – including ex-McKinsey or ex-BCG", "[[Consulting Practice]] – team of experts experienced in optimizing technology labor spend"]],
      [8.85, 2.1, 3.88, 2.65, [{ t: "[[Engagement Pods]]", nob: true }, "Collect, validate, & analyze data (SOWs, invoices, contracts, timecards)", "Facilitate stakeholder interviews and workshops", "Develop tailored opportunity assessments and preliminary target state recommendations", "Quick Win identification and planning"]],
      [8.85, 4.9, 3.88, 1.85, [{ t: "[[“Pod” for Each Member:]]", nob: true }, "Engagement Manager (covering 2 consortium members)", "Workforce Analytics Lead", "Data Analyst"]],
    ];
    inner.forEach((b) => {
      box(s, b[0], b[1], b[2], b[3], { line: H.mid, lineW: 0.75 });
      list(s, b[4], { x: b[0] + 0.1, y: b[1] + 0.07, w: b[2] - 0.2, h: b[3] - 0.12, fontSize: 12 }, { after: 2 });
    });
  }

  // A4. Participation and why join now
  {
    const s = content("Early Adopter participation: founding members get the deepest discount, earliest benchmarks, and most influence",
      "Sources: Kyle's decision 1 (Nov 22, 2026): $1.5MM per Early Adopter, contingent on the engagement generating more than $10MM in value for that client. Early Adopter Presentation (why join now; influence and co-development; next steps). Business Plan v1.5 (McKinsey team cost). Pitch Deck v1.1 (cost of delay).");
    box(s, L, 1.45, 5.0, 4.75, { fill: H.navy, noLine: true });
    txt(s, "$1.5MM", { x: L + 0.35, y: 1.6, w: 4.3, h: 1.1, fontSize: 60, bold: true, fontFace: "Aptos Display", color: "FFFFFF", valign: "bottom" });
    txt(s, "per Early Adopter", { x: L + 0.35, y: 2.75, w: 4.3, h: 0.45, fontSize: 18, color: H.lblue });
    txt(s, "Contingent on the engagement generating **more than $10MM in value** for that client – the fee is never more than 15% of the value created",
      { x: L + 0.35, y: 3.4, w: 4.3, h: 1.4, fontSize: 16, color: "FFFFFF" });
    txt(s, "For comparison, a McKinsey engagement team (EM + 4 Associates) runs about **$1.5MM per month**", { x: L + 0.35, y: 4.95, w: 4.3, h: 1.1, fontSize: 14, color: H.lblue });
    header(s, "Why join now?", 5.9, 1.45, 6.98, { icon: "PiHandshake", size: 18 });
    list(s, [
      "**Be a founding member** and shape the future of technology workforce management",
      "**Gain early access** to proprietary benchmarks and insights",
      "**Achieve rapid, measurable cost savings** – months, not years",
      "**Influence and co-development** – a seat at the table on the platform’s features, priorities and roadmap",
      "**Cost of delay** – about $3MM per week on a $150MM opportunity",
    ], { x: 5.95, y: 2.1, w: 6.9, h: 4.1, fontSize: 15 }, { after: 9 });
    banner(s, "Next steps: how to join the consortium, key contacts and follow-up process", L, 6.4, CW, 0.52, { rounded: true, size: 15 });
  }

  // ======================================================= ENDING B
  section = "Investor Overview";
  pres.addSection({ title: section });
  divider("Investor Overview", "Market, go-to-market, timelines and financial model");

  // B1. Market Opportunity
  {
    const s = content("Market Opportunity: a $1.87 trillion IT services market with no purpose-built solution for third-party labor",
      "Sources: Pitch Deck v1.1 section 4 (TAM, SAM, SOM; provider headcounts, citing Gartner and IDC); Business Plan v1.5 (target market analysis). Kyle's decision 4: organizations with $100MM+ in third-party technology labor spend.");
    const rows = [
      ["PiChartBar", "**Total Addressable Market:** Gartner and IDC estimate 2026 IT Services spend at **$1.87 trillion** (+8.7% Y/Y)"],
      ["PiTarget", "**Serviceable Addressable Market:** organizations with **$100MM+ in third-party labor spend** – typically 500+ third-party resources"],
      ["PiBank", "**Serviceable Obtainable Market:** **1,500+ companies** globally, ~50% in North America – **400+** in North American BFSI and Telecommunications"],
      ["PiRocketLaunch", "**TWM’s goal: capture 50+ of these clients**"],
    ];
    rows.forEach((r, i) => {
      const y = 1.5 + i * 1.3;
      icon(s, r[0], 0.6, y + 0.15, 0.6);
      txt(s, r[1], { x: 1.5, y, w: 5.75, h: 1.15, fontSize: 15, valign: "middle" });
      if (i < rows.length - 1) s.addShape(S.LINE, { x: 1.4, y: y + 1.22, w: 5.9, h: 0, line: { color: H.rule, width: 1 } });
    });
    txt(s, "The top seven IT services providers have ~3MM employees", { x: 7.75, y: 1.45, w: 5.13, h: 0.45, fontSize: 15, bold: true, color: H.navy });
    const data = [["Accenture", "784,000"], ["Tata Consultancy Services (TCS)", "582,000"], ["Capgemini", "423,000"], ["Cognizant", "352,000"], ["Infosys", "337,000"], ["IBM Consulting", "270,000"], ["HCLTech", "226,000"]];
    const hdr = (t, al) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: H.navy }, align: al } });
    const rowsT = [[hdr("Company", "left"), hdr("Approximate Employees", "right")],
      ...data.map((d, i) => [{ text: d[0], options: { fill: { color: i % 2 ? "FFFFFF" : H.lgrey } } }, { text: d[1], options: { align: "right", fill: { color: i % 2 ? "FFFFFF" : H.lgrey } } }]),
      [{ text: "Total", options: { bold: true } }, { text: "2,974,000", options: { bold: true, align: "right" } }]];
    s.addTable(rowsT, { x: 7.75, y: 2.0, w: 5.13, colW: [3.13, 2.0], fontSize: 13, fontFace: "Aptos", color: "000000", rowH: 0.42, margin: [0.04, 0.1, 0.04, 0.1], border: { type: "solid", pt: 0.5, color: H.rule } });
    txt(s, "Source: Pitch Deck v1.1, citing Gartner and IDC", { x: 7.75, y: 6.3, w: 5.13, h: 0.3, fontSize: 10, color: H.grey, italic: true });
  }

  // B2. Go-to-Market Strategy
  {
    const s = content("Go-to-Market Strategy – Year 1",
      "Sources: Business Plan deck v1.4 slide 10 (layout and wording); Pitch Deck v1.1 (years 2 to 3). 'SOWs and invoices leveraged to train proprietary AI models' and 'Provide critical data for AI/LLM solutions' are reworded per the architecture decisions (taught, not trained; rows never leave the client).");
    txt(s, "Early Adopters", { x: L, y: 1.45, w: 3.8, h: 0.6, fontSize: 24, bold: true, color: H.blue, valign: "middle" });
    icon(s, "PiRocketLaunch", 4.4, 1.45, 0.6);
    txt(s, "Focus on 4–5 Early Adopters - leveraging executive relationships and delivering rapid ROI", { x: L, y: 2.15, w: 5.6, h: 0.75, fontSize: 15, bold: true, color: H.navy });
    list(s, [
      "[[Rapid value]] – months not years – from Consulting Practice and benchmarking",
      "Significantly [[discounted rate]] (relative to McKinsey/BCG and value created)",
      "[[Form a consortium]] – to share their SOWs and invoices with TWM, but not each other (protecting confidentiality)",
      "[[Provide the documents that build the benchmark]] – rows never leave the client’s environment",
      "[[Generate shorter-term TWM revenue]]",
      "Will not directly be using the system – routed through Consulting team",
    ], { x: L + 0.05, y: 2.95, w: 5.55, h: 2.7, fontSize: 12.5 }, { after: 2 });
    box(s, L, 5.72, 5.6, 0.6, { rounded: true, lineW: 1 });
    txt(s, "**Years 2–3:** enterprise sales with 4–8 week POCs across North American BFSI and Telecom; CIOs first, CPOs second", { x: L + 0.15, y: 5.72, w: 5.3, h: 0.6, fontSize: 12.5, valign: "middle" });
    s.addShape(S.CHEVRON, { x: 6.25, y: 3.2, w: 0.35, h: 1.1, fill: { color: H.navy }, line: { color: H.navy }, objectName: "Arrow" });
    header(s, "Drives Client Value", 6.85, 1.45, 6.03, { size: 18, color: H.navy });
    list(s, [
      "[[Rate card variability/discrepancies]] within portfolio and relative to other Early Adopters",
      "A robust and [[benchmarked, specific Skills Matrix]] for each organization",
      "[[Identification of value leakage]] from non-competitive agreements, inconsistent SOWs, and discrepancies from invoicing vs. SOWs",
      "Recommendations on [[optimizing workforce mix]] - by location, resource type, seniority and skills",
    ], { x: 6.9, y: 2.0, w: 5.95, h: 1.75, fontSize: 12.5 }, { after: 1 });
    header(s, "Builds the Foundation", 6.85, 3.7, 6.03, { size: 18, color: H.navy });
    list(s, [
      "SOWs and invoices [[teach the platform]] – the role framework, mapping table and benchmark grow with every engagement",
      "Robust repository [[becoming the industry benchmark]] for external third-party spend",
      "Creates a [[repeatable playbook]] for other customers",
      "Creates [[success stories]] – with case studies, demos, etc. and momentum for broader adoption",
      "Groundwork for transition from a consulting-led, “white glove” service to a scalable, software-driven solution",
    ], { x: 6.9, y: 4.25, w: 5.95, h: 2.1, fontSize: 12.5 }, { after: 1 });
    banner(s, "Dual approach combining specialized Consulting Practice with AI-powered Platform team", L, 6.42, CW, 0.5, { rounded: true, size: 15 });
  }

  // B3. Preliminary Timelines
  {
    const s = content("Preliminary Timelines",
      "Kyle's decision 2 (Nov 22, 2026): the plan starts today, so every Business Plan milestone moves eight months later (team start April 2026 becomes December 2026). Layout and items from Business Plan deck v1.4 slide 11. FOR KYLE: profitability in Q2 2028 is Claude's proposal from the Business Plan model (decision 3).");
    const cols = [
      ["Dec 2026 – Feb 2027", ["Establish legal entity & brand", "Raise $1MM SAFE", "Recruit core leadership", "Outreach for Early Adopters", "[[Prototype platform: built and running on real contracts]]"]],
      ["Mar 2027", ["[[Launch]]", "Consulting team on the ground with 4 Early Adopters", "Detailed SOW analysis", "Document pipeline in client environments"]],
      ["Q2 – Q3 2027", ["Deliver first consulting recommendations", "Second cohort of Early Adopters (Sep)", "[[Series A]] (H2 2027)", "Benchmark repository expansion"]],
      ["Q4 2027", ["[[Platform v1]] in Early Adopter environments", "Expand AI/ML team", "Customer feedback loop"]],
      ["H1 2028", ["Full-fee clients from March", "[[Profitable from Q2 2028]]", "Case study development", "Begin Phase 2 planning"]],
      ["2028+", ["Phase 2 platform development", "Self-serve platform pilot", "Scale sales & marketing", "50 clients and a $200MM run rate by 2031"]],
    ];
    const gap = 0.15, w = (CW - 5 * gap) / 6;
    cols.forEach((c, i) => {
      const x = L + i * (w + gap);
      box(s, x, 1.45, w, 0.6, { fill: H.hdr, noLine: true });
      txt(s, c[0], { x: x + 0.05, y: 1.45, w: w - 0.1, h: 0.6, fontSize: 13.5, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
      box(s, x, 2.05, w, 2.85, { fill: H.body, noLine: true });
      list(s, c[1], { x: x + 0.1, y: 2.15, w: w - 0.2, h: 2.7, fontSize: 12.5 }, { after: 4 });
    });
    box(s, 0.9, 5.2, 11.53, 1.25, { rounded: true, lineW: 1.5 });
    list(s, [
      "**December 2026** - $1MM SAFE; founding team and first two Engagement Pods start",
      "**March 2027** - On-the-ground with Early Adopters",
      "**H2 2027** - Series A; second cohort of Early Adopters",
      "**Q2 2028** - Profitable as full-fee clients ramp",
    ], { x: 1.15, y: 5.3, w: 11.1, h: 1.1, fontSize: 14 }, { after: 2 });
  }

  // B4. Preliminary Financial Model
  {
    const s = content("Preliminary Financial Model",
      "Source: Business Plan deck v1.4 slide 12 and Business Plan v1.5 (preliminary financial model), all figures CAD $MM. Kyle's decision 2: years counted from the December 2026 start, so the model's 2026 to 2030 become Year 1 to Year 5, Year 1 being the first nine months of operations. Kyle's decision 1 matches the model's 4 Early Adopters at $1.5MM each. FOR KYLE: profitability in Q2 2028 is Claude's proposal (decision 3); the Pitch Deck's 'profitable in 2026' counted only consulting costs.");
    txt(s, "Summary", { x: L, y: 1.4, w: 2.6, h: 0.5, fontSize: 20, bold: true, color: H.blue, valign: "middle" });
    icon(s, "PiChartBar", 3.3, 1.42, 0.5);
    list(s, [
      { t: "[[Profitable in Q2 2028]]", nob: true },
      "Assumes full-fee clients from March 2028, each paying $4.0MM",
      "**Profitability at 5 clients** paying $4.0MM",
      "**Very conservative** cost assumptions",
      { t: "Actual investments dependent on clearer visibility into revenue projections", after: 8 },
      { t: "[[Exit Run Rate (2031)]]", nob: true },
      "Revenue - **$200MM**",
      "Profit (before taxes) - **$100MM+**",
      "Clients - 50",
    ], { x: L + 0.05, y: 2.0, w: 4.0, h: 3.1, fontSize: 13 }, { after: 2 });
    const cols = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Exit Run Rate"];
    const vals = {
      Revenue: [3.0, 23.0, 74.0, 130.0, 180.0, 200.0], Consulting: [3.5, 7.4, 10.2, 18.0, 22.2, 23.9], "Software and AI": [3.2, 8.3, 24.0, 26.5, 26.5, 26.5],
      "Sales and Distribution": [0.6, 2.1, 5.6, 9.8, 13.5, 15.0], "Other - Overhead": [1.5, 3.0, 5.0, 7.0, 10.0, 10.0], "Total Costs": [8.9, 20.7, 44.8, 61.2, 72.2, 75.4],
      "Profit (before taxes)": [-5.9, 2.3, 29.2, 68.8, 107.8, 124.6],
    };
    const money = (v) => (v < 0 ? "-$" : "$") + Math.abs(v).toFixed(1);
    const cell = (t, o) => ({ text: t, options: Object.assign({ align: "right" }, o || {}) });
    const rows = [[{ text: "", options: { fill: { color: "FFFFFF" } } }, ...cols.map((c, i) => cell(c, { bold: true, color: i === 5 ? "FFFFFF" : "000000", fill: { color: i === 5 ? H.navy : "A6A6A6" }, align: "center" }))]];
    const addRow = (label, key, o) => rows.push([{ text: label, options: { bold: !!(o && o.bold) } }, ...vals[key].map((v, i) => cell(money(v), { bold: !!(o && o.bold), color: v < 0 ? H.red : (i === 5 ? H.navy : "000000") }))]);
    addRow("Revenue", "Revenue", { bold: true });
    rows.push([{ text: "Costs", options: { bold: true } }, ...cols.map(() => cell(""))]);
    ["Consulting", "Software and AI", "Sales and Distribution", "Other - Overhead"].forEach((k) => addRow(k, k));
    addRow("Total Costs", "Total Costs", { bold: true });
    addRow("Profit (before taxes)", "Profit (before taxes)", { bold: true });
    rows.push([{ text: "Number of clients", options: { bold: true } }, ...[4, 8, 25, 40, 50, 50].map((n, i) => cell(String(n), { bold: true, color: i === 5 ? H.navy : "000000" }))]);
    s.addTable(rows, { x: 4.75, y: 1.45, w: 8.13, colW: [2.33, 0.95, 0.95, 0.95, 0.95, 0.95, 1.05], fontSize: 12, fontFace: "Aptos", color: "000000", rowH: 0.33,
      margin: [0.03, 0.08, 0.03, 0.08], border: [{ type: "none" }, { type: "none" }, { type: "solid", pt: 0.5, color: "E0E0E0" }, { type: "none" }] });
    txt(s, "CAD $MM. Business Plan model counted from a December 2026 start; Year 1 is the first nine months of operations.", { x: 4.75, y: 4.88, w: 8.13, h: 0.3, fontSize: 10, color: H.grey, italic: true });
    s.addShape(S.LINE, { x: L, y: 5.25, w: CW, h: 0, line: { color: H.rule, width: 1 } });
    const asum = [
      ["Revenue Assumptions", ["4 Early Adopters each pay $1.5MM, contingent on more than $10MM of value", "Full-fee clients pay an average $4.0MM per year from March 2028", "Clients grow from 4 to 50 by 2031"]],
      ["Consulting Practice", ["Avg cost ~$350K per Engagement Manager, ~$250K per Associate", "Each Pod covers ~2 clients, then ~4 once at scale", "Exit: ~$24MM per year"]],
      ["AI/Software and Other", ["Leaders ~$700K, engineers ~$300K: 2 leaders/6 engineers rising to 10/50", "Exit: software ~$26.5MM, sales ~$15MM, overhead ~$10MM per year"]],
    ];
    const aw = (CW - 2 * 0.3) / 3;
    asum.forEach((a, i) => {
      const x = L + i * (aw + 0.3);
      txt(s, a[0], { x, y: 5.33, w: aw, h: 0.35, fontSize: 14, bold: true, italic: true, color: H.blue });
      list(s, a[1], { x: x + 0.02, y: 5.7, w: aw - 0.04, h: 1.2, fontSize: 11.5 }, { after: 1 });
    });
  }

  // B5. The Ask
  {
    const s = content("The Ask: $1MM via a SAFE now, with a Series A in the second half of 2027",
      "Sources: Pitch Deck v1.1 (the ask; traction); Kyle's decision 5 (Nov 22, 2026). The Pitch Deck's line that the $1MM 'will also generate $2-2.5MM in revenue' is left out because the fee is now contingent on value. FOR KYLE: with a contingent fee, Early Adopter cash arrives only once more than $10MM of value is shown, likely months into Value Acceleration; at the Business Plan's cost base $1MM is about five weeks of spending. Check that it bridges the wait.");
    box(s, L, 1.45, 4.6, 4.7, { fill: H.navy, noLine: true });
    txt(s, "$1MM", { x: L + 0.35, y: 1.65, w: 3.9, h: 1.3, fontSize: 72, bold: true, fontFace: "Aptos Display", color: "FFFFFF", valign: "bottom" });
    txt(s, "Pre-seed SAFE", { x: L + 0.35, y: 3.0, w: 3.9, h: 0.5, fontSize: 22, color: H.lblue });
    txt(s, "to launch Value Acceleration with 4-5 Early Adopters", { x: L + 0.35, y: 3.75, w: 3.9, h: 1.2, fontSize: 17, color: "FFFFFF" });
    list(s, [
      "Funds the **founding leadership team** and the build-out of the **first two Engagement Pods** (2 Engagement Managers and 4 Associates)",
      "Funds the **3-to-4-month runway** required to launch Value Acceleration with the Early Adopters",
      "**The prototype already exists** – the money goes into the first engagements, not into proving the idea",
      "**Series A in the second half of 2027** to fund the development of the broader platform",
    ], { x: 5.45, y: 1.55, w: 7.4, h: 4.5, fontSize: 16 }, { after: 12 });
    banner(s, "This $1MM unlocks the foundational data and proves rapid 10-15% cost savings for our consortium", L, 6.35, CW, 0.55, { rounded: true, size: 15 });
  }

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})().catch((e) => { console.error(e); process.exit(1); });
