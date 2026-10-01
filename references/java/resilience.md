# Java: resilience for remote calls

Scope: timeouts, retries, circuit breakers on outbound calls. Signals: `RestClient`, `WebClient`, `@Retry`, `@CircuitBreaker`, Feign.
Rule RES-4 is harness inference [I]; a reviewer must accept it.

- **J-RES-1** Set connect and read timeouts on every client; the library defaults are not a policy. Src: harness default
  Why: a call without a bound holds a thread (or subscription) until the peer decides.
- **J-RES-2** Retry at one layer only, for idempotent operations, with exponential backoff and full jitter, and cap total attempts. Src: [AWS Architecture Blog, Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
  Why: the post compares jitter variants and finds full jitter does less client work than the others; stacked retries multiply load.
- **J-RES-3** Use Resilience4j for circuit breaker and bulkhead; do not adopt Hystrix. Src: [Resilience4j](https://resilience4j.readme.io/docs/getting-started), [Hystrix README](https://github.com/Netflix/Hystrix)
  Why: Hystrix is in maintenance mode and Netflix recommends resilience4j for new work.
- **J-RES-4** Retried writes carry an idempotency key the receiver deduplicates. Src: harness default [I]
  Why: a retry after a lost response otherwise repeats the side effect.
