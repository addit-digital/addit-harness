# Java: API and type design

Scope: public types, constructors, equality, nullness. Signals: new `class`/`record`/`interface`, `equals`, `Optional`, `null` checks.
Item numbers refer to Effective Java 3e; the book page returned 403, so numbers are unverified against the text.

- **J-API-1** Prefer static factory methods to public constructors when names, caching or subtype returns help. Src: [Effective Java 3e, Item 1](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: a name like `of`/`from` documents intent; constructors cannot be named.
- **J-API-2** Use a builder once a type has more than 4 constructor or factory parameters. Src: [Effective Java 3e, Item 2](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: positional arguments of the same type are swapped silently. The 4 is a harness default.
- **J-API-3** Minimize mutability: `record` or `final` fields, no setters unless needed. Src: [Effective Java 3e, Item 17](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: immutable values are thread-safe and cannot be left half-built.
- **J-API-4** Override `equals` and `hashCode` together, over the same fields. Src: [Effective Java 3e, Items 10-11](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: hash-based collections break when only one is overridden. Records generate both.
- **J-API-5** Minimize accessibility: package-private by default, public only for the API. Src: [Effective Java 3e, Item 15](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: every public member is a commitment you must keep.
- **J-API-6** `Optional` is a return type only; never a field, parameter or collection element. Src: [Effective Java 3e, Item 55](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: it signals "may be absent" at the call site; elsewhere it only adds allocation and noise.
- **J-API-7** Prefer composition over inheritance; design for inheritance or mark `final`. Src: [Effective Java 3e, Item 18](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: a subclass depends on superclass internals that can change.
- **J-API-8** Declare variables and parameters by interface (`List`, `Map`), not implementation. Src: [Effective Java 3e, Item 64](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: the implementation can change without touching callers.
- **J-API-9** Copy mutable inputs and outputs at the boundary (`List.copyOf`, `Map.copyOf`). Src: [Effective Java 3e, Item 50](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: callers keep a reference otherwise and can break your invariants later.
- **J-API-10** Mark packages `@NullMarked`; annotate the exceptions `@Nullable`. Src: [JSpecify user guide](https://jspecify.dev/docs/user-guide/)
  Why: `@NullMarked` makes every unannotated type non-null, so only the nullable cases need annotations.
- **J-API-11** Where the build runs Error Prone, add NullAway and fail the build on its errors. Src: [NullAway](https://github.com/uber/NullAway)
  Why: nullness is then checked at compile time instead of discovered as an NPE.
- **J-API-12** Build strings in a loop with `StringBuilder`, not `+=`. Src: harness default
  Why: each `+=` copies the whole string; the compiler does not hoist it out of a loop.

Return empty collections, never null (J-9, Effective Java Item 54).
