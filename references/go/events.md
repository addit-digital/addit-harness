# Go: in-process events

Scope: event bus, publishers, listeners. Signals: `Publish(`, `EventName()`, `IsAsync()`, `Subscribe(`. All EVT rules are overridable by id except the G-5/G-6 exceptions they invoke.

- **G-EVT-1** An event is a struct with `EventName() string` and `IsAsync() bool`, defined in one events package per domain. Src: owner
  Why: the bus routes on the name and chooses the dispatch mode.
- **G-EVT-2** Use a sync event (`IsAsync() == false`) for side effects that must succeed: it blocks and propagates the listener's error. Src: owner
  Why: the caller must know the follow-up failed.
- **G-EVT-3** An async event runs in a goroutine with `context.WithoutCancel(ctx)`; the dispatcher recovers panics and logs them, and `_ = publisher.Publish(...)` is the sanctioned discarded error. This is the one fire-and-forget exception to G-5 and G-6. Src: owner
  Why: a panic in a listener goroutine would otherwise crash the process, and Uber's no-fire-and-forget rule is deliberately set aside here.
- **G-EVT-4** Publish only after the state change is persisted. Src: owner
  Why: a subscriber must never see an event for data that is not stored.
- **G-EVT-5** Subscribe listeners in `cmd/` wiring (G-LAY-1). Src: owner
  Why: the bus topology is visible in one place.

```go
// dispatcher, async branch
go func() {
	defer func() { if r := recover(); r != nil { log.Error("listener panic", slog.Any("panic", r)) } }()
	_ = l.Listen(context.WithoutCancel(ctx), ev)
}()
```
