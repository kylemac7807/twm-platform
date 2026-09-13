#!/usr/bin/env python3
"""TWM Corpus v3 downloader — fetches ORIGINAL documents from the three v3 manifests.

Run on a machine with normal internet access, from the folder containing
v3_edgar/, v3_gov/, v3_invoices/:   python3 v3_download.py
Downloads land in v3_downloads/<source>/, named by row number + slug.
Re-runnable: existing non-empty files are skipped. Failures are listed at the
end and in v3_downloads/failures.csv — retry those manually in a browser
(several government CDNs block scripted clients but serve browsers fine).
"""
import csv, os, re, sys, time, urllib.request

MANIFESTS = [("v3_edgar", "url"), ("v3_gov", "url"), ("v3_invoices", "url")]
UA = "TWM research corpus build (kylefmcnamara@gmail.com)"  # SEC requires a descriptive UA
OUT = "v3_downloads"

def slug(row, i):
    bits = [row.get(k, "") for k in ("filer", "counterparty", "buyer", "vendor", "source_venue", "parties", "doc_type")]
    s = re.sub(r"[^A-Za-z0-9]+", "_", "_".join(b for b in bits if b))[:80].strip("_") or "doc"
    return f"{i:03d}_{s}"

def ext_of(url):
    m = re.search(r"\.(pdf|htm|html|docx?|xlsx?|zip|txt)(?:$|\?)", url.lower())
    return "." + m.group(1) if m else ".bin"

failures = []
total = ok = skipped = 0
for folder, urlcol in MANIFESTS:
    path = os.path.join(folder, "manifest.csv")
    if not os.path.exists(path):
        print(f"!! missing {path}, skipping"); continue
    os.makedirs(os.path.join(OUT, folder), exist_ok=True)
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), 1):
            url = (row.get(urlcol) or "").strip()
            if not url.startswith("http"): continue
            total += 1
            dest = os.path.join(OUT, folder, slug(row, i) + ext_of(url))
            if os.path.exists(dest) and os.path.getsize(dest) > 500:
                skipped += 1; continue
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as o:
                    o.write(r.read())
                head = open(dest, "rb").read(300).lower()
                if os.path.getsize(dest) < 500 or b"<title>error" in head or b"access denied" in head:
                    raise ValueError("looks like an error page")
                ok += 1
                if "sec.gov" in url: time.sleep(0.15)  # SEC rate courtesy
            except Exception as e:
                failures.append((folder, url, str(e)[:120]))
                if os.path.exists(dest): os.remove(dest)
            if total % 25 == 0: print(f"  ...{total} processed ({ok} ok)")

print(f"\nDone: {ok} downloaded, {skipped} already present, {len(failures)} failed of {total}.")
if failures:
    with open(os.path.join(OUT, "failures.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["manifest", "url", "error"]); w.writerows(failures)
    print(f"Failures listed in {OUT}/failures.csv — most are CDNs that require a normal browser; open those URLs manually.")
