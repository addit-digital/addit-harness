# Java — extensive conventions & patterns

On-demand reference (not auto-loaded). Read this for substantial Java work. The
always-on essentials live in `rules/java.md`. Targets modern Java (17/21) and
Spring Boot. Adapted from Effective Java idioms, Spring reference docs, and
[awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)
(java-springboot-jpa).

## Language & modern features
- Prefer `record` for immutable data carriers (DTOs, value objects):
  ```java
  public record Money(BigDecimal amount, Currency currency) {
      public Money {
          Objects.requireNonNull(amount);
          Objects.requireNonNull(currency);
      }
  }
  ```
- Use `var` for obvious locals; sealed types + pattern-matching `switch` for
  closed hierarchies:
  ```java
  sealed interface Shape permits Circle, Square {}
  double area = switch (shape) {
      case Circle c -> Math.PI * c.r() * c.r();
      case Square s -> s.side() * s.side();
  };
  ```
- Avoid `null` in new APIs. Use `Optional` for absent return values; never for
  fields or parameters, never bare `.get()` (use `orElseThrow`, `map`, etc.).
- Favor immutability: `final` fields, no setters on value types, return
  unmodifiable or defensive copies of collections.

## Dependency injection & Spring structure
- **Constructor injection only** (a single constructor needs no `@Autowired`):
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
- Layering: `@RestController` (HTTP mapping + validation) → `@Service` (business
  logic, transactions) → `@Repository` (persistence). Never return JPA entities
  from controllers — map to DTOs.
- Externalize configuration with typed `@ConfigurationProperties`, not scattered
  `@Value`:
  ```java
  @ConfigurationProperties(prefix = "billing")
  public record BillingProps(Duration timeout, int retries) {}
  ```
- Validate request bodies with Bean Validation (`@Valid`, `@NotNull`, `@Size`).

## Exceptions & errors
- Throw specific exceptions; reserve checked exceptions for recoverable
  conditions callers must handle. Don't catch `Exception` broadly except at
  boundaries.
- Never swallow: always wrap with the cause.
  ```java
  catch (IOException e) {
      throw new ReportException("render invoice " + id, e);
  }
  ```
- Centralize web error handling in `@RestControllerAdvice` with
  `@ExceptionHandler`, returning a consistent error body + status.
- Use try-with-resources for anything `AutoCloseable`.

## Persistence (JPA / Hibernate)
- **N+1 is the default footgun.** Fetch associations explicitly:
  ```java
  @Query("select o from Order o join fetch o.items where o.id = :id")
  Optional<Order> findWithItems(@Param("id") Long id);
  ```
  or use an `@EntityGraph`. Default associations to `LAZY`.
- Keep transactions at the **service** layer with `@Transactional`; mark
  read paths `@Transactional(readOnly = true)`. Don't let lazy access escape into
  controllers/serializers (causes `LazyInitializationException`).
- Use DTO projections for read models instead of returning entities:
  ```java
  @Query("select new com.app.OrderView(o.id, o.total) from Order o")
  List<OrderView> findViews();
  ```
- Be deliberate about cascade types and `equals`/`hashCode` on entities (base on
  business key or id, not mutable fields).
- Manage schema with Flyway/Liquibase; never rely on `ddl-auto=update` in prod.

## Concurrency
- Prefer `java.util.concurrent`: `ExecutorService`, `CompletableFuture`,
  concurrent collections — over raw threads and `wait/notify`.
  ```java
  CompletableFuture<Price> a = supplyAsync(() -> quote(x), pool);
  CompletableFuture<Price> b = supplyAsync(() -> quote(y), pool);
  Price best = a.thenCombine(b, Price::min).join();
  ```
- Make shared state immutable or properly synchronized; document thread-safety.
- WebFlux/reactive: never block (`block()`, blocking JDBC) on the event loop;
  keep the chain non-blocking end-to-end; use `Schedulers.boundedElastic()` for
  unavoidable blocking calls.

## Testing
- JUnit 5 + AssertJ + Mockito:
  ```java
  @Test
  void rejectsExpiredCard() {
      when(gateway.charge(any())).thenThrow(new CardExpired());
      assertThatThrownBy(() -> service.pay(order))
          .isInstanceOf(PaymentFailed.class)
          .hasMessageContaining("expired");
  }
  ```
- Prefer fast slice tests over full context: `@WebMvcTest` (controllers, with
  `MockMvc`), `@DataJpaTest` (repositories, with a real/embedded DB), plain unit
  tests for services (mock collaborators).
- Use `@SpringBootTest` only for true end-to-end wiring (it's slow).
- Use Testcontainers for integration tests against real Postgres/MySQL/Kafka.
- Name tests `method_condition_expectedResult`; test behavior via public APIs;
  add a regression test with every bug fix.

## API design
- RESTful resources, correct status codes, consistent error envelope, pagination
  for collections. Version when you break contracts.
- Document with springdoc-openapi; keep DTOs and validation annotations as the
  contract source of truth.
