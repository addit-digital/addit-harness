---
description: Build a summary page (data.json + offline report.html) from the local addit-harness telemetry log; optionally, only if you say yes when asked, publish aggregated KPIs as a private Artifact on claude.ai (this uploads them to Anthropic's hosted service under your account). Needs the telemetry_local option on. User-invoked only.
argument-hint: "[--days N]"
disable-model-invocation: true
---

<!--
This file exists only because Claude Code's plugin loader does not register
skills/*/SKILL.md as slash commands for marketplace-installed plugins
(anthropics/claude-code#18949, #57737) — only commands/*.md is indexed. Don't
delete this as a duplicate of the skill; it's the only way
`/addit-harness:telemetry-export` resolves and autocompletes until that's fixed
upstream. Keep the frontmatter above in sync with skills/telemetry-export/SKILL.md.
-->

Do not call the Skill tool: this skill is user-invoked only (`disable-model-invocation`), so
the Skill tool refuses it. Read `${CLAUDE_PLUGIN_ROOT}/skills/telemetry-export/SKILL.md` and follow
its steps exactly, forwarding any arguments given after the command: "$ARGUMENTS".
In that file, `${CLAUDE_PLUGIN_ROOT}` is `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` is
`${CLAUDE_PLUGIN_DATA}` (already resolved here); use those literal paths in the commands.
