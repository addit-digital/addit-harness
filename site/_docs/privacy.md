---
title: Privacy Policy
permalink: /privacy/
nav_exclude: true
---

**Last updated: 11 July 2026**

This Privacy Policy explains how the `addit-harness` Claude Code plugin
("addit-harness", "the plugin") handles data. It is published by addit digital
("we", "us"), the maker of addit-harness and other developer tools.

The short version: **addit-harness collects nothing.** It has no server, no
database, no analytics, and no telemetry. It never sends any data to us or to
any third party. Everything it does runs locally, inside your own Claude Code
session, on your own machine, using your own Anthropic account. The rest of
this page explains that in detail so you can verify it before you install.

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

**None.**

addit-harness has no backend of any kind. It does not:

- collect, store, or transmit personal data;
- include any analytics, tracking, telemetry, or "phone-home" code;
- assign you an identifier or track usage across sessions;
- read your source code, prompts, or files and send them anywhere.

There is no account to create and no data for us to hold, because we operate no
system that receives data from the plugin. Its hooks and setup scripts read and
write only local files on your own machine and make no network requests.

## How your data is actually processed when you use the plugin

When you use Claude Code with addit-harness installed, your prompts and any
files Claude Code reads are processed by **Claude Code and Anthropic's own
systems**, using your own Anthropic account or subscription. That processing is
governed by Anthropic's own privacy policy, not by us:

- [Anthropic Privacy Policy](https://www.anthropic.com/legal/privacy)

addit-harness sits on top of Claude Code as configuration. It does not add any
data-collection layer of its own, and it does not change what Anthropic
collects or how. Whatever data handling happens is between you and Anthropic.

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

We do not share, sell, rent, or disclose your data — because we do not collect
any. There is nothing for us to share or sell.

## Your rights

Privacy laws such as the GDPR and the CCPA give people rights to access,
correct, delete, and port their personal data. We honour the spirit of these
rights fully: because addit-harness holds no personal data about you and we
operate no system that receives any, there is no data for us to access,
correct, delete, or export on your behalf.

For the data that *is* processed when you use Claude Code, direct any such
requests to Anthropic under
[their privacy policy](https://www.anthropic.com/legal/privacy). For data held
by any third-party tool you connected yourself, direct requests to that provider.

## Children

addit-harness is a developer tool with no data collection and is not directed at
children.

## Changes to this policy

If we change how the plugin handles data, we will update this page and change the
"Last updated" date above. Because the plugin's source is public, any change to
its behaviour is also visible in the
[git history](https://github.com/addit-digital/addit-harness). If a future
version were ever to collect data, we would say so here clearly and prominently
before that version shipped.

## Contact

Questions about this policy or about how addit-harness handles data:

- Email: [privacy@addit.digital](mailto:privacy@addit.digital)
- Issues: [github.com/addit-digital/addit-harness/issues](https://github.com/addit-digital/addit-harness/issues)

---

*addit-harness is published by addit digital. This policy covers the plugin
only. Claude Code and Anthropic's services are governed by
[Anthropic's own terms and privacy policy](https://www.anthropic.com/legal/privacy).*
