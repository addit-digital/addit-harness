# claude-config

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
| `rules/{java,go,typescript}.md` | **Thin auto-loaded pointers** (Tier 1) — route to the vendored references | Authored (routing only, no convention text) |
| `references/{go,java,typescript}/` | **Vendored convention guides + linked authorities, read on-demand** (Tier 2) | **Vendored from recognized sources** (Uber Go Guide, bulletproof-react, sanjeed5/Google-derived) + links to authorities — see each `README.md` |
| `agents/*.md` | Subagents: code-reviewer, debugger, architect-reviewer, backend-architect, feature-investigator | **Vendored + pinned** — see `agents/SOURCES.md` |
| `skills/adr/` | `/adr` — record Architecture Decision Records (**MADR 4.0**) | Adopts MADR (see `skills/SOURCES.md`) |
| `skills/save-plan/` | `/save-plan` — save a plan to `docs/plans/` (or `--temp`) so mermaid renders in an IDE/GitHub | Authored |
| `settings.json` | Default model + permissions + official plugins (`enabledPlugins`) | Authored |
| `mcp.example.json` | Disabled Atlassian/DB scaffolding (opt-in) | Reference config |
| `templates/CLAUDE.project.md` | Per-repo memory template | Authored |

Three ways assets are delivered:
- **Adopted (declarative):** official plugins enabled via `settings.json` — track
  their marketplace, safe to auto-update.
- **Vendored (pinned):** subagents *and* the language convention guides, copied in
  at a fixed commit for reproducibility (provenance + license in `*/SOURCES.md`
  and each `references/*/README.md`).
- **Authored (routing/process only):** `CLAUDE.md`, `rules/engineering-loop.md`,
  and the thin Tier-1 pointer rules — no hand-written language conventions.

### Language conventions — vendored from well-known sources (two tiers)
The convention text comes from **recognized, established sources**, not authored
prose:

- **Tier 1 — `rules/{java,go,typescript}.md`** carry `paths:` frontmatter and
  auto-load when you touch that language. They contain **only a pointer** to the
  vendored references — no rules of our own.
- **Tier 2 — `references/{go,java,typescript}/`** hold the vendored guides + a
  `README.md` that lists what's vendored and links the link-only authorities.
  Not path-scoped, so they never auto-load; Claude reads the relevant guide on
  demand for substantial work.

What's vendored vs linked (full provenance + licenses in each `README.md`):

| Stack | Vendored (in-repo) | Linked authorities |
|-------|--------------------|--------------------|
| Go | Uber Go Style Guide (Apache-2.0) | Effective Go, Go Code Review Comments, Google Go Style; Gin & mongo-go-driver |
| Java/Spring | sanjeed5 `java.mdc` (CC0, Google-derived) | Effective Java, Google Java Style, Spring docs, spring-petclinic |
| TS / React / Next / RN | bulletproof-react docs (MIT) + sanjeed5 TS/React/Next/RN `.mdc` (CC0) | react.dev, Next.js docs, React Native docs, TypeScript Handbook, Total TypeScript |

Honest caveat: the genuinely comprehensive Java/TS *style guides* (Effective Java,
Google's guides) are a book / HTML, so they're **linked** while the in-repo text
for those stacks comes from the CC0 `sanjeed5` collection (script-generated,
derived from the official guides — a solid baseline; defer to the linked
authorities on any conflict). Go and React/Next use human-authored vendored
guides (Uber, bulletproof-react). The **`code-reviewer` subagent is wired to check
adherence** to these references.

### Official plugins (declared in `settings.json`)
Enabled from the auto-available `claude-plugins-official` marketplace (+
`anthropics/skills`). The big win is real **language servers**:
`gopls-lsp`, `jdtls-lsp`, `typescript-lsp`, plus `pr-review-toolkit`,
`commit-commands`, `security-guidance`, and `document-skills` (doc generation).
They install on first start, or run `./install.sh --plugins` to do it now.

### Subagents
Delegate isolated work to keep your main context clean:
`@code-reviewer` (also checks convention adherence), `@debugger`,
`@architect-reviewer`, `@backend-architect`, and `@feature-investigator`
(investigate a feature/product request before building → spec/PRD-lite).

## Use cases

Concrete workflows showing which configs fire together.

**Build a new feature**
1. `@feature-investigator` → requirements/scope (spec/PRD-lite) before any code.
2. Plan it — a diagram-rich plan (mermaid), then `/save-plan` to view it rendered
   in an IDE/GitHub (the terminal can't render mermaid).
3. Implement — Tier-1 `rules/<lang>.md` auto-load per file type; Claude reads the
   vendored `references/<lang>/` guides on demand.
4. `@code-reviewer` → checks correctness, security, *and* adherence to the
   vendored conventions (file:line violations).

**Review or debug existing code**
- `@code-reviewer` on a diff — flags convention violations with file:line.
- `@debugger` for a failing test or stack trace — isolates root cause.

**Make an architecture decision**
- `@architect-reviewer` / `@backend-architect` to weigh the design, then `/adr`
  to record it (MADR) under `docs/adr/`.

**Day-to-day coding in Go / Java / TS**
- Just open the file — language conventions auto-apply (Tier 1) and the reviewer
  enforces them; no command needed. Claude pulls deeper `references/` only for
  substantial work.

**Keep costs down**
- Default `opusplan` (Opus plans, Sonnet executes); `/model` to switch, `/effort
  low` for simple tasks, and delegate noisy work to subagents. See *Model & cost*.

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
| `code-reviewer` | `opus` | A strong reviewer = less *manual* review for you |
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
