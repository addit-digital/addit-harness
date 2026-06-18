# Naming & formatting

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: Effective Go (https://go.dev/doc/effective_go), Go Code Review Comments (https://go.dev/wiki/CodeReviewComments), Google Go Style — Decisions (https://google.github.io/styleguide/go/decisions), Uber Go Style Guide (https://github.com/uber-go/guide/blob/master/style.md).

## Formatting
- `gofmt` (or `goimports`, which also fixes imports) is non-negotiable — run on save, enforce in CI. No style debates.
- Tabs for indentation. No hard line-length limit, but break very long lines for readability.
- Don't hand-align or hand-format; let the tool win.

## Identifiers
- `MixedCaps` / `mixedCaps`, never `snake_case` or `SCREAMING_CASE` (Go has no constant case convention beyond MixedCaps).
- Exported == capitalized first letter; unexported == lowercase. Export deliberately, not by default.
- Keep acronyms a single case: `userID`, `ServeHTTP`, `parseURL` — not `userId`, `ServeHttp`, `parseUrl`.
- Shorter names in smaller scopes: `i`, `r`, `buf` in a tight loop; descriptive names for package-level symbols.
- Avoid stutter with the package qualifier: in package `chubby`, name it `File`, so callers write `chubby.File` — not `chubby.ChubbyFile`.

## Getters, setters, receivers
- No `Get` prefix on getters: `u.Name()`, not `u.GetName()`. Setters are `SetName(...)`.
- Receiver names are short (1–2 chars) and consistent across all methods of a type:
  ```go
  func (s *Server) Start() error { ... }
  func (s *Server) Stop()  error { ... }   // always s, never sometimes srv
  ```
- Don't name a receiver `this` or `self`.

## Interfaces
- Single-method interfaces take the `-er` suffix: `Reader`, `Writer`, `Stringer`, `Notifier`.

## Imports
- `goimports` groups stdlib first, then third-party (and module-local last if configured), each group blank-line separated:
  ```go
  import (
      "context"
      "fmt"

      "github.com/gin-gonic/gin"
      "go.mongodb.org/mongo-driver/mongo"
  )
  ```
- Alias only to resolve collisions or fix an ugly name (`mrand "math/rand"`). Never use dot-imports outside test helpers. Underscore imports only for documented side effects (drivers).

## Doc comments
- Every exported symbol gets a doc comment, a full sentence starting with the symbol name:
  ```go
  // Server handles inbound widget requests.
  type Server struct { ... }

  // Start begins serving and blocks until ctx is cancelled.
  func (s *Server) Start(ctx context.Context) error { ... }
  ```
- One package doc comment per package (in `doc.go` or the primary file), starting `// Package order ...`.
