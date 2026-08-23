from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fontTools.designspaceLib import AxisDescriptor

from scripts.config.base import INSTANCE_WEIGHT_MAPPING
from scripts.font_ops.glyphs import (
    prepare_designspace_source,
)
from scripts.task.designspace import (
    convert_glyphs_source,
    prepare_static_source,
    write_designspace_source,
)
from scripts.tests.test_font_generation import write_glyphs_fixture


class DesignspaceTaskTest(unittest.TestCase):
    def test_italic_filename_produces_unique_master_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "Fixture-Italic.glyphs"
            write_glyphs_fixture(
                source_path,
                {".notdef": ("Thin", "Regular", "ExtraBold")},
            )

            converted = convert_glyphs_source(source_path)

            self.assertEqual(converted.style, "italic")
            self.assertEqual(
                [source.styleName for source in converted.designspace.sources],
                ["ThinItalic", "Italic", "ExtraBoldItalic"],
            )
            self.assertEqual(
                [source.filename for source in converted.designspace.sources],
                [
                    "Fixture-ThinItalic.ufo",
                    "Fixture-Italic.ufo",
                    "Fixture-ExtraBoldItalic.ufo",
                ],
            )

    def test_build_preparation_loads_ufo_and_applies_current_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_path = root / "Fixture.glyphs"
            write_glyphs_fixture(
                source_path,
                {".notdef": ("Thin", "Regular", "ExtraBold")},
            )
            converted = convert_glyphs_source(source_path)
            static_source = prepare_static_source(converted)
            designspace_path = write_designspace_source(
                static_source,
                root / "generated",
                "Fixture.designspace",
            )

            prepared = prepare_designspace_source(
                designspace_path,
                "regular",
                weight_mapping={**INSTANCE_WEIGHT_MAPPING, "regular": 400},
                line_height=1.2,
            )

            axis = prepared.designspace.axes[0]
            self.assertIsInstance(axis, AxisDescriptor)
            assert isinstance(axis, AxisDescriptor)
            self.assertEqual(
                (axis.minimum, axis.default, axis.maximum),
                (100, 400, 800),
            )
            self.assertEqual(prepared.vertical_metric, (800, -200))
            for source in prepared.designspace.sources:
                assert source.font is not None
                self.assertEqual(source.font.info.openTypeHheaAscender, 960)
                self.assertEqual(source.font.info.openTypeHheaDescender, -240)

    def test_missing_generated_source_points_to_generation_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "Missing.designspace"

            with self.assertRaisesRegex(
                FileNotFoundError,
                "task.py designspace",
            ):
                prepare_designspace_source(missing, "regular")


if __name__ == "__main__":
    unittest.main()
