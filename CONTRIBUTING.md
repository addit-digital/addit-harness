# Contributing

Contributions are welcome — bug reports, new subagents, language rules, and skill additions. Keep each PR focused on one concern.

## How to extend

**Add a language rule**
Drop a lean `rules/<lang>.md` with `paths:` frontmatter (Tier 1). If it needs depth, add a `references/<lang>.md` it points to (Tier 2). See `rules/go.md` as an example of a thin Tier-1 pointer.

**Vendor another subagent**
Copy the `.md` into `agents/`, add a row with its source URL + commit SHA to `agents/SOURCES.md`. Subagents should declare a `model:` in their frontmatter.

**Add a skill**
Cherry-pick from community sources into `skills/`, record it in `skills/SOURCES.md` with provenance (URL, commit, license).

**Update a pinned asset**
Re-fetch at a newer commit, replace the file, bump the SHA in the relevant `SOURCES.md`.

**Per-project memory**
Copy `templates/CLAUDE.project.md` to a repo's `./CLAUDE.md`. Codebase-specific facts belong there, not in this global config.

## Principles

- Each addition should name the concrete pain it removes — no speculative tooling.
- Prefer adopting well-known, maintained assets over hand-rolling bespoke ones.
- Don't bundle unrelated changes in one PR.
- Test your changes with `./install.sh` on a clean `~/.claude` or a backup.

## License

By contributing you agree that your contributions are licensed under the [MIT License](LICENSE).
