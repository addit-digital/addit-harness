# Structured logging (slog)

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: log/slog package (https://pkg.go.dev/log/slog), Structured logging with slog / Go blog (https://go.dev/blog/slog), Google Go Style — Decisions (https://google.github.io/styleguide/go/decisions).

## Use slog for new code
- `log/slog` (Go 1.21+) is the standard structured logger. Prefer it over `log` and third-party loggers for new code.

## Attributes, not formatted strings
- Log a stable message plus key/value attributes — not interpolated text. This makes logs queryable.
  ```go
  slog.Info("order placed", "order_id", o.ID, "total", o.Total)
  // not: slog.Info(fmt.Sprintf("order %s placed for %d", o.ID, o.Total))
  ```
- Typed attributes avoid the `any` boxing and catch type mistakes:
  ```go
  slog.Info("order placed", slog.String("order_id", o.ID), slog.Int64("total", o.Total))
  ```

## Handlers
- `TextHandler` for local dev (human-readable); `JSONHandler` for production (machine-parseable, ingestible by log pipelines).
- Set level and options via `HandlerOptions`; install a default once at startup:
  ```go
  h := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo})
  slog.SetDefault(slog.New(h))
  ```

## Context & shared attributes
- Use the `...Context` variants so handlers can extract trace/request IDs from `ctx`:
  ```go
  slog.InfoContext(ctx, "handling request", "path", r.URL.Path)
  ```
- Bind shared attributes once with `With` and pass the derived logger down:
  ```go
  reqLog := slog.With("request_id", rid, "user", uid)
  reqLog.Info("authorized")
  ```

## Hygiene
- Never log secrets or PII (tokens, passwords, full card/SSN). Redact at the boundary.
- Log an error **once**, at the boundary that stops propagating it — don't log-and-return the same error (see errors.md).
- Choose levels deliberately: `Debug` for development detail, `Info` for normal events, `Warn` for recoverable anomalies, `Error` for failures that need attention.
- Prefer one logger injected via your handler/service struct over scattered package-global calls (eases testing and per-request enrichment).
