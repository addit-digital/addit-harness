#!/usr/bin/env bash
#
# install.sh — sync this repo's config into whichever coding agents you have
# installed. Auto-detects by default: checks each tool's CLI on PATH or home
# directory, and syncs config for every one it finds.
#
# Claude Code is no longer synced by this script by default — it has its own,
# better install path: a native plugin (agents/skills/references, tracked by
# git automatically) plus the /addit-harness:setup skill (rules/settings.json,
# which plugins can't carry). See the README's Install section, or
# docs/plans/2026-07-10-claude-code-plugin-packaging.md for why. `--target
# claude` still works below as an explicit legacy path for anyone who'd
# rather not use plugins.
#
# Usage:
#   ./install.sh              # auto-detect: sync every supported tool found (claude excluded)
#   ./install.sh --target X   # force one tool: claude|cursor|kiro|codex|copilot
#   ./install.sh --link       # symlink instead of copy (edits track git)
#   ./install.sh --plugins    # claude only: register marketplaces + install official plugins
#   ./install.sh --help
#
# copilot is project-scoped (lives in a repo's .github/, not a home
# directory) and is not covered by auto-detect — force it explicitly from
# inside the target project. Not yet implemented (see docs/plans/).
#
# MCP is intentionally NOT synced for any tool. mcp.example.json is a
# disabled, human-curated catalogue (see its own "_README" entry) meant for
# picking one entry, filling in credentials by hand, and pasting it into the
# tool's real MCP config yourself — see the printed notes below for where
# each tool expects that paste.
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$REPO_DIR/tools.config.json"
KNOWN_TOOLS=(claude cursor kiro codex copilot)
AUTO_DETECT_TOOLS=(cursor kiro codex)

MODE="copy"
DO_PLUGINS=0
FORCE_TARGET=""
STAMP="$(date +%Y%m%d-%H%M%S)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --link) MODE="link" ;;
    --plugins) DO_PLUGINS=1 ;;
    --target)
      shift
      FORCE_TARGET="${1:-}"
      [[ -z "$FORCE_TARGET" ]] && { echo "--target requires a value" >&2; exit 1; }
      ;;
    --help|-h)
      grep '^#' "$0" | sed 's/^# \{0,1\}//; 1d'
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done

if [[ -n "$FORCE_TARGET" ]]; then
  known=0
  for t in "${KNOWN_TOOLS[@]}"; do [[ "$t" == "$FORCE_TARGET" ]] && known=1; done
  [[ "$known" == "1" ]] || { echo "Unknown --target: $FORCE_TARGET (known: ${KNOWN_TOOLS[*]})" >&2; exit 1; }
fi

info() { printf '  %s\n' "$1"; }

tool_home() {
  local tool="$1" var_name
  var_name="$(echo "$tool" | tr '[:lower:]' '[:upper:]')_HOME"
  if [[ -n "${!var_name:-}" ]]; then
    echo "${!var_name}"
    return
  fi
  python3 -c "
import json, sys
print(json.load(open('$CONFIG'))[sys.argv[1]]['home'])
" "$tool" | sed "s|^~|$HOME|"
}

is_detected() {
  local tool="$1" bin dir
  bin="$(python3 -c "
import json, sys
print(json.load(open('$CONFIG'))[sys.argv[1]].get('detect', {}).get('bin', ''))
" "$tool")"
  dir="$(python3 -c "
import json, sys
print(json.load(open('$CONFIG'))[sys.argv[1]].get('detect', {}).get('dir', ''))
" "$tool")"
  dir="${dir/#\~/$HOME}"
  if [[ -n "$bin" ]] && command -v "$bin" >/dev/null 2>&1; then return 0; fi
  if [[ -n "$dir" && -d "$dir" ]]; then return 0; fi
  return 1
}

# Place a single Claude-Code-only file (settings.json has no cross-tool
# equivalent, so it stays outside sync_tools.py's generic interpreter).
backup_and_place() {
  local src="$1" dest="$2" backup_dir="$3" home="$4"
  mkdir -p "$(dirname "$dest")"
  if [[ -e "$dest" && ! -L "$dest" ]]; then
    local rel="${dest#"$home"/}"
    local backup_dest="$backup_dir/$rel"
    mkdir -p "$(dirname "$backup_dest")"
    cp -p "$dest" "$backup_dest"
    info "backed up existing $dest -> $backup_dest"
  fi
  rm -f "$dest"
  if [[ "$MODE" == "link" ]]; then
    ln -s "$src" "$dest"
  else
    cp "$src" "$dest"
  fi
}

maybe_install_plugins() {
  [[ "$DO_PLUGINS" == "1" ]] || return 0
  if command -v claude >/dev/null 2>&1; then
    echo "Registering marketplaces + installing official plugins..."
    claude plugin marketplace add anthropics/skills || true
    for p in gopls-lsp jdtls-lsp typescript-lsp pr-review-toolkit \
             commit-commands security-guidance figma; do
      claude plugin install "$p@claude-plugins-official" || true
    done
    claude plugin install document-skills@anthropic-agent-skills || true
    info "Done. Run /plugin inside Claude Code to verify."
  else
    info "'claude' CLI not found on PATH — skipping plugin install."
  fi
}

sync_tool() {
  local tool="$1" home backup_dir
  home="$(tool_home "$tool")"
  backup_dir="$home/.install-backups/$STAMP"
  mkdir -p "$home"

  echo "Syncing $tool -> $home"
  local extra_args=()
  [[ "$MODE" == "link" ]] && extra_args+=(--link)
  python3 "$REPO_DIR/sync_tools.py" "$tool" \
    --repo "$REPO_DIR" --home "$home" --config "$CONFIG" \
    --backup-dir "$backup_dir" "${extra_args[@]+"${extra_args[@]}"}"

  if [[ "$tool" == "claude" ]]; then
    backup_and_place "$REPO_DIR/settings.json" "$home/settings.json" "$backup_dir" "$home"
    maybe_install_plugins
  fi
}

echo "addit-harness: syncing coding-agent config (mode: $MODE)"
echo

if [[ "$FORCE_TARGET" == "copilot" ]]; then
  info "copilot is project-scoped (.github/ inside a repo, not a home directory)"
  info "and is not implemented yet — see docs/plans/2026-07-10-multi-tool-agent-config.md"
  exit 0
fi

TARGETS=()
if [[ -n "$FORCE_TARGET" ]]; then
  TARGETS=("$FORCE_TARGET")
else
  if is_detected claude; then
    info "claude: detected, but not synced by this script — install the plugin instead:"
    info "  /plugin marketplace add addit-digital/addit-harness"
    info "  /plugin install addit-harness@addit"
    info "  /addit-harness:setup"
    info "(pass --target claude to use this script for Claude Code anyway)"
  fi
  for t in "${AUTO_DETECT_TOOLS[@]}"; do
    if is_detected "$t"; then
      TARGETS+=("$t")
    else
      info "$t: not detected — skipping (pass --target $t to force)"
    fi
  done
  if [[ ${#TARGETS[@]} -eq 0 ]]; then
    echo
    echo "No supported coding agents detected on this machine (besides Claude Code,"
    echo "which uses the plugin path above)."
    echo "Install one of: cursor, kiro, codex — or force with --target <tool>."
    exit 0
  fi
fi

echo
for t in "${TARGETS[@]}"; do
  sync_tool "$t"
  echo
done

echo "Synced: ${TARGETS[*]}"
echo
echo "Notes:"
info "Backups of anything overwritten live under <tool-home>/.install-backups/$STAMP/."
info "MCP is intentionally NOT synced — mcp.example.json is a disabled catalogue for"
info "manual copy-paste (fill in credentials yourself, don't commit secrets):"
info "  claude -> ~/.claude/.mcp.json (secrets in ~/.claude/mcp.local.json, gitignored)"
info "  cursor -> ~/.cursor/mcp.json"
info "  kiro   -> ~/.kiro/settings/mcp.json"
info "  codex  -> ~/.codex/config.toml under [mcp_servers.<name>] (TOML, not JSON)"
info "  copilot-> repo Settings -> Copilot -> MCP servers (no repo file)"
info "templates/CLAUDE.project.md stays in the repo — copy it per project."
if [[ -z "$FORCE_TARGET" && "$DO_PLUGINS" == "0" ]]; then
  info "Claude plugins not installed (run with --plugins to register them now)."
fi
echo
echo "Done."
