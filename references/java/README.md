# Java / Spring: conventions by topic

On-demand reference (not auto-loaded). `rules/java.md` holds the precedence line, the J-1..J-14 contract and the topic index; read the one or two topic files that match the edit. Every rule has an id (`J-<TOPIC>-n`) and a `Src:` (a link, or `harness default` for a rule without an external authority). Rules marked [I] are inference; reviewers cite ids in findings.

| Topic | Covers |
|-------|--------|
| `api-design.md` | factories, builders, immutability, equals/hashCode, Optional, nullness |
| `errors.md` | exception choice, translation, `ProblemDetail` |
| `security-validation.md` | `@Valid`, method security, injection, CORS, CSRF, secrets |
| `concurrency.md` | executors, virtual threads, pinning, `CompletableFuture` |
| `spring-layering.md` | package by feature, wiring, config properties, `RestClient` |
| `reactive.md` | no blocking, error operators, Reactor `Context`, `StepVerifier` |
| `data-jpa.md` | transactions, open-in-view, N+1, pool size, migrations |
| `testing.md` | slices, `@MockitoBean`, Testcontainers |
| `resilience.md` | timeouts, retry with jitter, circuit breakers |
| `observability.md` | SLF4J, Micrometer, trace ids |
| `kafka.md` | idempotent producer, error handler, DLT, outbox |
| `build-style.md` | formatter, imports, BOM, wrapper, verification |

## Authorities (linked from the rules)
- [Effective Java, 3rd ed.](https://www.oreilly.com/library/view/effective-java/9780134686097/): item numbers cited in the topics are unverified against the book.
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html): formatting authority.
- [Spring Boot](https://docs.spring.io/spring-boot/) and [Spring Framework](https://docs.spring.io/spring-framework/reference/) reference docs; [Spring Data JPA](https://docs.spring.io/spring-data/jpa/reference/); [Spring for Apache Kafka](https://docs.spring.io/spring-kafka/reference/).
- [spring-projects/spring-petclinic](https://github.com/spring-projects/spring-petclinic): sample app structure.

## Per-project overrides
A project Checkstyle/PMD config sets the J-12 numbers; a project formatter replaces build-style BLD-1/2. There is no per-project Java conventions file.
