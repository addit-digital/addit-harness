# TypeScript / React / Next.js / React Native / Bun — conventions (vendored + authorities)

On-demand reference (not auto-loaded). The Tier-1 rule `rules/typescript.md`
points here. Covers both **frontend/mobile** (React, Next.js, React Native) and
**backend** (Bun) focus areas — see the matching subsection below. Convention
text is **vendored from recognized sources**, not hand-written.

## Frontend & mobile (React / Next.js / React Native)

### Vendored (read these)
| File / dir | Source | License |
|------------|--------|---------|
| `react/` (architecture: project-structure, components-and-styling, state-management, api-layer, testing, security, performance, error-handling, …) | [alan2207/bulletproof-react](https://github.com/alan2207/bulletproof-react) — the most-cited React architecture guide (human-authored) | MIT |
| `typescript-best-practices.md` | [sanjeed5/awesome-cursor-rules-mdc](https://github.com/sanjeed5/awesome-cursor-rules-mdc) `typescript.mdc` | CC0-1.0 |
| `react-best-practices.md` | sanjeed5 `react.mdc` | CC0-1.0 |
| `nextjs-best-practices.md` | sanjeed5 `next-js.mdc` | CC0-1.0 |
| `react-native-best-practices.md` | sanjeed5 `react-native.mdc` | CC0-1.0 |

> The `sanjeed5` files are a community collection (script-generated, derived from
> official guides) — a solid baseline; defer to the authorities below on conflict.
> For React/Next architecture, `react/` (bulletproof-react) is the primary source.

### Authorities to read (link-only)
- [react.dev](https://react.dev) — official React docs (hooks-first source of truth).
- [Next.js docs](https://nextjs.org/docs) + [vercel/next.js `/examples`](https://github.com/vercel/next.js/tree/canary/examples) — canonical App Router patterns.
- [React Native docs](https://reactnative.dev) — official RN source of truth.
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) — official TS reference.
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html) — comprehensive TS style (HTML).
- [Total TypeScript](https://www.totaltypescript.com) · [type-challenges](https://github.com/type-challenges/type-challenges) — advanced TS.
- [infinitered/ignite](https://github.com/infinitered/ignite) — battle-tested React Native boilerplate.
- [airbnb/javascript](https://github.com/airbnb/javascript) — historically dominant JS style guide (now declining; flat ESLint config + Prettier + typescript-eslint have largely displaced it).

## Backend (Bun)

### Vendored (read these)
| File | Source | License |
|------|--------|---------|
| `backend/bun-best-practices.md` | [sanjeed5/awesome-cursor-rules-mdc](https://github.com/sanjeed5/awesome-cursor-rules-mdc) `bun.mdc` | CC0-1.0 |

### Authorities to read (link-only)
- [Bun docs](https://bun.com/docs) — official source of truth: [test runner](https://bun.com/docs/test/writing-tests) (`bun test`, Jest-compatible), [bundler](https://bun.com/docs/bundler) (`bun build`), [HTTP server](https://bun.com/docs/runtime/http/server) (`Bun.serve`, WebSockets), built-in [SQLite](https://bun.com/docs/runtime/sqlite)/[S3](https://bun.com/docs/runtime/s3)/[Redis](https://bun.com/docs/runtime/redis) clients, [bunfig.toml](https://bun.com/docs/runtime/bunfig) & [workspaces](https://bun.com/docs/guides/install/workspaces).
- [Hono docs — Best Practices](https://hono.dev/docs/guides/best-practices) — runtime-agnostic (Bun/Deno/Node/Workers), the most-starred TS web framework; `app.route()` composition, factory pattern, type-safe RPC client (`hc`). MIT.
- [Elysia docs — Best Practice](https://elysiajs.com/essential/best-practice) — Bun-native framework (built specifically to exploit Bun's runtime); feature-folder structure, "instance-as-controller" pattern, method-chaining for end-to-end type inference. MIT.
- [santiq/bulletproof-nodejs](https://github.com/santiq/bulletproof-nodejs) — TypeScript layered architecture (controllers/services/repositories), centralized error handling, validation, Swagger docs. MIT. **Stale** (no commits since 2024) — treat as an architectural pattern reference, not a current-tooling reference; adapt its layering to Bun/Hono/Elysia rather than copying its Express/TypeDI wiring verbatim.

> Neither Hono nor Elysia monopolizes "the" Bun framework — pick one per project
> and read its best-practices doc; both are linked rather than vendored since
> framework APIs evolve fast.
