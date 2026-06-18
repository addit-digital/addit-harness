# Java + Spring Boot conventions — reference index

On-demand, per-topic reference set (not auto-loaded). The always-on essentials live in `../../rules/java.md`; open the relevant file below when doing substantial work in that area. Targets modern Java 17–21 (records, sealed types, pattern matching, virtual threads) and current Spring Boot 3.x.

| Topic file | Open it when... |
|---|---|
| `language-foundations.md` | Using records, sealed types, pattern matching, `var`, text blocks, enums, immutability. |
| `code-style.md` | Questions on naming, formatting, imports, `@Override`, Javadoc, member ordering. |
| `object-contracts.md` | Writing `equals`/`hashCode`/`Comparable`/`toString`, static factories, builders, try-with-resources, defensive copies. |
| `generics.md` | Designing generic APIs — raw types, PECS wildcards, lists vs arrays, `@SafeVarargs`. |
| `collections-streams.md` | Choosing collections, immutable factories, stream pipelines, `Collectors`, method references. |
| `optional-exceptions.md` | Null-safety with `Optional`, parameter validation, exception type/throwing/handling. |
| `time-and-money.md` | Working with `java.time` types, time zones/ISO-8601, or money with `BigDecimal`. |
| `concurrency.md` | Virtual threads, executors, `CompletableFuture`, atomics, locks, thread-safety. |
| `spring-core.md` | DI/constructor injection, `@ConfigurationProperties`, profiles, bean scopes, layering. |
| `spring-web-mvc.md` | Servlet REST controllers, Bean Validation, `@RestControllerAdvice`, RFC 9457 ProblemDetail. |
| `spring-webflux.md` | Reactive `Mono`/`Flux`, `WebClient`, Reactor Context — and whether to use WebFlux vs MVC + virtual threads. |
| `persistence-spring-data.md` | Spring Data JPA: N+1, `@EntityGraph`/JOIN FETCH, LAZY, projections, auditing, OSIV; Mongo parallels. |
| `transactions-caching-pooling.md` | `@Transactional` (propagation/rollback/self-invocation), HikariCP sizing, Caffeine/Redis caching. |
| `spring-security.md` | `SecurityFilterChain` DSL, authN/authZ, method security, password hashing, CSRF/CORS, JWT/OAuth2. |
| `messaging-resilience-observability.md` | Kafka listeners/idempotence/DLT, Resilience4j, Micrometer/Actuator/tracing, JSON logging + MDC. |
| `build-and-testing.md` | Gradle/Maven + Spring BOM, Flyway/Liquibase, JUnit 5, Mockito, slice tests, Testcontainers, WireMock, ArchUnit. |
