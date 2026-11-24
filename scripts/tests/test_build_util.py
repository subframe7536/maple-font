from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from scripts.cjk.config import CJKBuildConfig, CJKSourceConfig
from scripts.cjk.presets import build_preset_config, get_preset
from scripts.cjk.static import (
    apply_cjk_width_transform,
)
from scripts.config.base import (
    CJKCommonBuildOptions,
    ResolvedCJKBuildEntry,
)
from scripts.config.resolver import BuildConfigResolver
from scripts.config.runtime import BuildRuntimeContext
from scripts.font_ops.glyph_transform import change_glyph_width_or_scale
from scripts.tests.cjk_font_fixtures import build_test_font


def make_runtime_context() -> BuildRuntimeContext:
    return BuildRuntimeContext(
        src_dir="sources",
        output_root="fonts",
        output_otf="fonts/OTF",
        output_ttf="fonts/TTF",
        output_ttf_hinted="fonts/TTF-AutoHint",
        output_variable="fonts/Variable",
        output_woff2="fonts/Woff2",
        output_nf="fonts/NF",
        ttf_base_dir="fonts/TTF-AutoHint",
        is_nf_built=False,
        is_cjk_built=False,
        effective_github_mirror="github.com",
        font_forge_bin=None,
        resolved_vertical_metric=(1020, -300),
    )


def make_builtin_entry() -> ResolvedCJKBuildEntry:
    return ResolvedCJKBuildEntry(
        entry_id="cn",
        locale_name="CN",
        build_config=build_preset_config("cn"),
        common_options=CJKCommonBuildOptions(fix_meta_table=True),
        is_builtin=True,
        preset_id="cn",
        preset_spec=get_preset("cn"),
    )


def make_custom_entry() -> ResolvedCJKBuildEntry:
    return ResolvedCJKBuildEntry(
        entry_id="custom:hk",
        locale_name="HK",
        build_config=CJKBuildConfig(
            source=CJKSourceConfig(
                path=Path("source.ttf"),
                masters={100: {"wght": 100}, 400: {"wght": 400}, 800: {"wght": 800}},
            ),
            locale_name="HK",
        ),
        common_options=CJKCommonBuildOptions(fix_meta_table=True),
        is_builtin=False,
    )


class PostprocessCJKStaticFontTest(unittest.TestCase):
    def test_nf_propo_width_transform_marks_font_proportional(self) -> None:
        font_config = BuildConfigResolver().load_defaults()
        font_config.nerd_font.propo = True
        font = MagicMock()

        skip_verify = apply_cjk_width_transform(
            font,
            font_config,
            CJKCommonBuildOptions(),
        )

        self.assertFalse(font.table("post").isFixedPitch)
        self.assertEqual(font.table("OS/2").panose.bProportion, 0)
        self.assertEqual(font.table("OS/2").panose.bSpacing, 0)
        self.assertTrue(skip_verify)

    def test_width_transform_scales_composite_offsets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            font = build_test_font(Path(tmp) / "fixture.ttf", box_width=320)

        # box.component (composite, advance=670) and cjk (simple, advance=670)
        # both match; the composite has no `.coordinates` attribute.
        change_glyph_width_or_scale(
            font,
            match_width=670,
            target_width=500,
            scale_factor=(1.0, 1.0),
        )

        hmtx = font["hmtx"].metrics
        self.assertEqual(hmtx["box.component"][0], 500)
        self.assertEqual(hmtx["cjk"][0], 500)
        component = font["glyf"]["box.component"].components[0]
        # Offset shifted by the centering delta: 40 + round((500 - 670) / 2).
        self.assertEqual(component.x, -45)
        # Composite lsb is refreshed from recalculated bounds.
        self.assertEqual(hmtx["box.component"][1], 5)

    def _build_punctuation_test_font(self, path: Path):
        from fontTools.fontBuilder import FontBuilder
        from fontTools.pens.ttGlyphPen import TTGlyphPen

        from scripts.cjk.static import verify_cjk_widths
        from scripts.font_ops.fonttools import load_font
        from scripts.tests.cjk_font_fixtures import roundtrip_font

        self._verify_cjk_widths = verify_cjk_widths
        self._roundtrip_font = roundtrip_font

        def rect(x_min: int, y_min: int, width: int, height: int):
            pen = TTGlyphPen(None)
            pen.moveTo((x_min, y_min))
            pen.lineTo((x_min + width, y_min))
            pen.lineTo((x_min + width, y_min + height))
            pen.lineTo((x_min, y_min + height))
            pen.closePath()
            return pen.glyph()

        glyph_order = [
            ".notdef",
            "latinA",
            "uni4E00",
            "shared.part",
            "uni3001",
            "uni3001.tw",
            "uni3002",
            "uniFF0C",
            "uniFF10",
            "ellipsis.full",
        ]
        glyphs: dict[str, Any] = {
            ".notdef": TTGlyphPen(None).glyph(),
            "latinA": rect(50, 0, 500, 700),
            "uni4E00": rect(100, 100, 800, 800),
            "shared.part": rect(100, 100, 200, 200),
            "uni3001": rect(100, 100, 200, 200),
            "uni3001.tw": rect(500, 400, 200, 200),
            "uniFF0C": rect(100, 100, 200, 200),
            "uniFF10": rect(200, 100, 600, 700),
            "ellipsis.full": rect(100, 400, 1000, 100),
        }
        comp_pen = TTGlyphPen(glyphs)
        comp_pen.addComponent("shared.part", (1, 0, 0, 1, 50, 0))
        glyphs["uni3002"] = comp_pen.glyph()

        metrics = {
            ".notdef": (600, 0),
            "latinA": (600, 50),
            "uni4E00": (1200, 100),
            "shared.part": (1200, 100),
            "uni3001": (1200, 100),
            "uni3001.tw": (1200, 500),
            "uni3002": (1200, 150),
            "uniFF0C": (1200, 100),
            "uniFF10": (1200, 200),
            "ellipsis.full": (1200, 100),
        }
        cmap = {
            0x0041: "latinA",  # Halfwidth Latin A
            0x4E00: "uni4E00",  # CJK Unified Ideograph
            0x3001: "uni3001",  # Ideographic Comma (CJK punctuation)
            0x3002: "uni3002",  # Ideographic Full Stop (composite CJK punctuation)
            0xFF0C: "uniFF0C",  # Fullwidth Comma (Fullwidth ASCII punctuation)
            0xFF10: "uniFF10",  # Fullwidth Digit Zero (not punctuation)
        }

        builder = FontBuilder(1000, isTTF=True)
        builder.setupGlyphOrder(glyph_order)
        builder.setupCharacterMap(cmap)
        builder.setupGlyf(glyphs)
        builder.setupHorizontalMetrics(metrics)
        builder.setupHorizontalHeader(ascent=800, descent=-200)
        builder.setupNameTable(
            {
                "familyName": "Punctuation Fixture",
                "styleName": "Regular",
                "uniqueFontIdentifier": "Punctuation Fixture Regular",
                "fullName": "Punctuation Fixture Regular",
                "psName": "PunctuationFixture-Regular",
            }
        )
        builder.setupOS2(
            sTypoAscender=800,
            sTypoDescender=-200,
            usWinAscent=800,
            usWinDescent=200,
        )
        builder.setupPost()
        builder.setupMaxp()
        builder.setupHead(created=2082844800, modified=2082844800)
        builder.font.recalcTimestamp = False
        builder.save(path)
        return load_font(path)

    def test_scale_punctuation_factor_none_inherits_scale_factor(self) -> None:
        font_config = BuildConfigResolver().load_defaults()
        with tempfile.TemporaryDirectory() as tmp:
            font = self._build_punctuation_test_font(Path(tmp) / "fixture.ttf")

        apply_cjk_width_transform(
            font,
            font_config,
            CJKCommonBuildOptions(
                scale_factor=(1.2, 1.2),
                scale_punctuation_factor=None,
            ),
        )

        # Both CJK ideograph and punctuation scale by 1.2 when punctuation factor is None.
        self.assertEqual(
            font["glyf"]["uni4E00"].yMax - font["glyf"]["uni4E00"].yMin, 960
        )
        self.assertEqual(
            font["glyf"]["uni3001"].yMax - font["glyf"]["uni3001"].yMin, 240
        )
        self.assertEqual(
            font["glyf"]["uniFF0C"].yMax - font["glyf"]["uniFF0C"].yMin, 240
        )

    def test_scale_punctuation_factor_separates_cjk_and_punctuation(self) -> None:
        font_config = BuildConfigResolver().load_defaults()
        with tempfile.TemporaryDirectory() as tmp:
            fixture_path = Path(tmp) / "fixture.ttf"
            font = self._build_punctuation_test_font(fixture_path)

            apply_cjk_width_transform(
                font,
                font_config,
                CJKCommonBuildOptions(
                    scale_factor=(1.2, 1.2),
                    scale_punctuation_factor=(1.0, 1.0),
                ),
            )
            font = self._roundtrip_font(font, Path(tmp) / "out.ttf")

        # CJK ideograph, shared non-punctuation component, and fullwidth digit scale by 1.2.
        self.assertEqual(
            font["glyf"]["uni4E00"].yMax - font["glyf"]["uni4E00"].yMin, 960
        )
        self.assertEqual(
            font["glyf"]["shared.part"].yMax - font["glyf"]["shared.part"].yMin, 240
        )
        self.assertEqual(
            font["glyf"]["uniFF10"].yMax - font["glyf"]["uniFF10"].yMin, 840
        )
        # Fullwidth punctuation, .tw variant, and composite punctuation stay at 1.0.
        self.assertEqual(
            font["glyf"]["uni3001"].yMax - font["glyf"]["uni3001"].yMin, 200
        )
        self.assertEqual(
            font["glyf"]["uni3001.tw"].yMax - font["glyf"]["uni3001.tw"].yMin, 200
        )
        self.assertFalse(font["glyf"]["uni3002"].isComposite())
        self.assertEqual(
            font["glyf"]["uni3002"].yMax - font["glyf"]["uni3002"].yMin, 200
        )
        self.assertEqual(
            font["glyf"]["uniFF0C"].yMax - font["glyf"]["uniFF0C"].yMin, 200
        )
        # special_names continues to use _change_special_cjk_glyph (y-height unchanged).
        self.assertEqual(
            font["glyf"]["ellipsis.full"].yMax - font["glyf"]["ellipsis.full"].yMin,
            100,
        )

    def test_scale_punctuation_factor_alone_triggers_transform(self) -> None:
        font_config = BuildConfigResolver().load_defaults()
        with tempfile.TemporaryDirectory() as tmp:
            font = self._build_punctuation_test_font(Path(tmp) / "fixture.ttf")

        apply_cjk_width_transform(
            font,
            font_config,
            CJKCommonBuildOptions(
                scale_factor=(1.0, 1.0),
                scale_punctuation_factor=(0.9, 0.9),
            ),
        )

        self.assertEqual(
            font["glyf"]["uni4E00"].yMax - font["glyf"]["uni4E00"].yMin, 800
        )
        self.assertEqual(
            font["glyf"]["uni3001"].yMax - font["glyf"]["uni3001"].yMin, 180
        )
        self.assertEqual(
            font["glyf"]["uniFF0C"].yMax - font["glyf"]["uniFF0C"].yMin, 180
        )

    def test_scale_punctuation_factor_alone_preserves_slim_widths(self) -> None:
        font_config = BuildConfigResolver().load_defaults()
        font_config.feature.width = "slim"
        with tempfile.TemporaryDirectory() as tmp:
            font = self._build_punctuation_test_font(Path(tmp) / "fixture.ttf")

        skip_verify = apply_cjk_width_transform(
            font,
            font_config,
            CJKCommonBuildOptions(
                scale_factor=(1.0, 1.0),
                scale_punctuation_factor=(0.9, 0.9),
            ),
        )

        self.assertFalse(skip_verify)
        self._verify_cjk_widths(
            font,
            font_config,
            "MapleMonoCN-Regular",
            skip_verify,
            cjk_narrow=False,
        )
        hmtx = font["hmtx"].metrics
        self.assertEqual(hmtx["latinA"][0], 500)
        self.assertEqual(hmtx["uni4E00"][0], 1000)
        self.assertEqual(hmtx["uni3001"][0], 1000)
        self.assertEqual(hmtx["uniFF0C"][0], 1000)
        self.assertEqual(
            font["glyf"]["uni4E00"].yMax - font["glyf"]["uni4E00"].yMin, 800
        )
        self.assertEqual(
            font["glyf"]["uni3001"].yMax - font["glyf"]["uni3001"].yMin, 180
        )


if __name__ == "__main__":
    unittest.main()
