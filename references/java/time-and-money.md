# java.time, Money & Formatting

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: java.time package (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/package-summary.html); java.math.BigDecimal (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/math/BigDecimal.html).

## Pick the right temporal type
- `Instant` — a machine timestamp (UTC point on the timeline); use for "when did this happen", logs, DB timestamps.
- `LocalDate` — date with no time/zone (birthday, invoice date).
- `LocalTime` — wall-clock time, no date.
- `LocalDateTime` — date+time **without** zone; do *not* use it to represent an instant.
- `ZonedDateTime` — instant interpreted in a specific zone (for display/business rules in a locale).
- `OffsetDateTime` — instant with a fixed UTC offset; common at API/DB boundaries.
- `Duration` — time-based amount (seconds/nanos). `Period` — date-based amount (years/months/days).

## Hard rules
- Never use `java.util.Date`, `Calendar`, or `SimpleDateFormat` in new code — mutable and (the formatter) not thread-safe.
- Store and transmit instants as **UTC + ISO-8601**. Convert to a zone only at the display edge with an explicit `ZoneId` — never rely on the JVM default zone.
```java
Instant now = Instant.now();                              // UTC point
ZonedDateTime local = now.atZone(ZoneId.of("Europe/Berlin"));
Instant due = now.plus(Duration.ofDays(30));
```

## Formatting & parsing
- `DateTimeFormatter` is immutable and thread-safe — share a `static final` instance. Use `DateTimeFormatter.ISO_INSTANT` / `ISO_OFFSET_DATE_TIME` for interchange.
```java
private static final DateTimeFormatter F = DateTimeFormatter.ofPattern("yyyy-MM-dd");
LocalDate d = LocalDate.parse("2026-06-18");              // ISO by default
```
- Provide an explicit `Locale`/`ZoneId` when formatting for users.

## Money — always `BigDecimal`, never `double`
- Binary floating point cannot represent decimal money exactly (`0.1 + 0.2 != 0.3`). Use `BigDecimal`, constructed from a **String**, with an explicit scale and rounding mode.
```java
BigDecimal price = new BigDecimal("19.99");               // not new BigDecimal(19.99)
BigDecimal tax   = price.multiply(new BigDecimal("0.20"))
                        .setScale(2, RoundingMode.HALF_EVEN);  // banker's rounding
```
- Compare amounts with `compareTo` (not `equals` — `2.0` vs `2.00` differ by scale).
- Pair amounts with a `Currency`/`Money` value object (see the `Money` record in language-foundations.md); don't add across currencies.
- Choose the rounding mode deliberately — `HALF_EVEN` for statistics/finance, `HALF_UP` for everyday rounding. Never leave division unrounded (`ArithmeticException` on non-terminating results).
- For DB columns use `NUMERIC/DECIMAL(p, s)`; map to `BigDecimal`.
