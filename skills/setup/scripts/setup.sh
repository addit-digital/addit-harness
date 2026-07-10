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

# Before the plugin existed, install.sh's `--target claude` path copied
# agents/*.md and skills/*/ verbatim and unprefixed into ~/.claude/agents and
# ~/.claude/skills. The plugin now exposes that same content prefixed
# (addit-harness:code-reviewer, etc.), so anyone who ran the old install path
# and then adopted the plugin ends up with both the unprefixed legacy copy
# and the prefixed plugin copy listed side by side. Only ~/.claude is ever
# affected — the legacy script had no project-scope path — so this only runs
# for --scope global.
#
# Matching by name alone isn't safe (a name collision with the user's own,
# unrelated agent/skill would delete their file) and matching by exact byte
# content isn't effective (a legacy install predates the plugin's existence,
# so its content has near-certainly drifted from whatever the plugin ships
# today — measured 97-100% line similarity on real drifted copies vs. ~3% on
# a genuinely unrelated file of the same name, so a similarity threshold cuts
# cleanly between "same file, different revision" and "coincidental name
# collision"). Anything at/above the threshold is backed up then removed —
# so even a wrongly-flagged heavy customization is recoverable from the
# backup, never destroyed outright. Anything below is left alone and
# reported for the user to check by hand.
LEGACY_SIMILARITY_THRESHOLD=50

line_similarity_pct() {
  local a="$1" b="$2" la lb changed total
  la=$(wc -l < "$a"); lb=$(wc -l < "$b")
  changed=$(diff "$a" "$b" 2>/dev/null | grep -c '^[<>]' || true)
  total=$((la + lb))
  if [[ "$total" -eq 0 ]]; then echo 100; return; fi
  echo $(( 100 - (changed * 100 / total) ))
}

cleanup_legacy_claude_dupes() {
  local legacy_agents="$HOME/.claude/agents" legacy_skills="$HOME/.claude/skills"
  local retired_agents=0 retired_skills=0
  local skipped=()
  local legacy_backup="$BACKUP_ROOT/legacy-superseded-by-plugin"
  local f name d pct

  if [[ -d "$legacy_agents" ]]; then
    for f in "$PLUGIN_ROOT"/agents/*.md; do
      [[ -e "$f" ]] || continue
      name="$(basename "$f")"
      if [[ -e "$legacy_agents/$name" ]]; then
        pct="$(line_similarity_pct "$f" "$legacy_agents/$name")"
        if [[ "$pct" -ge "$LEGACY_SIMILARITY_THRESHOLD" ]]; then
          mkdir -p "$legacy_backup/agents"
          cp -p "$legacy_agents/$name" "$legacy_backup/agents/$name"
          rm -f "$legacy_agents/$name"
          retired_agents=$((retired_agents + 1))
        else
          skipped+=("agents/$name (${pct}% similar)")
        fi
      fi
    done
  fi

  if [[ -d "$legacy_skills" ]]; then
    for d in "$PLUGIN_ROOT"/skills/*/; do
      [[ -e "$d" ]] || continue
      name="$(basename "$d")"
      if [[ -e "$legacy_skills/$name/SKILL.md" && -e "$d/SKILL.md" ]]; then
        pct="$(line_similarity_pct "$d/SKILL.md" "$legacy_skills/$name/SKILL.md")"
        if [[ "$pct" -ge "$LEGACY_SIMILARITY_THRESHOLD" ]]; then
          mkdir -p "$legacy_backup/skills"
          cp -RPp "$legacy_skills/$name" "$legacy_backup/skills/$name"
          rm -rf "$legacy_skills/$name"
          retired_skills=$((retired_skills + 1))
        else
          skipped+=("skills/$name (${pct}% similar)")
        fi
      fi
    done
  fi

  if [[ "$retired_agents" -gt 0 || "$retired_skills" -gt 0 ]]; then
    info "retired $retired_agents legacy agent(s) + $retired_skills legacy skill(s) from a pre-plugin install"
    info "(>=${LEGACY_SIMILARITY_THRESHOLD}% similar to this plugin's shipped versions; backups -> $legacy_backup/)"
  fi
  if [[ ${#skipped[@]} -gt 0 ]]; then
    info "left ${#skipped[@]} name-matching but dissimilar item(s) alone (likely an unrelated file) — review by hand: ${skipped[*]}"
  fi
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

if [[ "$SCOPE" == "global" ]]; then
  cleanup_legacy_claude_dupes
fi

echo
echo "Done."
info "Backups of anything overwritten live under $BACKUP_ROOT/ (if anything was backed up)."
if [[ "$SCOPE" == "global" ]]; then
  info "Re-run /addit-harness:setup after the plugin auto-updates to re-sync these files."
else
  info "This project now has its own CLAUDE.md/rules — other projects are unaffected."
fi
