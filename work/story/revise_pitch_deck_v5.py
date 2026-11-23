"""Pitch deck v5: revenue corrected (Kyle, Nov 22, 2026): only 4 Early Adopters, their $6MM earned in Year 1, and the
two clients that were a second cohort pay the full fee from September 2027. Built on v4 (Kyle's v3 plus the redone
financial page). Figures from docs/story/twm-business-model-2026-11-22.xlsx, recalculated in Excel.
Usage: python revise_pitch_deck_v5.py <v4> <output v5> <workbook>
"""
import re
import sys
from decimal import ROUND_HALF_UP, Decimal

import openpyxl
from pptx import Presentation
from pptx.oxml.ns import qn

SRC, OUT, WB = sys.argv[1], sys.argv[2], sys.argv[3]


def set_runs(p, markup):
    first = p.runs[0].font if p.runs else None
    size, name = (first.size, first.name) if first else (None, None)
    color = first.color.rgb if first is not None and first.color and first.color.type is not None else None
    for r in p._p.findall(qn("a:r")) + p._p.findall(qn("a:br")):
        p._p.remove(r)
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", markup)):
        if part:
            r = p.add_run()
            r.text = part
            r.font.bold = i % 2 == 1
            if size:
                r.font.size = size
            if name:
                r.font.name = name
            if color is not None:
                r.font.color.rgb = color


def replace_in_runs(slide, old, new):
    """Replace text inside one run, keeping that run's formatting."""
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if old in r.text:
                    r.text = r.text.replace(old, new)
                    return
    raise KeyError(f"{old!r} not found in a single run")


def money(v):
    d = Decimal(str(v)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"-${-d}" if d < 0 else f"${d}"


fin = openpyxl.load_workbook(WB, data_only=True)["Financials"]
COLS = (6, 11, 16, 21, 26, 27)
ROWS = {"Revenue": 4, "Consulting": 7, "Software and AI": 8, "Sales and Distribution": 9, "Other - Overhead": 10,
        "Total Costs": 11, "Profit (before taxes)": 13, "Number of clients": 15}
values = {k: ([str(int(fin.cell(row=r, column=c).value)) for c in COLS] if k == "Number of clients"
              else [money(fin.cell(row=r, column=c).value) for c in COLS]) for k, r in ROWS.items()}
for k, v in values.items():
    print(f"  {k:24} {' | '.join(v)}")

prs = Presentation(SRC)


def slide_titled(start):
    return next(sl for sl in prs.slides if any(sh.has_text_frame and sh.text_frame.text.strip().startswith(start) for sh in sl.placeholders))


# executive summary, go-to-market, the ask: four Early Adopters, not four to five
replace_in_runs(slide_titled("Executive Summary"), "4-5 leading organizations", "4 leading organizations")
replace_in_runs(slide_titled("Go-to-Market"), "4–5 Early Adopters", "4 Early Adopters")
replace_in_runs(slide_titled("The Ask"), "4-5 Early Adopters", "4 Early Adopters")

# timelines: no second cohort; the first two full-fee clients start in September 2027
tl = slide_titled("Preliminary Timelines")
replace_in_runs(tl, "Second cohort of Early Adopters (Sep)", "First two full-fee clients (Sep)")
replace_in_runs(tl, "Full-fee clients from March", "Early Adopters on the full fee from March")
replace_in_runs(tl, "second cohort of Early Adopters", "first two full-fee clients")

# financial page
s = slide_titled("Preliminary Financial Model")
table = next(sh for sh in s.shapes if sh.has_table).table
for row in table.rows:
    label = row.cells[0].text.strip()
    if label in values:
        for cell, text in zip(list(row.cells)[1:], values[label]):
            p = cell.text_frame.paragraphs[0]
            p.runs[0].text = text
            for r in p.runs[1:]:
                p._p.remove(r._r)


def para(shape_text, starts):
    sh = next(x for x in s.shapes if x.has_text_frame and shape_text in x.text_frame.text)
    return next(p for p in sh.text_frame.paragraphs if "".join(r.text for r in p.runs).startswith(starts))


set_runs(para("Profitable in Q2 2028", "Assumes full-fee"), "Assumes 2 full-fee clients from September 2027 and 8 from March 2028, each paying $4.0MM")
set_runs(para("contingent on more than $10MM", "6 Early Adopters"), "4 Early Adopters each pay $1.5MM over ~6 months of Value Acceleration, contingent on more than $10MM of value")
set_runs(para("contingent on more than $10MM", "Full-fee clients"), "Full-fee clients pay $4.0MM per year: 2 from September 2027, 8 from March 2028")

s.notes_slide.notes_text_frame.text = (
    "Source: docs/story/twm-business-model-2026-11-22.xlsx, Kyle's Business Model workbook (October 2025) with his Nov 22, 2026 decisions. "
    "Revenue: only 4 Early Adopters, each paying $1.5MM over the ~6 months of Value Acceleration (March to August 2027), so all $6MM is in Year 1; "
    "the two clients that were a second cohort pay the full $4MM a year from September 2027; 8 full-fee clients from March 2028 (the 4 Early "
    "Adopters, those 2 and 2 new); then 12 from September 2028, 25 from March 2029, 40 from March 2030, 50 from March 2031. A client pays the full "
    "fee from its first quarter. Costs: Engagement Manager $225K, Associate $100K, software leaders $500K, engineers $200K. All figures CAD $MM; "
    "years counted from the December 2026 start (Year 1 is December 2026 to August 2027; later years run September to August). Cash needed before "
    "TWM pays for itself: about $5.3MM, deepest at the end of February 2028. FOR KYLE: the 4 Early Adopters pay nothing from September 2027 to "
    "February 2028 unless they move to the full fee when Value Acceleration ends. Review: docs/story/financial-model-review.md.")

ask = slide_titled("The Ask")
ask.notes_slide.notes_text_frame.text = (
    "Sources: Pitch Deck v1.1 (the ask; traction); Kyle's decision 5 (Nov 22, 2026). The Pitch Deck's line that the $1MM 'will also generate "
    "$2-2.5MM in revenue' is left out because the fee is now contingent on value. FOR KYLE: at the Nov 22 assumptions the first quarter "
    "(December 2026 to February 2027) costs about $1.9MM, so $1MM is about seven weeks of the full plan, or about four months of the two pods and "
    "consulting leadership alone. The Early Adopter fees ($6MM, March to August 2027) arrive only once more than $10MM of value is shown. The model "
    "needs about $5.3MM before it pays for itself (funding is topic 7 of the model review).")

prs.save(OUT)
print("saved", OUT)
