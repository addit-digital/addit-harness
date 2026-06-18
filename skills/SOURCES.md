# Vendored / adapted skills — provenance

| Skill | Origin | Notes |
|-------|--------|-------|
| `adr/` | Authored fresh; adopts the **MADR 4.0** format ([adr.github.io/madr](https://adr.github.io/madr/), [github.com/adr/madr](https://github.com/adr/madr)). Templates embedded verbatim from upstream. | Default = MADR minimal, with a full variant; Nygard kept as a fallback. Conventions (NNNN numbering, status lifecycle, supersede-don't-edit, README index) follow `adr-tools`/MADR norms. Prior art reviewed: [wshobson/agents ADR skill](https://github.com/wshobson/agents/blob/main/plugins/documentation-generation/skills/architecture-decision-records/SKILL.md), [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/blob/main/skills/architecture-decision-records/SKILL.md). Format gallery: [joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record). |

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
