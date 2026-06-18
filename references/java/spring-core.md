# Spring Core: DI, Configuration & Profiles

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Spring Framework Core (https://docs.spring.io/spring-framework/reference/core.html); Spring Boot Reference — Core Features (https://docs.spring.io/spring-boot/reference/features/index.html).

## Constructor injection only
- Inject through a single constructor (no `@Autowired` needed) → fields can be `final`, dependencies explicit, class trivially unit-testable without Spring.
- Never field/setter injection for required deps. Lombok `@RequiredArgsConstructor` is fine if the team uses Lombok.
```java
@Service
public class OrderService {
    private final OrderRepository repo;
    private final PaymentClient payments;
    public OrderService(OrderRepository repo, PaymentClient payments) {
        this.repo = repo;
        this.payments = payments;
    }
}
```

## Stereotypes & bean definitions
- `@Service` (business logic), `@Repository` (persistence, translates exceptions), `@Component` (generic), `@RestController` (web) — component scanning wires them.
- Use `@Configuration` + `@Bean` for third-party objects you don't own or that need wiring logic.
- Conditional beans: `@ConditionalOnProperty`, `@ConditionalOnMissingBean`, `@Profile`. Provide library defaults with `@ConditionalOnMissingBean` so users can override.

## Typed configuration
- Prefer `@ConfigurationProperties` (type-safe, validated, IDE-completed) over scattered `@Value`.
```java
@ConfigurationProperties(prefix = "billing")
@Validated
public record BillingProps(@NotNull Duration timeout, @Positive int retries) {}
```
- Enable with `@ConfigurationPropertiesScan` (or `@EnableConfigurationProperties`). Bind to records/immutable types.
- Config precedence (high→low): command-line args → env vars → profile-specific `application-{profile}.yml` → `application.yml` → defaults.

## Profiles
- Keep environment differences in `application-{profile}.yml`; activate with `spring.profiles.active`. Mark profile-only beans with `@Profile("...")`.
- Avoid profile sprawl; don't put secrets in committed property files — inject via env/secret manager.

## Bean scope & lifecycle
- Default singleton; use `prototype`/`request`/`session` deliberately. Singletons must be stateless or thread-safe.
- Lifecycle hooks: `@PostConstruct` / `@PreDestroy` (or `InitializingBean`/`DisposableBean`).
- Don't inject a shorter-scoped bean directly into a singleton — use a provider (`ObjectProvider`) or scoped proxy.

## Architecture & boundaries
- Layer: `@RestController` (HTTP, validation) → `@Service` (logic, `@Transactional`) → `@Repository` (data). Keep dependencies pointing inward.
- **Never return JPA entities from controllers** — map to DTOs (MapStruct or hand-written). Keep domain types out of the web contract.
- One responsibility per service; avoid "god" services and circular bean dependencies (a sign the design needs splitting).
- Enforce layering with ArchUnit (see build-and-testing.md).
