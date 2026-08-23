from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fontTools.ttLib import newTable

from scripts.cjk.variable import (
    get_unicode_cmap,
    merge_vf,
    rebuild_weight_masters_with_regular_default,
    skew_glyphs,
    variation_scalar,
)
from scripts.font_ops.fonttools import instantiate_variable_font
from scripts.font_ops.glyph_transform import reduce_glyph_side_bearings
from scripts.tests.cjk_font_fixtures import (
    CMAP,
    GLYPH_ORDER,
    build_test_font,
    glyph_coordinates,
    roundtrip_font,
)


class CJKVariableOperationsTest(unittest.TestCase):
    def test_variation_scalar_follows_normalized_support_region(self) -> None:
        support = (-1.0, 0.5, 1.0)

        self.assertEqual(variation_scalar(support, -1.1), 0.0)
        self.assertEqual(variation_scalar(support, -0.25), 0.5)
        self.assertEqual(variation_scalar(support, 0.5), 1.0)
        self.assertEqual(variation_scalar(support, 0.75), 0.5)
        self.assertEqual(variation_scalar(support, 1.1), 0.0)

    def test_reduce_side_bearings_preserves_variable_glyph_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            font = build_test_font(root / "variable.ttf", variable=True)
            font["hmtx"].metrics.update(
                {
                    "box": (600, 50),
                    "box.component": (600, 90),
                    "cjk": (1200, 80),
                }
            )
            original_coordinates = {
                glyph_name: glyph_coordinates(font, glyph_name)
                for glyph_name in ("box", "box.component", "cjk")
            }
            original_variations = {
                glyph_name: [
                    list(variation.coordinates or ())
                    for variation in font["gvar"].variations[glyph_name]
                ]
                for glyph_name in ("box", "box.component", "cjk")
            }

            reduce_glyph_side_bearings(
                font,
                ("box", "box.component", "cjk"),
                {600: 550, 1200: 1100},
            )
            adjusted = roundtrip_font(font, root / "adjusted.ttf")
            self.addCleanup(adjusted.close)

            self.assertEqual(adjusted["hmtx"].metrics["box"], (550, 25))
            self.assertEqual(adjusted["hmtx"].metrics["box.component"], (550, 65))
            self.assertEqual(adjusted["hmtx"].metrics["cjk"], (1100, 30))
            for glyph_name, shift_x in (
                ("box", -25),
                ("box.component", -25),
                ("cjk", -50),
            ):
                self.assertEqual(
                    glyph_coordinates(adjusted, glyph_name),
                    [(x + shift_x, y) for x, y in original_coordinates[glyph_name]],
                )
                self.assertEqual(
                    [
                        list(variation.coordinates or ())
                        for variation in adjusted["gvar"].variations[glyph_name]
                    ],
                    original_variations[glyph_name],
                )

    def test_merge_preserves_font_data_and_invalidates_metric_variations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = build_test_font(
                root / "base.ttf",
                glyph_order=GLYPH_ORDER[:3],
                variable=True,
            )
            extra = build_test_font(
                root / "extra.ttf",
                cjk_width=460,
                variable=True,
            )
            self.addCleanup(extra.close)
            expected_metric = extra["hmtx"].metrics["cjk"]
            expected_base_metric = base["hmtx"].metrics["box"]
            expected_variations = [
                (variation.axes, list(variation.coordinates or ()))
                for variation in extra["gvar"].variations["cjk"]
            ]
            base["HVAR"] = newTable("HVAR")
            base["VVAR"] = newTable("VVAR")

            merged, added_glyphs, added_codepoints = merge_vf(base, extra)
            reopened = roundtrip_font(merged, root / "merged.ttf")
            self.addCleanup(reopened.close)

            self.assertEqual(added_glyphs, ["cjk"])
            self.assertEqual(added_codepoints, 1)
            self.assertEqual(reopened.getGlyphOrder(), GLYPH_ORDER)
            self.assertEqual(get_unicode_cmap(reopened), CMAP)
            self.assertEqual(reopened["hmtx"].metrics["cjk"], expected_metric)
            self.assertEqual(reopened["hmtx"].metrics["box"], expected_base_metric)
            axis = reopened["fvar"].axes[0]
            self.assertEqual(
                (axis.axisTag, axis.minValue, axis.defaultValue, axis.maxValue),
                ("wght", 100, 400, 900),
            )
            self.assertEqual(
                [
                    (variation.axes, list(variation.coordinates or ()))
                    for variation in reopened["gvar"].variations["cjk"]
                ],
                expected_variations,
            )
            self.assertNotIn("HVAR", reopened)
            self.assertNotIn("VVAR", reopened)

    def test_rebuild_weight_masters_roundtrips_min_default_and_max(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            variable = build_test_font(
                root / "variable.ttf",
                box_width=280,
                cjk_width=380,
                variable=True,
            )
            masters = [
                build_test_font(
                    root / f"master-{weight}.ttf",
                    box_width=box_width,
                    cjk_width=cjk_width,
                )
                for weight, box_width, cjk_width in (
                    (100, 240, 340),
                    (400, 320, 420),
                    (900, 420, 540),
                )
            ]
            variable["HVAR"] = newTable("HVAR")
            variable["MVAR"] = newTable("MVAR")
            variable["avar"] = newTable("avar")

            min_master, regular_master, max_master = masters
            rebuild_weight_masters_with_regular_default(
                variable, min_master, regular_master, max_master
            )
            rebuilt = roundtrip_font(variable, root / "rebuilt.ttf")
            self.addCleanup(rebuilt.close)

            self.assertNotIn("HVAR", rebuilt)
            self.assertNotIn("MVAR", rebuilt)
            self.assertNotIn("avar", rebuilt)
            for weight, master in zip((100, 400, 900), masters, strict=False):
                instance = instantiate_variable_font(
                    rebuilt, {"wght": weight}, static=True
                )
                reopened = roundtrip_font(instance, root / f"instance-{weight}.ttf")
                try:
                    self.assertEqual(reopened.getGlyphOrder(), master.getGlyphOrder())
                    for glyph_name in GLYPH_ORDER:
                        self.assertEqual(
                            glyph_coordinates(reopened, glyph_name),
                            glyph_coordinates(master, glyph_name),
                        )
                        self.assertEqual(
                            reopened["hmtx"].metrics[glyph_name],
                            master["hmtx"].metrics[glyph_name],
                        )
                finally:
                    reopened.close()
                    master.close()

    def test_skew_preserves_advances_and_recomputes_simple_and_composite_lsbs(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            font = build_test_font(root / "upright.ttf")
            original_advances = {
                glyph_name: font["hmtx"].metrics[glyph_name][0]
                for glyph_name in ("box", "box.component")
            }
            original_coordinates = glyph_coordinates(font, "box")

            skew_glyphs(font, 12)
            skewed = roundtrip_font(font, root / "skewed.ttf")
            self.addCleanup(skewed.close)

            self.assertNotEqual(glyph_coordinates(skewed, "box"), original_coordinates)
            for glyph_name in ("box", "box.component"):
                glyph = skewed["glyf"][glyph_name]
                glyph.recalcBounds(skewed["glyf"])
                advance, lsb = skewed["hmtx"].metrics[glyph_name]
                self.assertEqual(advance, original_advances[glyph_name])
                self.assertEqual(lsb, glyph.xMin)
                self.assertLess(glyph.xMin, glyph.xMax)
                self.assertLess(glyph.yMin, glyph.yMax)


if __name__ == "__main__":
    unittest.main()
