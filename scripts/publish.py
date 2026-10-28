#!/usr/bin/env python3
"""Publishes the reviewed version of each plugin given: pins its sha256 in index.toml, uploads it
to the `files` release as `repoke-<id>-<sha12>` (GitHub counts its downloads there) and points
`url` at it. `--discussion` also opens the plugin's Discussion, where people vote and comment.

Run it only once a change has been reviewed: repoke installs nothing else. Needs `gh`.

    scripts/publish.py omz vscode
    scripts/publish.py --discussion mycommunityplugin
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import indexfile  # noqa: E402

REPO = "paveldelpozo/repoke-plugins"
RELEASE = "files"
CATEGORY = "Plugins"


def gh(*args, capture=True):
    out = subprocess.run(["gh", *args], capture_output=capture, text=True)
    if out.returncode != 0:
        sys.exit(f"gh {' '.join(args)} failed:\n{out.stderr}")
    return out.stdout


def ensure_release():
    listed = subprocess.run(["gh", "release", "view", RELEASE, "-R", REPO], capture_output=True)
    if listed.returncode != 0:
        notes = "Reviewed plugin files, one asset per version. `repoke plugin install` downloads them from here."
        gh("release", "create", RELEASE, "-R", REPO, "--title", "Plugin files", "--notes", notes, "--latest=false")


def assets():
    data = json.loads(gh("release", "view", RELEASE, "-R", REPO, "--json", "assets"))
    return {a["name"] for a in data["assets"]}


def upload(path, name):
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, name)
        shutil.copyfile(path, copy)
        gh("release", "upload", RELEASE, copy, "-R", REPO)


def open_discussion(plugin):
    owner, name = REPO.split("/")
    query = """query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) { id discussionCategories(first: 25) { nodes { id name } } }
    }"""
    repo = json.loads(gh("api", "graphql", "-f", f"query={query}", "-f", f"owner={owner}", "-f", f"name={name}"))
    repo = repo["data"]["repository"]
    category = next((c["id"] for c in repo["discussionCategories"]["nodes"] if c["name"] == CATEGORY), None)
    if not category:
        sys.exit(f"there is no `{CATEGORY}` Discussion category in {REPO}; create it on GitHub first")
    author = f" by @{plugin['author']}" if plugin.get("author") else ""
    body = (
        f"{plugin['description']}.\n\n"
        f"`repoke plugin install {plugin['id']}`{author}.\n\n"
        "Upvote this discussion if the plugin works for you; comments are for reviews, problems and ideas."
    )
    mutation = """mutation($repo: ID!, $category: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {repositoryId: $repo, categoryId: $category, title: $title, body: $body}) {
        discussion { url }
      }
    }"""
    created = json.loads(gh(
        "api", "graphql", "-f", f"query={mutation}", "-f", f"repo={repo['id']}",
        "-f", f"category={category}", "-f", f"title={plugin['name']} ({plugin['id']})", "-f", f"body={body}",
    ))
    return created["data"]["createDiscussion"]["discussion"]["url"]


def main():
    args = sys.argv[1:]
    discussion = "--discussion" in args
    ids = [a for a in args if not a.startswith("--")]
    if not ids:
        sys.exit(__doc__)
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    plugins = {p["id"]: p for p in indexfile.load()["plugin"]}
    unknown = [i for i in ids if i not in plugins]
    if unknown:
        sys.exit(f"not in index.toml: {', '.join(unknown)}")

    ensure_release()
    present = assets()
    fields = {}
    for plugin_id in ids:
        plugin = plugins[plugin_id]
        digest = hashlib.sha256(open(plugin["file"], "rb").read()).hexdigest()
        name = f"repoke-{plugin_id}-{digest[:12]}"
        if name not in present:
            upload(plugin["file"], name)
        fields[plugin_id] = {
            "sha256": digest,
            "url": f"https://github.com/{REPO}/releases/download/{RELEASE}/{name}",
        }
        if discussion and not plugin.get("discussion"):
            fields[plugin_id]["discussion"] = open_discussion(plugin)
        print(f"published {plugin_id} as {name}")
    indexfile.set_fields(fields)


if __name__ == "__main__":
    main()
