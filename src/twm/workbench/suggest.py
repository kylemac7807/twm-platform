"""Suggestions for the task card (plan v3 step 4, retrained after Kyle's first answer, Oct 13, 2026).

A suggestion is a labelled best guess the analyst confirms or changes; it is never saved on its own and never comes from the
model. Sources, in order of trust:
1. the rules: if the normalizer resolves the title, that is the suggestion;
2. the analyst's own saved answers: an answer for the same core title, then for a similar one ("you answered 'X' as ...");
3. the halves of a dual title ("Project Manager I / Test Leads");
4. generic-word defaults, taxonomy/core_defaults.csv: what 'analyst' or 'developer' on its own usually means, a file Kyle reads and extends;
5. similarity to known titles and role names, on the core of the title with seniority and location words stripped, so a word
   like "Associate" can never pick the role.
The band comes from the seniority word through the band crosswalk ("Associate" is junior); technology tags come from the title."""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Optional

from twm.pipeline.normalize import normalize_title, resolve
from twm.pipeline.resolve_model import similar_roles
from twm.taxonomy.store import TaxonomyStore

TAXONOMY = Path(__file__).resolve().parents[3] / "taxonomy"
STOP = {"of", "and", "the", "for", "in", "a", "an", "to", "or", "&", "-", "/", "i", "ii", "iii", "iv", "v"}
SENIORITY_SCHEMES = ("Title modifier", "Consulting pyramid")   # schemes whose levels are seniority words; G-Cloud and DDaT labels include role words


def load_core_defaults(path: Path = TAXONOMY / "core_defaults.csv") -> dict[str, dict]:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        return {r["core"].strip().lower(): r for r in csv.DictReader(f)}


STEMS = {"architecture": "architect", "architectural": "architect", "engineering": "engineer", "management": "manager", "managing": "manager",
         "analysis": "analyst", "analytics": "analyst", "testing": "test", "tester": "test", "tests": "test", "administration": "administrator",
         "consulting": "consultant", "consultancy": "consultant", "development": "developer", "developing": "developer", "programming": "programmer",
         "designing": "designer", "operations": "operation", "specialists": "specialist", "engineers": "engineer", "analysts": "analyst",
         "managers": "manager", "architects": "architect", "developers": "developer"}
# words that name what a person is (the head noun of a title); a role whose name ends in one of these and shares another word
# with the title is the most likely meaning: "cyber security ... architecture and design" -> Security Architect
HEAD_NOUNS = ("architect", "engineer", "analyst", "manager", "developer", "programmer", "administrator", "consultant", "designer", "tester",
              "specialist", "lead", "director", "coordinator", "scientist", "writer", "researcher", "auditor", "responder", "officer")


def _stem(t: str) -> str:
    return STEMS.get(t, t)


def _tokens(s: str) -> set[str]:
    return {_stem(t) for t in re.findall(r"[a-z0-9.#+]+", (s or "").lower()) if t not in STOP}


def head_noun(core: str) -> Optional[str]:
    """The last word in the title's core that names what the person is, after stemming ('architecture' -> 'architect')."""
    words = [_stem(w) for w in re.findall(r"[a-z]+", (core or "").lower())]
    for w in reversed(words):
        if w in HEAD_NOUNS:
            return w
    return None


def roles_by_head_noun(core: str, store: TaxonomyStore) -> list[tuple[str, int]]:
    """Roles whose name ends in the title's head noun and share at least one other word with the title, best overlap first."""
    hn = head_noun(core)
    if not hn:
        return []
    toks = _tokens(core) - {hn}
    out = []
    for r in store.roles:
        name_toks = [_stem(t) for t in re.findall(r"[a-z]+", r.name.lower())]
        if not name_toks or name_toks[-1] != hn:
            continue
        shared = len(toks & set(name_toks[:-1]))
        if shared:
            out.append((r.role_id, shared))
    return sorted(out, key=lambda x: -x[1])


def band_from_words(title: str, store: TaxonomyStore) -> tuple[Optional[str], Optional[str]]:
    """The band a seniority word in the title implies, through the crosswalk schemes that carry such words. Returns (band, word)."""
    words = re.findall(r"[A-Za-z]+", title)
    for w in words:
        for scheme in SENIORITY_SCHEMES:
            b = store.band_for(scheme, w)
            if b is not None:
                return b.twm_band, w
    return None, None


def suggest(title: str, store: TaxonomyStore, *, saved: Optional[list[dict]] = None, core_defaults: Optional[dict[str, dict]] = None) -> dict:
    """saved: the analyst's live answers for this vendor, as dicts with observed_title, canonical_role_id, twm_band, scope."""
    saved = saved or []
    defaults = core_defaults if core_defaults is not None else load_core_defaults()
    base = resolve(title, store)
    nt = normalize_title(title, store)
    core = (nt.core or nt.key or title).strip().lower()
    band, band_word = (base.twm_band, nt.seniority_token) if base.twm_band else band_from_words(title, store)
    out: list[dict] = []
    seen: set[str] = set()

    def add(rid: Optional[str], why: str, score: float) -> None:
        if rid and rid in store.role_by_id and rid not in seen:
            seen.add(rid); out.append(dict(id=rid, name=store.role_by_id[rid].name, why=why, score=round(score, 2)))

    # 1. the rules
    if base.status == "resolved" and base.canonical_role_id:
        add(base.canonical_role_id, "the rules place it here", 1.0)
    # 2. the analyst's own answers: same core first, then similar cores
    core_toks = _tokens(core)
    scored = []
    for a in saved:
        a_core = (normalize_title(a["observed_title"], store).core or a["observed_title"]).strip().lower()
        if not a.get("canonical_role_id"):
            continue
        if a_core == core:
            scored.append((1.0, a))
        else:
            t = _tokens(a_core)
            if core_toks and t:
                j = len(core_toks & t) / len(core_toks | t)
                if j >= 0.5:
                    scored.append((j, a))
    for sc, a in sorted(scored, key=lambda x: -x[0]):
        add(a["canonical_role_id"], f"you answered '{a['observed_title']}' as this" + (f" (for {'this contract set' if a.get('scope') == 'set' else 'this vendor' if a.get('scope') == 'vendor' else 'everyone'})" if a.get("scope") else ""), 0.95 * sc)
    # 3. halves of a dual title
    for rid in base.candidates:
        add(rid, "one half of the title", 0.9)
    # 4. generic-word defaults
    d = defaults.get(core)
    if d:
        add(d["canonical_role_id"], f"what '{core}' on its own usually means", 0.85)
        for alt in (d.get("alternatives") or "").split(";"):
            add(alt.strip(), f"another common meaning of '{core}'", 0.6)
    # 5 and 6, merged by score: a role that names what the person is (the head noun) and shares another word of the title,
    #    and similarity to known titles on the core, never on a seniority word; a similar title whose role has a different
    #    head noun ("secure design" -> engineer, for an "architecture" title) is marked down
    hn = head_noun(core)
    pool: list[tuple[float, str, str]] = []
    for rid, shared in roles_by_head_noun(core, store):
        pool.append((0.45 + 0.1 * shared, rid, f"a role ending in '{hn}' that shares words with the title"))
    for rid, score, matched in similar_roles(store, core, k=6):
        mt = _tokens(matched)
        if core_toks and not (core_toks & mt):
            continue
        sc = 0.8 * score
        if hn and head_noun(store.role_by_id[rid].name) not in (None, hn):
            sc *= 0.7
        pool.append((sc, rid, f"similar to '{matched}'"))
    for sc, rid, why in sorted(pool, key=lambda x: -x[0]):
        add(rid, why, sc)
    return dict(title=title, core=core, suggestions=out[:4], band=band, band_word=band_word, tech_found=list(nt.tech_tags),
                location=base.attr_location, rules_status=base.status,
                note="suggestions come from your earlier answers, the usual meaning of the words, and similar known titles; never from the model. Confirm or change.")
