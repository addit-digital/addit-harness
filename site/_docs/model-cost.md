---
title: Model & cost
description: Which model each subagent runs on, how explicit tool lists and dev-flow tiers keep token use down, and manual levers to cut spend.
nav_order: 6
nav_group: Reference
---

The goal is **good-enough model per task** to lower spend without hurting
code quality. Code quality is driven more by conventions + verification than
by raw model size, so a strong default plus tuned subagents goes a long way.

## Default model

`settings.json` sets `"model": "opusplan"` — Opus while planning, Sonnet
while executing. You get Opus-grade design (where rework is prevented) and
Sonnet's strong, cheaper execution against your rules.

Switch anytime with `/model` (pick + `Enter` to save as default, or `s` for
session-only). Drop to `sonnet` for routine work; bump to `opus`/`fable` when
a task is genuinely hard.

## Subagent routing

Set via `model:` in each agent's frontmatter (`agents/*.md`):

| Subagent | Model | Why |
|----------|-------|-----|
| `architect-reviewer` | `opus` | High-value, infrequent design judgment |
| `backend-architect` | `opus` | Design decisions prevent downstream rework |
| `frontend-architect` | `opus` | Rendering/state/component design — same rationale |
| `ux-designer` | `opus` | UX flow/journey/usability design — design-tier, upstream of frontend-architect |
| `figma-designer` | `sonnet` | Figma execution — materializes specs via MCP; execution-tier like developer agents |
| `code-reviewer` | `opus` | A strong reviewer = less *manual* review for you |
| `backend-developer` | `sonnet` | Implementation/execution — fast + cheap against the conventions |
| `frontend-developer` | `sonnet` | Implementation/execution — fast + cheap against the conventions |
| `debugger` | `sonnet` | Iterative; escalate with `/model` if stuck |
| `product-owner` | `sonnet` | Problem-statement framing (authored) |
| `saas-legal-advisor` | `opus` | Legal reasoning + compliance assessment — wrong guidance is costly |
| `cloud-architect` | `opus` | Infra design + review — mistakes are costly and often hard to reverse |
| `devops-engineer` | `sonnet` | Implementation/execution against a design |
| `qa-engineer` | `sonnet` | e2e/regression verification against a given scenario |
| `task-triager` | `sonnet` | Mechanical fact-gathering for `/dev-flow` triage; never returns a verdict |

Other mechanical agents (test-runners, formatters) should use `haiku` too.
Override all subagents at once with `CLAUDE_CODE_SUBAGENT_MODEL`.

## Built-in context savings

- **Explicit tool lists.** Every agent declares `tools:`, so it does not inherit every
  MCP server's tool schemas. For the four architect and design agents this cut
  first-turn context from about 33k to about 17k tokens in a controlled probe; your
  saving depends on which MCP servers you have connected. Full list on
  [Subagents](../subagents/#tools-per-agent).
- **Proportional `/dev-flow`.** Triage picks `light`, `standard` or `deep`. Worst-case
  agent calls for a whole run are 18, 46 and 50 (hard caps, mock-asserted, not measured
  live); a typical run makes fewer. At `deep` the skill warns that the design phase
  costs roughly 40–80% more tokens than `standard`; that range is the skill's own
  estimate, not a measurement. See [How dev-flow works](../dev-flow/#tiers--proportional-effort).

## Manual levers to cut tokens

- `/effort low|medium` for straightforward tasks (less thinking spend).
- `/clear` between unrelated tasks; `/context` to see what's using space;
  `/compact` near the limit.
- Delegate noisy work (test output, log scans, doc fetches) to a subagent —
  its output stays in *its* context, not yours.
- Prompt caching is automatic (CLAUDE.md/system prompt reused cheaply).
- Pin the background model with `ANTHROPIC_DEFAULT_HAIKU_MODEL`
  (`ANTHROPIC_SMALL_FAST_MODEL` is deprecated).

## Rough trade-off

Verify current pricing — but roughly: Haiku ≈ cheapest (mechanical work),
Sonnet ≈ daily-driver coding, Opus/Fable ≈ hardest reasoning at top cost.

## Next

- [Subagents](../subagents/) — full agent descriptions.
- [Concepts](../concepts/) — why "good-enough model per task" is the design
  goal, not just a cost note.
