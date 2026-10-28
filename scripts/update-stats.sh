#!/usr/bin/env bash
# Refreshes downloads and votes in index.toml and pushes them; a daily launchd agent on the
# maintainer's Mac runs it. Git goes over HTTPS with gh's login, since a launchd job has no ssh-agent.
set -euo pipefail
cd "$(dirname "$0")/.."

REMOTE=https://github.com/paveldelpozo/repoke-plugins.git
git_gh() { git -c credential.helper= -c 'credential.helper=!gh auth git-credential' "$@"; }

echo "== $(date '+%Y-%m-%d %H:%M')"
if [ -n "$(git status --porcelain)" ]; then
    echo "uncommitted changes in $(pwd), nothing done"
    exit 1
fi
git_gh pull --ff-only --quiet "$REMOTE" main
scripts/stats.py
if git diff --quiet index.toml; then
    echo "stats unchanged"
    exit 0
fi
scripts/check.sh
git commit --quiet -m "chore: update plugin stats" index.toml
git_gh push --quiet "$REMOTE" HEAD:main
echo "pushed"
