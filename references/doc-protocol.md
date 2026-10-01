# Document protocol

Read on demand by every agent or skill that writes a plan, solution, review report, ADR, Figma spec or index row. Use the template for the doc type; omit empty sections (never "N/A").

## Principles

- **Write for a decision.** Every section must change what a reader does; if removing it changes nothing, omit it.
- **Current state only.** The doc states the design as it is now. History lives in git and a `## Log` of at most 5 lines. No "v1 said / withdrawn / carried forward" prose.
- **Link, don't restate.** Code by `path:line`, other docs by link. One fact lives in one place.
- **Alternatives: decision-relevant only.** At most 3 rejected options, one line each with the reason.

**Diagrams.** Plans, solutions and structural ADRs include mermaid diagrams: one per concept (structure, flow, interaction, state), showing the current design, edited in place on revision. Candidate sketches are frozen once `## Decision` is written and are exempt from "current". Skip only for trivial edits (typo, one-liner, rename).

**Revising a document.** Edit the existing file in place. Rewrite only the sections the findings name; do not restate unchanged sections; delete superseded text (no "previously / withdrawn / carried forward" prose). Keep one `## Log` of at most 5 lines and drop the oldest beyond 5. Reviews after round 1 are deltas: prior finding ids as resolved/unresolved, plus new findings only; do not re-verify unchanged material. If more than ~30% of the file changes, state why in the Log. Before saving, delete any factual claim you cannot tie to evidence.

**Claims.** Label claims about existing code, runtime behavior, third-party systems, or design data as Observed (with evidence: `path:line`, command + output, Figma node id), Inferred (with premise), or Unknown (listed under Unknowns with what would resolve it, never filled in). Runtime behavior is Observed only after a probe was run and its output cited. A claim with no evidence is removed, not softened.

**Length.** Ceilings are "at most N lines":

| Doc | light | standard | deep |
|---|---|---|---|
| Plan | 40 (the change brief) | 120 | 200 |
| Solution | none | 200 | 350 |

Review report: r1 at most 120, r2+ delta at most 80. Intake brief at most 50. Going over a ceiling needs a one-line reason in `## Log`.

## Templates

### Plan
~~~md
# <title>
**Goal:** <1-2 lines> **Done when:** - [ ] <testable> - [ ] <testable>
## Approach
<one paragraph: chosen path>. Trade-offs: <=3 bullets. Rejected: <=3 one-liners.
(light tier only) ADR: candidate "<title>" | none
## Diagram
<one mermaid block per concept; current state>
## Steps
1. <change> - files: <paths> - accept: <observable criterion>
## Verification
<exact commands / checks>
## Unknowns
- <question> - resolve by: <how>
## Log
- <=5 lines: vN <what changed, finding ids>
~~~

### Solution
~~~md
# <title>
## Problem  (<=8 lines)
## Decision  (<=10 lines)
<choice, why, kill criteria>
ADR: candidate "<title>" | none
## Design
(only what changes; one mermaid diagram per concept, required)
## Claims
| claim | Observed/Inferred/Unknown | evidence |
## Non-goals (things that could be goals but are excluded)
## Rejected (<=3, one line each)
## Unknowns
## Log (<=5 lines)
~~~

The `ADR: candidate` line is the only place an ADR candidate is recorded; it is replaced by the ADR link after plan approval.

### Review report
~~~md
# Review <item> r<n>
**Verdict:** approve | changes | block   **Counts:** B/M/m
## Findings
- **B1** <severity> `path:line` - <problem in 1-2 lines> - fix: <1 line>
## Prior findings (r2+)  B1 resolved | B2 unresolved | ...
## Verified  (only what was run: command -> result)
~~~
No "what is solid" essay; no re-verification of unchanged material; each finding at most 4 lines.

### ADR
ADR: use skills/adr (MADR). Minimal ≤60 lines, full ≤80. Written only after plan approval, from the solution's ADR line.

### Figma implementation spec
~~~md
# <screen> implementation spec
**Source:** file key - page - node ids - tools used (get_design_context / get_variable_defs / get_screenshot) - date
## Observed (node data and variables only)
layout (auto-layout dir/gap/padding as tokens) - components (+ Code Connect / design-system match) - variables by name - text - states present
## Inferred (state the premise)
e.g. responsive behavior, hover/focus - each marked "confirm with designer"
## Unknown (do not implement; ask)
missing states (empty/error/loading/disabled), breakpoints, copy, a11y labels, interactions/transitions, data shape
## Design defects found
| id | node | defect | evidence | handling |
defect types: detached instance - hard-coded value where a token exists - off-scale spacing/color - inconsistent variant across screens - clipped/overlapping layer - missing state - low contrast - unlabeled control - tool output disagrees with screenshot (variant/token mismatch)
handling: follow design | use design-system token | ask designer (default: token, or ask; never silently compensate)
## Implementation notes
token/component mapping only; no invented values; nothing written for an Unknown
~~~
Rules: numbers come from node data or variables, never from measuring a screenshot; read the smallest node that answers the question (metadata first for big frames); after reading, cross-check tool output against the screenshot and log mismatches as defects; at most 150 lines per screen, split by screen.
Producer: whoever reads Figma (main session via figma:figma-design-to-code, or figma-designer, which returns it inline for the caller to save). Path: `solutions/spec-figma-<screen>.md`. Diagram: one stateDiagram when the screen has >2 states.

## Index row
`| date | [title](link) | one sentence: what + status |`, at most 2 rendered lines (≤240 chars). Update the row in place; never add a second row per slug.
