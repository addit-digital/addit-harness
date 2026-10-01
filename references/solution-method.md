# Solution method — mandatory for any non-trivial design

Knowing patterns is not the job. Finding the best answer for *this* problem is.
Your first idea is the most typical one, not necessarily the best. Treat it as candidate A, not the answer.

1. FRAME. Restate the goal, hard constraints, and non-goals. Write the numbers that
   matter (users, QPS, data size/growth, latency and consistency needs, budget, team
   size). If a number is unknown, state an explicit assumption and mark it
   labelled Inferred (assumption) per doc-protocol.md.
2. REFRAME. Answer in ≤5 lines: What known problem class is this (e.g. "append-only
   ledger", "fan-out-on-write feed", "workflow with human steps")? What first
   principles govern it? Which stated constraint is really a preference? What is the
   cheapest way to not need this at all (buy, configure, remove)?
3. DIVERGE. Produce ≥3 candidates that differ in *structure*, not in vendor names
   (Kafka vs RabbitMQ is one candidate, not two). Required:
   - A — proven/boring: what a strong team would ship with mainstream tools.
   - B — first-principles minimal: the least machinery that satisfies FRAME.
   - C — unconventional: a different architectural bet (different data model,
     push computation elsewhere, a specialized engine, a different consistency
     model). Rate each candidate's typicality 0–1. C must be ≤0.3.
   Write one paragraph each; one mermaid sketch only for the top-2 finalists. Do not pick yet.
4. PRIOR ART. Use WebSearch/WebFetch to find how best-in-class teams handled this
   problem class: engineering blogs, papers, well-known OSS. Cite ≥2 sources with URLs
   and say what each one changes about your candidates. If you find nothing, write
   "none found" plus the queries you tried. Never invent a citation.
5. QUANTIFY. Back-of-envelope for each candidate: peak load, storage over 3 years,
   p99 latency path, rough $/month, and the on-call burden (number of stateful components
   to operate). Show the arithmetic.
6. PRE-MORTEM. For each of the top two: "It is 12 months later and this design was
   a failure. What happened?" Give 3 specific stories (not "scalability issues").
   If a story is fatal and cannot be mitigated, drop that candidate and go back to step 3.
7. COMPARE. Build a weighted matrix (criteria come from FRAME, weights sum to 1). If the owner
   or an upstream agent proposed a solution, add it now as a candidate and score it
   the same way. Add a "where it loses" row for every column.
8. RECOMMEND. Give the choice, the runner-up, and KILL CRITERIA: observable signals
   (metric + threshold, or an event) that mean switching to the runner-up. Say what
   you consciously did not design (YAGNI list).

Anti-anchoring: A proposed solution reaches you only as text labelled candidate "Owner", at step 7.

Scale by tier: light — steps 3–6 one line each; say you shrank them. standard — steps 1–6, then a separate call does 7–8 with the owner's idea. deep — explorers do 1–6 for one lens; the synthesizer does 7–8.
