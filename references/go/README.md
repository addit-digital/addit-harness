# Go: conventions by topic

On-demand reference (not auto-loaded). `rules/go.md` holds the precedence line, the G-1..G-10 contract, the override model and the topic index; read the one or two topic files that match the edit. Every rule has an id (`G-<TOPIC>-n`) and a `Src:`: a link, `owner` (the owner's own approach), or `harness default` (no external authority; a reviewer must accept it). Reviewer findings cite ids.

| Topic | Covers |
|-------|--------|
| `layout.md` | `cmd/` wiring, `internal/`, domain package files, globals |
| `naming-style.md` | package/receiver/error-string names, import groups, nesting |
| `di.md` | Builder pattern, interface checks, functional options |
| `errors.md` | typed error, sentinels, no wrapping, log before return |
| `context.md` | `context` rules, user/tenant identity, `WithoutCancel` |
| `concurrency.md` | goroutine lifetime, errgroup, channels, mutexes, atomics |
| `logging.md` | `slog`, logger from context, hot-path attrs |
| `http.md` | versioned routes, verbs, handler flow, error rendering |
| `data.md` | MongoDB v2, SQL pools, uuid ids |
| `events.md` | sync and async events, panic recovery |
| `testing.md` | table tests, race/vet/govulncheck, fuzzing |

## Owner approach versus the Uber guide
The Uber Go guide is used wherever it does not collide with the owner's approach. Deliberate owner choices: log before returning an error (Uber: handle errors once), never wrap errors with `%w` (G-10), async event goroutines are fire-and-forget with panic recovery (Uber: no fire-and-forget), three import groups (Uber: two), Builder structs for services (Uber: functional options).

## Authorities (link-only)
- [Effective Go](https://go.dev/doc/effective_go), [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments), [Google Go Style Guide](https://google.github.io/styleguide/go/), [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md), [Go Proverbs](https://go-proverbs.github.io/).
- Stack: [gin-gonic/gin](https://github.com/gin-gonic/gin), [mongo-go-driver v2](https://github.com/mongodb/mongo-go-driver), [google/uuid](https://pkg.go.dev/github.com/google/uuid), [greatcloak/decimal](https://github.com/greatcloak/decimal), [honeycombio/otel-config-go](https://github.com/honeycombio/otel-config-go) (an example OTel setup).

## Per-project layer
Run `/go-conventions` to write `.claude/go-conventions.md` containing only the delta from this baseline. It may add rules and override a topic rule with `# OVERRIDE: G-<TOPIC>-n <reason>`. It may not override G-1..G-8 or G-10. G-9 numbers come from `.golangci.yml`.
