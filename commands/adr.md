---
description: Use when the user makes or records a significant architectural or technical decision — choosing a framework, database, protocol, pattern, or trade-off ("we decided to use X instead of Y because..."), or explicitly asks to write an ADR. Captures the decision as a structured MADR-format Architecture Decision Record in docs/adr/.
argument-hint: "[short decision title] [--full | --minimal]"
---

<!--
This file exists only because Claude Code's plugin loader does not register
skills/*/SKILL.md as slash commands for marketplace-installed plugins
(anthropics/claude-code#18949, #57737) — only commands/*.md is indexed. Don't
delete this as a duplicate of the skill; it's the only way
`/addit-harness:adr` resolves and autocompletes until that's fixed upstream.
Keep the frontmatter above in sync with skills/adr/SKILL.md.
-->

Invoke the `addit-harness:adr` skill via the Skill tool now, forwarding any
arguments given after the command: "$ARGUMENTS".
