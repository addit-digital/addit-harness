#!/usr/bin/env bash
#
# setup.sh — place addit-harness's CLAUDE.md, AGENTS.md, rules/, references/,
# and settings.json into a Claude Code scope. These are the artifacts the
# Claude Code plugin system cannot carry natively (no path-scoped auto-load
# rules, no plugin-level memory file, no plugin-carried permissions/model) —
# everything else (agents/, skills/) is already live via the plugin itself.
#
# Invoked by the /addit-harness:setup skill, which runs it with
# CLAUDE_PLUGIN_ROOT set. Anything it would overwrite is backed up first.
#
# Usage: setup.sh [--scope global|project] [--link] [--plugins]
set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:?CLAUDE_PLUGIN_ROOT not set — run this via the /addit-harness:setup skill, not directly}"
SCOPE="global"
MODE="copy"
INSTALL_PLUGINS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      shift
      SCOPE="${1:-}"
      [[ -z "$SCOPE" ]] && { echo "--scope requires a value (global|project)" >&2; exit 1; }
      ;;
    --link) MODE="link" ;;
    --plugins) INSTALL_PLUGINS=1 ;;
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

# settings.json holds user state (hooks, statusLine, env, permissions, plugin
# enable/disable choices) that a blind overwrite would destroy, so copy mode
# merges instead: top-level keys the template owns (model, permissions, ...)
# are updated, keys it lacks survive, and enabledPlugins /
# extraKnownMarketplaces are deep-merged with the user's existing values
# winning (a plugin they disabled stays disabled). Output is deterministic so
# re-runs are byte-identical. Link mode symlinks, as for every other file.
place_settings() {
  local src="$1" dest="$2" tmp
  if [[ "$MODE" == "link" || ! -e "$dest" ]]; then
    backup_and_place "$src" "$dest"
    return
  fi
  local backup_dest="$BACKUP_ROOT/$(basename "$dest")"
  mkdir -p "$(dirname "$backup_dest")"
  cp -p "$dest" "$backup_dest"
  info "backed up existing $dest -> $backup_dest"
  tmp="$(mktemp "$dest.XXXXXX")"
  if ! python3 - "$src" "$dest" "$tmp" <<'PY'
import json, sys
src, dest, out = sys.argv[1:4]
template = json.load(open(src))
try:
    existing = json.load(open(dest))
except ValueError as e:
    sys.exit(f"{dest} is not valid JSON ({e}); fix or remove it, then re-run")
if not isinstance(existing, dict):
    sys.exit(f"{dest} is not a JSON object; fix or remove it, then re-run")
merged = {**existing, **template}
for key in ("enabledPlugins", "extraKnownMarketplaces"):
    if isinstance(template.get(key), dict) and isinstance(existing.get(key), dict):
        merged[key] = {**template[key], **existing[key]}
# permissions: keep the user's own rules — union the allow/deny/ask lists, existing entries first
tp, ep = template.get("permissions"), existing.get("permissions")
if isinstance(tp, dict) and isinstance(ep, dict):
    perms = {**tp, **ep}
    for k in set(tp) | set(ep):
        a, b = tp.get(k), ep.get(k)
        if isinstance(a, list) or isinstance(b, list):
            perms[k] = list(dict.fromkeys((b if isinstance(b, list) else []) + (a if isinstance(a, list) else [])))
    merged["permissions"] = perms
with open(out, "w") as f:
    json.dump(merged, f, indent=2)
    f.write("\n")
PY
  then
    rm -f "$tmp"
    exit 1
  fi
  chmod 644 "$tmp"
  rm -f "$dest"
  mv "$tmp" "$dest"
}

# Opt-in: register every marketplace and install every plugin that the placed
# settings.json declares (read from the file, no hardcoded list), because
# whether Claude Code installs enabledPlugins on first start is unverified.
# Failures are reported, not fatal: re-running is safe.
install_declared_plugins() {
  if ! command -v claude >/dev/null 2>&1; then
    info "claude CLI not found on PATH; skipping --plugins (install the plugins from inside Claude Code instead)"
    return
  fi
  local kind arg
  while IFS=$'\t' read -r kind arg; do
    if [[ "$kind" == "marketplace" ]]; then
      claude plugin marketplace add "$arg" || info "could not add marketplace $arg (already added?)"
    else
      claude plugin install "$arg" || info "could not install plugin $arg"
    fi
  done < <(python3 - "$SETTINGS_DEST" <<'PY'
import json, sys
s = json.load(open(sys.argv[1]))
for m in (s.get("extraKnownMarketplaces") or {}).values():
    src = m.get("source") or {}
    ref = src.get("repo") or src.get("url") or src.get("path")
    if ref:
        print(f"marketplace\t{ref}")
for plugin, on in (s.get("enabledPlugins") or {}).items():
    if on is True:
        print(f"plugin\t{plugin}")
PY
)
}

backup_and_place_tree() {
  local src_dir="$1" dest_dir="$2" rel f backup_dest
  mkdir -p "$dest_dir"
  while IFS= read -r -d '' f; do
    rel="${f#"$src_dir"/}"
    backup_and_place "$f" "$dest_dir/$rel"
  done < <(find "$src_dir" -type f -print0)
}

# Before the plugin existed, the pre-plugin copy installer (since removed) copied
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

# References that earlier releases shipped and later releases replaced by topic
# files. backup_and_place_tree only adds files, so a re-sync would leave them
# behind (and project scope writes into the user's own repo, so they may have
# edited or reused the name). Fixed list, "relative path|sha256 of the version
# shipped at main (git show main:references/<path> | sha256sum)". A retired file
# is removed only when it is a symlink into a plugin root (--link install) or a
# regular file whose sha256 equals the shipped one. Anything else is copied to
# $BACKUP_ROOT/retired/ and reported, never deleted.
RETIRED_REFERENCES=(
  "java/java-best-practices.md|ea37c9476ddedd06ff9efb2405aa4ab38928c9d9fe044c04722b33fa56341e46"
  "go/app-erp-conventions.md|84e6a0f0d096d19b27cd913699548ad64b54472232dd9202bdba0e279276228c"
)

file_sha256() {
  python3 -c "import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest())" "$1"
}

cleanup_retired_references() {
  local entry rel want dest target got
  local removed=0 skipped=()
  for entry in "${RETIRED_REFERENCES[@]}"; do
    rel="${entry%%|*}"
    want="${entry##*|}"
    dest="$REFERENCES_DEST/$rel"
    [[ -e "$PLUGIN_ROOT/references/$rel" ]] && continue # still shipped: not retired
    if [[ -L "$dest" ]]; then
      target="$(readlink "$dest")"
      if [[ "$target" == "$PLUGIN_ROOT"/* || "$target" == */plugins/*/references/"$rel" ]]; then
        rm -f "$dest"
        removed=$((removed + 1))
      else
        skipped+=("references/$rel (symlink to $target)")
      fi
    elif [[ -f "$dest" ]]; then
      got="$(file_sha256 "$dest")"
      if [[ "$got" == "$want" ]]; then
        rm -f "$dest"
        removed=$((removed + 1))
      else
        mkdir -p "$BACKUP_ROOT/retired/$(dirname "$rel")"
        cp -p "$dest" "$BACKUP_ROOT/retired/$rel"
        skipped+=("references/$rel (modified; copy in $BACKUP_ROOT/retired/)")
      fi
    fi
  done
  if [[ "$removed" -gt 0 ]]; then
    info "removed $removed retired reference file(s) superseded by topic files"
  fi
  if [[ ${#skipped[@]} -gt 0 ]]; then
    info "kept ${#skipped[@]} retired reference file(s) that differ from the shipped version — review by hand: ${skipped[*]}"
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
cleanup_retired_references

place_settings "$PLUGIN_ROOT/settings.json" "$SETTINGS_DEST"
info "placed settings.json -> $SETTINGS_DEST"

if [[ "$SCOPE" == "global" ]]; then
  cleanup_legacy_claude_dupes
fi

if [[ "$INSTALL_PLUGINS" -eq 1 ]]; then
  echo
  echo "Installing plugins declared in settings.json (--plugins)"
  install_declared_plugins
fi

# Record a content hash of just the files this script actually copies
# (CLAUDE.md, AGENTS.md, rules/, references/, settings.json — agents/ and
# skills/ don't need this, the plugin loader already serves those live), so
# the SessionStart hook (hooks/check-setup-version.sh) can tell the user to
# re-run this skill only when THOSE files change — not on every plugin
# version bump, most of which don't touch them at all. Keep this hashing
# logic identical to the copy in check-setup-version.sh.
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

SETUP_CONTENT_HASH="$(setup_content_hash "$PLUGIN_ROOT")"
PLUGIN_VERSION="$(python3 -c "
import json
print(json.load(open('$PLUGIN_ROOT/.claude-plugin/plugin.json'))['version'])
" 2>/dev/null || echo "unknown")"
if [[ "$SCOPE" == "global" ]]; then
  MARKER="$DEST_ROOT/.addit-harness-setup-version"
else
  mkdir -p "$DEST_ROOT/.claude"
  MARKER="$DEST_ROOT/.claude/.addit-harness-setup-version"
fi
{
  echo "$SETUP_CONTENT_HASH"
  echo "$PLUGIN_VERSION"
} > "$MARKER"

echo
echo "Done."
info "Backups of anything overwritten live under $BACKUP_ROOT/ (if anything was backed up)."
if [[ "$SCOPE" == "global" ]]; then
  info "Re-run /addit-harness:setup after the plugin auto-updates to re-sync these files."
  info "(a SessionStart reminder will also tell you when a newer version is available)"
else
  info "This project now has its own CLAUDE.md/rules — other projects are unaffected."
fi
