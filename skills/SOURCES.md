# Vendored / adapted skills — provenance

| Skill | Origin | Notes |
|-------|--------|-------|
| `adr/` | Authored fresh; adopts the **MADR 4.0** format ([adr.github.io/madr](https://adr.github.io/madr/), [github.com/adr/madr](https://github.com/adr/madr)). Templates embedded verbatim from upstream. | Default = MADR minimal, with a full variant; Nygard kept as a fallback. Conventions (NNNN numbering, status lifecycle, supersede-don't-edit, README index) follow `adr-tools`/MADR norms. Optional mermaid `Architecture / Flow` section added for structural decisions. Prior art reviewed: [wshobson/agents ADR skill](https://github.com/wshobson/agents/blob/main/plugins/documentation-generation/skills/architecture-decision-records/SKILL.md), [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/blob/main/skills/architecture-decision-records/SKILL.md). Format gallery: [joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record). |
| `save-plan/` | Authored fresh. | `/save-plan [title] [--temp]` persists a plan/design doc to `docs/plans/<date>-<slug>.md` (or a gitignored `.plans/` scratch file) so its mermaid renders in an IDE preview or on GitHub — the CLI terminal can't render mermaid. No external dependency (no mermaid-cli/Chromium). |
| `go-conventions/` | Authored fresh. | `/go-conventions [--refresh]` scans the current Go repo and writes `.claude/go-conventions.md` — a project-specific convention file loaded by `rules/go.md` each session. `--refresh` merges new patterns into the existing file. |

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
