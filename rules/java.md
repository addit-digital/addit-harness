---
paths: ["**/*.java"]
---

# Java conventions

Auto-loaded when working in Java. Idiomatic, testable, modern Java (17+, Spring
Boot where relevant). Match the existing module's style first; these are the
defaults when there is no local precedent.

## Language & style
- Target modern Java: use `var` for obvious local types, records for immutable
  data carriers, sealed types/switch expressions/pattern matching where they
  clarify intent.
- Prefer immutability: `final` fields, no setters on value types, defensive
  copies or unmodifiable collections at boundaries.
- Use `Optional` for return values that may be absent; never for fields or
  parameters, and never call `.get()` without a guard.
- Avoid `null` in new APIs; document nullability when unavoidable. Validate
  arguments early (`Objects.requireNonNull`, guard clauses).
- Keep methods short and single-purpose; keep classes cohesive.

## Dependency injection & Spring
- **Constructor injection only.** No field/`@Autowired`-on-field injection — it
  hides dependencies and breaks testability. A single constructor needs no
  annotation.
- Depend on interfaces for collaborators that have real alternatives or need
  mocking; don't create interfaces with exactly one impl reflexively.
- Keep controllers thin (HTTP mapping + validation), services for business logic,
  repositories for persistence. Don't leak entities across the web boundary —
  use DTOs.
- Externalize configuration (`@ConfigurationProperties`), never hard-code
  environment-specific values.
- Use `@Transactional` deliberately at the service layer; understand the
  read-only vs read-write and propagation implications.

## Errors & exceptions
- Throw specific exceptions; don't catch-and-swallow. Don't catch `Exception`
  broadly except at well-defined boundaries.
- Prefer unchecked exceptions for programming errors; reserve checked exceptions
  for recoverable conditions callers must handle.
- Never use exceptions for normal control flow.
- Always include context in the message; wrap with the cause
  (`new XException("...", cause)`), never discard the original.
- Close resources with try-with-resources.

## Persistence (JPA/Hibernate)
- Beware N+1: use fetch joins / entity graphs deliberately; don't rely on lazy
  loading across the transaction boundary.
- Keep transactions at the service layer; don't let lazy access escape into
  controllers/serializers.
- Use DTO projections for read models instead of returning full entities to the
  API.

## Concurrency
- Prefer `java.util.concurrent` (executors, `CompletableFuture`, concurrent
  collections) over raw threads and manual `wait/notify`.
- Make shared state immutable or properly synchronized; document thread-safety.
- For reactive code (WebFlux), never block (`block()`, blocking I/O) on the event
  loop; keep the chain non-blocking end to end.

## Testing
- JUnit 5 + AssertJ for fluent assertions; Mockito for mocks. Don't introduce a
  different framework if the repo already standardizes on these.
- One logical assertion theme per test; descriptive test names
  (`methodUnderTest_condition_expectedResult`).
- Test through public behavior, not private internals. Mock collaborators at
  boundaries, not value objects.
- Use `@SpringBootTest` sparingly (slow); prefer slice tests (`@WebMvcTest`,
  `@DataJpaTest`) and plain unit tests.
- Cover edge/error cases; add a regression test with every bug fix.
