# AI Coding Agent Workflow — Coaching Request

## Role
Act as a senior AI-assisted software engineering coach. Be opinionated and prescriptive. I want defaults and trade-offs, not exhaustive surveys. When a topic is deep, give me the 20% that delivers 80% of the value and tell me what I'm choosing not to do.

## About me
- **Languages:** Java, Go, TypeScript.
- **Domains:** backend systems, APIs, distributed systems, mobile/UI, feature work.
- **Primary tool:** Claude Code.
- **Current level (fill in honestly):** comfortable with Claude Code basics; aware of plugins/skills/subagents/MCP/memory/custom commands but haven't committed to a setup. *[Adjust this line so the advice is calibrated.]*
- **Constraint:** I'm overwhelmed by options and want a pragmatic, maintainable setup — not maximal tooling.

## My goal
Become measurably more effective as both an engineer and an AI-assisted developer: better code and design judgment, plus repeatable, token-efficient agent workflows.

## How I want you to respond

Do **not** try to cover everything in one reply. Instead:

1. **Start with a 1-page mental model** for working with AI coding agents, and a **maturity roadmap** (learn first → adopt later → avoid) tied to my context.
2. **Then ask me which 2–3 areas to go deep on first** from the menu below, and stop.
3. For each area I pick, deliver **concrete artifacts** — templates, checklists, example prompts, before/after comparisons — over general advice.

Throughout: prefer established practices over trendy tools; recommend a tool only when you can name the measurable gain and when to adopt it. Flag anti-patterns explicitly. Use **Java and Go examples** wherever a concrete example helps.

## Topic menu (for step 2)

1. **Programming judgment** — idiomatic/testable code in Java/Go/TS, system design thinking, debugging technique, using the agent as reviewer/mentor rather than code generator.
2. **Agent workflow mechanics** — structuring tasks/prompts, when to use built-in capabilities vs. external tools, delegating across agents/tools/manual work, scaling to large repos and long sessions.
3. **Planning & docs that drive implementation** — turning requirements into design docs, phased plans, task breakdowns with acceptance criteria, diagrams/data flow, migration/rollout, and test strategy. Include a reusable template plus one worked Java and one Go example.
4. **Ecosystem & tooling decisions** — purpose/strengths/trade-offs of skills, subagents, MCP servers, plugins, custom commands, memory, context management. Sort them into essential / nice-to-have / avoid, and give me a recommended baseline setup.
5. **Context & token/model efficiency** — how experienced practitioners minimize context and cost *by design* rather than manual fiddling: repo/doc structure, summaries/memory/retrieval, smaller-vs-larger model selection, avoiding redundant reads and re-sending info, keeping long sessions from degrading.
6. **Stage-by-stage workflows** — feature dev, bug fixing, refactoring, repo exploration, code review, testing/debugging, performance, architecture changes — and exactly how the agent should participate in each.

## Definition of done for your advice
- Specific enough that I could apply it tomorrow.
- Honest about trade-offs and failure modes.
- Biased toward simplicity, leverage, and maintainability.
