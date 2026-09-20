"""M1 acceptance test: round-trip every observed seed title through rules + mapping table,
and sanity-check bands against the sources' own rate grids. Writes taxonomy/REPORT.md.

    .venv/Scripts/python.exe -m twm.taxonomy.acceptance
"""
from __future__ import annotations

import csv
import io
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from statistics import mean
from typing import Optional

from twm.pipeline.normalize import ResolutionResult, resolve
from twm.taxonomy.models import BAND_ORDER, BANDS
from twm.taxonomy.store import TaxonomyStore, title_key


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "taxonomy").is_dir() and (p / "corpus").is_dir():
            return p
    raise FileNotFoundError("repo root not found")


ROOT = repo_root()
RC = ROOT / "corpus" / "twm_corpus" / "02_rate_cards"
GC = ROOT / "corpus" / "gc15_ratecards"
FW = ROOT / "corpus" / "twm_corpus" / "01_skills_frameworks"


def read_csv_skip_comments(p: Path) -> list[dict]:
    lines = [l for l in p.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    return list(csv.DictReader(io.StringIO("\n".join(lines))))


def parse_rate(s: str) -> Optional[float]:
    s = (s or "").strip().replace(",", "").replace("£", "").replace("$", "")
    if not s or s in ("-", "—", "n/a", "N/A"):
        return None
    m = re.findall(r"\d+(?:\.\d+)?", s)
    if not m:
        return None
    vals = [float(x) for x in m[:2]]
    return sum(vals) / len(vals)  # midpoint for ranges like 650-750


# --------------------------------------------------------------------------- observation sets
@dataclass
class Obs:
    source: str
    title: str
    scheme: Optional[str]
    level: Optional[str]
    years: Optional[float] = None
    rate: Optional[float] = None
    grid: Optional[str] = None       # rate grid id for band sanity (e.g. "GC15 UK: Accenture")
    expect_role_of: Optional[str] = None  # DDaT: the ladder's parent role title


def load_observations() -> list[Obs]:
    obs: list[Obs] = []
    # Texas DIR 2024
    for r in read_csv_skip_comments(RC / "deep2_US_TX_DIR_ITSAC_NTE_rates_2024_DIR-CPO-5570.csv"):
        obs.append(Obs("Texas DIR ITSAC 2024", r["job_title"], "Texas DIR", r["level"], rate=float(r["hourly_rate_usd"]), grid="Texas DIR 2024 NTE (USD/hr)"))
    # NY HBITS
    for r in read_csv_skip_comments(RC / "US_NY_OGS_HBITS_avg_hourly_bill_rates_2026.csv"):
        obs.append(Obs("NY OGS HBITS 23158", r["job_title"], "NY HBITS", r["skill_level"], rate=float(r["avg_hourly_rate_usd"]),
                       grid=f"NY HBITS 2026 region {r['region']} (USD/hr)"))
    # TBIPS categories x 3 levels
    tb = (RC / "CA_TBIPS_resource_categories_skills_matrix.md").read_text(encoding="utf-8")
    for m in re.finditer(r"\b([AGIBPC])\.(\d+) (.+?)(?: \(or cert\))?(?=;|\.\s|\.$|\n)", tb, re.M):
        for lv in ("Level 1", "Level 2", "Level 3"):
            obs.append(Obs("Canada TBIPS", m.group(3).strip(), "TBIPS", lv))
    # G-Cloud 15 cards
    row_re = re.compile(r"^\| ([^|]+) \| ([^|]+) \| ([^|]*) \| ([^|]*) \|$")
    for p in sorted(GC.glob("UK_GCloud15_*.md")):
        vendor = p.stem.split("_")[2]
        for line in p.read_text(encoding="utf-8").splitlines():
            m = row_re.match(line)
            if not m or m.group(1).strip() in ("Role", "---") or m.group(1).startswith("-"):
                continue
            role_t, level = m.group(1).strip(), m.group(2).strip()
            uk, off = parse_rate(m.group(3)), parse_rate(m.group(4))
            obs.append(Obs("UK G-Cloud 15", role_t, "UK G-Cloud 15", level, rate=uk, grid=f"GC15 UK rate: {vendor} (GBP/day)"))
            if off is not None:
                obs.append(Obs("UK G-Cloud 15", role_t, "UK G-Cloud 15", level, rate=off, grid=f"GC15 offshore rate: {vendor} (GBP/day)"))
    # Deloitte grade card (band -> rate only; no titles)
    deloitte = (GC / "UK_GCloud15_Deloitte_SFIA_ratecard.md").read_text(encoding="utf-8")
    sect = deloitte.split("## Standard Rate Card (UK)")[1].split("## Specialist")[0]
    for line in sect.splitlines():
        m = re.match(r"^\| ([^|]+) \| ([\d,]+) \|$", line)
        if m and m.group(1).strip() != "Civil Service grade band" and not m.group(1).startswith("-"):
            obs.append(Obs("Deloitte GC15 grades", "(grade band)", "Deloitte CS grade", m.group(1).strip(), rate=parse_rate(m.group(2)),
                           grid="GC15 Deloitte standard UK card by CS grade (GBP/day)"))
    # DDaT ladders: every role-level label as an observed title
    dd = FW / "DDaT_Role_and_skill_content_2026-08-28.csv"
    if dd.exists():
        seen = set()
        with dd.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                key = (r["Role"], r["Role Level"])
                if key in seen or r["Role Level"].strip().upper() == "NOT IN USE":
                    continue
                seen.add(key)
                obs.append(Obs("UK DDaT ladders", r["Role Level"].strip(), "DDaT", r["Role Level"].strip(), expect_role_of=r["Role"].strip()))
    # GSA
    for r in read_csv_skip_comments(RC / "deep2_US_GSA_CALCplus_category_rate_stats_2026.csv"):
        obs.append(Obs("US GSA CALC+", r["labor_category"], None, None))
    for name, src, ycol in (("US_GSA_MAS_ConstellationWest_pricelist_54151S_2025.md", "GSA pricelist Constellation West", "year1_hourly_rate"),
                            ("US_GSA_MAS_tCognition_pricelist_54151S.md", "GSA pricelist tCognition", "rate_2025"),
                            ("US_GSA_ITSchedule_CDOTechnologies_pricelist_legacy.md", "GSA pricelist CDO Technologies", "year13")):
        txt = (RC / name).read_text(encoding="utf-8")
        m = re.search(r"^labor_category,.*?$(.*?)^\s*$", txt, re.M | re.S)
        if not m:
            continue
        hdr = re.search(r"^labor_category,.*$", txt, re.M).group(0).split(",")
        for line in m.group(1).strip().splitlines():
            parts = line.split(",")
            row = dict(zip(hdr, parts))
            rate = parse_rate(row.get(ycol, ""))
            obs.append(Obs(src, parts[0], None, None, rate=rate, grid=f"{src} (USD/hr, title-modifier bands)" if src.endswith("tCognition") else None))
    return obs


# --------------------------------------------------------------------------- run
@dataclass
class SourceTally:
    n: int = 0
    resolved: int = 0
    unbanded: int = 0
    ambiguous: int = 0
    flagged: int = 0
    band_sources: Counter = field(default_factory=Counter)
    matched_on: Counter = field(default_factory=Counter)


def run(store: TaxonomyStore, obs: list[Obs]):
    results: list[tuple[Obs, ResolutionResult]] = []
    cache: dict[tuple, ResolutionResult] = {}
    for o in obs:
        k = (o.title, o.scheme, o.level, o.years)
        if k not in cache:
            cache[k] = resolve(o.title, store, source=o.source, source_scheme=o.scheme, source_level=o.level, years=o.years)
        results.append((o, cache[k]))
    return results


def build_report(store: TaxonomyStore, results) -> str:
    L: list[str] = []
    tallies: dict[str, SourceTally] = defaultdict(SourceTally)
    distinct: dict[str, set] = defaultdict(set)
    flagged: dict[str, set] = defaultdict(set)
    ambiguous: dict[str, set] = defaultdict(set)
    ddat_mismatch: list[tuple[str, str, str, str]] = []
    for o, r in results:
        if o.source == "Deloitte GC15 grades":
            continue  # grade bands carry no titles; they only feed the band sanity check
        key = (o.title, o.level)
        if key in distinct[o.source]:
            continue
        distinct[o.source].add(key)
        t = tallies[o.source]
        t.n += 1
        if r.status == "resolved" and r.twm_band is None:
            t.unbanded += 1
            t.matched_on[r.matched_on] += 1
        elif r.status == "resolved":
            t.resolved += 1
            t.band_sources[r.band_source] += 1
            t.matched_on[r.matched_on] += 1
        elif r.status == "ambiguous":
            t.ambiguous += 1
            ambiguous[o.source].add((o.title, ", ".join(r.candidates)))
        else:
            t.flagged += 1
            flagged[o.source].add((o.title, o.level or "", "; ".join(r.notes)))
        if o.expect_role_of:
            parent = resolve(o.expect_role_of, store, source_scheme="DDaT")
            if r.status == "resolved" and parent.canonical_role_id and r.canonical_role_id != parent.canonical_role_id:
                ddat_mismatch.append((o.expect_role_of, o.title, parent.canonical_role_id, r.canonical_role_id))

    tot = SourceTally()
    for t in tallies.values():
        tot.n += t.n; tot.resolved += t.resolved; tot.unbanded += t.unbanded; tot.ambiguous += t.ambiguous; tot.flagged += t.flagged
        tot.band_sources.update(t.band_sources); tot.matched_on.update(t.matched_on)

    L.append("# Role Framework v0 — Acceptance Report\n")
    L.append(f"Generated {date.today().isoformat()} by `python -m twm.taxonomy.acceptance` from `taxonomy/*.csv` and the corpus seed sources.\n")
    L.append("## Framework size\n")
    L.append(f"- Families: **{len(store.families)}** (spec draft 16; two added — see Deviations)")
    L.append(f"- Canonical roles: **{len(store.roles)}** (target 120–180)")
    L.append(f"- Band crosswalk rows: **{len(store.bands)}** across schemes: {', '.join(store.schemes())}")
    L.append(f"- Tech vocabulary: **{len(store.tech)}** tags")
    act = sum(1 for m in store.mappings if m.status == "active")
    fl = sum(1 for m in store.mappings if m.status == "flagged")
    L.append(f"- Seeded title mappings: **{len(store.mappings)}** ({act} active, {fl} flagged; target 250–400)\n")
    fam_counts = Counter(r.family_id for r in store.roles)
    L.append("| Family | Roles |\n|---|---|")
    for f in store.families:
        L.append(f"| {f.name} (`{f.family_id}`) | {fam_counts.get(f.family_id, 0)} |")
    L.append("")

    L.append("## Round-trip test (spec acceptance)\n")
    L.append("Every distinct (observed title, source level) from the seed sources resolved through rules 1–4 + the mapping table. "
             "No model or embedding call is involved; anything the rules cannot place is *flagged* for the human queue. "
             "A title whose role resolves but which carries no seniority evidence is left **unbanded** on purpose "
             "(decided Sept 19, 2026: never invent seniority); it is excluded from band-level benchmark cuts.\n")
    L.append("| Source | Distinct titles×levels | Role + band | Role only (unbanded) | Ambiguous | Flagged | % role + band |\n|---|---|---|---|---|---|---|")
    for src in sorted(tallies):
        t = tallies[src]
        L.append(f"| {src} | {t.n} | {t.resolved} | {t.unbanded} | {t.ambiguous} | {t.flagged} | {100 * t.resolved / t.n:.1f}% |")
    pct = 100 * tot.resolved / tot.n if tot.n else 0
    L.append(f"| **All sources** | **{tot.n}** | **{tot.resolved}** | **{tot.unbanded}** | **{tot.ambiguous}** | **{tot.flagged}** | **{pct:.1f}%** |")
    verdict = "PASS" if pct >= 90 else "FAIL"
    role_pct = 100 * (tot.resolved + tot.unbanded) / tot.n if tot.n else 0
    L.append(f"\n**Target ≥ 90% resolved to exactly one (role, band): {pct:.1f}% → {verdict}.** "
             f"Role resolved, with or without a band: {role_pct:.1f}%.\n")
    L.append("**Read this number correctly.** It is a *consistency* check, not a test of generalization: the mapping table "
             "was seeded from these same sources, so most hits are exact look-ups of titles already in the table. Only the "
             "matches listed as `core` below show the rules taking an unfamiliar title apart. How well the framework handles "
             "documents it has never seen is measured by a separate held-out test, which has not yet been run.\n")
    L.append("How the band was determined for resolved titles:\n")
    L.append("| band source | count | share |\n|---|---|---|")
    for k, v in tot.band_sources.most_common():
        L.append(f"| {k} | {v} | {100 * v / tot.resolved:.1f}% |")
    L.append("\nHow the role was matched:\n")
    L.append("| matched on | count |\n|---|---|")
    for k, v in tot.matched_on.most_common():
        L.append(f"| {k} | {v} |")
    L.append("")

    L.append("### Flagged titles (for Kyle's review)\n")
    if not any(flagged.values()):
        L.append("None.\n")
    for src in sorted(flagged):
        L.append(f"**{src}**\n")
        L.append("| observed title | level | why |\n|---|---|---|")
        for title, lv, why in sorted(flagged[src]):
            L.append(f"| {title} | {lv} | {why} |")
        L.append("")
    L.append("### Ambiguous titles (2+ candidate roles — each is a disambiguation bug)\n")
    if not any(ambiguous.values()):
        L.append("None.\n")
    for src in sorted(ambiguous):
        L.append(f"**{src}**\n")
        L.append("| observed title | candidates |\n|---|---|")
        for title, c in sorted(ambiguous[src]):
            L.append(f"| {title} | {c} |")
        L.append("")
    L.append("### DDaT ladder consistency\n")
    L.append("Each DDaT role-level label (e.g. *Senior data engineer*, *Head of data science*) was resolved as a free-standing title; "
             "it should land on the same canonical role as its parent DDaT role.\n")
    if ddat_mismatch:
        L.append("| DDaT role | level label | parent resolves to | label resolves to |\n|---|---|---|---|")
        for a, b, c, d in sorted(ddat_mismatch):
            L.append(f"| {a} | {b} | {c} | {d} |")
        L.append(f"\n{len(ddat_mismatch)} mismatches. Expected where a DDaT ladder spans two TWM roles "
                 "(DDaT's *Service desk manager* ladder starts at *Service desk analyst*, which TWM keeps as its own role); "
                 "any other mismatch is a bug.\n")
    else:
        L.append("All labels landed on their parent role. 0 mismatches.\n")

    # ---------------------------------------------------------------- band sanity
    L.append("## Band sanity check (rate monotonicity)\n")
    L.append("Within each source's rate grid, the mean rate per TWM band must increase junior → intermediate → senior → lead_principal after mapping. "
             "Violations mean the band crosswalk disagrees with the money.\n")
    L.append("| rate grid | junior | intermediate | senior | lead_principal | n | monotonic? |\n|---|---|---|---|---|---|---|")
    violations = []
    grids: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for o, r in results:
        if o.grid and o.rate is not None:
            band = r.twm_band
            if o.source == "Deloitte GC15 grades":
                b = store.band_for("Deloitte CS grade", o.level)
                band = b.twm_band if b else None
            if band:
                grids[o.grid][band].append(o.rate)
    for g in sorted(grids):
        means = {b: (mean(v) if v else None) for b, v in ((b, grids[g].get(b, [])) for b in BANDS)}
        present = [(b, means[b]) for b in BANDS if means[b] is not None]
        mono = all(present[i][1] <= present[i + 1][1] for i in range(len(present) - 1))
        n = sum(len(v) for v in grids[g].values())
        cells = [f"{means[b]:,.0f}" if means[b] is not None else "—" for b in BANDS]
        L.append(f"| {g} | {' | '.join(cells)} | {n} | {'yes' if mono else '**NO**'} |")
        if not mono:
            violations.append((g, present))
    L.append("")
    if violations:
        L.append(f"**{len(violations)} grid(s) violate monotonicity:**\n")
        for g, present in violations:
            L.append(f"- {g}: " + " → ".join(f"{b} {m:,.0f}" for b, m in present))
        L.append("")
    else:
        L.append("All grids monotonic.\n")

    # ---------------------------------------------------------------- deviations & notes
    L.append("## Deviations from the spec draft (with justification)\n")
    L.append("1. **Two families added (18 vs 16).** `exec` Technology Leadership: G-Cloud 15 and DDaT publish a 'Chief digital and data' category priced as roles (e.g. £3,200/day); C-level titles are roles, not bands, and belong nowhere else. "
             "`chg` Change, Training & Communications: TBIPS stream 5 (change management consultant) and Texas DIR (OCM manager, instructor trainer, communications coordinator) both carry adoption/training/comms titles that are not delivery management. Non-IT adoption work bolts on here.")
    L.append("2. **Packaged Applications uses five generic roles** (functional consultant, developer, technical consultant, architect, administrator) with the platform as the tech tag (`sap`, `salesforce`, `servicenow`…), rather than one role per platform × function. "
             "The normalizer routes generic cores (developer/consultant/analyst/architect/administrator) into this family whenever a packaged-platform tag is present. **Proposed — Kyle to confirm**; the alternative (platform-named roles such as 'SAP Consultant') is a point-release change: add roles, re-point mappings.")
    L.append("3. **No GIS roles.** TBIPS stream 2 (11 GIS categories) maps to generic roles with tech tag `gis`, per the technology-as-attribute rule.")
    L.append("4. **DDaT level labels derive bands by wording** when not listed in `band_crosswalk.csv` (band_source = `source_level_derived`), rather than enumerating ~150 role-specific labels. The rule: trainee/apprentice/junior/associate → junior; senior → senior; lead/principal/head/chief/manager → lead_principal; otherwise the working level → intermediate.")
    L.append("5. **No default band (decided Sept 19, 2026).** A title with no level code, no stated years and no modifier keeps its role but is left unbanded (`needs_band_review`), is excluded from band-level cuts, and its band alone goes to the review queue. v0 first defaulted these to `intermediate`; Cowork's review and Kyle rejected that as inventing seniority from no evidence.")
    L.append("6. **Location is client-relative (decided Sept 19, 2026).** Only the words onshore, nearshore and offshore classify directly. A place name yields a country; onshore means the same country as the client, set per deployment (`client_country`). Without it, places are captured but not classified.\n")
    L.append("## Not yet done / v0.1\n")
    L.append("- O*NET alternate/reported titles and ESCO multilingual synonyms are downloaded but not folded in (spec: v0.1).")
    L.append("- Embedding similarity (rule 5) is a protocol stub; no model is wired. Everything unresolved goes to the flag queue.")
    L.append("- SFIA crosswalk column is intentionally empty (licensing decision pending).")
    L.append("- TBIPS stream 7 (Telecommunications T.1–T.9) titles were not captured in the corpus extraction; they are absent from the seed.")
    L.append("- G-Cloud 14 cards, Job Bank wages and the contract corpus are not used for the round-trip (spec lists the five seed sources); they are the natural next stress test.")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    except Exception:
        pass
    store = TaxonomyStore.load()
    obs = load_observations()
    results = run(store, obs)
    report = build_report(store, results)
    out = store.source_dir / "REPORT.md"
    out.write_text(report, encoding="utf-8")
    print(report.split("## Deviations")[0])
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
