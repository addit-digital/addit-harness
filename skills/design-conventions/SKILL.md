---
name: design-conventions
description: Scan the current TS/React project's existing UI layer and write .claude/design-conventions.md — a project-specific visual design convention file that rules/typescript.md loads before UI work. Use when starting UI work in an existing project, when design conventions have drifted, or when --refresh is passed to merge in new patterns.
user-invocable: true
argument-hint: "[--refresh]"
---

# /design-conventions — generate per-project visual design conventions

Scans the current TypeScript/React project's UI layer and produces
`.claude/design-conventions.md` — a lightweight, project-specific visual design
convention reference. `rules/typescript.md` instructs loading this file first for
any UI work, so the design language loads cheaply without re-scanning each session.

## Greenfield guard

This skill *derives from what exists*. If the project has **no existing UI at all**
(no Tailwind config, no token files, no components, no screens), stop and tell the
user to ask `@frontend-architect` first — creating a design language from a blank
slate is design work, not derivation. If only config exists (Tailwind config, a
chosen component lib, token file stubs) with no implemented screens, seed a minimal
stub from that and flag the rest for the architect.

## When to run

- **First time in a project with existing UI** — before any substantial UI work.
- **`--refresh`** — when the design system has evolved or a new visual pattern has
  been established. Merges new patterns into the existing file; preserves hand-edits.
- **Prompted by a gap** — if you hit a pattern the file doesn't cover while coding,
  append the rule inline (don't re-run the full scan).

## Procedure

### 1. Confirm context

Verify you're in a TS/React project: check for `package.json`, a `tsconfig.json`,
and the presence of `.ts`/`.tsx` files. If absent, stop and say so.

Check whether `.claude/design-conventions.md` already exists. If it does and
`--refresh` was not passed, report what's there and ask the user to pass `--refresh`
to merge new patterns.

### 2. Scan the project's UI layer

Read these artifacts in priority order:

**a. Design token / config foundation**
- `tailwind.config.{ts,js}` — custom color palette, spacing scale, type scale,
  breakpoints, font families, border-radius tokens, shadow scale
- `tokens/` or `design-tokens/` directory — primitive and semantic token definitions
- CSS custom-property files (`variables.css`, `globals.css`, `:root` blocks)
- `theme.{ts,js}` or `theme/` — if using a component lib (MUI, Chakra, Mantine)

**b. Component library / primitives**
- `package.json` — identify which component library is installed (Radix, Mantine,
  MUI, Chakra, shadcn/ui, etc.) and the styling solution (Tailwind, CSS Modules,
  styled-components, vanilla-extract)
- `components/ui/` or `src/ui/` or `lib/components/` — base primitive components
  (Button, Input, Card, Badge, etc.); read 3-4 to understand the token usage pattern

**c. Representative screens / pages**
- Read 2-3 full page or feature components to observe:
  - Spacing rhythm (gap, padding, margin patterns — are they from a scale?)
  - Layout structure (max-width containers, grid/flex patterns)
  - Typography usage (which text sizes, weights, and colors appear most)
  - Color usage (primary actions, secondary, destructive, surface, text)
  - Component composition patterns (card structures, list items, form layouts)

**d. State presentation patterns**
- Find one loading state, one empty state, one error state — document how each is
  presented visually

### 3. Derive conventions

From what you read, identify the established patterns for each section below.
Only document what you *actually observed* — don't invent from general knowledge.
If a section has no established pattern, omit it (leave a brief `# TODO:` note).

**Sections to cover:**

1. **Stack** — styling solution (Tailwind / CSS Modules / CSS-in-JS), component library, key UI deps
2. **Color tokens** — primary, secondary, destructive, surface, border, and text token names/values
3. **Type scale** — the sizes and weights in use (e.g. `text-sm/base/lg/xl`, `font-medium/semibold`)
4. **Spacing rhythm** — the spacing values in use; whether a strict scale is followed
5. **Layout patterns** — max-width container, column grid, common flex/grid structures
6. **Border & radius** — border-radius values, shadow scale in use
7. **Breakpoints** — the responsive breakpoints defined and their usage pattern
8. **Component primitives** — which primitives exist and their expected usage pattern
9. **Empty / loading / error states** — how each is presented (skeleton, spinner, illustration, etc.)
10. **Motion** — whether animations/transitions are used; `prefers-reduced-motion` handling

### 4. Write the file

Write to `.claude/design-conventions.md` in the repo root (create `.claude/` if
needed).

**With `--refresh`:** read the existing file first, merge new patterns in, keep
existing content that is still valid. Never overwrite hand-edits — look for
`# NOTE:` or `# OVERRIDE:` markers and preserve them.

**File header:**

```markdown
# Design conventions — {project-name}

Derived from codebase scan on {date}. Maintained by `/design-conventions --refresh`.

> **Stack:** {styling solution} · {component library} · {key UI deps}
```

Then one section per category found. Each section:
- States the rule plainly (imperative)
- Shows the token name or value where it isn't obvious
- Cites the file/pattern it was derived from (e.g. `// see tailwind.config.ts`)

Keep each section tight — 5-15 lines max. This file is loaded before every UI
session; brevity matters more than completeness.

### 5. Report

Tell the user:
- Path of the written file
- Number of sections covered
- Any areas where you couldn't find an established pattern (and what to do)
- How to view/edit it (it's plain markdown — open in any editor)
- Suggest adding `@.claude/design-conventions.md` to the project's `CLAUDE.md` for
  automatic inclusion (optional; `rules/typescript.md` reads it on demand without this)

Do **not** commit the file unless the user asks.

## Notes

- This skill writes to the *target project* repo, not to the addit-harness repo.
- If the project uses a design token system (Style Dictionary, Theo, etc.), prefer
  reading the token source files directly over the compiled output.
- A file generated by `@frontend-architect` for a greenfield project is a valid
  starting point — run `/design-conventions --refresh` after the first screens are
  built to extend it with observed patterns.
