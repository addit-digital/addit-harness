"""First-run welcome in hooks/check-setup-version.sh: once per install, interactive only, never model context.

Run: python3 -m unittest discover -s tests/onboarding -v
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks/check-setup-version.sh"
PAYLOAD = {"session_id": "3f2a9c1e-7b4d-4e8a-9c6b-1d2e3f4a5b6c", "hook_event_name": "SessionStart", "source": "startup"}
READY = "addit-harness ready."
NOT_RUN = "addit-harness installed. Run /addit-harness:setup"


class WelcomeCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="welcome-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.home, self.data = self.tmp / "home", self.tmp / "data"
        (self.home / ".claude").mkdir(parents=True)
        self.data.mkdir()
        self.marker = self.data / "onboarding/welcome-v1"

    def run_hook(self, source="startup", entrypoint="cli", data="DEFAULT", raw=None, path=None):
        env = {"PATH": path or os.environ["PATH"], "HOME": str(self.home), "CLAUDE_PLUGIN_ROOT": str(REPO)}
        if data == "DEFAULT":
            data = str(self.data)
        if data is not None:
            env["CLAUDE_PLUGIN_DATA"] = data
        if entrypoint is not None:
            env["CLAUDE_CODE_ENTRYPOINT"] = entrypoint
        proc = subprocess.run(["bash", str(HOOK)], input=raw if raw is not None else json.dumps({**PAYLOAD, "source": source}), capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def set_setup_marker(self, hash_value):
        (self.home / ".claude/.addit-harness-setup-version").write_text(f"{hash_value}\n0.3.0\n")

    def current_hash(self):
        out = subprocess.run(["bash", "-c", 'eval "$(sed -n "/^setup_content_hash()/,/^}/p" "$1")"; setup_content_hash "$2"', "_",
                              str(HOOK), str(REPO)], capture_output=True, text=True)
        return out.stdout.strip()


class TestWelcome(WelcomeCase):
    def test_first_run_emits_once_then_silent(self):
        out = json.loads(self.run_hook())
        self.assertEqual(set(out), {"systemMessage"})  # nothing for the model: no hookSpecificOutput/additionalContext
        self.assertTrue(out["systemMessage"].startswith(NOT_RUN), out)
        self.assertLessEqual(len(out["systemMessage"]), 160)
        self.assertTrue(out["systemMessage"].isascii())
        self.assertTrue(self.marker.is_file())
        self.assertEqual(self.run_hook(), "")

    def test_variant_when_setup_has_run(self):
        self.set_setup_marker(self.current_hash())
        out = json.loads(self.run_hook())
        self.assertTrue(out["systemMessage"].startswith(READY), out)
        self.assertLessEqual(len(out["systemMessage"]), 160)
        self.assertNotIn("hookSpecificOutput", out)

    def test_headless_is_silent_and_leaves_no_marker(self):
        self.assertEqual(self.run_hook(entrypoint="sdk-cli"), "")
        self.assertFalse(self.marker.exists())
        self.assertTrue(json.loads(self.run_hook())["systemMessage"])  # the later interactive start still gets it

    def test_unknown_entrypoint_shows(self):
        self.assertTrue(json.loads(self.run_hook(entrypoint=None))["systemMessage"])

    def test_only_on_startup(self):
        for source in ("resume", "clear", "compact"):
            self.assertEqual(self.run_hook(source=source), "", source)
        self.assertFalse(self.marker.exists())

    def test_startup_text_inside_another_field_is_not_a_startup(self):
        for payload in (
            {**PAYLOAD, "source": "resume", "extra": {"source": "startup"}},
            {**PAYLOAD, "source": "resume", "note": 'x "source": "startup" y'},
            {k: v for k, v in PAYLOAD.items() if k != "source"} | {"extra": {"source": "startup"}},
        ):
            self.assertEqual(self.run_hook(raw=json.dumps(payload)), "", payload)
        self.assertFalse(self.marker.exists())

    def test_malformed_payload_is_silent(self):
        self.assertEqual(self.run_hook(raw="not json"), "")
        self.assertFalse(self.marker.exists())

    def test_startup_with_other_spacing_still_shows(self):
        self.assertTrue(json.loads(self.run_hook(raw='{"hook_event_name":"SessionStart",\n "source" :\t"startup"}'))["systemMessage"])

    def test_emit_failure_leaves_no_marker_so_the_next_start_still_welcomes(self):
        real = shutil.which("python3")
        stub = self.tmp / "bin"
        stub.mkdir()
        (stub / "python3").write_text(f'#!/bin/bash\ncase "$*" in *systemMessage*) exit 1;; esac\nexec {real} "$@"\n')
        (stub / "python3").chmod(0o755)
        self.assertEqual(self.run_hook(path=f"{stub}:{os.environ['PATH']}"), "")
        self.assertFalse(self.marker.exists())
        self.assertTrue(json.loads(self.run_hook())["systemMessage"])

    def test_no_data_dir_is_silent(self):
        self.assertEqual(self.run_hook(data=None), "")
        self.assertEqual(self.run_hook(data=""), "")

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignores directory modes")
    def test_unwritable_data_dir_is_silent_and_exits_zero(self):
        self.data.chmod(0o500)
        self.addCleanup(self.data.chmod, 0o700)
        self.assertEqual(self.run_hook(), "")
        self.assertFalse(self.marker.exists())

    def test_data_path_that_is_a_file_is_silent_and_exits_zero(self):
        blocker = self.tmp / "blocker"
        blocker.write_text("x")
        self.assertEqual(self.run_hook(data=str(blocker)), "")

    def test_existing_marker_is_not_overwritten(self):
        self.marker.parent.mkdir()
        self.marker.write_text("keep")
        self.assertEqual(self.run_hook(), "")
        self.assertEqual(self.marker.read_text(), "keep")


class TestTipsCommand(unittest.TestCase):
    def test_command_and_skill_agree_the_skill_file_is_read_then_printed(self):
        command = (REPO / "commands/tips.md").read_text()
        skill = (REPO / "skills/tips/SKILL.md").read_text()
        self.assertIn("skills/tips/SKILL.md", command)
        self.assertNotIn("no tool calls", skill)

    def test_description_stays_small(self):
        for f in ("commands/tips.md", "skills/tips/SKILL.md"):
            desc = next(l for l in (REPO / f).read_text().splitlines() if l.startswith("description:"))
            self.assertLessEqual(len(desc), 120, f)


class TestWelcomeWithDrift(WelcomeCase):
    def test_one_merged_message_and_only_the_drift_reaches_the_model(self):
        self.set_setup_marker("0" * 64)
        out = json.loads(self.run_hook())
        self.assertTrue(out["systemMessage"].startswith(READY))
        self.assertIn("run /addit-harness:setup to pick up the changes", out["systemMessage"])
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("pick up the changes", ctx)
        self.assertNotIn("addit-harness ready", ctx)
        out2 = json.loads(self.run_hook())  # drift keeps nagging, the welcome does not
        self.assertNotIn("ready", out2["systemMessage"])
        self.assertIn("pick up the changes", out2["systemMessage"])


if __name__ == "__main__":
    unittest.main()
