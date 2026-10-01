# Java: testing

Scope: unit, slice and integration tests in Spring Boot. Signals: `@Test`, `@SpringBootTest`, `@WebMvcTest`, `@MockitoBean`, Testcontainers.
Rules marked [I] are harness inference; a reviewer must accept each.

- **J-TEST-1** Prefer a slice (`@WebMvcTest`, `@DataJpaTest`) to `@SpringBootTest` unless the test needs the whole context. Src: [Boot testing](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html)
  Why: the docs point to `@WebMvcTest` when only the web layer matters; slices start faster and fail closer to the cause.
- **J-TEST-2** Use `@MockitoBean` (Spring Framework) instead of the older Boot `@MockBean`. Src: [Boot testing](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html) [I: version]
  Why: the current docs describe `@MockitoBean`; check your Boot version before migrating, older lines only have `@MockBean`.
- **J-TEST-3** Run DB behaviour against the real engine through Testcontainers with `@ServiceConnection`. Src: [Boot Testcontainers](https://docs.spring.io/spring-boot/reference/testing/testcontainers.html)
  Why: `@ServiceConnection` wires the container's address into the matching beans with no property plumbing; H2 hides dialect differences.
- **J-TEST-4** One behaviour per test; the name states scenario and outcome (`rejectsExpiredToken`). Src: harness default
  Why: a failure name then says what broke.
- **J-TEST-5** No `Thread.sleep` waits; use a latch, `Awaitility` or an injected `Clock`. Src: harness default [I]
  Why: sleeps make tests slow when generous and flaky when tight.
