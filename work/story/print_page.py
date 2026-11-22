import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
s = s.replace("<details>", "<details open>").replace('<details id="fullpage">', '<details id="fullpage" open>')
extra = """
@page { size: Letter; margin: 10mm 9mm; }
@media print {
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  main { max-width: none; padding: 0; zoom: 0.82; }
  .flow { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
  .stage, .strip { break-inside: auto; }
  tr, img, .kv, .rule { break-inside: avoid; }
  h2 { break-after: avoid; margin-top: 20px; }
  summary { display: none; }
  details { margin-top: 10px; }
  .cols { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
"""
s = s.replace("</style>", extra + "</style>", 1)
open(dst, "w", encoding="utf-8").write(s)
print("print copy written")
