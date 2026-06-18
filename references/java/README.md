# Java / Spring — conventions (vendored + authorities)

On-demand reference (not auto-loaded). The Tier-1 rule `rules/java.md` points
here. Convention text is **vendored from a recognized collection**, not
hand-written.

## Vendored (read these)
| File | Source | License |
|------|--------|---------|
| `java-best-practices.md` | [sanjeed5/awesome-cursor-rules-mdc](https://github.com/sanjeed5/awesome-cursor-rules-mdc) `java.mdc` (community collection derived from the Google Java Style Guide; modern Java 21). Script-generated — treat as a solid baseline, defer to the authorities below on any conflict. | CC0-1.0 |

> Note: the Google Java Style Guide and Effective Java are authoritative but are
> HTML/a book, so they're linked rather than copied.

## Authorities to read (link-only)
- [Effective Java, 3rd ed. (Bloch)](https://www.oreilly.com/library/view/effective-java/9780134686097/) — the single most-cited Java authority (book).
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html) — dominant formatting standard.
- [Spring reference docs](https://docs.spring.io/spring-boot/) ([Framework](https://docs.spring.io/spring-framework/reference/)) — source of truth for Spring/Spring Boot.
- [Spring Guides](https://spring.io/guides) — official task-oriented guides.
- [spring-projects/spring-petclinic](https://github.com/spring-projects/spring-petclinic) — canonical Spring sample app (structure & idioms).

## Stack notes (this user)
- Both **Spring MVC** and **WebFlux**; **Kafka** ([Spring for Apache Kafka](https://docs.spring.io/spring-kafka/reference/)); **Spring Data** ([JPA](https://docs.spring.io/spring-data/jpa/reference/)); **Gradle and Maven**.
- REST errors: use `ProblemDetail` (RFC 9457).
