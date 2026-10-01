# Java: Kafka producers and consumers

Scope: Spring for Apache Kafka. Signals: `@KafkaListener`, `KafkaTemplate`, `DefaultErrorHandler`, `spring.kafka`.
KAF-2 is harness inference [I]; a reviewer must accept it.

- **J-KAF-1** Leave producer idempotence and `acks=all` at their defaults; never set `enable.idempotence=false` or `acks=1`. Src: [KIP-679](https://cwiki.apache.org/confluence/display/KAFKA/KIP-679%3A+Producer+will+enable+the+strongest+delivery+guarantee+by+default)
  Why: since Kafka 3.0 the producer defaults are `enable.idempotence=true` and `acks=all`.
- **J-KAF-2** Key records by aggregate id. Src: harness default [I]
  Why: one key lands in one partition, which keeps per-entity order.
- **J-KAF-3** Configure `DefaultErrorHandler` with a real backoff (`ExponentialBackOff` or `FixedBackOff` with a delay). Src: [Spring Kafka error handling](https://docs.spring.io/spring-kafka/reference/kafka/annotation-error-handling.html)
  Why: the default is `FixedBackOff(0L, 9)`: ten attempts with no delay, then the failure is only logged.
- **J-KAF-4** Pair the handler with `DeadLetterPublishingRecoverer`; the dead-letter topic is `<topic>-dlt` by default. Src: [Spring Kafka error handling](https://docs.spring.io/spring-kafka/reference/kafka/annotation-error-handling.html)
  Why: the default resolver uses the same partition number, so the DLT needs at least as many partitions as the source topic.
- **J-KAF-5** Consumers are idempotent: a redelivered record must not repeat its side effect (dedupe on an event id). Src: harness default
  Why: retries and rebalances deliver at least once.
- **J-KAF-6** Publish after commit: an outbox table, or a `@TransactionalEventListener` (default `AFTER_COMMIT`). Src: [Spring tx events](https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html)
  Why: a send inside the transaction survives a rollback that undoes the data it describes.
