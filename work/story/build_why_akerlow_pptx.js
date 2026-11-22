// Builds docs/story/why-akerlow.pptx: a one-slide case for the name Akerlow, from the description Kyle approved on Nov 22, 2026.
// Usage: node build_why_akerlow_pptx.js <output.pptx> <path to the pptx skill's scripts/apply_theme.js>
// Needs the npm package "pptxgenjs" on NODE_PATH.
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.argv[3]);
const OUT = process.argv[2] || "why-akerlow.pptx";

const THEME = {
  name: "Akerlow Ledger",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1B1B", lt1: "FFFFFF", dk2: "1E3B33", lt2: "EEF3F0",
    accent1: "C8963E", accent2: "2F6B5A", accent3: "7FA394", accent4: "D9C29A", accent5: "5B6770", accent6: "A44A3F",
    hlink: "2F6B5A", folHlink: "7FA394",
  },
};

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "Why Akerlow";
  pres.author = "Kyle McNamara";
  const C = pres.SchemeColor;

  // One layout: the dark name panel on the left, the title on the right.
  pres.defineSlideMaster({
    title: "NAME_PANEL",
    background: { color: C.background1 },
    objects: [
      { rect: { x: 0, y: 0, w: 4.6, h: 7.5, fill: { color: C.text2 } } },
      { placeholder: { options: { name: "title", type: "title", x: 5.1, y: 0.45, w: 7.6, h: 0.8, fontSize: 36, bold: true, color: C.text2, margin: 0, valign: "middle", align: "left" }, text: "" } },
    ],
  });

  pres.addSection({ title: "Why Akerlow" });
  const s = pres.addSlide({ masterName: "NAME_PANEL", sectionTitle: "Why Akerlow" });
  s.addText("Why Akerlow", { placeholder: "title", align: "left" });

  // Left panel: the name, how to say it, and the idea it carries
  s.addText("Proposed name for the business", { x: 0.6, y: 0.65, w: 3.6, h: 0.4, fontSize: 14, color: C.accent1, margin: 0, isTextBox: true, objectName: "Label" });
  s.addText("Akerlow", { x: 0.6, y: 1.1, w: 3.6, h: 1.0, fontSize: 54, bold: true, fontFace: THEME.headFontFace, color: C.background1, margin: 0, isTextBox: true, objectName: "Name" });
  s.addText("said AK-er-low", { x: 0.6, y: 2.1, w: 3.6, h: 0.4, fontSize: 16, color: C.accent4, margin: 0, isTextBox: true, objectName: "Pronunciation" });
  s.addText("“When one side of a market knows far more than the other, that side sets the price.”", {
    x: 0.6, y: 3.0, w: 3.5, h: 1.25, fontSize: 20, italic: true, fontFace: THEME.headFontFace, color: C.background1, margin: 0, valign: "top", isTextBox: true, objectName: "Idea",
  });
  s.addText("The insight that won George Akerlof the Nobel Prize in economics. The name is a nod to him.", {
    x: 0.6, y: 4.35, w: 3.5, h: 0.75, fontSize: 12, color: C.accent4, margin: 0, valign: "top", isTextBox: true, objectName: "Attribution",
  });
  s.addText("Akerlow is a coined word, not his surname: easy to say, distinctive enough to trademark, and it borrows no one’s name.", {
    x: 0.6, y: 6.05, w: 3.5, h: 0.9, fontSize: 12, color: C.background1, margin: 0, valign: "top", isTextBox: true, objectName: "Coined word",
  });

  // Right side: three numbered rows
  const rows = [
    { y: 1.45, h: 0.95, head: "What the business does",
      body: "It helps large enterprises cut what they spend on third-party technology labour. It reads their contracts, invoices and timesheets, builds one traceable record of every rate they pay, and benchmarks those rates against peers." },
    { y: 3.0, h: 1.4, head: "The gap in technology labour",
      body: "The vendor knows what every client pays for the same role. The client sees one statement of work at a time, and even there the rates are hard to read: every contract defines roles, seniority, rate units and price increases in its own way, inside complex terms and conditions. The vendor has the full picture; the client has fragments." },
    { y: 4.85, h: 1.35, head: "How we close it",
      body: "Every rate the client pays sits in one ledger, traceable to the page of the contract it came from. Benchmarks show what the same role costs elsewhere, like a price guide. And a consortium pools benchmarks that no single company could build alone, without any client’s contracts leaving its own walls." },
  ];
  rows.forEach((r, i) => {
    s.addShape(pres.shapes.OVAL, { x: 5.1, y: r.y, w: 0.5, h: 0.5, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `Number ${i + 1}` });
    s.addText(String(i + 1), { x: 5.1, y: r.y, w: 0.5, h: 0.5, fontSize: 18, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `Number ${i + 1} text` });
    s.addText(r.head, { x: 5.85, y: r.y - 0.02, w: 6.85, h: 0.42, fontSize: 18, bold: true, color: C.text2, margin: 0, valign: "middle", isTextBox: true, objectName: `Heading ${i + 1}` });
    s.addText(r.body, { x: 5.85, y: r.y + 0.42, w: 6.85, h: r.h, fontSize: 14, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 0, isTextBox: true, objectName: `Body ${i + 1}` });
  });

  s.addNotes("Built from the Akerlow description Kyle approved on November 22, 2026 (docs/story/naming.md). The deck itself uses TWM; this slide makes the case for the proposed name.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
