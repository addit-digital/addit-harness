# Spring WebFlux & Reactor

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Spring WebFlux (https://docs.spring.io/spring-framework/reference/web/webflux.html); Project Reactor (https://projectreactor.io/docs/core/release/reference/); JEP 444 (https://openjdk.org/jeps/444).

## When to choose WebFlux vs MVC + virtual threads
- **Default to MVC.** With Java 21 virtual threads (`spring.threads.virtual.enabled=true`), the classic blocking thread-per-request model scales to high concurrency with simple, debuggable code. That covers most services.
- **Choose WebFlux** when you genuinely need: streaming/SSE/WebSocket with backpressure, very high connection counts with a fully non-blocking stack (R2DBC, reactive Kafka, `WebClient`), or you're already reactive end-to-end.
- The reactive payoff disappears the moment one blocking call sneaks in. Don't adopt WebFlux for "performance" without an end-to-end non-blocking driver story.

## Core types
- `Mono<T>` = 0/1 element; `Flux<T>` = 0..N. Nothing runs until subscribed — return the publisher, let the framework subscribe.
```java
@GetMapping("/orders/{id}")
Mono<OrderResponse> get(@PathVariable String id) {
    return orderRepo.findById(id)
        .map(OrderResponse::from)
        .switchIfEmpty(Mono.error(new NotFoundException(id)));
}
```

## Never block the event loop
- No `block()`, blocking JDBC, `Thread.sleep`, or synchronous file I/O on reactive threads — it stalls all requests on that worker.
- Wrap unavoidable blocking work on a dedicated scheduler:
```java
Mono.fromCallable(() -> legacyBlockingCall())
    .subscribeOn(Schedulers.boundedElastic());
```
- `subscribeOn` sets where the source runs; `publishOn` switches threads downstream. Use sparingly and deliberately.

## Operators & errors
- Transform with `map` (sync), `flatMap` (async, returns a publisher), `zip`/`zipWith` (combine), `concatMap` (ordered async), `filter`, `collectList`.
- Errors are signals: `onErrorResume` (fallback publisher), `onErrorMap` (translate), `retryWhen` (backoff). Don't try/catch around reactive chains.
- Apply timeouts (`.timeout(Duration)`) and backpressure-aware operators; avoid `Flux` that buffers unboundedly.

## Context & MDC
- There is no ThreadLocal continuity across operators. Propagate request-scoped data via the **Reactor Context** (`contextWrite` / `Mono.deferContextual`), and use the Micrometer context-propagation library to bridge MDC/trace IDs for logging.

## Clients & data
- Use `WebClient` (reactive) instead of `RestTemplate` for outbound calls in a reactive app.
- For persistence use **R2DBC** or reactive Mongo — a blocking JPA repository defeats the model.

## Testing
- `StepVerifier` to assert signals; `WebTestClient` for endpoint tests.
```java
StepVerifier.create(service.find("x"))
    .expectNextMatches(o -> o.id().equals("x"))
    .verifyComplete();
```
