#!/bin/sh
# End-to-end smoke: build a tiny repo with real git, then map it.
set -eu

SAMPLE=/tmp/smoke-repo
rm -rf "$SAMPLE"
mkdir -p "$SAMPLE/src"
cd "$SAMPLE"
git init -q -b main
git config user.name "Smoke"
git config user.email "smoke@example.com"

printf 'a = 1\nb = 2\nc = 3\n' > src/core.py
git add -A
GIT_AUTHOR_DATE="2026-09-01T09:00:00-05:00" GIT_COMMITTER_DATE="2026-09-01T09:00:00-05:00" \
  git commit -qm "add core"

printf 'a = 1\nb = 2\nc = 3\nd = 4\n' > src/core.py
git add -A
GIT_AUTHOR_DATE="2026-09-02T09:00:00-05:00" GIT_COMMITTER_DATE="2026-09-02T09:00:00-05:00" \
  git commit -qm "extend core"

printf '# smoke\n' > readme.md
git add -A
GIT_AUTHOR_DATE="2026-09-03T09:00:00-05:00" GIT_COMMITTER_DATE="2026-09-03T09:00:00-05:00" \
  git commit -qm "add readme"

echo "== churn =="
repoheat churn "$SAMPLE"
echo "== hotspots =="
repoheat hotspots "$SAMPLE"
echo "== bus-factor =="
repoheat bus-factor "$SAMPLE"
