---
paths: ["**/*.go"]
---

# Go conventions

Auto-loaded when working in Go. Idiomatic, testable, production Go. Match the
existing module's style first; these are the defaults when there is no local
precedent.

## Formatting & tooling
- Code must be `gofmt`/`goimports` clean. Never hand-format.
- It must pass `go vet`; prefer `golangci-lint` if the repo configures it.
- Group imports: stdlib, third-party, local — separated by blank lines.

## Naming & structure
- Short, lower-case package names; no `util`/`common`/`helpers` grab-bags.
- Exported identifiers need doc comments starting with the identifier name.
- MixedCaps, not snake_case. Acronyms keep case: `ID`, `URL`, `HTTP`.
- Keep packages cohesive around a responsibility, not a layer.
- Accept interfaces, return structs.

## Errors
- Return errors; don't panic in library code. `panic` only for truly
  unrecoverable, programmer-error states.
- Wrap with context: `fmt.Errorf("doing X: %w", err)`. Preserve the chain with
  `%w` so `errors.Is`/`errors.As` work.
- Define sentinel errors (`var ErrNotFound = errors.New(...)`) or typed errors
  for cases callers must branch on.
- Handle every error explicitly. Only discard with `_` when deliberate and
  obvious; never swallow silently.
- Add context as the error travels up; don't log-and-return (that double-reports).

## Interfaces & types
- Keep interfaces small (often 1–2 methods); define them at the **consumer**,
  not the producer.
- Don't export an interface "just in case" — export concrete types; introduce an
  interface when a second implementation or a test seam actually needs it.
- Prefer composition over wide interfaces.

## Concurrency
- Don't start a goroutine without knowing how it stops. Tie lifetime to a
  `context.Context`.
- Pass `context.Context` as the first parameter (`ctx context.Context`) on calls
  that do I/O, block, or span goroutines. Never store it in a struct.
- Protect shared state with a mutex or confine it to one goroutine via channels —
  pick one model per piece of state, don't mix.
- Always `go test -race` for concurrent code.
- Use `errgroup` for fan-out/fan-in with error propagation and cancellation.
- Avoid leaking goroutines: ensure channels have a sender/receiver that
  terminates, and use `select` with `ctx.Done()`.

## API & resource hygiene
- `defer` Close/Unlock right after acquiring the resource; check Close errors on
  writers.
- Use `context` deadlines/timeouts for outbound calls; don't rely on defaults.
- Zero values should be useful where practical; document when they aren't.
- Prefer slices/maps over premature custom containers.

## Testing
- Table-driven tests with subtests (`t.Run`), named cases.
- Use the standard `testing` package; `testify/require` is fine if the repo
  already uses it. Don't introduce a new assertion framework unprompted.
- Test behavior through exported APIs; avoid testing unexported internals unless
  there's real complexity to pin down.
- Use `t.Parallel()` where safe; keep tests hermetic (no network/clock/FS
  surprises — inject them).
- Cover error paths, not just the happy path. Add a regression test with every
  bug fix.
