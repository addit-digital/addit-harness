#!/usr/bin/env bash
# changelog-release.sh — cut a release in CHANGELOG.md: rename "## [Unreleased]" to
# "## [<version>] - <date>" and put a fresh, empty "## [Unreleased]" above it. The
# heading is matched outside fenced code blocks only. Run by release.yml as part of
# the version-bump commit, after changelog-section.sh --require-nonempty Unreleased
# has confirmed there is something to release.
#
# Usage: changelog-release.sh <version> <YYYY-MM-DD> [CHANGELOG.md]
set -euo pipefail

version="${1:?usage: changelog-release.sh <version> <date> [file]}"
date="${2:?usage: changelog-release.sh <version> <date> [file]}"
file="${3:-CHANGELOG.md}"
[[ -f "$file" ]] || { echo "changelog-release: $file not found" >&2; exit 1; }

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
awk -v version="$version" -v date="$date" '
  /^ ? ? ?(```|~~~)/ { if (!infence) { infence = 1; fence = substr($0, match($0, /(```|~~~)/), 3) } else if (index($0, fence)) infence = 0 }
  !infence && !done && /^## \[Unreleased\]/ {
    print "## [Unreleased]"; print ""; print "## [" version "] - " date; done = 1; next
  }
  { print }
  END { if (!done) exit 2 }
' "$file" > "$tmp" || { echo "changelog-release: no '## [Unreleased]' section in $file" >&2; exit 1; }
cat "$tmp" > "$file"
