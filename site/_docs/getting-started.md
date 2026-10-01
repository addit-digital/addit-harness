---
title: Getting started
description: Install addit-harness as a Claude Code plugin, run setup, and check that the subagents loaded.
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

addit-harness supports Claude Code only. If you used the old `install.sh`, see
[Migrating from `install.sh`](#migrating-from-installsh) below.

## First run

The first time you start an interactive terminal session after installing, the
plugin shows one welcome line. If setup has not run yet, it says to run
`/addit-harness:setup`; once setup has run, it points at
`/addit-harness:dev-flow <what to build>`. Both versions mention
`/addit-harness:tips`.

- It appears once. The session-start hook creates an empty marker file,
  `onboarding/welcome-v1`, in the plugin's data folder before printing, and
  stays silent whenever that file exists. If the folder cannot be written, it
  prints nothing.
- It appears only at a fresh startup in an interactive terminal session (the
  hook checks that `CLAUDE_CODE_ENTRYPOINT` is `cli` or unset): not under
  `claude -p`, and not on resume, `/clear` or compaction. If your first session
  is headless, the welcome waits for the first interactive one. The filter is
  deliberately narrow: other entrypoints (the desktop app, IDE integrations) are
  not shown the welcome.
- It is shown to you as a hook message and is not added to the model's
  context. Nothing is sent anywhere (see [Privacy](../../privacy/)).

When setup finishes it prints a next-steps line: `/addit-harness:dev-flow` for
non-trivial work, `/addit-harness:tips` for the short guide, and a reminder that
local telemetry stays off unless you turn it on in `/config`.

`/addit-harness:tips` prints five short tips: when to use `/dev-flow`, that you
approve the plan before any code is written, where the documents land, how to
call the specialist agents (and the Go and React convention commands), and how
the local telemetry option works. It is user-invoked only; the model does not
run it on its own.

## What setup does to your `settings.json`

Setup **merges** the plugin's `settings.json` into yours instead of replacing
it, and backs up your previous file first (`~/.claude/.install-backups/<timestamp>/`,
or `.claude/.install-backups/<timestamp>/` for `--scope project`):

- Keys the template does not set (`hooks`, `statusLine`, `env` and so on) are
  kept as they are.
- `permissions` lists (`allow`, `deny`, `ask`) are unioned: your own rules stay,
  first, and the template's are added after them.
- `enabledPlugins`, `extraKnownMarketplaces` and `env` are merged key by key
  with your values winning, so a plugin you disabled stays disabled and an
  environment variable you set is never overwritten.
- `env` gains `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` unless you already set that
  variable. It turns on Claude Code's task tools, which are off by default on
  newer models, so `/dev-flow` can keep a lifecycle task list (see
  [Watching a run](../dev-flow/#watching-a-run)). The extra per-turn context
  this costs has not been measured. To opt out, set your own value for the
  variable; setup keeps it.
- `model` is set to the template's value (`opusplan`). Change it back with
  `/model` if you prefer another default.
- With `--link`, `settings.json` is symlinked instead of merged.

Re-running is idempotent. On a re-sync, setup also removes reference files
that an earlier release shipped and a later one replaced
(`references/java/java-best-practices.md`, `references/go/app-erp-conventions.md`),
but only when the file is unchanged or is a symlink into the plugin. A file you
edited is copied to the backup folder and left in place, and setup tells you.

**`--plugins` (opt-in).** `/addit-harness:setup --plugins` also runs
`claude plugin marketplace add` and `claude plugin install` for every
marketplace and every plugin set to `true` in the placed `settings.json`
(language servers, `pr-review-toolkit`, `figma` and others). It needs the
`claude` CLI on `PATH`. If an install fails from inside a session, run the
printed `claude plugin ...` command in a normal shell.

## Migrating from `install.sh`

`install.sh`, `sync_tools.py` and `tools.config.json` were removed; addit-harness
supports Claude Code only. To move to the plugin:

```
/plugin marketplace add addit-digital/addit-harness
/plugin install addit-harness@addit
/addit-harness:setup [--plugins]
```

With `--scope global`, setup retires the unprefixed copies the old script put
in `~/.claude/agents` and `~/.claude/skills`. A copy at least 50% similar (by
lines) to the plugin's version is backed up and then removed; a less similar
file with the same name is left alone and reported. Config already synced into
another tool keeps working but no longer updates; to keep using the old
installer, pin tag `addit-harness--v0.3.0`.

The `@addit-harness:feature-investigator` agent was renamed to
`@addit-harness:product-owner`; the old name no longer resolves.

## The `@addit-harness:` namespacing gotcha

Plugin-provided agents are **namespaced** — invoke them as
`@addit-harness:code-reviewer`, not bare `@code-reviewer`. This is the most
common "why isn't this working" moment for new installs. See
[Subagents](../subagents/) for the full list.

## Verify it worked

Run `/agents` — you should see `@addit-harness:code-reviewer` and the other
fourteen subagents listed. If they're missing, re-run
`/addit-harness:setup` and check the plugin installed without errors.

## All docs

The sidebar has the full list; here's the same thing with what each page
actually covers, so you don't have to click through page by page to find it:

**Start**
- [What's new](../whats-new/) — what changed in the upcoming release, including breaking changes
- [Concepts](../concepts/) — tiered conventions, curation philosophy, deterministic orchestration
- [The engineering loop](../engineering-loop/) — the loop, where documents go, and the doc protocol
- [How dev-flow works](../dev-flow/) — tiers, gates and loops, phase by phase
- [Example workflow](../example-workflow/) — one `/dev-flow` run, end to end

**Reference**
- [Subagents](../subagents/) — what each of the 15 subagents does, and its tools
- [Skills & commands](../skills-commands/) — every `/slash-command` this plugin adds
- [Model & cost](../model-cost/) — which subagent runs on which model, and how to cut spend
- [Enabling MCP](../mcp/) — connecting Jira, databases, and other optional integrations
- [Local telemetry](../telemetry/) — the opt-in, local-only usage log and its export

**Guides**
- [Use cases](../use-cases/) — concrete workflows showing which configs fire together
- [Extending](../extending/) — adding your own conventions, agents, or skills

**Project**
- [Roadmap](../roadmap/) — planned work and how to contribute
- [Changelog](../changelog/) — unreleased changes and every release
- [Privacy](../../privacy/) — what the plugin does and does not do with data
