# addit-harness

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-orange)
![Go](https://img.shields.io/badge/Go-00ADD8?logo=go&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?logo=openjdk&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)

A coding agent's out-of-the-box config is a blank slate. **addit-harness** is the config harness that turns it into a **full digital product development kit** — covering every layer from idea to ship: legal compliance, UX design, architecture, implementation in Go · Java · TypeScript, and code review, all wired into a plan→verify→commit engineering loop. One plugin install for Claude Code. Philosophy: curate established assets and adapt them — don't hand-roll what already exists.

---

A shared configuration that covers the full digital product development loop —
from idea investigation and legal compliance through UX design,
backend/frontend architecture, and implementation in Go · Java/Spring ·
TypeScript (Bun backend · React/Next.js frontend), to code review and
debugging — shipped as a [Claude Code](https://code.claude.com) plugin.
Built for **SaaS founders and product engineers** who own the full feature
lifecycle and want every layer of that loop to have an opinionated, specialized
subagent behind it.

**Philosophy:** adopt established, well-known assets (the official plugin
marketplace + reputable community collections) and adapt/pin them — don't
hand-roll what already exists. The repo is a thin **curation + config layer**, not
a pile of bespoke skills. It deliberately reuses Claude Code's built-ins
(`/code-review`, `/simplify`, `/verify`, `/run`, `/init`, `deep-research`).

## Documentation

The condensed, browsable version of this README lives at
**[tools.addit.digital/harness/docs/](https://tools.addit.digital/harness/docs/getting-started/)**
— grouped sidebar, on-page tables of contents, and a step-by-step install page.
Prefer browsing in-repo instead? Start at
[`site/_docs/README.md`](site/_docs/README.md).

## Contents

- [What's new](#whats-new)
- [Why this config?](#why-this-config)
- [Install](#install)
  - [Claude Code](#claude-code)
  - [Migrating from `install.sh`](#migrating-from-installsh)
- [What's in here](#whats-in-here)
  - [Language conventions — two tiers + per-project layer](#language-conventions--two-tiers--per-project-layer)
- [The engineering loop and the doc protocol](#the-engineering-loop-and-the-doc-protocol)
- [How dev-flow works](#how-dev-flow-works)
- [Using it](#using-it)
  - [Iterating & giving feedback on plans or code](#iterating--giving-feedback-on-plans-or-code)
  - [Official plugins (declared in `settings.json`)](#official-plugins-declared-in-settingsjson)
  - [Subagents](#subagents)
- [Use cases](#use-cases)
- [Model & cost](#model--cost)
- [Local telemetry (off by default)](#local-telemetry-off-by-default)
- [Enabling MCP (later)](#enabling-mcp-later)
- [Roadmap](#roadmap)
- [Extending](#extending)
- [Releasing the Claude Code plugin](#releasing-the-claude-code-plugin)

## What's new

Not yet released; the full list is the `Unreleased` section of
[`CHANGELOG.md`](CHANGELOG.md), summarized on the
[What's new](https://tools.addit.digital/harness/docs/whats-new/) page.

- **Breaking:** `install.sh` is gone (Claude Code only, see
  [Migrating from `install.sh`](#migrating-from-installsh)), and
  `@addit-harness:feature-investigator` is now `@addit-harness:product-owner`.
- `/dev-flow` triages each request into `light`, `standard` or `deep`, runs an
  intake brief, enforces plan approval with a hook, and runs QA once.
- Architects follow a solution method (at least 3 candidates, prior art,
  pre-mortem); every agent has an explicit `tools:` list.
- Frontend contract FC-1..FC-10; Go and Java conventions as cited topic files.
- One doc protocol for plans, designs and reports; setup merges `settings.json`.
- Optional local telemetry, off by default, with an offline export.
- `/dev-flow` progress in `/workflows`: tier, review rounds, blocking counts, gate
  verdicts and halt reasons, plus a six-step lifecycle task list (setup now turns
  the task tools on with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`).
- First run: a one-time welcome line, `/addit-harness:tips`, and a next-steps line
  at the end of setup.

## Why this config?

**Without it:** Claude Code starts as a blank slate — no engineering loop, no conventions, no subagents. You either wing it session to session or spend hours wiring up memory, rules, and delegation yourself, then rebuild it on every machine.

**With it:** one command gives you a reproducible, opinionated starting point:

| | Blank slate | This config |
|---|---|---|
| Engineering process | Ad-hoc | plan→verify→commit loop baked in |
| Legal compliance | Manual check (or skipped) before shipping | `@saas-legal-advisor` assesses impact of every feature change; drafts/reviews T&C, Privacy Policy, cookie policies, DPAs |
| Language conventions | Manual context injection every session | Auto-load per file type (Go · Java · TS) |
| Code review | Ask Claude to review | `@code-reviewer` enforces the conventions with file:line citations |
| Complex work | Monolithic context | Delegate to specialized subagents; main context stays clean |
| UX & design | Describe and hope | `@ux-designer` → `@figma-designer` → `@frontend-architect` pipeline |
| Feature build | Hand-drive every `Agent` call yourself, every time | `/dev-flow` — deterministic design-gate + review-gate loops, one human approval gate |
| e2e/regression QA | Manual click-through before every release | `@qa-engineer` — evidence-backed verification, web + mobile |
| New machine | Redo everything | plugin install + `/addit-harness:setup` |

## Install

### Claude Code

No clone, no shell script — install the plugin from inside Claude Code:

```
/plugin marketplace add addit-digital/addit-harness
/plugin install addit-harness@addit
/addit-harness:setup
```

- The plugin (`agents/`, `skills/`) tracks this repo via git automatically —
  no re-run needed to pick up updates.
- `/addit-harness:setup` places the parts a plugin can't carry natively
  (`CLAUDE.md`, `AGENTS.md`, `rules/`, `references/`, `settings.json`) — run
  it once after installing, and again after an update to re-sync. Add
  `--scope project` to confine it to the current project instead of
  `~/.claude` (default), or `--link` to symlink instead of copy.
- The plugin itself can also be scoped: `/plugin install
  addit-harness@addit --scope local` keeps it to just the current repo;
  `--scope project` shares it with collaborators via that repo's
  `.claude/settings.json`; default `--scope user` is global.
- Plugin-provided agents are namespaced — invoke them as
  `@addit-harness:code-reviewer`, not bare `@code-reviewer`.
- Add `--plugins` to also install the official plugins declared in
  `settings.json` now (`/addit-harness:setup --plugins`). Setup merges
  `settings.json` into yours instead of replacing it: your hooks,
  `statusLine`, `env` and plugin choices survive, your `permissions` rules are
  unioned with the template's, `env` is merged key by key with your values
  winning, `model` is set to the template's `opusplan`, and a backup of the
  previous file goes to `~/.claude/.install-backups/<timestamp>/`.
- The template's `env` sets `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` (unless you set
  that variable yourself) because Claude Code's task tools are off by default on
  newer models; `/dev-flow` uses them for its lifecycle task list. The per-turn
  context this adds has not been measured.
- The first interactive terminal session after install shows a one-line welcome, once
  (not the desktop app or IDE integrations; an empty marker,
  `onboarding/welcome-v1`, in the plugin data folder keeps it from repeating). It is a hook message for you, not model context. Setup ends
  with a next-steps line, and `/addit-harness:tips` prints five short tips.

### Migrating from `install.sh`

`install.sh`, `sync_tools.py` and `tools.config.json` are gone: addit-harness
supports Claude Code only, as a plugin. If you used `./install.sh`:

```
/plugin marketplace add addit-digital/addit-harness
/plugin install addit-harness@addit
/addit-harness:setup [--plugins]
```

Setup retires the old unprefixed `~/.claude/agents` and `~/.claude/skills`
copies (backed up first). Config already synced into Cursor, Kiro or Codex CLI
keeps working but is frozen; to keep updating it, pin commit `ebea6f3` or tag
`addit-harness--v0.3.0`, the last state that shipped `install.sh`.

## What's in here

| Path | What | How it's sourced |
|------|------|------------------|
| `AGENTS.md` | Canonical global memory: operating model + hard rules, imported by `CLAUDE.md` | Authored; follows [Anthropic memory](https://code.claude.com/docs/en/memory) & [best-practices](https://www.anthropic.com/engineering/claude-code-best-practices) |
| `CLAUDE.md` | 2-line `@import` pointer (`@AGENTS.md`, `@rules/engineering-loop.md`) — Claude Code specifically requires this literal filename | Authored |
| `.claude-plugin/plugin.json` + `marketplace.json` | Self-hosted Claude Code plugin (`addit-harness@addit`) — `agents/` and `skills/` auto-discovered from here | Authored |
| `rules/engineering-loop.md` | Always-on plan→verify→commit model + anti-patterns; sets diagram-rich (mermaid) plan/design-doc standards | Authored |
| `rules/{java,go,typescript,typescript-frontend}.md` | **Auto-loaded per file type** (Tier 1): the Go and Java contracts (G-1..G-10, J-1..J-14) and topic index, TS routing, and the Frontend Implementation Contract (FC-1..FC-10) | Authored |
| `references/{go,java,typescript}/` | **Convention guides + linked authorities, read on-demand** (Tier 2) | Go and Java: topic files with rule ids and cited sources; TS: vendored from recognized sources. See each `README.md` |
| `references/doc-protocol.md`, `references/solution-method.md` | How plans, designs, briefs and reports are written; the design method every architect follows | Authored |
| `agents/*.md` | Subagents: code-reviewer, debugger, architect-reviewer, backend-architect, frontend-architect, ux-designer, figma-designer, product-owner, backend-developer, frontend-developer, saas-legal-advisor, cloud-architect, devops-engineer, qa-engineer, task-triager | **Vendored + pinned** (except `backend-architect`/`frontend-architect`/`ux-designer`/`figma-designer`/`backend-developer`/`frontend-developer`/`saas-legal-advisor`/`qa-engineer`/`task-triager`, authored) — see `AGENTS_SOURCES.md` |
| `AGENTS_SOURCES.md` | Provenance table for vendored agents (source repo, commit SHA, changes) — kept at repo root, not inside `agents/`, since the Claude Code plugin auto-discovers every `.md` file in `agents/` as an agent | Authored |
| `skills/adr/` | `/adr` — record Architecture Decision Records (**MADR 4.0**) | Adopts MADR (see `skills/SOURCES.md`) |
| `skills/save-plan/` | `/save-plan` — persist an **implementation plan** to `docs/work/<slug>/plans/` (or `--temp`) so mermaid renders in an IDE/GitHub. Architecture designs → `docs/work/<slug>/solutions/`; review reports → `docs/work/<slug>/architecture-reports/` (written directly by the relevant agent) | Authored |
| `skills/go-conventions/` | `/go-conventions [--refresh]` — scan a Go repo and write `.claude/go-conventions.md` (project-specific layer on top of the global baseline) | Authored |
| `skills/design-conventions/` | `/design-conventions [--refresh]` — scan a TS/React project's existing UI layer and write `.claude/design-conventions.md` (visual design language: tokens, type/spacing/color scales, component lib, layout rhythm, state patterns). For greenfield projects, `@frontend-architect` generates this file instead. | Authored |
| `skills/setup/` | `/addit-harness:setup [--scope global\|project] [--link] [--plugins]` — places `CLAUDE.md`/`AGENTS.md`/`rules/`/`references/`/`settings.json` for Claude Code (the parts the plugin can't carry natively) | Authored |
| `skills/tips/` + `commands/tips.md` | `/addit-harness:tips` — user-invoked only: prints five short tips (when to use `/dev-flow`, plan approval, where documents land, calling the specialist agents, the local telemetry option) | Authored |
| `skills/telemetry-export/` + `commands/telemetry-export.md` | `/addit-harness:telemetry-export [--days N]` — user-invoked only: builds `data.json` and an offline `report.html` (no network, no external assets) from the local telemetry log under `export/<timestamp>/` in the plugin data folder. Only if you answer yes when asked, it publishes aggregated KPIs (no per-session rows, ids or hashes) as a private Artifact on claude.ai, which uploads them to Anthropic's hosted service under your account | Authored |
| `skills/dev-flow/` + `workflows/*.js` | `/dev-flow [what to build or fix] [--tier light|standard|deep]` — deterministic SDLC orchestration: triage (facts by `task-triager`, tier scored in JS) → tier gate → investigate → design ⇄ `architect-reviewer` loop → **your approval gate** → implement → review ⇄ fix loop → `qa-engineer` verifies once (re-verifies only after a QA-driven fix). The loops run as `Workflow` scripts (`workflows/dev-flow-triage.js`, `workflows/dev-flow-design.js`, `workflows/dev-flow-implement.js`), each tier-parameterised; the skill holds the one human gate a script can't pause for. See [How dev-flow works](#how-dev-flow-works) for the phase-by-phase mechanics and loop-termination logic. Relies on `${CLAUDE_PLUGIN_ROOT}` and the `Workflow` tool | Authored |
| `hooks/` | `SessionStart` hook — reminds the user to re-run `/addit-harness:setup` once the plugin's version has drifted past what was last synced (tracked via a version marker `setup.sh` writes per scope), and on the first interactive terminal startup after install shows a one-time welcome line (a `systemMessage`, not model context; an empty marker `onboarding/welcome-v1` in the plugin data folder keeps it to once); `PreToolUse` hook on `Workflow` — blocks `dev-flow-implement` unless the approved plan's marker and hash check out (all other workflows untouched); `PostToolUse` advisory frontend check (non-blank line count on UI .ts/.tsx; ADDIT_FE_GATE=eslint opts into your project's ESLint, =0 disables; set in shell or settings.json "env"); an optional local telemetry hook (`hooks/telemetry.sh`/`telemetry.py`) that runs its script only when you turn on `telemetry_local` (see [Local telemetry](#local-telemetry-off-by-default)). None of the four makes a network request | Authored |
| `settings.json` | Default model + permissions + official plugins (`enabledPlugins`) + `env` (`CLAUDE_CODE_ENABLE_TODO_TOOLS=1`, turns the task tools on) — placed by `/addit-harness:setup` | Authored |
| `mcp.example.json` | Disabled Atlassian/DB scaffolding (opt-in) | Reference config |
| `templates/CLAUDE.project.md` | Per-repo memory template | Authored |
| `tests/workflows/`, `tests/telemetry/`, `tests/setup/`, `tests/onboarding/` | Mock runner + scenarios for the dev-flow workflow scripts, each run also checked against the progress-line contract (`log-contract.mjs`); stdlib unit tests for the telemetry writer and exporter, the `settings.json` merge, and the first-run welcome hook | Authored |
| `CHANGELOG.md` | User-facing changes; each release's section becomes its GitHub release notes | Authored |

Three ways assets are delivered:
- **Adopted (declarative):** official plugins enabled via `settings.json` — track
  their marketplace, safe to auto-update.
- **Vendored (pinned):** some subagents *and* the TypeScript convention guides,
  copied in at a fixed commit for reproducibility (provenance + license in
  `AGENTS_SOURCES.md`, `skills/SOURCES.md`, and each `references/*/README.md`).
- **Authored:** `CLAUDE.md`, `rules/engineering-loop.md`, the doc protocol and
  solution method, the Tier-1 rules, and the Go and Java topic files (each rule
  cites its source).

### Language conventions — two tiers + per-project layer

- **Tier 1 — `rules/*.md`** carry `paths:` frontmatter and auto-load when you
  touch that language: a short contract with rule ids (Go G-1..G-10, Java
  J-1..J-14, frontend FC-1..FC-10) plus an index of topic files.
- **Tier 2 — `references/{go,java,typescript}/`** hold the topic files + a
  `README.md`. Not path-scoped; Claude reads the one or two topics that match the edit.
- **Per-project — `.claude/go-conventions.md`** in any Go repo. Run
  `/go-conventions` to generate it; `rules/go.md` loads it automatically. It may
  override a topic rule with `# OVERRIDE: G-<TOPIC>-n <reason>`, never G-1..G-8 or
  G-10. Java has no per-project file: a project Checkstyle/PMD config sets J-12's
  numbers and a project formatter replaces the formatting rules.
- **Per-project — `.claude/design-conventions.md`** in any TS/React project. Run
  `/design-conventions` on an existing project to derive it; for greenfield,
  `@frontend-architect` generates it. `rules/typescript.md` instructs loading it
  first for any UI work.

| Stack | In-repo reference | Linked authorities |
|-------|-------------------|--------------------|
| Go | `rules/go.md` contract (G-1..G-10) + 11 topic files in `references/go/` + per-project `.claude/go-conventions.md` | Effective Go, Go Code Review Comments, Google Go Style |
| Java/Spring | `rules/java.md` contract (J-1..J-14) + 12 cited topic files in `references/java/` | Effective Java, Google Java Style, Spring docs |
| TS / React / Next / RN | `rules/typescript-frontend.md` contract (FC-1..FC-10) + bulletproof-react docs (MIT) + sanjeed5 TS/React/Next/RN `.mdc` (CC0) | react.dev, Next.js docs, TypeScript Handbook, Total TypeScript |

The Go topics follow the owner's own approach and use the Uber guide where it
does not collide. The frontend contract caps file and component size, nesting,
props, complexity and hooks, and sets layering, feature boundaries and token
use; a project's ESLint config or `CLAUDE.md` may tighten a limit, never loosen
it. An advisory `PostToolUse` hook flags frontend files over 150 or 250
non-blank lines after each edit (`ADDIT_FE_GATE=eslint` adds your project's
ESLint, `=0` turns it off). The **`code-reviewer` subagent checks adherence** to
whichever conventions apply, citing rule ids and measured values.

## The engineering loop and the doc protocol

`rules/engineering-loop.md` is always on: frame intent → curate context → plan →
implement in small units → verify with tooling → commit → hand off. Every
document the loop produces goes to one folder per work item, and plugin
locations win over a project's own plans/ADR/legal folders:

```mermaid
flowchart TD
    W["docs/work/{slug}/"] --> SP["specs/ brief.md"]
    W --> SO["solutions/ solution-{track}.md"]
    W --> PL["plans/ plan.md"]
    W --> AR["architecture-reports/ report.md, report-r2.md"]
    W --> QA["qa-reports/ report.md"]
    W --> LG["legal/ assessment.md"]
```

The slug is `<YYYY-MM-DD>-<short-name>` or `<ticket-id>-<short-name>`; an existing
folder from another work item gets a `-2` suffix, never an overwrite. Standing
docs (`docs/adr/`, `docs/legal/`, the indexes) are edited in place.
`references/doc-protocol.md` gives each document type a template, a length
ceiling per tier (a `standard` plan at most 120 lines, a `deep` solution at most
350), Observed/Inferred/Unknown labels on claims, edit-in-place revisions with a
log of at most 5 lines, and one mermaid diagram per concept.
`references/solution-method.md` makes every architect compare at least three
structurally different candidates (one unconventional) with prior art and a
pre-mortem, scoring your own proposal only at the comparison step. Full
detail: [The engineering loop](https://tools.addit.digital/harness/docs/engineering-loop/).

## How dev-flow works

`/dev-flow` automates the design-gate and review-gate rounds of the
engineering loop above as real control flow — not the model remembering to
keep looping correctly on its own. It's a hybrid, not a single mechanism: a
skill alone can't guarantee it keeps looping right, and the `Workflow` tool
alone can't pause mid-run to ask you anything, which conflicts with this
repo's own hard rule that non-trivial work needs your explicit plan approval
before implementation starts. So the design splits along that seam:

- **`skills/dev-flow/SKILL.md`** (thin) — resolves the request, holds the one
  human approval gate, and is the only place that talks to you.
- **`workflows/dev-flow-triage.js`**, **`workflows/dev-flow-design.js`** and
  **`workflows/dev-flow-implement.js`**
  — real JavaScript run by the `Workflow` tool, no human interaction inside.

```mermaid
flowchart TD
    A[New request] --> S1["skills/dev-flow: resolve track, needsUX, repo(s)"]
    S1 --> W0["Workflow 0: dev-flow-triage.js\n(one read-only agent, tier scored in JS)"]
    W0 --> TG{{"Tier gate: ok / deeper / lighter"}}
    TG --> WA["Workflow A: dev-flow-design.js (tier)"]
    WA --> G{{"Human approves the plan\n(the one gate a script can't hold)"}}
    G --> WB["Workflow B: dev-flow-implement.js (tier)"]
    WB -. "scope breach at light" .-> TG
    WB --> C[Human commits]
```

**Tiers.** Before any design work, `dev-flow-triage.js` asks `@task-triager` (read-only,
facts only, never a verdict) which files the change touches and which risk surfaces it
hits; a deterministic score plus raise-only safety floors turns that into `light`,
`standard` or `deep`, and you can say `deeper` / `lighter` at the tier gate or pass
`--tier`. Both workflows take the tier:

| | `light` | `standard` | `deep` |
|---|---|---|---|
| Investigate | never | only if triage confidence is low | always |
| UX loop | never (UX pass skipped) | if `needsUX`, up to 3 rounds | if `needsUX`, up to 3 rounds |
| Design | one pass writes a change brief to `plan.md`, one review, no loop | loop, up to 3 rounds | loop, up to 3 rounds |
| Separate Plan phase | folded into the brief | yes, plus a review | yes, plus a review |
| Review floor (what blocks) | `blocking` only | `blocking` + `major` | everything |
| Reviewers per pass | `code-reviewer` only | `code-reviewer` + `pr-review-toolkit` | same |
| Architect / reviewer effort | medium / low | high / medium | high / high |
| Post-QA fix re-review | none (disclosed in the report) | one scoped `code-reviewer` call | same |
| Scope-breach escalation | halts and re-gates at `standard` | logged only | logged only |

Worst-case agent calls per tier:

| Tier | Design A (`both`, +UX) | Implement B (`both`) | Whole run incl. triage | One track, +UX |
|---|---|---|---|---|
| `light` | 4 (no UX) | 13 | 18 | 12 (no UX) |
| `standard` | 23 | 22 | 46 | 38 |
| `deep` | 27 | 22 | 50 | 42 |

The worst-case figures are hard caps, and the mock suite (`tests/workflows/`) asserts that
adversarial runs (reviewers never clean, design never approved, QA always failing) hit each
cell exactly and never trip the call-ceiling backstop. They are mock-asserted, not measured
live, and exclude the skill's `@product-owner` intake calls; a typical run makes far fewer.
The `standard`/`deep` design caps include scoring your proposed approach (one call per
track) and, at `deep`, three parallel explorers plus one candidate switch.

**Intake.** At `standard` and `deep`, `@product-owner` first asks only the questions that
change the approach (one batch of at most four, the tier gate included; `deep` may ask one
more batch), then writes a one-page brief to `docs/work/<slug>/specs/brief.md`. A solution
proposed in your request is moved to `specs/owner-proposal.md`; the architects see it only
as candidate "Owner" at the comparison step.

**Workflow A — investigate, design, plan.** Investigate runs per tier (always at
deep, at standard only if triage was unsure; `@product-owner` frames the problem
first); UX only runs if the work needs a fresh pass (`@ux-designer` ⇄
`@figma-designer` ⇄ fidelity-check, looping until approved); Design runs one
architect per track (`@backend-architect` and/or `@frontend-architect`, in
parallel when the work spans both) ⇄ `@architect-reviewer`, feeding each
round's findings into the next round's prompt so a retry is a refinement, not
a blind re-roll; Plan writes the implementation plan and gets one more
`@architect-reviewer` pass. `Workflow A` returns whether the design loop
actually converged — if it capped out instead, the skill says so plainly when
it shows you the plan, rather than presenting a capped-out draft the same way
it'd present an approved one.

**The human gate.** `Workflow A` runs to completion and returns; the skill
shows you the plan and waits for an ordinary conversational approval — this
isn't a pause *inside* a `Workflow` run, since there's no such thing.
`Workflow B` is a separate call, made only after you approve. The state that
survives between them is just the plan file already written to
`docs/work/<slug>/plans/plan.md` — approving days later, even in a new
session, is "read that file, call `Workflow B`." No special resume mechanism.
After you approve, the skill appends an approval marker to `plan.md`, invokes
`/addit-harness:adr` for each decision the plan lists under `## ADR candidates`,
and hashes the file; a `PreToolUse` hook (`hooks/gate-dev-flow-implement.sh`)
refuses to start `Workflow B` unless the plan exists, carries the marker, and
matches that hash. The gate stops accidents (a direct
`/addit-harness:dev-flow-implement`, a stale slug, a plan edited after approval);
it does not stop a model that ignores its instructions and writes the marker
itself — your approval in the conversation remains the real gate.

**Workflow B — implement, review, verify once.**

```mermaid
flowchart LR
    IM["Implement\nbackend/frontend-developer\n(sequential if same repo, else parallel)"] --> RV["Review\ncode-reviewer (+ pr-review-toolkit at standard/deep)"]
    RV --> FX["Fix loop\nseverity-filtered, until clean or capped"]
    FX --> QA["QA once\n@qa-engineer, evidence-backed"]
    QA -- "failed" --> QF["One fix cycle\n(+ scoped re-review at standard/deep)"] --> QR["QA re-verify\nthe 2nd and last run"]
```

Two tracks in the *same* repo implement sequentially, never in parallel, to
avoid concurrent writes to one branch; genuinely separate repos run in
parallel. `@code-reviewer` (always present) plus, at standard/deep and when
installed, the `pr-review-toolkit` bundle review; every finding is tagged
`blocking`, `major` or `minor` and the script (not the reviewer) applies the
tier's floor to decide the verdict; findings route to the track they're tagged
for; the fix loop repeats until clean or capped, then a final verdict-only
`@code-reviewer` pass judges the code as it stands after the last fix.
`@qa-engineer` then verifies **once**, with an evidence-backed report (a real
exit code, screenshot, or log — never a bare "looks good"); QA runs even if the
review loop never reached clean, so the report reflects real final state. A QA
failure is blocking at every tier: it gets one fix cycle (a scoped
`@code-reviewer` pass over that fix at standard/deep, none at light, said so in the
report) and one re-verification, never a third run. At `light`, the first review
also checks the touched files against the plan; a change that lands on a risk
surface or crosses a file-count band halts the run for a re-gate at `standard`.
You still run `git commit` yourself.

**How the loops know when to stop.** Every loop combines four signals:
convergence (the real success condition), a hard round cap (a backstop so
nothing runs forever), a token-budget guard, and a non-progress circuit
breaker (aborts immediately if a round's findings exactly match the previous
round's). The two caps are deliberately different, not copy-pasted: the
design-gate loop caps at **3 rounds**, the review-gate fix loop at **2**. At a
cap of 2, the circuit breaker can only ever compare on the very last allowed
round, making it structurally unable to save any work — 3 is the minimum
depth where "stop early" and "hit the cap anyway" are actually different
outcomes.

**Watching a run.** While a workflow runs, `/workflows` shows fixed-format
progress lines: `dev-flow <workflow> start: tier=… track=…`,
`<Loop> r<n>/<cap>: <k> at/above <floor>` per review round (`<k>` counts findings
at or above the tier's floor), `gate <name>: <verdict>`, and
`HALT <haltedBy>: <reason>` (fixed text or counts). No request text, agent output,
error messages or file paths are logged;
`tests/workflows/log-contract.mjs` checks this on every mock scenario. With the
task tools on, dev-flow also keeps six tasks (`Triage`, `Design + plan`,
`Approve plan`, `Implement + review`, `QA`, `Commit`) current at each step;
`Commit` stays pending because committing is yours. Unproven in a live terminal:
that the model issues every task update, the task tools' per-turn context cost,
and whether the task panel's one-line summary shows the latest log line. Details:
[Watching a run](https://tools.addit.digital/harness/docs/dev-flow/#watching-a-run).

**If the `Workflow` tool isn't available**, the skill checks whether it's
actually callable before using it, rather than assuming from configuration —
if it isn't, `skills/dev-flow/SKILL.md` documents a full manual fallback: the
identical phase order and loop logic, driven by direct sequential `@agent`
calls instead of a script. Slower, same gates, same outcome.

## Using it

### Iterating & giving feedback on plans or code

The "no way to say change this" problem is mostly a **terminal UI gap**:

| Scenario | What to do |
|----------|-----------|
| **Revising a plan** | Choose **"Keep planning with feedback"** when Claude presents a plan. Type your correction and Claude stays in plan mode. `Ctrl+G` opens the plan file in your editor to edit directly. |
| **Inline comments on code (web)** | Open the diff view → click any line → leave a comment. Comments queue and bundle with your next message — this is the easiest "change *this* line" path. |
| **Giving feedback in the terminal** | There's no line-selection UI. Reference the code as `pkg/sales/service.go:45` in your message, or paste the relevant lines. Press `Esc` to interrupt Claude mid-run and redirect. |
| **Browser plan review** | Run `/ultraplan <task>` → open the browser link → leave inline comments on specific sections → iterate before executing. |

### Official plugins (declared in `settings.json`)
Enabled from the auto-available `claude-plugins-official` marketplace (+
`anthropics/skills`). The big win is real **language servers**:
`gopls-lsp`, `jdtls-lsp`, `typescript-lsp`, plus `pr-review-toolkit`,
`commit-commands`, `security-guidance`, and `document-skills` (doc generation).
Run `/addit-harness:setup --plugins` to install them now.

### Subagents
Delegate isolated work to keep your main context clean:
`@code-reviewer` (also checks convention adherence), `@debugger`,
`@architect-reviewer`, `@backend-architect` (up-front API/service design only),
`@frontend-architect` (up-front component/rendering/state design only),
`@ux-designer` (user flows, journey maps, IA, wireframes, interaction specs, and
usability audits — reads the project's design system, bridges UX to UI patterns,
defers component/token/a11y architecture to `@frontend-architect`),
`@figma-designer` (materializes UX specs into Figma frames, components, auto-
layout, variables, and tokens via the official Figma MCP — composes downstream of
`@ux-designer`; requires `figma@claude-plugins-official` plugin),
`@product-owner` (frame a feature/product request as a problem statement before
design — never a solution), `@saas-legal-advisor` (SaaS-specialized legal advisor — assesses
legal impact of product changes, drafts and reviews privacy policies, T&C, cookie
policies, DPAs, and other compliance docs; reads the project's declared primary
jurisdiction from `CLAUDE.md`; use proactively whenever a feature touches user
data, payments, third-party integrations, or account types), `@cloud-architect`
(multi-cloud/Kubernetes infrastructure design **and** audits of existing
infrastructure — AWS/Azure/GCP/OCI/DigitalOcean, IaC strategy, cost, security,
DR; defers implementation to `@devops-engineer`), and the implementation
agents `@backend-developer` (Go · Java/Spring · TypeScript/Bun),
`@frontend-developer` (TS/React/Next/RN) — senior craftsmen that design clean
structures, write tests, and verify code against the conventions — and
`@devops-engineer` (writes and verifies the actual Terraform/Kubernetes
manifests/Dockerfiles/CI pipelines against a `@cloud-architect` design, plus
hands-on Linux systems administration — systemd, networking, SSH, logs — on
the VMs/nodes underneath; prefers the cloud/infra MCP servers in
`mcp.example.json` when connected, falls back to the provider CLI otherwise),
and `@qa-engineer` (verifies an implemented feature via e2e/regression testing —
writes scenarios, implements them as executable tests, runs them, reports with
mandatory evidence per claim; not unit/integration tests, which stay with the
developer agents; web verification requires `claude-in-chrome` connected).

## Use cases

Concrete workflows showing which configs fire together.

**Build a new feature**

`/dev-flow` automates this exact walkthrough end-to-end — investigate → design ⇄
`@architect-reviewer` loop → your approval gate → implement →
`@code-reviewer` ⇄ fix loop → `@qa-engineer` verifies — as deterministic `Workflow`
scripts instead of hand-driving each step below yourself. The steps below still
apply if you'd rather drive them by hand, or when the request doesn't fit the
software-development-lifecycle shape `/dev-flow` is scoped to (e.g. legal-only or
infra-only work). See [How dev-flow works](#how-dev-flow-works)
for the phase-by-phase mechanics and how the design/review loops know when to stop.

```mermaid
flowchart LR
  FI["@product-owner\nproblem statement"]
  LA["@saas-legal-advisor *(if data/payments/integrations)*\nlegal impact → doc updates"]
  UX["@ux-designer\nflows · wireframes · IA"]
  FG["@figma-designer *(optional)*\nFigma frames + tokens"]
  FA["@frontend-architect\ncomponent architecture"]
  SP["/save-plan → docs/work/<slug>/plans/\nTaskCreate tracked steps"]
  BD["@backend-developer"]
  FE["@frontend-developer"]
  QA["@qa-engineer\ne2e/regression verify"]
  CR["@code-reviewer\nconventions + security"]

  FI --> LA
  FI --> UX
  LA --> SP
  UX --> FG
  UX --> FA
  FG --> FA
  FA --> SP
  SP --> BD & FE
  BD --> QA
  FE --> QA
  QA --> CR
```

1. `@product-owner` → problem statement (never a solution) before any design.
2. `@saas-legal-advisor` *(if the feature touches user data, payments, third-party
   integrations, or account types)* → runs in parallel with UX design; produces an
   impact table (Critical/Important/Advisory) and drafts updated legal clauses.
   Saves the assessment to docs/work/<slug>/legal/assessment.md. Legal doc updates must ship before or with
   the feature — not after.
3. `@ux-designer` → user flows, journey map, IA, wireframes, state matrix, and
   interaction specs. Reads `.claude/design-conventions.md`; flags design system
   gaps for `@frontend-architect`. Saves spec to `docs/work/<slug>/solutions/`.
4. `@figma-designer` *(optional)* → materializes the UX spec into Figma frames,
   components, auto-layout, and tokens via the official Figma MCP. Requires the
   Figma plugin + MCP connected (see *Enabling MCP*).
5. `@frontend-architect` → component/rendering/state architecture informed by the
   UX spec; resolves any design system gaps flagged by `@ux-designer` or
   `@figma-designer`.
6. Plan it — a diagram-rich plan (mermaid), then `/save-plan` → `docs/work/<slug>/plans/`
   to view it rendered in an IDE/GitHub (the terminal can't render mermaid).
   TaskCreate a tracked task list from the plan's phased steps so status is
   visible; TaskUpdate each task as it completes.
7. Implement — `@backend-developer` and/or `@frontend-developer` write + verify
   the code; Tier-1 `rules/<lang>.md` auto-load per file type and they read the
   vendored `references/<lang>/` guides on demand.
8. `@qa-engineer` → verifies the implemented feature via e2e/regression testing,
   evidence-backed (not the unit/integration tests from step 7 — a separate,
   UI-level check that the feature actually works).
9. `@code-reviewer` → checks correctness, security, *and* adherence to the
   vendored conventions (file:line violations).

**Review or debug existing code**
- `@code-reviewer` on a diff — flags convention violations with file:line.
- `@debugger` for a failing test or stack trace — isolates root cause.

**Design or implement infrastructure**
- `@cloud-architect` for up-front design (new environment, migration, multi-cloud
  strategy) → design doc saved to `docs/work/<slug>/solutions/`.
- `@cloud-architect` to **audit existing infrastructure** (cost, security,
  reliability, IaC drift) → review report saved to `docs/work/<slug>/architecture-reports/`
  with Critical/Important/Advisory findings, same pattern as `@architect-reviewer`.
- `@devops-engineer` to implement the design or act on the review's findings —
  writes and verifies actual Terraform/Kubernetes manifests/Dockerfiles/CI config,
  plus edge security (Cloudflare WAF/DDoS/Zero Trust or the hyperscaler-native
  equivalent) and vulnerability/IaC/secrets scanning per the design.
- Both prefer the AWS/Azure/DigitalOcean/Terraform/Kubernetes/Docker/Cloudflare
  MCP servers in `mcp.example.json` when connected (see *Enabling MCP*), falling
  back to the provider CLI via Bash otherwise. Google Cloud has no unified official MCP
  server yet, so GCP work falls back to `gcloud` directly.

**Make an architecture decision**
- `@backend-architect` (API/service) or `@frontend-architect` (component/rendering/state)
  produce a design doc → saved to `docs/work/<slug>/solutions/solution-<track>.md`.
- `@architect-reviewer` evaluates an existing design → saved to
  `docs/work/<slug>/architecture-reports/report.md`.
- Record the decision with `/adr` (MADR) under `docs/adr/`.

**Assess legal impact before shipping a feature**
- Before a feature that touches user data, payments, or third-party services ships,
  invoke `@saas-legal-advisor` with the feature description or PR diff.
- It produces an impact table (Critical / Important / Advisory) mapping each change
  to the specific legal document and clause affected, then drafts the updated clause(s).
- Assessment → docs/work/<slug>/legal/assessment.md; standing docs updated in docs/legal/<document-kind>.md. Update the live documents before
  or alongside the feature — never after.

```
@saas-legal-advisor "We're adding Stripe Connect, storing payment method tokens,
and sending transactional emails via Resend — what needs to change in our legal docs?"
```

**Review or draft legal documents**
- Audit an existing doc for regulatory gaps, staleness, or cross-document inconsistencies:
  `@saas-legal-advisor "Audit our Privacy Policy against current GDPR requirements"`
- Draft a new document from scratch:
  `@saas-legal-advisor "Write a Data Processing Agreement for enterprise customers"`
- The agent reads the project's `CLAUDE.md` for the declared primary jurisdiction and
  applies that framework first. Add secondary jurisdictions (e.g. GDPR for EU users)
  in your request or in `CLAUDE.md`.

**New third-party integration**
- Any new SDK, API, or analytics tool is a legal event — it introduces a new data
  processor and may require cookie consent, privacy policy updates, or DPA amendments.
- Ask `@saas-legal-advisor` with the integration name before the code ships.

**Day-to-day coding in Go / Java / TS**
- Just open the file — language conventions auto-apply (Tier 1) and the reviewer
  enforces them; no command needed. Claude pulls deeper `references/` only for
  substantial work.

**Keep costs down**
- Default `opusplan` (Opus plans, Sonnet executes); `/model` to switch, `/effort
  low` for simple tasks, and delegate noisy work to subagents. See *Model & cost*.

**Review pull requests on GitHub (subscription-only, no API key)**

Two paths — both work on Pro/Max, no `ANTHROPIC_API_KEY` needed:

| Path | Setup | When to use |
|------|-------|-------------|
| **Local on-demand** | None — just be logged in | Quick reviews before a push, or when CI isn't set up |
| **Automated CI** | `claude setup-token` → add secret → copy workflow | Every PR auto-reviewed on open/push |

*Local (works right now):*
```
/code-review #<pr-number> --comment
```
Uses your `/login` subscription credentials. Posts inline comments on the PR diff via the GitHub MCP server. No secret or token needed.

*Automated CI:* see [`addit-digital/addit-actions`](https://github.com/addit-digital/addit-actions) — a reusable `workflow_call` workflow. Copy the caller into any app repo's `.github/workflows/`, add `CLAUDE_CODE_OAUTH_TOKEN` as a repo secret (`claude setup-token` → `gh secret set`), and Claude reviews every PR automatically.

> **Caveats:** CI runs consume your Pro/Max quota. The OAuth token (`setup-token`) lasts ~1 year.

**Connect Jira / a database**
- Enable the relevant server from `mcp.example.json`. See *Enabling MCP*.

**Set up a specific repo**
- Copy `templates/CLAUDE.project.md` → the repo's `./CLAUDE.md` for
  codebase-specific facts (keep them out of global memory).

## Model & cost

The goal is **good-enough model per task** to lower spend without hurting code
quality. Code quality is driven more by conventions + verification than by raw
model size, so a strong default plus tuned subagents goes a long way.

**Default model:** `settings.json` sets `"model": "opusplan"` — Opus while
planning, Sonnet while executing. You get Opus-grade design (where rework is
prevented) and Sonnet's strong, cheaper execution against your rules.
- Switch anytime with `/model` (pick + `Enter` to save as default, or `s` for
  session-only). Drop to `sonnet` for routine work; bump to `opus`/`fable` when a
  task is genuinely hard.

**Subagent routing** (`model:` in each `agents/*.md`):

| Subagent | Model | Why |
|----------|-------|-----|
| `architect-reviewer` | `opus` | High-value, infrequent design judgment |
| `backend-architect` | `opus` | Design decisions prevent downstream rework |
| `frontend-architect` | `opus` | Rendering/state/component design — same rationale as backend-architect |
| `ux-designer` | `opus` | UX flow/journey/usability design — design-tier, upstream of frontend-architect |
| `figma-designer` | `sonnet` | Figma execution — materializes specs into Figma via MCP; execution-tier like developer agents |
| `code-reviewer` | `opus` | A strong reviewer = less *manual* review for you |
| `backend-developer` | `sonnet` | Implementation/execution — fast + cheap against the conventions |
| `frontend-developer` | `sonnet` | Implementation/execution — fast + cheap against the conventions |
| `debugger` | `sonnet` | Iterative; escalate with `/model` if stuck |
| `product-owner` | `sonnet` | Problem-statement framing (authored) |
| `saas-legal-advisor` | `opus` | Legal reasoning + compliance assessment — high-stakes advisory; wrong guidance is costly |
| `cloud-architect` | `opus` | Infra design + review — mistakes are costly and often hard to reverse |
| `devops-engineer` | `sonnet` | Implementation/execution against a design — fast + cheap, same rationale as the other `*-developer` agents |
| `qa-engineer` | `sonnet` | e2e/regression verification execution — running and reporting against a given scenario, not designing one |
| `task-triager` | `haiku` | Fact-gathering for `/dev-flow` triage; read-only, never returns a verdict |

Every agent declares an explicit `tools:` list, so it does not load every MCP
server's tool schemas on its first turn. For the four architect and design
agents this cut first-turn context from about 33k to about 17k tokens in a
controlled probe; your saving depends on the MCP servers you have connected.

Other mechanical agents (test-runners, formatters) should use `haiku` too. Override
all subagents at once with `CLAUDE_CODE_SUBAGENT_MODEL`.

**Manual levers to cut tokens:**
- `/effort low|medium` for straightforward tasks (less thinking spend).
- `/clear` between unrelated tasks; `/context` to see what's using space;
  `/compact` near the limit.
- Delegate noisy work (test output, log scans, doc fetches) to a subagent — its
  output stays in *its* context, not yours.
- Prompt caching is automatic (CLAUDE.md/system prompt reused cheaply).
- Pin background model with `ANTHROPIC_DEFAULT_HAIKU_MODEL`
  (`ANTHROPIC_SMALL_FAST_MODEL` is deprecated).

**Rough trade-off** (verify current pricing): Haiku ≈ cheapest (mechanical work),
Sonnet ≈ daily-driver coding, Opus/Fable ≈ hardest reasoning at top cost.

## Local telemetry (off by default)

An optional hook keeps a metadata-only usage log on your own machine so you can
see which agents, skills and dev-flow steps you actually use. It is off unless
you turn on the `telemetry_local` option in `/config`; while it is off, the
plugin writes no telemetry. (The only file it creates regardless is an empty
one-time welcome marker, `onboarding/welcome-v1`, in the plugin data folder.)

- **Records:** which addit-harness components ran and how they ended, counts and
  sizes, gate verdicts, and pseudonymous salted hashes of your project folder
  path, document paths and dev-flow work-item names. The hashes are pseudonymous,
  not anonymous: whoever holds the log and its salt can test a guess against them.
- **Never records:** prompts, responses, code, file contents, your file names or
  paths, error text, or account details.
- **Stays local:** the plugin opens no network connection. Files are kept for 90
  days and deleted automatically; to delete them sooner, turn the option off and
  remove the folder. Uninstalling deletes it by default (unless `--keep-data`).

- **Summary page:** `/addit-harness:telemetry-export` (user-invoked only) writes
  `data.json` and an offline `report.html` next to the log, on your machine. Only if
  you answer yes when it asks does it publish aggregated numbers (no per-session
  rows, ids or hashes) as a private Artifact on claude.ai. That upload goes to
  Anthropic's hosted service under your account, through Claude Code's own
  Artifact tool; the plugin itself still opens no network connection. Without the
  Artifact tool, nothing is published and the local path is printed.

- **Cost when on:** roughly 41 ms median and 55 ms at the 90th percentile per hook
  event in local measurements. When off, a shell launcher exits before Python starts.

How it works: [Local telemetry](https://tools.addit.digital/harness/docs/telemetry/).
Details and the exact list: the [privacy policy](https://tools.addit.digital/harness/privacy/).

## Enabling MCP (later)

Both Atlassian and database MCP are intentionally **off** for now, and MCP is
never auto-enabled: `mcp.example.json` is a disabled, human-curated catalogue
(see its own `_README` entry) — pick an entry and fill in credentials by hand.
To enable:

1. Open `mcp.example.json` and copy the entry you want into
   `~/.claude/.mcp.json` (under an `mcpServers` object).
2. Put secrets/connection strings in `~/.claude/mcp.local.json` (gitignored) —
   never commit them.
3. Restart Claude Code; check with `/mcp`.

- **Figma (official plugin — recommended):** run `claude plugin install figma@claude-plugins-official` (or `/addit-harness:setup --plugins`, which installs it with the other declared plugins). Open any Figma file → authorise Claude Code in the plugin panel → OAuth completes → `/mcp` confirms the Figma server is connected. Write-to-canvas is in beta and will become usage-based/paid — confirm your plan covers cost before running `@figma-designer` for large tasks. See `mcp.example.json` → `figma_OFFICIAL` for the manual MCP-only path and `figma_COMMUNITY_ALTERNATIVE` for the free-plan plugin-bridge option.
- **Atlassian Cloud:** `claude mcp add --transport http atlassian https://mcp.atlassian.com/v1/mcp` (official Rovo server, OAuth).
- **Atlassian Data Center:** community `sooperset/mcp-atlassian` (token/PAT).
- **Postgres:** `crystaldba/postgres-mcp` (read-only by default).
- **MySQL:** `benborla/mcp-server-mysql` or `designcomputer/mysql_mcp_server`.
- **Cloud/infra (used by `@cloud-architect` / `@devops-engineer`):** official
  servers for AWS (`awslabs/mcp`), Azure (`@azure/mcp`), DigitalOcean
  (`digitalocean-labs/mcp-digitalocean`), Terraform (`hashicorp/terraform-mcp-server`,
  via Docker), Kubernetes (`kubernetes-mcp-server`), Docker (`docker mcp
  gateway`, built into Docker Desktop's MCP Toolkit), and Cloudflare
  (`cloudflare/mcp` — WAF, DDoS, Zero Trust, DNS, CDN; OAuth) — see
  `mcp.example.json`. Google Cloud has no unified official MCP server yet; both
  agents fall back to the `gcloud` CLI directly.

## Roadmap

See [open issues](https://github.com/addit-digital/addit-harness/issues?q=label%3Aroadmap) for planned work. Candidates:

- `/design-review` skill — audit a `docs/work/<slug>/solutions/` design doc against the project's conventions
- `@security-reviewer` subagent — dedicated security-focused review pass

Contributions welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md). Issues labeled [`good first issue`](https://github.com/addit-digital/addit-harness/issues?q=label%3A%22good+first+issue%22) are a good entry point.

## Extending

- **Add a language rule:** drop a lean `rules/<lang>.md` with `paths:` frontmatter
  (Tier 1) and, if it needs depth, a `references/<lang>.md` it points to (Tier 2).
- **Vendor another subagent:** copy the `.md` into `agents/`, add a row with its
  source + commit SHA to `AGENTS_SOURCES.md`.
- **Add a command/skill:** cherry-pick from
  [qdhenry/Claude-Command-Suite](https://github.com/qdhenry/Claude-Command-Suite)
  into `skills/`, record it in `skills/SOURCES.md`.
- **Update a pinned asset:** re-fetch at a newer commit, replace the file, bump
  the SHA in the relevant `SOURCES.md`.
- **Per-project memory:** copy `templates/CLAUDE.project.md` to a repo's
  `./CLAUDE.md` and fill it in. Codebase-specific facts belong there, not global.

Each addition should name the concrete pain it removes.

## Releasing the Claude Code plugin

Tagged releases, not rolling — a plain `/plugin marketplace add` tracks the
default branch, so cutting a release is what gives anyone who wants to pin a
version something to point at:

```bash
# 1. bump the version in .claude-plugin/plugin.json, and in CHANGELOG.md
#    rename "## [Unreleased]" to "## [<version>] - <YYYY-MM-DD>" and add a
#    new empty "## [Unreleased]" above it
# 2. tag + push (validates plugin.json and the marketplace entry agree)
claude plugin tag --push -m "addit-harness %s"
# 3. publish the matching CHANGELOG.md section as the release notes
.github/scripts/changelog-section.sh <version> > notes.md
gh release create addit-harness--v<version> --notes-file notes.md
```

`.github/workflows/release.yml` (manual `workflow_dispatch`) runs the bump, tag
and release in CI. It fails before changing anything if `## [Unreleased]` in
`CHANGELOG.md` is empty; otherwise the bump commit renames it to
`## [<version>] - <date>` and adds a fresh empty `## [Unreleased]` above it, and
the release body is that version's section (no fallback to generated notes). The
docs changelog page renders the `[Unreleased]` section plus every GitHub release
at deploy time, so released text appears once, from the release.

`claude plugin tag` creates a `addit-harness--v<version>` tag (not a bare
`vX.Y.Z`) and refuses a dirty working tree or a duplicate tag unless
`--force`; pass `--dry-run` to preview first.

> `v0.1.0`, the first release, was tagged manually (`git tag 0.1.0`) before
> this convention was settled — it predates `claude plugin tag` being used
> here. It still installs and works fine; from `v0.2.0` on, use `claude
> plugin tag` so every subsequent tag is validated and consistently named.

**Versioning is manual, not tag-derived.** `plugin.json`'s `version` field is
the source of truth — `claude plugin tag` reads it and creates a matching
git tag (and errors if `plugin.json` and the marketplace entry disagree); it
does not go the other direction and infer a version from existing tags. So
step 1 above (bump `version` by hand) always comes first — there's no
`npm version`-style auto-bump or git-tag-derived versioning in the Claude
Code plugin tooling today.
