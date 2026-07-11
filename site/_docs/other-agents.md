---
title: Other coding agents
nav_order: 7
nav_group: Reference
---

`AGENTS.md` is the single canonical source — every tool's config is
generated from it (plus `rules/`, `references/`, `agents/`). Claude Code has
its own plugin/marketplace path (see [Getting started](../getting-started/));
Cursor, Kiro, and Codex CLI are synced by `install.sh` + `sync_tools.py`
instead, driven by the declarative mapping in `tools.config.json`.

## Install

```bash
git clone <this-repo> ~/src/addit-harness && cd ~/src/addit-harness
./install.sh              # auto-detect: sync every supported agent found on this machine
./install.sh --target X   # force one: claude|cursor|kiro|codex
./install.sh --link       # symlink instead of copy, so edits track git
./install.sh --plugins    # claude only: also register marketplaces + install official plugins
```

`install.sh` checks each tool's CLI on `PATH` or home directory
(`~/.cursor`, `~/.kiro`, `~/.codex`) and syncs config into whichever it
finds. It merges per-file into each tool's home, never clobbering the whole
directory, so `projects/`, history, and existing hooks are preserved.
Re-running backs up anything it replaces to
`<tool-home>/.install-backups/<timestamp>/`.

Claude Code is no longer synced by a plain `./install.sh` run (it uses the
plugin path); `--target claude` still works if you'd rather use the
copy-based install — it backs up and replaces `~/.claude/settings.json` too,
so merge any custom permissions/hooks back from the backup.

## Cursor

- Baseline: `~/.cursor/rules/global.mdc` (`alwaysApply`)
- Language conventions: `~/.cursor/rules/*.mdc` (`globs`)
- Subagents: Cursor 2.4+ reads `~/.claude/agents/*.md` natively — **only if
  that directory is populated.** Plugin-only Claude Code installs no longer
  write there; run `install.sh --target claude` (or a future Cursor-native
  plugin, see [Roadmap](../roadmap/)) if you want Cursor to pick these up too.

## Kiro

- Baseline: `~/.kiro/steering/global.md` (`inclusion: always`)
- Language conventions: `~/.kiro/steering/*.md` (`inclusion: fileMatch`)
- Subagents: `~/.kiro/agents/*.md` — tool names remapped to Kiro's category
  tags (`read`/`write`/`shell`/`web`/...).

## Codex CLI

- Baseline: `~/.codex/AGENTS.md` (native filename, no rename needed)
- Language conventions: folded into the same `AGENTS.md`
- Subagents: `~/.codex/agents/*.toml` — converted to TOML; tool-restriction
  becomes a derived `sandbox_mode` (`read-only` vs `workspace-write`), since
  Codex has no per-tool allowlist.

## Per-tool coverage

| Tool | Baseline (`AGENTS.md` + engineering loop) | Language conventions | Subagents (`agents/*.md`) |
|------|------|------|------|
| **Claude Code** | Plugin: `agents/`/`skills/` auto-discovered. `/addit-harness:setup`: `~/.claude/CLAUDE.md` (`@import`) | `/addit-harness:setup`: `~/.claude/rules/*.md` (auto-load via `paths:`) | Plugin, auto-discovered — invoke as `@addit-harness:<name>` |
| **Cursor** | `~/.cursor/rules/global.mdc` (`alwaysApply`) | `~/.cursor/rules/*.mdc` (`globs`) | Reads `~/.claude/agents/*.md` natively (2.4+), only if populated |
| **Kiro** | `~/.kiro/steering/global.md` (`inclusion: always`) | `~/.kiro/steering/*.md` (`inclusion: fileMatch`) | `~/.kiro/agents/*.md`, remapped tool names |
| **Codex CLI** | `~/.codex/AGENTS.md` | folded into the same `AGENTS.md` | `~/.codex/agents/*.toml` |
| **GitHub Copilot** | *(planned — see [Roadmap](../roadmap/))* | | |

Vendored prose that hardcodes a `~/.claude/references/...` path (e.g.
`rules/go.md`) is rewritten per tool to that tool's own reference path
(`~/.cursor/references/...`, etc.) so the pointer actually resolves.

## MCP is not auto-synced

`mcp.example.json` is a disabled, human-curated catalogue by design — pick an
entry, fill in credentials by hand, and paste it into the tool's real MCP
config yourself (`install.sh`'s footer prints the right target path per tool
after every run). See [Enabling MCP](../mcp/) for the Claude Code specifics.

## Skills

Skills (`/adr`, `/save-plan`, etc.) are placed as files for the other tools
today, but porting them with correct per-tool invocation semantics (Cursor
commands, Kiro manual steering, Codex prompts, Copilot prompt files) is
planned, not yet implemented — see [Roadmap](../roadmap/).

## Next

- [Getting started](../getting-started/) — the Claude Code plugin path.
- [Roadmap](../roadmap/) — native plugin packaging for these three tools.
