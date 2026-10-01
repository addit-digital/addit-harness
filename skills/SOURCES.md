# Vendored / adapted skills — provenance

| Skill | Origin | Notes |
|-------|--------|-------|
| `adr/` | Authored fresh; adopts the **MADR 4.0** format ([adr.github.io/madr](https://adr.github.io/madr/), [github.com/adr/madr](https://github.com/adr/madr)). Templates embedded verbatim from upstream. | Default = MADR minimal, with a full variant; Nygard kept as a fallback. Conventions (NNNN numbering, status lifecycle, supersede-don't-edit, README index) follow `adr-tools`/MADR norms. Optional mermaid `Architecture / Flow` section added for structural decisions. Prior art reviewed: [wshobson/agents ADR skill](https://github.com/wshobson/agents/blob/main/plugins/documentation-generation/skills/architecture-decision-records/SKILL.md), [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code/blob/main/skills/architecture-decision-records/SKILL.md). Format gallery: [joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record). |
| `save-plan/` | Authored fresh. | `/save-plan [title] [--temp]` persists a plan/design doc to `docs/work/<slug>/plans/plan.md` (or a gitignored `.plans/` scratch file) so its mermaid renders in an IDE preview or on GitHub — the CLI terminal can't render mermaid. No external dependency (no mermaid-cli/Chromium). |
| `go-conventions/` | Authored fresh. | `/go-conventions [--refresh]` scans the current Go repo and writes `.claude/go-conventions.md` — a project-specific convention file loaded by `rules/go.md` each session. `--refresh` merges new patterns into the existing file. |
| `design-conventions/` | Authored fresh. | `/design-conventions [--refresh]` scans the current TS/React project's UI layer and writes `.claude/design-conventions.md` — a project-specific visual design convention file (tokens, type/spacing/color scales, component lib, layout rhythm, state patterns) loaded by `rules/typescript-frontend.md` before UI work. For greenfield projects, `@frontend-architect` generates this file instead. `--refresh` merges new patterns; preserves hand-edits. |
| `dev-flow/` | Authored fresh. | `/dev-flow [what to build or fix]` drives a work item through the full engineering loop — investigate → design ⇄ `architect-reviewer` (deterministic loop, capped at 3 rounds) → **explicit human approval gate** → implement → `qa-engineer` verifies → code-review ⇄ fix (deterministic loop, capped at 2 rounds) → `qa-engineer` re-verifies. The design-gate and review-gate loops run as `Workflow` scripts (`workflows/dev-flow-design.js`, `workflows/dev-flow-implement.js`, at plugin root, not nested under the skill) instead of hand-driven `Agent` calls; the skill itself stays thin — it resolves track/repo/slug, holds the one human-approval gate a `Workflow` script can't pause for, and falls back to direct sequential `Agent` calls if `Workflow` isn't available. Software-development-lifecycle scoped, not a generic multi-domain router — see `docs/work/2026-08-22-workflow-orchestration-qa-agent/plans/plan.md` for the full design history (three review-flagged and fixed mechanical issues: an unworkable skill-delegation attempt for the review-gate reverted to direct `parallel()` fan-out, a `'both'`-track bug that silently dropped frontend design/misrouted fixes, and missing repo-context arguments — plus a further `pr-review-toolkit:review-pr` round-trip that caught the design/UX loops not feeding reviewer findings into re-attempts, a reviewer-failure path that could report a false "clean," and untracked `A.track` validation). Depends on `${CLAUDE_PLUGIN_ROOT}` and the `Workflow` tool. |

## `../commands/` — why it duplicates these skills

Each skill above also has a matching `commands/<name>.md` at the repo root.
That's not stale duplication: Claude Code's plugin loader currently only
registers a plugin's `commands/*.md` as slash commands, not
`skills/*/SKILL.md`, for marketplace-installed plugins
([anthropics/claude-code#18949](https://github.com/anthropics/claude-code/issues/18949),
[#57737](https://github.com/anthropics/claude-code/issues/57737)). The
`commands/` files are thin delegates (frontmatter mirrored from the skill,
body just invokes the skill via the Skill tool) so `/addit-harness:setup`
etc. actually resolve until that's fixed upstream. If you add a new
user-invocable skill, add its `commands/<name>.md` delegate too.

## Skills adopted as plugins (not vendored here)
These are enabled via `settings.json` (placed by setup), not stored in this repo:
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
