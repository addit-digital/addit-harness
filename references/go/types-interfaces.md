# Types, structs & interfaces

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: Effective Go (https://go.dev/doc/effective_go), Go Code Review Comments (https://go.dev/wiki/CodeReviewComments), Uber Go Style Guide (https://github.com/uber-go/guide/blob/master/style.md), Google Go Style — Best Practices (https://google.github.io/styleguide/go/best-practices).

## Accept interfaces, return concrete types
- Functions take the narrow interface they need and return the concrete struct, so callers stay flexible and implementations stay honest.
  ```go
  // good: caller can pass any reader; returns a usable concrete type
  func NewScanner(r io.Reader) *Scanner { ... }
  ```
- Define interfaces where they are **consumed**, not where they are implemented. The consumer owns the contract.
  ```go
  // in the order package, which needs storage
  type Store interface {
      Save(ctx context.Context, o Order) error
  }
  ```

## Keep interfaces small
- One to three methods is the sweet spot. Big interfaces are hard to satisfy and fake. Compose small ones (`io.ReadWriteCloser`).
- Compile-time compliance check when a type must implement an interface:
  ```go
  var _ Store = (*MongoStore)(nil)
  ```

## Receivers: value vs pointer
- Be consistent per type — if one method needs a pointer receiver, use pointer receivers for all of them.
- Use a pointer receiver when the method mutates, the struct is large, or it contains a `sync.Mutex` (which must not be copied).
- Small immutable values (e.g. a `Point{X, Y int}`) can use value receivers.
- Don't take a pointer just to "save bytes"; fixed-size values are cheap to copy.

## Zero values
- Make the zero value useful where practical: `sync.Mutex`, `bytes.Buffer`, and `strings.Builder` are all ready to use unallocated.
  ```go
  var mu sync.Mutex   // usable immediately, no New needed
  var buf bytes.Buffer
  ```

## Embedding & composition
- Embed for composition, but don't embed types into exported structs casually — it leaks the embedded type's API into yours and couples you to it.
  ```go
  type Handler struct {
      log *slog.Logger   // prefer a named field over embedding *slog.Logger
  }
  ```

## Constructors & options
- Provide `NewX` constructors that return a ready-to-use value. Avoid `init()` — it hides ordering and complicates testing.
- For extensible constructors with many optional params, use functional options:
  ```go
  type Option func(*Server)

  func WithTimeout(d time.Duration) Option { return func(s *Server) { s.timeout = d } }

  func NewServer(addr string, opts ...Option) *Server {
      s := &Server{addr: addr, timeout: 30 * time.Second}
      for _, opt := range opts { opt(s) }
      return s
  }
  ```
