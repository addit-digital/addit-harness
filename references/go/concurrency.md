# Go: concurrency

Scope: goroutines, channels, locks, shared state. Signals: `go func`, `chan`, `sync.`, `errgroup`, `atomic`. CON-1 is G-6; the rest are overridable by id.

- **G-CON-1** Every goroutine has an owner that can stop it and wait for it; make its exit obvious or document when and why it exits. Sole exception: event-bus async dispatch (G-EVT-3). Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md), [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
  Why: leaked goroutines hold memory and resources, and a goroutine blocked on a channel is never collected.
- **G-CON-2** Fan out with `errgroup.WithContext` and bound it with `SetLimit`. Src: [errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup)
  Why: the first error cancels the siblings and the limit bounds load.
- **G-CON-3** Channels are unbuffered or size 1; any other size needs a reason. Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md)
  Why: a large buffer hides a stalled consumer until it fills under load.
- **G-CON-4** Use the zero-value `sync.Mutex`/`sync.RWMutex` as a field; almost never a pointer to one, never embedded in the struct (even an unexported one). Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md)
  Why: the zero value is ready to use, and embedding exposes `Lock`/`Unlock` as methods of the type.
- **G-CON-5** Copy slices and maps when receiving or returning them across a boundary. Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md)
  Why: the caller keeps a reference and can mutate your state.
- **G-CON-6** Use `atomic.Int64`/`atomic.Bool` (Go 1.19+), not raw `int64` with `atomic.AddInt64`, and not `go.uber.org/atomic`. Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md) [I: stdlib types remove the guide's reason]
  Why: the type makes a non-atomic access impossible.
- **G-CON-7** Where a package starts goroutines, add `goleak.VerifyTestMain(m)` in a `TestMain`. Src: [goleak](https://github.com/uber-go/goleak)
  Why: a leak fails the test run instead of surfacing in production.
