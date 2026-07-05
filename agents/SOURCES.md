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
| `backend-architect.md` | [wshobson/agents](https://github.com/wshobson/agents) | `plugins/backend-development/agents/backend-architect.md` | `cc37bfdd292ce520ba1c44df7a3a70d5f8137236` | `name` changed from `backend-development-backend-architect` to `backend-architect`; `model` changed from `inherit` to `opus` (design quality, infrequent/high-value); `description` scoped to **design only** (dropped "Use PROACTIVELY when creating new backend services" → defers implementation to `backend-developer`/`frontend-developer`, so it stops poaching coding tasks); body otherwise verbatim, except one bullet added under "Framework & Technology Expertise" (2026-07-05) noting Bun-native frameworks (Elysia, Hono) alongside the existing Node.js bullet |
| `feature-investigator.md` | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | `categories/08-business-product/business-analyst.md` | `5983fe3b4ea2785335ac1712c4aa1ac4e13a8fa2` | `name` → `feature-investigator` and `description` adjusted to "investigate a feature/product request before building" (so it triggers correctly); `tools`/`model: sonnet`/body verbatim. Companion option: `project-idea-validator` (same repo, `categories/10-research-analysis/`) for product go/no-go validation. |
| `backend-developer.md` | **Authored** (not vendored) | — | — | Backend implementation agent: a senior backend engineer + software craftsman (Go · Java/Spring · TypeScript/Bun) that designs clean structures, writes test cases, and verifies code following this setup's `references/{go,java,typescript}/` guides and `rules/{go,java,typescript}.md`. Authored because there was no implementation agent to adopt and the closest upstream candidate couldn't be copied verbatim through available tooling. TypeScript/Bun support added 2026-07-05, backed by the new `references/typescript/backend/` (vendored `bun.mdc`) — routes to that subtree, not the frontend `references/typescript/react/` tree used by `frontend-developer`. Body aligns with `CLAUDE.md` hard rules + the engineering loop; `model: sonnet` for fast execution. |
| `frontend-developer.md` | **Authored** (not vendored) | — | — | Frontend implementation agent: a senior frontend engineer + software craftsman (TS/React/Next/RN) that designs clean component structures, writes test cases, and verifies code following `references/typescript/` and `rules/typescript.md`. Authored for the same reasons as `backend-developer`; `model: sonnet`. To swap either to a vendored copy later, re-fetch the upstream file at a pinned commit, append a "Project convention adherence" section like `code-reviewer`, and update this row. |
| `ux-designer.md` | **Authored (blended)** — lifts journey mapping, usability heuristics, and persona sections from [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) `categories/08-business-product/ux-researcher.md` and interaction/state-design patterns from `categories/01-core-development/ui-designer.md`, both at pinned commit `5983fe3b4ea2785335ac1712c4aa1ac4e13a8fa2` | — | Authored because no single upstream agent covers the UX flow layer (flows/journeys/IA/wireframes/usability audits + UI-pattern advisory) without heavily duplicating the existing `frontend-architect`. Follows the architect skeleton (`model: opus`, no `tools` key, saves to `docs/solutions/`). Scope: consumes `.claude/design-conventions.md`; defers token/component/ARIA architecture to `@frontend-architect`. |
| `figma-designer.md` | **Authored** (not vendored) | — | — | Figma execution agent: materializes UX specs and design-system conventions into Figma frames, components, auto-layout, variables, and tokens via the official Figma MCP server (`mcp.figma.com`). Authored because no upstream agent drives Figma write-to-canvas; composes downstream of `@ux-designer`. `model: sonnet` (execution-tier); `tools: Read, Glob, Grep` (focused executor — MCP tools are additive from the connected Figma server). Requires `figma@claude-plugins-official` plugin + Figma remote MCP connected. |
| `saas-legal-advisor.md` | **Authored (blended)** — lifts focus areas, key regulations, and document types from [wshobson/agents](https://github.com/wshobson/agents) `plugins/hr-legal-compliance/agents/legal-advisor.md` at pinned commit `56848874a27cf0812b20a067ff3cf4eb8e0a7858` | — | `name` changed from `legal-advisor` to `saas-legal-advisor`; `model` changed from `sonnet` to `opus` (advisory-tier, same rationale as `architect-reviewer` and `ux-designer`); `tools` extended with `WebFetch, WebSearch` for regulatory research; body significantly augmented with: (1) Change Impact Analysis — the core gap no upstream agent covers: given a feature/PR/integration, identify which legal docs and clauses need updating, rate severity, and draft the updated clauses; (2) Document Review & Gap Analysis section; (3) SaaS-Specific Clauses section; (4) Workflow Position within this setup; (5) structured output format with impact tables and gap analysis tables; (6) `docs/legal/` output folder convention. |

## Subagent model routing
Models are tuned for cost/quality (see README → Model & cost): `code-reviewer`
and `architect-reviewer` = `opus` (upstream), `backend-architect` = `opus`
(changed from `inherit`), `debugger` = `sonnet` (upstream), `feature-investigator`
= `sonnet` (upstream), `backend-developer` and `frontend-developer` = `sonnet`
(authored), `ux-designer` = `opus` (authored — design-tier, same rationale as
architects), `figma-designer` = `sonnet` (authored — execution-tier, same
rationale as developer agents), `saas-legal-advisor` = `opus` (authored — advisory-tier;
legal reasoning and compliance assessment are high-stakes and benefit from strongest
synthesis). Override any of these by editing the `model:` field, or globally via
`CLAUDE_CODE_SUBAGENT_MODEL`.

## Notes
- Both source repos track `main` with no tagged releases — that's why we vendor
  and pin rather than installing live from a marketplace.
- The VoltAgent agents reference a multi-agent "context manager" protocol (JSON
  query blocks). That's harmless here — Claude treats it as role guidance — but
  it's noise you can trim if you want leaner files.
- Per-language conventions live in `references/<lang>/` (vendored from recognized
  sources); the always-on `rules/<lang>.md` are thin pointers to them. The
  `code-reviewer` is wired to check adherence to those references.
