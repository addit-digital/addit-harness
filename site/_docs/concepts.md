---
title: Concepts
description: Why addit-harness exists, the engineering loop, deterministic orchestration with /dev-flow, tiered language conventions, and the curation philosophy.
nav_order: 2
nav_group: Start
---

## Why this config?

**Without it:** Claude Code starts as a blank slate — no engineering loop, no
conventions, no subagents. You either wing it session to session or spend
hours wiring up memory, rules, and delegation yourself, then rebuild it on
every machine.

**With it:** one command gives you a reproducible, opinionated starting point.
See the [landing page comparison](../../#compare) for the full before/after.

## The engineering loop

Always-on mental model for non-trivial work: **frame intent → curate context →
write a plan → implement in small verifiable units → verify with tooling →
commit → clear/hand off.** The loop is documented in `rules/engineering-loop.md`
and auto-loads into every session. Two hard rules fall out of it:

- **Never present unverified code as done.** Run it, or say plainly that it's
  unverified and what would prove it.
- **Plan before non-trivial work**, written to the doc protocol
  (`references/doc-protocol.md`): a template per document type, a length
  ceiling per tier, Observed/Inferred/Unknown labels on claims, and one mermaid
  diagram per concept. The terminal can't render mermaid, so `/save-plan`
  persists plans to `docs/work/<slug>/plans/` for viewing in an IDE or on GitHub.

[The engineering loop](../engineering-loop/) page covers where each document
goes, slugs and collisions, and the doc protocol in detail.

## Deterministic orchestration — `/dev-flow`

The engineering loop above is hand-driven by default — you decide when to
invoke which subagent, one `Agent` call at a time, every session. `/dev-flow`
automates the design-gate and review-gate rounds of that same loop as real
`Workflow`-tool control flow instead: a `while` loop with a convergence check,
a hard round cap, a token-budget guard, and a non-progress circuit breaker —
not the model remembering to keep looping correctly on its own. The one step
that stays a plain conversational turn is **your approval of the plan** before
implementation starts; a `Workflow` script has no way to pause mid-run and ask,
so that gate lives in the surrounding skill instead, not the script, and a hook
refuses to start implementation unless the approved plan's hash matches. Effort
scales with the task: a triage step sorts each request into a `light`,
`standard` or `deep` tier, which sets how many agents and review rounds run.
While a run is going, `/workflows` shows its tier, review rounds, gate verdicts
and any halt, and, with the task tools on, a six-step task list tracks where it is (see
[Watching a run](../dev-flow/#watching-a-run)). See [How dev-flow works](../dev-flow/) for the phase-by-phase
mechanics and how the loops know when to stop.

## Language conventions — two tiers + per-project layer

- **Tier 1 — `rules/*.md`** carry `paths:` frontmatter and auto-load when you
  touch that language. `rules/go.md` and `rules/java.md` hold a short,
  enforceable contract (G-1..G-10, J-1..J-14) plus a topic index;
  `rules/typescript.md` routes to the TypeScript references, and
  `rules/typescript-frontend.md` (React/Next.js/React Native files) holds the
  Frontend Implementation Contract, FC-1..FC-10.
- **Tier 2 — `references/{go,java,typescript}/`** hold the topic files + a
  `README.md`. Not path-scoped; Claude reads the one or two topics that match
  the edit. Go and Java topic rules have ids (`G-ERR-1`, `J-DATA-2`) and a cited
  source; reviewers cite the ids in findings.
- **Per-project — `.claude/go-conventions.md`** in any Go repo. Run
  `/go-conventions` to generate it; `rules/go.md` loads it automatically. It may
  add rules and override a topic rule with `# OVERRIDE: G-<TOPIC>-n <reason>`,
  but never G-1..G-8 or G-10. G-9's numbers come from the project's
  `.golangci.yml` when it sets them.
- **Per-project, Java** — there is no conventions file. A project
  Checkstyle/PMD config replaces J-12's numbers, and a project formatter
  replaces the build-style formatting rules.
- **Per-project — `.claude/design-conventions.md`** in any TS/React project.
  Run `/design-conventions` on an existing project to derive it; for
  greenfield, `@frontend-architect` generates it.

| Stack | In-repo reference | Linked authorities |
|-------|-------------------|--------------------|
| Go | `rules/go.md` contract (G-1..G-10) + 11 topic files in `references/go/` + per-project `.claude/go-conventions.md` | Effective Go, Go Code Review Comments, Google Go Style, Uber Go Style (where it does not collide with the owner's approach) |
| Java/Spring | `rules/java.md` contract (J-1..J-14) + 12 cited topic files in `references/java/` | Effective Java, Google Java Style, Spring docs |
| TS / React / Next / RN | `rules/typescript-frontend.md` contract (FC-1..FC-10) + bulletproof-react docs (MIT) + sanjeed5 TS/React/Next/RN `.mdc` (CC0) | react.dev, Next.js docs, TypeScript Handbook, Total TypeScript |

### Frontend Implementation Contract

FC-1..FC-10 are hard limits on frontend code: at most 150 non-blank lines per
component or hook file (never more than 250), at most 80 lines per component
function, JSX nesting depth at most 4, at most 7 declared props, cognitive
complexity at most 10, at most 3 state/effect hooks per component, no data
fetching inside components, feature folders with no cross-feature imports, one
component per file, and reuse plus design tokens instead of literals. A
project's ESLint config or `CLAUDE.md` may tighten a number, never loosen it.
`@frontend-developer` writes to it and `@code-reviewer` checks it by measuring,
not eyeballing.

A `PostToolUse` hook (`hooks/fe-contract-check.sh`) checks FC-1 after every
`Write`/`Edit` of a frontend `.ts`/`.tsx` file and adds an advisory note when the
file passes 150 or 250 non-blank lines. It never blocks. `ADDIT_FE_GATE=eslint`
also runs your project's own locally installed ESLint on the file;
`ADDIT_FE_GATE=0` turns the hook off. Set it in your shell or in
`settings.json` `"env"`.

The `code-reviewer` subagent checks adherence to whichever conventions apply.

## Curation philosophy: vendored, not vibes

Assets are delivered three ways:

- **Adopted (declarative):** official plugins enabled via `settings.json` —
  track their marketplace, safe to auto-update.
- **Vendored (pinned):** some subagents *and* the TypeScript convention guides,
  copied in at a fixed commit for reproducibility (provenance + license tracked
  in `AGENTS_SOURCES.md`, `skills/SOURCES.md`, and each `references/*/README.md`).
- **Authored:** `CLAUDE.md`, `rules/engineering-loop.md`, the doc protocol and
  solution method, the Tier-1 rules, and the Go and Java topic files (each rule
  cites its source).

The repo is a thin **curation + config layer**, not a pile of bespoke skills —
it deliberately reuses Claude Code's built-ins (`/code-review`, `/simplify`,
`/verify`, `/run`, `/init`, `deep-research`) instead of reinventing them.

## Next

- [The engineering loop](../engineering-loop/) — the loop and the doc protocol in detail.
- [Subagents](../subagents/) — what each one does and when it fires.
- [Use cases](../use-cases/) — concrete workflows showing which configs fire together.
