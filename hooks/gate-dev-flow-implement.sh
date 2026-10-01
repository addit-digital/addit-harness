#!/usr/bin/env bash
#
# gate-dev-flow-implement.sh — PreToolUse hook on the Workflow tool. The
# dev-flow-implement workflow may only start once the user approved the plan:
# plan.md must exist, carry the approval marker the dev-flow skill appends, and
# hash to the planSha256 passed in the workflow args. Anything else is denied
# (exit 2, stderr goes to Claude) before any agent starts.
#
# Fail open for everything that is not dev-flow-implement, and for input that
# cannot even be read. From the moment the call is identified as
# dev-flow-implement, fail closed.
#
# This stops accidents (a direct /addit-harness:dev-flow-implement, a stale
# slug, a plan edited after approval). It does not stop a model that writes the
# marker and hash itself; the human approval in the conversation is the real gate.
set -uo pipefail  # no -e: every failure path below is handled explicitly

IN="$(cat)" || exit 0
grep -q 'dev-flow-implement' <<< "$IN" || exit 0

SUFFIX='Do not work around this; ask the user to approve the plan via /addit-harness:dev-flow.'
# Records the verdict locally when telemetry_local is on; runs after the decision and never changes it.
tel() { case "${CLAUDE_PLUGIN_OPTION_TELEMETRY_LOCAL:-}" in true|True|1) printf '%s' "$IN" | python3 -S "${CLAUDE_PLUGIN_ROOT}/hooks/telemetry.py" "$@" >/dev/null 2>&1 || true;; esac; }
deny() { tel gate plan_approval blocked; echo "dev-flow-implement blocked: $1 $SUFFIX" >&2; exit 2; }

command -v python3 >/dev/null 2>&1 || deny "python3 is required to verify the plan gate but was not found."

# Prints slug, repo, planSha256 (one per line). Exit 10 = a different workflow that
# merely mentions the name; exit 11 = malformed args; any other failure = unparseable.
PARSED="$(python3 -c '
import json, re, sys
NAMES = {"dev-flow-implement", "addit-harness:dev-flow-implement"}
tool_input = json.load(sys.stdin).get("tool_input") or {}
script_name = ""
m = re.search(r"export\s+const\s+meta\s*=\s*\{[\s\S]*?\bname\s*:\s*[\x27\"]([^\x27\"]+)[\x27\"]", tool_input.get("script") or "")
if m:
    script_name = m.group(1)
path = (tool_input.get("scriptPath") or "").rsplit("/", 1)[-1]
if path.endswith(".js"):
    path = path[:-3]
if not ({tool_input.get("name"), path, script_name} & NAMES):
    sys.exit(10)
a = tool_input.get("args")
if isinstance(a, str):
    a = json.loads(a)
if not isinstance(a, dict):
    sys.exit(11)
slug, repo, sha = (a.get(k) for k in ("slug", "repo", "planSha256"))
ok = (isinstance(slug, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", slug)
      and isinstance(repo, str) and repo.startswith("/")
      and isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{64}", sha))
if not ok:
    sys.exit(11)
print(slug); print(repo); print(sha)
' <<< "$IN" 2>/dev/null)"
rc=$?
[[ $rc -eq 10 ]] && exit 0
[[ $rc -eq 11 ]] && deny "args must carry a valid slug, an absolute repo, and a 64-hex planSha256."
[[ $rc -ne 0 ]] && deny "the Workflow call could not be parsed."

{ read -r SLUG; read -r REPO; read -r SHA; } <<< "$PARSED"
PLAN="$REPO/docs/work/$SLUG/plans/plan.md"

[[ -f "$PLAN" ]] || deny "plan not found at $PLAN."
grep -q '^> dev-flow: approved' "$PLAN" || deny "plan.md has no approval marker."
ACTUAL="$(shasum -a 256 "$PLAN" 2>/dev/null | cut -d' ' -f1)"
[[ -n "$ACTUAL" ]] || deny "could not hash $PLAN."
[[ "$ACTUAL" == "$SHA" ]] || deny "plan.md changed since approval (hash mismatch)."
tel gate plan_approval pass
exit 0
