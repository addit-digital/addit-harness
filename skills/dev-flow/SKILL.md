---
name: dev-flow
description: Use to drive a software feature or fix through the full engineering loop — investigate, design (with an architect-reviewer gate), get your explicit approval on the plan, then implement, verify with qa-engineer, and drive the code-review fix loop to a clean state. Deterministic multi-agent orchestration for the design-gate and review-gate loops this setup's engineering-loop rule already describes, so you don't have to hand-drive each Agent call yourself. Software-development-lifecycle scoped (not a generic router) — for legal or marketing work, use the relevant subagent directly.
user-invocable: true
argument-hint: "[what to build or fix] [--tier light|standard|deep]"
---

# dev-flow — deterministic SDLC orchestration

Drives a work item through the full loop this setup's `rules/engineering-loop.md`
already describes by hand: triage (a script scores the tier from facts) → investigate →
design ⇄ `architect-reviewer` (converges or caps) → **you approve the plan** →
implement → code-review ⇄ fix (converges or caps) → `qa-engineer` verifies once (and
re-verifies only if a fix was needed). Effort is proportional: `light`, `standard` or
`deep`. The design-gate and review-gate loops run as deterministic `Workflow` scripts
(real loop-until-approved control flow, not the model remembering to keep looping);
the one thing that stays a plain conversational step is your approval of the plan —
nothing skips that gate.

## 1. Gather the request

Take the work request as given. Don't ask for more detail than you need to resolve
the fields below — if it's already clear from the request, resolve it silently.
If the request carries `--tier light|standard|deep`, strip it from the request text
and keep it as `userTier` — it is an exact override of the triaged tier (step 6).

## 2. Resolve `track` and `needsUX`

- `track` is exactly one of `'backend'`, `'frontend'`, `'both'` — never anything
  else. Infer it from the request (a UI change → `frontend`; an API/data change →
  `backend`; anything touching both → `both`). Ask via `AskUserQuestion` only if the
  request genuinely doesn't say and the target repo doesn't make it obvious (e.g. a
  backend-only service repo settles it without asking).
- `needsUX` is a separate boolean, not a track value — true only when the work needs
  a fresh UX pass (new flow, new screen, a UI change with no existing design to work
  from). A bugfix or an already-specced change is usually `false`. Infer from the
  request; ask only if it's a genuine toss-up.

## 3. Resolve `investigate`

Decided by the tier chosen in step 6, not by judgment: `deep` → `true`; `standard` →
`true` only if triage returned `evidence.confidence: 'low'`; `light` → `false`.
`product-owner` frames the problem before any design work starts. Don't ask the user
"should I investigate first." When intake (step 6.3) produced a brief, it satisfies
this: pass `briefPath` and the workflow skips its own investigator.

## 4. Resolve `repo` and `secondaryRepo`

- `repo` **defaults to the current working directory** — no need to ask, matching
  every other skill in this setup (`code-review`, `save-plan`) that implicitly
  operates on "the repo you're in."
- `secondaryRepo` stays unset unless `track === 'both'`. In that case, do a quick
  check of the cwd first — e.g. a `go.mod` or a server-flavored `package.json` with
  no sibling frontend `package.json`, or vice versa, suggests the other track lives
  elsewhere. Only if that check can't confirm both codebases live in `repo`, ask via
  `AskUserQuestion` where the other track's repo is. Don't ask when the cwd is
  obviously a full-stack monorepo.

## 5. Resolve `slug`

- If the request names or implies an issue-tracker ticket, use
  `<ticket-id>-<short-kebab-name>`.
- Otherwise, `$(date +%F)-<short-kebab-name>`.
- Collision check: run `ls -d <repo>/docs/work/<slug>` (and `<secondaryRepo>`); if it
  exists and this session did not create or receive that slug, append -2, -3 …
  until absent; plugin conventions win (rules/engineering-loop.md).
- Validate against `/^[A-Za-z0-9][A-Za-z0-9._-]*$/` — this becomes a directory name
  and flows into every file path both workflow scripts write; don't let anything
  unvalidated near it.

## 6. Check `Workflow` availability, then triage and the tier gate

Look at what's actually callable in this session right now — don't assume based on
whether `Workflow` merely appears in a tool grant somewhere. If it's genuinely not
callable, skip to **"Fallback — no `Workflow` tool"** below and drive the same
procedure by hand instead.

Also note: `Workflow` being callable doesn't guarantee `workflows/dev-flow-design.js`
actually exists at the resolved `${CLAUDE_PLUGIN_ROOT}` path — that only holds under
a real plugin install (see the file's own "Claude Code plugin install only" note in
`README.md`/`skills/SOURCES.md`). **If the `Workflow` call itself errors** (e.g. the
script path can't be resolved), treat that the same as "`Workflow` isn't usable here"
and fall through to the manual fallback below rather than surfacing a raw tool error.

If it is callable, triage first. It is one read-only agent that reports facts; the
tier is scored by deterministic JS, never by the agent:

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/dev-flow-triage.js",
  args: { slug, track, needsUX, repo, request, userTier },
})
```

**Tier gate.** Show the user: `tier` (`light` | `standard` | `deep`), `S` and `R` with
`sizeTier` / `riskTier`, the `overrides` that held, `wouldBeT0`, `triageFailed` if set
(then the tier is `standard`), and the tier's row of the worst-case table below. At `deep`, say: "deep design phase costs ≈ +40–80% tokens vs standard". The user answers `ok`, `deeper` (one tier up)
or `lighter` (one tier down); the result is the run's `tier`. If `lighter` lands on
`light` while `needsUX` is true, say "UX pass skipped at light" and carry on — light
never runs the UX loop. Resolve `investigate` (step 3) from the final tier.
At `standard`/`deep` the tier-gate question is not a separate prompt: it is slot 1 of the
first intake batch (step 6.3). Triage is read-only and also reachable directly as
`/addit-harness:dev-flow-triage`.

Worst-case agent calls per tier (hard caps, asserted by the mock suite; a run that
needs fewer simply makes fewer). `both` = backend and frontend tracks; the last column
is one track with a UX pass. The `standard`/`deep` design caps include the owner-idea call
(one per track) and, at `deep`, the three explorers and one candidate switch:

| Tier | Design A (`both`, +UX) | Implement B (`both`) | Whole run incl. triage | One track, +UX |
|---|---|---|---|---|
| `light` | 4 (no UX) | 13 | 18 | 12 (no UX) |
| `standard` | 23 | 22 | 46 | 38 |
| `deep` | 27 | 22 | 50 | 42 |

## 6.2. Lifecycle task list

If `TaskCreate` is available (setup turns the task tools on with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`; without them skip this section silently), create these six tasks once, right after triage (or at the start when there is no triage), and keep them current with `TaskUpdate` at the existing steps: `Triage`, `Design + plan`, `Approve plan`, `Implement + review`, `QA`, `Commit`.

- Tier gate answered: `Triage` done (subject `Triage (<tier>)`). `Workflow A` started: `Design + plan` in progress; returned: done.
- Plan shown at step 7: `Approve plan` in progress; approved (7.5): done.
- `Workflow B` started: `Implement + review` in progress; returned: `Implement + review` and `QA` done (QA only if it ran).
- `Commit` stays pending: committing is the user's call.
- `haltedBy` set (or the plan not approved): leave the current task in progress and append ` (halted: <haltedBy>)` to its subject.

Task text is the names above plus the tier and `haltedBy`: no request text, code or paths.

## 6.3. Intake — interview and brief

**Intake.** light: tier gate only; request used as-is; with a Figma URL ask only the Figma spec's Unknowns before implementation guidance. standard: `product-owner` mode=questions; one `AskUserQuestion` batch of ≤4 (slot 1 = tier gate; add track/secondaryRepo if unresolved; then its questions) — skip questions if it returned none; mode=brief; show the brief; continue. deep: same, plus at most one more ≤4 batch for gaps the answers opened; confirm the brief (correct / edit) only if ≥1 default was applied. Headless: all defaults, say so. Never swap the request for the brief silently: the brief quotes it and the owner sees it. Read `specs/owner-proposal.md` if present and pass its text as `ownerProposal`; pass `briefPath`.

The brief is `docs/work/<slug>/specs/brief.md` (absolute path in `repo` as `briefPath`). When
`specs/owner-proposal.md` exists, pass `request` = the brief's "Original request" quote
(proposal already replaced by `[proposed approach moved out]`), so the proposal reaches the
workflow only as the `ownerProposal` text. If the tier gate lands on `light`, skip the brief.

## 6.5. Run `Workflow A`

`fanoutTrack` is the track (`backend` | `frontend`) whose repo holds more of triage's
`riskPaths` (tie → `backend`; one track → that track); only `deep` uses it, to pick the
track that gets the parallel explorers.

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/dev-flow-design.js",
  args: { slug, track, needsUX, investigate, repo, secondaryRepo, request, tier, plannedFiles, riskPaths, briefPath, ownerProposal, fanoutTrack },
})
```

Then continue the conversation normally — in this harness, a `<task-notification>`
is the standard, demonstrated mechanism for a completed background call to resume
the conversation (the same pattern every backgrounded `Agent` call already uses), so
there's no need to poll or hold the turn open here. That said, this specific
interactive-continuation behavior for `Workflow` itself hasn't been confirmed by a
live dogfood run yet (see the design plan's Verification section) — if a run
genuinely never resumes, that's the signal this note needs revisiting, not something
to silently work around. A fully non-interactive/headless invocation, if this skill
is ever triggered that way, would need an explicit wait loop instead, since there's
no later turn for a notification to land in — not the common case this skill is
written for.

While any workflow runs, `/workflows` shows its metadata-only log lines: `dev-flow <name> start: tier=… track=…`, `<Loop> r<n>/<cap>: <k> at/above <floor>` per round, `gate <name>: <verdict>`, and `HALT <haltedBy>: …`. Point the user there instead of narrating progress.

## 7. When `Workflow A` returns — reconcile the index, then stop for approval

1. **Reconcile the `docs/work/README.md` index row — you are its sole owner**
   (spawned agents are told not to touch it; multiple agents write into the same
   work-item folder, sometimes concurrently, so a shared index appended to by more
   than one writer is a real race). Delete every table row whose *first markdown
   link* resolves inside `<slug>/`, then insert one canonical row
   (`| date | [Title](<slug>/plans/plan.md) | summary |`). Row format: references/doc-protocol.md "Index row".
   Run this after Workflow A, after Workflow B, and on any `haltedBy`.
2. Report to the user, blockers first: `haltedBy` if set; `designApproved: false`
   ("the design did not converge after N rounds; this is a capped-out draft, not an
   approved design", with `designBlocking` qualifying findings, plus `designBreaker` if
   the loop stopped on repeated findings — at `light` there is no loop, so say "design
   did not converge — N blocking findings" and offer `deeper`); `tracksCompleted` if it
   lists fewer tracks than `track` asked for;
   `planApproved` and `planFindings`; `uxApproved: false` as a blocker ("the UX spec is
   an unapproved draft"). Don't present a capped-out result the same way you'd present
   a converged one.
3. **If `planWritten` is `false`, stop** — there is no plan, so no approval is offered.
4. Otherwise show the plan and **stop here and wait for explicit human approval.**
   This is the one hard-coded gate the whole point of this exists to preserve — do not
   infer approval from silence, do not proceed on your own judgment that the plan
   looks fine. Ask plainly if it isn't already clear whether they've approved.

## 7.5. Only after explicit approval in the user's own message — record it

1. Append `> dev-flow: approved by user on $(date +%F)` as the last line of
   `docs/work/<slug>/plans/plan.md`.
2. For each `ADR: candidate "<title>"` line (skip `none`) in the solution docs'
   `## Decision` — at `light`, in `plan.md` `## Approach` — invoke `addit-harness:adr`;
   it replaces that line with the ADR link.
3. Compute `PLAN_SHA=$(shasum -a 256 docs/work/<slug>/plans/plan.md | cut -d' ' -f1)`.
   Do this last: any later edit to `plan.md` invalidates the hash and the gate below
   refuses to start.

## 8. Run `Workflow B`

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/dev-flow-implement.js",
  args: { slug, track, repo, secondaryRepo, planSha256: PLAN_SHA, tier, plannedFiles, riskPaths },
})
```

A `PreToolUse` hook (`hooks/gate-dev-flow-implement.sh`) checks that `plan.md` exists,
carries the approval marker, and hashes to `planSha256`; the script re-checks the hash
format. **If the call is denied, report the denial verbatim and stop** — do not retry,
do not edit the plan to make the hash match, do not work around it.

The gate stops accidents: a direct `/addit-harness:dev-flow-implement`, a stale slug, a
plan edited after approval. It does **not** stop a model that ignores these instructions
and writes the marker and hash itself — the human approval in the conversation remains
the real gate.

Same async handling as step 6 — continue normally, the notification arrives when
it's done. When it returns, reconcile the index row again (step 7.1).

## 9. When `Workflow B` returns — report, don't commit

**If `haltedBy` is `escalation`** (scope breach, `light` only): the first review found
the change outside what triage predicted — `scopeBreach.risk` lists risk-surface files
outside the plan, `scopeBreach.magnitude` means it crossed a file-count band. `scopeBreach.unknown` means the reviewers reported no touched files, so the scope could not be verified and `light` escalates rather than assume no breach. Nothing
after that review ran (no QA). Show the breached files and ask: keep the working tree,
`git stash` it, or discard it. Then re-run the tier gate (step 6) preset to `standard`,
run `Workflow A` again, and get the plan re-approved (new marker, new `planSha256`)
before `Workflow B` — at most one such re-entry.

**If `haltedBy` is `implement-failed`**: a developer agent returned no result, so the plan
was not (fully) implemented; review and QA did not run and `clean` / `qaPassed` are false.
Report which track failed (`implementSucceeded: false`), show the working tree state, and
offer to re-run `Workflow B` (same plan, same `planSha256`).

Otherwise report the final pass/fail and findings plainly — `haltedBy` if set; whether
the review loop capped out without reaching clean (`reviewBreaker` if it stopped on
repeated findings; `reviewRounds` / `fixRounds`); that review findings were filtered
at the tier's severity floor (`light` hides `major` and `minor` by design; `standard`
hides `minor`); and what QA found (`qaRuns`: 1 on the happy path; 2 if QA failed and a
fix cycle ran — it runs even on a non-converged review loop, so the report reflects
real final state). If `postQaFixRan` and `postQaFixReviewed` is false (always at
`light`), say "the post-QA fix was not code-reviewed". **You do not run `git commit`** — that stays the
user's call, unchanged from every other agent/skill in this setup. State that
explicitly so it's not ambiguous.

## Fallback — no `Workflow` tool

If `Workflow` isn't callable, drive the identical procedure yourself via direct,
sequential `Agent` calls in this conversation, following the same phase order and
loop logic both scripts encode (design ⇄ `architect-reviewer` until approved or
capped at 3 rounds; implement; code-review ⇄ fix for up to 2 fix rounds plus a final
verdict-only `code-reviewer` pass; `qa-engineer` verify once, and on failure one fix
cycle plus re-verify) — same
human-approval gate before implementation starts (including the approval marker and
`planSha256` by hand, step 7.5), same "you don't commit" rule at the end. This is slower and
more manual than the scripted version, but the procedure and its gates don't change.
Without `Workflow` there is no triage: run the `standard` tier (or the `--tier` the user gave).
