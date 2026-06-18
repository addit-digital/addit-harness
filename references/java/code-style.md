# Code Style & Formatting

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Google Java Style Guide (https://google.github.io/styleguide/javaguide.html); Effective Java 3rd ed (https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/).

## Naming
- `UpperCamelCase` for classes/interfaces/enums/records; `lowerCamelCase` for methods/fields/params/locals; `CONSTANT_CASE` for `static final` constants; lowercase dotted for packages.
- Acronyms are treated as words: `HttpClient`, `xmlId`, `parseUrl` — not `HTTPClient`/`parseURL`.
- Names say what, not how. No Hungarian prefixes, no `I`-prefixed interfaces, no `_` member prefixes.
- Test methods: `method_condition_expectedResult` (e.g. `pay_expiredCard_throws`).

## Formatting
- Pick one indent and apply via a formatter (Google = 2 spaces; many teams use 4). Don't hand-format — wire up `spotless`/`google-java-format` so it's enforced, not debated.
- One top-level class per file; file name matches the public type.
- Braces always, even for one-line `if`/`for`/`while`. One statement per line.
- Keep lines reasonably short (Google: 100 cols). Break long chains/args at logical points.

## Imports
- No wildcard imports (`import java.util.*;`) — list explicitly.
- No unused imports. Order/group via the formatter (don't reorder by hand).
- Avoid static imports except for genuinely fluent APIs (`assertThat`, `Mockito.when`, `Collectors.*` in stream-heavy code).

## Annotations & overrides
- `@Override` on every method that overrides or implements — lets the compiler catch signature drift.
- Put annotations on their own line for methods/types; inline for params is fine.
- Use `@Nullable`/`@NonNull` (one library, consistently — e.g. JSpecify or Spring's) to document nullability at API edges.

## Members & ordering
- Order within a class: static fields → instance fields → constructors → methods. Group related methods; callers above callees reads well.
- Fields `private` and `final` by default; widen access only when needed.
- Minimize the accessibility of every class and member (Effective Java Item 15).

## Documentation
- Javadoc on every exported (public/protected) type and method: what it does, params, return, thrown exceptions. First sentence is a summary fragment.
```java
/**
 * Charges the order's payment method.
 *
 * @param order the order to charge; must be unpaid
 * @return the resulting payment receipt
 * @throws PaymentFailedException if the gateway declines the charge
 */
Receipt charge(Order order);
```
- Add `package-info.java` for package-level docs and shared nullability defaults.
- Comments explain *why*, not *what* the code already says. Delete commented-out code.
- `@throws` for every documented exception, checked or unchecked, that callers should know about.
