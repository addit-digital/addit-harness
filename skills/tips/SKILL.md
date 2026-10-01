---
name: tips
description: Print the short addit-harness guide (five tips). Run only when the user asks for it.
user-invocable: true
disable-model-invocation: true
---

# addit-harness tips

Print the five tips below to the user exactly as written, with no preamble and no commentary.

1. **Bigger than a small fix?** `/addit-harness:dev-flow <what to build or fix>` investigates, designs, and stops for your OK before writing code. For small fixes, just ask.
2. **You approve the plan.** dev-flow shows the plan and waits. Say yes to build it, or say what to change. Nothing is implemented until you approve.
3. **Docs land in your repo** under `docs/work/<date>-<name>/` (plans/, solutions/, reports). Open them in your IDE's Markdown preview to see the diagrams.
4. **Specialists use a prefix:** `@addit-harness:code-reviewer`, `@addit-harness:ux-designer`, and others. In a Go repo, run `/addit-harness:go-conventions` once. For React UI, run `/addit-harness:design-conventions`.
5. **Telemetry is off, and local only.** Turn on `telemetry_local` in `/config`, then run `/addit-harness:telemetry-export`. Docs: https://tools.addit.digital/harness/docs/getting-started/
