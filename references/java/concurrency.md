# Java: concurrency and virtual threads

Scope: threads, executors, shared state, virtual threads (JDK 21+). Signals: `Thread`, `ExecutorService`, `synchronized`, `@Async`, `CompletableFuture`.
Effective Java item numbers are unverified against the book (page returned 403). The Netflix pinning post also returned 403 and is not cited.

- **J-CON-1** No mutable static state; share state through injected, thread-safe beans. Src: harness default
  Why: static fields are shared by every request thread and every test.
- **J-CON-2** Use executors and concurrency utilities, not raw `Thread` or `wait/notify`. Src: [Effective Java 3e, Items 80-81](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: executors own thread lifecycle and give you futures, cancellation and bounded queues.
- **J-CON-3** On JDK 21+ set `spring.threads.virtual.enabled=true` for blocking Spring MVC apps. Src: [Boot task execution](https://docs.spring.io/spring-boot/reference/features/task-execution-and-scheduling.html)
  Why: Boot then runs its auto-configured executors and scheduler on virtual threads.
- **J-CON-4** Never pool virtual threads; limit concurrency with a `Semaphore`. Src: [JEP 444](https://openjdk.org/jeps/444)
  Why: virtual threads are cheap per task; a pool exists to ration expensive threads, a semaphore rations a resource.
- **J-CON-5** JDK 21-23: no blocking I/O inside `synchronized`; use `ReentrantLock`. JDK 24+: JEP 491 removes most of that pinning, so the rule is no longer needed there. Src: [JEP 491](https://openjdk.org/jeps/491)
  Why: a virtual thread blocked in `synchronized` keeps its carrier thread, which caps throughput.
- **J-CON-6** Pass an explicit executor to `CompletableFuture` async methods. Src: harness default [I]
  Why: the default is the common pool, shared with unrelated work and unsuited to blocking calls.
