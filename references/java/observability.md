# Java: logging and observability

Scope: logs, metrics, traces. Signals: `Logger`, `log.`, `MeterRegistry`, `Observation`, `management.*`.
OBS-3 is harness inference [I]; a reviewer must accept it.

- **J-OBS-1** Log with SLF4J placeholders (`log.info("order {} paid", id)`), not concatenation. Src: harness default
  Why: the message is only built when the level is enabled.
- **J-OBS-2** Instrument through the Micrometer Observation API and export traces over OTLP. Src: [Boot observability](https://docs.spring.io/spring-boot/reference/actuator/observability.html)
  Why: one observation yields both metrics and spans; Boot documents OpenTelemetry support.
- **J-OBS-3** Put the trace id in every log line (MDC pattern). Src: harness default [I]
  Why: it joins a log line to its trace.
- **J-OBS-4** Never log secrets, tokens or personal data; log ids instead. Src: harness default
  Why: logs are widely readable and kept long.
