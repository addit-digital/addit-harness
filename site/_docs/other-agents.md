---
title: Claude Code only
description: addit-harness supports Claude Code only; the old multi-tool installer (install.sh) was removed.
nav_exclude: true
sitemap: false
---

addit-harness supports Claude Code only, as a plugin, and `install.sh` has been
removed.

Install it:

```
/plugin marketplace add addit-digital/addit-harness
/plugin install addit-harness@addit
/addit-harness:setup
```

See [Getting started](../getting-started/) for details and
[Migrating from `install.sh`](../getting-started/#migrating-from-installsh).

Config you already synced with the old installer keeps working but no longer
updates. To keep using it, pin tag `addit-harness--v0.3.0`, the last release
that shipped `install.sh`.
