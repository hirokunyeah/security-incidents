"""Fetch the latest ledger bundle published to Google Drive and rebuild the site.

The daily Claude task uploads ledger-data-YYYY-MM-DD.json to a public Drive folder
and writes its file id (A1), date (B1) and sha256 (C1) into a public pointer sheet.
usage: python3 _build/fetch_and_build.py OUT_DIR
"""
import csv, hashlib, io, json, pathlib, subprocess, sys, tempfile, urllib.request

POINTER = "https://docs.google.com/spreadsheets/d/18V9XpJ7tNDrNe4U7-sGiXFYt1b9RjYzN8jt_7JfvCFI/export?format=csv"
DOWNLOAD = "https://drive.usercontent.google.com/download?id={}&export=download&confirm=t"

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "gh-actions"}), timeout=60) as r:
        return r.read()

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
row = next(csv.reader(io.StringIO(get(POINTER).decode("utf-8"))))
file_id, date, sha = (row + ["", "", ""])[:3]
blob = get(DOWNLOAD.format(file_id.strip()))
if sha.strip() and hashlib.sha256(blob).hexdigest() != sha.strip():
    sys.exit(f"sha256 mismatch for {file_id}")
bundle = json.loads(blob)
if not bundle.get("incidents"):
    sys.exit("bundle has no incidents; refusing to publish an empty ledger")

here = pathlib.Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    page = t / "page.html"
    page.write_text(bundle["page"] if bundle.get("page") else (out / "_build" / "page.html").read_text(encoding="utf-8"), encoding="utf-8")
    (t / "inc.json").write_text(json.dumps({"rows": bundle["incidents"]}, ensure_ascii=False), encoding="utf-8")
    (t / "chg.json").write_text(json.dumps({"rows": bundle.get("changelog", [])}, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(here / "build.py"), str(page), str(t / "inc.json"), str(t / "chg.json"), str(out)], check=True)
    (here / "page.html").write_text(page.read_text(encoding="utf-8"), encoding="utf-8")
print(f"published bundle {file_id} ({date})")
