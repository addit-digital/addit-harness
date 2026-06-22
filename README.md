# claude-config

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-orange)
![Go](https://img.shields.io/badge/Go-00ADD8?logo=go&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?logo=openjdk&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)

Claude Code's out-of-the-box global config is a blank slate. This repo gives you a battle-tested starting point for backend engineers: language conventions that auto-load per file type, specialized subagents (architect, reviewer, debugger, developer), a plan→verify→commit engineering loop baked into the system prompt, and a one-line install. Philosophy: curate established assets and adapt them — don't hand-roll what already exists.

---

My personal, global [Claude Code](https://code.claude.com) configuration for
Java / Go / TypeScript backend & distributed-systems work.

**Philosophy:** adopt established, well-known assets (the official plugin
marketplace + reputable community collections) and adapt/pin them — don't
hand-roll what already exists. The repo is a thin **curation + config layer**, not
a pile of bespoke skills. It deliberately reuses Claude Code's built-ins
(`/code-review`, `/simplify`, `/verify`, `/run`, `/init`, `deep-research`).

## Install

```bash
git clone <this-repo> ~/src/claude-config && cd ~/src/claude-config
./install.sh             # copy files into ~/.claude (backs up anything it replaces)
./install.sh --link      # OR symlink instead, so edits track git
./install.sh --plugins   # also register marketplaces + install official plugins now
```

`install.sh` maps each item to its required place under `~/.claude/` and merges
per-file — it never clobbers the whole directory, so `projects/`, history, and
existing hooks are preserved. Re-running backs up replaced files to `*.bak.<ts>`.

> If you already had a `~/.claude/settings.json`, it's backed up and replaced —
> merge any custom permissions/hooks back from the `.bak` file.

## What's in here

| Path | What | How it's sourced |
|------|------|------------------|
| `CLAUDE.md` | Lean global memory: operating model + hard rules | Authored; follows [Anthropic memory](https://code.claude.com/docs/en/memory) & [best-practices](https://www.anthropic.com/engineering/claude-code-best-practices) |
| `rules/engineering-loop.md` | Always-on plan→verify→commit model + anti-patterns; sets diagram-rich (mermaid) plan/design-doc standards | Authored |
| `rules/{java,go,typescript}.md` | **Thin auto-loaded pointers** (Tier 1) — route to the references | Authored (routing only, no convention text) |
| `references/{go,java,typescript}/` | **Convention guides + linked authorities, read on-demand** (Tier 2) | Go: codebase-derived from app-erp; Java/TS: vendored from recognized sources — see each `README.md` |
| `agents/*.md` | Subagents: code-reviewer, debugger, architect-reviewer, backend-architect, frontend-architect, feature-investigator, backend-developer, frontend-developer | **Vendored + pinned** (except `backend-architect`/`frontend-architect`/`backend-developer`/`frontend-developer`, authored) — see `agents/SOURCES.md` |
| `skills/adr/` | `/adr` — record Architecture Decision Records (**MADR 4.0**) | Adopts MADR (see `skills/SOURCES.md`) |
| `skills/save-plan/` | `/save-plan` — persist an **implementation plan** to `docs/plans/` (or `--temp`) so mermaid renders in an IDE/GitHub. Architecture designs → `docs/solutions/`; review reports → `docs/architecture-reports/` (written directly by the relevant agent) | Authored |
| `skills/go-conventions/` | `/go-conventions [--refresh]` — scan a Go repo and write `.claude/go-conventions.md` (project-specific layer on top of the global baseline) | Authored |
| `skills/design-conventions/` | `/design-conventions [--refresh]` — scan a TS/React project's existing UI layer and write `.claude/design-conventions.md` (visual design language: tokens, type/spacing/color scales, component lib, layout rhythm, state patterns). For greenfield projects, `@frontend-architect` generates this file instead. | Authored |
| `settings.json` | Default model + permissions + official plugins (`enabledPlugins`) | Authored |
| `mcp.example.json` | Disabled Atlassian/DB scaffolding (opt-in) | Reference config |
| `templates/CLAUDE.project.md` | Per-repo memory template | Authored |

Three ways assets are delivered:
- **Adopted (declarative):** official plugins enabled via `settings.json` — track
  their marketplace, safe to auto-update.
- **Vendored (pinned):** subagents *and* Java/TS convention guides, copied in at a
  fixed commit for reproducibility (provenance + license in `*/SOURCES.md` and
  each `references/*/README.md`).
- **Authored (routing/process only):** `CLAUDE.md`, `rules/engineering-loop.md`,
  thin Tier-1 pointer rules, and the Go conventions file (codebase-derived).

### Language conventions — two tiers + per-project layer

- **Tier 1 — `rules/{java,go,typescript}.md`** carry `paths:` frontmatter and
  auto-load when you touch that language. They contain **only a pointer** — no
  convention text of their own.
- **Tier 2 — `references/{go,java,typescript}/`** hold the convention guides + a
  `README.md`. Not path-scoped; Claude reads them on demand for substantial work.
- **Per-project — `.claude/go-conventions.md`** in any Go repo. Run
  `/go-conventions` to generate it; `rules/go.md` loads it automatically.
- **Per-project — `.claude/design-conventions.md`** in any TS/React project. Run
  `/design-conventions` on an existing project to derive it; for greenfield,
  `@frontend-architect` generates it. `rules/typescript.md` instructs loading it
  first for any UI work.

| Stack | In-repo reference | Linked authorities |
|-------|-------------------|--------------------|
| Go | `references/go/app-erp-conventions.md` (codebase-derived: Gin · MongoDB v2 · slog · OTel) + per-project `.claude/go-conventions.md` | Effective Go, Go Code Review Comments, Google Go Style |
| Java/Spring | sanjeed5 `java.mdc` (CC0, Google-derived) | Effective Java, Google Java Style, Spring docs |
| TS / React / Next / RN | bulletproof-react docs (MIT) + sanjeed5 TS/React/Next/RN `.mdc` (CC0) | react.dev, Next.js docs, TypeScript Handbook, Total TypeScript |

The Go reference is **codebase-derived** (not a third-party style guide) — it
reflects the actual patterns in addit-digital/app-erp and expands per-project
via `/go-conventions`. The **`code-reviewer` subagent checks adherence** to
whichever conventions apply.

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
They install on first start, or run `./install.sh --plugins` to do it now.

### Subagents
Delegate isolated work to keep your main context clean:
`@code-reviewer` (also checks convention adherence), `@debugger`,
`@architect-reviewer`, `@backend-architect` (up-front API/service design only),
`@frontend-architect` (up-front component/rendering/state design only),
`@feature-investigator` (investigate a feature/product request before building →
spec/PRD-lite), and the implementation agents `@backend-developer` (Go ·
Java/Spring) and `@frontend-developer` (TS/React/Next/RN) — senior craftsmen that
design clean structures, write tests, and verify code against the conventions.

## Use cases

Concrete workflows showing which configs fire together.

**Build a new feature**
1. `@feature-investigator` → requirements/scope (spec/PRD-lite) before any code.
2. Plan it — a diagram-rich plan (mermaid), then `/save-plan` → `docs/plans/`
   to view it rendered in an IDE/GitHub (the terminal can't render mermaid).
   TaskCreate a tracked task list from the plan's phased steps so status is
   visible; TaskUpdate each task as it completes.
3. Implement — `@backend-developer` and/or `@frontend-developer` write + verify
   the code; Tier-1 `rules/<lang>.md` auto-load per file type and they read the
   vendored `references/<lang>/` guides on demand.
4. `@code-reviewer` → checks correctness, security, *and* adherence to the
   vendored conventions (file:line violations).

**Review or debug existing code**
- `@code-reviewer` on a diff — flags convention violations with file:line.
- `@debugger` for a failing test or stack trace — isolates root cause.

**Make an architecture decision**
- `@backend-architect` (API/service) or `@frontend-architect` (component/rendering/state)
  produce a design doc → saved to `docs/solutions/<date>-<slug>.md`.
- `@architect-reviewer` evaluates an existing design → saved to
  `docs/architecture-reports/<date>-<slug>.md`.
- Record the decision with `/adr` (MADR) under `docs/adr/`.

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
| `code-reviewer` | `opus` | A strong reviewer = less *manual* review for you |
| `backend-developer` | `sonnet` | Implementation/execution — fast + cheap against the conventions |
| `frontend-developer` | `sonnet` | Implementation/execution — fast + cheap against the conventions |
| `debugger` | `sonnet` | Iterative; escalate with `/model` if stuck |
| `feature-investigator` | `sonnet` | Requirements/spec investigation (upstream default) |

Future mechanical agents (test-runners, formatters) should use `haiku`. Override
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

## Enabling MCP (later)

Both Atlassian and database MCP are intentionally **off** for now. To enable:

1. Open `mcp.example.json` and copy the entry you want into
   `~/.claude/.mcp.json` (under an `mcpServers` object).
2. Put secrets/connection strings in `~/.claude/mcp.local.json` (gitignored) —
   never commit them.
3. Restart Claude Code; check with `/mcp`.

- **Atlassian Cloud:** `claude mcp add --transport http atlassian https://mcp.atlassian.com/v1/mcp` (official Rovo server, OAuth).
- **Atlassian Data Center:** community `sooperset/mcp-atlassian` (token/PAT).
- **Postgres:** `crystaldba/postgres-mcp` (read-only by default).
- **MySQL:** `benborla/mcp-server-mysql` or `designcomputer/mysql_mcp_server`.

## Extending

- **Add a language rule:** drop a lean `rules/<lang>.md` with `paths:` frontmatter
  (Tier 1) and, if it needs depth, a `references/<lang>.md` it points to (Tier 2).
- **Vendor another subagent:** copy the `.md` into `agents/`, add a row with its
  source + commit SHA to `agents/SOURCES.md`.
- **Add a command/skill:** cherry-pick from
  [qdhenry/Claude-Command-Suite](https://github.com/qdhenry/Claude-Command-Suite)
  into `skills/`, record it in `skills/SOURCES.md`.
- **Update a pinned asset:** re-fetch at a newer commit, replace the file, bump
  the SHA in the relevant `SOURCES.md`.
- **Per-project memory:** copy `templates/CLAUDE.project.md` to a repo's
  `./CLAUDE.md` and fill it in. Codebase-specific facts belong there, not global.

Each addition should name the concrete pain it removes.
