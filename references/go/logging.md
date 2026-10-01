# Go: logging

Scope: `log/slog` use. Signals: `slog.`, `logger`, `log.Info`, `logrus`. LOG-2 and LOG-4 are overridable by id (a zap or zerolog repo can comply).

- **G-LOG-1** Use `log/slog`; do not add `logrus` or `log` in new code. Src: [Go slog blog](https://go.dev/blog/slog)
  Why: slog is the standard library's structured logger with swappable handlers.
- **G-LOG-2** Take the logger from the context at the top of each method that logs; it carries correlation id and user info. Src: owner
  Why: every line then joins its request.
- **G-LOG-3** On hot paths use `LogAttrs` with typed attrs (`slog.String`) instead of alternating key/values. Src: [Go slog blog](https://go.dev/blog/slog)
  Why: the blog describes it as more efficient, with fewer allocations.
- **G-LOG-4** Local: JSON handler on stdout. Production: the OpenTelemetry log bridge. Src: owner
  Why: the same call sites feed both.
- **G-LOG-5** Never log secrets, tokens or personal data; log ids. Src: harness default
  Why: logs are widely readable and retained.
