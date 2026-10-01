---
name: dev-flow
description: Use to drive a software feature or fix through the full engineering loop — investigate, design (with an architect-reviewer gate), get your explicit approval on the plan, then implement, verify with qa-engineer, and drive the code-review fix loop to a clean state. Deterministic multi-agent orchestration for the design-gate and review-gate loops this setup's engineering-loop rule already describes, so you don't have to hand-drive each Agent call yourself. Software-development-lifecycle scoped (not a generic router) — for legal or marketing work, use the relevant subagent directly.
user-invocable: true
argument-hint: "[what to build or fix]"
---

# dev-flow — deterministic SDLC orchestration

Drives a work item through the full loop this setup's `rules/engineering-loop.md`
already describes by hand: investigate → design ⇄ `architect-reviewer` (converges or
caps) → **you approve the plan** → implement → `qa-engineer` verifies → code-review
⇄ fix (converges or caps) → `qa-engineer` re-verifies. The design-gate and
review-gate loops run as deterministic `Workflow` scripts (real loop-until-approved
control flow, not the model remembering to keep looping); the one thing that stays a
plain conversational step is your approval of the plan — nothing skips that gate.

## 1. Gather the request

Take the work request as given. Don't ask for more detail than you need to resolve
the fields below — if it's already clear from the request, resolve it silently.

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

`true` if the request's scope is still fuzzy enough that `product-owner`
should frame the problem before any design work starts; `false` if it's already a clear,
bounded requirement. This is a judgment call you make yourself — don't ask the user
"should I investigate first," just decide from how well-specified the request is.

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
- Otherwise, `<today's-date>-<short-kebab-name>`.
- Validate against `/^[A-Za-z0-9][A-Za-z0-9._-]*$/` — this becomes a directory name
  and flows into every file path both workflow scripts write; don't let anything
  unvalidated near it.

## 6. Check `Workflow` availability, then run `Workflow A`

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

If it is callable:

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/dev-flow-design.js",
  args: { slug, track, needsUX, investigate, repo, secondaryRepo, request },
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

## 7. When `Workflow A` returns — update the index, then stop for approval

1. Update the `docs/work/README.md` index row for this work item yourself — this is
   always the skill's job, never a spawned agent's (multiple agents can write into
   the same work-item folder, sometimes concurrently; a shared index file being
   appended to by more than one writer is a real race, so there's exactly one owner).
2. Show the plan to the user. **If `designApproved` came back `false`**, say so
   prominently and first — "the design did not converge after N rounds; this is a
   capped-out draft, not an approved design" — don't present a capped-out result the
   same way you'd present a converged one.
3. **Stop here and wait for explicit human approval.** This is the one hard-coded
   gate the whole point of this exists to preserve — do not infer approval from
   silence, do not proceed on your own judgment that the plan looks fine. Ask
   plainly if it isn't already clear whether they've approved.

## 8. Only after explicit approval — run `Workflow B`

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/dev-flow-implement.js",
  args: { slug, track, repo, secondaryRepo },
})
```

Same async handling as step 6 — continue normally, the notification arrives when
it's done.

## 9. When `Workflow B` returns — report, don't commit

Report the final pass/fail and findings plainly — including if the review loop
capped out without reaching clean, and what the post-fix QA re-verification actually
found (it always runs, even on a non-converged review loop, so the report reflects
real final state either way). **You do not run `git commit`** — that stays the
user's call, unchanged from every other agent/skill in this setup. State that
explicitly so it's not ambiguous.

## Fallback — no `Workflow` tool

If `Workflow` isn't callable, drive the identical procedure yourself via direct,
sequential `Agent` calls in this conversation, following the same phase order and
loop logic both scripts encode (design ⇄ `architect-reviewer` until approved or
capped at 3 rounds; implement; `qa-engineer` verify; code-review ⇄ fix until clean or
capped at 2 rounds; `qa-engineer` re-verify) — same human-approval gate before
implementation starts, same "you don't commit" rule at the end. This is slower and
more manual than the scripted version, but the procedure and its gates don't change.
