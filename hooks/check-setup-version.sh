#!/usr/bin/env bash
#
# check-setup-version.sh — SessionStart hook. /addit-harness:setup copies
# CLAUDE.md/AGENTS.md/rules/references/settings.json out of the plugin into
# ~/.claude (or a project) at run time — the plugin loader doesn't auto-sync
# those, so they go stale silently once the plugin updates. This hook
# compares a content hash of just those files against the marker setup.sh
# writes each time it runs, and reminds the user to re-run it on a mismatch.
#
# Deliberately content-hash-based, not plugin-version-based: most version
# bumps only touch agents/skills/hooks, which the plugin loader already
# serves live and need no re-sync — comparing versions would nag on every
# release regardless of whether it touched anything this skill copies.
#
# Silent if setup was never run for a given scope (no marker) — that's an
# opt-in the user hasn't made, not our place to nag about.
set -uo pipefail  # no -e: this must never abort a session start over a stray failure

cat >/dev/null  # consume the hook's stdin JSON payload; nothing here needs it

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
[[ -z "$PLUGIN_ROOT" ]] && exit 0

# Keep this hashing logic identical to the copy in skills/setup/scripts/setup.sh.
setup_content_hash() {
  python3 -c "
import hashlib, pathlib, sys
root = pathlib.Path(sys.argv[1])
paths = [root / n for n in ('CLAUDE.md', 'AGENTS.md', 'settings.json')]
for sub in ('rules', 'references'):
    d = root / sub
    if d.is_dir():
        paths.extend(d.rglob('*'))
h = hashlib.sha256()
for p in sorted({p for p in paths if p.is_file()}):
    h.update(str(p.relative_to(root)).encode())
    h.update(p.read_bytes())
print(h.hexdigest())
" "$1"
}

CURRENT_HASH="$(setup_content_hash "$PLUGIN_ROOT")"
[[ -z "$CURRENT_HASH" ]] && exit 0

PLUGIN_VERSION="$(python3 -c "
import json
print(json.load(open('$PLUGIN_ROOT/.claude-plugin/plugin.json'))['version'])
" 2>/dev/null)"

MESSAGES=()

check_marker() {
  local marker="$1" scope="$2" synced_hash synced_version
  [[ -f "$marker" ]] || return 0
  synced_hash="$(sed -n '1p' "$marker" 2>/dev/null)"
  synced_version="$(sed -n '2p' "$marker" 2>/dev/null)"
  if [[ -n "$synced_hash" && "$synced_hash" != "$CURRENT_HASH" ]]; then
    MESSAGES+=("addit-harness's CLAUDE.md/AGENTS.md/rules/references/settings.json changed since your $scope-scope /addit-harness:setup last ran (synced from v${synced_version:-unknown}, plugin is now v${PLUGIN_VERSION:-unknown}) — run /addit-harness:setup to pick up the changes.")
  fi
}

check_marker "$HOME/.claude/.addit-harness-setup-version" "global"
[[ -n "${CLAUDE_PROJECT_DIR:-}" ]] && check_marker "$CLAUDE_PROJECT_DIR/.claude/.addit-harness-setup-version" "project"

if [[ ${#MESSAGES[@]} -eq 0 ]]; then
  exit 0
fi

NOTICE="$(printf '%s\n' "${MESSAGES[@]}")"
python3 -c "
import json, sys
notice = sys.stdin.read()
print(json.dumps({
    'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': notice},
    'systemMessage': notice,
}))
" <<< "$NOTICE"
exit 0
