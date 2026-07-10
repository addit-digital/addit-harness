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

## What to run

Run the bundled script with the Bash tool, passing through any arguments the
user gave this skill:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/scripts/setup.sh" [--scope global|project] [--link]
```

- `--scope global` (default): places everything under `~/.claude/` — applies
  to every Claude Code session on the machine, same as `install.sh` today.
- `--scope project`: places `CLAUDE.md`, `AGENTS.md`, `rules/`, `references/`
  bare at the current project root, and `settings.json` at
  `./.claude/settings.json` — matches Claude Code's own memory-file
  convention (project memory at root, project settings nested under
  `.claude/`) and only applies inside this one project. Use this when the
  user doesn't want the harness's conventions loaded globally.
- `--link`: symlink instead of copy, so edits to `rules/`/`settings.json`
  track the plugin's own git checkout. Default is copy.

The script backs up anything it would overwrite (matching `install.sh`'s
existing behavior) and prints a summary of what it placed and where.

## When to re-run

- After the plugin auto-updates (new `rules/`/`references/`/`settings.json`
  content), re-run with the same `--scope` to pick up the changes.
- To switch scope later (e.g. tried `--scope project`, now want it
  everywhere), re-run with `--scope global` — it's additive, doesn't remove
  the project-scoped files.

## If asked which scope to use

Default to `--scope global` unless the user says they only want this in the
current project, are just trying it out, or are working in a shared/team repo
where they don't want to affect their other work. In that case, `--scope
project` and mention that the plugin itself can independently be scoped too
(`/plugin install addit-harness@addit --scope local` keeps the agents/skills
confined to this repo as well — see the README's *Install* section for both
mechanisms together).
