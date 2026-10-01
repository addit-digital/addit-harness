"""Tests for hooks/telemetry.{sh,py}: off by default, metadata only, fails open, no network.

Run: python3 -m unittest discover -s tests/telemetry -v
Timings are printed; they are asserted only under ADDIT_TEL_BENCH=strict.
"""
import ast
import copy
import importlib.util
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / "hooks"
LAUNCHER = HOOKS / "telemetry.sh"
SCRIPT = HOOKS / "telemetry.py"
FIX = Path(__file__).resolve().parent / "fixtures"
STRICT = os.environ.get("ADDIT_TEL_BENCH") == "strict"
RUNS = int(os.environ.get("ADDIT_TEL_RUNS", "50"))

sys.dont_write_bytecode = True  # importing the hook must not leave __pycache__ in hooks/
spec = importlib.util.spec_from_file_location("telemetry", SCRIPT)
tel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tel)


def fixture(name):
    return json.loads((FIX / (name + ".json")).read_text())


def hook_names():
    return sorted(p.stem for p in FIX.glob("*.json"))


class Sandbox(unittest.TestCase):
    """A throwaway CLAUDE_PLUGIN_DATA and project dir per test."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="tel-"))
        self.data = self.tmp / "data"
        self.proj = self.tmp / "proj"
        self.data.mkdir()
        self.proj.mkdir()
        self.root = self.data / "telemetry"
        self.addCleanup(lambda: (os.chmod(self.root, 0o700) if self.root.is_dir() else None, shutil.rmtree(self.tmp, ignore_errors=True)))

    def env(self, opt="true", **extra):
        e = {"PATH": os.environ["PATH"], "HOME": str(self.tmp), "CLAUDE_PLUGIN_DATA": str(self.data),
             "CLAUDE_PROJECT_DIR": str(self.proj), "CLAUDE_PLUGIN_ROOT": str(REPO)}
        if opt is not None:
            e["CLAUDE_PLUGIN_OPTION_TELEMETRY_LOCAL"] = opt
        e.update(extra)
        return e

    def run_hook(self, payload, opt="true", args=("hook",), launcher=("sh", str(LAUNCHER)), raw=None, **extra):
        stdin = raw if raw is not None else json.dumps(payload)
        cmd = list(launcher) if args == ("hook",) else [sys.executable, "-S", str(SCRIPT), *args]
        return subprocess.run(cmd, input=stdin, capture_output=True, text=True, env=self.env(opt, **extra), timeout=30)

    def assert_silent_ok(self, proc):
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "")
        self.assertNotIn("Traceback", proc.stderr)

    def files(self, sub="sessions"):
        base = self.root / sub
        return sorted(p for p in base.rglob("*") if p.is_file()) if base.exists() else []

    def lines(self):
        out = []
        for f in self.files():
            for ln in f.read_text().splitlines():
                out.append(json.loads(ln))
        return out


SID_FILE = "3f2a9c1e-7b4d-4e8a-9c6b-1d2e3f4a5b6c"


def scripted_session(sb):
    """start -> agents (resume) -> handback -> stop -> skill -> slash+delegate -> workflow -> gate -> docs -> failure -> fc -> end."""
    other = fixture("subagent_start")
    other.update(agent_id="open-agent-2", agent_type="addit-harness:frontend-developer")
    steps = [("hook", "session_start"), ("hook", "instructions_loaded"), ("setup", "ok"), ("hook", "subagent_start"),
             ("hook", "subagent_start"), ("hook", "post_handback"), ("hook", "subagent_stop"), ("hook", "post_skill"),
             ("hook", "user_prompt_expansion"), ("hook", "post_skill_delegate"), ("hook", "post_workflow"),
             ("gate", "pre_workflow"), ("hook", "post_write_plan"), ("hook", "post_edit_legacy"), ("hook", "post_failure"),
             ("fc", "session_start"), ("hook", other), ("hook", "session_end")]
    for kind, what in steps:
        payload = what if isinstance(what, dict) else fixture(what if kind in ("hook", "gate", "fc") else "session_start")
        args = {"hook": ("hook",), "gate": ("gate", "plan_approval", "pass"), "fc": ("fc", "FC-1", "cap", "3"),
                "setup": ("setup", what)}[kind]
        proc = sb.run_hook(payload, args=args)
        sb.assert_silent_ok(proc)


EXPECTED = Counter({
    "addit.session.start": 1, "addit.rule.loaded": 1, "addit.setup.state": 1, "addit.agent.start": 2,
    "addit.agent.handback": 1, "invoke_agent code-reviewer": 1, "invoke_agent frontend-developer": 1,
    "execute_tool Skill adr": 1, "execute_tool Skill save-plan": 1, "invoke_workflow dev-flow-design": 1,
    "addit.gate.verdict": 2, "addit.doc.write": 2, "addit.tool.failure": 1, "addit.fc.violation": 1, "session": 1})


class TestOff(Sandbox):
    def test_off_no_files(self):
        names = hook_names()
        for opt in (None, "false", "0", ""):
            for name in names:
                proc = self.run_hook(fixture(name), opt=opt)
                self.assert_silent_ok(proc)
                self.assertFalse(self.root.exists(), "%s with option %r created files" % (name, opt))
        for name in names:  # the script itself also refuses to run when off
            self.assert_silent_ok(self.run_hook(fixture(name), opt="false", args=("hook",), launcher=(sys.executable, "-S", str(SCRIPT), "hook")))
            self.assert_silent_ok(self.run_hook(fixture(name), opt="false", args=("gate", "plan_approval", "pass")))
        self.assertFalse(self.root.exists())

    def test_no_data_dir_no_files(self):
        proc = subprocess.run(["sh", str(LAUNCHER)], input=json.dumps(fixture("session_start")), capture_output=True, text=True,
                              env={"PATH": os.environ["PATH"], "CLAUDE_PLUGIN_OPTION_TELEMETRY_LOCAL": "true"})
        self.assert_silent_ok(proc)

    def test_launcher_shells(self):
        shells = [("/bin/bash",), ("sh",)] + ([("dash",)] if shutil.which("dash") else [])
        for sh in shells:
            if not shutil.which(sh[0]) and not os.path.exists(sh[0]):
                continue
            shutil.rmtree(self.root, ignore_errors=True)
            self.assert_silent_ok(self.run_hook(fixture("session_start"), launcher=(*sh, str(LAUNCHER))))
            self.assertEqual(len(self.lines()), 1, sh)
            shutil.rmtree(self.root, ignore_errors=True)
            self.assert_silent_ok(self.run_hook(fixture("session_start"), opt="false", launcher=(*sh, str(LAUNCHER))))
            self.assertFalse(self.root.exists())
        if os.path.exists("/bin/bash"):
            ver = subprocess.run(["/bin/bash", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
            print("\nlauncher verified under: %s" % ver)
        for script in HOOKS.glob("*.sh"):
            self.assertEqual(subprocess.run(["bash", "-n", str(script)]).returncode, 0, script)


class TestOn(Sandbox):
    def test_each_once(self):
        scripted_session(self)
        got = Counter(r["name"] for r in self.lines())
        self.assertEqual(got, EXPECTED)
        templates = {tel._find_record(r)[0] for r in self.lines()}
        self.assertEqual(templates, set(tel.contract()["records"]) - {"addit.telemetry.dropped"})
        print("\nevents covered: %d record types (R13 excluded), %d lines" % (len(set(got)), sum(got.values())))
        self.assertNotIn("addit.telemetry.dropped", got)
        interrupted = [r for r in self.lines() if r["name"] == "invoke_agent frontend-developer"]
        self.assertEqual(interrupted[0]["addit.outcome"], "interrupted")
        done = [r for r in self.lines() if r["name"] == "invoke_agent code-reviewer"][0]
        self.assertEqual((done["addit.outcome"], done["addit.resumes"], done["addit.closing_chars"]), ("completed", 1, 26))
        slash = [r for r in self.lines() if r["name"] == "execute_tool Skill save-plan"][0]
        self.assertEqual((slash["addit.trigger"], slash["addit.component.kind"]), ("slash", "command"))
        self.assertEqual(len(self.files()), 1)

    def test_doc_metadata_only_counts(self):
        doc = self.proj / "docs/work/2026-10-02-x/plans/plan.md"
        doc.parent.mkdir(parents=True)
        doc.write_text("# P\n> dev-flow: approved\n```mermaid\ngraph LR\n```\n~~~mermaid\n~~~\n")
        p = fixture("post_write_plan")
        p["tool_input"]["file_path"] = str(doc)
        self.assert_silent_ok(self.run_hook(p))
        rec = self.lines()[0]
        self.assertEqual((rec["addit.doc.lines"], rec["addit.doc.mermaid_blocks"], rec["addit.doc.approved"], rec["addit.doc.kind"],
                          rec["addit.doc.layout"], rec["gen_ai.agent.name"]), (7, 2, True, "plan", "work", "backend-architect"))

    def test_solution_method_fields(self):
        doc = self.proj / "docs/work/s/solutions/solution-backend.md"
        doc.parent.mkdir(parents=True)
        doc.write_text("# S\n## Candidates\nA [O: ls] B [I] C [U]\n## Owner idea\nx\n")
        p = fixture("post_write_plan")
        p["tool_input"]["file_path"] = str(doc)
        self.assert_silent_ok(self.run_hook(p))
        rec = self.lines()[0]
        self.assertEqual((rec["addit.doc.kind"], rec["addit.doc.track"], rec["addit.doc.has_candidates"], rec["addit.doc.has_owner_idea"],
                          rec["addit.doc.candidates_before_owner"], rec["addit.doc.claim_labels"]), ("solution", "backend", True, True, True, 3))

    def test_non_docs_write_ignored_and_foreign_agents_ignored(self):
        p = fixture("post_write_plan")
        p["tool_input"]["file_path"] = "/home/u/proj/src/app.ts"
        self.assert_silent_ok(self.run_hook(p))
        s = fixture("subagent_start")
        s["agent_type"] = "my-private-agent"
        self.assert_silent_ok(self.run_hook(s))
        self.assertEqual(self.lines(), [])

    def test_doc_location_gate_only_for_harness_outputs(self):
        cases = [("docs/work/README.md", False), ("docs/adr/0001-choice.md", False), ("docs/guide.md", False),
                 ("docs/plans/old-plan.md", True), ("docs/solutions/s.md", True), ("docs/architecture-reports/r.md", True),
                 ("docs/work/2026-10-02-x/plans/plan.md", False)]
        for rel, fails in cases:
            with self.subTest(rel=rel):
                shutil.rmtree(self.root, ignore_errors=True)
                p = fixture("post_write_plan")
                p["tool_input"]["file_path"] = str(self.proj / rel)
                self.assert_silent_ok(self.run_hook(p))
                names = [r["name"] for r in self.lines()]
                self.assertIn("addit.doc.write", names)
                self.assertEqual(names.count("addit.gate.verdict"), int(fails))

    def test_skill_dedup_needs_a_prompt_id(self):
        def triggers():
            return [r["addit.trigger"] for r in self.lines() if r["name"].startswith("execute_tool Skill")]
        slash, model = fixture("user_prompt_expansion"), fixture("post_skill_delegate")
        self.assert_silent_ok(self.run_hook(slash))
        self.assert_silent_ok(self.run_hook(model))
        self.assertEqual(triggers(), ["slash"])  # same prompt: the model call is the slash command's own delegate
        shutil.rmtree(self.root)
        for p in (slash, model):
            del p["prompt_id"]
        self.assert_silent_ok(self.run_hook(slash))
        self.assert_silent_ok(self.run_hook(model))
        self.assertEqual(triggers(), ["slash", "model"])

    def test_unhandled_event_creates_nothing(self):
        self.assert_silent_ok(self.run_hook(fixture("pre_workflow")))
        self.assertFalse(self.root.exists())

    def test_resume_keeps_first_day_folder(self):
        self.assert_silent_ok(self.run_hook(fixture("session_start")))
        ptr = self.root / "state" / "sessions" / SID_FILE
        ptr.write_text("2026/01/02 2026-01-02T03:04:05.000Z")
        self.assert_silent_ok(self.run_hook(fixture("instructions_loaded")))
        self.assertTrue((self.root / "sessions/2026/01/02" / (SID_FILE + ".jsonl")).exists())

    def test_prune_retention_and_cap(self):
        old = self.root / "sessions/2020/01/01"
        old.mkdir(parents=True)
        (old / "x.jsonl").write_text("{}\n")
        agents = self.root / "state/agents"
        agents.mkdir(parents=True)
        for n, closed in (("old-closed", True), ("old-open", False)):
            (agents / (n + ".json")).write_text(json.dumps({"closed": closed}))
            os.utime(agents / (n + ".json"), (time.time() - 3 * 86400,) * 2)
        self.assert_silent_ok(self.run_hook(fixture("session_start")))
        self.assertFalse((self.root / "sessions/2020").exists())
        self.assertFalse((agents / "old-closed.json").exists())
        self.assertTrue((agents / "old-open.json").exists())
        keep = self.root / "sessions" / time.strftime("%Y/%m/%d", time.gmtime(time.time() - 86400))
        keep.mkdir(parents=True, exist_ok=True)
        (keep / "big.jsonl").write_bytes(b"x" * 1024)
        saved = tel.contract()["limits"]["root_mb"]
        tel.contract()["limits"]["root_mb"] = 0
        try:
            tel.prune(str(self.root), time.time())
        finally:
            tel.contract()["limits"]["root_mb"] = saved
        self.assertFalse(keep.exists())


    def test_prune_cap_spares_today_and_tolerates_vanishing_files(self):
        now = time.time()
        sessions = self.root / "sessions"
        today = sessions / time.strftime("%Y/%m/%d", time.gmtime(now))
        older = sessions / time.strftime("%Y/%m/%d", time.gmtime(now - 86400))
        for d in (today, older):
            d.mkdir(parents=True, exist_ok=True)
            (d / "big.jsonl").write_bytes(b"x" * 2048)
        os.symlink(str(self.tmp / "gone"), str(older / "rotated.jsonl"))  # getsize raises, as for a concurrently rotated file
        limits = tel.contract()["limits"]
        saved, limits["root_mb"] = limits["root_mb"], 0
        try:
            tel.prune(str(self.root), now)
        finally:
            limits["root_mb"] = saved
        self.assertTrue((today / "big.jsonl").exists())
        self.assertFalse(older.exists())

class TestContract(Sandbox):
    def test_allowlist_structural(self):
        sb = self
        scripted_session(sb)
        c = tel.contract()
        checked = 0
        for rec in sb.lines():
            tpl, d, _ = tel._find_record(rec)
            self.assertIsNotNone(d, rec["name"])
            allowed = set(c["envelope"]) | set(c["span_envelope" if d["kind"] == "span" else "event_envelope"]) | set(d["keys"]) | {"name"}
            self.assertLessEqual(set(rec), allowed, rec["name"])
            clean, dropped, reason = tel.validate(rec)
            self.assertEqual((clean, dropped, reason), (rec, 0, None), rec["name"])
            checked += len(rec)
        print("\nallow-list: %d keys checked across %d lines" % (checked, len(sb.lines())))

    def test_validate_rules(self):
        base = {"schema_version": "2.0", "kind": "event", "name": "addit.agent.handback", "trace_id": "a" * 32, "span_id": "b" * 16,
                "service.name": "addit-harness", "service.version": "0.3.0", "session.id": "s1", "addit.project.hash": "c" * 12,
                "time": "2026-10-01T00:00:00.000Z", "gen_ai.agent.name": "code-reviewer", "gen_ai.agent.id": "a1", "addit.report_chars": 5}
        self.assertEqual(tel.validate(base), (base, 0, None))
        cases = [("gen_ai.agent.name", "not-in-inventory", "other"), ("gen_ai.agent.id", "bad id/../x", tel.sha("bad id/../x", 32))]
        for k, v, want in cases:
            self.assertEqual(tel.validate(dict(base, **{k: v}))[0][k], want)
        for bad in (-1, True, "5", 1.5, 10 ** 13):
            clean, dropped, reason = tel.validate(dict(base, **{"addit.report_chars": bad}))
            self.assertEqual((clean, reason), (None, "missing_required"), bad)
        clean, dropped, reason = tel.validate(dict(base, prompt="secret", **{"addit.x": 1}))
        self.assertEqual((dropped, reason, "prompt" in clean), (2, "undeclared_key", False))
        self.assertEqual(tel.validate(dict(base, kind="span"))[2], "bad_value")
        self.assertEqual(tel.validate(dict(base, name="nope"))[0], None)
        self.assertEqual(tel.validate("x")[0], None)
        gate = {k: v for k, v in base.items() if not k.startswith(("gen_ai", "addit.report"))}
        gate.update(name="addit.gate.verdict", **{"addit.gate.name": "plan_approval", "addit.gate.verdict": "pass"})
        self.assertEqual(tel.validate(gate)[1:], (0, None))
        self.assertEqual(tel.validate(dict(gate, **{"addit.gate.verdict": "weird"}))[0::2], (None, "missing_required"))

    def test_iso_rejects_impossible_instants(self):
        good = ["2026-10-01T00:00:00.000Z", "2028-02-29T23:59:59.999Z"]
        bad = ["2026-13-45T00:00:00.000Z", "2026-02-29T00:00:00.000Z", "2026-04-31T00:00:00.000Z", "2026-10-01T24:00:00.000Z",
               "2026-10-01T00:60:00.000Z", "2026-10-01T00:00:60.000Z", "2026-00-10T00:00:00.000Z", "2026-10-00T00:00:00.000Z",
               "2026-10-01T00:00:00,000Z", "2026-10-01T00:00:00.00aZ", "xxxx-10-01T00:00:00.000Z", "2026-10-01T00:00:00.000X"]
        for v in good:
            self.assertEqual(tel._coerce("iso", v), (True, v), v)
        for v in bad:
            self.assertEqual(tel._coerce("iso", v), (False, None), v)

    def test_line_cap(self):
        sb = self
        sb.assert_silent_ok(sb.run_hook(fixture("session_start")))
        c = tel.Ctx(sb.env(), fixture("session_start"))
        c.emit("addit.agent.handback", {"gen_ai.agent.name": "code-reviewer", "gen_ai.agent.id": "a1", "addit.report_chars": 1, "addit.blob": "x" * 5000})
        recs = sb.lines()
        self.assertEqual(recs[-1]["name"], "addit.telemetry.dropped")
        self.assertEqual((recs[-1]["addit.dropped.keys"], recs[-1]["addit.dropped.reason"]), (1, "undeclared_key"))
        self.assertTrue(all(len(json.dumps(r)) < 4096 for r in recs))
        limits = tel.contract()["limits"]
        saved, limits["line_bytes"] = limits["line_bytes"], 420
        try:
            c.emit("invoke_agent {gen_ai.agent.name}", {"gen_ai.operation.name": "invoke_agent", "gen_ai.agent.name": "code-reviewer", "gen_ai.agent.id": "a1",
                   "addit.outcome": "completed", "addit.closing_chars": 1, "addit.resumes": 0}, span=True)
        finally:
            limits["line_bytes"] = saved
        self.assertEqual(sb.lines()[-1]["addit.dropped.reason"], "too_large")
        self.assertEqual(sum(1 for r in sb.lines() if r["name"].startswith("invoke_agent")), 0)

    def test_contract_sync(self):
        c = tel.contract()
        table = (REPO / "references/doc-protocol.md").read_text()
        rows = {m.group(1).lower(): [int(re.match(r"\s*(\d+)", cell).group(1)) for cell in m.group(2).split("|") if re.match(r"\s*\d", cell)]
                for m in re.finditer(r"^\| (Plan|Solution) \|(.*)$", table, re.M)}
        self.assertEqual(list(c["doc_ceilings"]["plan"].values()), rows["plan"])
        self.assertEqual(list(c["doc_ceilings"]["solution"].values()), rows["solution"])
        self.assertEqual(c["schema_version"], "2.2")
        self.assertIn(c["schema_version"], c["enums"]["schema"])
        self.assertLessEqual((HOOKS / "telemetry-contract.json").stat().st_size, 6 * 1024)
        self.assertEqual(c["limits"], {"line_bytes": 4096, "root_mb": 100, "retention_days": 90})
        wf = "".join(p.read_text() for p in (REPO / "workflows").glob("dev-flow-*.js"))
        for k in c["workflow_result_keys"]:
            self.assertIn(k, wf)
        hooks = json.loads((HOOKS / "hooks.json").read_text())["hooks"]
        for event, groups in hooks.items():
            for g in groups:
                for h in g["hooks"]:
                    if "telemetry.sh" in json.dumps(h):
                        self.assertEqual((h["command"], h["type"]), ("sh", "command"))
                        self.assertTrue(h["args"][0].endswith("hooks/telemetry.sh"))
                        self.assertEqual("timeout" in h, event != "SessionEnd", event)
                        if "if" in h:
                            self.assertIn(event, ("PreToolUse", "PostToolUse", "PostToolUseFailure"))

    def test_no_network(self):
        banned = re.compile(r"socket|urllib|http\.client|requests|fetch\(|XMLHttpRequest|WebSocket|ftplib|smtplib|subprocess|curl|wget|ssl")
        for f in (SCRIPT, LAUNCHER):
            self.assertIsNone(banned.search(f.read_text()), f)
        imported = set()
        for node in ast.walk(ast.parse(SCRIPT.read_text())):
            if isinstance(node, ast.Import):
                imported |= {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module)
        self.assertLessEqual(imported, {"os", "sys", "time", "json", "hashlib", "_sha2", "re", "shutil"})
        print("\nimports: %s; telemetry.py %d bytes; contract %d bytes" % (sorted(imported), SCRIPT.stat().st_size, (HOOKS / "telemetry-contract.json").stat().st_size))


def walk_strings(obj, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, path + (i,))
    elif isinstance(obj, str):
        yield path


ROUTING = {"hook_event_name", "tool_name", "command_source", "load_reason", "source", "reason", "memory_type"}


class TestCanary(Sandbox):
    def canary(self, n):
        return "CANARY%02d <leak>/../x:y\"z" % n

    def test_canary(self):
        project = self.tmp / ("proj CANARY-proj <leak>")
        project.mkdir()
        doc = project / "docs/work/slug CANARY-slug <leak>/plans/plan CANARY-file.md"
        doc.parent.mkdir(parents=True)
        doc.write_text("# CANARY-body\n```mermaid\ngraph LR\n```\ndef f():\n    return '/Users/canary/src/a.ts'\n> dev-flow: approved\n")
        extras = {"prompt": "CANARY-prompt: deploy key", "user_email": "canary@example.com", "git_branch": "CANARY-branch/leak",
                  "last_assistant_message": "CANARY-report " * 5, "error": "CANARY-error at /Users/canary/src/a.ts", "file_path": "/Users/canary/src/a.ts"}
        n = 0
        rounds = [fixture(x) for x in hook_names()]
        for payload in rounds:
            payload = copy.deepcopy(payload)
            for path in list(walk_strings(payload)):
                if path[-1] in ROUTING:
                    continue
                parent = payload
                for key in path[:-1]:
                    parent = parent[key]
                n += 1
                parent[path[-1]] = parent[path[-1]] + self.canary(n)
            payload.update(extras)
            if payload.get("tool_name") == "Write":
                payload["tool_input"]["file_path"] = str(doc)
                payload["tool_input"]["content"] = "CANARY-content def f():\n"
            self.assert_silent_ok(self.run_hook(payload, CLAUDE_PROJECT_DIR=str(project), GIT_BRANCH="CANARY-env-branch", EMAIL="canary@example.com"))
            if payload["hook_event_name"] == "PreToolUse":
                self.assert_silent_ok(self.run_hook(payload, args=("gate", "plan_approval", "pass"), CLAUDE_PROJECT_DIR=str(project)))
        for args in (("gate", "CANARY-gate", "CANARY-verdict"), ("setup", "CANARY-state"), ("fc", "CANARY-fc", "CANARY-sev", "7")):
            self.assert_silent_ok(self.run_hook(fixture("session_start"), args=args, CLAUDE_PROJECT_DIR=str(project)))
        injected = n + len(extras) * len(rounds) + 3 + 4 + 5
        self.assertGreater(len(self.lines()), 10, "canary run wrote almost nothing; the test would be vacuous")
        banned = [b"CANARY", b"canary", b"/Users/canary", b"def f()", b"```mermaid", b"leak", str(project).encode(), b"deploy key", b"@example.com"]
        hits = []
        for f in self.root.rglob("*"):
            if f.is_file():
                blob = f.read_bytes()
                if f.name == "salt":
                    continue
                hits += [(f.name, b) for b in banned if b in blob]
        self.assertEqual(hits, [])
        salt = (self.root / "state/salt").read_bytes()
        self.assertEqual(len(salt), 16)
        for f in self.files():
            self.assertNotIn(salt, f.read_bytes())
        print("\ncanary strings injected: %d across %d payloads + env + doc body/slug/filename; hits: 0" % (injected, len(rounds)))


class TestFailOpen(Sandbox):
    def all_fixtures(self):
        for name in hook_names():
            self.assert_silent_ok(self.run_hook(fixture(name)))

    def test_root_is_a_file(self):
        self.root.write_text("not a dir")
        self.all_fixtures()

    def test_read_only_root(self):
        self.root.mkdir()
        os.chmod(self.root, 0o500)
        self.all_fixtures()

    def test_garbage_state(self):
        scripted_session(self)
        for f in self.files("state"):
            f.write_bytes(b"\x00garbage{")
        self.all_fixtures()
        self.assertEqual(len((self.root / "state/salt").read_bytes()), 16)
        ptr = (self.root / "state/sessions" / SID_FILE).read_text()
        self.assertRegex(ptr, r"^\d{4}/\d\d/\d\d 20\d\d-")
        for ln in (ln for f in self.files() for ln in f.read_text().splitlines()):
            json.loads(ln)

    def test_traversal_ids(self):
        for name in hook_names():
            p = fixture(name)
            p["session_id"] = "../../x"
            for key in ("agent_id", "tool_use_id"):
                if key in p:
                    p[key] = "../../x"
            self.assert_silent_ok(self.run_hook(p))
        self.assertEqual(sorted(x.name for x in self.tmp.iterdir()), ["data", "proj"])
        self.assertEqual(sorted(x.name for x in self.data.iterdir()), ["telemetry"])
        for f in self.root.rglob("*"):
            self.assertNotIn("..", f.relative_to(self.root).parts)
        self.assertTrue(self.files() and all(re.fullmatch(r"[0-9a-f]{32}\.jsonl", f.name) for f in self.files()))
        self.assertTrue(all(r["session.id"] == tel.sha("../../x", 32) for r in self.lines()))

    def test_truncated_and_bad_stdin(self):
        for raw in ('{"hook_event_name":"SessionSta', "", "[1,2]", "null", "\xff\xfe", '{"session_id": 5}', '{"hook_event_name":"SessionStart"}'):
            self.assert_silent_ok(self.run_hook(None, raw=raw))
        self.assertEqual(self.lines(), [])

    def test_missing_contract(self):
        h = self.tmp / "h"
        h.mkdir()
        shutil.copy(SCRIPT, h)
        shutil.copy(LAUNCHER, h)
        self.assert_silent_ok(self.run_hook(fixture("session_start"), launcher=("sh", str(h / "telemetry.sh"))))
        self.assertEqual(self.lines(), [])

    def test_bad_cli_args(self):
        for args in (("gate",), ("fc", "FC-1", "cap", "many"), ("nope",), ()):
            self.assert_silent_ok(self.run_hook(fixture("session_start"), args=args or ("setup",)))
        self.assert_silent_ok(subprocess.run([sys.executable, "-S", str(SCRIPT)], input="{}", capture_output=True, text=True, env=self.env()))


class TestConcurrency(Sandbox):
    def test_salt_race_threads(self):
        root = str(self.root)
        os.makedirs(root)
        out, barrier = [], threading.Barrier(16)

        def go():
            barrier.wait()
            out.append(tel.get_salt(root))
        ts = [threading.Thread(target=go) for _ in range(16)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(len(set(out)), 1)
        self.assertEqual((self.root / "state/salt").read_bytes(), out[0])
        self.assertEqual(oct((self.root / "state/salt").stat().st_mode & 0o777), "0o600")

    def test_salt_never_visible_half_written(self):
        root = str(self.root)
        os.makedirs(root)
        real_write, entered, release, calls = os.write, threading.Event(), threading.Event(), []

        def stalled_write(fd, data):  # the first writer stalls mid-create, like a descheduled process
            calls.append(fd)
            if len(calls) == 1:
                entered.set()
                release.wait(10)
            return real_write(fd, data)
        out = {}
        first = threading.Thread(target=lambda: out.update(a=tel.get_salt(root)))
        os.write = stalled_write
        try:
            first.start()
            self.assertTrue(entered.wait(10))
            out["b"] = tel.get_salt(root)
            release.set()
            first.join(10)
        finally:
            os.write = real_write
            release.set()
        self.assertEqual(len(out["a"]), 16)
        self.assertEqual(out["a"], out["b"])
        self.assertEqual((self.root / "state/salt").read_bytes(), out["a"])

    def test_salt_race_processes(self):
        procs = []
        for i in range(12):
            payload = fixture("session_start" if i % 2 else "instructions_loaded")
            procs.append(subprocess.Popen(["sh", str(LAUNCHER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          text=True, env=self.env()))
            procs[-1].stdin.write(json.dumps(payload))
            procs[-1].stdin.close()
            procs[-1].stdin = None
        for p in procs:
            p.communicate(timeout=30)
            self.assertEqual(p.returncode, 0)
        hashes = {r["addit.project.hash"] for r in self.lines()}
        self.assertEqual(len(self.lines()), 12)
        self.assertEqual(len(hashes), 1)
        self.assertEqual(len((self.root / "state/salt").read_bytes()), 16)
        self.assertEqual(sorted(f.name for f in self.files("state") if "sessions" in f.parts), [SID_FILE])

    def test_append_atomic_threads(self):
        path = str(self.root / "a" / "x.jsonl")
        n_threads, per = 8, 120

        def go(t):
            for i in range(per):
                tel.append_line(path, (json.dumps({"t": t, "i": i, "pad": "p" * 3500}) + "\n").encode())
        ts = [threading.Thread(target=go, args=(t,)) for t in range(n_threads)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        rows = [json.loads(ln) for ln in Path(path).read_text().splitlines()]
        self.assertEqual(len(rows), n_threads * per)
        self.assertEqual(len({(r["t"], r["i"]) for r in rows}), n_threads * per)

    def test_append_processes(self):
        procs = []
        for w in range(6):
            sh = "for i in 1 2 3 4 5 6 7 8; do sh '%s' < '%s'; done" % (LAUNCHER, FIX / "instructions_loaded.json")
            procs.append(subprocess.Popen(["sh", "-c", sh], env=self.env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        for p in procs:
            p.communicate(timeout=60)
            self.assertEqual(p.returncode, 0)
        self.assertEqual(len(self.lines()), 48)


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))]


class TestOverhead(Sandbox):
    def timed(self, payload, opt):
        stdin = json.dumps(payload)
        env = self.env(opt)
        out = []
        for _ in range(RUNS):
            t = time.perf_counter()
            subprocess.run(["sh", str(LAUNCHER)], input=stdin, capture_output=True, text=True, env=env)
            out.append((time.perf_counter() - t) * 1000)
        return out

    def test_overhead(self):
        rows = []
        off = self.timed(fixture("session_start"), "false")
        rows.append(("OFF", pct(off, 0.5), pct(off, 0.9)))
        self.assertFalse(self.root.exists())
        for name in hook_names():
            ms = self.timed(fixture(name), "true")
            rows.append((name, pct(ms, 0.5), pct(ms, 0.9)))
        print("\n%d runs per fixture, wall time incl. sh + process spawn (ms)" % RUNS)
        for name, p50, p90 in rows:
            print("  %-24s p50 %6.1f  p90 %6.1f" % (name, p50, p90))
        print("  overall on-path p50 %.1f ms, p90 %.1f ms" % (statistics.median(r[1] for r in rows[1:]), max(r[2] for r in rows[1:])))
        if STRICT:
            self.assertLessEqual(rows[0][2], 20)
            for name, p50, p90 in rows[1:]:
                self.assertLessEqual(p90, 150 if name == "session_start" else 50, name)


if __name__ == "__main__":
    unittest.main()
