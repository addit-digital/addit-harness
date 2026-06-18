---
name: adr
description: Use when the user makes or records a significant architectural or technical decision — choosing a framework, database, protocol, pattern, or trade-off ("we decided to use X instead of Y because..."), or explicitly asks to write an ADR. Captures the decision as a structured Architecture Decision Record in docs/adr/.
user-invocable: true
argument-hint: [short decision title]
---

# Architecture Decision Record (ADR)

Capture a significant architectural/technical decision as a durable, structured
record using Michael Nygard's lightweight format. ADRs live in version control
next to the code so future readers understand *why*, not just *what*.

## When to write one
A decision is ADR-worthy when it is **significant and hard to reverse**:
technology/framework/database choice, API or integration style, data model,
architectural pattern (e.g. monolith vs services, sync vs event-driven),
security approach, or a notable trade-off. Skip trivial, easily-reversed choices.

## Procedure
1. **Locate/initialize the store.** Use `docs/adr/`. If it doesn't exist, create
   it and a `docs/adr/README.md` index. If the repo already has an ADR location
   or template, follow that instead.
2. **Assign the next number.** Sequential, zero-padded: `0001`, `0002`, …. Scan
   existing files for the highest number and increment.
3. **Gather context from the conversation/code.** Extract: what's being decided,
   why now, the forces/constraints, the alternatives considered, and the
   consequences (good and bad). Ask the user only for what you can't infer.
4. **Write the file** `docs/adr/NNNN-kebab-case-title.md` using the template
   below. Be concrete about *alternatives rejected and why* — that's the part
   future readers need most.
5. **Update the index** `docs/adr/README.md` with a row linking the new ADR.
6. **Report** the path and a one-line summary. Don't commit unless asked.

## Template
```markdown
# NNNN. <Title of the decision>

- **Status:** Proposed | Accepted | Deprecated | Superseded by [ADR-XXXX](XXXX-*.md)
- **Date:** YYYY-MM-DD
- **Deciders:** <people involved>

## Context
The forces at play: technical constraints, requirements, and the problem that
makes a decision necessary. State facts, not the choice yet.

## Decision
The change we are making, in active voice: "We will ...". Be specific.

## Alternatives considered
- **Option A** — summary; why rejected (or why not chosen).
- **Option B** — summary; trade-offs.
(Include the chosen option here too, with why it won.)

## Consequences
- **Positive:** what gets better / easier.
- **Negative:** costs, new risks, things now harder.
- **Follow-ups:** migrations, monitoring, or future decisions this implies.
```

## Lifecycle
ADRs are immutable once Accepted. To change a decision, write a **new** ADR and
set the old one's status to `Superseded by [ADR-XXXX]`, with a link both ways.
Never silently edit an accepted decision's substance.
