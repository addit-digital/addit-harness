---
title: Roadmap
nav_order: 10
nav_group: Project
---

See [open issues](https://github.com/addit-digital/addit-harness/issues?q=label%3Aroadmap)
for planned work. Candidates:

- **Native plugin packaging for Cursor, Kiro, and Codex CLI** — all three
  have since shipped their own plugin/marketplace systems (Cursor plugins,
  Kiro Powers, Codex CLI plugins), analogous to what Claude Code now has.
  Each has its own manifest format and real gaps (Kiro Powers can't bundle
  custom agents; Codex CLI has an open team-rollout limitation), so each is
  its own follow-up rather than one change.
- **GitHub Copilot support** — project-scoped bundle
  (`.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`,
  `.github/agents/*.agent.md`), since Copilot has no machine-wide home
  directory to sync into like the other tools.
- **Skills as real slash-commands/prompts** per tool (`.cursor/commands/`,
  Kiro manual-inclusion steering, `~/.codex/prompts/`,
  `.github/prompts/*.prompt.md`) with correct invocation semantics, not just
  file placement.
- **`/design-review` skill** — audit a `docs/solutions/` design doc against
  the project's conventions.
- **`@security-reviewer` subagent** — dedicated security-focused review
  pass.

Contributions welcome — see
[`CONTRIBUTING.md`](https://github.com/addit-digital/addit-harness/blob/main/CONTRIBUTING.md).
Issues labeled
[`good first issue`](https://github.com/addit-digital/addit-harness/issues?q=label%3A%22good+first+issue%22)
are a good entry point.

## Next

- [Changelog](../changelog/) — what's already shipped, release by release.
- [Other coding agents](../other-agents/) — today's state of Cursor/Kiro/Codex support.
