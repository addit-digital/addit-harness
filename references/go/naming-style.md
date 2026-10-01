# Go: naming and style

Scope: names, imports, control flow. Signals: new identifiers, `import (`, deep `if` nesting. Idiom follows the surrounding module (precedence line in `rules/go.md`). Overridable by id (STY-4 typically).

- **G-STY-1** Package names are lowercase and singular (`invoice`, not `invoices`), no underscores. Files are `snake_case.go`. Src: owner, [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
  Why: the package name prefixes every use site (`invoice.Service`).
- **G-STY-2** Receiver names are one or two letters of the type (`c`, `cl` for `Client`), never `this`/`self`. Src: [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
  Why: the review comments ask for a short reflection of the type's identity.
- **G-STY-3** Error strings are lowercase with no final punctuation. Src: [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
  Why: they are printed after other context.
- **G-STY-4** Import groups: standard library, then this module, then third-party; alias only to resolve a collision. Src: owner
  Why: goimports keeps the order. Uber's guide uses two groups (stdlib, everything else); owner order wins.
- **G-STY-5** Return early; no `else` after a `return`. Keep nesting at G-9's limit. Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md)
  Why: the happy path stays at the left edge.
- **G-STY-6** No naked boolean or literal arguments when meaning is unclear: name them in a comment or use a typed value. Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md)
  Why: `f(true, false)` cannot be read at the call site.
- **G-STY-7** Start enums at 1 (`iota + 1`) unless the zero value is the meaningful default. Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md)
  Why: an unset field must not look like a valid first value.
- **G-STY-8** Use `time.Duration` for periods and `time.Time` for instants, never bare ints or strings. Src: [Uber Go guide](https://github.com/uber-go/guide/blob/master/style.md)
  Why: units are in the type.
- **G-STY-9** Handlers are named `handle<Action><Resource>` (`handleCreateInvoice`). Src: owner
  Why: a stack trace and a grep both find the route's handler.
