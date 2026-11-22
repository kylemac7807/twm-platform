"""Revise Kyle's edited pitch deck (his saved file, Nov 22, 2026) into twm-pitch-deck-v2.pptx, keeping his edits.

Kyle's feedback applied:
  slide 2   reword the Master Benchmark Ledger benefit (less cryptic)
  slide 5   finish the "fragments" thought; right-size the bottom box
  slide 7   Competitive Analysis dropped (refresh goes to the backlog)
  10-12     consolidated into one slide: the prototype runs each step
  13-15     consolidated into one progress slide, from Kyle's trimmed versions
  slide 24  self-citation of the Pitch Deck removed (data refresh goes to the backlog)
  slide 25  Go-to-Market condensed
Usage: python revise_pitch_deck_v2.py <kyle's saved deck> <output deck>   (needs python-pptx)
"""
import re
import sys
from copy import deepcopy

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

SRC, OUT = sys.argv[1], sys.argv[2]
NAVY, BLUE, GREY, LGREY, BLACK, WHITE = (RGBColor.from_string(c) for c in ("0E2841", "0070C0", "7F7F7F", "F2F2F2", "000000", "FFFFFF"))
P14 = "{http://schemas.microsoft.com/office/powerpoint/2010/main}"

prs = Presentation(SRC)
slides = list(prs.slides)
S = lambda n: slides[n - 1]  # Kyle's numbering, before any deletion


# ---------------------------------------------------------------- helpers
def shape_with(slide, text):
    for sh in slide.shapes:
        if sh.has_text_frame and text in sh.text_frame.text:
            return sh
    raise KeyError(f"no shape with {text!r}")


def para_with(shape, text):
    for p in shape.text_frame.paragraphs:
        if text in "".join(r.text for r in p.runs):
            return p
    raise KeyError(f"no paragraph with {text!r}")


def segments(markup):
    """**bold**, __bold italic__, [[blue bold]] -> [(text, style)]"""
    out, last = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*|__(.+?)__|\[\[(.+?)\]\]", markup):
        if m.start() > last:
            out.append((markup[last:m.start()], "n"))
        out.append((m.group(1), "b") if m.group(1) else (m.group(2), "bi") if m.group(2) else (m.group(3), "blue"))
        last = m.end()
    if last < len(markup):
        out.append((markup[last:], "n"))
    return out


def set_runs(p, markup, size=None, color=None):
    runs = p.runs
    tsize = size if size else (runs[0].font.size if runs else None)
    for r in p._p.findall(qn("a:r")) + p._p.findall(qn("a:br")):
        p._p.remove(r)
    for text, style in segments(markup):
        r = p.add_run()
        r.text = text
        f = r.font
        f.name = "Aptos"
        if tsize:
            f.size = tsize
        f.bold = style in ("b", "bi", "blue")
        f.italic = style == "bi"
        f.color.rgb = BLUE if style == "blue" else (color or BLACK)


def rewrite_list(shape, items, size=None, color=None):
    """Reuse the shape's paragraphs (keeping their bullets) for the new items; drop the rest."""
    paras = shape.text_frame.paragraphs
    assert len(paras) >= len(items), "not enough paragraphs to reuse"
    for p, item in zip(paras, items):
        set_runs(p, item, size, color)
    for p in paras[len(items):]:
        p._p.getparent().remove(p._p)


def bulletize(p, indent_in=0.18):
    pPr = p._p.get_or_add_pPr()
    emu = str(int(Inches(indent_in)))
    pPr.set("marL", emu)
    pPr.set("indent", "-" + emu)
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum", "a:buFont"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
    etree.SubElement(pPr, qn("a:buChar")).set("char", "•")


def textbox(slide, x, y, w, h, items, size=13, color=None, align=None, anchor=MSO_ANCHOR.TOP, after=4):
    """items: list of markup strings; a leading '- ' makes a bullet."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        bullet = item.startswith("- ")
        text = item[2:] if bullet else item
        p.space_after = Pt(after)
        if align:
            p.alignment = align
        set_runs(p, text, Pt(size), color)
        if bullet:
            bulletize(p)
    return tb


def header(slide, text, x, y, w, size=16):
    textbox(slide, x, y, w, 0.42, [f"[[{text}]]"], size=size, anchor=MSO_ANCHOR.BOTTOM, after=0)
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y + 0.46), Inches(x + w), Inches(y + 0.46))
    ln.line.color.rgb = BLUE
    ln.line.width = Pt(1)


def outline_box(slide, x, y, w, h, fill=None, line=NAVY, width=1.5, rounded=True):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if rounded:
        shp.adjustments[0] = 0.08
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    else:
        shp.fill.background()
    shp.line.color.rgb = line
    shp.line.width = Pt(width)
    shp.shadow.inherit = False
    shp.text_frame.text = ""
    return shp


def set_title(slide, text):
    """Replace the title text, keeping the first run's formatting (the title is a body placeholder in these masters)."""
    ph = min((sh for sh in slide.placeholders if sh.has_text_frame), key=lambda sh: sh.top)
    p = ph.text_frame.paragraphs[0]
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        p._p.remove(r._r)
    for extra in ph.text_frame.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def clear_body(slide):
    for sh in list(slide.shapes):
        if not sh.is_placeholder:
            sh._element.getparent().remove(sh._element)


def near(v, inches, tol=0.06):
    return abs(Emu(v).inches - inches) < tol


def delete_slide(slide):
    lst = prs.slides._sldIdLst
    for sld in list(lst):
        if prs.part.related_part(sld.rId) is slide.part:
            sid = sld.get("id")
            prs.part.drop_rel(sld.rId)
            lst.remove(sld)
            for el in list(prs.part._element.iter(P14 + "sldId")):
                if el.get("id") == sid:
                    el.getparent().remove(el)
            return
    raise KeyError("slide not found")


# ---------------------------------------------------------------- slide 2: the ledger benefit, in plain words
p = para_with(shape_with(S(2), "An auditable Master Benchmark Ledger"), "An auditable Master Benchmark Ledger")
set_runs(p, "__One auditable record of every rate:__ each rate you pay is linked to the exact contract page it came from – so every saving can be proven to the vendor")

# ---------------------------------------------------------------- slide 5: finish the thought; right-size the bottom box
set_runs(para_with(shape_with(S(5), "The full picture"), "The full picture"), "**The full picture** – it can compare every client against the others")
set_runs(para_with(shape_with(S(5), "Fragments"), "Fragments"), "**Only fragments** – nothing to compare a rate against")
closing = shape_with(S(5), "TWM closes the gap")
for sh in S(5).shapes:
    if sh.shape_type == 1 and near(sh.top, 5.5) and sh.width > Inches(10):  # the rounded box behind the closing line
        sh.top, sh.height = Inches(5.55), Inches(0.8)
closing.top, closing.height = Inches(5.55), Inches(0.8)
set_runs(closing.text_frame.paragraphs[0], "**TWM closes the gap:** one traceable record of every rate, benchmarked against peers", Pt(17))

# ---------------------------------------------------------------- slides 10-12: one slide, the prototype runs each step
s10 = S(10)
set_title(s10, "We have built a working prototype that runs each step on real contracts")
captions = {
    "Texas contract DIR-STS": "436 public documents in 228 contract sets",
    "Seven files recognized": "Sorts files into contract sets – seven Texas files as one",
    "111-row rate table": "Reads text and tables, with every cell’s position",
    "checked against the page": "Pulls each rate as written, then checks it against the page",
    "resolved once": "Maps vendor titles to TWM’s role framework – or asks",
    "Stored with page 8": "Stores each rate with its page and position",
}
for key, text in captions.items():
    set_runs(shape_with(s10, key).text_frame.paragraphs[0], text)
set_runs(shape_with(s10, "Page 8 of Attachment 2.1").text_frame.paragraphs[0],
         "A real State of Texas contract with Accenture – page 8 of its pricing attachment. The red box is drawn from the position the ledger stores.")
banner_text = shape_with(s10, "becomes Systems Engineer")
for sh in s10.shapes:
    if sh.shape_type == 1 and near(sh.top, 5.45) and near(sh.height, 1.05):
        sh.top, sh.height = Inches(6.22), Inches(0.62)
banner_text.top, banner_text.height = Inches(6.22), Inches(0.62)
set_runs(banner_text.text_frame.paragraphs[0], "“Advanced Systems Engineer, $83.00 per hour” becomes Systems Engineer, senior – stored with page 8 and its position. Nothing in the ledger is an estimate.", Pt(14), WHITE)
callouts = [
    ("Precision first", "When it is not sure, it asks – and every answer becomes a rule, so no question is asked twice"),
    ("In-tenant by design", "Built to run inside each client’s own Azure environment; documents and rates never leave"),
    ("Own vs. rent", "We rent the AI models; we own the role framework, the checks and the consortium benchmark"),
]
cw = (12.43 - 2 * 0.3) / 3
for i, (head, body) in enumerate(callouts):
    x = 0.45 + i * (cw + 0.3)
    outline_box(s10, x, 4.85, cw, 1.2)
    textbox(s10, x + 0.25, 4.93, cw - 0.5, 1.05, [f"[[{head}]]", body], size=13, after=3)
notes(s10, "Consolidates the earlier follow-one-rate, precision-first and technical-approach slides (Kyle, Nov 22). Sources: docs/story/follow-one-rate.html (pipeline run of Oct 6, 2026); docs/library-summary.md (436 documents, 228 contract sets); architecture decisions 1, 3, 5 and 6. The prototype runs locally today; the Azure installation is the next step, hence 'built to run'.")

# ---------------------------------------------------------------- slides 13-15: one progress slide, from Kyle's trimmed versions
s13 = S(13)
clear_body(s13)
set_title(s13, "Progress to date: a document library, TWM’s own role framework and a working pipeline")
cw = (12.43 - 2 * 0.3) / 3
xs = [0.45 + i * (cw + 0.3) for i in range(3)]
header(s13, "Document library", xs[0], 1.45, cw)
textbox(s13, xs[0], 2.05, cw, 3.7, [
    "- **436 public documents in 228 contract sets** – contracts, amendments, SOWs, rate cards, invoices and timesheets",
    "- **About 240** contracts US public companies filed with the securities regulator",
    "- **Examples – 5 Texas and 13 Michigan** contract sets with rates visible (i.e. a **$109M, 13-year Deloitte** contract)",
    "- **48** signed UK government contracts and **13** major vendors’ UK rate cards (about 2,600 priced rows)",
    "- **Canadian federal** packages; **invoices and timesheets**",
], size=13, after=6)
outline_box(s13, xs[0], 5.95, cw, 0.9)
textbox(s13, xs[0] + 0.15, 5.95, cw - 0.3, 0.9, ["**Preliminary models built with public data before securing access to client information**"], size=12.5, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
header(s13, "TWM Role Framework", xs[1], 1.45, cw)
textbox(s13, xs[1], 2.05, cw, 1.9, [
    "- **129 roles** in **18 families**, with **4 seniority bands** (junior, intermediate, senior, lead/principal)",
    "- Built from open public sources: **US O*NET, UK government job ladders and Canada’s TBIPS categories**",
    "- **547 vendor titles** mapped, each with its reasoning, who decided, and a version",
], size=13, after=6)
textbox(s13, xs[1], 4.0, cw, 0.35, ["**Tested on 113 titles it had never seen**"], size=13, color=NAVY, align=PP_ALIGN.CENTER)
cd = CategoryChartData()
cd.categories = ["By the rules alone", "After one review pass"]
cd.add_series("Placed", (40.7, 95.6))
gf = s13.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(xs[1]), Inches(4.35), Inches(cw), Inches(1.85), cd)
ch = gf.chart
ch.has_legend = False
ch.has_title = False
ch.font.size, ch.font.name = Pt(11), "Aptos"
plot = ch.plots[0]
plot.gap_width = 80
plot.has_data_labels = True
plot.data_labels.number_format, plot.data_labels.number_format_is_linked = '0.0"%"', False
plot.data_labels.font.size, plot.data_labels.font.bold = Pt(13), True
ser = plot.series[0]
ser.format.fill.solid()
ser.format.fill.fore_color.rgb = NAVY
va = ch.value_axis
va.maximum_scale, va.minimum_scale = 115, 0
va.has_major_gridlines = False
va.visible = False
textbox(s13, xs[1], 6.25, cw, 0.6, ["**Learns from analyst decisions, not from retraining a model**"], size=12.5, color=NAVY, align=PP_ALIGN.CENTER)
header(s13, "Working pipeline", xs[2], 1.45, cw)
textbox(s13, xs[2], 2.05, cw, 2.6, [
    "- **1,034 contract terms** read – escalation, discounts, expenses – each quote proven word for word on its page",
    "- **Analyst workbench prototyped** – the review queue; click any rate through to its page; every answer recorded with who and why",
    "- **166 automated tests**, each listed as a plain-English promise",
], size=13, after=6)
outline_box(s13, xs[2], 5.2, cw, 1.65, fill=LGREY, line=GREY, width=0.75, rounded=False)
textbox(s13, xs[2] + 0.2, 5.3, cw - 0.4, 1.5, [
    "**Next**",
    "- The whole library through the pipeline",
    "- Accuracy measured against hand-checked answer sheets",
    "- Benchmarking, findings and savings",
], size=13, color=BLACK, after=3)
notes(s13, "Consolidates the three progress slides, using Kyle's trimmed versions (Nov 22). Sources: docs/library-summary.md (436 documents, 228 contract sets; the counts Kyle approved Nov 22); taxonomy/REPORT.md and taxonomy/HELDOUT.md; work/contract-terms/review.md; test suite (166 tests).")

# ---------------------------------------------------------------- slide 24: no self-citation
src = shape_with(S(24), "Source: Pitch Deck")
src._element.getparent().remove(src._element)
notes(S(24), "Every data point on this slide (IT services market size and growth, provider headcounts, the serviceable and obtainable market counts) is to be refreshed from external sources before the deck is shown (backlog item, Nov 22). Kyle's decision 4: organizations with $100MM+ in third-party technology labor spend.")

# ---------------------------------------------------------------- slide 25: Go-to-Market, condensed
s25 = S(25)
rewrite_list(shape_with(s25, "Rapid value"), [
    "[[Rapid value]] – months, not years",
    "[[Discounted rate]] relative to McKinsey/BCG and the value created",
    "[[Consortium]] – members share SOWs and invoices with TWM, not with each other",
    "[[Shorter-term revenue]] for TWM; members are served through the Consulting team",
], size=Pt(14))
set_runs(shape_with(s25, "Years 2").text_frame.paragraphs[0], "**Years 2–3:** enterprise sales and 4–8 week pilots; CIOs first, CPOs second", Pt(13))
rewrite_list(shape_with(s25, "Rate card variability"), [
    "[[Rate card variability]] across the portfolio and against peers",
    "A [[benchmarked Skills Matrix]] for each organization",
    "[[Value leakage]] identified and the [[workforce mix]] optimized",
], size=Pt(14))
foundation = shape_with(s25, "teach the platform")
rewrite_list(foundation, [
    "Every engagement [[grows the benchmark]] and the role framework",
    "A [[repeatable playbook]] and [[success stories]] for the next clients",
    "The path from consulting-led to [[software-driven]]",
], size=Pt(14))
for sh in s25.shapes:
    if near(sh.top, 2.0) and near(sh.left, 6.9):
        sh.height = Inches(1.3)
    elif near(sh.top, 3.7) and near(sh.left, 6.85):
        sh.top = Inches(3.5)
    elif near(sh.top, 4.16) and near(sh.left, 6.85):
        sh.top = Inches(3.96)
foundation.top, foundation.height = Inches(4.05), Inches(1.5)
notes(s25, "Condensed from the Business Plan deck v1.4 slide 10 at Kyle's request (Nov 22). Pitch Deck v1.1 for years 2 to 3.")

# ---------------------------------------------------------------- deletions (Kyle's numbering)
for n in (7, 11, 12, 14, 15):
    delete_slide(S(n))

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
