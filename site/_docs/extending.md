---
title: Extending
description: How to add a language rule, agent or skill to addit-harness, and how a release is cut from CHANGELOG.md.
nav_order: 10
nav_group: Guides
---

## Add to the config

- **Add a language rule:** drop a lean `rules/<lang>.md` with `paths:`
  frontmatter (Tier 1) and, if it needs depth, topic files under
  `references/<lang>/` it points to (Tier 2). Follow the Go and Java layout: a
  short contract table with ids and sources in the rule, one topic file per
  concern, every rule citing a source or marked `harness default`.
- **Override a convention in one project:** Go reads `.claude/go-conventions.md`
  (generate it with `/go-conventions`; `# OVERRIDE: G-<TOPIC>-n <reason>` replaces a
  topic rule, never G-1..G-8 or G-10). Java has no per-project file: your
  Checkstyle/PMD config sets J-12's numbers and your formatter replaces the
  formatting rules. For frontend code, your ESLint config or `CLAUDE.md` may
  tighten an FC limit, never loosen it.
- **Vendor another subagent:** copy the `.md` into `agents/`, add a row with
  its source + commit SHA to `AGENTS_SOURCES.md`, and give it an explicit
  `tools:` list (an agent without one loads every MCP tool schema on its first
  turn).
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
# 1. bump the version in .claude-plugin/plugin.json, and in CHANGELOG.md
#    rename "## [Unreleased]" to "## [<version>] - <YYYY-MM-DD>" and add a
#    new empty "## [Unreleased]" above it
# 2. tag + push (validates plugin.json and the marketplace entry agree)
claude plugin tag --push -m "addit-harness %s"
# 3. publish the matching CHANGELOG.md section as the release notes
.github/scripts/changelog-section.sh <version> > notes.md
gh release create addit-harness--v<version> --notes-file notes.md
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
runs the bump, tag and release steps in CI — trigger it with
`workflow_dispatch` instead of running the commands locally. It uses the
`CHANGELOG.md` section for the new version as the release body, falls back to
the `[Unreleased]` section if you have not renamed it yet, and to GitHub's
generated notes if both are empty. It does not edit `CHANGELOG.md` itself. See
the [Changelog](../changelog/) for what that produces.

## Next

- [Roadmap](../roadmap/) — larger planned work.
- [Concepts](../concepts/) — the curation philosophy behind "vendor, don't
  hand-roll."
