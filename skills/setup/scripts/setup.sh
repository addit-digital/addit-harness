#!/usr/bin/env bash
#
# setup.sh — place addit-harness's CLAUDE.md, AGENTS.md, rules/, references/,
# and settings.json into a Claude Code scope. These are the artifacts the
# Claude Code plugin system cannot carry natively (no path-scoped auto-load
# rules, no plugin-level memory file, no plugin-carried permissions/model) —
# everything else (agents/, skills/) is already live via the plugin itself.
#
# Invoked by the /addit-harness:setup skill, which runs it with
# CLAUDE_PLUGIN_ROOT set. Mirrors install.sh's backup_and_place so Claude
# Code users get the same behavior as the Cursor/Kiro/Codex CLI install path.
#
# Usage: setup.sh [--scope global|project] [--link]
set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:?CLAUDE_PLUGIN_ROOT not set — run this via the /addit-harness:setup skill, not directly}"
SCOPE="global"
MODE="copy"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      shift
      SCOPE="${1:-}"
      [[ -z "$SCOPE" ]] && { echo "--scope requires a value (global|project)" >&2; exit 1; }
      ;;
    --link) MODE="link" ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done

if [[ "$SCOPE" != "global" && "$SCOPE" != "project" ]]; then
  echo "Unknown --scope: $SCOPE (expected global|project)" >&2
  exit 1
fi

STAMP="$(date +%Y%m%d-%H%M%S)"

if [[ "$SCOPE" == "global" ]]; then
  DEST_ROOT="$HOME/.claude"
  CLAUDE_MD_DEST="$DEST_ROOT/CLAUDE.md"
  AGENTS_MD_DEST="$DEST_ROOT/AGENTS.md"
  RULES_DEST="$DEST_ROOT/rules"
  REFERENCES_DEST="$DEST_ROOT/references"
  SETTINGS_DEST="$DEST_ROOT/settings.json"
  BACKUP_ROOT="$DEST_ROOT/.install-backups/$STAMP"
  REFERENCES_REWRITE_TARGET="$DEST_ROOT/references/"
else
  DEST_ROOT="$(pwd)"
  CLAUDE_MD_DEST="$DEST_ROOT/CLAUDE.md"
  AGENTS_MD_DEST="$DEST_ROOT/AGENTS.md"
  RULES_DEST="$DEST_ROOT/rules"
  REFERENCES_DEST="$DEST_ROOT/references"
  SETTINGS_DEST="$DEST_ROOT/.claude/settings.json"
  BACKUP_ROOT="$DEST_ROOT/.claude/.install-backups/$STAMP"
  REFERENCES_REWRITE_TARGET="$DEST_ROOT/references/"
fi

info() { printf '  %s\n' "$1"; }

backup_and_place() {
  local src="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if [[ -e "$dest" && ! -L "$dest" ]]; then
    local backup_dest="$BACKUP_ROOT/$(basename "$dest")"
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

backup_and_place_tree() {
  local src_dir="$1" dest_dir="$2" rel f backup_dest
  mkdir -p "$dest_dir"
  while IFS= read -r -d '' f; do
    rel="${f#"$src_dir"/}"
    backup_and_place "$f" "$dest_dir/$rel"
  done < <(find "$src_dir" -type f -print0)
}

echo "addit-harness setup: placing config (scope: $SCOPE, mode: $MODE)"
echo

backup_and_place "$PLUGIN_ROOT/CLAUDE.md" "$CLAUDE_MD_DEST"
backup_and_place "$PLUGIN_ROOT/AGENTS.md" "$AGENTS_MD_DEST"
info "placed CLAUDE.md + AGENTS.md -> $DEST_ROOT"

backup_and_place_tree "$PLUGIN_ROOT/rules" "$RULES_DEST"
if [[ "$SCOPE" == "project" ]]; then
  # rules/*.md hardcode ~/.claude/references/... — rewrite to this scope's path
  find "$RULES_DEST" -name '*.md' -type f -exec \
    sed -i.bak "s|~/.claude/references/|${REFERENCES_REWRITE_TARGET}|g" {} \;
  find "$RULES_DEST" -name '*.md.bak' -type f -delete
fi
info "placed rules/ -> $RULES_DEST"

backup_and_place_tree "$PLUGIN_ROOT/references" "$REFERENCES_DEST"
info "placed references/ -> $REFERENCES_DEST"

backup_and_place "$PLUGIN_ROOT/settings.json" "$SETTINGS_DEST"
info "placed settings.json -> $SETTINGS_DEST"

echo
echo "Done."
info "Backups of anything overwritten live under $BACKUP_ROOT/ (if anything was backed up)."
if [[ "$SCOPE" == "global" ]]; then
  info "Re-run /addit-harness:setup after the plugin auto-updates to re-sync these files."
else
  info "This project now has its own CLAUDE.md/rules — other projects are unaffected."
fi
