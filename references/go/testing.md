# Testing, benchmarks & linting

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: testing package (https://pkg.go.dev/testing), Fuzzing tutorial (https://go.dev/doc/tutorial/fuzz), Go Code Review Comments (https://go.dev/wiki/CodeReviewComments), golangci-lint (https://golangci-lint.run/).

## Table-driven tests
```go
func TestDouble(t *testing.T) {
    tests := []struct {
        name string
        in   int
        want int
    }{
        {"zero", 0, 0},
        {"positive", 2, 4},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            if got := Double(tt.in); got != tt.want {
                t.Fatalf("Double(%d) = %d, want %d", tt.in, got, tt.want)
            }
        })
    }
}
```
- Subtests via `t.Run` give isolation and selective runs (`go test -run TestDouble/zero`).
- `t.Parallel()` for independent cases (Go 1.22+ scopes the loop variable correctly).
- `t.Fatalf` stops the case (missing prerequisites); `t.Errorf` continues (independent assertions).

## Helpers & cleanup
- Mark assertion helpers with `t.Helper()` so failures point at the caller's line.
- Use `t.Cleanup(fn)` for teardown — runs even on failure, composes better than `defer`.
- `t.TempDir()` / `t.Setenv()` for hermetic filesystem/env state.

## Hermetic & through the API
- Test through exported APIs. Inject clock, network, and FS via small interfaces so tests don't touch real time/IO.
- Prefer hand-written fakes implementing your consumer-side interfaces over heavyweight mock frameworks.
- `testify/require` is fine if the repo already uses it; otherwise stdlib `if got != want`.
- Golden files for large stable output (`-update` flag to regenerate); don't assert on inherently unstable output (map order, timestamps).

## Fuzzing
- Fuzz parsers, decoders, and anything taking untrusted bytes:
  ```go
  func FuzzParse(f *testing.F) {
      f.Add("a=1")
      f.Fuzz(func(t *testing.T, s string) {
          _, _ = Parse(s)   // must not panic
      })
  }
  ```
  Run with `go test -fuzz=FuzzParse`.

## Benchmarks
```go
func BenchmarkSum(b *testing.B) {
    b.ReportAllocs()
    for b.Loop() {   // Go 1.24+; else: for i := 0; i < b.N; i++
        _ = Sum(data)
    }
}
```
- Profile before optimizing (`-cpuprofile`, `pprof`); don't guess hot paths.

## CI gates
- Always run `go test -race ./...` in CI — data races pass functional tests but corrupt production.
- Treat coverage as a signal, not a target.
- Use `golangci-lint` with a committed config; a solid baseline: `errcheck`, `govet`, `staticcheck`, `revive`, `ineffassign`, `gosec`.
