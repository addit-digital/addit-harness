---
description: Use when the user wants to save, export, or persist a plan (or any diagram-rich design doc shown in the CLI) to a markdown file so it can be opened and viewed with rendered mermaid diagrams. The terminal can't render mermaid; this writes the plan to docs/plans/ (or a temp scratch file) for viewing in an IDE preview or on GitHub.
argument-hint: "[short plan title] [--temp]"
---

<!--
This file exists only because Claude Code's plugin loader does not register
skills/*/SKILL.md as slash commands for marketplace-installed plugins
(anthropics/claude-code#18949, #57737) — only commands/*.md is indexed. Don't
delete this as a duplicate of the skill; it's the only way
`/addit-harness:save-plan` resolves and autocompletes until that's fixed
upstream. Keep the frontmatter above in sync with skills/save-plan/SKILL.md.
-->

Invoke the `addit-harness:save-plan` skill via the Skill tool now, forwarding
any arguments given after the command: "$ARGUMENTS".
