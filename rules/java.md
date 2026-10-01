---
paths: ["**/*.java"]
---

# Java

Contract ids apply to new and changed code. Formatting, naming and idiom follow the surrounding module. A project linter/formatter config sets numbers and format.

| ID | Rule | Src |
|---|---|---|
| J-1 | Constructor injection, `final` fields; no field `@Autowired` | Spring DI |
| J-2 | Controllers bind, validate, call one service, map. `@Transactional` on public service methods; self-invocation is not transactional | Spring tx |
| J-3 | Never return JPA entities from an API (map to `record` DTOs); `spring.jpa.open-in-view=false` | harness default; Boot SQL |
| J-4 | Validate every request body (`@Valid`); authorize in the service (`@PreAuthorize`); never build JPQL/SQL by concatenation | Boot validation; Spring Security; Spring Data JPA |
| J-5 | Never swallow an exception (an intentional ignore gets a comment). REST errors: `ProblemDetail` from one `@RestControllerAdvice` | Google Style 6.2; Spring REST errors |
| J-6 | Every remote call has a timeout; retry at one layer, idempotent ops only, exponential backoff with full jitter | AWS Architecture Blog; Resilience4j |
| J-7 | Never pool virtual threads; cap with a `Semaphore`. JDK 21-23: no blocking I/O in `synchronized` (use `ReentrantLock`) | JEP 444, JEP 491 |
| J-8 | Reactive code never blocks (`block()`, JDBC, `Thread.sleep`) | Spring WebFlux |
| J-9 | Immutable by default (`record`, `final`); empty collections, not null; `Optional` only as a return type | Effective Java 17, 54, 55 |
| J-10 | `@NullMarked` packages + `@Nullable`; NullAway where the build has Error Prone | JSpecify; NullAway |
| J-11 | SLF4J placeholders, no concatenation; never log secrets, tokens or PII | harness default |
| J-12 | Method <= 60 lines (hard 150), cyclomatic <= 10, params <= 7 | Checkstyle 150/10/7; 60 harness default |
| J-13 | Behaviour change ships with a test; prefer slices (`@WebMvcTest`, `@DataJpaTest`); DB via Testcontainers `@ServiceConnection` | Boot testing |
| J-14 | Side effects leave the transaction only after commit (`@TransactionalEventListener` or outbox). Consumers idempotent; `DefaultErrorHandler` with backoff + DLT | Spring tx events; Spring Kafka; KIP-679 |

Overrides: a project Checkstyle/PMD config replaces J-12 numbers; a project formatter replaces build-style BLD-1/2. Read the topic that matches the edit:

- `~/.claude/references/java/api-design.md` public types, records, builders, equals
- `~/.claude/references/java/errors.md` exceptions, `@ControllerAdvice`
- `~/.claude/references/java/security-validation.md` `@Valid`, `@PreAuthorize`, CORS, CSRF, secrets
- `~/.claude/references/java/concurrency.md` threads, executors, virtual threads
- `~/.claude/references/java/spring-layering.md` packages, `@Configuration*`, `RestClient`
- `~/.claude/references/java/reactive.md` `Mono`, `Flux`, `WebClient`
- `~/.claude/references/java/data-jpa.md` `@Transactional`, `*Repository`, entities
- `~/.claude/references/java/testing.md` `@SpringBootTest`, Mockito, Testcontainers
- `~/.claude/references/java/resilience.md` timeouts, retries, circuit breakers
- `~/.claude/references/java/observability.md` logging, Micrometer, tracing
- `~/.claude/references/java/kafka.md` `@KafkaListener`, `KafkaTemplate`
- `~/.claude/references/java/build-style.md` Gradle/Maven, formatter, imports
