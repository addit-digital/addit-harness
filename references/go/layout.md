# Go: layout and domain packages

Scope: directories, wiring, domain package files. Signals: new package, `cmd/`, `internal/`, `main.go`. Overridable by id in `.claude/go-conventions.md` (LAY-1..3 typically).

- **G-LAY-1** Wire every dependency in `cmd/<app>/main.go` (or `cmd/app.go`); `cmd/` holds wiring and nothing else; services never construct their own dependencies. Src: owner
  Why: one place shows the object graph and tests can inject fakes.
- **G-LAY-2** Put non-exported code under `internal/`; a domain may also live in `pkg/<domain>` (one package per business domain). Src: [Go module layout](https://go.dev/doc/modules/layout), owner
  Why: other modules cannot import `internal/`, so you can refactor it freely.
- **G-LAY-3** A domain package holds `model.go` (entities, `bson`/`db` tags), `service.go`, `repository.go`, `mapper.go`, optionally `listener.go` and `lifecycle.go` (state-machine entities only). Add other files only with a reason. Src: owner
  Why: a fixed file set makes any domain findable without a search.
- **G-LAY-4** No mutable package globals, no side effects in `init()`, no goroutines in `init()`, `os.Exit`/`log.Fatal` only in `main`. Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md)
  Why: globals and `init()` hide dependencies and make tests order-dependent; library code that exits cannot be tested.

```
cmd/<app>/     main.go: wiring only
internal/      database/ errors/ event/ logger/ validator/ ...  (shared infrastructure)
pkg/<domain>/  model.go service.go repository.go mapper.go [listener.go] [lifecycle.go]
```
