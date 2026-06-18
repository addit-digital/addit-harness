# Configuration, flags & environment

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: flag package (https://pkg.go.dev/flag), Effective Go (https://go.dev/doc/effective_go), Twelve-Factor config (https://12factor.net/config).

## Sources & precedence
- `flag` for CLI invocation; environment variables for deploy/runtime config (containers, secrets injection).
- Establish a clear precedence and document it: **flag > env > default**.
- Don't scatter `os.Getenv` calls through the codebase. Read all config in one place at startup into a typed struct.

## Typed config, validated at startup
```go
type Config struct {
    Addr     string
    MongoURI string
    LogLevel slog.Level
    Timeout  time.Duration
}

func Load() (Config, error) {
    c := Config{
        Addr:    getenv("ADDR", ":8080"),
        Timeout: 30 * time.Second,
    }
    c.MongoURI = os.Getenv("MONGO_URI")
    if c.MongoURI == "" {
        return Config{}, errors.New("MONGO_URI is required")
    }
    return c, nil
}

func getenv(k, def string) string {
    if v := os.Getenv(k); v != "" { return v }
    return def
}
```
- Fail fast: validate required values and parse durations/levels at startup, before serving. A misconfigured process should exit immediately with a clear message, not fail on the first request.

## Flags
```go
addr := flag.String("addr", ":8080", "listen address")
flag.Parse()
```
- Define flags in `main`, not in `init()` or library packages (libraries shouldn't register global flags).

## Secrets
- Never hardcode or commit secrets. Read them from env vars or a secret manager (Vault, cloud secret store) at startup.
- Keep secrets out of logs, error messages, and config dumps (see logging-slog.md).
- For richer needs (files + env + flags layered), `spf13/viper` is common — but only adopt it when plain `flag`/env genuinely falls short; don't add it speculatively.
