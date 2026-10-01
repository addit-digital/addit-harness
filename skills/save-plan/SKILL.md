---
name: save-plan
description: Use when the user wants to save, export, or persist a plan (or any diagram-rich design doc shown in the CLI) to a markdown file so it can be opened and viewed with rendered mermaid diagrams. The terminal can't render mermaid; this writes the plan to docs/work/<slug>/plans/ (or a temp scratch file) for viewing in an IDE preview or on GitHub.
user-invocable: true
argument-hint: "[short plan title] [--temp]"
---

# Save plan — persist a plan to a viewable markdown file

The Claude Code CLI shows a ` ```mermaid ` block as raw code, never a rendered
diagram, and a plan presented in the CLI isn't saved anywhere convenient to open.
This skill writes the plan to a markdown file so it can be opened with **rendered
mermaid** — in an IDE preview (Cursor / VS Code, Ctrl/Cmd+Shift+V) or on GitHub
(renders mermaid natively).

## What to save
The current plan under discussion — typically the approved plan-mode plan (the
harness plan file) or the most recent plan/design doc written in this session.
Save it as-is when within its tier ceiling in references/doc-protocol.md; if over, trim to the plan template first and say what you cut. Keep mermaid blocks intact. If no
plan exists yet, say so and stop — don't invent one.

## Where it goes — artifact routing

This skill is for **implementation plans** (phased steps, to-do lists, acceptance
criteria). Docs are grouped by unit of work, not by type: one folder per feature,
bug fix, improvement, or enhancement at `docs/work/<slug>/`, holding everything
produced for it in per-type subfolders. The broader taxonomy:

| Artifact | Subfolder | Produced by |
|----------|--------|-------------|
| Implementation plan | `plans/` | This skill (default) |
| Architecture design / solution doc (no to-do list) | `solutions/` | `@backend-architect`, `@frontend-architect` directly |
| Architecture review report | `architecture-reports/` | `@architect-reviewer` directly |
| QA/regression verification report | `qa-reports/` | `@qa-engineer` directly |
| Per-change legal analysis | `legal/` | `@saas-legal-advisor` directly |

Layout, slug and collision: plugin conventions win — see rules/engineering-loop.md "Doc taxonomy".

For a pure architecture design, review report, or QA report, skip this skill —
the relevant agent writes directly to the correct subfolder inside
`docs/work/<slug>/`, following the same naming convention (create the folder + a
`docs/work/README.md` index row if missing).

## Choosing permanent vs temporary
- **Permanent** (default): `docs/work/<YYYY-MM-DD>-<kebab-title>/plans/plan.md`
  (or `docs/work/<ticket-id>-<kebab-title>/plans/plan.md` if the project uses an
  issue tracker), tracked in git. Best for design docs worth keeping and for
  remote sessions (push → view on GitHub).
- **Temporary** (`--temp`): a scratch file under `.plans/` (gitignored) for quick
  local viewing without committing. Mainly useful in **local** CLI sessions — in a
  remote/container session a temp file isn't on your machine, so prefer permanent
  + push there.

## Procedure
1. **Resolve the slug.** Use the given title (kebab-case it); otherwise derive a
   short slug from the plan's heading. Prefix with the issue-tracker ID if the
   plan is tied to a ticket, else `$(date +%F)-`. Then check
   `ls -d docs/work/<slug>`: if it exists and this session did not create or
   receive that slug, append `-2`, `-3`… until absent. Never overwrite another
   work item's plan.
2. **Pick the path.**
   - Default: ensure `docs/work/<slug>/plans/` exists (create it, and
     `docs/work/README.md` with an index if missing). Target
     `docs/work/<slug>/plans/plan.md` — the file is always named `plan.md`; the
     slug lives in the folder name, not the filename, so everything produced for
     this work item sits together.
   - `--temp`: ensure `.plans/` exists and is in `.gitignore` (add the line if
     missing); target `.plans/<slug>.md`. If not in a repo, fall back
     to the system temp dir.
3. **Write** the plan content to the file as prepared above (mermaid intact). Don't strip
   or "fix" diagrams.
4. **Update the index** (permanent only): add a row to `docs/work/README.md` —
   row per doc-protocol.md "Index row"; update in place.
5. **Report** the absolute path and how to view it rendered:
   - Local: "open in Cursor / VS Code and toggle preview (Ctrl/Cmd+Shift+V)."
   - Remote/container session: "this file is in the container — commit & push,
     then view on GitHub (renders mermaid), or pull it locally."
   Don't commit or push unless the user asks.

## Notes
- Quality of rendering depends on valid mermaid syntax — keep node labels simple
  and quote labels containing special characters.
- This skill only persists and locates the file; it does not render images itself
  (no mermaid-cli/Chromium dependency). Rendering happens in the IDE/GitHub.
