---
name: setup
description: Use once, right after installing the addit-harness Claude Code plugin, to place the parts a plugin can't carry natively (CLAUDE.md, AGENTS.md, path-scoped rules/, references/, settings.json) into ~/.claude or the current project. Also use to re-sync after a plugin update, or to switch between global and project scope.
user-invocable: true
argument-hint: "[--scope global|project] [--link]"
---

# addit-harness setup

The `addit-harness` plugin ships `agents/` and `skills/` — those are already
live once the plugin is installed, nothing to do. This skill places the rest:
**`CLAUDE.md`, `AGENTS.md`, `rules/` (path-scoped language conventions),
`references/`, and `settings.json`** — none of which Claude Code plugins can
carry natively (no plugin-level memory file, no path-scoped auto-load rules,
no plugin-carried permissions/model).

## Choosing a scope — ask, don't silently default

`--scope` changes where files land in a way that's annoying to undo cleanly
(global touches every Claude Code session on the machine; project touches
just the current repo). Don't guess:

- If the user already passed `--scope` as an argument to this skill, use it
  as given — no need to ask.
- If they didn't, and the conversation doesn't already make the intent
  obvious (e.g. "just try it here" / "in this repo only" → project; "on my
  machine" or no project context at all → global), **ask** which they want
  before running anything. Offer `global` as the default recommendation
  since it matches `install.sh`'s existing behavior, but let them choose:
  - `global`: places everything under `~/.claude/` — applies to every Claude
    Code session on the machine.
  - `project`: places `CLAUDE.md`, `AGENTS.md`, `rules/`, `references/` bare
    at the current project root, and `settings.json` at
    `./.claude/settings.json` — matches Claude Code's own memory-file
    convention (project memory at root, project settings nested under
    `.claude/`) and only applies inside this one project.
- Mention while asking that the plugin itself can independently be scoped
  too (`/plugin install addit-harness@addit --scope local` keeps
  agents/skills confined to this repo as well) — see the README's *Install*
  section for both mechanisms together.

## What to run

Once the scope is settled, run the bundled script with the Bash tool:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/scripts/setup.sh" --scope <global|project> [--link]
```

`--link` symlinks instead of copying, so edits to `rules/`/`settings.json`
track the plugin's own git checkout. Default is copy.

The script backs up anything it would overwrite (matching `install.sh`'s
existing behavior) and prints a summary of what it placed and where.

For `--scope global`, it also retires any leftover unprefixed `agents/`
and `skills/` from a pre-plugin install (`install.sh --target claude`
used to copy those straight into `~/.claude/agents` and `~/.claude/skills`
unprefixed — the plugin now exposes the same content as
`addit-harness:<name>`, so the old copies are stale duplicates). A legacy
install predates the plugin, so its content has usually drifted from
whatever the plugin ships today — exact-match wouldn't catch most real
duplicates. Instead it compares line-level similarity: a name match at or
above 50% similar is treated as the same file at a different revision (backed
up, then removed — so even a wrongly-flagged heavy customization is
recoverable from the backup, never destroyed outright); anything less
similar is left in place and reported, since it's more likely a genuinely
unrelated file that happens to share the name.

## When to re-run

- After the plugin auto-updates (new `rules/`/`references/`/`settings.json`
  content), re-run with the same `--scope` to pick up the changes.
- To switch scope later (e.g. tried `--scope project`, now want it
  everywhere), re-run with `--scope global` — it's additive, doesn't remove
  the project-scoped files.
