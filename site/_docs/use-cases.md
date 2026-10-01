---
title: Use cases
description: Concrete workflows showing which addit-harness agents, skills and commands fire together, from a feature build to legal review.
nav_order: 9
nav_group: Guides
---

Concrete workflows showing which configs fire together.

## Build a new feature

`/dev-flow` automates this exact walkthrough end-to-end — triage → intake brief →
design ⇄ `@architect-reviewer` loop → your approval gate → implement →
`@code-reviewer` ⇄ fix loop → `@qa-engineer` verifies once — as deterministic
`Workflow` scripts instead of hand-driving each step below yourself. The
[example workflow](../example-workflow/) follows one run from start to finish. The steps below still
apply if you'd rather drive them by hand, or when the request doesn't fit the
software-development-lifecycle shape `/dev-flow` is scoped to. See
[How dev-flow works](../dev-flow/) for the phase-by-phase mechanics.

```mermaid
flowchart LR
  FI["@product-owner\nproblem statement"]
  LA["@saas-legal-advisor *(if data/payments/integrations)*\nlegal impact → doc updates"]
  UX["@ux-designer\nflows · wireframes · IA"]
  FG["@figma-designer *(optional)*\nFigma frames + tokens"]
  FA["@frontend-architect\ncomponent architecture"]
  SP["/save-plan → docs/work/<slug>/plans/\nTaskCreate tracked steps"]
  BD["@backend-developer"]
  FE["@frontend-developer"]
  QA["@qa-engineer\ne2e/regression verify"]
  CR["@code-reviewer\nconventions + security"]

  FI --> LA
  FI --> UX
  LA --> SP
  UX --> FG
  UX --> FA
  FG --> FA
  FA --> SP
  SP --> BD & FE
  BD --> CR
  FE --> CR
  CR --> QA
```

1. `@product-owner` → problem statement (never a solution) before any design.
2. `@saas-legal-advisor` *(if the feature touches user data, payments,
   third-party integrations, or account types)* → runs in parallel with UX
   design; produces an impact table (Critical/Important/Advisory) and drafts
   updated legal clauses. Saves the assessment to docs/work/<slug>/legal/assessment.md. Legal doc
   updates ship before or with the feature — not after.
3. `@ux-designer` → user flows, journey map, IA, wireframes, state matrix,
   and interaction specs. Reads `.claude/design-conventions.md`; flags
   design-system gaps for `@frontend-architect`. Saves the spec to
   `docs/work/<slug>/solutions/`.
4. `@figma-designer` *(optional)* → materializes the UX spec into Figma
   frames, components, auto-layout, and tokens via the official Figma MCP.
5. `@frontend-architect` → component/rendering/state architecture informed
   by the UX spec; resolves any design-system gaps flagged upstream.
6. Plan it — a diagram-rich plan (mermaid), then `/save-plan` →
   `docs/work/<slug>/plans/`. TaskCreate a tracked task list from the plan's
   phased steps so status is visible; TaskUpdate each task as it completes.
7. Implement — `@backend-developer` and/or `@frontend-developer` write +
   verify the code; Tier-1 `rules/<lang>.md` auto-load per file type.
8. `@code-reviewer` → checks correctness, security, *and* adherence to the
   language conventions (file:line violations); fix and re-review until clean.
9. `@qa-engineer` → verifies the reviewed feature via e2e/regression
   testing, evidence-backed (a separate, UI-level check from the unit/
   integration tests in step 7).

## Review or debug existing code

- `@code-reviewer` on a diff — flags convention violations with file:line.
- `@debugger` for a failing test or stack trace — isolates root cause.

## Design or implement infrastructure

- `@cloud-architect` for up-front design (new environment, migration,
  multi-cloud strategy) → design doc saved to `docs/work/<slug>/solutions/`.
- `@cloud-architect` to **audit existing infrastructure** (cost, security,
  reliability, IaC drift) → review report saved to
  `docs/work/<slug>/architecture-reports/` with Critical/Important/Advisory findings.
- `@devops-engineer` implements the design or acts on the review's findings
  — Terraform/Kubernetes manifests, Dockerfiles, CI config, edge security
  (Cloudflare WAF/DDoS/Zero Trust or the hyperscaler-native equivalent), and
  vulnerability/IaC/secrets scanning per the design.
- Both prefer the AWS/Azure/DigitalOcean/Terraform/Kubernetes/Docker/
  Cloudflare MCP servers when connected (see [Enabling MCP](../mcp/)),
  falling back to the provider CLI otherwise. Google Cloud has no unified
  official MCP server yet, so GCP work falls back to `gcloud` directly.

## Make an architecture decision

- `@backend-architect` (API/service) or `@frontend-architect`
  (component/rendering/state) produce a design doc → saved to
  `docs/work/<slug>/solutions/solution-<track>.md`.
- `@architect-reviewer` evaluates an existing design → saved to
  `docs/work/<slug>/architecture-reports/report.md`.
- Record the decision with `/adr` (MADR) under `docs/adr/`.

## Assess legal impact before shipping a feature

Before a feature that touches user data, payments, or third-party services
ships, invoke `@saas-legal-advisor` with the feature description or PR diff.
It produces an impact table (Critical / Important / Advisory) mapping each
change to the specific legal document and clause affected, then drafts the
updated clause(s). Assessment → docs/work/<slug>/legal/assessment.md; standing docs updated in docs/legal/<document-kind>.md — update the
live documents before or alongside the feature, never after.

```
@saas-legal-advisor "We're adding Stripe Connect, storing payment method
tokens, and sending transactional emails via Resend — what needs to change
in our legal docs?"
```

## Review or draft legal documents

- Audit: `@saas-legal-advisor "Audit our Privacy Policy against current GDPR requirements"`
- Draft: `@saas-legal-advisor "Write a Data Processing Agreement for enterprise customers"`
- The agent reads the project's `CLAUDE.md` for the declared primary
  jurisdiction and applies that framework first. Add secondary
  jurisdictions (e.g. GDPR for EU users) in your request or in `CLAUDE.md`.

## New third-party integration

Any new SDK, API, or analytics tool is a legal event — it introduces a new
data processor and may require cookie consent, privacy policy updates, or
DPA amendments. Ask `@saas-legal-advisor` with the integration name before
the code ships.

## Day-to-day coding in Go / Java / TS

Just open the file — language conventions auto-apply (Tier 1) and the
reviewer enforces them; no command needed. Claude pulls deeper `references/`
only for substantial work.

## Keep costs down

Default `opusplan` (Opus plans, Sonnet executes); `/model` to switch,
`/effort low` for simple tasks, and delegate noisy work to subagents. See
[Model & cost](../model-cost/).

## Review pull requests on GitHub (subscription-only, no API key)

Two paths — both work on Pro/Max, no `ANTHROPIC_API_KEY` needed:

| Path | Setup | When to use |
|------|-------|-------------|
| **Local on-demand** | None — just be logged in | Quick reviews before a push, or when CI isn't set up |
| **Automated CI** | `claude setup-token` → add secret → copy workflow | Every PR auto-reviewed on open/push |

*Local (works right now):*

```
/code-review #<pr-number> --comment
```

Uses your `/login` subscription credentials. Posts inline comments on the PR
diff via the GitHub MCP server. No secret or token needed.

*Automated CI:* see
[`addit-digital/addit-actions`](https://github.com/addit-digital/addit-actions)
— a reusable `workflow_call` workflow. Copy the caller into any app repo's
`.github/workflows/`, add `CLAUDE_CODE_OAUTH_TOKEN` as a repo secret
(`claude setup-token` → `gh secret set`), and Claude reviews every PR
automatically.

> **Caveats:** CI runs consume your Pro/Max quota. The OAuth token
> (`setup-token`) lasts ~1 year.

## Connect Jira / a database

Enable the relevant server from `mcp.example.json`. See
[Enabling MCP](../mcp/).

## Set up a specific repo

Copy `templates/CLAUDE.project.md` → the repo's `./CLAUDE.md` for
codebase-specific facts (keep them out of global memory).

## Next

- [Subagents](../subagents/) — full descriptions of every agent used above.
- [Extending](../extending/) — add a new rule, subagent, or command.
