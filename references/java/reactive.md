# Java: reactive code (WebFlux, Reactor)

Scope: `Mono`/`Flux` pipelines and `WebClient`. Signals: `Mono`, `Flux`, `WebClient`, `@EnableWebFlux`, `reactor.core`.
Do not mix this style into Spring MVC code; block-free is the whole point.

- **J-RX-1** Never block in a pipeline (`block()`, JDBC, `Thread.sleep`). If a blocking library is unavoidable, isolate it with `publishOn` on a bounded scheduler. Src: [Spring WebFlux concurrency model](https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html)
  Why: a small event-loop pool serves all requests; one blocked thread stalls many.
- **J-RX-2** Handle errors with `onErrorResume`, `onErrorReturn` or `onErrorMap`; do not wrap pipeline assembly in try/catch. Src: [Reactor error handling](https://projectreactor.io/docs/core/release/reference/coreFeatures/error-handling.html)
  Why: errors are terminal events that travel down the chain to the subscriber's `onError`; the operators are the reference's equivalent of catch blocks.
- **J-RX-3** Carry request-scoped data in the Reactor `Context` (`contextWrite`), not `ThreadLocal`. Src: [Reactor context](https://projectreactor.io/docs/core/release/reference/advancedFeatures/context.html)
  Why: a pipeline can hop threads, so thread-bound data is lost; MDC-based correlation ids are the reference's own example.
- **J-RX-4** Test pipelines with `StepVerifier`. Src: [Reactor testing](https://projectreactor.io/docs/core/release/reference/testing.html)
  Why: it asserts the expected signals step by step and can control virtual time.
- **J-RX-5** Give every `WebClient` call a timeout (`.timeout(Duration)` or client config). Src: harness default
  Why: an unbounded remote call holds the subscription forever.
