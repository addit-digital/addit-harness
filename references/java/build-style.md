# Java: build, formatting and static checks

Scope: Gradle/Maven, formatter, imports. Signals: `build.gradle`, `pom.xml`, import blocks. A project formatter replaces BLD-1 and BLD-2 (AOSP 4-space is a valid choice).
BLD-4 is harness inference [I]; a reviewer must accept it.

- **J-BLD-1** Format with google-java-format (or the project's AOSP variant) and let it decide whitespace. Src: [google-java-format](https://github.com/google/google-java-format)
  Why: Google style indents by +2 spaces; a formatter ends debate and diff noise.
- **J-BLD-2** No wildcard imports; always `@Override`; 100-column limit. Src: [Google Java Style 3.3.1, 6.1, 4.4](https://google.github.io/styleguide/javaguide.html)
  Why: explicit imports show dependencies; `@Override` is omitted only when the parent is `@Deprecated`.
- **J-BLD-3** Take versions from the framework BOM (Spring Boot dependency management); do not pin managed artifacts by hand. Src: harness default
  Why: the BOM is tested as a set; individual pins drift into incompatible combinations.
- **J-BLD-4** Build with the committed Gradle or Maven wrapper. Src: harness default [I]
  Why: every machine and CI run uses the same tool version.
- **J-BLD-5** Where adopted, keep dependency verification current (Gradle `gradle/verification-metadata.xml`). Src: [Gradle dependency verification](https://docs.gradle.org/current/userguide/dependency_verification.html)
  Why: a recorded checksum fails the build on a tampered artifact.
- **J-BLD-6** Where adopted, run Error Prone and NullAway in CI. Src: [Error Prone](https://errorprone.info/)
  Why: it catches bug patterns at compile time.
