"""changelog-section.sh and changelog-release.sh against fixture CHANGELOGs (release.yml's changelog handling).

Runs the real scripts in a temp dir; nothing here touches git, GitHub or the repo's CHANGELOG.md.
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / ".github/scripts"
SECTION = SCRIPTS / "changelog-section.sh"
RELEASE = SCRIPTS / "changelog-release.sh"

HEAD = "# Changelog\n\nIntro.\n\n"
FENCED = HEAD + """## [Unreleased]

### Added

- New thing.

```md
## [9.9.9] - not a heading, inside a fence
```

- After the fence.

## [1.0.0] - 2026-01-01

- Old.
"""


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.file = Path(self._tmp.name) / "CHANGELOG.md"

    def write(self, text):
        self.file.write_text(text)

    def section(self, *args):
        return subprocess.run(["bash", str(SECTION), *args, str(self.file)], capture_output=True, text=True, timeout=30)


class TestSection(Base):
    def test_missing_file_fails(self):
        proc = self.section("Unreleased")
        self.assertNotEqual(proc.returncode, 0)

    def test_missing_section_fails(self):
        self.write(HEAD + "## [Unreleased]\n\n- x\n")
        proc = self.section("1.2.3")
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")

    def test_prints_body_without_heading_or_surrounding_blanks(self):
        self.write(HEAD + "## [Unreleased]\n\n\n- a\n- b\n\n\n## [1.0.0] - d\n\n- old\n")
        proc = self.section("Unreleased")
        self.assertEqual((proc.returncode, proc.stdout), (0, "- a\n- b\n"))

    def test_heading_inside_fence_does_not_end_section(self):
        self.write(FENCED)
        proc = self.section("Unreleased")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("- After the fence.", proc.stdout)
        self.assertIn("## [9.9.9]", proc.stdout)
        self.assertNotIn("- Old.", proc.stdout)

    def test_fenced_heading_is_not_a_section(self):
        self.write(FENCED)
        self.assertNotEqual(self.section("9.9.9").returncode, 0)

    def test_trailing_link_references_are_excluded(self):
        self.write(HEAD + "## [1.0.0] - d\n\n- old\n\n[Unreleased]: https://x/compare/v1.0.0...HEAD\n[1.0.0]: https://x/v1.0.0\n")
        proc = self.section("1.0.0")
        self.assertEqual((proc.returncode, proc.stdout), (0, "- old\n"))

    def test_v_prefixed_heading_matches_bare_version(self):
        self.write(HEAD + "## [v1.2.3] - d\n\n- notes\n")
        self.assertEqual(self.section("1.2.3").stdout, "- notes\n")
        self.assertEqual(self.section("v1.2.3").stdout, "- notes\n")

    def test_version_match_is_exact(self):
        self.write(HEAD + "## [1.2.30] - d\n\n- other\n")
        self.assertNotEqual(self.section("1.2.3").returncode, 0)

    def test_empty_section_prints_nothing_but_succeeds(self):
        self.write(HEAD + "## [Unreleased]\n\n## [1.0.0] - d\n\n- old\n")
        proc = self.section("Unreleased")
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_require_nonempty_fails_on_empty_unreleased(self):
        self.write(HEAD + "## [Unreleased]\n\n## [1.0.0] - d\n\n- old\n")
        proc = self.section("--require-nonempty", "Unreleased")
        self.assertNotEqual(proc.returncode, 0)

    def test_require_nonempty_fails_on_links_only_section(self):
        self.write(HEAD + "## [Unreleased]\n\n[Unreleased]: https://x\n")
        self.assertNotEqual(self.section("--require-nonempty", "Unreleased").returncode, 0)

    def test_require_nonempty_passes_with_notes(self):
        self.write(HEAD + "## [Unreleased]\n\n- a\n")
        proc = self.section("--require-nonempty", "Unreleased")
        self.assertEqual((proc.returncode, proc.stdout), (0, "- a\n"))


class TestRelease(Base):
    def release(self, version="1.2.3", date="2026-10-01"):
        return subprocess.run(["bash", str(RELEASE), version, date, str(self.file)], capture_output=True, text=True, timeout=30)

    def test_renames_unreleased_and_inserts_a_fresh_one(self):
        self.write(HEAD + "## [Unreleased]\n\n- a\n\n## [1.0.0] - 2026-01-01\n\n- old\n")
        self.assertEqual(self.release().returncode, 0)
        self.assertEqual(
            self.file.read_text(),
            HEAD + "## [Unreleased]\n\n## [1.2.3] - 2026-10-01\n\n- a\n\n## [1.0.0] - 2026-01-01\n\n- old\n",
        )

    def test_released_section_is_the_release_body_and_unreleased_is_empty(self):
        self.write(FENCED)
        self.assertEqual(self.release().returncode, 0)
        body = self.section("--require-nonempty", "1.2.3")
        self.assertEqual(body.returncode, 0)
        self.assertIn("- After the fence.", body.stdout)
        self.assertEqual(self.section("Unreleased").stdout, "")

    def test_second_release_needs_new_notes(self):
        self.write(HEAD + "## [Unreleased]\n\n- a\n")
        self.release()
        self.assertNotEqual(self.section("--require-nonempty", "Unreleased").returncode, 0)

    def test_unreleased_heading_inside_fence_is_left_alone(self):
        self.write(HEAD + "```md\n## [Unreleased]\n```\n\n## [Unreleased]\n\n- a\n")
        self.assertEqual(self.release().returncode, 0)
        self.assertTrue(self.file.read_text().startswith(HEAD + "```md\n## [Unreleased]\n```\n\n## [Unreleased]\n\n## [1.2.3] - 2026-10-01\n"))

    def test_missing_section_fails_and_leaves_the_file(self):
        self.write(HEAD + "## [1.0.0] - d\n")
        self.assertNotEqual(self.release().returncode, 0)
        self.assertEqual(self.file.read_text(), HEAD + "## [1.0.0] - d\n")

    def test_missing_file_fails(self):
        self.assertNotEqual(self.release().returncode, 0)


if __name__ == "__main__":
    unittest.main()
