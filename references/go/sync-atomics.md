# Synchronization primitives & atomics

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: sync package (https://pkg.go.dev/sync), sync/atomic package (https://pkg.go.dev/sync/atomic), Uber Go Style Guide (https://github.com/uber-go/guide/blob/master/style.md), Go Code Review Comments (https://go.dev/wiki/CodeReviewComments).

## Mutexes
- The zero value of `sync.Mutex`/`sync.RWMutex` is a ready, unlocked lock — no constructor needed.
- Keep critical sections small; do I/O outside the lock. `defer mu.Unlock()` right after `Lock()` to survive early returns.
  ```go
  type Counter struct {
      mu sync.Mutex
      n  int
  }
  func (c *Counter) Inc() {
      c.mu.Lock()
      defer c.mu.Unlock()
      c.n++
  }
  ```
- Use `RWMutex` only when reads dominate and you've measured contention; it's heavier than `Mutex`.
- Embed a mutex unexported and next to the data it guards. Add a comment naming what it protects.

## Don't copy a Mutex
- A `Mutex` must not be copied after first use — copying duplicates lock state and corrupts mutual exclusion. So methods on a struct containing a mutex need **pointer receivers**, and you pass `*T`, never `T`.
  ```go
  func (c *Counter) Value() int { ... }   // pointer receiver — Counter has a Mutex
  ```
- `go vet` catches many lock-copy mistakes.

## Once and Pool
- `sync.Once` for one-time lazy init:
  ```go
  var once sync.Once
  var conn *Client
  func get() *Client { once.Do(func() { conn = dial() }); return conn }
  ```
- `sync.Pool` reuses transient objects on hot allocation paths — use only when profiling shows allocation pressure; objects may vanish at any GC.

## Atomics
- Prefer the typed atomics (Go 1.19+) over the bare functions — they can't be misused with the wrong width and the field can't be accessed non-atomically.
  ```go
  var ready atomic.Bool
  ready.Store(true)
  if ready.Load() { ... }

  var seq atomic.Int64
  id := seq.Add(1)

  var cfg atomic.Pointer[Config]   // lock-free config swap
  cfg.Store(newCfg)
  ```
- Atomics protect a single word; for invariants spanning multiple fields, use a mutex.

## Globals & races
- Avoid mutable package-level globals. If unavoidable, make them immutable after init or guard every access with a mutex/atomic.
- Data-race freedom is mandatory, not optional. Run `go test -race` in CI; the race detector finds real bugs that pass functionally.
