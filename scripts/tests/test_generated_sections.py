from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.task.fea import replace_section


class GeneratedSectionTest(unittest.TestCase):
    def test_requires_exactly_one_section(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "README.md"
            target.write_text("no marker", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly one"):
                replace_section(str(target), "<!-- X -->", "value")

            target.write_text("<!-- X -->" * 4, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly one"):
                replace_section(str(target), "<!-- X -->", "value")

    def test_replaces_single_section(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "README.md"
            target.write_text("<!-- X -->old<!-- X -->", encoding="utf-8")
            replace_section(str(target), "<!-- X -->", "new")
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                "<!-- X -->\nnew\n<!-- X -->",
            )
