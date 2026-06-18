# Slices, maps & strings

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: Effective Go (https://go.dev/doc/effective_go), Go Code Review Comments (https://go.dev/wiki/CodeReviewComments), Uber Go Style Guide (https://github.com/uber-go/guide/blob/master/style.md), Google Go Style — Best Practices (https://google.github.io/styleguide/go/best-practices).

## Slices
- A `nil` slice is valid and usable: `len`, `range`, and `append` all work on it. Prefer returning `nil` over `[]T{}`.
  ```go
  var s []int          // nil, len 0 — fine
  s = append(s, 1)
  ```
- Distinguish `nil` from empty only when the API contract genuinely differs (e.g. JSON `null` vs `[]`).
- Preallocate when the size is known — avoids repeated re-grows:
  ```go
  out := make([]Order, 0, len(ids))
  ```
- `append` may reuse or reallocate the backing array. Reslicing aliases the same memory — mutating one view can corrupt another. Copy when handing a slice to code that retains it.
  ```go
  cp := make([]byte, len(b))
  copy(cp, b)
  ```

## Defensive copies at boundaries
- Don't store a caller's slice/map without copying if you'll mutate it (or they will). Likewise copy before returning internal state you must keep stable.

## Maps
- Preallocate with a size hint: `make(map[string]int, n)`.
- Iteration order is randomized by design — never rely on it; sort keys for deterministic output.
- Maps are **not** safe for concurrent read/write. Guard with a mutex, or use `sync.Map` for the specific append-only / disjoint-key cases it targets.
- Comma-ok distinguishes "absent" from "zero value":
  ```go
  v, ok := m[k]
  ```

## Strings
- Strings are immutable UTF-8 bytes. `len(s)` is bytes, not characters.
- `range` over a string yields runes (code points) with byte offsets; index `s[i]` yields a byte.
  ```go
  for i, r := range "héllo" { _ = i; _ = r } // r is a rune
  ```
- `[]byte(s)` and `[]rune(s)` conversions allocate and copy — avoid in hot loops.
- Build strings with `strings.Builder`, not `+=` in a loop:
  ```go
  var b strings.Builder
  for _, p := range parts { b.WriteString(p) }
  s := b.String()
  ```
- Use `strconv` for number↔string conversion, not `fmt.Sprintf` — it's far faster and clearer:
  ```go
  n, err := strconv.Atoi(s)
  out := strconv.Itoa(n)
  ```
