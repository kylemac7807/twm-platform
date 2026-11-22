"""Revise Kyle's second round of edits (his saved v2, Nov 22, 2026) into twm-pitch-deck-v3.pptx, keeping his edits.

Kyle's feedback applied (his slide numbers):
  slide 2   the TWM sentence becomes a navy header banner across the slide, out of the "Why" column
  slide 9   the one callout he kept spans the slide, so the page is balanced
  slide 10  invoices and timesheets dropped: none in the library can be matched to a contract set with a rate table
  11, 12    platform phases and organization structure move into the investor section
  slide 16  team slide rebalanced after his content changes
  slide 18  investor divider subtitle follows the new order
Usage: python revise_pitch_deck_v3.py <kyle's saved deck> <output deck>   (needs python-pptx)
"""
import re
import sys
from copy import deepcopy

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

SRC, OUT = sys.argv[1], sys.argv[2]
BLUE, BLACK, WHITE = (RGBColor.from_string(c) for c in ("0070C0", "000000", "FFFFFF"))
P14 = "{http://schemas.microsoft.com/office/powerpoint/2010/main}"

prs = Presentation(SRC)
slides = list(prs.slides)
S = lambda n: slides[n - 1]  # Kyle's numbering, before any move


# ---------------------------------------------------------------- helpers (as in revise_pitch_deck_v2.py)
def shape_with(slide, text):
    for sh in slide.shapes:
        if sh.has_text_frame and text in sh.text_frame.text:
            return sh
    raise KeyError(f"no shape with {text!r}")


def shape_id(slide, sid):
    for sh in slide.shapes:
        if sh.shape_id == sid:
            return sh
    raise KeyError(f"no shape id {sid}")


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


def drop_para(p):
    p._p.getparent().remove(p._p)


def place(sh, x=None, y=None, w=None, h=None):
    if x is not None:
        sh.left = Inches(x)
    if y is not None:
        sh.top = Inches(y)
    if w is not None:
        sh.width = Inches(w)
    if h is not None:
        sh.height = Inches(h)


def add_notes(slide, text):
    tf = slide.notes_slide.notes_text_frame
    tf.text = (tf.text + "\n\n" + text) if tf.text.strip() else text


# ---------------------------------------------------------------- slide 2: the TWM sentence as a header banner
s2 = S(2)
why = shape_with(s2, "Targeting inefficiencies")
drop_para(para_with(why, "Technology Workforce Management (TWM) enables"))
s5 = S(5)
banner_src, banner_txt_src = shape_id(s5, 4), shape_id(s5, 5)  # the navy quote banner and its text, house style
banner, banner_txt = deepcopy(banner_src._element), deepcopy(banner_txt_src._element)
tree = s2.shapes._spTree
next_id = max(sh.shape_id for sh in s2.shapes) + 1
for el in (banner, banner_txt):  # unique shape ids on this slide
    el.find(".//" + qn("p:cNvPr")).set("id", str(next_id))
    next_id += 1
    tree.append(el)
b, bt = s2.shapes[-2], s2.shapes[-1]
place(b, 0.45, 1.3, 12.43, 0.8)
place(bt, 0.65, 1.3, 12.03, 0.8)
bt.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
p = bt.text_frame.paragraphs[0]
for extra in bt.text_frame.paragraphs[1:]:
    drop_para(extra)
set_runs(p, "**Technology Workforce Management (TWM) enables large organizations to cut their third-party technology labor spend and restructure their workforce for the future**", Pt(16), WHITE)
p.alignment = PP_ALIGN.CENTER
for sid, y in ((4, 2.3), (7, 2.3), (5, 2.76), (8, 2.76)):  # column headers and their rules
    place(shape_id(s2, sid), y=y)
for sid in (6, 9):  # the two columns
    place(shape_id(s2, sid), y=2.85, h=4.05)

# ---------------------------------------------------------------- slide 9: the one callout Kyle kept spans the slide
s9 = S(9)
box9, txt9 = shape_id(s9, 27), shape_id(s9, 28)
place(box9, 0.45, 5.0, 12.43, 0.8)
place(txt9, 0.7, 5.0, 11.93, 0.8)
txt9.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
paras = txt9.text_frame.paragraphs
body = "".join(r.text for r in paras[1].runs).strip()
set_runs(paras[0], f"[[Precision first:]] {body}", Pt(14))
paras[0].alignment = PP_ALIGN.CENTER
drop_para(paras[1])

# ---------------------------------------------------------------- slide 10: no orphaned invoices or timesheets
s10 = S(10)
lib = shape_with(s10, "Canadian federal")
set_runs(para_with(lib, "228 contract"), "**228 contract “sets”** – contracts, amendments, SOWs and rate cards")
set_runs(para_with(lib, "Canadian federal"), "**Canadian federal** packages")
drop_para(para_with(lib, "Invoices"))
add_notes(s10, "Invoices and timesheets left off (Kyle, Nov 22: only worth showing if they can be matched to a contract set with a rate table). "
          "Checked Nov 22: every invoice and timesheet in the library comes from one group of 27 documents (corpus/manifests/v3_invoices); "
          "none of their vendor-client pairs (CorTech and Corix, HTI, the FTX fee applications, Tyler and Fort Bend, the board payment lists) "
          "appears in any contract, SOW or rate card in the library, so none can be checked against a contracted rate. "
          "The CorTech invoice and timesheet match each other (hours times rate), but there is no contract behind them, and the work is utility staffing, not technology labor.")

# ---------------------------------------------------------------- slide 16: team slide rebalanced
s16 = S(16)
empty = [sh for sh in s16.shapes if sh.has_text_frame and not sh.text_frame.text.strip() and not sh.is_placeholder
         and sh.shape_type == 17]
for sh in empty:  # the text box left behind when Kyle removed a box
    sh._element.getparent().remove(sh._element)
BOTTOM = 6.2
place(shape_id(s16, 6), h=BOTTOM - 1.95)       # Consortium Member body
place(shape_id(s16, 7), h=BOTTOM - 1.95 - 0.15)
place(shape_id(s16, 10), h=BOTTOM - 1.95)      # TWM Team body
place(shape_id(s16, 11), 4.75, 2.1, 7.98, 1.4)   # TWM Leadership, across the top
place(shape_id(s16, 12), 4.85, 2.17, 7.78, 1.28)
lower_y, lower_h = 3.65, BOTTOM - 0.15 - 3.65
place(shape_id(s16, 15), 4.75, lower_y, 3.92, lower_h)   # Engagement Pods
place(shape_id(s16, 16), 4.85, lower_y + 0.07, 3.72, lower_h - 0.12)
place(shape_id(s16, 17), 8.81, lower_y, 3.92, lower_h)   # "Pod" for each member
place(shape_id(s16, 18), 8.91, lower_y + 0.07, 3.72, lower_h - 0.12)

# ---------------------------------------------------------------- slide 18: divider subtitle follows the new order
sub = shape_with(S(18), "Market, go-to-market").text_frame.paragraphs[0]
sub.runs[0].text = "Market, platform, go-to-market, organization, timelines and financial model"  # keeps the divider's formatting
for r in sub.runs[1:]:
    sub._p.remove(r._r)


# ---------------------------------------------------------------- move slides 11 and 12 into the investor section
def sld_id_of(slide):
    for sld in prs.slides._sldIdLst:
        if prs.part.related_part(sld.rId) is slide.part:
            return sld
    raise KeyError


lst = prs.slides._sldIdLst
platform, org = sld_id_of(S(11)), sld_id_of(S(12))
market, gtm = sld_id_of(S(19)), sld_id_of(S(20))
lst.remove(platform)
lst.remove(org)
market.addnext(platform)   # Market, Platform, Go-to-Market
gtm.addnext(org)           # Go-to-Market, Organization, Timelines ...
order = [el.get("id") for el in lst]
moved = {platform.get("id"), org.get("id")}
for sec in prs.part._element.iter(P14 + "section"):
    ids = sec.find(P14 + "sldIdLst")
    for el in list(ids):
        if el.get("id") in moved:
            ids.remove(el)
    if sec.get("name") == "Investor Overview":
        for el in list(ids):
            ids.remove(el)
        start = order.index(market.get("id")) - 1  # the divider
        for sid in order[start:]:
            new = ids.makeelement(P14 + "sldId", {})
            new.set("id", sid)
            ids.append(new)

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
