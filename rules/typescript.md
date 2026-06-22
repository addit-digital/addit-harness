---
paths: ["**/*.ts", "**/*.tsx"]
---

# TypeScript / React / Next.js / React Native

## Code conventions (highest → lowest)

1. **Per-project style** — match the existing codebase's naming, idiom, and
   structure over any guide. Read the neighbours before writing.
2. **Vendored conventions** — read `~/.claude/references/typescript/` (start at
   its `README.md`). For React/Next architecture the base is **bulletproof-react**;
   the README links the authorities (react.dev, Next.js docs, React Native docs,
   TypeScript Handbook, Total TypeScript).
3. **Expand** — when you hit a pattern neither covers, follow the code you can see
   and note the gap.

## Visual design conventions (highest → lowest)

1. **Per-project design file** — if `.claude/design-conventions.md` exists in the
   repo root, read it and follow it. It is a derived snapshot of the project's
   design language (tokens, type/spacing/color scales, component lib, layout rhythm,
   state patterns, breakpoints). Run `/design-conventions` to generate or refresh it.
2. **Existing UI — derive on the fly** — if no file exists but the project has an
   established UI (Tailwind config, token files, existing screens), derive the
   visual language from those before writing any component. Optionally run
   `/design-conventions` to capture it for future sessions.
3. **Greenfield** — if there is no existing design language, `@frontend-architect`
   is responsible for generating `.claude/design-conventions.md` before substantial
   implementation begins.

## Always

- Read the relevant guide before substantial work.
- For UI work: check `.claude/design-conventions.md` first; if absent, derive from
  what's there before writing a single component.
