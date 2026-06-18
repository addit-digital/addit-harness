# Concurrency: Virtual Threads, Executors & Atomics

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: JEP 444 virtual threads (https://openjdk.org/jeps/444); Structured concurrency (https://docs.oracle.com/en/java/javase/21/core/structured-concurrency.html); Effective Java 3rd ed, Ch. 11 (https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/).

## Virtual threads (Java 21)
- Use virtual threads for **high-concurrency, blocking I/O** (HTTP calls, JDBC, file). They make thread-per-request scale to millions of cheap threads — write straightforward blocking code, no reactive plumbing.
- **Do not pool virtual threads** — they're cheap; create one per task. Use `Executors.newVirtualThreadPerTaskExecutor()`.
```java
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    var futures = ids.stream()
        .map(id -> exec.submit(() -> fetch(id)))   // one VT per task
        .toList();
    for (var f : futures) results.add(f.get());
}
```
- Spring Boot: `spring.threads.virtual.enabled=true` runs MVC/Tomcat on virtual threads.
- **Avoid pinning**: a virtual thread blocked inside a `synchronized` block pins its carrier. Use `ReentrantLock` around blocking calls instead. (Largely mitigated in JDK 24+, but `ReentrantLock` is still the safe default.)
- Keep `ThreadLocal` use minimal — millions of threads multiply its cost.

## Platform-thread executors
- For CPU-bound work use a bounded platform-thread pool sized near core count; for blocking work prefer virtual threads.
- Always shut executors down (`try (var e = ...)` with the AutoCloseable form, or `shutdown()`/`awaitTermination`).

## CompletableFuture
- Compose async work without blocking intermediate stages; pass an explicit executor.
```java
var a = supplyAsync(() -> quote(x), pool);
var b = supplyAsync(() -> quote(y), pool);
Price best = a.thenCombine(b, Price::min).join();
```
- Handle failures with `exceptionally`/`handle`; don't lose the cause.

## Structured concurrency `[preview]`
- `StructuredTaskScope` ties subtask lifetimes to a scope: fan out, join, propagate cancellation/errors as a unit. Use for "run N tasks, all must succeed" or "first result wins".

## Synchronization & shared state
- Prefer `java.util.concurrent`: `ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue`, `Atomic*`, `ReentrantLock`/`ReadWriteLock` over raw `synchronized`/`wait`/`notify`.
- Best thread-safety is **immutability** — share immutable objects freely (records, `java.time`, unmodifiable collections).
- For visibility of a single mutable flag use `volatile`; for compound updates use `Atomic*` or a lock. Know the happens-before rules.
- Keep critical sections tiny; never call alien/blocking code while holding a lock.
- Document each class's thread-safety (immutable / thread-safe / not thread-safe).

## Reactive interop
- In WebFlux, never block the event loop (`block()`, blocking JDBC). With virtual threads available, plain blocking code on MVC is often simpler than reactive — see spring-webflux.md for the decision.
