#!/usr/bin/env bash
# fe-contract-check.sh — PostToolUse advisory for the Frontend Implementation Contract.
# Advises only (exit 0 + additionalContext); fails open. ADDIT_FE_GATE: unset=line count, eslint=+project ESLint, 0=off.
set -uo pipefail; trap 'exit 0' ERR
GATE="${ADDIT_FE_GATE:-lines}"; [[ "$GATE" == "0" ]] && exit 0
command -v python3 >/dev/null || exit 0
IN="$(cat)"
tel() { case "${CLAUDE_PLUGIN_OPTION_TELEMETRY_LOCAL:-}" in true|True|1) printf '%s' "$IN" | python3 -S "${CLAUDE_PLUGIN_ROOT}/hooks/telemetry.py" "$@" >/dev/null 2>&1 || true;; esac; }
{ IFS= read -r FILE; IFS= read -r CWD; } < <(python3 -c 'import json,sys
try: d=json.load(sys.stdin)
except Exception: sys.exit(0)
print((d.get("tool_input") or {}).get("file_path","")); print(d.get("cwd",""))' <<< "$IN" 2>/dev/null) || exit 0
FILE="${FILE//\\//}"; CWD="${CWD//\\//}"
[[ "$FILE" =~ \.tsx?$ && ! "$FILE" =~ (\.d\.ts|\.(test|spec|stories)\.tsx?)$ && ! "$FILE" =~ /(node_modules|\.next|dist|build)/ ]] || exit 0
[[ "$FILE" =~ \.tsx$ || "$FILE" =~ /(components|features|hooks|app|screens)/ ]] || exit 0
[[ -f "$FILE" ]] || exit 0
msg=""; n=$(grep -cv '^[[:space:]]*$' "$FILE")
(( n > 250 )) && msg+="FC-1 (hard cap): $FILE has $n non-blank lines > 250. Split now."$'\n' && tel fc FC-1 cap "$n"
(( n > 150 && n <= 250 )) && msg+="FC-1: $FILE has $n non-blank lines > 150. Split or state a reason in your report."$'\n' && tel fc FC-1 advice "$n"
if [[ "$GATE" == "eslint" ]]; then   # explicit opt-in: runs the project's own ESLint config and plugins
  dir=$(dirname "$FILE"); root=""; bin=""
  while :; do
    [[ -z "$root" ]] && { compgen -G "$dir/eslint.config.*" >/dev/null || compgen -G "$dir/.eslintrc*" >/dev/null; } && root="$dir"
    [[ -n "$root" && -x "$dir/node_modules/.bin/eslint" ]] && { bin="$dir/node_modules/.bin/eslint"; break; }
    up=$(dirname "$dir"); [[ "$up" == "$dir" ]] && break; dir="$up"
  done
  if [[ -n "$bin" ]]; then
    rel="${FILE#"$root"/}"   # relative: avoids symlinked-path mismatches with ESLint's base path
    rc=0; out=$(cd "$root" && "$bin" --max-warnings 0 --no-warn-ignored "$rel" 2>/dev/null) || rc=$?
    (( rc == 2 )) && { rc=0; out=$(cd "$root" && "$bin" --max-warnings 0 "$rel" 2>/dev/null) || rc=$?; }   # ESLint 8: no --no-warn-ignored
    (( rc == 1 )) && msg+="ESLint:"$'\n'"$(printf '%s\n' "$out" | head -n 15)"$'\n'
  fi
fi
[[ -z "$msg" ]] && exit 0
python3 -c 'import json,sys; print(json.dumps({"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"[addit-harness advisory, Frontend Implementation Contract]\n"+sys.argv[1]}}))' "$msg"
exit 0
