#!/usr/bin/env bash
# Checks every plugin in index.toml: the file exists and is executable, `describe` prints
# protocol-1 JSON whose id matches the index, and its sha256 is the one pinned in the index.
# `--pin` writes the current sha256 of every file into index.toml: run it only once the change
# has been reviewed, since repoke installs nothing else. Needs python3 for TOML and JSON.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 - "$@" <<'PY'
import hashlib, json, os, re, subprocess, sys, tomllib

with open("index.toml", "rb") as f:
    index = tomllib.load(f)
pin = "--pin" in sys.argv[1:]
digests = {}
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
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if pin:
        digests[plugin["id"]] = digest
    elif plugin.get("sha256") != digest:
        problems.append(f"sha256 is {digest}, the index pins {plugin.get('sha256')}: review it and run --pin")
    print(("ok  " if not problems else "FAIL"), plugin["id"], "; ".join(problems))
    failed |= bool(problems)
if pin:
    # Rewrites only the sha256 line of each [[plugin]] block, keeping comments and order.
    head, *blocks = open("index.toml").read().split("[[plugin]]\n")
    for i, block in enumerate(blocks):
        id = re.search(r'^id = "(.*)"$', block, re.M).group(1)
        block = re.sub(r'^sha256 = ".*"\n', "", block, flags=re.M)
        body, gap = block.rstrip("\n"), block[len(block.rstrip("\n")):]
        blocks[i] = f'{body}\nsha256 = "{digests[id]}"\n' + (gap[1:] if gap else "")
    open("index.toml", "w").write("[[plugin]]\n".join([head, *blocks]))
sys.exit(1 if failed else 0)
PY
