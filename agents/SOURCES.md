# Vendored subagents — provenance

These role subagents are vendored (copied) from established community
collections and **pinned to a specific commit** for reproducibility. To update
one, re-fetch from the source repo at a newer commit, replace the file, and bump
the SHA below.

Retrieved: 2026-06-18.

| File | Source repo | Path | Pinned commit | Changes |
|------|-------------|------|---------------|---------|
| `code-reviewer.md` | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | `categories/04-quality-security/code-reviewer.md` | `5983fe3b4ea2785335ac1712c4aa1ac4e13a8fa2` | verbatim |
| `debugger.md` | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | `categories/04-quality-security/debugger.md` | `5983fe3b4ea2785335ac1712c4aa1ac4e13a8fa2` | verbatim |
| `architect-reviewer.md` | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | `categories/04-quality-security/architect-reviewer.md` | `5983fe3b4ea2785335ac1712c4aa1ac4e13a8fa2` | verbatim |
| `backend-architect.md` | [wshobson/agents](https://github.com/wshobson/agents) | `plugins/backend-development/agents/backend-architect.md` | `cc37bfdd292ce520ba1c44df7a3a70d5f8137236` | `name` changed from `backend-development-backend-architect` to `backend-architect` for standalone invocation; body verbatim |

## Notes
- Both source repos track `main` with no tagged releases — that's why we vendor
  and pin rather than installing live from a marketplace.
- The VoltAgent agents reference a multi-agent "context manager" protocol (JSON
  query blocks). That's harmless here — Claude treats it as role guidance — but
  it's noise you can trim if you want leaner files.
- Per-language depth (Java/Go/TS) is intentionally delivered via auto-loading
  `rules/`, not subagents, so it applies without manual invocation.
