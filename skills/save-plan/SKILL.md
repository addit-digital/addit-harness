---
name: save-plan
description: Use when the user wants to save, export, or persist a plan (or any diagram-rich design doc shown in the CLI) to a markdown file so it can be opened and viewed with rendered mermaid diagrams. The terminal can't render mermaid; this writes the plan to docs/plans/ (or a temp scratch file) for viewing in an IDE preview or on GitHub.
user-invocable: true
argument-hint: [short plan title] [--temp]
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
Preserve it verbatim, including all mermaid blocks and section structure. If no
plan exists yet, say so and stop — don't invent one.

## Choosing permanent vs temporary
- **Permanent** (default): `docs/plans/<YYYY-MM-DD>-<kebab-title>.md`, tracked in
  git. Best for design docs worth keeping and for remote sessions (push → view on
  GitHub).
- **Temporary** (`--temp`): a scratch file under `.plans/` (gitignored) for quick
  local viewing without committing. Mainly useful in **local** CLI sessions — in a
  remote/container session a temp file isn't on your machine, so prefer permanent
  + push there.

## Procedure
1. **Resolve the title.** Use the given title (kebab-case it); otherwise derive a
   short slug from the plan's heading.
2. **Pick the path.**
   - Default: ensure `docs/plans/` exists (create it + a `docs/plans/README.md`
     index if missing). Target `docs/plans/<YYYY-MM-DD>-<slug>.md`. If the repo
     already has a plans/design-docs location, follow that instead.
   - `--temp`: ensure `.plans/` exists and is in `.gitignore` (add the line if
     missing); target `.plans/<YYYY-MM-DD>-<slug>.md`. If not in a repo, fall back
     to the system temp dir.
3. **Write** the plan content to the file verbatim (mermaid intact). Don't strip
   or "fix" diagrams.
4. **Update the index** (permanent only): add a row to `docs/plans/README.md` —
   date, title (link), one-line summary.
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
