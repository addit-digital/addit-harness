# Object Methods & Contracts

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Effective Java 3rd ed, Items 1–14 (https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/).

## `equals` / `hashCode` (Items 10–11)
- Override them together or neither. `equals` must be reflexive, symmetric, transitive, consistent, and `x.equals(null) == false`.
- Whenever `equals` is overridden, `hashCode` must be too: equal objects → equal hash codes.
- Compare the *same* significant fields in both. Records generate both correctly — prefer records for value types.
```java
@Override public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof PhoneNumber pn)) return false;   // pattern instanceof
    return areaCode == pn.areaCode && lineNum == pn.lineNum;
}
@Override public int hashCode() { return Objects.hash(areaCode, lineNum); }
```
- For JPA entities, base `equals`/`hashCode` on a stable business key, not the generated id (see persistence-spring-data.md).

## `Comparable` (Item 14)
- `compareTo` should be consistent with `equals` (document any exception). Build comparators fluently instead of subtracting ints (overflow risk).
```java
private static final Comparator<PhoneNumber> CMP =
    comparingInt((PhoneNumber p) -> p.areaCode).thenComparingInt(p -> p.lineNum);
public int compareTo(PhoneNumber o) { return CMP.compare(this, o); }
```

## `toString` (Item 12)
- Provide a useful `toString` for diagnostics/logging; include the key fields. Records do this for free. Don't leak secrets/PII.

## Static factories over constructors (Item 1)
- Named, can cache/return subtypes, not forced to create a new instance.
```java
static Optional<Color> from(String hex) { ... }   // named, may return empty
public static final Boolean TRUE = ...;            // cached
```

## Builder for many parameters (Item 2)
- Use a builder when a constructor would have 4+ params, many optional. Cleaner than telescoping constructors or setter-based half-built objects.
```java
Pizza p = new Pizza.Builder(SMALL).topping(HAM).topping(ONION).build();
```
- For small fixed shapes, a record (or canonical constructor) is simpler than a builder.

## Resource & lifecycle (Items 8–9)
- Use **try-with-resources** for any `AutoCloseable`; it closes in reverse order and preserves the primary exception (suppressing close errors).
```java
try (var in = Files.newInputStream(p); var out = Files.newOutputStream(q)) {
    in.transferTo(out);
}
```
- Avoid `finalize`/`Cleaner` for cleanup — unpredictable and slow.

## Defensive copies (Item 50)
- Copy mutable constructor inputs *before* validation, and copy mutable fields on return. Don't expose internal arrays/collections directly.
```java
public Period(Date start, Date end) {
    this.start = new Date(start.getTime());   // copy first
    this.end   = new Date(end.getTime());
    if (this.start.after(this.end)) throw new IllegalArgumentException();
}
```
- Prefer immutable types (records, `java.time`, `List.copyOf`) so copies become unnecessary.
