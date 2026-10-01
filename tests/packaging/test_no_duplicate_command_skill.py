import pathlib
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]


class TestNoDuplicateCommandSkill(unittest.TestCase):
    """Claude Code lists a command and a skill with the same name as two picker entries
    (anthropics/claude-code#88050); skills are the slash commands, so no commands/<name>.md
    may share a name with skills/<name>/ or workflows/<name>.js."""

    def test_no_command_shares_a_name_with_a_skill_or_workflow(self):
        names = {p.name for p in (REPO / "skills").iterdir() if p.is_dir()}
        names |= {p.stem for p in (REPO / "workflows").glob("*.js")}
        commands = {p.stem for p in (REPO / "commands").glob("*.md")} if (REPO / "commands").is_dir() else set()
        self.assertEqual(sorted(commands & names), [])


if __name__ == "__main__":
    unittest.main()
