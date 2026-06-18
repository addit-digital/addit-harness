---
paths: ["**/*.ts", "**/*.tsx"]
---

# TypeScript conventions (essentials) — React / Next.js / React Native

Always-on when editing TS/TSX. Frontend & mobile focus. The non-negotiables;
match the existing project's style first. For depth (React patterns, Next.js App
Router, React Native, state management, worked examples) read the relevant topic in `~/.claude/references/typescript/` (start at its
`README.md` index) before substantial work.

- **Type safety:** `strict` on. No implicit `any` (prefer `unknown` at
  boundaries + narrowing). No `// @ts-ignore` (use `// @ts-expect-error` with a
  reason). Avoid non-null `!` and unsafe `as`; validate external data (e.g. `zod`).
- **Style:** named exports over default; `const` by default; model state with
  discriminated unions + exhaustive `switch`. Use `readonly`/`as const`.
- **React:** function components + hooks only. Obey the rules of hooks (no
  conditional hooks); complete `useEffect` dependency arrays; key lists by stable
  id (not index). Lift state only as far as needed; memoize deliberately, not
  reflexively. Keep components small and composable.
- **Next.js:** default to Server Components; add `"use client"` only when you need
  interactivity/browser APIs. Fetch on the server where possible; never put
  secrets in client components.
- **React Native:** mind platform differences (`Platform.select`); avoid heavy
  work on the JS thread; use the project's navigation lib consistently.
- **Async/errors:** `async/await`, no floating promises; throw `Error` (never
  strings) and preserve `cause`.
- **Testing:** use the project's runner (Jest/Vitest) + React Testing Library;
  test behavior, not internals; type test data (no `any`); add a regression test
  with every bug fix.
