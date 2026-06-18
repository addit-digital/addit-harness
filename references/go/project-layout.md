# Project layout, modules & build

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: Effective Go (https://go.dev/doc/effective_go), Standard project layout (https://github.com/golang-standards/project-layout), Google Go Style — Best Practices (https://google.github.io/styleguide/go/best-practices), Go modules ref (https://go.dev/ref/mod).

## Modules
- One module per repo (usually). Module path = repo URL: `module github.com/acme/widget`.
- `go.mod` declares the path, Go version, and direct deps; `go.sum` pins checksums — commit both.
- Semantic import versioning: v2+ puts the major version in the path and the module line: `github.com/acme/widget/v2`.
- Add/upgrade with `go get pkg@version`; tidy with `go mod tidy` before committing.

## Directory layout
- `cmd/<binary>/main.go` — thin entrypoints, one dir per binary. Wire deps, then call into packages.
- `internal/` — compiler-enforced privacy: only importable by code rooted at the parent of `internal/`. Default home for app code.
- `pkg/` — use sparingly; only for code genuinely meant for external import. Often unnecessary — don't add it reflexively.
- No `src/` directory; Go modules don't use GOPATH-style layout.

```
widget/
  go.mod
  cmd/widgetd/main.go      # entrypoint
  internal/order/          # business logic, private
  internal/store/          # persistence
  api/openapi.yaml         # optional: schemas/protos
```

## Packages
- Package == directory. Package name is short, lowercase, single word: `order`, not `orderService` or `orders`.
- No underscores, no plurals, no MixedCaps in package names.
- Name a package by what it provides, not the layer. Avoid junk buckets: `util`, `common`, `misc`, `base`, `helpers`, `models`.
- One concept per package; keep the exported API small. Cyclic imports are a design smell — split or invert the dependency.
- Organize files by feature, not by type. There is no "one type per file" rule; group related types/functions together.

## Build & tooling
- `go build ./...` and `go vet ./...` over the whole module in CI.
- Build constraints via the `//go:build` line (top of file, blank line after):
  ```go
  //go:build linux && amd64

  package sys
  ```
- Cross-compile with `GOOS`/`GOARCH`: `GOOS=linux GOARCH=arm64 go build ./cmd/widgetd`.
- `GOFLAGS`, `GOPROXY`, `GONOSUMDB`/`GONOSUMCHECK` tune dependency fetching. Vendoring (`go mod vendor`) is for hermetic/airgapped builds — module proxy is the default and simpler.
