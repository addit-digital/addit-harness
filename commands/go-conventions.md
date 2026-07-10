---
description: Scan the current Go repo and write .claude/go-conventions.md — a project-specific convention file that rules/go.md loads on every session instead of re-scanning the codebase from scratch. Use when starting work in a new Go repo, when conventions have drifted, or when --refresh is passed to merge in new patterns.
argument-hint: "[--refresh]"
---

<!--
This file exists only because Claude Code's plugin loader does not register
skills/*/SKILL.md as slash commands for marketplace-installed plugins
(anthropics/claude-code#18949, #57737) — only commands/*.md is indexed. Don't
delete this as a duplicate of the skill; it's the only way
`/addit-harness:go-conventions` resolves and autocompletes until that's
fixed upstream. Keep the frontmatter above in sync with
skills/go-conventions/SKILL.md.
-->

Invoke the `addit-harness:go-conventions` skill via the Skill tool now,
forwarding any arguments given after the command: "$ARGUMENTS".
