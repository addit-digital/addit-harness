---
title: Enabling MCP
nav_order: 6
nav_group: Reference
---

Both Atlassian and database MCP are intentionally **off** by default.
`mcp.example.json` is a disabled, human-curated catalogue by design — pick an
entry, fill in credentials by hand, and paste it into the tool's real MCP
config yourself. MCP is **not** auto-synced for any tool (`install.sh`'s
footer prints the right target path per tool after every run).

<div class="docs-toc" markdown="1">
**On this page**
- [How to enable any entry](#how-to-enable-any-entry)
- [Figma](#figma-official-plugin--recommended)
- [Atlassian Cloud](#atlassian-cloud)
- [Atlassian Data Center](#atlassian-data-center)
- [Postgres](#postgres)
- [MySQL](#mysql)
- [Cloud / infra](#cloud--infra)
</div>

## How to enable any entry

1. Open `mcp.example.json` and copy the entry you want into
   `~/.claude/.mcp.json` (under an `mcpServers` object).
2. Put secrets/connection strings in `~/.claude/mcp.local.json` (gitignored)
   — never commit them.
3. Restart Claude Code; check with `/mcp`.

## Figma (official plugin — recommended)

Run `./install.sh --plugins` (already adds `figma@claude-plugins-official`).
Open any Figma file → authorise Claude Code in the plugin panel → OAuth
completes → `/mcp` confirms the Figma server is connected.

Write-to-canvas is in beta and will become usage-based/paid — confirm your
plan covers cost before running `@addit-harness:figma-designer` for large
tasks. See `mcp.example.json` → `figma_OFFICIAL` for the manual MCP-only path
and `figma_COMMUNITY_ALTERNATIVE` for the free-plan plugin-bridge option.

## Atlassian Cloud

```bash
claude mcp add --transport http atlassian https://mcp.atlassian.com/v1/mcp
```

Official Rovo server, OAuth.

## Atlassian Data Center

Community [`sooperset/mcp-atlassian`](https://github.com/sooperset/mcp-atlassian) (token/PAT).

## Postgres

[`crystaldba/postgres-mcp`](https://github.com/crystaldba/postgres-mcp) (read-only by default).

## MySQL

[`benborla/mcp-server-mysql`](https://github.com/benborla/mcp-server-mysql) or
[`designcomputer/mysql_mcp_server`](https://github.com/designcomputer/mysql_mcp_server).

## Cloud / infra

Used by `@addit-harness:cloud-architect` / `@addit-harness:devops-engineer`:
official servers for AWS (`awslabs/mcp`), Azure (`@azure/mcp`), DigitalOcean
(`digitalocean-labs/mcp-digitalocean`), Terraform
(`hashicorp/terraform-mcp-server`, via Docker), Kubernetes
(`kubernetes-mcp-server`), Docker (`docker mcp gateway`, built into Docker
Desktop's MCP Toolkit), and Cloudflare (`cloudflare/mcp` — WAF, DDoS, Zero
Trust, DNS, CDN; OAuth) — see `mcp.example.json`.

Google Cloud has no unified official MCP server yet; both agents fall back
to the `gcloud` CLI directly.

## Next

- [Use cases](../use-cases/#connect-jira--a-database) — where MCP fits into a
  real workflow.
- [Subagents](../subagents/#cloud-architect) — the agents that prefer these
  servers when connected.
