---
paths: ["**/*.go"]
---

# Go conventions (essentials)

Always-on when editing Go. The non-negotiables; match the existing module's style
first. For depth (concurrency, interfaces, API/resource patterns, testing,
worked examples) read the relevant topic in `~/.claude/references/go/` (start at its
`README.md` index) before substantial Go work.

- **Formatting/tooling:** `gofmt`/`goimports` clean; passes `go vet` (and
  `golangci-lint` if configured). Never hand-format.
- **Errors:** return them, don't panic in library code. Wrap with context using
  `fmt.Errorf("...: %w", err)`; handle every error explicitly (only `_` when
  deliberate). Don't log-and-return the same error.
- **Naming:** MixedCaps; short package names (no `util`/`common`); acronyms keep
  case (`ID`, `URL`, `HTTP`). Exported identifiers get doc comments.
- **Interfaces:** small, defined at the **consumer**; accept interfaces, return
  structs. Don't export an interface "just in case".
- **Concurrency:** never start a goroutine without knowing how it stops; tie it to
  a `context.Context` (first param, never stored in a struct). Run `go test -race`.
- **Resources:** `defer` Close/Unlock right after acquiring; set timeouts on
  outbound calls.
- **Testing:** table-driven with subtests (`t.Run`); cover error paths; add a
  regression test with every bug fix. Use stdlib `testing` (don't introduce a new
  assertion framework unprompted).
