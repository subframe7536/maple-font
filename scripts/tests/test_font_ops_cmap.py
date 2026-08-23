from __future__ import annotations

import unittest
from typing import TYPE_CHECKING, cast

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from scripts.font_ops.merge import merge_cmap_entries

if TYPE_CHECKING:
    from scripts.font_ops.fonttools import TTFont


def build_cmap_font(cmap: dict[int, str]) -> TTFont:
    glyph_order = [".notdef", *dict.fromkeys(cmap.values())]
    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(cmap)
    builder.setupGlyf({name: TTGlyphPen(None).glyph() for name in glyph_order})
    builder.setupHorizontalMetrics(dict.fromkeys(glyph_order, (600, 0)))
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable({"familyName": "Test", "styleName": "Regular"})
    builder.setupOS2()
    builder.setupPost()
    builder.setupMaxp()
    return cast("TTFont", builder.font)


class FontOpsCmapTest(unittest.TestCase):
    def test_merge_respects_subtable_ranges_and_existing_mappings(self) -> None:
        base = build_cmap_font({0x41: "existing", 0x10001: "existing-supp"})
        extra = build_cmap_font(
            {
                0x41: "replacement",
                0x42: "new-bmp",
                0x10000: "new-supp",
            }
        )

        merged = merge_cmap_entries(
            base,
            extra,
            {"replacement", "new-bmp", "new-supp"},
        )

        self.assertEqual(merged, {0x42, 0x10000})
        self.assertEqual((base["cmap"].getBestCmap() or {})[0x41], "existing")
        format_4 = next(table for table in base["cmap"].tables if table.format == 4)
        format_12 = next(table for table in base["cmap"].tables if table.format == 12)
        self.assertEqual(format_4.cmap[0x42], "new-bmp")
        self.assertNotIn(0x10000, format_4.cmap)
        self.assertEqual(format_12.cmap[0x10000], "new-supp")


if __name__ == "__main__":
    unittest.main()
