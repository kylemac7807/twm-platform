#!/usr/bin/env python3
"""Recover Texas DIR documents served through the Widen CDN viewer.

v3_download.py saves txdir.widen.net URLs as-is, but those return an HTML *viewer page*
(saved with a .pdf extension), not the PDF. The viewer page embeds a short-lived signed
URL on previews.*.widencdn.net that serves the real PDF. This script finds every file in
v3_downloads/ whose name ends .pdf but whose content is HTML, refetches the viewer page
for a fresh signature, downloads the real PDF, and overwrites the bogus file.

Run from corpus/manifests:   python ../scripts/widen_recover.py
Re-runnable: files that already start with %PDF are left alone.
"""
import csv, html, os, re, sys, time, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
OUT = "v3_downloads"
PREVIEW_RE = re.compile(r'https://previews[^"\'\s<>\\]+?/pdf/[^"\'\s<>\\]+')


def get(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main():
    fixed, failed = [], []
    for folder in ("v3_gov", "v3_edgar", "v3_invoices"):
        rows = list(csv.DictReader(open(os.path.join(folder, "manifest.csv"), newline="", encoding="utf-8")))
        d = os.path.join(OUT, folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.lower().endswith(".pdf"):
                continue
            path = os.path.join(d, name)
            with open(path, "rb") as f:
                if f.read(4) == b"%PDF":
                    continue
            idx = int(name.split("_", 1)[0])
            url = rows[idx - 1]["url"].strip()
            try:
                page = get(url).decode("utf-8", "ignore")
                m = PREVIEW_RE.search(page)
                if not m:
                    raise ValueError("no preview pdf link in viewer page")
                pdf = get(html.unescape(m.group(0)))
                if not pdf.startswith(b"%PDF"):
                    raise ValueError("preview link did not return a PDF")
                with open(path, "wb") as o:
                    o.write(pdf)
                fixed.append((name, len(pdf)))
                print(f"  ok  {len(pdf)//1024:6} KB  {name}")
                time.sleep(1.0)
            except Exception as e:  # noqa: BLE001
                failed.append((folder, url, name, str(e)[:100]))
                print(f"  FAIL {name}: {e}")
    print(f"\nrecovered {len(fixed)}, failed {len(failed)}")
    if failed:
        with open(os.path.join(OUT, "widen_failures.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["manifest", "url", "dest", "error"]); w.writerows(failed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
