---
name: go-conventions
description: Scan the current Go repo and write .claude/go-conventions.md — a project-specific convention file that rules/go.md reads whenever a .go file is read, instead of re-scanning the codebase from scratch. Use when starting work in a new Go repo, when conventions have drifted, or when --refresh is passed to merge in new patterns.
user-invocable: true
argument-hint: "[--refresh]"
---

# /go-conventions — generate per-project Go conventions

Scans the current Go module and produces `.claude/go-conventions.md` — a
lightweight, project-specific convention reference. `rules/go.md` reads this
file whenever a `.go` file is read, so conventions load cheaply without
re-scanning. It holds only the **delta** from the global baseline.

## When to run

- **First time in a Go repo** — before any substantial code work.
- **`--refresh`** — when conventions have evolved or a new area has been added.
  Merges new patterns into the existing file; preserves hand-edits.
- **Prompted by a gap** — if you hit a pattern the file doesn't cover while coding,
  append the rule inline (don't re-run the full scan).

## Procedure

### 1. Confirm context
Verify you're in a Go repo: check for `go.mod`. If absent, stop and say so.

### 2. Scan the repo

Read these artifacts in priority order:

**a. Module identity**
- `go.mod` — module path, Go version, key direct dependencies (web framework,
  DB driver, logging, IDs, config)

**b. Existing config (if any)**
- `.golangci.yml` / `.golangci.toml` — enabled linters and their settings
- `Makefile` — `build`, `test`, `lint`, `run` targets
- `CONTRIBUTING.md` or any docs folder — pre-existing convention docs

**c. Project layout** (just list, don't read all files yet)
- Top-level dirs: `cmd/`, `internal/`, `pkg/`, `api/`, `app/`, etc.

**d. Representative code** — read 2-3 files from each category:
- Entry point: `cmd/*.go` or `main.go`
- Domain package: a `service.go` + `repository.go` + `model.go` from the largest domain
- HTTP/transport: a handler or controller file
- Error handling: look for custom error types
- Logging: find where logs are initialized and called

### 3. Derive conventions

From what you read, identify the established patterns for each section below.
Only document what you *actually observed* — don't invent from general knowledge.
If a section has no established pattern, omit it (omit it; the baseline applies).

**Sections to cover** (one per baseline topic, named by topic id; see
`${CLAUDE_PLUGIN_ROOT}/references/go/README.md`). For each, write only where the
repo differs from or extends the baseline default:

1. **LAY** project layout and domain package files (LAY-1..3 are often overridden)
2. **STY** naming, import order (STY-4)
3. **DI** constructor pattern (Builder, functional options, plain params)
4. **ERR** error type, sentinels, propagation (ERR-1, ERR-5)
5. **CTX** how user/tenant identity flows through the context
6. **CON** concurrency helpers in use
7. **LOG** logging library and how a logger is acquired (LOG-2)
8. **HTTP** router framework, route prefix, error rendering (HTTP-1, 2, 4, 6)
9. **DATA** DB driver, pagination, soft delete, collection naming (DATA-2)
10. **EVT** event bus, if one exists (EVT-*)
11. **TEST** test style and CI commands
12. **Key libraries**: one-line usage note per direct dependency

Where the repo contradicts a baseline topic rule, record it as
`# OVERRIDE: G-<TOPIC>-n <reason>`. Never write an override for G-1..G-8 or
G-10: those are not overridable. If the repo contradicts one, report it to the
user instead.

### 4. Write the file

Write to `.claude/go-conventions.md` in the repo root (create `.claude/` if needed).

**With `--refresh`:** read the existing file first, merge new patterns in, keep
existing content that is still valid. Never overwrite hand-edits — look for
`# NOTE:` or `# OVERRIDE:` markers and preserve them.

**File header:**

```markdown
# Go conventions — {module-name}

Derived from codebase scan on {date}. Maintained by `/go-conventions --refresh`.
Global baseline: `${CLAUDE_PLUGIN_ROOT}/references/go/README.md` (topic files).

> **Stack:** Go {version} · {key libs}
```

Then one section per category found. Each section:
- States the rule plainly (imperative)
- Shows a short code example where the rule isn't obvious
- Cites the example file/pattern it was derived from (e.g. `// see pkg/sales/service.go`)

Keep each section tight — 5-15 lines max. This file is read whenever a `.go` file
is read; brevity matters more than completeness.

### 5. Report

Tell the user:
- Path of the written file
- Number of sections covered
- Any areas where you couldn't find an established pattern (and what to do)
- How to view/edit it (it's plain markdown — open in any editor)
- Suggest adding `@.claude/go-conventions.md` to the project's `CLAUDE.md` for
  automatic inclusion (optional; `rules/go.md` reads it on demand without this)

Do **not** commit the file unless the user asks.

## Notes

- This skill writes to the *target project* repo, not to the addit-harness repo.
- The file it generates is a supplement to the topic files under `${CLAUDE_PLUGIN_ROOT}/references/go/`,
  not a replacement. Put only the *delta* — what differs from or extends the global baseline.
- If the project is a perfect match for the baseline (same stack, same patterns), say so
  and write a minimal file noting the match rather than duplicating all baseline content.
