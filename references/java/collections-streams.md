# Collections & Streams

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Effective Java 3rd ed, Items 42–48 (https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/); java.util.stream API (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/package-summary.html).

## Choosing collections
- `ArrayList` for indexed/iteration-heavy; `ArrayDeque` for stack/queue (not `Stack`/`LinkedList`); `HashMap`/`HashSet` for lookup; `LinkedHashMap` for insertion order; `TreeMap`/`TreeSet` for sorted; `EnumMap`/`EnumSet` for enum keys.
- Program to interfaces (`List`, `Map`, `Set`) in fields/params/returns, not implementations.

## Immutable collections
- `List.of`, `Set.of`, `Map.of`/`Map.ofEntries` for small fixed collections (reject nulls, throw on mutation).
- `List.copyOf(x)` for a defensive immutable snapshot. `Collectors.toUnmodifiableList()` from a stream.
- Don't return live internal collections — return copies or unmodifiable views.

## Streams — judiciously (Item 45)
- Use streams for declarative transform/filter/aggregate pipelines. Don't force everything into a stream; a plain loop is often clearer for side-effecting or complex control flow.
- Functions in pipelines must be **side-effect-free**. Use `forEach` only to *report* results, never to mutate state — collect instead.
```java
// not that: forEach mutating external state
words.forEach(w -> counts.merge(w, 1L, Long::sum));
// do this: collect
Map<String, Long> counts = words.stream()
    .collect(groupingBy(identity(), counting()));
```

## Collectors
- `groupingBy`, `partitioningBy`, `counting`, `joining`, `summingInt`, `mapping`.
- `toMap` needs a **merge function** when keys can collide, or it throws on duplicates.
```java
Map<Long, Order> byId = orders.stream()
    .collect(toMap(Order::id, identity(), (a, b) -> b));   // last-wins
```

## Method references & functional interfaces (Items 42–44)
- Prefer method references when clearer (`Order::total`, `String::isBlank`); keep a lambda when it documents intent better.
- Favor the standard functional interfaces (`Function`, `Predicate`, `Supplier`, `Consumer`, `BiFunction`) over custom ones.

## Return types & iteration (Items 47–48)
- Prefer `Collection`/`List` over `Stream` as a return type — callers can stream *or* iterate. Return `Stream` only for large/lazy/infinite sequences.
- `Stream` isn't `Iterable`; don't return it where callers want a for-each loop.
- Avoid parallel streams by default — they help only for large, CPU-bound, splittable work with no shared state; measure before using `.parallel()`.

## Misc
- Prefer `Collections.emptyList()`/`Map.of()` over returning `null` for "no results".
- `computeIfAbsent`/`merge`/`getOrDefault` over check-then-put idioms.
