---
title: Privacy Policy
description: How the addit-harness plugin handles data. It sends nothing to us; an optional, off-by-default telemetry log stays on your machine.
permalink: /privacy/
nav_exclude: true
---

**Last updated: 1 October 2026**

This Privacy Policy explains how the `addit-harness` Claude Code plugin
("addit-harness", "the plugin") handles data. It is published by addit digital
("we", "us"), the maker of addit-harness and other developer tools.

The short version: **addit-harness sends nothing to us or to anyone.** It has no
server, no database, and no analytics. One optional feature, off by default,
keeps a metadata-only log on your own machine; it is described under
[Optional local telemetry](#optional-local-telemetry-off-by-default). The only
exception is a publish you explicitly confirm, also described there. Everything
the plugin does runs locally, inside your own Claude Code session, on your own
machine, using your own Anthropic account. The rest of this page explains that
in detail so you can verify it before you install.

## What addit-harness is

addit-harness is a plugin for [Claude Code](https://www.anthropic.com/claude-code).
It is a git-distributed bundle of configuration files, subagent definitions,
skills, commands, and engineering rules. You install it from inside Claude Code
with `/plugin install addit-harness@addit`. Once installed, it changes how
Claude Code behaves in your sessions — it adds specialised subagents, workflows,
and conventions. It is not a service you sign into and it is not an application
that runs on its own.

The full source is public and MIT-licensed at
[github.com/addit-digital/addit-harness](https://github.com/addit-digital/addit-harness).
You can read every file it ships before you install it.

## Data we collect

**None.** We receive no data from the plugin.

addit-harness has no backend of any kind. It does not:

- send or transmit any data to us or to anyone;
- include analytics, tracking, or "phone-home" code, and we never receive an
  identifier of any kind;
- read your source code, prompts, or files and send them anywhere.

There is no account to create and no data for us to hold, because we operate no
system that receives data from the plugin. The plugin runs scripts in four
hooks, and none of them makes a network request:

- **Setup-version check** (session start): reads the plugin's own files and the
  version marker that `/addit-harness:setup` wrote on your machine, hashes the
  plugin files locally, and shows a reminder if they changed. The first time
  you start an interactive terminal session after install, it also shows a one-line
  welcome and creates an empty marker file, `onboarding/welcome-v1`, in the
  plugin's data folder so the welcome appears only once. The marker is local,
  holds nothing, is never sent anywhere, and is deleted when you uninstall.
- **`dev-flow-implement` gate**: reads the work item's `plan.md` and hashes it
  locally with `shasum` to confirm the plan you approved is the plan being
  implemented.
- **Frontend check**: reads the file just edited and counts its lines. Only when
  you set ADDIT_FE_GATE=eslint does it also run your project's own locally
  installed ESLint and config.
- **Local telemetry** (runs its script only when you turn it on): writes the
  local log described [below](#optional-local-telemetry-off-by-default),
  including the verdicts and counts of the other hooks. It sends nothing.

## How your data is actually processed when you use the plugin

When you use Claude Code with addit-harness installed, your prompts and any
files Claude Code reads are processed by **Claude Code and Anthropic's own
systems**, using your own Anthropic account or subscription. That processing is
governed by Anthropic's own privacy policy, not by us:

- [Anthropic Privacy Policy](https://www.anthropic.com/legal/privacy)

addit-harness sits on top of Claude Code as configuration. It adds no data
collection that leaves your machine (the optional local log is described
below), and it does not change what Anthropic collects or how. Whatever data
handling happens is between you and Anthropic.

## Optional local telemetry (off by default)

If you turn on the `telemetry_local` option in `/config`, addit-harness appends
one line per event to a log folder on your own machine,
`~/.claude/plugins/data/<plugin-id>/telemetry/`. While the option is off, the
plugin writes nothing there.

**What a line records:**

- which addit-harness agents, skills, commands, dev-flow workflows and gates ran,
  and how they ended;
- counts and sizes (characters, lines, diagrams), the kind of document written
  (plan, solution, report and so on), the context size Claude Code reports when
  a session resumes, and gate verdicts and the results of the other hooks
  (frontend line-cap findings, setup drift state);
- the names of the standard instruction files (`CLAUDE.md`, `AGENTS.md`) and of
  the plugin's own rules that were loaded, with their sizes;
- timestamps, and the random session, agent and workflow-run identifiers that
  Claude Code itself assigns;
- pseudonymous salted hashes of your project folder path, of the paths of
  documents written under a `docs/` folder, and of dev-flow work-item names. The
  salt is a random value stored only on your machine. These hashes are
  pseudonymous, not anonymous: anyone who holds both the log and the salt can
  test a guess against them.

To count lines, diagrams and headings, the plugin reads Markdown documents that
Claude Code writes under a `docs/` folder and keeps only those numbers.

**What it never records:** prompts, responses, code, file contents, the names or
paths of your own files and folders, command lines, error text, branch or
repository names, or account, email or organisation details. Any name that is
not one of addit-harness's own components is recorded as "other".

**Where it goes:** nowhere, unless you publish a summary as described
below. The plugin opens no network connection and never
transmits the log. Files are removed automatically after 90 days (checked when a
session starts), and the folder is capped at 100 MB. To delete the log yourself,
turn the option off and delete the folder. Uninstalling the plugin deletes the
folder by default, unless you uninstall with `--keep-data`.

**Summary page and optional publish:** the `/addit-harness:telemetry-export`
command, which you run yourself, builds a summary page (`data.json` and an
offline `report.html`) in an `export/` folder next to the log. Those files stay
on your machine and contain only the same metadata, including pseudonymous
hashes in the per-session rows. Only if you explicitly answer yes when the
command asks does it publish aggregated numbers, with no per-session rows, ids
or hashes, as a private page (an Artifact) on claude.ai under your Anthropic
account. That upload goes to Anthropic's hosted service through Claude Code's
own Artifact tool, not through a connection opened by the plugin, and that page
is governed by Anthropic's terms. A yes is not remembered; the command asks
every time. If the Artifact tool is not available to you, nothing is published.

## Third-party integrations you configure yourself

Some subagents in addit-harness (for example the cloud and DevOps agents) can
optionally work with external tools — such as the GitHub CLI, Jira, a Postgres
database, or the AWS, Azure, and GCP command-line tools — through
[MCP](https://modelcontextprotocol.io/) servers or CLIs.

These integrations are **entirely yours**. You install them, you configure them,
and you supply your own credentials, which stay on your own machine. addit-harness
ships an example configuration file (`mcp.example.json`) as a disabled reference
catalogue; nothing in it is enabled or connected by default. When you connect
one of these tools, any data that flows does so directly between your machine and
that third-party service, under that service's own terms and privacy policy. **We
never see, receive, or handle that data or those credentials.**

## Cookies and tracking

The plugin uses no cookies and no tracking technologies, because it has no web
interface and no server.

Our documentation website at
[tools.addit.digital](https://tools.addit.digital) is a separate, static site.
If it uses any cookies or analytics, that is disclosed on the site itself and is
not part of the plugin.

## Data sharing and sale

We do not share, sell, rent, or disclose your data — because we do not receive
any. There is nothing for us to share or sell.

## Your rights

Privacy laws such as the GDPR and the CCPA give people rights to access,
correct, delete, and port their personal data. We honour the spirit of these
rights fully: because we operate no system that receives data from the plugin,
there is no data about you for us to access, correct, delete, or export on your
behalf. The optional local log lives on your machine, under your control: you
can read or delete it at any time.

For the data that *is* processed when you use Claude Code, direct any such
requests to Anthropic under
[their privacy policy](https://www.anthropic.com/legal/privacy). For data held
by any third-party tool you connected yourself, direct requests to that provider.

## Children

addit-harness is a developer tool that sends no data to us and is not directed
at children.

## Changes to this policy

If we change how the plugin handles data, we will update this page and change the
"Last updated" date above. Because the plugin's source is public, any change to
its behaviour is also visible in the
[git history](https://github.com/addit-digital/addit-harness). If a future
version were ever to send data off your machine, we would say so here clearly and
prominently before that version shipped.

## Contact

Questions about this policy or about how addit-harness handles data:

- Email: [privacy@addit.digital](mailto:privacy@addit.digital)
- Issues: [github.com/addit-digital/addit-harness/issues](https://github.com/addit-digital/addit-harness/issues)

---

*addit-harness is published by addit digital. This policy covers the plugin
only. Claude Code and Anthropic's services are governed by
[Anthropic's own terms and privacy policy](https://www.anthropic.com/legal/privacy).*
