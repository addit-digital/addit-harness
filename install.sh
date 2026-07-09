#!/usr/bin/env bash
#
# install.sh — install this Claude Code config into ~/.claude
#
# Maps each item in this repo to its required location under ~/.claude, backing
# up anything it would overwrite. Merges per-item: it never replaces the whole
# ~/.claude directory, so your projects/, history, and existing hooks are safe.
#
# Usage:
#   ./install.sh            # copy files (default)
#   ./install.sh --link     # symlink files back to this repo (edits track git)
#   ./install.sh --plugins  # also register marketplaces + install official plugins
#   ./install.sh --help
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_HOME:-$HOME/.claude}"
MODE="copy"
DO_PLUGINS=0
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$CLAUDE_DIR/.install-backups/$STAMP"

for arg in "$@"; do
  case "$arg" in
    --link) MODE="link" ;;
    --plugins) DO_PLUGINS=1 ;;
    --help|-h)
      grep '^#' "$0" | sed 's/^# \{0,1\}//; 1d'
      exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

info() { printf '  %s\n' "$1"; }

# Place one file: $1 = source path, $2 = destination path.
place_file() {
  local src="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  # If a real (non-symlink) file is in the way, back it up once, into
  # BACKUP_DIR (mirroring its path under CLAUDE_DIR) rather than cluttering
  # the destination directory with a sibling .bak file.
  if [[ -e "$dest" && ! -L "$dest" ]]; then
    local rel="${dest#"$CLAUDE_DIR"/}"
    local backup_dest="$BACKUP_DIR/$rel"
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

# Place every file under a source dir into the matching dir under ~/.claude.
place_dir() {
  local src_dir="$1" dest_dir="$2"
  local f rel
  while IFS= read -r -d '' f; do
    rel="${f#"$src_dir"/}"
    place_file "$f" "$dest_dir/$rel"
  done < <(find "$src_dir" -type f -print0)
}

echo "Installing Claude Code config -> $CLAUDE_DIR  (mode: $MODE)"
mkdir -p "$CLAUDE_DIR"

# Single files
place_file "$REPO_DIR/CLAUDE.md"     "$CLAUDE_DIR/CLAUDE.md"
place_file "$REPO_DIR/settings.json" "$CLAUDE_DIR/settings.json"

# Directories (merge per-file)
place_dir  "$REPO_DIR/rules"      "$CLAUDE_DIR/rules"
place_dir  "$REPO_DIR/references" "$CLAUDE_DIR/references"
place_dir  "$REPO_DIR/agents"     "$CLAUDE_DIR/agents"
place_dir  "$REPO_DIR/skills"     "$CLAUDE_DIR/skills"

echo "Files installed."
echo
echo "Notes:"
if [[ -d "$BACKUP_DIR" ]]; then
  info "Existing files that were overwritten are backed up under $BACKUP_DIR."
fi
info "settings.json was replaced (old one backed up). If you had custom"
info "permissions/hooks, merge them back from $BACKUP_DIR/settings.json."
info "MCP is intentionally NOT installed. To enable Atlassian/DB later, copy an"
info "entry from mcp.example.json into $CLAUDE_DIR/.mcp.json and put secrets in"
info "$CLAUDE_DIR/mcp.local.json (gitignored). See README 'Enabling MCP'."
info "templates/CLAUDE.project.md stays in the repo — copy it per project."

if [[ "$DO_PLUGINS" == "1" ]]; then
  echo
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
    info "settings.json already lists the plugins in enabledPlugins; they will"
    info "be offered when you next start Claude Code."
  fi
else
  echo
  info "Plugins not installed (run with --plugins to register them now)."
  info "They are also declared in settings.json:enabledPlugins."
fi

echo
echo "Done."
