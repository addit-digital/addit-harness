# Go: context and identity

Scope: `context.Context` use and request-scoped identity. Signals: `ctx`, `context.`, `WithCancel`, `WithTimeout`, user/tenant lookups. CTX-5 and CTX-6 are overridable by id; CTX-1..4 are G-1.

- **G-CTX-1** `ctx` is the first parameter, named `ctx`, on every function that does I/O or can block. Src: [pkg context](https://pkg.go.dev/context)
  Why: it is the documented convention that tooling checks.
- **G-CTX-2** Never store a `Context` in a struct; pass it to each call. Src: [pkg context](https://pkg.go.dev/context)
  Why: a stored context outlives the request it belonged to.
- **G-CTX-3** Never pass a nil `Context`; use `context.TODO()` when unsure. Src: [pkg context](https://pkg.go.dev/context)
  Why: callees may call `ctx.Done()`.
- **G-CTX-4** Use context values only for request-scoped data (identity, correlation id), never for optional parameters. Src: [pkg context](https://pkg.go.dev/context)
  Why: values are untyped and invisible in signatures.
- **G-CTX-5** Read user and tenant identity from the context (set by auth middleware); never take it from request bodies or params, and scope every query by tenant id. Src: owner (G-2)
  Why: client-supplied tenant ids allow cross-tenant access.
- **G-CTX-6** Use `context.WithoutCancel` only for work that must outlive the request (async events, G-EVT-3). Src: [pkg context](https://pkg.go.dev/context), owner
  Why: it keeps request values and drops cancellation, so the work is not cut short when the response is sent.
