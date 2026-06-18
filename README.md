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
| `rules/engineering-loop.md` | Always-on plan→verify→commit model + anti-patterns | Authored |
| `rules/{java,go,typescript}.md` | **Lean per-language essentials, auto-applied** (Tier 1) | Adapted from [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) + established idioms |
| `references/{go,java,typescript}/` | **Extensive per-topic conventions + examples, read on-demand** (Tier 2) — one file per topic + `README.md` index | Adapted from canonical style guides + Spring/React docs; Go → Gin + MongoDB/`database/sql`; TS → React/Next.js/React Native |
| `agents/*.md` | Role subagents: code-reviewer, debugger, architect-reviewer, backend-architect | **Vendored + pinned** — see `agents/SOURCES.md` |
| `skills/adr/` | `/adr` — record Architecture Decision Records (**MADR 4.0**) | Adopts MADR (see `skills/SOURCES.md`) |
| `settings.json` | Default model + permissions + official plugins (`enabledPlugins`) | Authored |
| `mcp.example.json` | Disabled Atlassian/DB scaffolding (opt-in) | Reference config |
| `templates/CLAUDE.project.md` | Per-repo memory template | Authored |

Three ways assets are delivered:
- **Adopted (declarative):** official plugins enabled via `settings.json` — track
  their marketplace, safe to auto-update.
- **Vendored (pinned):** community subagents/skills copied in at a fixed commit
  for reproducibility (provenance in `*/SOURCES.md`).
- **Adapted:** rules/memory authored from established sources.

### Auto-applied language conventions — two tiers (the main feature)
Conventions are split to give depth *and* low token cost:

- **Tier 1 — `rules/{java,go,typescript}.md`** carry `paths:` frontmatter, so when
  you work in a Go file the lean Go essentials load automatically — **no command
  to invoke**. Open a `.java` file and Java essentials apply; Go ones don't. These
  are short (the non-negotiables) so the in-language token cost stays small.
- **Tier 2 — `references/{go,java,typescript}/`** hold the *extensive* conventions
  with worked examples, **split into one file per topic** (e.g.
  `references/java/persistence-spring-data.md`) with a `README.md` index. They are
  **not** path-scoped, so they never auto-load; each Tier-1 rule points to the
  index, and Claude reads only the relevant topic with the Read tool **when doing
  substantial work**. Cost ≈ zero until needed, and even then only the one topic
  loads. Go covers Gin + MongoDB/`database/sql`; Java covers MVC + WebFlux + Kafka
  + Spring Data + Gradle/Maven; TS covers React/Next.js/React Native.

Why this matters: path-scoped rules load only in-language (not every session) and
the whole file stays for that session — so keeping Tier 1 lean and pushing depth
to on-demand Tier 2 is the token-efficient pattern
([memory docs](https://code.claude.com/docs/en/memory),
[skills docs](https://code.claude.com/docs/en/skills)). The global `CLAUDE.md`
stays under 200 lines. TypeScript conventions target **React / Next.js / React
Native** (frontend & mobile).

### Official plugins (declared in `settings.json`)
Enabled from the auto-available `claude-plugins-official` marketplace (+
`anthropics/skills`). The big win is real **language servers**:
`gopls-lsp`, `jdtls-lsp`, `typescript-lsp`, plus `pr-review-toolkit`,
`commit-commands`, `security-guidance`, and `document-skills` (doc generation).
They install on first start, or run `./install.sh --plugins` to do it now.

### Subagents
Delegate isolated work to keep your main context clean:
`@code-reviewer`, `@debugger`, `@architect-reviewer`, `@backend-architect`.

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
