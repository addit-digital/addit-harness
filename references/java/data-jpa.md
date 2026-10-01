# Java: Spring Data JPA and transactions

Scope: transactions, entities, repositories, connection pool. Signals: `@Transactional`, `@Entity`, `*Repository`, `spring.datasource`, `spring.jpa`.
Rules marked [I] are harness inference; a reviewer must accept each.

- **J-DATA-1** The transaction boundary is a public service method; do not put `@Transactional` on controllers or repositories you also call directly. Src: [Spring tx annotations](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
  Why: one use case, one transaction; the proxy only intercepts calls from outside the bean.
- **J-DATA-2** A call from one method to another in the same class does not start a transaction; move it to another bean. Src: [Spring tx annotations](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
  Why: the annotation works through a proxy, and self-invocation bypasses it.
- **J-DATA-3** Mark query-only service methods `@Transactional(readOnly = true)`. Src: harness default [I]
  Why: it states intent and lets the stack skip flush work.
- **J-DATA-4** Set `spring.jpa.open-in-view=false`. Src: [Boot SQL](https://docs.spring.io/spring-boot/reference/data/sql.html)
  Why: Boot registers the open-EntityManager-in-view interceptor by default; off, lazy loading in the view fails fast instead of querying from rendering.
- **J-DATA-5** Avoid N+1 reads with a fetch join or `@EntityGraph`. Src: harness default [I]
  Why: lazy collections otherwise cost one query per parent row.
- **J-DATA-6** Entities never leave the service; return `record` DTOs (J-3). Src: harness default
  Why: serializing an entity exposes columns and triggers lazy loads.
- **J-DATA-7** Size the Hikari pool from `cores * 2 + effective spindles`, then measure under load. Src: [HikariCP pool sizing](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing)
  Why: the page offers it as a starting point and says to test around it; bigger pools often slow the database.
- **J-DATA-8** Change schema through migrations (Flyway/Liquibase); never `ddl-auto=update` outside local dev. Src: harness default [I]
  Why: auto-update cannot drop or rename and leaves environments different.
- **J-DATA-9** Publish events and messages after commit (J-14, kafka KAF-6). Src: [Spring tx events](https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html)
  Why: `@TransactionalEventListener` defaults to `AFTER_COMMIT`, so a rolled-back write sends nothing.
