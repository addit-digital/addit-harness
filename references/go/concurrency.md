# Concurrency: goroutines, channels & context

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: Effective Go (https://go.dev/doc/effective_go), context package (https://pkg.go.dev/context), Go Code Review Comments (https://go.dev/wiki/CodeReviewComments), Uber Go Style Guide (https://github.com/uber-go/guide/blob/master/style.md).

## Principles
- "Share memory by communicating." Pick one model per piece of state: a mutex *or* confinement to one goroutine via channels — don't mix.
- Concurrency is not parallelism; add goroutines for clearer structure, not reflexively for speed.

## Goroutine lifetime
- Never fire-and-forget. Every goroutine needs a clear stop condition and an owner that waits for it (`sync.WaitGroup` or `errgroup`).
- No goroutines in `init()`.
- A goroutine blocked forever on a channel is a leak — ensure a terminating sender/receiver or a `ctx.Done()` exit.
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

## Channels
- Express direction in signatures: `<-chan T` (receive-only), `chan<- T` (send-only). Documents ownership.
- The producer owns and closes the channel; receivers never close. Closing a closed channel panics.
- Default buffer size is unbuffered (synchronization point) or 1; justify any larger buffer.

## Context
- Pass `ctx context.Context` as the **first** parameter of any function that does I/O, blocks, or spawns goroutines. Never store it in a struct.
- Propagate cancellation, deadlines, and timeouts; always `defer cancel()`:
  ```go
  ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
  defer cancel()
  ```
- Only put genuinely request-scoped values in context (request ID, auth subject). Never pass optional params or dependencies through it.

## errgroup — fan-out with cancellation + first error
```go
g, ctx := errgroup.WithContext(ctx)
for _, u := range urls {
    g.Go(func() error { return fetch(ctx, u) })   // Go 1.22+: no loop-var copy needed
}
if err := g.Wait(); err != nil {
    return err   // first error cancels ctx for the rest
}
```

## Worker pool
```go
jobs := make(chan Job)
var wg sync.WaitGroup
for range runtime.NumCPU() {
    wg.Add(1)
    go func() { defer wg.Done(); worker(ctx, jobs) }()
}
// feed jobs..., then close(jobs); wg.Wait()
```

## Rate limiting
```go
lim := rate.NewLimiter(rate.Limit(100), 10) // 100/s, burst 10
if err := lim.Wait(ctx); err != nil { return err }
```

- Always run concurrent code under `go test -race`.
