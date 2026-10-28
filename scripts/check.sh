#!/usr/bin/env bash
# Checks every plugin in index.toml: the file exists and is executable, and `describe` prints
# protocol-1 JSON whose id matches the index. Needs python3 for the TOML and JSON parsing.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 - <<'PY'
import json, os, subprocess, sys, tomllib

with open("index.toml", "rb") as f:
    index = tomllib.load(f)
failed = False
for plugin in index["plugin"]:
    path, problems = plugin["file"], []
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
    if not os.path.basename(path) == f"repoke-{plugin['id']}":
        problems.append(f"file should be named repoke-{plugin['id']}")
    print(("ok  " if not problems else "FAIL"), plugin["id"], "; ".join(problems))
    failed |= bool(problems)
sys.exit(1 if failed else 0)
PY
