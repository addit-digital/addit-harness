---
paths: ["**/*.ts", "**/*.tsx"]
---

# TypeScript conventions

Auto-loaded when working in TypeScript. Idiomatic, type-safe, testable TS for
backend (Node/NestJS) and frontend. Match the existing project's style first;
these are the defaults when there is no local precedent.

## Type safety
- Treat `strict` as mandatory. No implicit `any`; no silencing the compiler with
  `// @ts-ignore` — fix the type or use `// @ts-expect-error` with a reason.
- Avoid `any`; prefer `unknown` at boundaries and narrow with type guards.
- Avoid non-null assertions (`!`) — narrow instead. Avoid unsafe `as` casts;
  validate external data (e.g. `zod`) rather than asserting its shape.
- Model domain state with discriminated unions; prefer exhaustive `switch` with a
  `never` default to catch missing cases at compile time.
- Use `readonly`/`as const` for immutable data; prefer `type` for unions and
  composition, `interface` for extendable object contracts — stay consistent
  with the repo.

## Style & structure
- Prefer named exports; avoid default exports (better refactoring/auto-import).
- Keep modules narrow and cohesive; avoid barrel files that create import cycles.
- Pure functions where practical; isolate side effects.
- Use `const` by default; never `var`.
- Name things fully; no cryptic abbreviations.

## Async & errors
- `async/await` over raw `.then()` chains. Always handle rejections; never leave
  a floating promise (await it, return it, or explicitly `void` it).
- Use `Promise.all`/`allSettled` for independent concurrent work; don't `await`
  in a loop when calls are independent.
- Throw `Error` (or subclasses) with messages — never throw strings. Preserve the
  cause (`new Error("...", { cause })`).
- Model expected failures in the type system (result/union types) rather than
  throwing for routine control flow.

## Node / NestJS (backend)
- Constructor-based dependency injection; depend on interfaces/tokens, keep
  controllers thin and services for business logic.
- Validate and type all external input (request bodies, env, queue messages) at
  the boundary with a schema validator; never trust `any` from the wire.
- Load config through a typed config module; never read `process.env` ad hoc deep
  in the code.
- No blocking the event loop with heavy sync work; offload or stream.

## Testing
- Use the project's runner (Jest/Vitest); don't introduce a second one.
- Test behavior through public APIs; type the test data, no `any` in tests.
- Mock at boundaries (network, DB, clock), not internal pure functions.
- Cover error/edge cases; add a regression test with every bug fix.
- Keep tests deterministic — inject time/randomness/IO.
