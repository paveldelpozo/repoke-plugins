#!/usr/bin/env python3
"""Writes each plugin's `downloads` (all its versions in the `files` release) and `votes` (upvotes
on its Discussion) into index.toml, for `repoke plugin search` and the landing. Needs `gh`."""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import indexfile  # noqa: E402
from publish import RELEASE, REPO, gh  # noqa: E402


def downloads():
    data = json.loads(gh("release", "view", RELEASE, "-R", REPO, "--json", "assets"))
    totals = {}
    for asset in data["assets"]:
        match = re.fullmatch(r"repoke-(.+)-[0-9a-f]{12}", asset["name"])
        if match:
            totals[match.group(1)] = totals.get(match.group(1), 0) + asset["downloadCount"]
    return totals


def votes(url):
    number = int(url.rstrip("/").rsplit("/", 1)[1])
    owner, name = REPO.split("/")
    query = """query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) { discussion(number: $number) { upvoteCount } }
    }"""
    out = json.loads(gh(
        "api", "graphql", "-f", f"query={query}", "-f", f"owner={owner}", "-f", f"name={name}",
        "-F", f"number={number}",
    ))
    return out["data"]["repository"]["discussion"]["upvoteCount"]


def main():
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    counted = downloads()
    fields = {}
    for plugin in indexfile.load()["plugin"]:
        stats = {"downloads": counted.get(plugin["id"], 0)}
        if plugin.get("discussion"):
            stats["votes"] = votes(plugin["discussion"])
        fields[plugin["id"]] = stats
        print(plugin["id"], stats)
    indexfile.set_fields(fields)


if __name__ == "__main__":
    main()
