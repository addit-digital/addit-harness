---
description: Scan the current TS/React project's existing UI layer and write .claude/design-conventions.md — a project-specific visual design convention file that rules/typescript.md loads before UI work. Use when starting UI work in an existing project, when design conventions have drifted, or when --refresh is passed to merge in new patterns.
argument-hint: "[--refresh]"
---

<!--
This file exists only because Claude Code's plugin loader does not register
skills/*/SKILL.md as slash commands for marketplace-installed plugins
(anthropics/claude-code#18949, #57737) — only commands/*.md is indexed. Don't
delete this as a duplicate of the skill; it's the only way
`/addit-harness:design-conventions` resolves and autocompletes until that's
fixed upstream. Keep the frontmatter above in sync with
skills/design-conventions/SKILL.md.
-->

Invoke the `addit-harness:design-conventions` skill via the Skill tool now,
forwarding any arguments given after the command: "$ARGUMENTS".
