"""The three existing hooks record verdicts through telemetry.py without changing their own result.

Run: python3 -m unittest discover -s tests/telemetry -v
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / "hooks"
SID = "3f2a9c1e-7b4d-4e8a-9c6b-1d2e3f4a5b6c"
BASE = {"session_id": SID, "cwd": "/w", "transcript_path": "/w/t.jsonl"}


class HookSandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="telh-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.home, self.data, self.proj = self.tmp / "home", self.tmp / "data", self.tmp / "proj"
        for d in (self.home / ".claude", self.data, self.proj):
            d.mkdir(parents=True)
        self.root = self.data / "telemetry"

    def run_hook(self, script, payload, opt="true", **extra):
        env = {"PATH": os.environ["PATH"], "HOME": str(self.home), "CLAUDE_PLUGIN_ROOT": str(REPO),
               "CLAUDE_PLUGIN_DATA": str(self.data), "CLAUDE_PROJECT_DIR": str(self.proj),
               "CLAUDE_CODE_ENTRYPOINT": "sdk-cli"}  # headless: keeps the first-run welcome (tests/onboarding) out of these assertions
        if opt is not None:
            env["CLAUDE_PLUGIN_OPTION_TELEMETRY_LOCAL"] = opt
        env.update(extra)
        return subprocess.run(["bash", str(HOOKS / script)], input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=30)

    def records(self):
        return [json.loads(ln) for f in sorted(self.root.rglob("*.jsonl")) for ln in f.read_text().splitlines()]


class TestGate(HookSandbox):
    def payload(self, sha):
        return {**BASE, "hook_event_name": "PreToolUse", "tool_name": "Workflow",
                "tool_input": {"scriptPath": "/p/workflows/dev-flow-implement.js",
                               "args": {"slug": "s1", "repo": str(self.proj), "planSha256": sha}}}

    def plan(self, text):
        p = self.proj / "docs/work/s1/plans/plan.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return hashlib.sha256(text.encode()).hexdigest()

    def test_deny_is_unchanged_and_recorded(self):
        pay = self.payload("0" * 64)  # no plan yet
        off, on = self.run_hook("gate-dev-flow-implement.sh", pay, opt="false"), self.run_hook("gate-dev-flow-implement.sh", pay)
        self.assertEqual((off.returncode, on.returncode), (2, 2))
        self.assertEqual(off.stderr.replace(str(self.proj), ""), on.stderr.replace(str(self.proj), ""))
        self.assertEqual(on.stdout, "")
        rec = [r for r in self.records() if r["name"] == "addit.gate.verdict"]
        self.assertEqual([(r["addit.gate.name"], r["addit.gate.verdict"]) for r in rec], [("plan_approval", "blocked")])

    def test_pass_is_unchanged_and_recorded(self):
        pay = self.payload(self.plan("# plan\n> dev-flow: approved\n"))
        off, on = self.run_hook("gate-dev-flow-implement.sh", pay, opt="false"), self.run_hook("gate-dev-flow-implement.sh", pay)
        self.assertEqual((off.returncode, on.returncode, on.stdout, on.stderr), (0, 0, "", ""))
        rec = [r for r in self.records() if r["name"] == "addit.gate.verdict"]
        self.assertEqual([(r["addit.gate.verdict"], "addit.devflow.slug_hash" in r) for r in rec], [("pass", True)])

    def test_off_and_non_dev_flow_write_nothing(self):
        self.run_hook("gate-dev-flow-implement.sh", self.payload("0" * 64), opt="false")
        other = self.payload("0" * 64)
        other["tool_input"]["scriptPath"] = "/p/workflows/other.js"
        proc = self.run_hook("gate-dev-flow-implement.sh", other)
        self.assertEqual(proc.returncode, 0)
        self.assertFalse(self.root.exists())

    def test_telemetry_failure_never_changes_the_decision(self):
        self.root.parent.joinpath("telemetry").write_text("a file, not a directory")
        self.assertEqual(self.run_hook("gate-dev-flow-implement.sh", self.payload("0" * 64)).returncode, 2)
        self.assertEqual(self.run_hook("gate-dev-flow-implement.sh", self.payload(self.plan("> dev-flow: approved\n"))).returncode, 0)


class TestFrontendCheck(HookSandbox):
    def edit(self, lines, name="Big.tsx"):
        f = self.proj / "src/components" / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("const a = 1\n" * lines)
        return {**BASE, "hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {"file_path": str(f)},
                "agent_type": "addit-harness:frontend-developer", "agent_id": "fe1"}

    def test_cap_and_advice_recorded_and_advisory_unchanged(self):
        for n, sev, text in ((260, "cap", "FC-1 (hard cap)"), (200, "advice", "> 150")):
            pay = self.edit(n)
            off, on = self.run_hook("fe-contract-check.sh", pay, opt="false"), self.run_hook("fe-contract-check.sh", pay)
            self.assertEqual((off.returncode, on.returncode), (0, 0))
            self.assertEqual(off.stdout, on.stdout)
            self.assertIn(text, on.stdout)
            self.assertEqual(self.records()[-1]["addit.fc.severity"], sev)
        rec = [r for r in self.records() if r["name"] == "addit.fc.violation"]
        self.assertEqual([(r["addit.fc.severity"], r["addit.fc.count"], r["gen_ai.agent.name"]) for r in rec],
                         [("cap", 260, "frontend-developer"), ("advice", 200, "frontend-developer")])

    def test_small_file_and_off_record_nothing(self):
        self.assertEqual(self.run_hook("fe-contract-check.sh", self.edit(20)).stdout, "")
        self.assertFalse(self.root.exists())
        self.run_hook("fe-contract-check.sh", self.edit(260), opt="false")
        self.assertFalse(self.root.exists())


class TestSetupVersion(HookSandbox):
    def run_setup(self, opt="true"):
        return self.run_hook("check-setup-version.sh", {**BASE, "hook_event_name": "SessionStart", "source": "startup"}, opt=opt)

    def state(self):
        return [r["addit.setup.state"] for r in self.records() if r["name"] == "addit.setup.state"]

    def current_hash(self):
        out = subprocess.run(["bash", "-c", 'eval "$(sed -n "/^setup_content_hash()/,/^}/p" "$1")"; setup_content_hash "$2"', "_",
                              str(HOOKS / "check-setup-version.sh"), str(REPO)], capture_output=True, text=True)
        return out.stdout.strip()

    def test_absent(self):
        proc = self.run_setup()
        self.assertEqual((proc.returncode, proc.stdout, self.state()), (0, "", ["absent"]))

    def test_unmanaged_when_plugin_named_file_without_marker(self):
        (self.home / ".claude/AGENTS.md").write_text("mine\n")
        proc = self.run_setup()
        self.assertEqual((proc.returncode, proc.stdout, self.state()), (0, "", ["unmanaged"]))

    def test_ok_and_drift_from_marker_with_reminder_unchanged(self):
        marker = self.home / ".claude/.addit-harness-setup-version"
        marker.write_text(self.current_hash() + "\n0.3.0\n")
        proc = self.run_setup()
        self.assertEqual((proc.returncode, proc.stdout, self.state()), (0, "", ["ok"]))
        marker.write_text("deadbeef\n0.1.0\n")
        on, off = self.run_setup(), self.run_setup(opt="false")
        self.assertEqual(on.stdout, off.stdout)
        self.assertIn("run /addit-harness:setup", on.stdout)
        self.assertEqual(self.state(), ["ok", "drift"])

    def test_off_writes_nothing(self):
        (self.home / ".claude/AGENTS.md").write_text("mine\n")
        self.run_setup(opt="false")
        self.assertFalse(self.root.exists())


if __name__ == "__main__":
    unittest.main()
