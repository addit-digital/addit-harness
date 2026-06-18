# Spring Security

*On-demand reference (not auto-loaded). Part of the Java conventions set; see ../../rules/java.md for the always-on essentials.*

Sources: Spring Security Reference (https://docs.spring.io/spring-security/reference/); OWASP Top 10 (https://owasp.org/www-project-top-ten/); OWASP Cheat Sheets (https://cheatsheetseries.owasp.org/).

## SecurityFilterChain (lambda DSL)
- Configure a `SecurityFilterChain` bean with the lambda DSL. `WebSecurityConfigurerAdapter` is removed — don't use it.
```java
@Bean
SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    return http
        .authorizeHttpRequests(a -> a
            .requestMatchers("/public/**", "/actuator/health").permitAll()
            .requestMatchers("/admin/**").hasRole("ADMIN")
            .anyRequest().authenticated())
        .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()))
        .csrf(csrf -> csrf.disable())            // stateless API: see CSRF note
        .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
        .build();
}
```

## AuthN vs AuthZ
- **Authentication** (who): form login + session for server-rendered apps; **JWT / OAuth2 resource server** for stateless APIs; OAuth2 login for delegated identity.
- **Authorization** (what): URL rules via `authorizeHttpRequests`, plus method security.

## Method security
- Enable `@EnableMethodSecurity` and guard service methods. Prefer authorities/scopes for fine-grained perms; roles for coarse buckets.
```java
@PreAuthorize("hasAuthority('order:write') and #cmd.userId == authentication.name")
Order create(CreateOrder cmd) { ... }
```
- `@PostAuthorize` to filter on the return value; `@PreFilter`/`@PostFilter` for collections.

## Passwords
- Store with a strong adaptive hash — **BCrypt** (default) or **Argon2**; never plaintext, MD5, or unsalted SHA. Use the `DelegatingPasswordEncoder` so hashes are upgradeable.
```java
@Bean PasswordEncoder encoder() { return PasswordEncoderFactories.createDelegatingPasswordEncoder(); }
```

## CSRF & CORS
- **CSRF**: keep it **on** for browser/session apps; safe to disable for stateless token APIs (no ambient cookie auth). If using cookies for tokens, keep CSRF on.
- **CORS**: configure an explicit allow-list of origins/methods/headers via `CorsConfigurationSource`; never reflect arbitrary origins or use `*` with credentials.

## JWT / OAuth2 validation
- Validate **issuer, audience, expiry, and signature** against the provider's JWKS. Configure `spring.security.oauth2.resourceserver.jwt.issuer-uri`. Map scopes/claims to authorities with a `JwtAuthenticationConverter`.
- Keep tokens short-lived; don't put secrets/PII in JWT claims (they're readable).

## General hardening (OWASP)
- Validate and encode all input/output; use parameterized queries (no string-built SQL/JPQL) to prevent injection.
- Secrets via env/secret manager (Vault), never in code or committed config.
- Set security headers (HSTS, `X-Content-Type-Options`, CSP) — Spring Security adds sensible defaults.
- Principle of least privilege for roles, DB users, and service accounts. Don't log credentials/tokens.
