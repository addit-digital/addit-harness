---
title: Model & cost
nav_order: 5
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
| `feature-investigator` | `sonnet` | Requirements/spec investigation (upstream default) |
| `saas-legal-advisor` | `opus` | Legal reasoning + compliance assessment — wrong guidance is costly |
| `cloud-architect` | `opus` | Infra design + review — mistakes are costly and often hard to reverse |
| `devops-engineer` | `sonnet` | Implementation/execution against a design |

Future mechanical agents (test-runners, formatters) should use `haiku`.
Override all subagents at once with `CLAUDE_CODE_SUBAGENT_MODEL`.

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
