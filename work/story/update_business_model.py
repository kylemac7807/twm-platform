"""Copy Kyle's Business Model workbook and apply his Nov 22, 2026 assumptions, keeping every formula.

Usage: python update_business_model.py <source workbook> <output workbook>
Excel recalculates the copy afterwards (openpyxl writes formulas but not their results).
"""
import sys

import openpyxl
from openpyxl.styles import Font

SRC, OUT = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(SRC)
rev, cost = wb["Revenue"], wb["Cost"]

CHANGES = [  # sheet, cell, label cell, new value, reason
    (rev, "B9", "A9", 1.5, "Every Early Adopter pays $1.5MM, the second cohort too (Kyle, Nov 22, 2026)"),
    (cost, "B9", "A9", 225, "Engagement Manager cost (Kyle, Nov 22, 2026)"),
    (cost, "B10", "A10", 100, "Associate cost (Kyle, Nov 22, 2026)"),
    (cost, "B29", "A29", 500, "Software and AI leader cost; the Business Plan text said 700, the workbook 750 (Kyle, Nov 22, 2026)"),
    (cost, "B33", "A33", 200, "Engineer cost (Kyle, Nov 22, 2026)"),
]

fin = wb["Financials"]
# Kyle, Nov 22, 2026 (second pass): only 4 Early Adopters. Their $1.5MM each is earned over the two quarters of
# Value Acceleration (workbook Q3-Q4 2026 = March to August 2027), so all $6MM falls in Year 1. The two clients that
# were the second cohort become full-fee clients from their original start (workbook Q1 2027 = September 2027).
FORMULAS = [
    ("D4", "=Revenue!$B$6*Revenue!$B$7/2", "Early Adopter fees earned over the two quarters of Value Acceleration (were spread over four)"),
    ("E4", "=Revenue!$B$6*Revenue!$B$7/2", "as D4"),
    ("G4", "=Revenue!$B$8*Revenue!$B$18/4", "the two former second-cohort clients pay the full fee (was 2 x $2MM over two quarters, plus Early Adopter instalments)"),
    ("H4", "=Revenue!$B$8*Revenue!$B$18/4", "as G4"),
]
formula_log = []
for cell, f, why in FORMULAS:
    formula_log.append(["Financials", cell, fin[cell].value, f, why])
    fin[cell] = f
rev["A5"] = ("Revenue - first year (updated Nov 22, 2026): 4 Early Adopters each pay $1.5MM, earned over the ~6 months of Value Acceleration "
             "(workbook Q3-Q4 2026; March to August 2027 in the pitch deck's dates). There is no second cohort of Early Adopters: those 2 clients "
             "pay the full fee from workbook Q1 2027 (September 2027).")
rev["A8"] = "Full-fee clients from Q1 2027 (formerly the second cohort of Early Adopters) - Number"
rev["A9"] = "Not used since Nov 22, 2026 (these clients pay the full fee, B18)"

log = wb.create_sheet("Changes")
log["A1"] = "Changes from 'TWM - Business Model - October 2nd.xlsx'"
log["A1"].font = Font(bold=True)
log.append([])
log.append(["Sheet", "Input", "Was", "Now", "Why"])
for c in log[3]:
    c.font = Font(bold=True)
for ws, cell, label, new, why in CHANGES:
    old = ws[cell].value
    ws[cell] = new
    log.append([ws.title, ws[label].value, old, new, why])
log.append([])
log.append(["Formula changes (Kyle, Nov 22, 2026: only 4 Early Adopters; all $6MM in Year 1; the former second cohort pays the full fee)"])
log[log.max_row][0].font = Font(bold=True)
log.append(["Sheet", "Cell", "Was", "Now", "Why"])
for c in log[log.max_row]:
    c.font = Font(bold=True)
for row in formula_log:
    log.append(row)
log.append([])
log.append(["Unchanged and confirmed by Kyle on Nov 22, 2026: the Early Adopter fee of $1.5MM, the full fee of $4MM per client per year, and the client ramp."])
log.append(["Open: the 4 Early Adopters pay nothing between the end of Value Acceleration (August 2027) and March 2028, when the workbook starts them on the full fee."])
log.append(["Figures in $MM except the Cost sheet's per-person costs, which are in $ thousands ('$M'), as in the original. All CAD."])
log.append(["The pitch deck counts these calendar years from a December 2026 start: workbook 2026 = Year 1 (first nine months of operations), 2030 = Year 5, exit run rate 2031."])
for col, w in zip("ABCDE", (12, 36, 8, 8, 90)):
    log.column_dimensions[col].width = w
wb.save(OUT)
print("saved", OUT)
for ws, cell, label, new, why in CHANGES:
    print(f"  {ws.title}!{cell} {ws[label].value}: now {new}")
