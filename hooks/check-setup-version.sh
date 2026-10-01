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
#
# Also shows a one-line welcome (systemMessage only — never model context) the
# first time per install, in an interactive terminal session: a local marker in
# ${CLAUDE_PLUGIN_DATA}/onboarding/ makes it once, no network, fails open.
set -uo pipefail  # no -e: this must never abort a session start over a stray failure

IN="$(cat)"  # the payload only supplies session ids to the optional local telemetry
tel() { case "${CLAUDE_PLUGIN_OPTION_TELEMETRY_LOCAL:-}" in true|True|1) printf '%s' "$IN" | python3 -S "${CLAUDE_PLUGIN_ROOT}/hooks/telemetry.py" "$@" >/dev/null 2>&1 || true;; esac; }

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
STATE=""  # ok | drift, from the markers; unmanaged/absent are derived below when there is none

check_marker() {
  local marker="$1" scope="$2" synced_hash synced_version
  [[ -f "$marker" ]] || return 0
  synced_hash="$(sed -n '1p' "$marker" 2>/dev/null)"
  synced_version="$(sed -n '2p' "$marker" 2>/dev/null)"
  [[ -n "$synced_hash" && "$synced_hash" == "$CURRENT_HASH" && "$STATE" != drift ]] && STATE=ok
  if [[ -n "$synced_hash" && "$synced_hash" != "$CURRENT_HASH" ]]; then
    STATE=drift
    MESSAGES+=("addit-harness's CLAUDE.md/AGENTS.md/rules/references/settings.json changed since your $scope-scope /addit-harness:setup last ran (synced from v${synced_version:-unknown}, plugin is now v${PLUGIN_VERSION:-unknown}) — run /addit-harness:setup to pick up the changes.")
  fi
}

check_marker "$HOME/.claude/.addit-harness-setup-version" "global"
[[ -n "${CLAUDE_PROJECT_DIR:-}" ]] && check_marker "$CLAUDE_PROJECT_DIR/.claude/.addit-harness-setup-version" "project"

if [[ -z "$STATE" ]]; then
  STATE=absent
  for f in "$HOME/.claude/AGENTS.md" "$HOME/.claude/CLAUDE.md" "$HOME"/.claude/rules/*.md; do
    [[ -f "$f" ]] || continue
    case "${f##*/}" in AGENTS.md|CLAUDE.md) STATE=unmanaged; break;; *) [[ -f "$PLUGIN_ROOT/rules/${f##*/}" ]] && { STATE=unmanaged; break; };; esac
  done
fi
tel setup "$STATE"

# Welcome: once per install, interactive terminal sessions only. CLAUDE_CODE_ENTRYPOINT is `cli` in a terminal and
# `sdk-cli` under `claude -p`; unset means unknown, which shows; the desktop app and IDE integrations use other
# values and are deliberately not shown it. The output is built BEFORE the marker is written, and the marker is
# created exclusively (noclobber) just before printing, so a lost race or an unwritable data dir prints nothing
# instead of repeating every session, and a failure while building the message does not use up the welcome.
WELCOME=""
is_startup() { printf '%s' "$IN" | python3 -c 'import json, sys; sys.exit(0 if json.load(sys.stdin).get("source") == "startup" else 1)' 2>/dev/null; }
welcome_due() {
  [[ "${CLAUDE_CODE_ENTRYPOINT:-cli}" == cli ]] || return 1
  local dir="${CLAUDE_PLUGIN_DATA:-}"
  [[ -n "$dir" && ! -e "$dir/onboarding/welcome-v1" ]] || return 1
  is_startup
}
claim_welcome() {
  local dir="${CLAUDE_PLUGIN_DATA:-}"
  mkdir -p "$dir/onboarding" 2>/dev/null || return 1
  ( set -o noclobber; : > "$dir/onboarding/welcome-v1" ) 2>/dev/null
}
if welcome_due; then
  case "$STATE" in
    ok|drift) WELCOME="addit-harness ready. For anything bigger than a small fix: /addit-harness:dev-flow <what to build>. All tips: /addit-harness:tips";;
    *) WELCOME="addit-harness installed. Run /addit-harness:setup once, then /addit-harness:dev-flow <what to build>. Tips: /addit-harness:tips";;
  esac
fi

if [[ ${#MESSAGES[@]} -eq 0 && -z "$WELCOME" ]]; then
  exit 0
fi

NOTICE=""
[[ ${#MESSAGES[@]} -gt 0 ]] && NOTICE="$(printf '%s\n' "${MESSAGES[@]}")"
emit() {
  python3 -c "
import json, sys
welcome, notice = sys.argv[1], sys.stdin.read()
out = {'systemMessage': '\n'.join(p for p in (welcome, notice.rstrip('\n')) if p)}
if notice.strip():
    out['hookSpecificOutput'] = {'hookEventName': 'SessionStart', 'additionalContext': notice}
print(json.dumps(out))
" "$1" <<< "$NOTICE"
}
OUT="$(emit "$WELCOME")" || exit 0
if [[ -n "$WELCOME" ]] && ! claim_welcome; then  # lost the race or cannot write: no welcome, keep any drift notice
  [[ ${#MESSAGES[@]} -eq 0 ]] && exit 0
  OUT="$(emit "")" || exit 0
fi
printf '%s\n' "$OUT"
exit 0
