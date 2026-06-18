# <Project name> — project memory

> Copy this to a repo's `./CLAUDE.md` (or `.claude/CLAUDE.md`) and fill it in.
> This is where **codebase-specific** facts live — keep them out of global memory.
> Keep it tight; prune anything that wouldn't change Claude's behavior.

## What this is
One or two sentences: what the service/app does and its role in the wider system.

## Build / test / run
The exact commands (so Claude can verify its own work):
- Build: `...`
- Test: `...`  (and how to run a single test)
- Lint/format: `...`
- Run locally: `...`

## Architecture
- Key modules/packages and their responsibilities.
- Important data flows / request lifecycle.
- External dependencies (DBs, queues, services) and how they're configured.

## Conventions specific to this repo
- Patterns to follow (and any deliberate deviations from the global language rules).
- Naming, layering, error-handling norms unique to this codebase.

## Gotchas
- Non-obvious constraints, footguns, flaky areas, "don't touch X without Y".

## Where to start
- The files/dirs to read first to understand a change in a given area.
