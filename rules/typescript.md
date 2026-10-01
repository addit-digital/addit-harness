---
paths: ["**/*.ts", "**/*.tsx"]
---

# TypeScript / React / Next.js / React Native / Bun

## Code conventions (highest → lowest)

1. **Per-project style** — match the existing codebase's naming, idiom, and
   structure over any guide. Read the neighbours before writing.
2. **Vendored conventions** — read `~/.claude/references/typescript/README.md`
   first to route to the right subsection, then the guide it points to:
   - **Frontend/mobile** (React, Next.js, React Native): base is
     **bulletproof-react** (`references/typescript/react/`); authorities are
     react.dev, Next.js docs, React Native docs, TypeScript Handbook, Total
     TypeScript.
   - **Backend** (Bun): base is `references/typescript/backend/bun-best-practices.md`;
     authorities are the official Bun docs, and the best-practices doc of
     whichever framework the project uses (Hono or Elysia).
   Frontend work also loads `rules/typescript-frontend.md`.
3. **Expand** — when you hit a pattern neither covers, follow the code you can see
   and note the gap.
