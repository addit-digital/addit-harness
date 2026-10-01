import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
SKILL = (REPO / "skills/dev-flow/SKILL.md").read_text()


class TestDevFlowCallsWorkflowsByName(unittest.TestCase):
    """The Workflow tool refuses a scriptPath outside the project / added folders, and an
    installed plugin lives in ~/.claude/plugins/cache. The skill must call by name."""

    def test_no_scriptpath_into_the_plugin_root(self):
        self.assertNotRegex(SKILL, r'scriptPath:\s*"\$\{CLAUDE_PLUGIN_ROOT\}')

    def test_each_workflow_is_called_by_its_namespaced_name(self):
        for wf in ("triage", "design", "implement"):
            self.assertIn('name: "addit-harness:dev-flow-%s"' % wf, SKILL)
            self.assertTrue((REPO / ("workflows/dev-flow-%s.js" % wf)).is_file())

    def test_fallback_says_it_must_announce_before_intake(self):
        self.assertRegex(SKILL, r"tell the user first that the scripted workflow is\s+unavailable")


if __name__ == "__main__":
    unittest.main()
