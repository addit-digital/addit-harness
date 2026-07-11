---
title: Skills & commands
nav_order: 4
nav_group: Reference
---

## Namespacing

Like the [subagents](../subagents/), plugin-provided commands can be
namespaced — `/addit-harness:setup` is the one that always needs the prefix
(there's a bare `setup` collision risk). If a slash command doesn't respond,
try the `addit-harness:` prefix before assuming it's missing.

## Skills this repo ships

| Command | What it does |
|---------|---------------|
| `/adr` | Record an Architecture Decision Record (**MADR 4.0**) |
| `/save-plan` | Persist an implementation plan to `docs/plans/` (or `--temp`) so mermaid renders in an IDE/GitHub |
| `/go-conventions [--refresh]` | Scan a Go repo and write `.claude/go-conventions.md` — the project-specific layer on top of the global Go baseline |
| `/design-conventions [--refresh]` | Scan a TS/React project's existing UI layer and write `.claude/design-conventions.md` (tokens, type/spacing/color scales, component lib, layout rhythm, state patterns) |
| `/addit-harness:setup [--scope global\|project] [--link]` | Places `CLAUDE.md`/`AGENTS.md`/`rules/`/`references/`/`settings.json` for Claude Code — the parts the plugin can't carry natively |

`docs/solutions/` (architecture designs) and `docs/architecture-reports/`
(review reports) are written directly by the relevant subagent, not through a
skill — only implementation plans go through `/save-plan`.

## Claude Code's own built-ins (reused, not reinvented)

The philosophy here is to reuse what Claude Code already ships rather than
hand-roll a competing skill:

- `/code-review` — review a diff or PR (see
  [Use cases](../use-cases/#review-pull-requests-on-github-subscription-only-no-api-key)).
- `/simplify` — reduce complexity in existing code.
- `/verify` — run the project's tests/build/lint and report real output.
- `/run` — execute a command with output surfaced back into context.
- `/init` — bootstrap a new `CLAUDE.md` for a repo.
- `deep-research` — multi-step research task.

## Official plugins (declared in `settings.json`)

Enabled from the auto-available `claude-plugins-official` marketplace (+
`anthropics/skills`). The big win is real **language servers**: `gopls-lsp`,
`jdtls-lsp`, `typescript-lsp`, plus `pr-review-toolkit`, `commit-commands`,
`security-guidance`, and `document-skills` (doc generation). They install on
first start, or run `./install.sh --plugins` to do it now.

## Iterating & giving feedback on plans or code

The "no way to say change this" problem is mostly a terminal UI gap:

| Scenario | What to do |
|----------|-----------|
| Revising a plan | Choose **"Keep planning with feedback"** when Claude presents a plan. Type your correction and Claude stays in plan mode. `Ctrl+G` opens the plan file in your editor to edit directly. |
| Inline comments on code (web) | Open the diff view → click any line → leave a comment. Comments queue and bundle with your next message. |
| Feedback in the terminal | No line-selection UI — reference code as `pkg/sales/service.go:45`, or paste the relevant lines. `Esc` interrupts Claude mid-run to redirect it. |
| Browser plan review | Run `/ultraplan <task>` → open the browser link → leave inline comments → iterate before executing. |

## Next

- [Subagents](../subagents/) — the agents these commands and plugins support.
- [Use cases](../use-cases/) — commands and agents in a real workflow.
