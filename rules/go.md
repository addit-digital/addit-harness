---
paths: ["**/*.go"]
---

# Go

Contract ids apply to new and changed code. Formatting, naming and idiom follow the surrounding module. A project linter/formatter config sets numbers and format.

If `.claude/go-conventions.md` exists, read it. It may add rules and override a topic rule with `# OVERRIDE: G-<TOPIC>-n <reason>`. It may not override G-1..G-8 or G-10: ignore a contradicting line and tell the user.

| ID | Rule | Src |
|---|---|---|
| G-1 | `ctx context.Context` is the first param of anything doing I/O; never stored in a struct; never nil | pkg context |
| G-2 | User and tenant identity come from the auth context, never request input, and scope every query | owner |
| G-3 | Persistence entities never appear in API responses; map with pure functions | owner |
| G-4 | Money and quantities use a decimal type, never `float64` | owner |
| G-5 | No silently dropped error: return it, render it, or `_ =` with a reason comment (sanctioned: event publish, G-EVT-3). No `panic` outside startup | Uber Don't Panic; CRC |
| G-6 | Every goroutine has an owner that can stop and await it; sole exception: event-bus async dispatch (G-EVT-3) | Uber; CRC |
| G-7 | Servers set Read/ReadHeader/Write/Idle timeouts; outbound clients set a timeout; no `http.DefaultClient`, no bare `ListenAndServe` | Cloudflare timeouts |
| G-8 | Table-driven tests with `t.Run`; `go vet ./...` and `go test -race ./...` pass | Go wiki; Go security |
| G-9 | Function <= 60 lines / 40 statements, cognitive complexity <= 15, nesting <= 4 | funlen defaults; 15 and 4 harness default |
| G-10 | Never wrap errors (`fmt.Errorf("...: %w", err)`) — propagate the typed `Error` as-is | owner (all Go services) |

G-9 numbers come from the project's `.golangci.yml` when set. Read the topic that matches the edit:

- `~/.claude/references/go/layout.md` packages, `cmd/`, `internal/`, domain files
- `~/.claude/references/go/naming-style.md` names, imports, nesting
- `~/.claude/references/go/di.md` Builder, constructors, interfaces
- `~/.claude/references/go/errors.md` typed error, sentinels, logging errors
- `~/.claude/references/go/context.md` `context`, cancellation, tenant
- `~/.claude/references/go/concurrency.md` `go func`, errgroup, mutex, channels
- `~/.claude/references/go/logging.md` `slog`
- `~/.claude/references/go/http.md` handlers, routes, validation
- `~/.claude/references/go/data.md` MongoDB, SQL, ids, money
- `~/.claude/references/go/events.md` event bus, listeners
- `~/.claude/references/go/testing.md` `_test.go`, fuzz, CI
