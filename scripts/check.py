#!/usr/bin/env python3
"""Check that the page, the agent rules and the asset manifest agree with tokens.json.

Run from the project root:  python3 scripts/check.py
Exit code 1 lists every mismatch.
"""
import json, re, sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"
tokens = json.loads((WEB / "tokens.json").read_text())

def values(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from values(v)
    elif isinstance(node, str):
        yield from re.findall(r"#[0-9A-Fa-f]{6}\b", node)

allowed = {h.upper() for h in values(tokens)}
# hexes that may appear only as warnings or history: named in the rules as "never use", or noted as outdated
mentioned_only = {"#8A8A8F", "#E6E6E8", "#000000", "#98F048"}
problems = []

def check_hexes(name, text):
    for h in sorted({h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}\b", text)}):
        if h not in allowed and h not in mentioned_only:
            problems.append(f"{name}: {h} is not in tokens.json")
    for m in re.findall(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", text):
        h = "#%02X%02X%02X" % tuple(map(int, m))
        if h not in allowed:
            problems.append(f"{name}: rgba colour {h} is not in tokens.json")

for page in ("index.html", "marker.html", "blob.html", "dots.html", "3d.html", "page.css", "nav.js", "labs/canvas.html", "labs/line-lab.html", "labs/ui/badges.js"):
    check_hexes(page, (WEB / page).read_text())
check_hexes("brand.md", (WEB / "brand.md").read_text())
# every local link and image in the pages and in llms.txt / brand.md resolves to a file
for page in ("index.html", "marker.html", "blob.html", "dots.html", "3d.html", "llms.txt", "brand.md"):
    text = (WEB / page).read_text()
    refs = re.findall(r'(?:src|href|poster|data-src)="([^"#?:]+)', text) + re.findall(r'\]\(([^)#?:]+)\)', text) + re.findall(r'`((?:assets|labs)/[^`*<>]+?\.(?:svg|png|webp|webm|mov|html|json|js))`', text)
    for r in refs:
        if r.startswith(("http", "mailto")) or r.endswith("/"): continue
        if page == "3d.html" and r.endswith("ring-swirl") or r.endswith("icon-spin"): r += ".webm"   # the video's base name, the page adds the format
        if not (WEB / r).exists(): problems.append(f"{page}: broken reference {r}")

manifest = json.loads((WEB / "assets" / "manifest.json").read_text())
def files(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("svg", "png", "webp", "webm", "mov", "poster", "woff2", "file") and isinstance(v, str):
                yield v
            else:
                yield from files(v)
    elif isinstance(node, list):
        for v in node:
            yield from files(v)
for f in files(manifest):
    if f.startswith("http"): continue   # videos live on Cloudflare R2 (checked by hand: curl -I)
    if not (WEB / f).exists():
        problems.append(f"manifest.json: missing file {f}")
check_hexes("manifest.json", json.dumps(manifest))

# every inline script parses (node --check): a stray comment once swallowed a line's end and blanked a page
import subprocess, tempfile, shutil
if shutil.which("node"):
    for page in ("index.html", "marker.html", "blob.html", "dots.html", "3d.html", "labs/canvas.html", "labs/line-lab.html"):
        if not (WEB / page).exists(): continue   # the shared copy carries only some of the labs
        for i, js in enumerate(re.findall(r"<script(?![^>]*src)[^>]*>(.*?)</script>", (WEB / page).read_text(), re.S)):
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as t: t.write(js)
            r = subprocess.run(["node", "--check", t.name], capture_output=True, text=True)
            if r.returncode: problems.append(f"{page}: script {i} does not parse: {r.stderr.strip().splitlines()[-1]}")

if problems:
    print("\n".join(problems)); sys.exit(1)
print(f"ok: {len(allowed)} token colours, page, rules and {len(list(files(manifest)))} asset files agree")
