---
description: Use once, right after installing the addit-harness Claude Code plugin, to place the parts a plugin can't carry natively (CLAUDE.md, AGENTS.md, path-scoped rules/, references/, settings.json) into ~/.claude or the current project. Also use to re-sync after a plugin update, or to switch between global and project scope.
argument-hint: "[--scope global|project] [--link]"
---

<!--
This file exists only because Claude Code's plugin loader does not register
skills/*/SKILL.md as slash commands for marketplace-installed plugins
(anthropics/claude-code#18949, #57737) — only commands/*.md is indexed. Don't
delete this as a duplicate of the skill; it's the only way
`/addit-harness:setup` resolves and autocompletes until that's fixed
upstream. Keep the frontmatter above in sync with skills/setup/SKILL.md.
-->

Invoke the `addit-harness:setup` skill via the Skill tool now, forwarding
any arguments given after the command: "$ARGUMENTS".
