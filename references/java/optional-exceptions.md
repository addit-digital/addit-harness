# Optional, Null-Safety & Exceptions

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Effective Java 3rd ed, Items 49–55 & 69–77 (https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/).

## Optional (Item 55)
- Use `Optional<T>` as a **return type** for "maybe absent". Never for fields, parameters, collection elements, or map values (use empty collections / `null`-free designs instead).
- Never call bare `.get()`. Use `orElse`, `orElseGet`, `orElseThrow`, `map`, `filter`, `ifPresent`.
```java
return repo.findById(id);                  // Optional<Order>
Order o = repo.findById(id)
    .orElseThrow(() -> new NotFoundException(id));
String name = find(id).map(User::name).orElse("anonymous");
```
- Don't wrap collections in `Optional` — return an empty collection.
- Avoid `Optional<Integer>` etc. in hot paths; use `OptionalInt`/`OptionalLong` if needed.

## Null-safety
- Avoid `null` in new APIs; prefer `Optional`, empty collections, or null-object. Annotate edges with `@Nullable`/`@NonNull` (one library consistently) so tooling enforces it.
- Validate parameters and fail fast at the top of public methods (Item 49).
```java
public void transfer(Account from, BigDecimal amt) {
    Objects.requireNonNull(from, "from");
    if (amt.signum() <= 0) throw new IllegalArgumentException("amt must be > 0");
}
```

## Exception type selection (Items 69–72)
- Use exceptions only for exceptional conditions, **never for control flow**.
- Unchecked (`RuntimeException` subclasses) for programming errors / unrecoverable conditions — the common case. Checked only when the caller can plausibly recover and you want to force handling.
- Favor standard exceptions: `IllegalArgumentException`, `IllegalStateException`, `NullPointerException`, `IndexOutOfBoundsException`, `UnsupportedOperationException`.

## Throwing & wrapping (Items 73–75)
- Throw exceptions appropriate to the abstraction; translate lower-level ones, preserving the cause (exception chaining).
```java
try {
    return mapper.readValue(json, Invoice.class);
} catch (JsonProcessingException e) {
    throw new InvoiceParseException("bad invoice payload", e);  // chain the cause
}
```
- Include failure-capture detail in the message (the values that caused it) — never secrets/PII.
- Document every thrown exception with `@throws`.

## Handling (Items 76–77)
- Never swallow an exception silently. At minimum log with context; usually rethrow/translate.
```java
catch (IOException ignored) {}              // not that
```
- Handle an error once: log *or* propagate, not both at every layer.
- Strive for failure atomicity — a failed call should leave the object in its prior consistent state.
- Use try-with-resources for cleanup (see object-contracts.md).
