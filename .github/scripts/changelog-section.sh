#!/usr/bin/env bash
# changelog-section.sh — print the body of one "## [<name>]" section of CHANGELOG.md
# (heading excluded, surrounding blank lines trimmed). Prints nothing if the section
# is missing or empty. Used by release.yml (release notes) and deploy-docs.yml (the
# docs changelog page).
#
# Usage: changelog-section.sh <version|Unreleased> [CHANGELOG.md]
set -euo pipefail

want="${1:?usage: changelog-section.sh <version|Unreleased> [file]}"
file="${2:-CHANGELOG.md}"
[[ -f "$file" ]] || exit 0

awk -v want="$want" '
  /^## \[/ {
    if (found) exit
    name = $0
    sub(/^## \[/, "", name)
    sub(/\].*$/, "", name)
    if (name == want) { found = 1; next }
  }
  found { lines[++n] = $0 }
  END {
    first = 1; while (first <= n && lines[first] ~ /^[[:space:]]*$/) first++
    last = n;  while (last >= first && lines[last] ~ /^[[:space:]]*$/) last--
    for (i = first; i <= last; i++) print lines[i]
  }
' "$file"
