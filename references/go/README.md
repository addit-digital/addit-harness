# Go — conventions (baseline + authorities)

On-demand reference (not auto-loaded). The Tier-1 rule `rules/go.md` points here.

## Baseline (read first)

| File | Source | Notes |
|------|--------|-------|
| `app-erp-conventions.md` | Derived from [addit-digital/app-erp](https://github.com/addit-digital/app-erp) | Gin · MongoDB v2 · uuid · decimal · slog/OTel |

This replaces the previous Uber Go Style Guide baseline. Conventions reflect the
actual codebase, not an external style guide.

## Authorities (link-only — fallback for greenfield code)

Use when the codebase is silent on a topic or for brand-new projects with no
established patterns:

- [Effective Go](https://go.dev/doc/effective_go) — foundational idiomatic Go (Go team)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) — de-facto reviewer checklist
- [Google Go Style Guide](https://google.github.io/styleguide/go/) — comprehensive style + decisions
- [Go Proverbs](https://go-proverbs.github.io/) — design philosophy

## Stack-specific (this user's stack)

- Web: [gin-gonic/gin](https://github.com/gin-gonic/gin) — examples & docs for idiomatic Gin
- Data: [mongodb/mongo-go-driver v2](https://github.com/mongodb/mongo-go-driver) — official v2 driver patterns
- IDs: [google/uuid](https://pkg.go.dev/github.com/google/uuid)
- Decimal: [greatcloak/decimal](https://github.com/greatcloak/decimal) — for money + quantities
- OTel: [honeycombio/otel-config-go](https://github.com/honeycombio/otel-config-go) — single-call OTel setup

## Per-project layer

Run `/go-conventions` in a repo to generate `.claude/go-conventions.md` — a
project-specific extension of this baseline. `rules/go.md` loads that file first
when it exists, then falls back here.
