# Vendored subagents — provenance

These role subagents are vendored (copied) from established community
collections and **pinned to a specific commit** for reproducibility. To update
one, re-fetch from the source repo at a newer commit, replace the file, and bump
the SHA below.

Retrieved: 2026-06-18.

| File | Source repo | Path | Pinned commit | Changes |
|------|-------------|------|---------------|---------|
| `code-reviewer.md` | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | `categories/04-quality-security/code-reviewer.md` | `5983fe3b4ea2785335ac1712c4aa1ac4e13a8fa2` | body verbatim + a local "Project convention adherence" section appended (instructs it to read `references/<lang>/` and report rule violations) |
| `debugger.md` | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | `categories/04-quality-security/debugger.md` | `5983fe3b4ea2785335ac1712c4aa1ac4e13a8fa2` | verbatim |
| `architect-reviewer.md` | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | `categories/04-quality-security/architect-reviewer.md` | `5983fe3b4ea2785335ac1712c4aa1ac4e13a8fa2` | verbatim |
| `backend-architect.md` | [wshobson/agents](https://github.com/wshobson/agents) | `plugins/backend-development/agents/backend-architect.md` | `cc37bfdd292ce520ba1c44df7a3a70d5f8137236` | `name` changed from `backend-development-backend-architect` to `backend-architect`; `model` changed from `inherit` to `opus` (design quality, infrequent/high-value); `description` scoped to **design only** (dropped "Use PROACTIVELY when creating new backend services" → defers implementation to `backend-developer`/`frontend-developer`, so it stops poaching coding tasks); body otherwise verbatim |
| `feature-investigator.md` | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | `categories/08-business-product/business-analyst.md` | `5983fe3b4ea2785335ac1712c4aa1ac4e13a8fa2` | `name` → `feature-investigator` and `description` adjusted to "investigate a feature/product request before building" (so it triggers correctly); `tools`/`model: sonnet`/body verbatim. Companion option: `project-idea-validator` (same repo, `categories/10-research-analysis/`) for product go/no-go validation. |
| `backend-developer.md` | **Authored** (not vendored) | — | — | Backend implementation agent: a senior backend engineer + software craftsman (Go · Java/Spring) that designs clean structures, writes test cases, and verifies code following this setup's `references/{go,java}/` guides and `rules/{go,java}.md`. Authored because there was no implementation agent to adopt and the closest upstream candidate couldn't be copied verbatim through available tooling. Body aligns with `CLAUDE.md` hard rules + the engineering loop; `model: sonnet` for fast execution. |
| `frontend-developer.md` | **Authored** (not vendored) | — | — | Frontend implementation agent: a senior frontend engineer + software craftsman (TS/React/Next/RN) that designs clean component structures, writes test cases, and verifies code following `references/typescript/` and `rules/typescript.md`. Authored for the same reasons as `backend-developer`; `model: sonnet`. To swap either to a vendored copy later, re-fetch the upstream file at a pinned commit, append a "Project convention adherence" section like `code-reviewer`, and update this row. |
| `ux-designer.md` | **Authored (blended)** — lifts journey mapping, usability heuristics, and persona sections from [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) `categories/08-business-product/ux-researcher.md` and interaction/state-design patterns from `categories/01-core-development/ui-designer.md`, both at pinned commit `5983fe3b4ea2785335ac1712c4aa1ac4e13a8fa2` | — | Authored because no single upstream agent covers the UX flow layer (flows/journeys/IA/wireframes/usability audits + UI-pattern advisory) without heavily duplicating the existing `frontend-architect`. Follows the architect skeleton (`model: opus`, no `tools` key, saves to `docs/solutions/`). Scope: consumes `.claude/design-conventions.md`; defers token/component/ARIA architecture to `@frontend-architect`. |
| `figma-designer.md` | **Authored** (not vendored) | — | — | Figma execution agent: materializes UX specs and design-system conventions into Figma frames, components, auto-layout, variables, and tokens via the official Figma MCP server (`mcp.figma.com`). Authored because no upstream agent drives Figma write-to-canvas; composes downstream of `@ux-designer`. `model: sonnet` (execution-tier); `tools: Read, Glob, Grep` (focused executor — MCP tools are additive from the connected Figma server). Requires `figma@claude-plugins-official` plugin + Figma remote MCP connected. |

## Subagent model routing
Models are tuned for cost/quality (see README → Model & cost): `code-reviewer`
and `architect-reviewer` = `opus` (upstream), `backend-architect` = `opus`
(changed from `inherit`), `debugger` = `sonnet` (upstream), `feature-investigator`
= `sonnet` (upstream), `backend-developer` and `frontend-developer` = `sonnet`
(authored), `ux-designer` = `opus` (authored — design-tier, same rationale as
architects), `figma-designer` = `sonnet` (authored — execution-tier, same
rationale as developer agents). Override any of these by editing the `model:`
field, or globally via `CLAUDE_CODE_SUBAGENT_MODEL`.

## Notes
- Both source repos track `main` with no tagged releases — that's why we vendor
  and pin rather than installing live from a marketplace.
- The VoltAgent agents reference a multi-agent "context manager" protocol (JSON
  query blocks). That's harmless here — Claude treats it as role guidance — but
  it's noise you can trim if you want leaner files.
- Per-language conventions live in `references/<lang>/` (vendored from recognized
  sources); the always-on `rules/<lang>.md` are thin pointers to them. The
  `code-reviewer` is wired to check adherence to those references.
