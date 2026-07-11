---
title: Extending
nav_order: 9
nav_group: Guides
---

## Add to the config

- **Add a language rule:** drop a lean `rules/<lang>.md` with `paths:`
  frontmatter (Tier 1) and, if it needs depth, a `references/<lang>.md` it
  points to (Tier 2).
- **Vendor another subagent:** copy the `.md` into `agents/`, add a row with
  its source + commit SHA to `AGENTS_SOURCES.md`.
- **Add a command/skill:** cherry-pick from
  [qdhenry/Claude-Command-Suite](https://github.com/qdhenry/Claude-Command-Suite)
  into `skills/`, record it in `skills/SOURCES.md`.
- **Update a pinned asset:** re-fetch at a newer commit, replace the file,
  bump the SHA in the relevant `SOURCES.md`.
- **Per-project memory:** copy `templates/CLAUDE.project.md` to a repo's
  `./CLAUDE.md` and fill it in. Codebase-specific facts belong there, not
  global.

Each addition should name the concrete pain it removes.

## Releasing the Claude Code plugin

Tagged releases, not rolling — a plain `/plugin marketplace add` tracks the
default branch, so cutting a release is what gives anyone who wants to pin a
version something to point at:

```bash
# 1. bump the version in .claude-plugin/plugin.json
# 2. tag + push (validates plugin.json and the marketplace entry agree)
claude plugin tag --push -m "addit-harness %s"
# 3. publish release notes, using the tag claude plugin tag just created
gh release create addit-harness--v<version> --notes "..."
```

`claude plugin tag` creates an `addit-harness--v<version>` tag (not a bare
`vX.Y.Z`) and refuses a dirty working tree or a duplicate tag unless
`--force`; pass `--dry-run` to preview first.

**Versioning is manual, not tag-derived.** `plugin.json`'s `version` field is
the source of truth — `claude plugin tag` reads it and creates a matching
git tag (and errors if `plugin.json` and the marketplace entry disagree); it
does not go the other direction and infer a version from existing tags. So
step 1 above (bump `version` by hand) always comes first.

The [`release.yml` workflow](https://github.com/addit-digital/addit-harness/blob/main/.github/workflows/release.yml)
runs this exact sequence in CI — trigger it with `workflow_dispatch` instead
of running the commands locally. See the [Changelog](../changelog/) for what
that produces.

## Next

- [Roadmap](../roadmap/) — larger planned work, including native plugin
  packaging for the other three tools.
- [Concepts](../concepts/) — the curation philosophy behind "vendor, don't
  hand-roll."
