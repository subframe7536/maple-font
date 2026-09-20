from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fontTools.designspaceLib import AxisDescriptor, SourceDescriptor
from ufoLib2 import Font as UFOFont

from scripts.config.base import INSTANCE_WEIGHT_MAPPING
from scripts.font_ops.glyphs import (
    prepare_designspace_source,
)
from scripts.task.designspace import (
    _canonicalize_platform_sensitive_glyphs,
    convert_glyphs_source,
    prepare_static_source,
    write_designspace_source,
)
from scripts.tests.test_font_generation import write_glyphs_fixture


class DesignspaceTaskTest(unittest.TestCase):
    @staticmethod
    def _tag_source(weight: int) -> SourceDescriptor:
        source = SourceDescriptor()
        source.location = {"Weight": weight}
        source.font = UFOFont()
        return source

    @staticmethod
    def _draw_test_glyph(
        font: UFOFont,
        name: str,
        *,
        width: float,
        offset: tuple[float, float],
    ) -> None:
        glyph = font.newGlyph(name)
        glyph.width = width
        pen = glyph.getPen()
        pen.moveTo(offset)
        pen.lineTo((offset[0] + 10, offset[1]))
        pen.lineTo((offset[0] + 10, offset[1] + 10))
        pen.closePath()
        glyph.contours[0].points[0].smooth = True

    def _tag_sources(
        self, middle_offset: tuple[float, float]
    ) -> list[SourceDescriptor]:
        sources = [self._tag_source(weight) for weight in (100, 400, 800)]
        for source, offset, width in zip(
            sources,
            ((0.5, -0.5), middle_offset, (14.5, 13.5)),
            (500.5, 999.5, 640.5),
            strict=True,
        ):
            assert source.font is not None
            self._draw_test_glyph(
                source.font,
                "tag_demo.liga",
                width=width,
                offset=offset,
            )
            self._draw_test_glyph(
                source.font,
                "A.bg",
                width=width,
                offset=offset,
            )
            self._draw_test_glyph(
                source.font,
                "a",
                width=width,
                offset=(0.5, -0.5),
            )
        return sources

    def test_platform_sensitive_glyphs_use_quantized_endpoint_interpolation(
        self,
    ) -> None:
        sources = self._tag_sources((999.5, 999.5))
        low, middle, high = sources
        assert low.font is not None
        assert middle.font is not None
        assert high.font is not None
        original_types = [
            (point.type, point.smooth)
            for point in middle.font["tag_demo.liga"].contours[0]
        ]

        _canonicalize_platform_sensitive_glyphs(sources, middle, "Weight")

        self.assertEqual(low.font["tag_demo.liga"].width, 501)
        self.assertEqual(middle.font["tag_demo.liga"].width, 561)
        self.assertEqual(high.font["tag_demo.liga"].width, 641)
        self.assertEqual(
            [(point.x, point.y) for point in middle.font["tag_demo.liga"].contours[0]],
            [(7, 6), (17, 6), (17, 16)],
        )
        self.assertEqual(
            [
                (point.type, point.smooth)
                for point in middle.font["tag_demo.liga"].contours[0]
            ],
            original_types,
        )
        self.assertEqual(middle.font["A.bg"].width, 561)
        self.assertEqual(
            [(point.x, point.y) for point in middle.font["A.bg"].contours[0]],
            [(7, 6), (17, 6), (17, 16)],
        )
        self.assertEqual(
            [(point.x, point.y) for point in middle.font["a"].contours[0]],
            [(0.5, -0.5), (10.5, -0.5), (10.5, 9.5)],
        )

    def test_tag_glyph_serialization_ignores_middle_master_geometry(self) -> None:
        first_sources = self._tag_sources((100, 100))
        second_sources = self._tag_sources((-100, -100))

        _canonicalize_platform_sensitive_glyphs(
            first_sources, first_sources[1], "Weight"
        )
        _canonicalize_platform_sensitive_glyphs(
            second_sources, second_sources[1], "Weight"
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, sources in (("first", first_sources), ("second", second_sources)):
                middle_font = sources[1].font
                assert middle_font is not None
                middle_font.save(root / f"{name}.ufo", overwrite=True)

            self.assertEqual(
                (root / "first.ufo/glyphs/tag_demo.liga.glif").read_bytes(),
                (root / "second.ufo/glyphs/tag_demo.liga.glif").read_bytes(),
            )
            self.assertEqual(
                (root / "first.ufo/glyphs/A_.bg.glif").read_bytes(),
                (root / "second.ufo/glyphs/A_.bg.glif").read_bytes(),
            )

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
