---
title: Subagents
description: The 15 subagents addit-harness ships, what each one does, which model it runs on, and which tools it is allowed.
nav_order: 3
nav_group: Reference
---

Delegate isolated work to keep your main context clean. Every subagent below
ships with the plugin and is namespaced — invoke it as
`@addit-harness:<name>`, not bare `@<name>` (see
[the namespacing gotcha](../getting-started/#the-addit-harness-namespacing-gotcha)).
Model tiers are covered in full on [Model & cost](../model-cost/).

<div class="docs-toc" markdown="1">
**On this page**
- [Tools per agent](#tools-per-agent)
- [code-reviewer](#code-reviewer)
- [debugger](#debugger)
- [architect-reviewer](#architect-reviewer)
- [backend-architect](#backend-architect)
- [frontend-architect](#frontend-architect)
- [ux-designer](#ux-designer)
- [figma-designer](#figma-designer)
- [product-owner](#product-owner)
- [saas-legal-advisor](#saas-legal-advisor)
- [cloud-architect](#cloud-architect)
- [backend-developer](#backend-developer)
- [frontend-developer](#frontend-developer)
- [devops-engineer](#devops-engineer)
- [qa-engineer](#qa-engineer)
- [task-triager](#task-triager)
</div>

## Tools per agent

Every agent declares an explicit `tools:` list in its frontmatter. An agent without
one inherits every tool in the session, including the schemas of every connected MCP
server, and those schemas are loaded into its context on the first turn. Adding
`tools:` to the four architect and design agents (`backend-architect`,
`frontend-architect`, `cloud-architect`, `ux-designer`) cut their first-turn context
from about 33k to about 17k tokens in a controlled probe. The exact saving depends
on which MCP servers you have connected.

| Agent | Model | Tools |
|---|---|---|
| `architect-reviewer` | `opus` | Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch |
| `backend-architect` | `opus` | Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch |
| `frontend-architect` | `opus` | Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch |
| `cloud-architect` | `opus` | Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch |
| `ux-designer` | `opus` | Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Figma MCP |
| `saas-legal-advisor` | `opus` | Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch |
| `code-reviewer` | `opus` | Read, Write, Edit, Bash, Glob, Grep |
| `product-owner` | `sonnet` | Read, Write, Glob, Grep, WebFetch, WebSearch |
| `figma-designer` | `sonnet` | Read, Glob, Grep, Skill, Figma MCP |
| `backend-developer` | `sonnet` | Read, Write, Edit, Bash, Glob, Grep |
| `frontend-developer` | `sonnet` | Read, Write, Edit, Bash, Glob, Grep |
| `devops-engineer` | `sonnet` | Read, Write, Edit, Bash, Glob, Grep |
| `debugger` | `sonnet` | Read, Write, Edit, Bash, Glob, Grep |
| `qa-engineer` | `sonnet` | Read, Write, Edit, Bash, Glob, Grep, Claude in Chrome |
| `task-triager` | `haiku` | Read, Glob, Grep |

## code-reviewer

Reviews a diff or PR for correctness, security, and adherence to your
language conventions — with file:line citations, not vague notes. Go and Java
findings cite the rule ids (`G-…`, `J-…`). For `.ts`/`.tsx` diffs it runs a
measured frontend checklist against the
[Frontend Implementation Contract](../concepts/#frontend-implementation-contract)
(FC-1..FC-10): line counts come from `grep`, FC-3 and FC-5 only from ESLint output,
and each finding states the measured value against the limit.
`opus` tier: a strong reviewer means less manual review for you.

## debugger

Isolates the root cause of a failing test or stack trace. `sonnet` tier;
escalate with `/model` if it gets stuck.

## architect-reviewer

Evaluates an existing architecture/design → a review report saved to
`docs/work/<slug>/architecture-reports/`. `opus` tier: high-value, infrequent
design judgment.

## backend-architect

Up-front API/service design only (not implementation) → a design doc saved
to `docs/work/<slug>/solutions/`. Follows the
[solution method](../engineering-loop/#the-solution-method): at least three
structurally different candidates, one of them unconventional, prior art, a
pre-mortem, and your own proposal scored only at the comparison step. `opus` tier:
design decisions prevent downstream rework.

## frontend-architect

Up-front component/rendering/state design only (not implementation), using the
same solution method. Same `opus` rationale as backend-architect.

## ux-designer

User flows, journey maps, IA, wireframes, interaction specs, and usability
audits. Reads the project's design system, bridges UX to UI patterns, and
defers component/token/a11y architecture to frontend-architect. `opus` tier —
design-tier, upstream of frontend-architect.

## figma-designer

Materializes UX specs into Figma frames, components, auto-layout, variables,
and tokens via the official Figma MCP. Composes downstream of ux-designer;
requires the `figma@claude-plugins-official` plugin. `sonnet` tier —
execution-tier, like the developer agents.

## product-owner

Replaces `feature-investigator`, which no longer resolves. Frames a feature, fix or
product request as a problem statement before any design: who is affected, current
versus desired behaviour (with `path:line` evidence), constraints, non-goals and
Given/When/Then acceptance criteria. It never proposes a solution; a solution in the
request is copied verbatim under "Owner's proposed approach (unevaluated)". Inside
`/dev-flow` it also runs the [intake interview and brief](../dev-flow/#intake--interview-and-brief).
`sonnet` tier.

## saas-legal-advisor

SaaS-specialized legal advisor — assesses the legal impact of product
changes and drafts/reviews privacy policies, T&Cs, cookie policies, and DPAs.
Reads the project's declared primary jurisdiction from `CLAUDE.md`. Use
proactively whenever a feature touches user data, payments, third-party
integrations, or account types. `opus` tier — wrong legal guidance is
costly.

## cloud-architect

Multi-cloud/Kubernetes infrastructure design **and** audits of existing
infrastructure (AWS/Azure/GCP/OCI/DigitalOcean) — IaC strategy, cost,
security, disaster recovery. New designs follow the same solution method as the
other architects. Defers implementation to devops-engineer.
`opus` tier — infra mistakes are costly and often hard to reverse.

## backend-developer

Implements and verifies backend code — Go, Java/Spring, TypeScript/Bun.
Senior-craftsman conventions: clean structure, tests, verification against
the vendored language conventions. `sonnet` tier — fast, cheap execution.

## frontend-developer

Implements and verifies frontend code — TypeScript/React/Next.js/React
Native. Builds a reuse inventory before writing, and writes to the
[Frontend Implementation Contract](../concepts/#frontend-implementation-contract)
(FC-1..FC-10); exceeding a limit needs a one-line reason in its report. Same
`sonnet` tier as backend-developer.

## devops-engineer

Writes and verifies the actual Terraform/Kubernetes manifests, Dockerfiles,
and CI pipelines against a cloud-architect design, plus hands-on Linux
systems administration (systemd, networking, SSH, logs). Prefers the
cloud/infra MCP servers in `mcp.example.json` when connected, falls back to
the provider CLI otherwise. `sonnet` tier — implementation against a design.

## qa-engineer

Verifies an implemented feature via e2e/regression testing — writes scenarios,
implements them as executable test code (Playwright, Maestro, or whatever fits
the target repo), runs them, and reports with mandatory evidence per claim. Not
unit/integration tests (stays with the developer agents); web verification
requires `claude-in-chrome` connected. `sonnet` tier — execution against a given
scenario, not designing one.

## task-triager

Answers a fixed fact questionnaire about a change request (which files, which risk
surfaces, what checks exist) for `dev-flow`'s triage step. Read-only (`Read`,
`Glob`, `Grep`) and never returns a verdict — a deterministic script scores the
facts into a tier. `haiku` tier.

## Next

- [Use cases](../use-cases/) shows which of these fire together for a real
  feature build.
- [Model & cost](../model-cost/) has the full model-tier table and cost
  levers.
