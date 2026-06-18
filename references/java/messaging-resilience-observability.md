# Messaging, Resilience & Observability

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Spring for Apache Kafka (https://docs.spring.io/spring-kafka/reference/); Resilience4j (https://resilience4j.readme.io/); Micrometer (https://micrometer.io/docs) & Micrometer Tracing (https://docs.micrometer.io/tracing/reference/); Spring Boot Actuator (https://docs.spring.io/spring-boot/reference/actuator/index.html).

## Kafka (Spring for Apache Kafka)
- Consume with `@KafkaListener`; configure a `ConcurrentKafkaListenerContainerFactory` (concurrency = #partitions). Keep handlers fast and idempotent.
```java
@KafkaListener(topics = "orders", groupId = "billing")
void onOrder(OrderEvent event, Acknowledgment ack) {
    if (processed.contains(event.id())) { ack.acknowledge(); return; }  // idempotent
    billing.charge(event);
    ack.acknowledge();                                                  // manual commit
}
```
- **Producers**: enable idempotence + strong durability: `acks=all`, `enable.idempotence=true`, bounded `retries`. This prevents duplicates/reordering on retry.
- **Consumers**: use `MANUAL`/`MANUAL_IMMEDIATE` ack and commit *after* successful processing (at-least-once). Design consumers idempotent (dedup by event id / use an inbox table) since duplicates are inevitable.
- **Error handling + DLT**: use `DefaultErrorHandler` with exponential backoff and a `DeadLetterPublishingRecoverer` to route poison messages to `<topic>.DLT` after N attempts — don't block the partition forever.
```java
@Bean DefaultErrorHandler errorHandler(KafkaTemplate<?, ?> t) {
    return new DefaultErrorHandler(new DeadLetterPublishingRecoverer(t),
        new ExponentialBackOff(1000L, 2.0));
}
```
- Serialization: JSON for flexibility; Avro/Protobuf + Schema Registry for contract enforcement at scale. Set trusted packages for JSON deserialization.

## Resilience4j
- Protect outbound calls with composable decorators. Typical order outermost→innermost: **Retry → CircuitBreaker → RateLimiter → TimeLimiter → Bulkhead** (so retries don't hammer an open breaker).
```java
@CircuitBreaker(name = "pricing", fallbackMethod = "cachedPrice")
@Retry(name = "pricing")
@TimeLimiter(name = "pricing")
CompletableFuture<Price> price(String sku) { ... }
Price cachedPrice(String sku, Throwable t) { return lastKnown(sku); }
```
- **Circuit breaker** stops cascading failures; **retry** (with backoff + jitter, only on transient errors); **rate limiter** caps call rate; **bulkhead** caps concurrent calls; **time limiter** bounds latency. Always provide a fallback. Don't retry non-idempotent operations.

## Observability — metrics, tracing, health
- **Micrometer** is the metrics facade; export to Prometheus/OTLP. Custom metrics via `MeterRegistry`; `@Timed`/`@Counted` on methods.
```java
meterRegistry.counter("orders.created", "channel", channel).increment();
```
- **Actuator**: expose `health`, `metrics`, `prometheus` (and only those — lock down the rest). Use liveness/readiness probes for k8s.
- **Tracing**: Micrometer Tracing + OpenTelemetry/Brave auto-propagates trace/span IDs across HTTP, Kafka, and `WebClient`/`RestClient`. Set `management.tracing.sampling.probability` appropriately.

## Structured logging + MDC
- Log JSON in prod (Logback `logstash-logback-encoder` or Boot's structured logging). Put correlation/trace IDs in **MDC** so every line is queryable.
```java
try (var ignored = MDC.putCloseable("orderId", id)) { log.info("charging order"); }
```
- Trace/span IDs flow into MDC automatically with Micrometer Tracing. **Never log secrets, tokens, or PII.** Log an error once (see optional-exceptions.md). In WebFlux, propagate MDC via Reactor Context (see spring-webflux.md).
