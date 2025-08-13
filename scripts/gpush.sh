#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-ai/feature-$(date +%Y%m%d-%H%M%S)}"
MSG="${2:-chore: automated update}"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "run from repo root"; exit 1; }

git checkout -B "$BRANCH"
git add -A
if git diff --cached --quiet; then
  echo "no staged changes; nothing to commit"
  exit 0
fi

git commit -m "$MSG"
git push -u origin "$BRANCH"

gh pr create --title "$MSG" --body "Automated PR by Manus." --head "$BRANCH" --base main

