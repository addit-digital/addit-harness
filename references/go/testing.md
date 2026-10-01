# Go: testing

Scope: `_test.go` files and CI checks. Signals: `testing.T`, `t.Run`, fuzz targets. Overridable by id except TEST-1 and TEST-3, which are G-8.

- **G-TEST-1** Write table-driven tests with a named case struct and `t.Run(tt.name, ...)`. Src: [Go wiki TableDrivenTests](https://go.dev/wiki/TableDrivenTests)
  Why: each case reports its own name and failure message.
- **G-TEST-2** Prefer `t.Errorf` to `t.Fatalf` while later checks are still informative; use `Fatalf` when continuing would panic. Src: [Go wiki TableDrivenTests](https://go.dev/wiki/TableDrivenTests)
  Why: one run then shows every failing case. Include got and want in the message.
- **G-TEST-3** CI runs `go vet ./...`, `go test -race ./...` and `govulncheck ./...`. Src: [Go security best practices](https://go.dev/doc/security/best-practices)
  Why: the race detector and the vulnerability scanner find what review does not.
- **G-TEST-4** Fuzz parsers of untrusted input (`func FuzzParse(f *testing.F)`). Src: [Go security best practices](https://go.dev/doc/security/best-practices)
  Why: the page recommends fuzzing as automated testing for security bugs.
- **G-TEST-5** Keep table tests simple: no conditionals or branching logic inside the loop body. Src: [Uber Go guide, Test Tables](https://github.com/uber-go/guide/blob/master/style.md)
  Why: a test with logic needs its own tests.
