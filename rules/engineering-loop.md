# The engineering loop

Always-on. The mental model for every non-trivial task.

## The loop
1. **Frame intent** — restate the goal, constraints, and what "done" means.
   If the request is ambiguous in a way that changes the approach, ask first.
2. **Curate context** — read the specific code that matters; don't guess. Reuse
   existing functions, patterns, and utilities before writing new ones.
3. **Write the plan** — for non-trivial work, produce rich, scannable plan
   documentation before coding (not a prose blob). Default sections:
   **Context/problem**, **Approach** (chosen path + key trade-offs, not every
   alternative), **Diagrams (mermaid)**, **phased steps with acceptance
   criteria**, and **verification**. Include the mermaid diagrams that fit the
   change: architecture/component (`graph`/`flowchart`), data/control flow, and a
   `sequenceDiagram` for request/interaction flows; add a file-change map for
   multi-file work. Skip diagrams only for trivial edits (typo / one-liner /
   rename). See "Design documentation & viewing" below.
4. **Implement in small, verifiable units** — one concern at a time.
5. **Verify with tooling** — run tests/build/lint or `/verify`. Observe real
   behavior; don't assert success from reading the code.
6. **Commit** at a coherent checkpoint with a clear message.
7. **Clear / hand off** — when context grows long, summarize decisions and next
   steps so the session can be reset cheaply.

## Design documentation & viewing
- Plans, ADRs (`/adr`), and PR descriptions are design documentation: include
  relevant mermaid diagrams wherever you describe structure or flow — prose alone
  isn't enough for non-trivial work.
- The CLI terminal **cannot render mermaid** (it shows raw code). So save a
  non-trivial plan to a markdown file with `/save-plan` (default `docs/plans/`),
  then open it in an IDE preview (Cursor / VS Code, Ctrl/Cmd+Shift+V) or on
  GitHub — both render mermaid. ADRs and PR descriptions already live as files /
  on GitHub, so they render there too.

## Anti-patterns to avoid
- **Mega-prompt**: cramming many unrelated goals into one turn. Split them.
- **Endless session**: letting context degrade instead of summarizing + clearing.
- **Speculative tooling**: adding libraries/abstractions/MCP servers with no
  present need.
- **Unverified "done"**: claiming success without running anything.
- **Re-explaining context**: re-sending what's already in memory or the repo;
  put durable facts in `CLAUDE.md`/`rules/`, not repeated prose.
- **Scope creep in a change**: mixing refactor + feature + fix in one diff.
