---
description: Use to drive a software feature or fix through the full engineering loop — investigate, design (with an architect-reviewer gate), get your explicit approval on the plan, then implement, verify with qa-engineer, and drive the code-review fix loop to a clean state. Deterministic multi-agent orchestration for the design-gate and review-gate loops this setup's engineering-loop rule already describes, so you don't have to hand-drive each Agent call yourself. Software-development-lifecycle scoped (not a generic router) — for legal or marketing work, use the relevant subagent directly.
argument-hint: "[what to build or fix] [--tier light|standard|deep]"
---

<!--
This file exists only because Claude Code's plugin loader does not register
skills/*/SKILL.md as slash commands for marketplace-installed plugins
(anthropics/claude-code#18949, #57737) — only commands/*.md is indexed. Don't
delete this as a duplicate of the skill; it's the only way
`/addit-harness:dev-flow` resolves and autocompletes until that's fixed
upstream. Keep the frontmatter above in sync with skills/dev-flow/SKILL.md.
-->

Invoke the `addit-harness:dev-flow` skill via the Skill tool now, forwarding
any arguments given after the command: "$ARGUMENTS".
