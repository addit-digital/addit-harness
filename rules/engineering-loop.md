# The engineering loop

Always-on. The mental model for every non-trivial task.

## The loop
1. **Frame intent** — restate the goal, constraints, and what "done" means.
   If the request is ambiguous in a way that changes the approach, ask first.
2. **Curate context** — read the specific code that matters; don't guess. Reuse
   existing functions, patterns, and utilities before writing new ones.
3. **Write the plan** — for non-trivial work, write the plan before coding per `references/doc-protocol.md` (addit-harness plugin): the doc type's template, tier ceiling, Observed/Inferred/Unknown labels, edit in place on revision. One mermaid diagram per concept, current state; skip only for trivial edits (typo / one-liner / rename).
   After plan approval, persist it with `/save-plan` → `docs/work/<slug>/plans/`
   (the harness scratch file at `~/.claude/plans/` is ephemeral working state,
   not the home). Then create a tracked task list with TaskCreate from the plan's
   phased steps so implementation status is visible; update each task
   (TaskUpdate) as it completes.
4. **Implement in small, verifiable units** — one concern at a time.
5. **Verify with tooling** — run tests/build/lint or `/verify`. Observe real
   behavior; don't assert success from reading the code.
6. **Commit** at a coherent checkpoint with a clear message.
7. **Clear / hand off** — when context grows long, summarize decisions and next
   steps so the session can be reset cheaply.

## Design documentation & viewing
- Plans, solutions, ADRs and PR descriptions are design documentation: one mermaid diagram per concept, edited in place. Git holds history.
- The CLI terminal **cannot render mermaid** (it shows raw code). So save a
  non-trivial plan to a markdown file with `/save-plan` (default
  `docs/work/<slug>/plans/`), then open it in an IDE preview (Cursor / VS Code,
  Ctrl/Cmd+Shift+V) or on GitHub — both render mermaid. ADRs and PR descriptions
  already live as files / on GitHub, so they render there too.

### Doc taxonomy — where each artifact lives

One folder per unit of work — feature, bug fix, improvement, or enhancement —
at `docs/work/<slug>/`, holding everything produced for it in per-type subfolders:

| Subfolder | Holds | Produced by |
|--------|-------|-------------|
| `plans/` | **Implementation plans** — phased steps, to-do lists, acceptance criteria | Main Claude via `/save-plan` |
| `solutions/` | **Architecture solution/design docs** — no to-do list, pure design | `@backend-architect`, `@frontend-architect`, or main Claude for design-only output |
| `architecture-reports/` | **Architecture review reports** | `@architect-reviewer` |
| `specs/` | **Intake brief** `brief.md`; quarantined `owner-proposal.md` | `@product-owner` |
| `qa-reports/` | **QA/regression verification reports**, evidence-backed | `@qa-engineer` |
| `legal/` | **Per-change legal analysis** (`legal/assessment.md`) | `@saas-legal-advisor` |

Subfolders, not flat files: a whole category (e.g. `plans/`) can be ignored by
directory. Files: `plans/plan.md`, `solutions/solution-<track>.md`,
`architecture-reports/report.md`, `qa-reports/report.md` — reports
round-suffixed (`report-r2.md`) on a repeat round; create the
`docs/work/<slug>/` folder + a row in `docs/work/README.md` on first use; don't
commit/push unless asked.

**Plugin conventions win.** Write work artifacts only to `docs/work/<slug>/<type>/`, ADRs to `docs/adr/`, standing legal docs to `docs/legal/<document-kind>.md` — even if the repo has its own plans/ADR/legal folders (read those as input). A project `CLAUDE.md` adds facts; it does not move these folders.
**Slug.** `$(date +%F)-<short-name>`, or `<ticket-id>-<short-name>` for ticket work.
**Never overwrite work-item artifacts.** A slug is the same work item only if this session created or was given it; otherwise, if `docs/work/<slug>/` exists, append `-2`, `-3`…. Standing docs (`docs/legal/`, `docs/adr/README.md`, `docs/work/README.md`, `.claude/design-conventions.md`) are edited in place; git is the history.

## Anti-patterns to avoid
- **Mega-prompt**: cramming many unrelated goals into one turn. Split them.
- **Endless session**: letting context degrade instead of summarizing + clearing.
- **Speculative tooling**: adding libraries/abstractions/MCP servers with no
  present need.
- **Unverified "done"**: claiming success without running anything.
- **Re-explaining context**: re-sending what's already in memory or the repo;
  put durable facts in `CLAUDE.md`/`rules/`, not repeated prose.
- **Scope creep in a change**: mixing refactor + feature + fix in one diff.
- **Wrong plan location**: writing plans to `~/.claude/plans/`, `.cursor/plans/`,
  or any IDE/harness scratch directory. Those are ephemeral working files — the
  durable artifact belongs in the repo under `docs/work/<slug>/plans/` (via
  `/save-plan`), `solutions/`, `architecture-reports/`, or `qa-reports/` per the
  taxonomy above.
