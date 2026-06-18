# Vendored / adapted skills — provenance

| Skill | Origin | Notes |
|-------|--------|-------|
| `adr/` | Adapted from the `architecture-decision-records` skill in [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/blob/main/skills/architecture-decision-records/SKILL.md) (commit `ceca28852e5b31edbbf66ebccc8fd163dd14208e`), following Michael Nygard's standard ADR format. | Authored fresh as a lean, self-contained `SKILL.md` rather than copied, to avoid pulling in the source repo's broader harness. |

## Skills adopted as plugins (not vendored here)
These are enabled via `settings.json` / `install.sh`, not stored in this repo:
- **Document generation** — `document-skills@anthropic-agent-skills`
  (official [anthropics/skills](https://github.com/anthropics/skills): docx, pdf,
  pptx, xlsx).

## Built-ins we deliberately reuse (do NOT re-create as skills)
`/code-review`, `/simplify`, `/verify`, `/run`, `/init`, and `deep-research`
already ship with Claude Code.

## Optional, cherry-pick later (see README)
[qdhenry/Claude-Command-Suite](https://github.com/qdhenry/Claude-Command-Suite)
has good architecture / feature-build / docs commands if you want more than the
ADR skill — copy individual command files into `skills/` and record them here.
