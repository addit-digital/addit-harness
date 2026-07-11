---
title: Concepts
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
- **Plan before non-trivial work**, with diagrams (mermaid) for anything that
  touches architecture or flow — the terminal can't render mermaid, so
  `/save-plan` persists plans to `docs/plans/` for viewing in an IDE or on
  GitHub.

## Language conventions — two tiers + per-project layer

- **Tier 1 — `rules/{java,go,typescript}.md`** carry `paths:` frontmatter and
  auto-load when you touch that language. They contain **only a pointer** — no
  convention text of their own.
- **Tier 2 — `references/{go,java,typescript}/`** hold the convention guides +
  a `README.md`. Not path-scoped; Claude reads them on demand for substantial
  work.
- **Per-project — `.claude/go-conventions.md`** in any Go repo. Run
  `/go-conventions` to generate it; `rules/go.md` loads it automatically.
- **Per-project — `.claude/design-conventions.md`** in any TS/React project.
  Run `/design-conventions` on an existing project to derive it; for
  greenfield, `@frontend-architect` generates it.

| Stack | In-repo reference | Linked authorities |
|-------|-------------------|--------------------|
| Go | `references/go/app-erp-conventions.md` (codebase-derived) + per-project `.claude/go-conventions.md` | Effective Go, Go Code Review Comments, Google Go Style |
| Java/Spring | sanjeed5 `java.mdc` (CC0, Google-derived) | Effective Java, Google Java Style, Spring docs |
| TS / React / Next / RN | bulletproof-react docs (MIT) + sanjeed5 TS/React/Next/RN `.mdc` (CC0) | react.dev, Next.js docs, TypeScript Handbook, Total TypeScript |

The `code-reviewer` subagent checks adherence to whichever conventions apply.

## Curation philosophy: vendored, not vibes

Assets are delivered three ways:

- **Adopted (declarative):** official plugins enabled via `settings.json` —
  track their marketplace, safe to auto-update.
- **Vendored (pinned):** subagents *and* Java/TS convention guides, copied in
  at a fixed commit for reproducibility (provenance + license tracked in
  `AGENTS_SOURCES.md`, `skills/SOURCES.md`, and each `references/*/README.md`).
- **Authored (routing/process only):** `CLAUDE.md`, `rules/engineering-loop.md`,
  thin Tier-1 pointer rules, and the Go conventions file (codebase-derived).

The repo is a thin **curation + config layer**, not a pile of bespoke skills —
it deliberately reuses Claude Code's built-ins (`/code-review`, `/simplify`,
`/verify`, `/run`, `/init`, `deep-research`) instead of reinventing them.

## Next

- [Subagents](../subagents/) — what each one does and when it fires.
- [Use cases](../use-cases/) — concrete workflows showing which configs fire together.
