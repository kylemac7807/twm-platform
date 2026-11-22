"""Replica of Kyle's Business Model workbook (TWM - Business Model - October 2nd.xlsx), quarter by quarter,
plus the scenarios used in the Nov 22, 2026 review. All figures CAD $MM, as the workbook states.

The workbook's quarters run Q1 2026 to Q4 2030. The deck counts from a December 2026 start, eight months later
than the Business Plan, so workbook quarter q starts eight months after its calendar date.
Run: python work/story/financial_model_review.py
"""
from dataclasses import dataclass, field, replace

Q = 20  # quarters, workbook Q1 2026 .. Q4 2030


@dataclass(frozen=True)
class A:
    # revenue (Revenue sheet)
    ea_n: int = 4
    ea_fee: float = 1.5
    ea2_n: int = 2
    ea2_fee: float = 2.0
    clients: tuple = (0, 0, 4, 4, 6, 6, 8, 8, 12, 12, 25, 25, 25, 25, 40, 40, 40, 40, 50, 50)  # Financials row 15
    fee_per_client: float = 4.0  # $MM per full-fee client per year
    full_fee_from: int = 6  # first quarter index billed at the full fee (workbook Q3 2027)
    ea_cash_lag: int = 0  # quarters between the EA work and the EA fee being earned (contingent fee)
    ea_paid: float = 1.0  # share of Early Adopter fees that are earned at all (contingency met)
    # consulting (Cost sheet)
    em: float = 0.35
    assoc: float = 0.25
    assoc_per_pod: int = 4
    clients_per_pod_early: int = 2  # until the full-fee period
    clients_per_pod_scale: int = 4
    consult_lead: tuple = (1.5, 4.0, 4.0, 7.0, 7.0)  # per year, years 1..5
    # software and AI
    sw_leaders: tuple = (2, 3, 10, 10, 10)
    sw_leader_cost: float = 0.75  # the workbook says 750; the Business Plan text says 700
    sw_eng: tuple = (6, 15, 50, 50, 50)
    sw_eng_cost: float = 0.30
    sw_overhead: tuple = (1.0, 1.5, 1.5, 4.0, 4.0)
    sw_start_q: int = 1  # software team costs start Q2 2026
    pods_start_q: int = 1  # first two pods hired Q2 2026 (a quarter before the Early Adopter work)
    ea_upfront: float = 0.0  # share of each Early Adopter fee paid at signing, before the value test
    # sales, overhead
    sales_per_client: float = 0.30
    overhead: tuple = (1.5, 3.0, 5.0, 7.0, 10.0)
    # additions not in the workbook
    per_client_run_cost: float = 0.0  # in-tenant deployment, support, security reviews, Azure, per client per year
    label: str = "base"


def run(a: A):
    rev, cost, prof, cl = [], [], [], []
    pod_cost = a.em + a.assoc_per_pod * a.assoc
    for q in range(Q):
        y = q // 4  # year index 0..4
        n = a.clients[q]
        # revenue: full-fee clients from the full-fee quarter, at the annual fee from their first day
        r = n * a.fee_per_client / 4 if q >= a.full_fee_from else 0.0
        # Early Adopter fees as the workbook books them (4 x 1.5 over Q3 2026..Q2 2027; second cohort 2 x 2.0 over
        # Q1..Q2 2027), optionally earned later (contingent), partly paid at signing, or partly never earned
        later = 1 - a.ea_upfront
        qe = q - a.ea_cash_lag
        if 2 <= qe <= 5:
            r += a.ea_n * a.ea_fee / 4 * a.ea_paid * later
        if 4 <= qe <= 5:
            r += a.ea2_n * a.ea2_fee / 2 * a.ea_paid * later
        if q == 2:
            r += a.ea_n * a.ea_fee * a.ea_upfront
        if q == 4:
            r += a.ea2_n * a.ea2_fee * a.ea_upfront
        # consulting: leadership plus pods sized to clients
        c_cons = a.consult_lead[y] / 4
        if q == 1 and a.pods_start_q <= 1:
            c_cons += (a.ea_n / a.clients_per_pod_early) * pod_cost / 4
        elif q >= 2:
            per = a.clients_per_pod_early if q < a.full_fee_from else a.clients_per_pod_scale
            c_cons += (n / per) * pod_cost / 4
        c_sw = 0.0 if q < a.sw_start_q else (a.sw_leaders[y] * a.sw_leader_cost + a.sw_eng[y] * a.sw_eng_cost + a.sw_overhead[y]) / 4
        c_sales = a.sales_per_client * n / 4
        c_oh = a.overhead[y] / 4
        c_run = a.per_client_run_cost * n / 4
        c = c_cons + c_sw + c_sales + c_oh + c_run
        rev.append(r); cost.append(c); prof.append(r - c); cl.append(n)
    return rev, cost, prof, cl


def workbook_quirks(a: A):
    """The workbook's own pod formula for 2027 H1 uses 'second adopters per team' (2) and for Q2 2026 uses EA/2; replicate exactly."""
    return a


def summary(a: A):
    rev, cost, prof, cl = run(a)
    yr = lambda xs: [round(sum(xs[i * 4:(i + 1) * 4]), 1) for i in range(5)]
    cum, trough, trough_q, be_q = 0.0, 0.0, None, None
    for q, p in enumerate(prof):
        cum += p
        if cum < trough:
            trough, trough_q = cum, q
    first_profit_q = next((q for q, p in enumerate(prof) if p > 0 and all(x > 0 for x in prof[q:])), None)
    cum = 0.0
    for q, p in enumerate(prof):
        cum += p
        if cum >= 0 and q > (trough_q or 0):
            be_q = q
            break
    return dict(label=a.label, revenue=yr(rev), cost=yr(cost), profit=yr(prof), exit_rev=round(rev[-1] * 4, 1),
                exit_profit=round(prof[-1] * 4, 1), exit_margin=round(prof[-1] / rev[-1] * 100) if rev[-1] else None,
                peak_funding=round(-trough, 1), trough_q=trough_q, first_profit_q=first_profit_q, payback_q=be_q)


def deck_quarter(q):
    """Workbook quarter index -> calendar quarter of its first month after the eight-month shift (Dec 2026 start)."""
    if q is None:
        return "never"
    month = 1 + 3 * (q % 4) + 8  # first month of the workbook quarter, shifted
    year = 2026 + q // 4 + (month - 1) // 12
    month = (month - 1) % 12 + 1
    return f"{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][month-1]} {year}"


BASE = A()

# The workbook's 2027 H1 consulting uses 6 clients / 2 per pod, and from Q3 2027 the scale ratio; Q2 2026 uses 4/2.
SCENARIOS = [
    BASE,
    replace(BASE, ea_cash_lag=2, label="EA fee earned two quarters later (contingent on >$10MM value)"),
    replace(BASE, ea_cash_lag=2, ea_paid=0.5, label="contingent fee, and only half the EAs reach $10MM"),
    replace(BASE, fee_per_client=2.5, label="full fee $2.5MM a year (BP: $20MM saved -> $2-3MM)"),
    replace(BASE, clients=(0, 0, 4, 4, 6, 6, 6, 6, 8, 8, 12, 12, 18, 18, 25, 25, 32, 32, 40, 40), label="clients two quarters to a year slower, 40 by year 5"),
    replace(BASE, per_client_run_cost=0.4, label="add $0.4MM per client per year to run each in-tenant install"),
    replace(BASE, ea_cash_lag=2, fee_per_client=3.0, clients=(0, 0, 4, 4, 6, 6, 6, 6, 8, 8, 12, 12, 18, 18, 25, 25, 32, 32, 40, 40), per_client_run_cost=0.4,
            label="combined: contingent fee, $3MM fee, slower ramp, run cost"),
    # lean launch: pods hired when the Early Adopter work starts, the software team waits for the Series A
    # (workbook Q1 2027 = Sep 2027 after the shift), half the Year 1 leadership and overhead; contingent fee
    replace(BASE, ea_cash_lag=2, pods_start_q=2, sw_start_q=4, consult_lead=(0.75, 4.0, 4.0, 7.0, 7.0), overhead=(0.75, 3.0, 5.0, 7.0, 10.0),
            label="lean launch with the contingent fee"),
    replace(BASE, ea_cash_lag=2, ea_upfront=1 / 3, pods_start_q=2, sw_start_q=4, consult_lead=(0.75, 4.0, 4.0, 7.0, 7.0), overhead=(0.75, 3.0, 5.0, 7.0, 10.0),
            label="lean launch, a third of each EA fee at signing"),
]

if __name__ == "__main__":
    rev, cost, prof, cl = run(BASE)
    print("Replica check, quarterly (workbook calendar):")
    print("  revenue", [round(x, 3) for x in rev])
    print("  cost   ", [round(x, 3) for x in cost])
    print("  profit ", [round(x, 3) for x in prof])
    cum, line = 0.0, []
    for p in prof:
        cum += p
        line.append(round(cum, 2))
    print("  cumulative", line)
    for s in SCENARIOS:
        r = summary(s)
        print()
        print(r["label"])
        print("  revenue by year", r["revenue"], " cost", r["cost"], " profit", r["profit"])
        print(f"  exit run rate: revenue {r['exit_rev']}, profit {r['exit_profit']} ({r['exit_margin']}%)")
        print(f"  cash needed before self-funding: {r['peak_funding']}  (deepest point {deck_quarter(r['trough_q'])})")
        print(f"  profitable every quarter from {deck_quarter(r['first_profit_q'])}; all money back by {deck_quarter(r['payback_q'])}")
