"""Build the static public site from the ledger's page source and data files.

usage: python3 build.py PAGE_HTML INCIDENTS_JSON CHANGELOG_JSON OUT_DIR
"""
import json, os, sys, datetime, pathlib

page, inc, chg, out = sys.argv[1:5]
here = pathlib.Path(__file__).resolve().parent
tpl = (here / "template.html").read_text(encoding="utf-8")
body = pathlib.Path(page).read_text(encoding="utf-8")

def rows(p):
    d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    return d["rows"] if isinstance(d, dict) else d

incidents, changelog = rows(inc), rows(chg)
latest = max((r.get("date", "") for r in changelog), default="") or \
    max((r.get("first_seen", "") for r in incidents), default="")

html = tpl.replace("<!--PAGE-->", body).replace("<!--UPDATED-->", latest)
o = pathlib.Path(out); (o / "data").mkdir(parents=True, exist_ok=True)
(o / "index.html").write_text(html, encoding="utf-8")
for name, r in (("incidents", incidents), ("changelog", changelog)):
    (o / "data" / f"{name}.json").write_text(json.dumps({"rows": r}, ensure_ascii=False), encoding="utf-8")
(o / ".nojekyll").write_text("")
print(f"built {o}: {len(incidents)} incidents, {len(changelog)} log rows, latest {latest}")
