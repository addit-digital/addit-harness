---
title: Other coding agents
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

See [Getting started](../getting-started/) for details.

Config you already synced into another tool keeps working but is frozen. To
keep updating it, pin commit `ebea6f3` or tag `addit-harness--v0.3.0`, the last
state that shipped `install.sh`.
