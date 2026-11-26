from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from ttfautohint import StemWidthMode

from scripts.config.resolver import BuildConfigResolver
from scripts.font_ops.fonttools import load_font
from scripts.font_ops.hinting import get_ttfautohint_options
from scripts.pipeline.base_fonts import build_mono_autohint


class StaticAutoHintTest(unittest.TestCase):
    def test_powerline_outline_is_not_hinted_with_missing_blue_zones(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "base.ttf"
            target = Path(tmp) / "hinted.ttf"
            builder = FontBuilder(1000, isTTF=True)
            glyphs = {".notdef": TTGlyphPen(None).glyph()}
            for name, points in {
                "o": [(70, 0), (70, 500), (520, 500), (520, 0)],
                "A": [(65, 0), (65, 720), (530, 720), (530, 0)],
                "uniE0B0": [
                    (10, 1020),
                    (600, 360),
                    (10, -300),
                    (-40, -300),
                    (-40, 1020),
                ],
            }.items():
                pen = TTGlyphPen(None)
                pen.moveTo(points[0])
                for point in points[1:]:
                    pen.lineTo(point)
                pen.closePath()
                glyphs[name] = pen.glyph()
            builder.setupGlyphOrder(list(glyphs))
            builder.setupCharacterMap({ord("o"): "o", ord("A"): "A", 0xE0B0: "uniE0B0"})
            builder.setupGlyf(glyphs)
            builder.setupHorizontalMetrics(
                {
                    name: (600, lsb)
                    for name, lsb in zip(glyphs, (0, 70, 65, -40), strict=True)
                }
            )
            builder.setupHorizontalHeader(ascent=1020, descent=-300)
            builder.setupNameTable(
                {"familyName": "Hint Fixture", "styleName": "Regular"}
            )
            builder.setupOS2(
                sTypoAscender=1020,
                sTypoDescender=-300,
                usWinAscent=1020,
                usWinDescent=300,
            )
            builder.setupPost()
            builder.save(source)

            build_mono_autohint(
                source, source, target, BuildConfigResolver().load_defaults()
            )

            with load_font(target) as font:
                cmap = font.getBestCmap() or {}
                glyf = font.table("glyf")
                self.assertTrue(glyf[cmap[ord("o")]].program.getBytecode())
                self.assertFalse(glyf[cmap[0xE0B0]].program.getBytecode())
                self.assertTrue(all(tag in font for tag in ("cvt ", "fpgm", "prep")))


class AutoHintOptionsTest(unittest.TestCase):
    def test_converts_stem_width_modes_without_mutating_config(self) -> None:
        params = {
            "hinting_limit": 180,
            "stem_width_mode": {
                "gray": "natural",
                "dw_cleartype": "quantized",
            },
        }

        options = get_ttfautohint_options(params)

        self.assertEqual(params["stem_width_mode"]["gray"], "natural")
        self.assertEqual(options["hinting_limit"], 180)
        self.assertNotIn("stem_width_mode", options)
        self.assertEqual(options["gray_stem_width_mode"], StemWidthMode.NATURAL)
        self.assertEqual(
            options["dw_cleartype_stem_width_mode"], StemWidthMode.QUANTIZED
        )

    def test_rejects_unknown_stem_width_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown stem width mode"):
            get_ttfautohint_options({"stem_width_mode": {"gray": "unsupported"}})
