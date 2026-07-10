---
name: go-conventions
description: Scan the current Go repo and write .claude/go-conventions.md — a project-specific convention file that rules/go.md loads on every session instead of re-scanning the codebase from scratch. Use when starting work in a new Go repo, when conventions have drifted, or when --refresh is passed to merge in new patterns.
user-invocable: true
argument-hint: "[--refresh]"
---

# /go-conventions — generate per-project Go conventions

Scans the current Go module and produces `.claude/go-conventions.md` — a
lightweight, project-specific convention reference. `rules/go.md` reads this
file first on every session, so conventions load cheaply without re-scanning.

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
- `.cursor/rules/*.mdc` or `.github/copilot-instructions.md` — any pre-existing
  convention docs

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
If a section has no established pattern, omit it (leave a brief `# TODO:` note).

**Sections to cover:**

1. **Project layout** — the actual top-level structure and what lives where
2. **Package / module structure** — how domain packages are organized (which files,
   naming pattern for constructors, interfaces vs structs)
3. **Naming** — types, functions, constants, files, packages
4. **Dependency injection** — constructor pattern (Builder? functional options? plain params?)
5. **Model/DTO separation** — where domain entities live vs API types; how they're mapped
6. **Error handling** — custom error types, wrapping, sentinel errors, propagation
7. **Logging** — library, how to acquire a logger, log levels used
8. **Data access** — DB driver, query patterns, pagination, soft delete, collection naming
9. **HTTP layer** — router framework, handler signature, request binding, error response
10. **Events / async** — if an event bus exists: how events are defined, published, subscribed
11. **Context & auth** — how user/auth context flows through the system
12. **Validation** — library, where validation happens, custom validators
13. **Import order** — observed ordering convention
14. **Key libraries** — for each direct dep, one-line usage note (e.g. "uuid.New() for IDs")

### 4. Write the file

Write to `.claude/go-conventions.md` in the repo root (create `.claude/` if needed).

**With `--refresh`:** read the existing file first, merge new patterns in, keep
existing content that is still valid. Never overwrite hand-edits — look for
`# NOTE:` or `# OVERRIDE:` markers and preserve them.

**File header:**

```markdown
# Go conventions — {module-name}

Derived from codebase scan on {date}. Maintained by `/go-conventions --refresh`.
Global baseline: `${CLAUDE_PLUGIN_ROOT}/references/go/app-erp-conventions.md`.

> **Stack:** Go {version} · {key libs}
```

Then one section per category found. Each section:
- States the rule plainly (imperative)
- Shows a short code example where the rule isn't obvious
- Cites the example file/pattern it was derived from (e.g. `// see pkg/sales/service.go`)

Keep each section tight — 5-15 lines max. This file is loaded every session;
brevity matters more than completeness.

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
- The file it generates is a supplement to `${CLAUDE_PLUGIN_ROOT}/references/go/app-erp-conventions.md`,
  not a replacement. Put only the *delta* — what differs from or extends the global baseline.
- If the project is a perfect match for the baseline (same stack, same patterns), say so
  and write a minimal file noting the match rather than duplicating all baseline content.
