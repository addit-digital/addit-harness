# Language Foundations & Modern Syntax (Java 17–21)

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Effective Java 3rd ed (https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/); Google Java Style (https://google.github.io/styleguide/javaguide.html); JEP 444 virtual threads (https://openjdk.org/jeps/444); JDK 21 API (https://docs.oracle.com/en/java/javase/21/docs/api/).

## `var` — local type inference
- Use `var` when the initializer makes the type obvious; it cuts noise on the left.
- Never on fields, method params, or return types (no inference there). Don't use it when it hides the type (e.g. `var x = service.process()` where the result type is unclear).
```java
var orders = new ArrayList<Order>();          // good: RHS states the type
var total = computeTotal(orders);             // avoid: what type is total?
```

## Records — immutable data carriers
- Reach for `record` for DTOs, value objects, query results, multi-value returns. Fields are `final`; you get `equals`/`hashCode`/`toString`/accessors free.
- Validate and normalize in a **compact constructor**; defensively copy mutable components.
```java
public record Money(BigDecimal amount, Currency currency) {
    public Money {                            // compact constructor
        Objects.requireNonNull(amount);
        Objects.requireNonNull(currency);
        amount = amount.stripTrailingZeros(); // normalize before assignment
    }
}
public record Range(List<Integer> values) {
    public Range { values = List.copyOf(values); } // defensive copy → immutable
}
```
- Records can implement interfaces and have static factories/extra methods, but not extend classes.

## Sealed types + pattern matching
- Model closed hierarchies with `sealed` + `permits`; the compiler then enforces exhaustive `switch` (no `default` needed).
```java
sealed interface Shape permits Circle, Square, Rectangle {}
record Circle(double r) implements Shape {}
record Square(double side) implements Shape {}
record Rectangle(double w, double h) implements Shape {}

double area = switch (shape) {                 // exhaustive: no default
    case Circle c       -> Math.PI * c.r() * c.r();
    case Square s       -> s.side() * s.side();
    case Rectangle(double w, double h) -> w * h; // record deconstruction
};
```
- Pattern `instanceof` removes casts: `if (o instanceof Order ord && ord.isPaid())`.
- Guarded patterns: `case Integer i when i > 0 -> ...`.

## Text blocks
- Multi-line literals for SQL/JSON/HTML; preserves layout, fewer escapes.
```java
String sql = """
    select o.id, o.total
    from orders o
    where o.status = 'PAID'
    """;
```

## Enums over int constants
- Type-safe, named, support methods/fields. Use `EnumSet`/`EnumMap` instead of bit fields or ordinal-indexed arrays.
```java
enum Status { NEW, PAID, SHIPPED }
EnumMap<Status, Handler> handlers = new EnumMap<>(Status.class);
```
- Never persist or compare on `ordinal()`; store the `name()` (or an explicit code field).

## Immutability & composition
- Prefer immutable types: `final` fields, no setters, return unmodifiable/defensive copies.
- Favor composition over inheritance (Effective Java Item 18); design for extension explicitly or make classes `final`.
- Minimize mutability and scope; `final` by default for locals and params where it documents intent.
