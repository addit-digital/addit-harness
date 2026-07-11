---
title: Getting started
nav_order: 1
nav_group: Start
---

## Which tool are you on?

**Claude Code** → follow this page. **Cursor, Kiro, or Codex CLI** → the
install steps differ (no plugin marketplace on those tools yet) — see
[Other coding agents](../other-agents/) instead.

## Install (Claude Code)

No clone, no shell script — install the plugin from inside Claude Code:

```
/plugin marketplace add addit-digital/addit-harness
/plugin install addit-harness@addit
/addit-harness:setup
```

- The plugin (`agents/`, `skills/`) tracks the repo via git automatically —
  no re-run needed to pick up updates.
- `/addit-harness:setup` places the parts a plugin can't carry natively
  (`CLAUDE.md`, `AGENTS.md`, `rules/`, `references/`, `settings.json`) — run
  it once after installing, and again after an update to re-sync. Add
  `--scope project` to confine it to the current project instead of
  `~/.claude` (default), or `--link` to symlink instead of copy.
- The plugin itself can also be scoped: `/plugin install addit-harness@addit
  --scope local` keeps it to just the current repo; `--scope project` shares
  it with collaborators via that repo's `.claude/settings.json`; default
  `--scope user` is global.

## The `@addit-harness:` namespacing gotcha

Plugin-provided agents are **namespaced** — invoke them as
`@addit-harness:code-reviewer`, not bare `@code-reviewer`. This is the most
common "why isn't this working" moment for new installs. See
[Subagents](../subagents/) for the full list.

## Verify it worked

Run `/help` — you should see `@addit-harness:code-reviewer` and the other
eleven subagents listed under Agents. If they're missing, re-run
`/addit-harness:setup` and check the plugin installed without errors.

## Alternative: copy-based install

Prefer the old copy-based install instead? `./install.sh --target claude`
still works — see [Other coding agents](../other-agents/) for the general
`install.sh` flags. It's no longer run automatically by a plain
`./install.sh` with no arguments.

## Next

- New to the mental model? Read [Concepts](../concepts/) next.
- Want to know what each subagent does? Read [Subagents](../subagents/).
