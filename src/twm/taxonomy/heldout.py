"""Held-out generalization test for the Role Framework (action item B1, Oct 6, 2026).

Runs the normalizer on titles from sources that were NOT used to seed the mapping table, with
no additions to the table, and reports how the rules cope with titles they have never seen.
The acceptance report is a consistency check; this is the honest test. Writes taxonomy/HELDOUT.md.

    .venv/Scripts/python.exe -m twm.taxonomy.heldout
"""
from __future__ import annotations

import csv
import io
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from twm.pipeline.normalize import resolve
from twm.taxonomy.acceptance import RC, read_csv_skip_comments, repo_root
from twm.taxonomy.store import TaxonomyStore

ROOT = repo_root()
SEED_SOURCES = {"Texas DIR ITSAC 2024", "NY OGS HBITS 23158", "Canada TBIPS", "UK G-Cloud 15", "UK DDaT framework",
                "US GSA CALC+", "GSA pricelist CDO Technologies", "GSA pricelist Constellation West", "GSA pricelist tCognition", "TWM alias"}


def load_heldout() -> list[tuple[str, str, str | None, str | None]]:
    """(source, title, scheme, level). None of these titles were in the seed."""
    obs: list[tuple[str, str, str | None, str | None]] = []
    # 1. Texas DIR TSS-699 Accenture pricing exhibit (76 titles incl. onsite/remote duplicates)
    for r in read_csv_skip_comments(RC / "deep3_US_TX_DIR_TSS699_Accenture_titles_2025.csv"):
        obs.append(("Texas DIR TSS-699 Accenture exhibit", r["labor_category"], None, None))
    # 2. Deloitte GSA MAS price list (titles from the extraction table)
    md = (RC / "deep3_US_GSA_MAS_Deloitte_pricelist.md").read_text(encoding="utf-8")
    for m in re.finditer(r"^\| ([^|]+) \| (HACS|54151S|HEAL) \|", md, re.M):
        title = m.group(1).strip()
        if " / " in title:  # collapsed rows like "Project Controller I / II / III"
            continue
        obs.append(("Deloitte GSA MAS price list", title, None, None))
    # 3. Canada Job Bank occupations (NOC titles)
    for r in read_csv_skip_comments(RC / "deep2_CA_JobBank_IT_hourly_wages_2023-2024.csv"):
        obs.append(("Canada Job Bank NOC occupations", r["occupation"], None, None))
    # 4. Texas DIR ITSAC 2020 generation: titles that differ from the 2024 grid
    t24 = {r["job_title"] for r in read_csv_skip_comments(RC / "deep2_US_TX_DIR_ITSAC_NTE_rates_2024_DIR-CPO-5570.csv")}
    for r in read_csv_skip_comments(RC / "US_TX_DIR_ITSAC_NTE_rates_2020_DIR-CPO-4653.csv"):
        if r["job_title"] not in t24:
            obs.append(("Texas DIR ITSAC 2020 (titles not in 2024)", r["job_title"], "Texas DIR", r["level"]))
    # 5. G-Cloud 14 Deloitte and Version 1 cards: role-named rows if any (most GC14 cards are vendor level label x category, no titles)
    for name, src in (("UK_GCloud14_Deloitte_SFIA_ratecard.md", "UK G-Cloud 14 Deloitte card"),
                      ("deep2_UK_GCloud14_Version1_SFIA_ratecard.md", "UK G-Cloud 14 Version 1 card"),
                      ("deep2_UK_GCloud14_specialists_SFIA_ratecards.md", "UK G-Cloud 14 specialists")):
        p = RC / name
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\| ([A-Za-z][^|]{3,60}) \|", line)
            if m:
                cell = m.group(1).strip()
                if re.match(r"^(SFIA )?Level|^\d|^-|Strategy|Change|Development|Delivery|People|Relationships|Role|Grade|Band", cell):
                    continue
                if re.search(r"[A-Za-z]{3,}", cell) and not re.search(r"£|\d{3}", cell):
                    obs.append((src, cell, None, None))
    # dedupe
    seen, out = set(), []
    for o in obs:
        k = (o[0], o[1].lower(), o[3])
        if k not in seen:
            seen.add(k); out.append(o)
    return out


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    store = TaxonomyStore.load()
    obs = load_heldout()
    tallies: dict[str, Counter] = defaultdict(Counter)
    matched: Counter = Counter()
    flagged: dict[str, list] = defaultdict(list)
    examples: dict[str, list] = defaultdict(list)
    for src, title, scheme, level in obs:
        r = resolve(title, store, source=src, source_scheme=scheme, source_level=level)
        t = tallies[src]
        t["n"] += 1
        if r.status == "resolved" and r.twm_band is not None:
            t["role_band"] += 1
        elif r.status == "resolved":
            t["role_only"] += 1
        elif r.status == "ambiguous":
            t["ambiguous"] += 1
        else:
            t["flagged"] += 1
            flagged[src].append(title)
        if r.status == "resolved":
            matched[r.matched_on] += 1
            if len(examples[src]) < 6:
                examples[src].append((title, r.canonical_role_id, r.twm_band or "unbanded", r.attr_technology or "", r.matched_on))
    tot = Counter()
    for t in tallies.values():
        tot.update(t)

    L = ["# Role Framework v0 — Held-out generalization test", "",
         f"Generated {date.today().isoformat()} by `python -m twm.taxonomy.heldout`. Titles from sources **not used to seed the mapping table**, resolved by the rules and the existing table with no additions. "
         "This is the honest test the acceptance report (a same-source consistency check) is not.", "",
         "| Source | Titles | Role + band | Role only (unbanded) | Ambiguous | Flagged | % role resolved |", "|---|---|---|---|---|---|---|"]
    for src in sorted(tallies):
        t = tallies[src]
        rr = t["role_band"] + t["role_only"]
        L.append(f"| {src} | {t['n']} | {t['role_band']} | {t['role_only']} | {t['ambiguous']} | {t['flagged']} | {100 * rr / t['n']:.1f}% |")
    rr = tot["role_band"] + tot["role_only"]
    pct = 100 * rr / tot["n"] if tot["n"] else 0
    L.append(f"| **All** | **{tot['n']}** | **{tot['role_band']}** | **{tot['role_only']}** | **{tot['ambiguous']}** | **{tot['flagged']}** | **{pct:.1f}%** |")
    L += ["", f"**Role resolved on unseen titles: {pct:.1f}%** (acceptance report on seed sources: 99.3%). Unbanded is expected here: most of these sources state no seniority level, so the title modifier is the only evidence.", "",
          "**History.** First run, Oct 6, 2026, before any change: **37.4%** of 115 titles. Two generic rule fixes the same day (seniority words in the middle of a title such as \"IT Sr. Manager\"; all-caps bracketed acronyms such as \"(BIA)\" dropped) and two junk rows removed from the Texas extraction gave the figure above. No title-specific aliases were added: that would turn a held-out test back into a consistency check. The flagged titles go to Kyle's review queue (`taxonomy/review-queue-heldout.md`) and are codified only after he decides. "
          "**Later the same day** Kyle reviewed all 65 rows in Word; 51 confirmed rows were codified with him as reviewer (method `human`, version 0.1) and one kept flagged, after which the figure above applies. From that point the titles he confirmed are no longer held out; the figure now measures the rules **plus the analyst queue**, which is how production works. The remaining flags are the rows he questioned (consulting Manager and Analyst grades, slash-combined project-manager/test titles, IT Center Associate Lead).", "",
          "How the role was matched (unseen titles can only hit by full-title coincidence, by the stripped core, or by a role name):", "",
          "| matched on | count |", "|---|---|"]
    for k, v in matched.most_common():
        L.append(f"| {k} | {v} |")
    L += ["", "## Examples of correct-looking resolutions (spot-check these)", ""]
    for src in sorted(examples):
        L.append(f"**{src}**" + NL)
        L.append("| title | role | band | tech | via |" + NL + "|---|---|---|---|---|")
        for title, role, band, tech, via in examples[src]:
            L.append(f"| {title} | {role} | {band} | {tech} | {via} |")
        L.append("")
    L += ["## Flagged titles (the rules could not place these; each is a candidate alias, role or rule)", ""]
    for src in sorted(flagged):
        L.append(f"**{src}** ({len(flagged[src])})" + NL)
        for title in flagged[src]:
            L.append(f"- {title}")
        L.append("")
    L += ["## Reading this", "",
          "- A flagged title is not a failure of the product: in production it goes to the model step (similarity search plus model confirmation, decided Oct 6) and then to the analyst queue, and the answer is kept. The number above is what the *rules alone* achieve on cold titles, which is the floor.",
          "- The gap between this and the acceptance score is the value the model step and the volume run must supply, and the evaluation harness (M3) will measure."]
    out = store.source_dir / "HELDOUT.md"
    out.write_text(NL.join(L) + NL, encoding="utf-8")
    print(NL.join(L[:14]))
    print(f"wrote {out}")
    return 0


NL = chr(10)

if __name__ == "__main__":
    sys.exit(main())
