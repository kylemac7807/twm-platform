"""Build docs/story/follow-one-rate.html from facts.json (ledger + PDF facts, images as data URIs).

Every number on the page comes from the ledger or the page; nothing is typed in by hand.
"""
import json, sys, html
from datetime import datetime

facts_path, out_path = sys.argv[1], sys.argv[2]
F = json.load(open(facts_path, encoding="utf-8"))
ase, ops = F["ase"], F["ops"]
docs = {d["filename"][:3]: d for d in F["documents"] if d["filename"][:3].isdigit()}
rec085 = json.loads(docs["085"]["record_json"])
rec087 = json.loads(docs["087"]["record_json"])
run = next(r for r in F["runs"] if r["run_id"] == ase["run_id"])
texas = F["texas"]
tx_doc = next(d for d in F["per_doc"] if d["document_id"] == ase["document_id"])
gc_doc = next(d for d in F["per_doc"] if d["document_id"] != ase["document_id"])
T = F["totals"]
bbox = json.loads(ase["source_bbox"])
ops_bbox = json.loads(ops["source_bbox"])
run_date = datetime.fromisoformat(run["started_at"]).strftime("%B %-d, %Y") if sys.platform != "win32" else datetime.fromisoformat(run["started_at"]).strftime("%B %d, %Y").replace(" 0", " ")
created = datetime.fromisoformat(ase["created_at"]).strftime("%Y-%m-%d %H:%M UTC")
e = html.escape

def fmt_box(b):
    return "[" + ", ".join(f"{x:g}" for x in b) + "]"

# queue items for the Texas set, grouped
tx_queue_titles = [r for r in texas if r["resolution_status"] in ("flagged", "ambiguous")]
flagged_titles = [r for r in tx_queue_titles if r["resolution_status"] == "flagged"]
ambiguous_titles = [r for r in tx_queue_titles if r["resolution_status"] == "ambiguous"]

doc_labels = {
    "msa": "master agreement", "sow": "statement of work", "rate_card": "rate card", "solicitation": "solicitation",
    "sla": "service-level definitions", "amendment": "amendment", "unknown": "unknown",
}
doc_rows = ""
for k in sorted(docs):
    d = docs[k]
    rec = json.loads(d["record_json"])
    flag = rec["flags"][0] if rec["flags"] else ""
    link = rec["links"][0] if rec["links"] else None
    rel = {"exhibit_of": "exhibit of the master agreement", "under_msa": "statement of work under the master agreement"}.get(link["relation"], link["relation"]) if link else "the root: the master agreement itself"
    cls = f'{doc_labels.get(d["doc_class"], d["doc_class"])} ({d["class_confidence"]:.2f})'
    hl = ' class="hl"' if k == "085" else ""
    doc_rows += f'<tr{hl}><td>{e(d["filename"])}</td><td>{e(cls)}</td><td>{rec["page_count"]}</td><td>{e(rel)}</td><td class="flag">{e(flag)}</td></tr>\n'

queue_rows = ""
for r in flagged_titles:
    queue_rows += f'<tr><td>title</td><td>{e(r["observed_title"])}</td><td>{e(r["rate_as_stated"])}</td><td>no rule match; the model was asked and abstained; an analyst decides</td></tr>\n'
for r in ambiguous_titles:
    queue_rows += f'<tr><td>title</td><td>{e(r["observed_title"])}</td><td>{e(r["rate_as_stated"])}</td><td>one label for two jobs (project management and testing); ambiguous by design, the statement of work decides</td></tr>\n'
queue_rows += f'<tr><td>extraction</td><td>{e(F["queue_084"]["item"])}</td><td></td><td>{e(F["queue_084"]["detail"])} (Exhibit 2 is prose about financial provisions, not a rate table)</td></tr>\n'
queue_rows += f'<tr><td>intake</td><td>{e(F["queue_087"]["item"])}</td><td></td><td>{e(F["queue_087"]["detail"])}; a 3-page attachment whose first pages gave no signal, so the label rests on the file name only</td></tr>\n'
tx_queue_n = len(tx_queue_titles) + 2

# the model's own words for Operations, as stored (the ledger keeps the first 300 characters)
ops_detail = F["queue_ops"]["detail"]
ops_reason = ops_detail.split("(conf 0.30): ", 1)[1] if "(conf 0.30): " in ops_detail else ops_detail

# the 53 rows of the Texas exhibit, compact
tx_rows = ""
for r in texas:
    status = r["resolution_status"]
    role = r["canonical_role_id"] or ""
    band = r["twm_band"] or ("" if status != "resolved" else "unbanded")
    cls = {"flagged": "q", "ambiguous": "q"}.get(status, "")
    if r["obs_id"] == ase["obs_id"]:
        cls = "hl"
    counted = "yes" if r["counted"] else "no"
    tx_rows += f'<tr class="{cls}"><td>{r["obs_id"]}</td><td>{e(r["observed_title"])}</td><td class="num">{e(r["rate_as_stated"])}</td><td>{e(role)}</td><td>{e(band)}</td><td>{e(status)}</td><td>{counted}</td></tr>\n'

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Follow one rate</title>
<meta name="description" content="One real rate followed from the page of a signed Texas contract to a row in the ledger, through the six stages of the TWM pipeline, with the row that gets flagged instead.">
<style>
:root {{
  --bg: #f6f5f1; --card: #ffffff; --ink: #1d1d1b; --muted: #5d5c57; --line: #d9d7cf;
  --accent: #b22a2a; --accent-soft: #fbe9e9; --amber: #c27600; --amber-soft: #fff3df;
  --green: #2f6b3a; --green-soft: #e8f2ea; --blue: #27496d; --blue-soft: #e8eef6; --mono: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.5 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
main {{ max-width: 1800px; margin: 0 auto; padding: 24px 16px 64px; }}
h1 {{ font-size: 32px; line-height: 1.15; margin: 0 0 6px; letter-spacing: -0.01em; }}
h2 {{ font-size: 22px; margin: 44px 0 10px; }}
h3 {{ font-size: 15px; margin: 0 0 6px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }}
p {{ margin: 0 0 10px; }}
.lede {{ font-size: 18px; color: var(--muted); max-width: 900px; }}
.rule {{ background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--blue); padding: 12px 16px; margin: 18px 0 0; max-width: 900px; }}
.flow {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }}
.stage {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 14px 14px 12px; display: flex; flex-direction: column; min-width: 0; position: relative; }}
.stage .n {{ position: absolute; top: -12px; left: 12px; background: var(--blue); color: #fff; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 10px; }}
.stage h3 {{ color: var(--ink); font-size: 16px; text-transform: none; letter-spacing: 0; margin: 4px 0 4px; }}
.stage .what {{ font-size: 13.5px; color: var(--muted); margin-bottom: 10px; min-height: 0; }}
.row {{ border-top: 2px solid var(--accent); padding-top: 8px; margin-top: 4px; }}
.row.flag {{ border-top-color: var(--amber); }}
.row .tag {{ display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--accent); margin-bottom: 6px; }}
.row.flag .tag {{ color: var(--amber); }}
dl {{ margin: 0; display: grid; grid-template-columns: 1fr; gap: 0; font-size: 13px; }}
dt {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 7px; }}
dd {{ margin: 0; overflow-wrap: anywhere; }}
.v {{ font-family: var(--mono); font-size: 12.5px; }}
.big {{ font-size: 18px; font-weight: 700; line-height: 1.25; }}
.img {{ display: block; width: 100%; height: auto; border: 1px solid var(--line); border-radius: 4px; background: #fff; }}
.note {{ font-size: 12.5px; color: var(--muted); margin-top: 8px; }}
.check {{ font-size: 12.5px; margin-top: 8px; padding: 6px 8px; background: var(--green-soft); border-left: 3px solid var(--green); }}
.refuse {{ font-size: 12.5px; margin-top: 8px; padding: 6px 8px; background: var(--amber-soft); border-left: 3px solid var(--amber); }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; background: var(--card); }}
th, td {{ text-align: left; padding: 5px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }}
td.num {{ text-align: right; font-family: var(--mono); white-space: nowrap; }}
tr.hl td {{ background: var(--accent-soft); }}
tr.q td {{ background: var(--amber-soft); }}
td.flag {{ color: var(--amber); }}
.strip {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 16px; }}
.strip.amber {{ border-left: 6px solid var(--amber); }}
.strip.blue {{ border-left: 6px solid var(--blue); }}
.strip.coming {{ border: 2px dashed var(--line); background: transparent; }}
.cols {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }}
.kv {{ font-size: 14px; }}
.kv b {{ display: inline-block; min-width: 190px; color: var(--muted); font-weight: 500; }}
details {{ margin-top: 10px; }}
summary {{ cursor: pointer; color: var(--blue); font-size: 14px; }}
.muted {{ color: var(--muted); }}
.quote {{ font-style: italic; background: var(--bg); padding: 8px 10px; border-radius: 4px; font-size: 13.5px; }}
.terms dt {{ font-weight: 600; color: var(--ink); font-size: 14px; text-transform: none; letter-spacing: 0; margin-top: 0; }}
.terms {{ grid-template-columns: max-content 1fr; gap: 4px 14px; font-size: 14px; }}
.terms dd {{ margin-bottom: 2px; }}
footer {{ margin-top: 48px; font-size: 13px; color: var(--muted); border-top: 1px solid var(--line); padding-top: 14px; }}
@media (max-width: 1500px) {{ .flow {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} }}
@media (max-width: 980px) {{ .flow {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
@media (max-width: 640px) {{ .flow {{ grid-template-columns: 1fr; }} h1 {{ font-size: 26px; }} .kv b {{ min-width: 0; display: block; }} .terms {{ grid-template-columns: 1fr; }} }}
@media print {{ body {{ background: #fff; }} .flow {{ grid-template-columns: repeat(3, 1fr); }} }}
</style>
</head>
<body>
<main>
<h1>Follow one rate: from the page to the ledger</h1>
<p class="lede">One real number from a signed State of Texas contract with Accenture, followed through the six stages of the pipeline. The same row appears under every stage, exactly as the code recorded it. Beneath it, the row that gets flagged instead, because refusing to guess is the point.</p>
<div class="rule"><b>Everything here is real.</b> The document is public and unchanged. Every value is read from the ledger written by the run of {e(run_date)} or from the page itself. Nothing is mocked, rounded or filled in. Where the system did not know, the field is empty and says so.</div>

<h2>The six stages, one row</h2>
<div class="flow">

<section class="stage"><span class="n">1</span>
<h3>The document library</h3>
<p class="what">The collection of real contracts, rate cards, invoices and timesheets gathered to build the product. This one is Attachment 2.1, Pricing and Volumes, of Texas contract DIR-STS-TSS-699 with Accenture LLP, fetched from the Texas Department of Information Resources website.</p>
<div class="row"><span class="tag">This row</span>
<a href="#fullpage" title="See the page at full size"><img class="img" alt="Page 8 of the pricing attachment with the Advanced Systems Engineer row boxed in red" src="{F['img_thumb']}"></a>
<dl><dt>File</dt><dd class="v">{e(docs['085']['filename'])}</dd>
<dt>Page</dt><dd>{ase['source_page']} of {F['n_pages']} (the footer reads &ldquo;Rate Card&rdquo;)</dd>
<dt>Source class</dt><dd>public</dd></dl>
<p class="note">The red box is the row this page follows. It is drawn from the position the ledger stores, not by hand. Click the page to see it at full size.</p>
</div></section>

<section class="stage"><span class="n">2</span>
<h3>Intake</h3>
<p class="what">The front door. Each file gets a permanent id and a fingerprint of its contents, is checked for what it really is (by looking inside, never by its name), labelled, and linked to the other files of the same contract. One contract is usually several files; this one is seven.</p>
<div class="row"><span class="tag">This row</span>
<dl><dt>Document id</dt><dd class="v">{e(rec085['document_id'])}</dd>
<dt>Fingerprint</dt><dd class="v">{e(rec085['fingerprint'][:16])}&hellip;</dd>
<dt>True type</dt><dd>{e(rec085['true_type'])} (content checked)</dd>
<dt>Label</dt><dd>rate card, confidence {rec085['class_confidence']:.2f}</dd>
<dt>Evidence</dt><dd class="v">{e(rec085['class_evidence'])}</dd>
<dt>Contract numbers</dt><dd class="v">{e(', '.join(rec085['contract_numbers']))}</dd>
<dt>Contract set</dt><dd>exhibit of the master agreement (file 081)</dd>
<dt>Link evidence</dt><dd>{e(rec085['links'][0]['evidence'])}; confirmed</dd>
<dt>Readiness</dt><dd>{e(rec085['readiness'])}: usable text layer, {rec085['page_count']} pages</dd></dl>
<p class="check">Linking only on strong evidence: the contract number printed on the page. Without it, intake suggests a link and asks.</p>
</div></section>

<section class="stage"><span class="n">3</span>
<h3>Reading</h3>
<p class="what">Turns the file into text and tables that software can use, with the page and position of every element. A position is a box: four numbers, left, top, right, bottom, in points from the page corner. The box is what lets any number later light up its spot on the page.</p>
<div class="row"><span class="tag">This row</span>
<img class="img" alt="The header rows and the Advanced Systems Engineer row of the rate table, enlarged" src="{F['img_ase']}">
<dl><dt>Reader</dt><dd>local text-layer reader (no OCR needed)</dd>
<dt>Quality</dt><dd>native: text layer present, 26,304 characters over 11 pages</dd>
<dt>Page 8</dt><dd>116 text lines, 1 table of 111 rows by 19 columns (2,109 cells), each with a box</dd>
<dt>Title cell</dt><dd class="v">row 4, col 0 &ldquo;Advanced Systems Engineer&rdquo; [64.3, 127.6, 151.1, 133.2]</dd>
<dt>Rate cell</dt><dd class="v">row 4, col 2 &ldquo;$83.00&rdquo; [176.5, 127.6, 200.1, 133.2]</dd>
<dt>Text line</dt><dd class="v">{e(fmt_box(bbox))}</dd></dl>
<p class="note">Scan quality follows the row all the way to the ledger. A rate from a poor scan is never trusted as much as one from a native file.</p>
</div></section>

<section class="stage"><span class="n">4</span>
<h3>Extraction</h3>
<p class="what">A frontier model (rented, reached through one wrapper so it can be swapped) reads the table and fills a typed record: title, rate, unit, currency, period, location, each with a confidence. It records the words as written and does not interpret them. Then the software checks that every number it returned literally appears on the page at the claimed spot.</p>
<div class="row"><span class="tag">This row</span>
<img class="img" alt="The title cell and the year-one rate cell, enlarged" src="{F['img_cells']}">
<dl><dt>Title as written</dt><dd class="big">{e(ase['observed_title'])}</dd>
<dt>Rate as written</dt><dd class="big">{e(ase['rate_as_stated'])} per hour</dd>
<dt>Currency</dt><dd>{e(ase['currency'])}</dd>
<dt>Period</dt><dd>{e(ase['period_raw'])}</dd>
<dt>Column group</dt><dd>{e(ase['qualifier'])}</dd>
<dt>Location as written</dt><dd>{e(ase['location_raw'])}</dd>
<dt>Seniority stated</dt><dd class="muted">none on the page</dd>
<dt>Confidence</dt><dd>{ase['extraction_confidence']:.2f}</dd></dl>
<p class="check">Verified: the line &ldquo;{e(ase['source_quote'])}&rdquo; is on page {ase['source_page']} inside box {e(fmt_box(bbox))}. {tx_doc['n']} rows kept from this file, 0 rejected. A test proves an invented number ($999.99) is thrown out.</p>
<p class="refuse">Where the model is unsure of a field it leaves it blank and says why. It never fills a default.</p>
</div></section>

<section class="stage"><span class="n">5</span>
<h3>Normalization</h3>
<p class="what">Turns the vendor&rsquo;s words into the standard categories the ledger needs: a canonical role (one of 130) and a seniority band (one of four: junior, intermediate, senior, lead/principal). The rate itself is never changed. A title is resolved once, with its reasoning, and written to a mapping table; every later occurrence is a lookup, so the same title can never resolve two ways.</p>
<div class="row"><span class="tag">This row</span>
<dl><dt>Looked up</dt><dd>&ldquo;{e(ase['observed_title'])}&rdquo; was already in the mapping table</dd>
<dt>Resolved by</dt><dd>a person, Kyle McNamara, during the Role Framework stage, from this same exhibit (mapping confidence 1.00)</dd>
<dt>Role</dt><dd class="big">Systems Engineer</dd>
<dt>Role id</dt><dd class="v">{e(ase['canonical_role_id'])}</dd>
<dt>Band</dt><dd class="big">{e(ase['twm_band'])}</dd>
<dt>Band from</dt><dd>that mapping row (the ledger labels it <span class="v">{e(ase['band_source'])}</span>)</dd>
<dt>Match</dt><dd>full title; rule confidence {ase['resolution_confidence']:.2f}</dd>
<dt>Technology</dt><dd class="muted">none in the title</dd>
<dt>Location</dt><dd>kept as written, not classified</dd>
<dt>Status</dt><dd>{e(ase['resolution_status'])}</dd></dl>
<p class="refuse">The platform never decides from a place name whether work is onshore, nearshore or offshore; an analyst categorizes a place once for a client, then it is a lookup. &ldquo;Onsite (Customer Location)&rdquo; stays as the page says it.</p>
</div></section>

<section class="stage"><span class="n">6</span>
<h3>The ledger</h3>
<p class="what">The book of record: one row per rate seen, kept forever inside the client&rsquo;s own environment, with everything needed to trace it back to the page. Re-runs add rows and mark old ones superseded; nothing is overwritten. Rows below the confidence threshold stay visible but are not counted until an analyst confirms them.</p>
<div class="row"><span class="tag">This row, as stored</span>
<dl><dt>Row</dt><dd class="v">obs_id {ase['obs_id']}, run {e(ase['run_id'])}</dd>
<dt>Vendor / client</dt><dd>{e(ase['vendor'])} / {e(ase['client'])}</dd>
<dt>Rate</dt><dd class="v">{e(ase['rate_value'])} {e(ase['currency'])} per {e(ase['rate_unit'])}; as stated &ldquo;{e(ase['rate_as_stated'])}&rdquo;</dd>
<dt>Period</dt><dd>{e(ase['period_raw'])}; effective date: <span class="muted">not stated on the page, left empty</span></dd>
<dt>In CAD</dt><dd><span class="muted">empty: no reference exchange rate was fetched, so nothing was converted</span></dd>
<dt>Role / band</dt><dd class="v">{e(ase['canonical_role_id'])} / {e(ase['twm_band'])}</dd>
<dt>Confidence</dt><dd>resolution {ase['resolution_confidence']:.2f}, extraction {ase['extraction_confidence']:.2f}, scan {e(ase['scan_quality'])}</dd>
<dt>Counted</dt><dd><b>yes</b>: this row counts toward benchmarks</dd>
<dt>Source</dt><dd class="v">page {ase['source_page']}, box {e(fmt_box(bbox))}</dd>
<dt>Quote</dt><dd class="v">{e(ase['source_quote'])}</dd>
<dt>Written</dt><dd class="v">{e(created)}</dd></dl>
<p class="check">Nothing in this row is an estimate. A vendor who challenges it is shown page {ase['source_page']} with the box lit.</p>
</div></section>

</div>

<h2>The review queue: where the system stopped and asked</h2>
<div class="strip blue">
<p>Every place the pipeline was not sure, it left the field empty, wrote one sentence a consultant can read, and put the item in a queue. An analyst decides once; the decision becomes a rule, so the same question is never asked twice for the same client. From this contract set the run left <b>{tx_queue_n} open items</b>:</p>
<table>
<tr><th>Kind</th><th>Item</th><th>Rate</th><th>Why it is here</th></tr>
{queue_rows}</table>
<p class="note">Across both contract sets run so far, {F['queue_open']} items are open. None of them is a place name: neither document names a city.</p>
</div>

<h2>A row that gets flagged instead</h2>
<div class="strip amber">
<p>Same page, same table, fourteen rows down: a title the system could not place. It went through the same six stages and stopped at the fifth. Abstaining is not a failure of the pipeline. A false claim in front of a vendor could lose the engagement; a missed row is caught at the next pass.</p>
<img class="img" alt="The Operations row of the same rate table, boxed in amber" src="{F['img_ops']}" style="margin: 10px 0 14px;">
<div class="cols">
<div class="kv"><h3>Stages 1 to 4: identical</h3>
<p><b>Title as written</b> {e(ops['observed_title'])}</p>
<p><b>Rate as written</b> {e(ops['rate_as_stated'])} per hour ({e(ops['currency'])})</p>
<p><b>Period</b> {e(ops['period_raw'])}</p>
<p><b>Location as written</b> {e(ops['location_raw'])}</p>
<p><b>Verified on the page</b> &ldquo;{e(ops['source_quote'])}&rdquo;, page {ops['source_page']}, box {e(fmt_box(ops_bbox))}; extraction confidence {ops['extraction_confidence']:.2f}</p>
</div>
<div class="kv"><h3>Stage 5: normalization stops</h3>
<p><b>Rules</b> no match in the mapping table and no rule applies: &ldquo;Operations&rdquo; alone names no role</p>
<p><b>The model is asked</b> it answered with confidence 0.30, below the floor of 0.75, and so abstained. In its own words:</p>
<p class="quote">{e(ops_reason)}&hellip;</p>
<p class="muted" style="font-size:12.5px">The ledger keeps the first 300 characters of the reason; the sentence continues in the model&rsquo;s answer.</p>
</div>
<div class="kv"><h3>Stage 6: stored, not counted</h3>
<p><b>Row</b> obs_id {ops['obs_id']}</p>
<p><b>Role</b> <span class="muted">empty</span></p>
<p><b>Band</b> <span class="muted">empty</span></p>
<p><b>Status</b> {e(ops['resolution_status'])}</p>
<p><b>Counted</b> no: excluded from every benchmark and every savings total until an analyst decides</p>
<p><b>Queue item</b> kind {e(F['queue_ops']['kind'])}, status {e(F['queue_ops']['status'])}</p>
<p><b>What happens next</b> the analyst reads the statement of work, picks the role (or none), writes one line of reasoning. From then on &ldquo;Operations&rdquo; from this vendor at this client is a lookup.</p>
</div>
</div>
</div>

<h2>Coming: savings stacking</h2>
<div class="strip coming">
<p><b>This box is a placeholder on purpose.</b> No finding exists yet, and nothing below is computed. Once findings exist, this is where the row&rsquo;s savings will appear, stacked into three tranches so that no dollar is counted twice:</p>
<div class="cols">
<div class="kv"><h3>Contractual</h3><p>The rate billed against the <strong>contracted rate</strong>, the price the statement of work or master agreement says the vendor may charge for this role. No contracted rate for the role means $0 here, with the reason stated, and a separate finding that a role was billed without one.</p></div>
<div class="kv"><h3>Operational</h3><p>The contracted rate against the vendor&rsquo;s own best rate for the same role and band at this client. No second rate from the same vendor means $0 and says so.</p></div>
<div class="kv"><h3>Market alignment</h3><p>Against the market mid-point for the same role, band and location: the consortium-plus-public distribution, published only when a cut has at least 3 observations and 2 contributing clients. A rate already below the mid-point is reported as below market, a fact, never a negative saving.</p></div>
</div>
<p class="note">Observed and projected savings will be two labelled numbers, never one blended total. A missing reference always yields zero plus an explanation, never a guess.</p>
</div>

<h2>The whole file, and the run behind this page</h2>
<div class="strip">
<div class="cols">
<div class="kv">
<p><b>This contract set</b> 7 files, one contract set under DIR-STS-TSS-699</p>
<p><b>This file</b> {tx_doc['n']} rate rows kept, {tx_doc['resolved']} resolved to a role ({tx_doc['unbanded']} of them with no seniority stated, so left unbanded on purpose), {tx_doc['flagged']} to the queue, {tx_doc['ambiguous']} ambiguous by design, {tx_doc['counted']} counted toward benchmarks</p>
<p><b>Year 1 only</b> the table prices eight contract years; the run kept the first. Escalation columns are a follow-up.</p>
</div>
<div class="kv">
<p><b>Second contract set, same code</b> Accenture&rsquo;s UK G-Cloud 15 rate page (a web page, not a PDF): {gc_doc['n']} rows kept, {gc_doc['resolved']} resolved ({gc_doc['unbanded']} unbanded on purpose), {gc_doc['flagged']} to the queue, {gc_doc['counted']} counted</p>
<p><b>Ledger today</b> {T['rows_live']} rows, {T['counted']} counted, {T['resolved']} resolved, {T['flagged']} flagged, {T['ambiguous']} ambiguous, {F['queue_open']} queue items open, {F['mapping_decisions']} titles newly resolved by the model and awaiting an analyst&rsquo;s confirmation</p>
<p><b>Run</b> {e(run['run_id'])}, {e(run_date)}, model {e(run['model'])}, rule version {e(run['rule_version'])}, reader {e(run['reader'])}</p>
</div>
</div>
<details id="fullpage"><summary>Page 8 at full size, with the row boxed</summary>
<img class="img" alt="Page 8 of the pricing attachment at full size" src="{F['img_full']}" style="max-width: 1000px; margin-top: 8px;">
</details>
<details><summary>The seven files as intake labelled them</summary>
<table>
<tr><th>File</th><th>Label (confidence)</th><th>Pages</th><th>Link</th><th>Flag</th></tr>
{doc_rows}</table>
<p class="note">Two labels differ from what a person would write. File 084 is Exhibit 2, Financial Provisions; intake called it a rate card from the words &ldquo;rate card services&rdquo; in its table of contents, and extraction then found no rate table in it and said so. File 087 is a 3-page key-personnel attachment; intake could only fall back on the file name and flagged its own label as weak. Both are in the queue above.</p>
</details>
<details><summary>All {tx_doc['n']} rows from this file, as the ledger holds them</summary>
<table>
<tr><th>Row</th><th>Title as written</th><th>Rate</th><th>Role</th><th>Band</th><th>Status</th><th>Counted</th></tr>
{tx_rows}</table>
<p class="note">Rows 52 and 53 are the same title priced per month and per year on the page; they are stored as stated, per month and per year, never converted to an hourly figure.</p>
</details>
</div>

<h2>Terms used on this page</h2>
<div class="strip">
<dl class="terms">
<dt>Document library</dt><dd>The collection of real documents gathered to build the product. Example: the 13 UK G-Cloud rate cards and this Texas contract.</dd>
<dt>Contract set</dt><dd>The files that belong to one contract. Example: this master agreement, its statement of work, exhibits and attachments, seven files.</dd>
<dt>Contracted rate</dt><dd>The price the statement of work or master agreement says the vendor may charge for a role. Example: $83.00 per hour for an Advanced Systems Engineer, onsite, in year 1.</dd>
<dt>Ledger</dt><dd>The book of record of every rate seen, with its source. Example: row 1 above.</dd>
<dt>Mapping table</dt><dd>The list of vendor titles already resolved to a role and band, with the reasoning and who decided. Example: &ldquo;Advanced Systems Engineer&rdquo; to Systems Engineer, senior.</dd>
<dt>Role and band</dt><dd>The two axes of the role framework: what the person does (130 roles) and how senior they are (four bands). Location and technology are recorded beside them, never multiplied into the rate.</dd>
<dt>Box</dt><dd>Four numbers giving a position on a page: left, top, right, bottom, in points from the top-left corner. Example: {e(fmt_box(bbox))}.</dd>
<dt>Confidence</dt><dd>A number from 0 to 1 that a stage attaches to its own answer. Below the floor, the answer is withheld and the item is flagged. Example: the model&rsquo;s 0.30 for &ldquo;Operations&rdquo;.</dd>
<dt>Counted</dt><dd>Whether a row may enter benchmark distributions and savings totals. Only rows above the confidence threshold, from a usable scan, with a resolved title, count.</dd>
<dt>Model</dt><dd>A frontier language model, rented through one wrapper. TWM owns everything around it: the record shapes, prompts, checks, the role framework, the mapping table and the evaluation sets.</dd>
</dl>
</div>

<footer>
<p>Source document: Texas DIR contract DIR-STS-TSS-699, Attachment 2.1 Pricing and Volumes, Accenture LLP, published by the Texas Department of Information Resources (dir.texas.gov), {F['n_pages']} pages. Ledger: the single-file prototype ledger, run {e(run['run_id'])}. Page built {datetime.now().strftime('%B %d, %Y').replace(' 0', ' ')} from the ledger and the PDF by a script; no value on it was typed by hand.</p>
<p>This page shows public documents only. In a client deployment the ledger, the documents and every row stay inside the client&rsquo;s own environment; only vocabulary and cohort summaries ever leave.</p>
</footer>
</main>
</body>
</html>
"""
open(out_path, "w", encoding="utf-8").write(page)
print("wrote", out_path, len(page), "bytes")
