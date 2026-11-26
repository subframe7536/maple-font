from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.font_ops.variable_hinting import autohint_variable_han
from scripts.tests.cjk_font_fixtures import build_test_font, roundtrip_font
from scripts.utils.errors import BuildDependencyError


class VariableHintingTest(unittest.TestCase):
    def test_only_han_instructions_are_added(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            with build_test_font(root / "input.ttf", variable=True) as font:
                preserved = {
                    tag: font.getTableData(tag)
                    for tag in ("fvar", "gvar", "cmap", "hmtx")
                }
                self.assertEqual(autohint_variable_han(font), 1)
                with roundtrip_font(font, root / "output.ttf") as output:
                    for tag, data in preserved.items():
                        self.assertEqual(output.getTableData(tag), data, tag)
                    glyphs = output.table("glyf")
                    bytecode = glyphs["cjk"].program.getBytecode()
                    self.assertTrue(bytecode)
                    self.assertEqual(
                        output.table("maxp").maxSizeOfInstructions, len(bytecode)
                    )
                    self.assertFalse(glyphs["box"].program.getBytecode())
                    with self.assertRaisesRegex(BuildDependencyError, "existing hints"):
                        autohint_variable_han(output)

    def test_rejects_static_or_glyphless_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            with (
                build_test_font(root / "static.ttf") as font,
                self.assertRaisesRegex(
                    BuildDependencyError, "requires a TrueType variable font"
                ),
            ):
                autohint_variable_han(font)
            with (
                build_test_font(
                    root / "latin.ttf", variable=True, glyph_order=[".notdef", "box"]
                ) as font,
                self.assertRaisesRegex(BuildDependencyError, "no eligible Han glyphs"),
            ):
                autohint_variable_han(font)

    def test_rejects_empty_generated_bytecode(self) -> None:
        with (
            tempfile.TemporaryDirectory() as temporary_dir,
            build_test_font(Path(temporary_dir) / "input.ttf", variable=True) as font,
            patch("scripts.font_ops.variable_hinting._alignment_program") as make,
            self.assertRaisesRegex(BuildDependencyError, "invalid program size"),
        ):
            make.return_value.getBytecode.return_value = b""
            autohint_variable_han(font)
