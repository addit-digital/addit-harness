---
description: Print the short addit-harness guide (five tips). User-invoked only.
disable-model-invocation: true
---

<!--
This file exists only because Claude Code's plugin loader does not register
skills/*/SKILL.md as slash commands for marketplace-installed plugins
(anthropics/claude-code#18949, #57737) — only commands/*.md is indexed. Don't
delete this as a duplicate of the skill; it's the only way
`/addit-harness:tips` resolves and autocompletes until that's fixed
upstream. Keep the frontmatter above in sync with skills/tips/SKILL.md.
-->

Do not call the Skill tool: this skill is user-invoked only (`disable-model-invocation`), so
the Skill tool refuses it. Read `${CLAUDE_PLUGIN_ROOT}/skills/tips/SKILL.md` (your only tool call), then print the five tips in it to the user exactly as written, with no preamble and no commentary.
