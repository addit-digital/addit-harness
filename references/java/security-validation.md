# Java: security and validation

Scope: request validation, authorization, injection, CORS, CSRF, secrets. Signals: `@RequestBody`, `@Valid`, `@PreAuthorize`, `@Query`, `SecurityFilterChain`, `application.yml`.
Rules marked [I] are harness inference without a fetched source; a reviewer must accept each.

- **J-SEC-1** Put `@Valid` on every `@RequestBody`; put `@Validated` on a class whose methods carry constraint annotations. Src: [Boot validation](https://docs.spring.io/spring-boot/reference/io/validation.html)
  Why: Boot only searches for inline method constraints on `@Validated` classes.
- **J-SEC-2** Enable `@EnableMethodSecurity` and put `@PreAuthorize` on service methods, not only on controllers. Src: [Spring Security method security](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html)
  Why: the check then holds for every caller (jobs, listeners), not just HTTP.
- **J-SEC-3** Bind query values with parameters (`:name` with `@Param`, or `?1`); never concatenate input into JPQL or SQL. Src: [Spring Data JPA query methods](https://docs.spring.io/spring-data/jpa/reference/jpa/query-methods.html)
  Why: bound parameters are never parsed as query text, which closes injection.
- **J-SEC-4** CORS: allow-list each origin; never `*` together with credentials. Src: harness default [I]
  Why: a wildcard with credentials lets any site act as the logged-in user.
- **J-SEC-5** Keep CSRF on for cookie sessions; turn it off only for stateless token APIs. Src: harness default [I]
  Why: cookies are sent automatically by the browser; bearer tokens are not.
- **J-SEC-6** Read secrets from environment or a vault; never commit them in `application.yml`. Src: harness default [I]
  Why: git history keeps a leaked secret forever.
