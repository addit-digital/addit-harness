---
paths: ["**/*.java"]
---

# Java conventions (essentials)

Always-on when editing Java (17+, Spring Boot where relevant). The
non-negotiables; match the existing module's style first. For depth (Spring
patterns, JPA/Hibernate, concurrency, testing, worked examples) read
`~/.claude/references/java.md` before substantial Java work.

- **Immutability first:** `final` fields, records for data carriers, unmodifiable
  collections at boundaries. Validate args early (`Objects.requireNonNull`).
- **No null in new APIs:** use `Optional` for absent return values (never for
  fields/params, never bare `.get()`).
- **DI = constructor injection only.** No field/`@Autowired`-on-field injection.
- **Layering:** thin controllers (HTTP + validation), services for logic,
  repositories for persistence. Don't leak entities across the web boundary — use
  DTOs. Externalize config (`@ConfigurationProperties`).
- **Exceptions:** throw specific types; never catch-and-swallow or use exceptions
  for control flow. Wrap with the cause; close resources with try-with-resources.
- **JPA:** beware N+1 (fetch joins/entity graphs); keep transactions at the
  service layer; don't let lazy loading escape the transaction.
- **Concurrency:** prefer `java.util.concurrent` over raw threads; never block on
  the reactive event loop (WebFlux).
- **Testing:** JUnit 5 + AssertJ + Mockito; prefer slice tests
  (`@WebMvcTest`/`@DataJpaTest`) over `@SpringBootTest`; cover error cases; add a
  regression test with every bug fix.
