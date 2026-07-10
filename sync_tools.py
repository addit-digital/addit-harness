#!/usr/bin/env python3
"""
sync_tools.py — place canonical config into one coding agent's home directory.

Interprets tools.config.json to decide, per artifact class (baseline, rules,
references, agents, skills, mcp), whether to place a file/tree as-is or run
one of a small number of transforms (frontmatter field rename, Kiro tool-tag
remap, Codex TOML conversion). Called by install.sh once per detected/forced
tool — see docs/plans/2026-07-10-multi-tool-agent-config.md for the design.

MCP is intentionally out of scope: mcp.example.json is a disabled,
human-curated catalogue for manual copy-paste (see its own "_README" entry),
not a live server config to sync — see the "MCP" note near the bottom.

Usage:
  sync_tools.py <tool> --repo <path> --home <path> --config <path>
                 --backup-dir <path> [--link]
"""
import argparse
import glob
import json
import os
import re
import shutil
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n?(.*)\Z", re.DOTALL)
LINE_RE = re.compile(r"^(\w[\w-]*):\s*(.*)$")


# ---------------------------------------------------------------------------
# Frontmatter parsing / serialization (small hand-rolled subset — our
# frontmatter is always flat key: value pairs, values are quoted strings,
# bare scalars, or JSON-style arrays; no nested maps, no multi-line values).
# ---------------------------------------------------------------------------

def parse_scalar(raw):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        return json.loads(raw)
    if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
        return raw[1:-1]
    return raw


def split_frontmatter(text):
    """Returns (ordered_fields, body). ordered_fields is a list of (key, value)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return [], text
    fm_block, body = m.group(1), m.group(2)
    fields = []
    for line in fm_block.split("\n"):
        if not line.strip():
            continue
        lm = LINE_RE.match(line)
        if lm:
            fields.append((lm.group(1), parse_scalar(lm.group(2))))
    return fields, body


SIMPLE_SCALAR_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")


def dump_scalar(value):
    if isinstance(value, list):
        return "[" + ", ".join(json.dumps(v, ensure_ascii=False) for v in value) + "]"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return value if SIMPLE_SCALAR_RE.match(value) else json.dumps(value, ensure_ascii=False)
    return str(value)


def dump_frontmatter(fields):
    lines = ["---"]
    for k, v in fields:
        lines.append("{}: {}".format(k, dump_scalar(v)))
    lines.append("---")
    return "\n".join(lines) + "\n"


def fields_get(fields, key, default=None):
    for k, v in fields:
        if k == key:
            return v
    return default


# ---------------------------------------------------------------------------
# Placement primitives (shared backup-before-overwrite behavior, mirrors
# install.sh's place_file so every tool gets the same safety net)
# ---------------------------------------------------------------------------

def backup_if_present(dest, backup_dir, home):
    if dest.exists() and not dest.is_symlink():
        rel = dest.relative_to(home)
        backup_dest = backup_dir / rel
        backup_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, backup_dest)
        print("  backed up existing {} -> {}".format(dest, backup_dest))


def place_file(src, dest, link, backup_dir, home):
    dest.parent.mkdir(parents=True, exist_ok=True)
    backup_if_present(dest, backup_dir, home)
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    if link:
        dest.symlink_to(src)
    else:
        shutil.copy2(src, dest)


def write_generated(dest, content, backup_dir, home):
    """Generated/transformed content is always a real file, never a symlink."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    backup_if_present(dest, backup_dir, home)
    dest.write_text(content, encoding="utf-8")


def place_tree(src_dir, dest_dir, link, backup_dir, home):
    if not src_dir.is_dir():
        return
    for f in sorted(src_dir.rglob("*")):
        if f.is_file():
            rel = f.relative_to(src_dir)
            place_file(f, dest_dir / rel, link, backup_dir, home)


# ---------------------------------------------------------------------------
# Baseline concat — AGENTS.md (+ rules/*.md for tools with no path-scoped
# loading) squashed into one always-on file per tool, with a frontmatter
# header added where the target format wants one.
# ---------------------------------------------------------------------------

def resolve_includes(repo, patterns):
    paths = []
    for pattern in patterns:
        if "*" in pattern:
            paths.extend(sorted(Path(p) for p in glob.glob(str(repo / pattern))))
        else:
            paths.append(repo / pattern)
    return paths


def rewrite_home_refs(body, home_alias):
    """Rewrite hardcoded ~/.claude/references/... mentions in vendored prose
    to the equivalent path under this tool's own home (Tier-1 rule bodies
    reference the Claude path directly, e.g. rules/go.md's
    '~/.claude/references/go/app-erp-conventions.md')."""
    if not home_alias:
        return body
    return body.replace("~/.claude/references/", "{}/references/".format(home_alias))


def render_include_body(path, home_alias=None):
    text = path.read_text(encoding="utf-8")
    fields, body = split_frontmatter(text)
    body = rewrite_home_refs(body.strip(), home_alias) + "\n"
    paths_val = fields_get(fields, "paths")
    if paths_val:
        # Tier-1 bodies already open with their own heading (e.g. "# Go") —
        # add only a small applicability note, don't synthesize a competing one.
        note = "_Applies to: {}_\n".format(", ".join(paths_val))
        return note + "\n" + body
    return body


def sync_baseline(repo, home, cfg, backup_dir, home_alias=None):
    dest = home / cfg["dest"]
    sections = [render_include_body(p, home_alias) for p in resolve_includes(repo, cfg["include"])]
    content = "\n\n".join(s.rstrip() for s in sections) + "\n"
    frontmatter = cfg.get("frontmatter")
    if frontmatter:
        content = dump_frontmatter(list(frontmatter.items())) + "\n" + content
    write_generated(dest, content, backup_dir, home)
    print("  wrote baseline -> {}".format(dest))


def sync_baseline_claude(repo, home, cfg, link, backup_dir):
    # CLAUDE.md is already the 2-line @import pointer in the repo (@AGENTS.md +
    # @rules/engineering-loop.md) — passthrough, plus AGENTS.md itself so the
    # @AGENTS.md import has something to resolve against.
    place_file(repo / "CLAUDE.md", home / cfg["dest"], link, backup_dir, home)
    place_file(repo / "AGENTS.md", home / "AGENTS.md", link, backup_dir, home)
    print("  placed CLAUDE.md + AGENTS.md -> {}".format(home))


# ---------------------------------------------------------------------------
# Rules — Tier-1 pointer files. Passthrough for claude; frontmatter key
# rename (+ optional array->comma join) for cursor/kiro; inlined with the
# matching Tier-2 reference for copilot (Phase 2, not implemented here).
# ---------------------------------------------------------------------------

def sync_rules_passthrough(repo, home, cfg, link, backup_dir):
    place_tree(repo / "rules", home / cfg["dest"], link, backup_dir, home)


def sync_rules_frontmatter_rename(repo, home, cfg, backup_dir, home_alias=None):
    src_dir = repo / "rules"
    dest_dir = home / cfg["dest"]
    ext = cfg.get("ext", "md")
    fm_map = cfg.get("frontmatterMap", {})
    extra_fm = cfg.get("frontmatter", {})
    join_arrays = cfg.get("joinArrays", False)
    for f in sorted(src_dir.glob("*.md")):
        if f.name == "engineering-loop.md":
            continue  # no paths: frontmatter to remap — it's part of baseline
        text = f.read_text(encoding="utf-8")
        fields, body = split_frontmatter(text)
        new_fields = []
        for k, v in fields:
            new_key = fm_map.get(k, k)
            if isinstance(v, list) and join_arrays:
                v = ", ".join(v)
            new_fields.append((new_key, v))
        for k, v in extra_fm.items():
            new_fields.append((k, v))
        out = dump_frontmatter(new_fields) + "\n" + rewrite_home_refs(body, home_alias)
        dest = dest_dir / (f.stem + "." + ext)
        write_generated(dest, out, backup_dir, home)
    print("  wrote rules -> {}".format(dest_dir))


# ---------------------------------------------------------------------------
# Agents — passthrough (claude), skip (cursor: reads .claude/agents natively),
# Kiro tool-tag remap, Codex TOML conversion.
# ---------------------------------------------------------------------------

def remap_tools(tools_csv, tool_map, drop_unmapped):
    names = [t.strip() for t in tools_csv.split(",") if t.strip()]
    out = []
    for name in names:
        if name in drop_unmapped:
            continue
        mapped = tool_map.get(name)
        if mapped is None:
            # exact match failed — try glob-style keys (e.g. mcp__plugin_figma_figma__*)
            for pattern, target in tool_map.items():
                if "*" in pattern and re.fullmatch(pattern.replace("*", ".*"), name):
                    mapped = target
                    break
        if mapped and mapped not in out:
            out.append(mapped)
    return out


def list_agent_files(src_dir):
    return sorted(src_dir.glob("*.md"))


def sync_agents_kiro(repo, home, cfg, backup_dir):
    src_dir = repo / "agents"
    dest_dir = home / cfg["dest"]
    tool_map = cfg["toolMap"]
    drop_unmapped = set(cfg.get("dropUnmapped", []))
    for f in list_agent_files(src_dir):
        text = f.read_text(encoding="utf-8")
        fields, body = split_frontmatter(text)
        tools_csv = fields_get(fields, "tools")
        new_fields = [(k, v) for k, v in fields if k != "tools"]
        if tools_csv:
            new_fields.append(("tools", remap_tools(tools_csv, tool_map, drop_unmapped)))
        else:
            new_fields.append(("tools", ["*"]))  # no restriction in Claude == full access
        out = dump_frontmatter(new_fields) + "\n" + body
        write_generated(dest_dir / f.name, out, backup_dir, home)
    print("  wrote {} agents -> {}".format(len(list_agent_files(src_dir)), dest_dir))


def toml_escape(s):
    return s.replace("\\", "\\\\")


def toml_string(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def toml_multiline_string(value):
    body = toml_escape(value)
    # TOML forbids three consecutive quotes inside a triple-quoted string.
    body = body.replace('"""', '\\"\\"\\"')
    return '"""\n' + body + '\n"""'


def derive_sandbox_mode(tools_csv, sandbox_rule):
    if not tools_csv:
        return sandbox_rule["then"]  # no tools: line in Claude == full access
    names = {t.strip() for t in tools_csv.split(",") if t.strip()}
    if names & set(sandbox_rule["anyOf"]):
        return sandbox_rule["then"]
    return sandbox_rule["else"]


def sync_agents_codex(repo, home, cfg, backup_dir):
    src_dir = repo / "agents"
    dest_dir = home / cfg["dest"]
    body_field = cfg["bodyField"]
    sandbox_rule = cfg["sandboxRule"]
    count = 0
    for f in list_agent_files(src_dir):
        text = f.read_text(encoding="utf-8")
        fields, body = split_frontmatter(text)
        name = fields_get(fields, "name", f.stem)
        description = fields_get(fields, "description", "")
        tools_csv = fields_get(fields, "tools")
        sandbox_mode = derive_sandbox_mode(tools_csv, sandbox_rule)
        toml_lines = [
            "name = {}".format(toml_string(name)),
            "description = {}".format(toml_string(description)),
            "sandbox_mode = {}".format(toml_string(sandbox_mode)),
            "{} = {}".format(body_field, toml_multiline_string(body.strip() + "\n")),
        ]
        dest = dest_dir / (f.stem + ".toml")
        write_generated(dest, "\n".join(toml_lines) + "\n", backup_dir, home)
        count += 1
    print("  wrote {} agents -> {}".format(count, dest_dir))


# ---------------------------------------------------------------------------
# MCP is intentionally NOT auto-synced for any tool. mcp.example.json is a
# disabled, human-curated catalogue (see its own "_README" entry) meant for
# picking one entry, filling in credentials by hand, and pasting it into the
# tool's real MCP config — it is not a live `mcpServers` block, so there is
# nothing here to place or transform automatically. install.sh prints the
# right manual paste target per tool instead (see tools.config.json's "mcp"
# entries, and each print in the install.sh footer).
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def sync_claude(repo, home, tool_cfg, args, backup_dir):
    sync_baseline_claude(repo, home, tool_cfg["baseline"], args.link, backup_dir)
    place_tree(repo / "rules", home / tool_cfg["rules"]["dest"], args.link, backup_dir, home)
    place_tree(repo / "references", home / tool_cfg["references"]["dest"], args.link, backup_dir, home)
    place_tree(repo / "agents", home / tool_cfg["agents"]["dest"], args.link, backup_dir, home)
    place_tree(repo / "skills", home / tool_cfg["skills"]["dest"], args.link, backup_dir, home)


def sync_cursor(repo, home, tool_cfg, args, backup_dir):
    home_alias = "~/.cursor"
    sync_baseline(repo, home, tool_cfg["baseline"], backup_dir, home_alias)
    sync_rules_frontmatter_rename(repo, home, tool_cfg["rules"], backup_dir, home_alias)
    place_tree(repo / "references", home / tool_cfg["references"]["dest"], args.link, backup_dir, home)
    print("  agents: skipped ({})".format(tool_cfg["agents"]["reason"]))


def sync_kiro(repo, home, tool_cfg, args, backup_dir):
    home_alias = "~/.kiro"
    sync_baseline(repo, home, tool_cfg["baseline"], backup_dir, home_alias)
    sync_rules_frontmatter_rename(repo, home, tool_cfg["rules"], backup_dir, home_alias)
    place_tree(repo / "references", home / tool_cfg["references"]["dest"], args.link, backup_dir, home)
    sync_agents_kiro(repo, home, tool_cfg["agents"], backup_dir)


def sync_codex(repo, home, tool_cfg, args, backup_dir):
    home_alias = "~/.codex"
    sync_baseline(repo, home, tool_cfg["baseline"], backup_dir, home_alias)
    place_tree(repo / "references", home / tool_cfg["references"]["dest"], args.link, backup_dir, home)
    sync_agents_codex(repo, home, tool_cfg["agents"], backup_dir)


DISPATCH = {
    "claude": sync_claude,
    "cursor": sync_cursor,
    "kiro": sync_kiro,
    "codex": sync_codex,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tool", choices=list(DISPATCH.keys()))
    ap.add_argument("--repo", required=True)
    ap.add_argument("--home", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--backup-dir", required=True)
    ap.add_argument("--link", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    home = Path(args.home).expanduser()
    backup_dir = Path(args.backup_dir).expanduser()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    tool_cfg = config[args.tool]

    home.mkdir(parents=True, exist_ok=True)
    DISPATCH[args.tool](repo, home, tool_cfg, args, backup_dir)


if __name__ == "__main__":
    main()
