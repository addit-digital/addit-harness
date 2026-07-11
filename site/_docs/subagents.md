---
title: Subagents
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
- [code-reviewer](#code-reviewer)
- [debugger](#debugger)
- [architect-reviewer](#architect-reviewer)
- [backend-architect](#backend-architect)
- [frontend-architect](#frontend-architect)
- [ux-designer](#ux-designer)
- [figma-designer](#figma-designer)
- [feature-investigator](#feature-investigator)
- [saas-legal-advisor](#saas-legal-advisor)
- [cloud-architect](#cloud-architect)
- [backend-developer](#backend-developer)
- [frontend-developer](#frontend-developer)
- [devops-engineer](#devops-engineer)
</div>

## code-reviewer

Reviews a diff or PR for correctness, security, and adherence to your
vendored language conventions — with file:line citations, not vague notes.
`opus` tier: a strong reviewer means less manual review for you.

## debugger

Isolates the root cause of a failing test or stack trace. `sonnet` tier;
escalate with `/model` if it gets stuck.

## architect-reviewer

Evaluates an existing architecture/design → a review report saved to
`docs/architecture-reports/`. `opus` tier: high-value, infrequent design
judgment.

## backend-architect

Up-front API/service design only (not implementation) → a design doc saved
to `docs/solutions/`. `opus` tier: design decisions prevent downstream
rework.

## frontend-architect

Up-front component/rendering/state design only (not implementation). Same
`opus` rationale as backend-architect.

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

## feature-investigator

Investigates a feature/product request before any code is written → produces
a spec/PRD-lite. `sonnet` tier — requirements investigation is the upstream
default.

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
security, disaster recovery. Defers implementation to devops-engineer.
`opus` tier — infra mistakes are costly and often hard to reverse.

## backend-developer

Implements and verifies backend code — Go, Java/Spring, TypeScript/Bun.
Senior-craftsman conventions: clean structure, tests, verification against
the vendored language conventions. `sonnet` tier — fast, cheap execution.

## frontend-developer

Implements and verifies frontend code — TypeScript/React/Next.js/React
Native. Same senior-craftsman conventions and `sonnet` tier as
backend-developer.

## devops-engineer

Writes and verifies the actual Terraform/Kubernetes manifests, Dockerfiles,
and CI pipelines against a cloud-architect design, plus hands-on Linux
systems administration (systemd, networking, SSH, logs). Prefers the
cloud/infra MCP servers in `mcp.example.json` when connected, falls back to
the provider CLI otherwise. `sonnet` tier — implementation against a design.

## Next

- [Use cases](../use-cases/) shows which of these fire together for a real
  feature build.
- [Model & cost](../model-cost/) has the full model-tier table and cost
  levers.
