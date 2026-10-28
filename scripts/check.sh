#!/usr/bin/env bash
# Checks every plugin in index.toml: the file exists and is executable, `describe` prints
# protocol-1 JSON whose id matches the index, its sha256 and `url` are the ones
# scripts/publish.py pinned, and community plugins name their author. Needs python3.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 - <<'PY'
import hashlib, json, os, subprocess, sys, tomllib

with open("index.toml", "rb") as f:
    index = tomllib.load(f)
failed = False
for plugin in index["plugin"]:
    path, problems = plugin["file"], []
    tier = plugin.get("tier", "official")
    folder = {"official": "plugins/", "community": "community/"}.get(tier)
    if folder is None:
        problems.append(f"tier is {tier}, not official or community")
    elif not path.startswith(folder):
        problems.append(f"{tier} plugins live in {folder}")
    if tier == "community" and not plugin.get("author"):
        problems.append("community plugins need an author (GitHub login)")
    if not os.access(path, os.X_OK):
        problems.append("not executable")
    else:
        out = subprocess.run([path, "describe"], capture_output=True, text=True, timeout=10)
        try:
            described = json.loads(out.stdout)
            if described.get("protocol") != 1:
                problems.append(f"protocol {described.get('protocol')}")
            if described.get("id") != plugin["id"]:
                problems.append(f"describes itself as {described.get('id')}")
        except json.JSONDecodeError:
            problems.append("describe printed no JSON")
        digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if plugin.get("sha256") != digest:
            problems.append(f"sha256 is {digest[:12]}…, not the pinned one: review it, then scripts/publish.py {plugin['id']}")
        elif not plugin.get("url", "").endswith(f"/repoke-{plugin['id']}-{digest[:12]}"):
            problems.append(f"url doesn't point at this version: scripts/publish.py {plugin['id']}")
    if not os.path.basename(path) == f"repoke-{plugin['id']}":
        problems.append(f"file should be named repoke-{plugin['id']}")
    print(("ok  " if not problems else "FAIL"), plugin["id"], "; ".join(problems))
    failed |= bool(problems)
sys.exit(1 if failed else 0)
PY
