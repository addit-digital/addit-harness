# Go — extensive conventions & patterns

On-demand reference (not auto-loaded). Read this for substantial Go work. The
always-on essentials live in `rules/go.md`. Adapted from Effective Go, the Go
Code Review Comments wiki, and idioms in
[awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules).

## Project layout
- Keep `main` packages thin under `cmd/<binary>/`; put reusable logic in
  packages. Use `internal/` for code that must not be imported externally.
- Package = a responsibility, not a layer. Name by what it provides
  (`payment`, `tokenbucket`), not `models`/`utils`/`helpers`.
- One package per directory; avoid cyclic imports (a sign of unclear boundaries).

## Errors
- Wrap with context as the error travels up; don't restate the same fact twice:
  ```go
  if err := repo.Save(ctx, u); err != nil {
      return fmt.Errorf("save user %s: %w", u.ID, err)
  }
  ```
- Sentinel errors for branchable cases; check with `errors.Is`:
  ```go
  var ErrNotFound = errors.New("not found")
  if errors.Is(err, ErrNotFound) { ... }
  ```
- Typed errors when callers need data; extract with `errors.As`:
  ```go
  type ValidationError struct{ Field, Msg string }
  func (e *ValidationError) Error() string { return e.Field + ": " + e.Msg }
  var ve *ValidationError
  if errors.As(err, &ve) { ... }
  ```
- Don't `log` and `return` the same error (double reporting). Log at the top
  boundary that decides to stop propagation.
- `panic` only for truly unrecoverable programmer errors; recover at process
  boundaries (e.g. an HTTP middleware) if at all.

## Interfaces & types
- Define interfaces where they're **consumed**, keep them tiny:
  ```go
  // in the package that needs it
  type UserStore interface {
      ByID(ctx context.Context, id string) (*User, error)
  }
  ```
- Accept interfaces, return concrete structs. This keeps callers flexible and
  implementations honest.
- Prefer composition (embedding) over large interfaces. Use `io.Reader`/`Writer`
  style small contracts.
- Make the zero value useful when practical (e.g. `bytes.Buffer`).

## Concurrency
- Every goroutine needs a clear stop condition tied to `ctx`:
  ```go
  func worker(ctx context.Context, jobs <-chan Job) {
      for {
          select {
          case <-ctx.Done():
              return
          case j, ok := <-jobs:
              if !ok { return }
              handle(ctx, j)
          }
      }
  }
  ```
- Fan-out/fan-in with `errgroup` for cancellation + first-error propagation:
  ```go
  g, ctx := errgroup.WithContext(ctx)
  for _, u := range urls {
      u := u
      g.Go(func() error { return fetch(ctx, u) })
  }
  if err := g.Wait(); err != nil { return err }
  ```
- Pick one model per piece of state: a mutex *or* confinement to one goroutine via
  channels — don't mix. "Share memory by communicating."
- Always `go test -race` for concurrent code. Watch for goroutine leaks (a
  channel with no terminating sender/receiver).
- Pass `ctx context.Context` as the first parameter on anything that does I/O,
  blocks, or spans goroutines. Never store it in a struct.

## API & resource hygiene
- `defer` cleanup immediately after acquiring; check `Close` errors on writers:
  ```go
  f, err := os.Create(path)
  if err != nil { return err }
  defer func() { err = errors.Join(err, f.Close()) }()
  ```
- Set explicit timeouts/deadlines on outbound calls (`http.Client{Timeout: ...}`,
  `context.WithTimeout`). Don't rely on defaults.
- Use `context` deadlines to bound request lifetimes; propagate cancellation.

## HTTP services (net/http, chi, gin, echo)
- Keep handlers thin: decode → validate → call service → encode. Put business
  logic in services, not handlers.
- Return structured errors with appropriate status codes; never leak internal
  error strings to clients.
- Use middleware for cross-cutting concerns (logging, recovery, auth, request
  IDs). Inject dependencies via a handler struct, not globals.
- Stream large responses; set `Content-Type`; respect `r.Context()`.

## Testing
- Table-driven with subtests and named cases:
  ```go
  tests := []struct {
      name string; in int; want int
  }{
      {"zero", 0, 0},
      {"positive", 2, 4},
  }
  for _, tt := range tests {
      tt := tt
      t.Run(tt.name, func(t *testing.T) {
          t.Parallel()
          if got := Double(tt.in); got != tt.want {
              t.Fatalf("Double(%d) = %d, want %d", tt.in, got, tt.want)
          }
      })
  }
  ```
- Test through exported APIs; inject clock/network/FS for hermetic tests.
- `testify/require` is fine if the repo already uses it; otherwise stdlib.
- Use `t.Helper()` in assertion helpers; `t.Cleanup()` for teardown.
- Benchmark hot paths with `testing.B` when performance matters; profile with
  `pprof` rather than guessing.

## Performance (only when measured)
- Preallocate slices/maps with known capacity (`make([]T, 0, n)`).
- Reuse buffers via `sync.Pool` for hot allocation paths.
- Avoid premature optimization; profile first (`go test -bench`, `pprof`).
