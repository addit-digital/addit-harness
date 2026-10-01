# Go: errors

Scope: error values, propagation, logging. Signals: `errors.New`, `fmt.Errorf`, `if err != nil`, sentinel `Err...`. ERR-1, ERR-2, ERR-5 are overridable by id; ERR-3 restates G-10 and is not.

- **G-ERR-1** Define one typed application error carrying a code, an HTTP status and optional params; it implements `error` and renders to the API. Src: owner
  Why: the rendering middleware (HTTP-4) can map any error to a response without string matching.
- **G-ERR-2** Declare sentinel errors with an `Err` prefix (`ErrNotFound`); unexported ones use `err`. Src: [Uber Go guide, Error Naming](https://github.com/uber-go/guide/blob/master/style.md)
  Why: callers match them with `errors.Is`.
- **G-ERR-3** Never wrap errors (`fmt.Errorf("...: %w", err)`) — propagate the typed `Error` as-is. At the boundary where a driver error enters, convert it to the typed error once. Src: owner (G-10, not overridable)
  Why: handlers and middleware see one error type.
- **G-ERR-4** Compare with `errors.Is` and `errors.As`, never by string. Src: [Go errors blog](https://go.dev/blog/go1.13-errors), [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md)
  Why: it works for sentinels and typed errors independent of message text.
- **G-ERR-5** Log at the failing site before returning the error (`log.Error(...)`), then return it. Src: owner
  Why: the owner's services log where context is richest. This deliberately differs from Uber's "handle errors once".

```go
// repository: convert a driver error into the typed error, once
if errors.Is(err, mongo.ErrNoDocuments) {
	return nil, ErrNotFound // typed; no %w, no wrapping
}
log.Error("find failed", slog.Any("error", err))
return nil, err
```
