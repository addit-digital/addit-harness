#!/usr/bin/env bash
# changelog-section.sh — print the body of one "## [<name>]" section of CHANGELOG.md
# (heading excluded; surrounding blank lines and trailing "[label]: url" link
# references trimmed). A "## [" line inside a fenced code block does not end the
# section. A leading "v" on the heading or on <name> is ignored ("## [v1.2.3]"
# matches 1.2.3). Used by release.yml (release notes, and the guard that blocks a
# release with no Unreleased notes) and deploy-docs.yml (the docs changelog page).
#
# Usage: changelog-section.sh [--require-nonempty] <version|Unreleased> [CHANGELOG.md]
# Exit:  0 section found (printed; empty output is allowed unless --require-nonempty)
#        1 file or section missing, or --require-nonempty and the section is empty
set -euo pipefail

require=0
if [[ "${1:-}" == "--require-nonempty" ]]; then require=1; shift; fi
want="${1:?usage: changelog-section.sh [--require-nonempty] <version|Unreleased> [file]}"
file="${2:-CHANGELOG.md}"
[[ -f "$file" ]] || { echo "changelog-section: $file not found" >&2; exit 1; }

body="$(awk -v want="$want" '
  function norm(s) { sub(/^v/, "", s); return s }
  /^ ? ? ?(```|~~~)/ { if (!infence) { infence = 1; fence = substr($0, match($0, /(```|~~~)/), 3) } else if (index($0, fence)) infence = 0 }
  !infence && /^## \[/ {
    if (found) exit
    name = $0
    sub(/^## \[/, "", name)
    sub(/\].*$/, "", name)
    if (norm(name) == norm(want)) { found = 1; next }
  }
  found { lines[++n] = $0 }
  END {
    if (!found) exit 2
    first = 1; while (first <= n && lines[first] ~ /^[[:space:]]*$/) first++
    last = n;  while (last >= first && (lines[last] ~ /^[[:space:]]*$/ || lines[last] ~ /^\[[^]]+\]:[[:space:]]/)) last--
    for (i = first; i <= last; i++) print lines[i]
  }
' "$file")" || { echo "changelog-section: no '## [$want]' section in $file" >&2; exit 1; }

if [[ -z "$body" ]]; then
  [[ $require -eq 1 ]] && { echo "changelog-section: '## [$want]' in $file is empty" >&2; exit 1; }
  exit 0
fi
printf '%s\n' "$body"
