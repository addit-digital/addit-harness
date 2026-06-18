# Build, Migrations & Testing

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Spring Boot Gradle/Maven plugins (https://docs.spring.io/spring-boot/gradle-plugin/, https://docs.spring.io/spring-boot/maven-plugin/); Flyway (https://documentation.red-gate.com/fd) / Liquibase (https://docs.liquibase.com/); JUnit 5 (https://junit.org/junit5/docs/current/user-guide/); Mockito (https://site.mockito.org/); Testcontainers (https://java.testcontainers.org/); WireMock (https://wiremock.org/docs/); ArchUnit (https://www.archunit.org/).

## Build — Gradle (Kotlin DSL) and Maven
- Let the Spring Boot BOM manage versions; never pin Spring/Jackson/etc. versions by hand.
- **Gradle** (`build.gradle.kts`):
```kotlin
plugins {
    id("org.springframework.boot") version "3.x"
    id("io.spring.dependency-management") version "1.x"
    java
}
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web") // BOM-managed, no version
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```
- **Maven**: inherit `spring-boot-starter-parent` (or import the BOM in `<dependencyManagement>`); declare starters without versions.
- Use `implementation` over `api` to limit leakage; favor reproducible builds (locked toolchain/Java version). Run `dependencyUpdates`/`versions:display-dependency-updates` periodically.

## Database migrations
- **Flyway** (SQL-first, `V1__init.sql`) or **Liquibase** (changelog). Versioned, ordered, **immutable** — never edit an applied migration; add a new one.
- `ddl-auto=validate` in real environments; schema changes only through migrations. Keep migrations idempotent-safe and test them in CI against a real DB (Testcontainers).

## JUnit 5
- `@Test`, lifecycle (`@BeforeEach`/`@AfterEach`), `@Nested` for grouping, `@DisplayName` for readability.
- `@ParameterizedTest` + `@ValueSource`/`@CsvSource`/`@MethodSource` instead of copy-pasted cases.
- Assert with AssertJ (`assertThat(...)`) for fluent, readable assertions. Name tests `method_condition_expectedResult`.
```java
@ParameterizedTest
@CsvSource({"100,0.20,20.00", "50,0.10,5.00"})
void tax_isAmountTimesRate(BigDecimal amt, BigDecimal rate, BigDecimal expected) {
    assertThat(taxes.compute(amt, rate)).isEqualByComparingTo(expected);
}
```

## Mockito
- Mock collaborators, not value objects. `when(...).thenReturn(...)`, `verify(...)` interactions; avoid over-mocking (don't mock what you can construct).
- `@MockBean` (replaces a bean in the Spring context) for slice tests; plain `@Mock`/`@ExtendWith(MockitoExtension.class)` for unit tests.

## Test layering
- **Unit tests** (no Spring) for services — mock collaborators, fastest.
- **Slice tests**: `@WebMvcTest` (controllers + `MockMvc`, mock services), `@DataJpaTest` (repositories against a real/Testcontainers DB), `@JsonTest`, `@RestClientTest`.
- `@SpringBootTest` only for true end-to-end wiring — slow, use sparingly.

## Integration testing
- **Testcontainers** for real Postgres/MySQL/Kafka/Redis — far more trustworthy than H2.
```java
@Testcontainers @SpringBootTest
class OrderIT {
    @Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:16");
    @DynamicPropertySource static void props(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url", db::getJdbcUrl);
        r.add("spring.datasource.username", db::getUsername);
        r.add("spring.datasource.password", db::getPassword);
    }
}
```
- **WireMock** to stub external HTTP dependencies (verify requests, simulate failures/timeouts for resilience tests).

## Architecture tests & quality
- **ArchUnit** to enforce layering/dependency rules (controllers don't touch repositories, no cycles, naming conventions).
- Tests must be deterministic (no real clocks/random/network without control). Use test-data builders/object mothers. Treat coverage as a signal, not a target; add a regression test with every bug fix.
- Secrets never in tests/fixtures; scan for them in CI (OWASP/dependency-check, secret scanning).
