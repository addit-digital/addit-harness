# Transactions, Caching & Connection Pooling

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Spring Data Access — Transactions (https://docs.spring.io/spring-framework/reference/data-access/transaction.html); HikariCP (https://github.com/brettwooldridge/HikariCP); Spring Cache + Caffeine (https://docs.spring.io/spring-framework/reference/integration/cache.html, https://github.com/ben-manes/caffeine).

## `@Transactional` placement
- Put it on the **service** layer, around a complete unit of work — not on repositories or controllers. Mark read paths `@Transactional(readOnly = true)` (lets Hibernate skip dirty checking and hints the driver).
```java
@Transactional
public Order place(CreateOrder cmd) {
    var order = orderRepo.save(Order.from(cmd));
    inventory.reserve(order);          // same transaction — rolls back together
    return order;
}
```

## Self-invocation pitfall
- Spring transactions work via a proxy. A call from one method of a bean to another `@Transactional` method on **the same bean** bypasses the proxy → no transaction.
```java
public void outer() { this.inner(); }      // inner()'s @Transactional is IGNORED
```
- Fix: move `inner()` to another bean, or inject self, or use `TransactionTemplate`. Same caveat applies to `@Cacheable`/`@Async`.

## Propagation, isolation, rollback
- `REQUIRED` (default) joins an existing tx; `REQUIRES_NEW` suspends and starts an independent one (use for audit logs that must persist even if the outer tx rolls back).
- Default isolation is the DB's (usually READ_COMMITTED); raise only with a concrete need.
- **Rollback default is unchecked exceptions only.** Checked exceptions do *not* roll back unless you set `rollbackFor`:
```java
@Transactional(rollbackFor = PaymentException.class)
```
- Keep transactions short; never do remote calls / long I/O inside them (holds a connection).

## HikariCP sizing
- Pool size should be small. A good starting point: `connections ≈ ((core_count * 2) + effective_spindle_count)` — often 10–20, not hundreds. Oversized pools increase contention and latency.
```yaml
spring.datasource.hikari:
  maximum-pool-size: 10
  minimum-idle: 10
  connection-timeout: 3000      # fail fast rather than queue forever
  max-lifetime: 1800000         # < DB/proxy idle timeout
```
- With virtual threads, the DB pool is still the real concurrency limit — size for the DB, not the thread count.

## Caching
- `@EnableCaching` + `@Cacheable`/`@CachePut`/`@CacheEvict`. Cache idempotent, read-heavy, expensive lookups. Design explicit keys; set TTLs.
```java
@Cacheable(cacheNames = "rates", key = "#from + '-' + #to")
Rate rate(String from, String to) { ... }
```
- **Caffeine** for in-process (single instance, lowest latency, bounded by `maximumSize`/`expireAfterWrite`). **Redis** for shared cache across instances or when entries must survive restarts.
- Beware stale data: pick TTL/eviction to match staleness tolerance; evict on writes. Don't cache user-specific data under a shared key.
- Cache annotations are proxy-based — same self-invocation caveat as transactions.
