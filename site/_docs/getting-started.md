---
title: Getting started
nav_order: 1
nav_group: Start
---

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
thirteen subagents listed under Agents. If they're missing, re-run
`/addit-harness:setup` and check the plugin installed without errors.

## All docs

The sidebar has the full list; here's the same thing with what each page
actually covers, so you don't have to click through page by page to find it:

**Start**
- [Concepts](../concepts/) — the engineering loop, tiered conventions, curation philosophy, deterministic orchestration
- [How dev-flow works](../dev-flow/) — phase-by-phase mechanics of the design-gate/review-gate loops

**Reference**
- [Subagents](../subagents/) — what each of the 13 subagents does and when it fires
- [Skills & commands](../skills-commands/) — every `/slash-command` this plugin adds
- [Model & cost](../model-cost/) — which subagent runs on which tier, and how to cut spend
- [Enabling MCP](../mcp/) — connecting Jira, databases, and other optional integrations

**Guides**
- [Use cases](../use-cases/) — concrete workflows showing which configs fire together
- [Extending](../extending/) — adding your own conventions, agents, or skills

**Project**
- [Roadmap](../roadmap/) — planned work and how to contribute
- [Changelog](../changelog/) — what's shipped, release by release
