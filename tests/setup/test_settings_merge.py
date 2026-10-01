"""setup.sh merges settings.json key by key for `env`: the user's keys survive and their values win.

Runs the real script against a throwaway $HOME; never touches the real ~/.claude.
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SETUP = REPO / "skills/setup/scripts/setup.sh"
KEY = "CLAUDE_CODE_ENABLE_TODO_TOOLS"


class TestEnvMerge(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.home = Path(self._tmp.name)
        (self.home / ".claude").mkdir()
        self.settings = self.home / ".claude/settings.json"

    def run_setup(self):
        env = {**os.environ, "HOME": str(self.home), "CLAUDE_PLUGIN_ROOT": str(REPO)}
        proc = subprocess.run(["bash", str(SETUP)], capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(self.settings.read_text())

    def test_template_carries_the_key(self):
        self.assertEqual(json.loads((REPO / "settings.json").read_text())["env"][KEY], "1")

    def test_fresh_install_gets_the_key(self):
        self.assertEqual(self.run_setup()["env"], {KEY: "1"})

    def test_user_env_keys_kept_and_key_added(self):
        self.settings.write_text(json.dumps({"env": {"MY_VAR": "a", "OTHER": "b"}, "theme": "dark"}))
        out = self.run_setup()
        self.assertEqual(out["env"], {"MY_VAR": "a", "OTHER": "b", KEY: "1"})
        self.assertEqual(out["theme"], "dark")

    def test_users_own_value_for_the_same_key_wins(self):
        self.settings.write_text(json.dumps({"env": {KEY: "0", "MY_VAR": "a"}}))
        self.assertEqual(self.run_setup()["env"], {KEY: "0", "MY_VAR": "a"})

    def test_non_object_env_is_not_crashed_on(self):
        self.settings.write_text(json.dumps({"env": "oops"}))
        self.assertEqual(self.run_setup()["env"], {KEY: "1"})

    def test_second_run_is_byte_identical(self):
        self.settings.write_text(json.dumps({"env": {"MY_VAR": "a"}}))
        self.run_setup()
        first = self.settings.read_bytes()
        self.run_setup()
        self.assertEqual(self.settings.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
