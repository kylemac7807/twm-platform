# Pull every number the page shows straight from the ledger and the PDF, into one JSON file.
import sys, json, sqlite3, base64, pdfplumber
from PIL import ImageDraw
db, pdf_path, img_dir, out = sys.argv[1:5]
con = sqlite3.connect(db); con.row_factory = sqlite3.Row
q = lambda s, a=(): [dict(r) for r in con.execute(s, a)]
F = {}
F["runs"] = q("select * from runs order by started_at")
F["documents"] = q("select document_id, filename, true_type, doc_class, class_confidence, contract_numbers, family_id, readiness, record_json from documents order by filename")
F["ase"] = q("select * from observations where observed_title='Advanced Systems Engineer' and superseded_by is null")[0]
F["ops"] = q("select * from observations where observed_title='Operations' and superseded_by is null")[0]
F["queue_ops"] = q("select * from review_queue where item='Operations'")[0]
F["queue_084"] = q("select * from review_queue where kind='extraction'")[0]
F["queue_087"] = q("select * from review_queue where kind='intake'")[0]
F["queue_counts"] = q("select kind, count(*) n from review_queue where status='open' group by kind")
F["texas"] = q("select obs_id, observed_title, rate_as_stated, canonical_role_id, twm_band, resolution_status, resolution_confidence, counted, source_bbox from observations where document_id=? and superseded_by is null order by obs_id", (F["ase"]["document_id"],))
F["totals"] = q("select count(*) rows_live, sum(counted) counted, sum(case when resolution_status='resolved' then 1 else 0 end) resolved, sum(case when resolution_status='flagged' then 1 else 0 end) flagged, sum(case when resolution_status='ambiguous' then 1 else 0 end) ambiguous, sum(case when twm_band is null and resolution_status='resolved' then 1 else 0 end) unbanded from observations where superseded_by is null")[0]
F["per_doc"] = q("select document_id, count(*) n, sum(counted) counted, sum(case when resolution_status='resolved' then 1 else 0 end) resolved, sum(case when twm_band is null and resolution_status='resolved' then 1 else 0 end) unbanded, sum(case when resolution_status='flagged' then 1 else 0 end) flagged, sum(case when resolution_status='ambiguous' then 1 else 0 end) ambiguous from observations where superseded_by is null group by document_id")
F["queue_open"] = q("select count(*) n from review_queue where status='open'")[0]["n"]
F["mapping_decisions"] = q("select count(*) n from mapping_decisions")[0]["n"]
# the page images
S = 2.0
with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[7]
    F["page_size"] = [page.width, page.height]
    F["n_pages"] = len(pdf.pages)
    base = page.to_image(resolution=72*S).original.convert("RGB")
    def boxed(bbox, color, scale):
        im = page.to_image(resolution=72*scale).original.convert("RGB"); d = ImageDraw.Draw(im)
        x0, top, x1, bottom = bbox
        d.rectangle([x0*scale-3, top*scale-3, x1*scale+3, bottom*scale+3], outline=color, width=4 if scale < 3 else 5)
        return im
    ase_bbox = json.loads(F["ase"]["source_bbox"]); ops_bbox = json.loads(F["ops"]["source_bbox"])
    full = boxed(ase_bbox, (198, 40, 40), S); full.save(img_dir + "/page8_full.png")
    thumb = boxed(ase_bbox, (198, 40, 40), 1.0); thumb.save(img_dir + "/page8_thumb.png")
    S4 = 4.0
    c = boxed(ase_bbox, (198, 40, 40), S4).crop((int(60*S4), int(98*S4), int(560*S4), int(150*S4))); c.save(img_dir + "/page8_ase.png")
    c2 = boxed(ops_bbox, (214, 120, 0), S4).crop((int(60*S4), int((ops_bbox[1]-14)*S4), int(560*S4), int((ops_bbox[3]+14)*S4))); c2.save(img_dir + "/page8_ops.png")
    # title cell + rate cell only, large
    c3 = boxed(ase_bbox, (198, 40, 40), 6.0).crop((int(60*6), int((ase_bbox[1]-5)*6), int(240*6), int((ase_bbox[3]+5)*6))); c3.save(img_dir + "/page8_cells.png")
def b64(p):
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
F["img_thumb"] = b64(img_dir + "/page8_thumb.png"); F["img_full"] = b64(img_dir + "/page8_full.png"); F["img_ase"] = b64(img_dir + "/page8_ase.png"); F["img_ops"] = b64(img_dir + "/page8_ops.png"); F["img_cells"] = b64(img_dir + "/page8_cells.png")
json.dump(F, open(out, "w", encoding="utf-8"), indent=1, default=str)
print({k: (len(v) if isinstance(v, (list, str)) else v) for k, v in F.items() if not k.startswith("img")})
print("images bytes", sum(len(F[k]) for k in F if k.startswith("img")))
