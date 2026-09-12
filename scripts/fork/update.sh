#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../.."
[[ -z "$(git status --porcelain)" ]] || { echo 'Commit or stash changes before updating.' >&2; exit 1; }
git fetch upstream --tags
# main is only the upstream mirror. Refuse to discard any accidental owner work.
git merge-base --is-ancestor main upstream/main || { echo 'main diverged from upstream; review it manually.' >&2; exit 1; }
git branch -f main upstream/main
branch="update/upstream-$(git rev-parse --short upstream/main)"
git switch -c "$branch" ios-hr-apple
git merge --no-edit upstream/main
git submodule update --init --recursive deps/ish
python3 scripts/fork/localize.py
printf '%s\n' "Review $branch, rebuild changed native dependencies, run scripts/fork/build.py and the FORK.md device checks. Merge into ios-hr-apple only after validation."
