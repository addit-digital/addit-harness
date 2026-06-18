# Spring Web MVC: REST, Validation & Errors

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Spring Web MVC (https://docs.spring.io/spring-framework/reference/web/webmvc.html); Bean Validation (https://jakarta.ee/specifications/bean-validation/); RFC 9457 Problem Details (https://www.rfc-editor.org/rfc/rfc9457).

## Controllers & resources
- `@RestController` with resource-oriented URIs and correct verbs/status: `GET` (200), `POST` (201 + `Location`), `PUT`/`PATCH` (200/204), `DELETE` (204). Plural nouns: `/orders/{id}`.
- Keep controllers thin: bind, validate, delegate to a service, map to a response DTO. No business logic, no entities crossing the boundary.
```java
@PostMapping("/orders")
ResponseEntity<OrderResponse> create(@Valid @RequestBody CreateOrder req) {
    var saved = orderService.create(req.toCommand());
    return ResponseEntity.created(URI.create("/orders/" + saved.id()))
                         .body(OrderResponse.from(saved));
}
```

## DTOs & mapping
- Separate request/response DTOs (records) from entities. Map with MapStruct or explicit factory methods. Never serialize JPA entities (lazy-loading + over-exposure leaks).

## Validation at the boundary
- `@Valid` on request bodies; Bean Validation annotations (`@NotNull`, `@NotBlank`, `@Size`, `@Email`, `@Positive`) on the DTO. `@Validated` on the controller for `@RequestParam`/`@PathVariable` constraints.
- Write custom constraints for domain rules rather than ad-hoc `if` checks in the controller.

## Centralized errors → RFC 9457 ProblemDetail
- Handle exceptions in one `@RestControllerAdvice`; return `ProblemDetail` (Spring's RFC 9457 type, `application/problem+json`). Never leak stack traces.
```java
@RestControllerAdvice
class ApiExceptionHandler {
    @ExceptionHandler(NotFoundException.class)
    ProblemDetail handleNotFound(NotFoundException e) {
        var pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
        pd.setType(URI.create("https://api.example.com/errors/not-found"));
        pd.setProperty("resourceId", e.getId());
        return pd;
    }
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ProblemDetail handleValidation(MethodArgumentNotValidException e) {
        var pd = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
        pd.setProperty("errors", e.getFieldErrors().stream()
            .map(f -> Map.of("field", f.getField(), "message", f.getDefaultMessage())).toList());
        return pd;
    }
}
```
- Extend `ResponseEntityExceptionHandler` to get consistent ProblemDetail for Spring's built-in exceptions. Enable `spring.mvc.problemdetails.enabled=true`.

## Pagination, sorting, negotiation
- Accept `Pageable` and return `Page<T>` (or a slim page DTO) for collections; cap page size.
- Content negotiation via `Accept`; default JSON. Use ETag/`If-None-Match` for caching where it helps.

## Idempotency & versioning
- Make `PUT`/`DELETE` idempotent; support an `Idempotency-Key` header for `POST` where retries matter.
- Version when you break the contract (URI `/v2/...` or media-type versioning). Don't silently change response shapes.

## Misc
- Prefer `ResponseEntity` only when you need to set status/headers/`Location`; otherwise return the body and annotate `@ResponseStatus`.
- Document the API with springdoc-openapi; DTO + validation annotations are the contract source of truth.
- For high-concurrency blocking endpoints, enable virtual threads (`spring.threads.virtual.enabled=true`) before reaching for WebFlux.
