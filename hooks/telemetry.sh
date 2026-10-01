#!/bin/sh
# Off-path gate: no python unless local telemetry is on. Always exit 0.
case "${CLAUDE_PLUGIN_OPTION_TELEMETRY_LOCAL:-}" in true|True|1) ;; *) cat >/dev/null 2>&1; exit 0;; esac
command -v python3 >/dev/null 2>&1 || { cat >/dev/null 2>&1; exit 0; }
d="${0%/*}"; [ "$d" = "$0" ] && d=.
exec python3 -S "$d/telemetry.py" hook
