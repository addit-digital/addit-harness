# Generics & type parameters

*On-demand reference (not auto-loaded). Part of the Go conventions set; see ../../rules/go.md for the always-on essentials.*

Sources: Go generics tutorial (https://go.dev/doc/tutorial/generics), Tutorial intro to generics / Go blog (https://go.dev/blog/intro-generics), Google Go Style — Best Practices (https://google.github.io/styleguide/go/best-practices).

## Basics
- Type parameters go in square brackets with a constraint:
  ```go
  func Map[T, U any](in []T, f func(T) U) []U {
      out := make([]U, len(in))
      for i, v := range in { out[i] = f(v) }
      return out
  }
  ```
- `any` is the alias for `interface{}` (any type). `comparable` permits `==`/`!=` and is required for map keys / set elements.
  ```go
  func Keys[K comparable, V any](m map[K]V) []K { ... }
  ```

## Constraints
- A constraint is an interface listing methods and/or a type set (union of allowed types):
  ```go
  type Number interface {
      ~int | ~int64 | ~float64   // ~ includes named types with these underlying types
  }
  func Sum[T Number](xs []T) T { var s T; for _, x := range xs { s += x }; return s }
  ```
- The `golang.org/x/exp/constraints` package predefines `Ordered`, `Integer`, `Float`, etc.

## Inference
- Type args are usually inferred from the function args, so call sites stay clean: `Map(nums, sqr)` not `Map[int, int](nums, sqr)`.
- Supply explicit type args only when inference can't determine them (e.g. no value of the type param appears in the arguments).

## When (and when not)
- Use generics for genuinely type-agnostic containers and algorithms (collections, `Map`/`Filter`/`Reduce`, `Min`/`Max`).
- Don't reach for generics to replace interfaces. If behavior varies by type, an interface is clearer; if only the data type varies, a type parameter fits.
- Don't over-generify. A concrete type or `interface{ Method() }` is often simpler and more readable than three type parameters.

## Limitation
- Methods cannot have their own type parameters — only the type or the function can. Design around it: put the type parameter on the type, or make it a standalone generic function.
  ```go
  type Cache[K comparable, V any] struct{ m map[K]V }
  func (c *Cache[K, V]) Get(k K) (V, bool) { v, ok := c.m[k]; return v, ok }
  ```
