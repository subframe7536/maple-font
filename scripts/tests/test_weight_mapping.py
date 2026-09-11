from __future__ import annotations

import unittest

from scripts.font_ops.glyphs import _apply_designspace_weight_mapping
from fontTools.designspaceLib import (
    AxisDescriptor,
    DesignSpaceDocument,
    InstanceDescriptor,
    SourceDescriptor,
)


STYLE_DESIGN_WEIGHTS = (
    ("Thin", 100),
    ("ExtraLight", 210),
    ("Light", 320),
    ("Regular", 400),
    ("Medium", 490),
    ("SemiBold", 570),
    ("Bold", 680),
    ("ExtraBold", 800),
)


def make_designspace() -> DesignSpaceDocument:
    designspace = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.tag = "wght"
    axis.name = "Weight"
    axis.minimum = 100
    axis.maximum = 800
    axis.default = 400
    axis.map = list(
        zip(
            (100, 200, 300, 400, 500, 600, 700, 800),
            (100, 210, 320, 400, 490, 570, 680, 800),
            strict=True,
        )
    )
    designspace.addAxis(axis)

    for style_name, design_weight in (
        ("Thin", 100),
        ("Regular", 400),
        ("ExtraBold", 800),
    ):
        source = SourceDescriptor()
        source.name = f"Fixture {style_name}"
        source.styleName = style_name
        source.location = {"Weight": design_weight}
        source.font = object()
        designspace.addSource(source)

    for style_name, design_weight in STYLE_DESIGN_WEIGHTS:
        instance = InstanceDescriptor()
        instance.name = f"Fixture {style_name}"
        instance.styleName = style_name
        instance.designLocation = {"Weight": design_weight}
        designspace.addInstance(instance)

    return designspace


class WeightMappingTest(unittest.TestCase):
    def test_custom_regular_weight_remains_default_master(self) -> None:
        designspace = make_designspace()
        mapping = {
            "thin": 100,
            "extralight": 200,
            "light": 250,
            "regular": 300,
            "medium": 400,
            "semibold": 500,
            "bold": 600,
            "extrabold": 800,
        }

        _apply_designspace_weight_mapping(designspace, mapping)

        axis = designspace.axes[0]
        self.assertEqual(axis.default, 300)
        self.assertEqual(axis.map_forward(axis.default), 400)
        default_source = designspace.findDefault()
        self.assertIsNotNone(default_source)
        assert default_source is not None
        self.assertEqual(default_source.styleName, "Regular")

    def test_non_monotonic_weight_mapping_is_rejected(self) -> None:
        designspace = make_designspace()
        mapping = {
            "thin": 100,
            "extralight": 200,
            "light": 250,
            "regular": 300,
            "medium": 400,
            "semibold": 350,
            "bold": 500,
            "extrabold": 800,
        }

        with self.assertRaisesRegex(
            ValueError,
            "unique and strictly increase from Thin to ExtraBold",
        ):
            _apply_designspace_weight_mapping(designspace, mapping)

    def test_duplicate_weight_mapping_is_rejected(self) -> None:
        designspace = make_designspace()
        mapping = {
            "thin": 100,
            "extralight": 200,
            "light": 250,
            "regular": 300,
            "medium": 400,
            "semibold": 400,
            "bold": 500,
            "extrabold": 800,
        }

        with self.assertRaisesRegex(
            ValueError,
            "unique and strictly increase from Thin to ExtraBold",
        ):
            _apply_designspace_weight_mapping(designspace, mapping)


if __name__ == "__main__":
    unittest.main()
