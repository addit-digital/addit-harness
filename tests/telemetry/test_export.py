"""Tests for skills/telemetry-export/scripts/export.py: allow-list, canary end to end, empty root, crash fixture.

Run: python3 -m unittest discover -s tests/telemetry -v
"""
import copy
import html.parser
import os
import shutil
import subprocess
import time
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

from test_telemetry import REPO, Sandbox, fixture, hook_names, scripted_session, walk_strings, ROUTING

EXPORT = REPO / "skills/telemetry-export/scripts/export.py"
TEMPLATE = REPO / "skills/telemetry-export/assets/report.html"
CHROME = os.environ.get("CHROME") or shutil.which("chromium") or shutil.which("google-chrome") or (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" if Path("/Applications/Google Chrome.app").exists() else None)
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("telemetry_export", EXPORT)
exp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp)

DAYS = 36500


class ExportSandbox(Sandbox):
    def build(self):
        return exp.build(str(self.root), DAYS, time.time())

    def write_data(self, data):
        out = self.root / "export" / "t1"
        exp.write(str(out / "data.json"), json.dumps(data, indent=1))
        return out / "data.json"


class TestExport(ExportSandbox):
    def test_scripted_session_kpis_and_allowlist(self):
        scripted_session(self)
        data = self.build()
        self.assertEqual(data["sessions_n"], 1)
        self.assertEqual(data["schema_version"], "2.2")
        self.assertEqual(set(data), set(exp.tel.contract()["export"]["top_level_keys"]))
        self.assertEqual(data["invalid_lines"], 0)
        self.assertEqual(data["plugin_versions"], [json.loads((REPO / ".claude-plugin/plugin.json").read_text())["version"]])
        c = exp.tel.contract()
        self.assertEqual(set(data["kpis"]), set(c["export"]["na"]) | {"AR1", "AR2", "AR3", "CE3", "MH1", "MH2", "LE1", "DF1", "LE3", "DOC1", "DOC2", "DOC3", "SQ1", "FC-1"})
        for kid, v in data["kpis"].items():
            self.assertIn(v["status"], ("ok", "na"), kid)
            self.assertEqual(set(v) - {"detail"}, {"value", "n", "unit", "status", "reason"}, kid)
            if v["status"] == "na":
                self.assertTrue(v["reason"], kid)
        for kid in c["export"]["na"]:
            self.assertEqual(data["kpis"][kid]["status"], "na")
        self.assertEqual(data["kpis"]["AR2"]["detail"]["outcomes"], {"completed": 1, "interrupted": 1})
        self.assertEqual(data["kpis"]["MH1"]["detail"], {"ok": 1})
        self.assertEqual(data["kpis"]["FC-1"]["status"], "ok")
        row = data["per_session"][0]
        self.assertEqual(set(row), set(c["export"]["per_session_keys"]))
        self.assertEqual(row["outcomes"], {"completed": 1, "interrupted": 1})
        self.assertTrue(re.fullmatch(r"[0-9a-f]{12}", row["sid_hash"]))
        self.assertEqual(row["workflows"], [{"name": "dev-flow-design", "tier": "standard"}])
        self.assertEqual(row["doc_writes"], 2)
        text = self.write_data(data).read_text()
        for raw in ("3f2a9c1e-7b4d", "a1b2c3d4e5f60718", "open-agent-2", "wf_8c1d2e3f4a5b", "2026-10-02-billing-export", "/workspace"):
            self.assertNotIn(raw, text)
        salt = (self.root / "state/salt").read_bytes()
        self.assertNotIn(salt, text.encode())
        inv_a, inv_s = exp.tel.inventory("agent"), exp.tel.inventory("skill")
        for name in row["agents"]:
            self.assertIn(name, inv_a)
        for name in data["kpis"]["AR1"]["detail"]["skills_used"]:
            self.assertIn(name, inv_s)
        self.assertIn(row["end_reason"], exp.tel.contract()["enums"]["end_reason"])

    def test_empty_root_every_kpi_na(self):
        for root in (self.root, self.tmp / "missing"):
            data = exp.build(str(root), 30, 1790000000)
            self.assertEqual(data["sessions_n"], 0)
            self.assertEqual(data["per_session"], [])
            self.assertEqual({v["status"] for v in data["kpis"].values()}, {"na"})
            self.assertTrue(all(v["reason"] for v in data["kpis"].values()))

    def test_crash_fixture_exactly_one_interrupted(self):
        for name in ("session_start", "subagent_start"):
            self.assert_silent_ok(self.run_hook(fixture(name)))
        data = self.build()
        row = data["per_session"][0]
        self.assertEqual(row["outcomes"], {"interrupted": 1})
        self.assertEqual(row["end_reason"], "unknown")
        self.assertEqual(data["kpis"]["AR2"]["detail"]["outcomes"], {"interrupted": 1})
        self.assertGreaterEqual(row["duration_s"], 0)

    def test_invalid_lines_are_skipped_not_fatal(self):
        scripted_session(self)
        f = self.files()[0]
        f.write_text(f.read_text() + "not json\n" + json.dumps({"name": "addit.session.start", "prompt": "x"}) + "\n")
        data = self.build()
        self.assertEqual((data["sessions_n"], data["invalid_lines"]), (1, 2))
        page = exp.render(data, "local")
        self.assertIn('"invalid_lines":2', page)
        self.assertRegex(TEMPLATE.read_text(), r"if \(D\.invalid_lines\) app\.appendChild\(el\('p', 'mut'")

    def test_bad_timestamp_never_aborts_export(self):
        scripted_session(self)
        f = self.files()[0]
        rows = [json.loads(ln) for ln in f.read_text().splitlines()]
        bad = dict(next(r for r in rows if r["name"] == "session"), start="2026-13-45T00:00:00.000Z")
        f.write_text(f.read_text() + json.dumps(bad) + "\n")
        self.assertEqual(self.build()["sessions_n"], 1)
        real, exp.validate = exp.validate, lambda rec: (rec, 0, None)  # a line the validator wrongly let through
        try:
            data = self.build()
        finally:
            exp.validate = real
        self.assertEqual(data["sessions_n"], 1)
        self.assertEqual(exp.epoch("2026-13-45T00:00:00.000Z"), 0.0)

    def test_window_excludes_old_days(self):
        scripted_session(self)
        self.assertEqual(exp.build(str(self.root), 1, time.time() + 40 * 86400)["sessions_n"], 0)


class TestExportCanary(ExportSandbox):
    def test_canary_end_to_end(self):
        project = self.tmp / "proj CANARY-proj <leak>"
        doc = project / "docs/work/slug CANARY-slug <leak>/plans/plan CANARY-file.md"
        doc.parent.mkdir(parents=True)
        doc.write_text("# CANARY-body\n```mermaid\ngraph LR\n```\ndef f():\n    return '/Users/canary/src/a.ts'\n> dev-flow: approved\n")
        n = 0
        for name in hook_names():
            payload = copy.deepcopy(fixture(name))
            for path in list(walk_strings(payload)):
                if path[-1] in ROUTING:
                    continue
                parent = payload
                for key in path[:-1]:
                    parent = parent[key]
                n += 1
                parent[path[-1]] += " CANARY%02d <leak>/../x" % n
            payload.update(prompt="CANARY-prompt: deploy key", last_assistant_message="CANARY-report " * 5)
            if payload.get("tool_name") == "Write":
                payload["tool_input"]["file_path"] = str(doc)
            self.assert_silent_ok(self.run_hook(payload, CLAUDE_PROJECT_DIR=str(project)))
        self.assertGreater(len(self.lines()), 10)
        self.write_data(self.build())
        banned = [b"CANARY", b"canary", b"/Users/canary", b"def f()", b"```mermaid", b"leak", str(project).encode(), b"deploy key"]
        hits = [(f.name, b) for f in self.root.rglob("*") if f.is_file() and f.name != "salt" for b in banned if b in f.read_bytes()]
        self.assertEqual(hits, [])
        exported = (self.root / "export/t1/data.json").read_bytes()
        self.assertNotIn((self.root / "state/salt").read_bytes(), exported)
        print("\nexport canary: %d strings injected, hits under the whole root: 0" % n)


class Dom(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.scripts = [], []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "script":
            self.scripts.append(dict(attrs))


CANARY = "</script><img src=x onerror=alert(1)>"


class TestReport(ExportSandbox):
    def canary_ledger(self):
        sid = "c" * 32
        base = {"schema_version": "2.1", "kind": "span", "trace_id": sid, "span_id": "a" * 16, "service.name": "addit-harness",
                "service.version": "0.3.0", "session.id": sid, "addit.project.hash": "b" * 12,
                "start": "2026-10-01T10:00:00.000Z", "end": "2026-10-01T10:00:00.000Z"}
        rec = dict(base, name="execute_tool Skill " + CANARY, **{"gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": "Skill",
                   "addit.skill.name": CANARY, "addit.component.kind": "skill", "addit.trigger": "model"})
        f = self.root / "sessions/2026/10/01" / (sid + ".jsonl")
        f.parent.mkdir(parents=True)
        f.write_text(json.dumps(rec) + "\n")

    def test_canary_is_inert_in_report(self):
        self.canary_ledger()
        real, exp.validate = exp.validate, lambda rec: (rec, 0, None)  # a hostile name the writer would have refused
        try:
            data = exp.build(str(self.root), DAYS, time.time())
        finally:
            exp.validate = real
        self.assertIn(CANARY, data["kpis"]["AR1"]["detail"]["skills_used"])
        page = exp.render(data, "local")
        head, _, rest = page.partition('<script type="application/json" id="d">')
        blob = rest.split("</script>", 1)[0]
        self.assertTrue(rest.startswith(blob + "</script>"))
        self.assertNotRegex(blob, r"[<>&]")
        self.assertIn("\\u003c/script\\u003e\\u003cimg src=x onerror=alert(1)\\u003e", blob)
        self.assertNotIn(CANARY, page)
        dom = Dom()
        dom.feed(page)
        self.assertNotIn("img", dom.tags)
        self.assertEqual([s.get("type") for s in dom.scripts], ["application/json", None])
        self.assertEqual(json.loads(blob)["kpis"]["AR1"]["detail"]["skills_used"], {CANARY: 1})
        out = self.tmp / "canary.html"
        out.write_text(page)
        if not CHROME:
            print("\nreport canary: DOM-less check only (html.parser: no img element, data block holds no < > &); no headless browser found")
            return
        proc = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--virtual-time-budget=3000", "--enable-logging=stderr",
                               "--dump-dom", out.as_uri()], capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
        rendered = Dom()
        rendered.feed(proc.stdout)
        self.assertNotIn("img", rendered.tags)
        self.assertIn("<h1>Harness Telemetry</h1>", proc.stdout)
        self.assertIn("&lt;/script&gt;&lt;img src=x onerror=alert(1)&gt;", proc.stdout)  # shown as inert text
        self.assertNotRegex(proc.stderr, r"CONSOLE.*(Uncaught|rror)")
        print("\nreport canary: headless Chrome DOM has no img element; the name renders as text; no console errors")

    def test_artifact_has_no_per_session_ids_or_hashes(self):
        scripted_session(self)
        data = self.build()
        art = exp.aggregated(data)
        self.assertNotIn("per_session", art)
        page = exp.render(art, "artifact")
        blob = page.partition('id="d">')[2].split("</script>", 1)[0]
        self.assertNotIn("sid_hash", blob)
        self.assertEqual(json.loads(blob)["mode"], "artifact")
        for r in self.lines():
            for k in ("addit.project.hash", "addit.devflow.slug_hash", "addit.doc.path_hash", "gen_ai.agent.id", "session.id", "addit.workflow.run_id"):
                if k in r:
                    self.assertNotIn(str(r[k]), blob, k)
        self.assertNotIn(data["per_session"][0]["sid_hash"], blob)

    def test_artifact_payload_has_no_per_session_list(self):
        scripted_session(self)
        rule = self.tmp / "CLAUDE.md"
        rule.write_text("x" * 321)
        self.assert_silent_ok(self.run_hook(dict(fixture("instructions_loaded"), file_path=str(rule))))
        data = self.build()
        self.assertIn("per_session", data["kpis"]["CE3"]["detail"])
        art = exp.aggregated(data)

        def keys(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    yield k
                    yield from keys(v)
            elif isinstance(o, list):
                for v in o:
                    yield from keys(v)
        self.assertNotIn("per_session", set(keys(art)))
        self.assertEqual(art["kpis"]["CE3"]["value"], data["kpis"]["CE3"]["value"])
        self.assertIn("per_session", data["kpis"]["CE3"]["detail"])  # the local data.json keeps it
        out = self.tmp / "o"
        self.assertEqual(exp.main(["--root", str(self.root), "--out", str(out), "--artifact"]), 0)
        self.assertNotIn("per_session", (out / "artifact.html").read_text().partition('id="d">')[2].split("</script>", 1)[0])

    def test_cli_writes_data_and_report(self):
        scripted_session(self)
        out = self.tmp / "out"
        proc = subprocess.run([sys.executable, str(EXPORT), "--root", str(self.root), "--out", str(out)], capture_output=True, text=True,
                              env={"PATH": os.environ["PATH"]}, timeout=60)
        self.assertEqual((proc.returncode, proc.stderr), (0, ""))
        self.assertEqual(proc.stdout.split(), [str(out / "data.json"), str(out / "report.html")])
        self.assertEqual(json.loads((out / "data.json").read_text())["sessions_n"], 1)
        self.assertEqual((out / "report.html").stat().st_mode & 0o777, 0o600)
        proc = subprocess.run([sys.executable, str(EXPORT), "--root", str(self.tmp / "none"), "--out", str(self.tmp / "o2")], capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        art = subprocess.run([sys.executable, str(EXPORT), "--root", str(self.root), "--out", str(out), "--artifact"], capture_output=True, text=True, timeout=60)
        self.assertEqual(art.stdout.strip(), str(out / "artifact.html"))
        self.assertNotIn("sid_hash", (out / "artifact.html").read_text())


class TestExportNoNetwork(unittest.TestCase):
    def test_no_network_and_budgets(self):
        banned = re.compile(r"socket|urllib|https?://|http\.client|requests|fetch\(|XMLHttpRequest|WebSocket|ftplib|smtplib|subprocess|curl|wget|ssl")
        self.assertIsNone(banned.search(EXPORT.read_text()))
        page = TEMPLATE.read_text()
        self.assertIsNone(re.search(r"https?://|src=|@import|fetch\(|XMLHttpRequest|WebSocket|innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval\(", page))
        self.assertIn("default-src 'none'", page)
        self.assertEqual(page.count("__DATA__"), 1)
        self.assertLessEqual(EXPORT.stat().st_size, 16 * 1024)
        self.assertLessEqual(TEMPLATE.stat().st_size, 12288)


if __name__ == "__main__":
    unittest.main()
