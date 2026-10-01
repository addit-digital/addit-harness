#!/usr/bin/env python3
"""addit-harness local telemetry writer (opt-in, metadata only, no network).

Usage:  telemetry.py hook | gate <name> <verdict> | fc <id> <severity> <count> | setup <state>
stdin is the calling hook's JSON payload. Every record passes validate() against
hooks/telemetry-contract.json before it is written: strings must be enum members or
names from this plugin's own inventory, everything else is a count, a boolean or a
hash. There is no free-text type, so prompts, paths and code cannot be written.
Fails open: any error exits 0 silently.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ON = ("true", "True", "1")
HEX = frozenset("0123456789abcdef")
IDCH = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-")
PREFIX = "addit-harness:"
_CACHE = {}


def contract():
    if "c" not in _CACHE:
        import json
        with open(os.path.join(HERE, "telemetry-contract.json")) as f:
            _CACHE["c"] = json.load(f)
    return _CACHE["c"]


def sha256(data):
    try:
        from _sha2 import sha256 as f  # skips the ~8 ms OpenSSL load behind hashlib; same digest
    except ImportError:
        from hashlib import sha256 as f
    return f(data)


def sha(text, n):
    return sha256(text.encode("utf-8", "replace")).hexdigest()[:n]


def safe_id(v):
    v = v if isinstance(v, str) else str(v)
    return v if 1 <= len(v) <= 64 and set(v) <= IDCH else sha(v, 32)


def iso(t=None):
    t = time.time() if t is None else t
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + ".%03dZ" % (int(t * 1000) % 1000)


def _stems(sub, ext=".md"):
    try:
        return {n[:-len(ext)] for n in os.listdir(os.path.join(os.path.dirname(HERE), sub)) if n.endswith(ext)}
    except OSError:
        return set()


def _skill_dirs():
    try:
        with os.scandir(os.path.join(os.path.dirname(HERE), "skills")) as it:
            return {e.name for e in it if e.is_dir()}
    except OSError:
        return set()


def inventory(kind):
    """Names this plugin ships (agents, skills+commands, rule stems), read once per process."""
    if kind not in _CACHE:
        _CACHE[kind] = {
            "agent": lambda: _stems("agents") | set(contract()["competitors"]) | {"main", "other"},
            "skill": lambda: _skill_dirs() | _stems("commands") | {"other"},
            "rule": lambda: _stems("rules") | {"CLAUDE.md", "AGENTS.md", "other"},
        }[kind]()
    return _CACHE[kind]


def norm(kind, v):
    return v if isinstance(v, str) and v in inventory(kind) else "other"


def _is_iso(v):
    """YYYY-MM-DDTHH:MM:SS.mmmZ naming a real UTC instant."""
    if not (isinstance(v, str) and len(v) == 24 and v[10] == "T" and v[19] == "." and v[-1] == "Z"):
        return False
    digits = v[:4] + v[5:7] + v[8:10] + v[11:13] + v[14:16] + v[17:19] + v[20:23]
    if not (digits.isascii() and digits.isdigit() and v[4] == v[7] == "-" and v[13] == v[16] == ":"):
        return False
    y, mo, d, h, mi, sec = (int(v[a:b]) for a, b in ((0, 4), (5, 7), (8, 10), (11, 13), (14, 16), (17, 19)))
    leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
    days = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    return 1 <= mo <= 12 and 1 <= d <= days[mo - 1] and h < 24 and mi < 60 and sec < 60


def _coerce(spec, v):
    t, _, arg = spec.rstrip("?").partition(":")
    if t == "enum":
        vals = contract()["enums"][arg]
        if isinstance(v, str):
            return (True, v) if v in vals else ((True, "other") if "other" in vals else (False, None))
        return False, None
    if t == "name":
        return (True, norm(arg, v)) if isinstance(v, str) else (False, None)
    if t == "int":
        return (True, v) if isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 10 ** 12 else (False, None)
    if t == "bool":
        return (True, v) if isinstance(v, bool) else (False, None)
    if t == "hex":
        return (True, v) if isinstance(v, str) and len(v) == int(arg) and set(v) <= HEX else (False, None)
    if t == "iso":
        return (True, v) if _is_iso(v) else (False, None)
    if t == "id":
        return (True, safe_id(v)) if isinstance(v, str) else (False, None)
    if t == "semver":
        p = v.split(".") if isinstance(v, str) else []
        return (True, v) if len(p) == 3 and all(x.isdigit() for x in p) else (False, None)
    return False, None


def _find_record(rec):
    c = contract()["records"]
    name = rec.get("name")
    if not isinstance(name, str):
        return None, None, None
    if name in c and "{" not in name:
        return name, c[name], None
    for tpl, d in c.items():
        if "{" in tpl:
            prefix, _, rest = tpl.partition("{")
            key = rest.partition("}")[0]
            if name.startswith(prefix) and name != prefix:
                return tpl, d, (key, name[len(prefix):])
    return None, None, None


def validate(rec):
    """Return (clean_record or None, dropped_key_count, reason or None)."""
    if not isinstance(rec, dict):
        return None, 0, "unknown_record"
    c = contract()
    tpl, d, derived = _find_record(rec)
    if d is None:
        return None, len(rec), "unknown_record"
    if rec.get("kind") != d["kind"]:
        return None, len(rec), "bad_value"
    specs = dict(c["envelope"])
    specs.update(c["span_envelope"] if d["kind"] == "span" else c["event_envelope"])
    specs.update(d["keys"])
    clean, dropped, reason = {"name": None}, 0, None
    for k, v in rec.items():
        if k == "name":
            continue
        ok, nv = _coerce(specs[k], v) if k in specs else (False, None)
        if ok:
            clean[k] = nv
        else:
            dropped += 1
            reason = reason or ("undeclared_key" if k not in specs else "bad_value")
    for k, s in specs.items():
        if not s.endswith("?") and k not in clean:
            return None, dropped, "missing_required"
    clean["name"] = tpl
    if derived:
        key, given = derived
        if given != "{%s}" % key and given != clean.get(key):
            return None, dropped, "bad_value"
        clean["name"] = tpl.replace("{%s}" % key, str(clean[key]))
    return clean, dropped, reason


def _read(path, tries=1):
    for i in range(tries):
        try:
            with open(path, "rb") as f:
                b = f.read()
            if b or i == tries - 1:
                return b
        except OSError:
            return None
        time.sleep(0.005)
    return b""


def _json_state(path):
    import json
    try:
        d = json.loads(_read(path) or b"")
        return d if isinstance(d, dict) else None
    except ValueError:
        return None


def _put_json(path, obj):
    import json
    os.makedirs(os.path.dirname(path), 0o700, exist_ok=True)
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def _excl_write(path, data):
    """Create-once file; False if it already exists."""
    os.makedirs(os.path.dirname(path), 0o700, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    try:
        os.write(fd, data)
    finally:
        os.close(fd)
    return True


def _create_once(path, data):
    """Create path holding all of data atomically (temp file + hard link); False if it exists. Never visible half-written."""
    tmp = "%s.%d.%s.tmp" % (path, os.getpid(), os.urandom(4).hex())
    _excl_write(tmp, data)
    try:
        os.link(tmp, path)
        return True
    except FileExistsError:
        return False
    except OSError:  # no hard links on this filesystem
        return _excl_write(path, data)
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def get_salt(root):
    path = os.path.join(root, "state", "salt")
    b = _read(path)
    if b is not None and len(b) == 16:
        return b
    if b is not None:
        try:
            os.unlink(path)
        except OSError:
            pass
    s = os.urandom(16)
    if _create_once(path, s):
        return s
    b = _read(path)
    return b if b is not None and len(b) == 16 else s


def append_line(path, data):
    os.makedirs(os.path.dirname(path), 0o700, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


README = ("addit-harness local telemetry (off by default).\n"
          "One JSON line per event under sessions/: counts, sizes, enums and salted hashes only; never prompts,\n"
          "code, file contents, paths or error text. Nothing is ever sent anywhere. Kept 90 days.\n"
          "To delete everything: turn the telemetry_local switch off and remove this folder.\n")


class Ctx:
    def __init__(self, env, payload):
        sid = payload.get("session_id")
        if not isinstance(sid, str) or not sid:
            raise ValueError("no session")
        self.root = os.path.join(env["CLAUDE_PLUGIN_DATA"], "telemetry")
        self.project = env.get("CLAUDE_PROJECT_DIR", "")
        self.p = payload
        self.sid = safe_id(sid)
        self.now = time.time()
        self._salt = None
        self._ptr = None
        h = sid.replace("-", "").lower()
        self.trace = h if len(h) == 32 and set(h) <= HEX else sha(sid, 32)
        self.root_span = sha("root:" + self.sid, 16)
        _excl_write(os.path.join(self.root, "README.md"), README.encode())

    def hash(self, value, n=12):
        if self._salt is None:
            self._salt = get_salt(self.root)
        return sha256(self._salt + value.encode("utf-8", "replace")).hexdigest()[:n]

    def pointer(self):
        """(YYYY/MM/DD, start iso): the UTC day this session was first seen."""
        if self._ptr:
            return self._ptr
        path = os.path.join(self.root, "state", "sessions", self.sid)
        for attempt in (0, 1):
            raw = _read(path, 5)
            if raw:
                day, _, start = raw.decode("ascii", "replace").partition(" ")
                if len(day) == 10 and day[4] == day[7] == "/" and day.replace("/", "").isdigit() and _coerce("iso", start)[0]:
                    self._ptr = (day, start)
                    return self._ptr
            fresh = time.strftime("%Y/%m/%d", time.gmtime(self.now)) + " " + iso(self.now)
            if raw is None and _excl_write(path, fresh.encode()):
                self._ptr = tuple(fresh.split(" "))
                return self._ptr
            if raw is not None and attempt:
                tmp = "%s.%d.tmp" % (path, os.getpid())
                with open(tmp, "w") as f:
                    f.write(fresh)
                os.replace(tmp, path)
                self._ptr = tuple(fresh.split(" "))
                return self._ptr
        self._ptr = tuple((time.strftime("%Y/%m/%d", time.gmtime(self.now)) + " " + iso(self.now)).split(" "))
        return self._ptr

    def _put(self, rec):
        clean, dropped, reason = validate(rec)
        if clean is None:
            return None, dropped, reason
        line = (_dumps(clean) + "\n").encode()
        day = self.pointer()[0]
        if len(line) > contract()["limits"]["line_bytes"]:
            return None, 0, "too_large"
        append_line(os.path.join(self.root, "sessions", *day.split("/"), self.sid + ".jsonl"), line)
        return clean, dropped, reason

    def emit(self, name, fields, span=False, agent_id=None, start=None, parent=None):
        cfg = contract()
        now = iso(self.now)
        rec = {"schema_version": cfg["schema_version"], "kind": "span" if span else "event", "name": name,
               "trace_id": self.trace, "service.name": "addit-harness", "session.id": self.sid,
               "service.version": self._version(), "addit.project.hash": self.hash(self.project)}
        if span:
            rec.update({"start": start or now, "end": now, "span_id": agent_id and sha("agent:" + agent_id, 16) or self.root_span})
            if parent:
                rec["parent_span_id"] = parent
        else:
            rec.update({"time": now, "span_id": sha("agent:" + agent_id, 16) if agent_id else self.root_span})
        rec.update(fields)
        clean, dropped, reason = self._put(rec)
        if clean is None or dropped:
            self._put(dict(rec_base(rec), name="addit.telemetry.dropped", kind="event", time=now,
                           **{"addit.dropped.keys": dropped, "addit.dropped.reason": reason or "bad_value"}))

    def _version(self):
        if "ver" not in _CACHE:
            d = _json_state(os.path.join(os.path.dirname(HERE), ".claude-plugin", "plugin.json")) or {}
            _CACHE["ver"] = d.get("version", "0.0.0")
        return _CACHE["ver"]


def rec_base(rec):
    keys = ("schema_version", "trace_id", "span_id", "service.name", "service.version", "session.id", "addit.project.hash")
    return {k: rec[k] for k in keys if k in rec}


def _dumps(o):
    import json
    return json.dumps(o, separators=(",", ":"))


def agent_name(agent_type):
    """Normalized harness/competitor agent name, or None for any other agent."""
    if not isinstance(agent_type, str):
        return None
    if agent_type.startswith(PREFIX):
        return norm("agent", agent_type[len(PREFIX):])
    return agent_type if agent_type in contract()["competitors"] else None


def _count(v):
    return len(v) if isinstance(v, str) else 0


def _dict(v):
    return v if isinstance(v, dict) else {}


def _agent_state(c, aid):
    st = _json_state(os.path.join(c.root, "state", "agents", aid + ".json"))
    ok = st and isinstance(st.get("start"), str) and isinstance(st.get("resumes"), int) and isinstance(st.get("name"), str) and "sid" in st
    return st if ok else None


def _save_agent(c, aid, st):
    _put_json(os.path.join(c.root, "state", "agents", aid + ".json"), st)


def _close_agent(c, aid, st, outcome, closing):
    c.emit("invoke_agent {gen_ai.agent.name}", {"gen_ai.operation.name": "invoke_agent", "gen_ai.agent.name": norm("agent", st["name"]),
           "gen_ai.agent.id": aid, "addit.outcome": outcome, "addit.closing_chars": closing, "addit.resumes": st["resumes"]},
           span=True, agent_id=aid, start=st["start"], parent=c.root_span)
    st["closed"] = True
    _save_agent(c, aid, st)


def h_session_start(c, p):
    f = {"addit.session.source": p.get("source") if isinstance(p.get("source"), str) else "other"}
    if isinstance(p.get("context_tokens"), int):
        f["addit.session.context_tokens"] = p["context_tokens"]
    c.emit("addit.session.start", f)
    prune(c.root, c.now)


def h_session_end(c, p):
    adir = os.path.join(c.root, "state", "agents")
    for n in sorted(os.listdir(adir)) if os.path.isdir(adir) else []:
        st = _agent_state(c, n[:-5]) if n.endswith(".json") else None
        if st and st["sid"] == c.sid and not st.get("closed"):
            _close_agent(c, n[:-5], st, "interrupted", 0)
    reason = p.get("reason") if isinstance(p.get("reason"), str) else "unknown"
    c.emit("session", {"addit.session.end_reason": reason}, span=True, start=c.pointer()[1])


def h_subagent_start(c, p):
    name, aid = agent_name(p.get("agent_type")), p.get("agent_id")
    if not name or not isinstance(aid, str):
        return
    aid = safe_id(aid)
    st = _agent_state(c, aid)
    if st:
        st.update(resumes=st["resumes"] + 1, closed=False, handback=False, start=iso(c.now))
        _save_agent(c, aid, st)
        return
    _save_agent(c, aid, {"start": iso(c.now), "name": name, "handback": False, "resumes": 0, "closed": False, "sid": c.sid})
    c.emit("addit.agent.start", {"gen_ai.agent.name": name, "gen_ai.agent.id": aid}, agent_id=aid)


def h_subagent_stop(c, p):
    name, aid = agent_name(p.get("agent_type")), p.get("agent_id")
    if not name or not isinstance(aid, str):
        return
    aid = safe_id(aid)
    st = _agent_state(c, aid) or {"start": iso(c.now), "name": name, "handback": False, "resumes": 0, "closed": False, "sid": c.sid}
    if st.get("closed"):
        return
    chars = _count(p.get("last_assistant_message"))
    _close_agent(c, aid, st, "completed" if st.get("handback") or chars else "empty", chars)


def h_handback(c, p):
    name, aid = agent_name(p.get("agent_type")), p.get("agent_id")
    if not name or not isinstance(aid, str):
        return
    aid = safe_id(aid)
    st = _agent_state(c, aid) or {"start": iso(c.now), "name": name, "handback": False, "resumes": 0, "closed": False, "sid": c.sid}
    st["handback"] = True
    _save_agent(c, aid, st)
    c.emit("addit.agent.handback", {"gen_ai.agent.name": name, "gen_ai.agent.id": aid,
           "addit.report_chars": _count(_dict(p.get("tool_input")).get("message"))}, agent_id=aid)


def _skill_span(c, raw, trigger, call_id=None):
    name = raw[len(PREFIX):] if raw.startswith(PREFIX) else raw
    name = norm("skill", name)
    kind = "command" if trigger == "slash" and name in _stems("commands") else "skill"
    f = {"gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": "Skill", "addit.skill.name": name,
         "addit.component.kind": kind, "addit.trigger": trigger}
    if call_id:
        f["gen_ai.tool.call.id"] = call_id
    c.emit("execute_tool Skill {addit.skill.name}", f, span=True, parent=c.root_span)
    return name


def _slash_path(c):
    return os.path.join(c.root, "state", "slash", c.sid)


def h_expansion(c, p):
    cmd = p.get("command_name")
    if p.get("command_source") != "plugin" or not isinstance(cmd, str) or not cmd.startswith(PREFIX):
        return
    name = _skill_span(c, cmd, "slash")
    os.makedirs(os.path.dirname(_slash_path(c)), 0o700, exist_ok=True)
    _put_json(_slash_path(c), {"prompt": safe_id(p.get("prompt_id", "")), "name": name})


def h_skill(c, p):
    raw = _dict(p.get("tool_input")).get("skill")
    if not isinstance(raw, str) or (":" in raw and not raw.startswith(PREFIX)):
        return
    seen = _json_state(_slash_path(c)) or {}
    name = norm("skill", raw[len(PREFIX):] if raw.startswith(PREFIX) else raw)
    prompt = p.get("prompt_id")
    if prompt and isinstance(prompt, str) and seen.get("prompt") == safe_id(prompt) and seen.get("name") == name:
        return
    _skill_span(c, raw, "model", safe_id(p["tool_use_id"]) if isinstance(p.get("tool_use_id"), str) else None)


def _workflow_name(p):
    ti, tr = _dict(p.get("tool_input")), _dict(p.get("tool_response"))
    raw = tr.get("workflowName") if isinstance(tr.get("workflowName"), str) else os.path.basename(str(ti.get("scriptPath", ""))).rsplit(".", 1)[0]
    return raw if raw in contract()["enums"]["workflow"] else "other"


def _args(p):
    a = _dict(p.get("tool_input")).get("args")
    if isinstance(a, str):
        import json
        try:
            a = json.loads(a)
        except ValueError:
            a = None
    return a if isinstance(a, dict) else {}


def h_workflow(c, p):
    a = _args(p)
    f = {"gen_ai.operation.name": "invoke_workflow", "gen_ai.workflow.name": _workflow_name(p)}
    if isinstance(a.get("slug"), str):
        f["addit.devflow.slug_hash"] = c.hash(a["slug"])
    tier = a.get("tier") if isinstance(a.get("tier"), str) else a.get("userTier")
    if isinstance(tier, str):
        f["addit.devflow.tier"] = tier
    run = _dict(p.get("tool_response")).get("runId")
    if isinstance(run, str):
        f["addit.workflow.run_id"] = run
    c.emit("invoke_workflow {gen_ai.workflow.name}", f, span=True, parent=c.root_span)


SUBDIR_KIND = {"plans": "plan", "solutions": "solution", "architecture-reports": "report", "qa-reports": "qa",
               "adr": "adr", "adrs": "adr", "decisions": "adr", "specs": "spec"}


HARNESS_OUTPUT_KINDS = ("plan", "solution", "report", "qa")


def doc_fields(c, p):
    ti = _dict(p.get("tool_input"))
    path = ti.get("file_path")
    if not isinstance(path, str):
        return None
    parts = path.replace("\\", "/").split("/")
    if "docs" not in parts[:-1]:
        return None
    rest = parts[len(parts) - 1 - parts[::-1][1:].index("docs"):]
    work = len(rest) >= 3 and rest[0] == "work"
    sub, fname = (rest[2] if work else rest[0]), parts[-1]
    stem = fname.rsplit(".", 1)[0]
    kind = "brief" if sub == "specs" and fname == "brief.md" else SUBDIR_KIND.get(sub, "other")
    track = "other"
    if kind == "solution":
        for pre in ("solution-", "explore-"):
            if stem.startswith(pre):
                track = stem[len(pre):].split("-")[0]
    try:
        with open(path, "rb") as fh:
            raw = fh.read(2 * 1024 * 1024)
        size = os.stat(path).st_size
    except OSError:
        raw = ti.get("content", "").encode("utf-8", "replace") if isinstance(ti.get("content"), str) else b""
        size = len(raw)
    text = raw.decode("utf-8", "replace")
    import re
    f = {"addit.doc.kind": kind, "addit.doc.track": track, "addit.doc.layout": "work" if work else "legacy",
         "addit.doc.op": "write" if p.get("tool_name") == "Write" else "edit", "addit.doc.bytes": size,
         "addit.doc.lines": text.count("\n") + (1 if text and not text.endswith("\n") else 0),
         "addit.doc.mermaid_blocks": len(re.findall(r"^[ \t]*(?:```|~~~)\s*mermaid", text, re.M)),
         "addit.doc.path_hash": c.hash(path), "gen_ai.agent.name": agent_name(p.get("agent_type")) or "main"}
    if work:
        f["addit.devflow.slug_hash"] = c.hash(rest[1])
    if kind == "plan":
        f["addit.doc.approved"] = bool(re.search(r"^> dev-flow: approved", text, re.M))
    if kind == "solution" and stem.startswith("solution-"):
        cand = re.search(r"^#+[ \t].*\bcandidates?\b", text, re.M | re.I)
        owner = re.search(r"^#+[ \t].*\bowner\b|owner'?s? (?:idea|proposal)", text, re.M | re.I)
        f.update({"addit.doc.has_candidates": bool(cand), "addit.doc.has_owner_idea": bool(owner),
                  "addit.doc.candidates_before_owner": bool(cand and owner and cand.start() < owner.start()),
                  "addit.doc.claim_labels": len(re.findall(r"\[(?:O|I|U)\b[^\]\n]{0,40}\]", text))})
    return f, work


def h_doc(c, p):
    got = doc_fields(c, p)
    if got:
        c.emit("addit.doc.write", got[0])
        if not got[1] and got[0]["addit.doc.kind"] in HARNESS_OUTPUT_KINDS:
            c.emit("addit.gate.verdict", {"addit.gate.name": "doc_location", "addit.gate.verdict": "fail"})


def h_failure(c, p):
    tool, ti = p.get("tool_name"), _dict(p.get("tool_input"))
    f = {"gen_ai.tool.name": tool if isinstance(tool, str) else "other",
         "error.type": "interrupt" if p.get("is_interrupt") is True else "error"}
    if tool == "Agent" and isinstance(ti.get("subagent_type"), str):
        t = ti["subagent_type"]
        f["gen_ai.agent.name"] = norm("agent", t[len(PREFIX):] if t.startswith(PREFIX) else t)
    elif tool == "Skill" and isinstance(ti.get("skill"), str):
        s = ti["skill"]
        f["addit.skill.name"] = norm("skill", s[len(PREFIX):] if s.startswith(PREFIX) else s)
    elif tool == "Workflow":
        f["gen_ai.workflow.name"] = _workflow_name(p)
    if tool in ("Agent", "Skill", "Workflow"):
        c.emit("addit.tool.failure", f)


def h_instructions(c, p):
    path = p.get("file_path") if isinstance(p.get("file_path"), str) else ""
    base = os.path.basename(path)
    try:
        size = os.stat(path).st_size
    except OSError:
        size = 0
    c.emit("addit.rule.loaded", {"addit.rule.name": base if base in ("CLAUDE.md", "AGENTS.md") else norm("rule", base[:-3] if base.endswith(".md") else base),
           "addit.rule.load_reason": p.get("load_reason"), "addit.rule.memory_type": p.get("memory_type"), "addit.rule.bytes": size})


def h_post_tool(c, p):
    tool = p.get("tool_name")
    if tool == "SubagentHandback":
        h_handback(c, p)
    elif tool == "Skill":
        h_skill(c, p)
    elif tool == "Workflow":
        h_workflow(c, p)
    elif tool in ("Write", "Edit"):
        h_doc(c, p)


HANDLERS = {"SessionStart": h_session_start, "SessionEnd": h_session_end, "SubagentStart": h_subagent_start,
            "SubagentStop": h_subagent_stop, "PostToolUse": h_post_tool, "PostToolUseFailure": h_failure,
            "UserPromptExpansion": h_expansion, "InstructionsLoaded": h_instructions}


def prune(root, now):
    import shutil
    lim = contract()["limits"]
    cutoff = time.strftime("%Y/%m/%d", time.gmtime(now - lim["retention_days"] * 86400))
    sdir, days = os.path.join(root, "sessions"), []
    for y in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
        for m in sorted(os.listdir(os.path.join(sdir, y))):
            for d in sorted(os.listdir(os.path.join(sdir, y, m))):
                days.append(("%s/%s/%s" % (y, m, d), os.path.join(sdir, y, m, d)))
    keep = []
    for ymd, path in days:
        if ymd < cutoff:
            shutil.rmtree(path, ignore_errors=True)
        else:
            keep.append((ymd, path))

    def size(path):
        total = 0
        for a, _, fs in os.walk(path):
            for f in fs:
                try:
                    total += os.path.getsize(os.path.join(a, f))
                except OSError:
                    pass
        return total
    today = time.strftime("%Y/%m/%d", time.gmtime(now))
    total = sum(size(k) for _, k in keep)
    for ymd, path in keep:
        if total <= lim["root_mb"] * 1024 * 1024 or ymd >= today:
            break
        total -= size(path)
        shutil.rmtree(path, ignore_errors=True)
    for y in os.listdir(sdir) if os.path.isdir(sdir) else []:
        for m in os.listdir(os.path.join(sdir, y)):
            if not os.listdir(os.path.join(sdir, y, m)):
                os.rmdir(os.path.join(sdir, y, m))
        if not os.listdir(os.path.join(sdir, y)):
            os.rmdir(os.path.join(sdir, y))
    for sub, age in (("sessions", lim["retention_days"] * 86400), ("slash", lim["retention_days"] * 86400), ("agents", 2 * 86400)):
        d = os.path.join(root, "state", sub)
        for n in os.listdir(d) if os.path.isdir(d) else []:
            try:
                st = os.path.join(d, n)
                old = now - os.path.getmtime(st)
                if old > lim["retention_days"] * 86400 or (sub == "agents" and old > age and (_json_state(st) or {}).get("closed")):
                    os.unlink(st)
            except OSError:
                pass


def run(argv, env, stdin):
    if env.get("CLAUDE_PLUGIN_OPTION_TELEMETRY_LOCAL") not in ON or not env.get("CLAUDE_PLUGIN_DATA") or not argv:
        return
    import json
    raw = stdin.buffer.read(8 * 1024 * 1024)
    payload = json.loads(raw) if raw.strip() else {}
    if not isinstance(payload, dict):
        return
    cmd = argv[0]
    handler = HANDLERS.get(payload.get("hook_event_name")) if cmd == "hook" else None
    if cmd == "hook" and not handler:
        return
    c = Ctx(env, payload)
    if handler:
        handler(c, payload)
    elif cmd == "gate" and len(argv) == 3:
        f = {"addit.gate.name": argv[1], "addit.gate.verdict": argv[2]}
        slug = _args(payload).get("slug")
        if isinstance(slug, str):
            f["addit.devflow.slug_hash"] = c.hash(slug)
        c.emit("addit.gate.verdict", f)
    elif cmd == "fc" and len(argv) == 4:
        c.emit("addit.fc.violation", {"addit.fc.id": argv[1], "addit.fc.severity": argv[2],
               "addit.fc.count": int(argv[3]), "gen_ai.agent.name": agent_name(payload.get("agent_type")) or "main"})
    elif cmd == "setup" and len(argv) == 2:
        c.emit("addit.setup.state", {"addit.setup.state": argv[1]})


def main():
    try:
        run(sys.argv[1:], os.environ, sys.stdin)
    except BaseException:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
