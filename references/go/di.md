# Go: dependency injection

Scope: constructors for services, repositories and clients. Signals: `func New...`, `type Builder`, struct holding collaborators. Overridable by id.

- **G-DI-1** Services and repositories take an exported `Builder` struct of dependencies; the implementation type is unexported and `NewService(b Builder) Service` returns the interface. Src: owner
  Why: a struct names every dependency at the call site and adding one is not a signature break.
- **G-DI-2** Dependencies in a `Builder` are interfaces, never concrete types. Src: owner
  Why: tests pass fakes.
- **G-DI-3** Assert interface compliance at compile time: `var _ Service = (*service)(nil)`. Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md)
  Why: a broken implementation fails the build, not a runtime wiring path.
- **G-DI-4** Use functional options only for reusable clients with several optional settings (Uber suggests it from three arguments); services use the Builder. Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md), owner
  Why: options suit public APIs that will grow; a service is wired once.
- **G-DI-5** An optional dependency is passed as a pointer or nil-able interface and checked for nil before use. Src: owner
  Why: the feature degrades instead of panicking.

```go
type Builder struct {
	Repository Repository
	Publisher  event.Publisher // interface
}
type service struct{ Builder }

func NewService(b Builder) Service { return &service{Builder: b} }
```
