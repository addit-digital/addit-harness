# Error handling

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: Working with Errors / Go blog (https://go.dev/blog/go1.13-errors), errors package (https://pkg.go.dev/errors), Go Code Review Comments (https://go.dev/wiki/CodeReviewComments), Uber Go Style Guide (https://github.com/uber-go/guide/blob/master/style.md).

## Errors are values
- Return errors as the last return value; check immediately. Don't defer the check.
  ```go
  o, err := repo.Load(ctx, id)
  if err != nil {
      return fmt.Errorf("load order %s: %w", id, err)
  }
  ```

## Wrap with context
- Add what *this* layer knows using `%w`, which preserves the chain for `Is`/`As`. Don't restate the same fact twice as it travels up.
- Use `%w` only when callers should be able to inspect the wrapped error; use `%v` to deliberately opaque it.

## Sentinels — branch on identity
```go
var ErrNotFound = errors.New("not found")

if errors.Is(err, ErrNotFound) {
    return c.JSON(http.StatusNotFound, ...)
}
```

## Custom types — carry data
```go
type ValidationError struct{ Field, Msg string }

func (e *ValidationError) Error() string { return e.Field + ": " + e.Msg }

var ve *ValidationError
if errors.As(err, &ve) {
    // ve.Field available
}
```

## Multiple errors
- `errors.Join` aggregates (e.g. cleanup + main error); `Is`/`As` see through joins.
  ```go
  err = errors.Join(err, f.Close())
  ```

## Conventions
- Error strings are lowercase, no trailing punctuation: `"connect: timeout"`, not `"Connect: timeout."`. They get embedded in larger messages.
- Handle an error **once**: either log it or return it, never both — double-reporting makes logs noisy and obscures the real boundary.
- Don't `panic` for ordinary failures. Reserve `panic` for unrecoverable programmer errors; `recover` only at a well-defined boundary (e.g. an HTTP middleware), never as routine control flow.
- Handle failed type assertions with the comma-ok form:
  ```go
  v, ok := x.(string)
  if !ok { return fmt.Errorf("want string, got %T", x) }
  ```

## Cleanup
- `defer` cleanup right after acquiring the resource. Check `Close` errors on writers (a failed flush loses data):
  ```go
  f, err := os.Create(path)
  if err != nil { return err }
  defer func() { err = errors.Join(err, f.Close()) }()
  ```
