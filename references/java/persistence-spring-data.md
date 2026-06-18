# Spring Data JPA & Persistence

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Spring Data JPA (https://docs.spring.io/spring-data/jpa/reference/); Hibernate ORM (https://hibernate.org/orm/documentation/); Spring Data MongoDB (https://docs.spring.io/spring-data/mongodb/reference/).

## Repositories
- Extend `JpaRepository<Entity, ID>`. Use derived query methods for simple cases (`findByStatusAndCreatedAtAfter`), `@Query` (JPQL) for anything non-trivial — derived names get unreadable fast.
- `@Modifying @Query` for bulk update/delete; they bypass the persistence context, so `clearAutomatically = true` (or flush/clear) to avoid stale state.

## N+1 — the default footgun
- Lazy associations accessed in a loop fire one query per row. Fetch explicitly:
```java
@EntityGraph(attributePaths = {"items", "customer"})
List<Order> findByStatus(Status status);

@Query("select o from Order o join fetch o.items where o.id = :id")
Optional<Order> findWithItems(@Param("id") Long id);
```
- Use `@EntityGraph` for repository methods, `JOIN FETCH` for custom JPQL. For collections + pagination, fetch ids first then the graph (JOIN FETCH + paging loads all rows in memory).
- Set `hibernate.default_batch_fetch_size` to soften remaining N+1.

## Fetch strategy
- **Everything `LAZY`.** `@ManyToOne`/`@OneToOne` default to EAGER — override with `fetch = FetchType.LAZY`. Never `EAGER` on collections.

## Projections over full entities
- For read models, return interface or DTO projections so only needed columns load:
```java
interface OrderView { Long getId(); BigDecimal getTotal(); }
List<OrderView> findByStatus(Status status);

@Query("select new com.app.OrderView(o.id, o.total) from Order o")
List<OrderView> views();
```

## Entity design
- `equals`/`hashCode` on a **stable business key** (e.g. natural id / UUID assigned at construction), never the DB-generated id (null before persist, breaks `Set` membership). Records can't be entities — use classes.
- Be deliberate with `cascade` and `orphanRemoval`; avoid bidirectional relationships unless needed, and keep both sides in sync via helper methods.
- Assign UUID/natural keys in the constructor to make `equals` stable from creation.

## Transactions & OSIV
- Keep `@Transactional` at the **service** layer; `readOnly = true` on read paths (see transactions-caching-pooling.md).
- **Disable Open-Session-In-View**: `spring.jpa.open-in-view=false`. It hides lazy-load-in-view as N+1 at render time and holds connections too long — fetch what you need in the service instead.

## Auditing & schema
- `@EnableJpaAuditing` + `@CreatedDate`/`@LastModifiedDate`/`@CreatedBy`/`@LastModifiedBy` on a base `@MappedSuperclass`.
- Manage schema with Flyway/Liquibase; never `ddl-auto=update` in prod (use `validate`). See build-and-testing.md.
- Pagination with `Pageable`/`Page<T>`; cap sizes.

## Spring Data MongoDB parallels
- `MongoRepository<T, ID>` mirrors the API; `@Document`/`@Field`/`@Indexed` instead of JPA annotations; `MongoTemplate` for complex/aggregation queries.
- No JOINs — model with embedding vs referencing; there's no JPA-style N+1, but `$lookup` and manual ref resolution have their own cost. Create indexes deliberately; transactions need a replica set.
