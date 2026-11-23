"""Pitch deck v4: the financial model page redone with Kyle's Nov 22, 2026 assumptions, on his latest saved v3.

Figures come from docs/story/twm-business-model-2026-11-22.xlsx (recalculated in Excel), rounded half up to one decimal.
Usage: python revise_pitch_deck_v4.py <Kyle's saved v3> <output v4> <updated workbook>
"""
import sys
from decimal import ROUND_HALF_UP, Decimal

import re

import openpyxl
from pptx import Presentation
from pptx.oxml.ns import qn


def set_runs(p, markup):
    """Replace a paragraph's text, keeping the first run's font; **bold** marks bold spans."""
    first = p.runs[0].font if p.runs else None
    size, name = (first.size, first.name) if first else (None, None)
    color = first.color.rgb if first is not None and first.color and first.color.type is not None else None
    for r in p._p.findall(qn("a:r")) + p._p.findall(qn("a:br")):
        p._p.remove(r)
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", markup)):
        if not part:
            continue
        r = p.add_run()
        r.text = part
        r.font.bold = i % 2 == 1
        if size:
            r.font.size = size
        if name:
            r.font.name = name
        if color is not None:
            r.font.color.rgb = color

SRC, OUT, WB = sys.argv[1], sys.argv[2], sys.argv[3]

# ---------------------------------------------------------------- figures from the recalculated workbook
fin = openpyxl.load_workbook(WB, data_only=True)["Financials"]
COLS = (6, 11, 16, 21, 26, 27)  # Total 2026 .. Total 2030, exit run rate -> Year 1..5, exit
ROWS = {"Revenue": 4, "Consulting": 7, "Software and AI": 8, "Sales and Distribution": 9, "Other - Overhead": 10,
        "Total Costs": 11, "Profit (before taxes)": 13, "Number of clients": 15}


def money(v):
    d = Decimal(str(v)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"-${-d}" if d < 0 else f"${d}"


values = {}
for label, r in ROWS.items():
    vals = [fin.cell(row=r, column=c).value for c in COLS]
    values[label] = [str(int(v)) for v in vals] if label == "Number of clients" else [money(v) for v in vals]
for k, v in values.items():
    print(f"  {k:24} {' | '.join(v)}")

prs = Presentation(SRC)
s = next(sl for sl in prs.slides if any(sh.has_text_frame and sh.text_frame.text.strip() == "Preliminary Financial Model" for sh in sl.placeholders))


def shape_with(text):
    return next(sh for sh in s.shapes if sh.has_text_frame and text in sh.text_frame.text)


def set_cell(cell, text):
    p = cell.text_frame.paragraphs[0]
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        p._p.remove(r._r)


table = next(sh for sh in s.shapes if sh.has_table).table
for row in table.rows:
    label = row.cells[0].text.strip()
    if label in values:
        for cell, text in zip(list(row.cells)[1:], values[label]):
            set_cell(cell, text)

# summary column (Kyle's wording kept; the numbers follow the model)
summary = shape_with("Profitable in Q2 2028").text_frame.paragraphs
for p in summary:
    t = "".join(r.text for r in p.runs)
    if t.startswith("Profitability at 5 clients"):
        set_runs(p, "**Profitability at 4 clients** paying $4.0MM")
    elif t.startswith("Profit (before taxes)"):
        set_runs(p, "Profit (before taxes) - **$140MM+**")

note = shape_with("CAD $MM.")
set_runs(note.text_frame.paragraphs[0], "CAD $MM, Nov 22, 2026 assumptions. Year 1 is the first nine months from a December 2026 start. Totals may not add (rounding).")

rev = shape_with("Early Adopters each pay").text_frame.paragraphs
set_runs(rev[0], "6 Early Adopters (4, then a second cohort of 2) each pay $1.5MM, contingent on more than $10MM of value")
cons = shape_with("per Engagement Manager").text_frame.paragraphs
set_runs(cons[0], "Avg cost ~$225K per Engagement Manager, ~$100K per Associate")
set_runs(cons[2], "Exit: ~$15MM per year")
sw = shape_with("engineers").text_frame.paragraphs
set_runs(sw[0], "Leaders ~$500K, engineers ~$200K: 2 leaders/6 engineers rising to 10/50")
set_runs(sw[1], "Exit: software ~$19MM, sales ~$15MM, overhead ~$10MM per year")

s.notes_slide.notes_text_frame.text = (
    "Source: docs/story/twm-business-model-2026-11-22.xlsx, Kyle's Business Model workbook (October 2025) with his Nov 22, 2026 "
    "assumptions: every Early Adopter pays $1.5MM (the second cohort was $2MM); Engagement Manager $225K and Associate $100K "
    "(were $350K and $250K); software leaders $500K and engineers $200K (were $750K in the workbook, $700K in the Business Plan, and $300K). "
    "Unchanged: the $4MM full fee, the client ramp, leadership and overhead amounts. All figures CAD $MM. Years counted from the December 2026 start "
    "(the workbook's 2026 to 2030 are Year 1 to Year 5). Cash needed before TWM pays for itself, at these costs: about $6.3MM, deepest at the end of "
    "February 2028. Profitable every quarter from the quarter starting March 2028. Review: docs/story/financial-model-review.md.")

ask = next(sl for sl in prs.slides if any(sh.has_text_frame and sh.text_frame.text.startswith("The Ask") for sh in sl.placeholders))
ask.notes_slide.notes_text_frame.text = (
    "Sources: Pitch Deck v1.1 (the ask; traction); Kyle's decision 5 (Nov 22, 2026). The Pitch Deck's line that the $1MM 'will also generate "
    "$2-2.5MM in revenue' is left out because the fee is now contingent on value. FOR KYLE: at the Nov 22 cost assumptions the first quarter "
    "(December 2026 to February 2027) costs about $1.9MM, so $1MM is about seven weeks of the full plan, or about four months of the two pods and "
    "consulting leadership alone. The model needs about $6.3MM before it pays for itself (funding is topic 7 of the model review).")

prs.save(OUT)
print("saved", OUT)
