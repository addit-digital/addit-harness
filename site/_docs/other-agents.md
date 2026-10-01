---
title: Other coding agents
description: addit-harness supports Claude Code only; Cursor, Kiro and Codex CLI support and install.sh were removed.
nav_exclude: true
sitemap: false
---

addit-harness supports Claude Code only. Cursor, Kiro and Codex CLI are no
longer targeted, and `install.sh` has been removed.

Install it as a Claude Code plugin:

```
/plugin marketplace add addit-digital/addit-harness
/plugin install addit-harness@addit
/addit-harness:setup
```

See [Getting started](../getting-started/) for details and
[Migrating from `install.sh`](../getting-started/#migrating-from-installsh).

Config you already synced into another tool keeps working but no longer
updates. To keep using the old installer, pin tag `addit-harness--v0.3.0`, the
last release that shipped `install.sh`.
