# Java: errors and exceptions

Scope: throwing, catching, translating and rendering exceptions. Signals: `throw`, `catch`, `try`, `@ControllerAdvice`, `@ExceptionHandler`.
Effective Java item numbers are unverified against the book (page returned 403).

- **J-ERR-1** Use exceptions only for exceptional conditions, never for normal control flow. Src: [Effective Java 3e, Item 69](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: it is slow, hides the real flow and swallows genuine bugs.
- **J-ERR-2** Checked exception for a condition the caller can recover from, runtime exception for a programming error. Src: [Effective Java 3e, Item 70](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: the type tells the caller whether to handle or to fix the code.
- **J-ERR-3** Reuse standard exceptions (`IllegalArgumentException`, `IllegalStateException`, `NoSuchElementException`) before creating your own. Src: [Effective Java 3e, Item 72](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: readers already know their meaning.
- **J-ERR-4** Use try-with-resources for anything `AutoCloseable`. Src: [Effective Java 3e, Item 9](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: it closes in all paths and keeps the primary exception when `close` also fails.
- **J-ERR-5** Translate low-level exceptions to the layer's own exception and keep the cause. Src: [Effective Java 3e, Item 73](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: a service should not leak `SQLException`, and the stack trace must survive.
- **J-ERR-6** Put the failing values in the detail message (id, limit, actual). Src: [Effective Java 3e, Item 75](https://www.oreilly.com/library/view/effective-java/9780134686097/)
  Why: the log line must be enough to reproduce. Exclude secrets and PII (J-11).
- **J-ERR-7** Never leave a `catch` empty; an intentional ignore carries a comment saying why. Src: [Google Java Style 6.2](https://google.github.io/styleguide/javaguide.html)
  Why: the guide calls doing nothing in response to a caught exception very rarely correct.
- **J-ERR-8** REST errors are `ProblemDetail` (RFC 9457), produced by one `@RestControllerAdvice` extending `ResponseEntityExceptionHandler`. Src: [Spring REST errors](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html)
  Why: one handler gives clients a single error shape; controllers stay free of try/catch.
