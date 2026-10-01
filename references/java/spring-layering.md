# Java: Spring layering and wiring

Scope: package layout, bean wiring, configuration, HTTP clients. Signals: `@Service`, `@RestController`, `@Configuration`, `@Value`, `RestTemplate`.

- **J-SPR-1** Package by feature (`owner`, `vet`, `system`), not by technical layer. Src: [spring-petclinic](https://github.com/spring-projects/spring-petclinic)
  Why: a feature's code changes together; layer packages scatter every change.
- **J-SPR-2** Keep implementation in an `internal` subpackage and expose only the module API; verify with Spring Modulith when the project uses it. Src: [Spring Modulith](https://docs.spring.io/spring-modulith/reference/fundamentals.html)
  Why: a module's beans in sub-packages such as `internal` are shown as non-exposed, so other modules should not depend on them.
- **J-SPR-3** Constructor injection with `final` fields; no field `@Autowired`. Src: [Spring DI](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)
  Why: dependencies are explicit, immutable and set without reflection in tests.
- **J-SPR-4** Bind settings with `@ConfigurationProperties` records instead of scattered `@Value`. Src: [Boot external config](https://docs.spring.io/spring-boot/reference/features/external-config.html)
  Why: constructor binding gives immutable, validated, typed settings in one place.
- **J-SPR-5** Controllers bind, validate, call one service and map; no business logic or repository access. Src: harness default
  Why: logic in controllers is only reachable over HTTP and is hard to test.
- **J-SPR-6** Use `RestClient` for synchronous calls and `WebClient` for reactive ones; write no new `RestTemplate` code. Src: [Spring REST clients](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html)
  Why: the reference deprecates `RestTemplate` as of Spring Framework 7.0 in favour of `RestClient`.
