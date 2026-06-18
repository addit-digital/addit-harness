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
| `rules/{java,go,typescript}.md` | **Extensive per-language conventions, auto-applied** | Adapted from [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) + established idioms |
| `agents/*.md` | Role subagents: code-reviewer, debugger, architect-reviewer, backend-architect | **Vendored + pinned** — see `agents/SOURCES.md` |
| `skills/adr/` | `/adr` — record Architecture Decision Records | Adapted (see `skills/SOURCES.md`) |
| `settings.json` | Permissions + official plugins (`enabledPlugins`) | Authored |
| `mcp.example.json` | Disabled Atlassian/DB scaffolding (opt-in) | Reference config |
| `templates/CLAUDE.project.md` | Per-repo memory template | Authored |

Three ways assets are delivered:
- **Adopted (declarative):** official plugins enabled via `settings.json` — track
  their marketplace, safe to auto-update.
- **Vendored (pinned):** community subagents/skills copied in at a fixed commit
  for reproducibility (provenance in `*/SOURCES.md`).
- **Adapted:** rules/memory authored from established sources.

### Auto-applied language conventions (the main feature)
`rules/{java,go,typescript}.md` carry `paths:` frontmatter, so when you work in a
Go repo the Go conventions load automatically — **no command to invoke**. Open a
`.java` file and Java conventions apply; Go ones don't. The always-on global
`CLAUDE.md` stays small (<200 lines); the heavy per-language detail is
path-scoped so it only costs context when relevant.

### Official plugins (declared in `settings.json`)
Enabled from the auto-available `claude-plugins-official` marketplace (+
`anthropics/skills`). The big win is real **language servers**:
`gopls-lsp`, `jdtls-lsp`, `typescript-lsp`, plus `pr-review-toolkit`,
`commit-commands`, `security-guidance`, and `document-skills` (doc generation).
They install on first start, or run `./install.sh --plugins` to do it now.

### Subagents
Delegate isolated work to keep your main context clean:
`@code-reviewer`, `@debugger`, `@architect-reviewer`, `@backend-architect`.

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

- **Add a language rule:** drop `rules/<lang>.md` with `paths:` frontmatter.
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
