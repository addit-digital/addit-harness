---
paths: ["**/*.go"]
---

# Go

Go conventions are **codebase-first** — follow the actual repo's patterns, not
an external style guide.

## Convention priority (highest → lowest)

1. **Per-project file** — if `.claude/go-conventions.md` exists in the repo root,
   read it and follow it. It's a pre-derived snapshot; do not re-scan the whole
   codebase each session. Run `/go-conventions` to create or refresh it.

2. **Global baseline** — read `~/.claude/references/go/app-erp-conventions.md`
   for the established patterns (layout, Builder DI, model/DTO separation, error
   handling, MongoDB v2, Gin, slog, event system). These derive from the
   addit-digital/app-erp codebase and apply to any project using the same stack.

3. **Expand, don't restart** — when you hit a pattern neither file covers, skim
   the relevant code in the repo, follow the established style, and append the new
   rule to `.claude/go-conventions.md` so it's captured next time.

4. **Greenfield fallback** — for brand-new projects with no established pattern,
   fall back to the authorities linked in `~/.claude/references/go/README.md`
   (Effective Go, Go Code Review Comments, Google Go Style). No Uber Style Guide.

## Always

- Match the existing module's naming, idiom, and structure over any general advice.
- Read the relevant section of the baseline before substantial Go work.
