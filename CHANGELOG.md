# Changelog

All notable changes to addit-harness are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow
[Semantic Versioning](https://semver.org/). Releases up to v0.3.0 are described
only on [GitHub Releases](https://github.com/addit-digital/addit-harness/releases).

## [Unreleased]

### Fixed

- Typing `/addit-harness` listed every skill twice. The plugin shipped a thin
  `commands/<name>.md` next to each skill (a workaround for
  [anthropics/claude-code#18949](https://github.com/anthropics/claude-code/issues/18949)),
  and current Claude Code shows a command and a skill with the same name as two entries
  ([#88050](https://github.com/anthropics/claude-code/issues/88050)). The `commands/`
  folder is removed; the skills are the slash commands, unchanged. A test now fails if a
  command shares a name with a skill.

## [0.4.0] - 2026-10-01

### Added

- `/dev-flow` triage: one read-only `@task-triager` agent (new, `haiku`) reports facts
  about the request and a script scores it as `light`, `standard` or `deep`. You
  confirm or change the tier at a tier gate, or pass `--tier`. The tier sets
  investigation, UX, design rounds, reviewers, effort and severity floors. Worst-case
  agent calls for a whole run are 18 / 46 / 50 (hard caps, mock-asserted).
- `/dev-flow` intake: at `standard` and `deep`, `@product-owner` asks at most a few
  questions that change the approach, then writes a one-page brief
  (`docs/work/<slug>/specs/brief.md`). A solution proposed in the request is moved to
  `specs/owner-proposal.md` and scored later as candidate "Owner".
- Solution method for every architect: at least three structurally different
  candidates (one unconventional), cited prior art, numbers, a pre-mortem, a weighted
  comparison and kill criteria. Your proposed approach is only scored at the
  comparison step. `@architect-reviewer` reviews as a red team and can name a better
  alternative. At `deep`, three explorers design in parallel and a synthesizer picks.
- ADRs are recorded after you approve the plan, from the plan's `ADR: candidate`
  lines.
- Doc protocol (`references/doc-protocol.md`): templates per document type, length
  ceilings per tier, Observed/Inferred/Unknown labels on claims, edit-in-place
  revisions with a short log, and one mermaid diagram per concept.
- Frontend Implementation Contract FC-1..FC-10 (`rules/typescript-frontend.md`),
  followed by `@frontend-developer` and measured by `@code-reviewer`.
- Advisory frontend hook: after each edit of a frontend `.ts`/`.tsx` file it notes
  files over 150 or 250 non-blank lines. It never blocks. `ADDIT_FE_GATE=eslint`
  also runs your project's ESLint; `ADDIT_FE_GATE=0` turns it off.
- Go and Java conventions as cited topic files with rule ids: `rules/go.md`
  (G-1..G-10, 11 topics, Uber guide where it does not collide with the owner's
  approach) and `rules/java.md` (J-1..J-14, 12 topics). Go projects can override a
  topic rule in `.claude/go-conventions.md`.
- `/addit-harness:setup --plugins` installs the plugins and marketplaces declared in
  `settings.json`.
- Optional local telemetry, off by default (`telemetry_local` in `/config`): a
  metadata-only log on your machine, never sent anywhere by the plugin.
  `/addit-harness:telemetry-export` builds `data.json` and an offline `report.html`,
  and publishes aggregated KPIs as a private claude.ai Artifact only if you answer
  yes.
- Mock test harness for the dev-flow workflow scripts (`tests/workflows/`) and unit
  tests for the telemetry writer and exporter (`tests/telemetry/`).
- `CHANGELOG.md`; the release workflow fails if `## [Unreleased]` is empty, cuts it to
  `## [<version>] - <date>` in the bump commit (with a fresh empty `Unreleased` above)
  and uses that section as the release notes, with no generated-notes fallback.
  Fixture tests for both scripts live in `tests/release/`.
- `/dev-flow` progress lines in the built-in `/workflows` view: a start line with
  tier and track, one line per review round with its count at or above the tier's floor, each gate
  verdict (`gate qa first` marks a QA failure that gets a fix cycle), and a `HALT` line with a fixed reason. They carry metadata only: no request
  text, agent output, error messages or file paths (a scope breach logs a count; the
  paths stay in the run's result). `tests/workflows/log-contract.mjs` checks the
  format, including every `HALT` line, on every mock scenario run.
- `/dev-flow` lifecycle task list: six tasks (`Triage`, `Design + plan`,
  `Approve plan`, `Implement + review`, `QA`, `Commit`) kept current at each step,
  when the task tools are available. Not yet checked in a live terminal.
- First run: a one-time welcome line on the first interactive terminal startup after
  install (not the desktop app or IDE integrations), shown to you as a hook message and not added to the model's context. An
  empty local marker, `onboarding/welcome-v1` in the plugin data folder, keeps it
  to once. New `/addit-harness:tips` command (user-invoked only) prints five short
  tips, and setup ends with a next-steps line.

### Changed

- **Breaking:** `@addit-harness:feature-investigator` is renamed to
  `@addit-harness:product-owner`, and the old name no longer resolves. The new agent
  describes the problem only and never proposes a solution.
- `/dev-flow` review: findings are tagged `blocking`, `major` or `minor` and the
  script applies the tier's floor. After the last fix round a verdict-only
  `@code-reviewer` pass judges the final code.
- `/dev-flow` QA runs once, after review. Only a QA failure triggers one fix cycle
  and a second, last QA run.
- `/dev-flow` at `light`: if the first review finds the change on a risk surface the
  plan did not list, or past a file-count band, the run stops and re-gates at
  `standard`.
- `/dev-flow` plan approval is enforced by a hook: implementation starts only if
  `plan.md` carries the approval marker and still matches the hash taken at approval.
- One failed agent call no longer kills a `/dev-flow` run; it is logged. A developer
  that returns nothing stops the run as `implement-failed` instead of reporting an
  empty diff as clean.
- Every agent has an explicit `tools:` list. For the four architect and design agents
  this cut first-turn context from about 33k to about 17k tokens in a controlled
  probe.
- `/addit-harness:setup` merges `settings.json` instead of replacing it: your
  `hooks`, `env`, `statusLine` and plugin choices are kept, `permissions` lists are
  unioned, and a backup is taken first.
- Setup's `settings.json` template now sets `env.CLAUDE_CODE_ENABLE_TODO_TOOLS=1`,
  because Claude Code's task tools are off by default on newer models. `env` is
  merged key by key with your values winning, so a value you already set is kept.
  The per-turn context cost of the task tools has not been measured.
- Plugin document locations (`docs/work/<slug>/...`, `docs/adr/`, `docs/legal/`) apply
  even when a project has its own folders. Ticket-id slugs are still allowed; an
  existing slug folder from another work item gets a `-2` suffix instead of being
  overwritten.

### Removed

- **Breaking:** `install.sh`, `sync_tools.py` and `tools.config.json`. addit-harness
  supports Claude Code only, as a plugin: `/plugin marketplace add
  addit-digital/addit-harness`, `/plugin install addit-harness@addit`, then
  `/addit-harness:setup`. Cursor, Kiro and Codex CLI are no longer supported; config
  already synced into them keeps working but no longer updates. Tag
  `addit-harness--v0.3.0` is the last release with `install.sh`.
- `references/java/java-best-practices.md` and `references/go/app-erp-conventions.md`,
  replaced by topic files. Setup removes them on re-sync only if unchanged; an edited
  copy is backed up and kept.
- Copied template text in vendored agents that named agents which do not exist and
  quoted made-up metrics.

### Fixed

- Setup no longer drops your own `permissions` rules on re-sync.
- Setup warns when your `settings.json` has `env`, `enabledPlugins` or
  `extraKnownMarketplaces` as something other than an object and the template's value
  replaces it (your original stays in the backup); it did so silently before.
- `/dev-flow`: two tracks in the same repo fix sequentially; reviewer
  `touchedFiles` are keyed by repo, and missing ones count as unknown scope; the
  owner-proposal end marker is stripped fully; triage counts root-level files as one
  directory.
- Telemetry export rejects impossible timestamps without aborting, and reports
  skipped invalid lines.
- The `telemetry_local` option description in `/config` and the README now link to
  the privacy policy at its published address, `/harness/privacy/`.

### Security

- Every hook that runs a script is now listed in the privacy policy, with what it
  reads. None of them makes a network request.
- The requester's proposed solution reaches the design workflow only as quoted,
  untrusted data.
