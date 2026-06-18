# Go conventions — on-demand reference index

Deep, source-backed Go conventions split by topic. These are Tier-2: read on demand, **not** auto-loaded. The always-on essentials live in `../../rules/go.md`. Open only the file relevant to the task at hand.

| Topic file | Open it when you are… |
| --- | --- |
| [project-layout.md](project-layout.md) | Structuring a module/repo — `cmd/`, `internal/`, package naming, `go.mod`, build tags. |
| [naming-formatting.md](naming-formatting.md) | Naming identifiers, receivers, interfaces; gofmt/goimports, acronym case, doc comments. |
| [types-interfaces.md](types-interfaces.md) | Designing structs/interfaces — accept-interfaces/return-concrete, receivers, zero values, functional options. |
| [errors.md](errors.md) | Handling errors — `%w` wrapping, `errors.Is/As/Join`, sentinels, custom types, panic/recover. |
| [concurrency.md](concurrency.md) | Writing goroutines, channels, `context`, cancellation, worker pools, errgroup, rate limiting. |
| [sync-atomics.md](sync-atomics.md) | Using mutexes, `sync.Once`/`Pool`, typed atomics; avoiding lock-copy bugs and data races. |
| [data-structures.md](data-structures.md) | Working with slices, maps, and strings — nil/aliasing/capacity, map order, UTF-8/runes. |
| [generics.md](generics.md) | Writing generic containers/algorithms — type params, constraints, inference, when not to. |
| [json-serialization.md](json-serialization.md) | Marshaling JSON — struct tags, `omitempty` pitfalls, nullable pointers, custom marshalers, strict decode. |
| [logging-slog.md](logging-slog.md) | Adding structured logging with `log/slog` — attrs, handlers, context/trace IDs, hygiene. |
| [config.md](config.md) | Loading configuration — flags vs env precedence, typed config, fail-fast validation, secrets. |
| [persistence.md](persistence.md) | Talking to a database — MongoDB (`mongo-go-driver`) primary, plus `database/sql`; migrations. |
| [http-gin.md](http-gin.md) | Building an HTTP service with Gin — routing/groups, binding+validation, middleware, errors, graceful shutdown. |
| [testing.md](testing.md) | Writing tests/benchmarks — table-driven subtests, fakes, fuzzing, `-race`, golangci-lint. |
