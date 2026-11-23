from __future__ import annotations

import math
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from scripts.cjk.config import CJKBuildConfig, CJKSourceConfig
from scripts.cjk.postprocess import finalize_static_font_instance
from scripts.cjk.static import (
    apply_cjk_meta_table,
    postprocess_cjk_extended_static_font,
)
from scripts.cjk.variable import update_italic_metadata
from scripts.font_ops.fonttools import MetaTable, TTFont, load_font
from scripts.font_ops.metadata import (
    OBLIQUE_BIT,
    fix_italic_metadata,
    set_meta_table,
    sync_ribbi_style_metadata,
)
from scripts.font_ops.names import is_ribbi_bold
from scripts.pipeline.nerd_fonts import build_nf
from scripts.task import googlefonts
from scripts.task.googlefonts import (
    DESIGN_LANGUAGES,
    SUPPORTED_LANGUAGES,
    apply_googlefonts_meta,
)
from scripts.tests.cjk_font_fixtures import build_test_font
from scripts.tests.pipeline_fixtures import (
    make_custom_entry,
    make_font_config,
    make_runtime_context,
)

USE_TYPO_METRICS_BIT = 7


def _build_ribbi_test_font(
    path: Path,
    *,
    italic_angle_deg: float = 0.0,
    fs_selection: int = 0xC0,
    mac_style: int = 0x00,
    weight_class: int = 400,
) -> TTFont:
    pen = TTGlyphPen(None)
    skew = math.tan(math.radians(italic_angle_deg))
    for x0, y0, x1, y1 in (
        (100, 0, 180, 700),
        (420, 0, 500, 700),
        (180, 320, 420, 390),
    ):
        pen.moveTo((round(x0 + y0 * skew), y0))
        pen.lineTo((round(x1 + y0 * skew), y0))
        pen.lineTo((round(x1 + y1 * skew), y1))
        pen.lineTo((round(x0 + y1 * skew), y1))
        pen.closePath()
    glyph_h = pen.glyph()

    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder([".notdef", "H"])
    builder.setupCharacterMap({0x0048: "H"})
    builder.setupGlyf({".notdef": TTGlyphPen(None).glyph(), "H": glyph_h})
    builder.setupHorizontalMetrics({".notdef": (600, 0), "H": (600, 100)})
    builder.setupHorizontalHeader(ascent=1020, descent=-300)
    builder.setupNameTable(
        {
            "familyName": "Maple Mono",
            "styleName": "Regular",
            "uniqueFontIdentifier": "Maple Mono Regular",
            "fullName": "Maple Mono Regular",
            "psName": "MapleMono-Regular",
        }
    )
    builder.setupOS2(
        version=4,
        usWeightClass=weight_class,
        fsSelection=fs_selection,
        sTypoAscender=1020,
        sTypoDescender=-300,
        usWinAscent=1020,
        usWinDescent=300,
    )
    builder.setupPost()
    builder.setupMaxp()
    builder.setupHead(macStyle=mac_style, created=2082844800, modified=2082844800)
    path.parent.mkdir(parents=True, exist_ok=True)
    builder.font.recalcTimestamp = False
    builder.save(path)
    return load_font(path)


class FontMetadataTest(unittest.TestCase):
    def test_set_meta_table_replaces_script_language_tags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            font = build_test_font(Path(tmp) / "Fixture.ttf")
            try:
                set_meta_table(font, "Old", "Old")
                set_meta_table(font, "Latn", "Latn, Cyrl, Grek")

                meta = cast("MetaTable", font["meta"])
                self.assertEqual(
                    meta.data,
                    {"dlng": "Latn", "slng": "Latn, Cyrl, Grek"},
                )
            finally:
                font.close()

    def test_cjk_meta_table_keeps_code_page_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            font = build_test_font(Path(tmp) / "Fixture.ttf")
            try:
                apply_cjk_meta_table(font, "Latn, Hans", 1 << 18)

                self.assertEqual(font.table("OS/2").ulCodePageRange1, 1 << 18)
                self.assertEqual(
                    cast("MetaTable", font["meta"]).data,
                    {"dlng": "Latn, Hans", "slng": "Latn, Hans"},
                )
            finally:
                font.close()

    def test_is_ribbi_bold_only_matches_bold_and_bold_italic(self) -> None:
        for style, expected in (
            ("Regular", False),
            ("Bold", True),
            ("Italic", False),
            ("BoldItalic", True),
            ("Bold Italic", True),
            ("Thin", False),
            ("ExtraLight", False),
            ("Light", False),
            ("Medium", False),
            ("SemiBold", False),
            ("SemiBoldItalic", False),
            ("ExtraBold", False),
            ("ExtraBoldItalic", False),
        ):
            with self.subTest(style=style):
                self.assertEqual(is_ribbi_bold(style), expected)

    def test_sync_ribbi_style_metadata_matrix_and_stale_correction(self) -> None:
        matrix = (
            ("Regular", False, False, 400, 0xC0, 0xC0, 0x00),
            ("Bold", True, False, 700, 0xC0, 0xA0, 0x01),
            ("Italic", False, True, 400, 0xC0, 0x81, 0x02),
            ("BoldItalic", True, True, 700, 0x81, 0xA1, 0x03),
            ("SemiBold", False, False, 600, 0xC0, 0xC0, 0x00),
            ("SemiBoldItalic", False, True, 600, 0xC0, 0x81, 0x02),
            ("ExtraBold", False, False, 800, 0xC0, 0xC0, 0x00),
            ("ExtraBoldItalic", False, True, 800, 0xC0, 0x81, 0x02),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for (
                style,
                is_bold,
                is_italic,
                weight_class,
                initial_fs,
                expected_fs,
                expected_mac,
            ) in matrix:
                with self.subTest(style=style):
                    font = _build_ribbi_test_font(
                        root / f"{style}.ttf",
                        italic_angle_deg=10.0 if is_italic else 0.0,
                        fs_selection=initial_fs | (1 << OBLIQUE_BIT),
                        mac_style=0x00,
                        weight_class=weight_class,
                    )
                    try:
                        sync_ribbi_style_metadata(
                            font, is_bold=is_bold, is_italic=is_italic
                        )
                        self.assertEqual(font.table("OS/2").fsSelection, expected_fs)
                        self.assertEqual(font.table("head").macStyle, expected_mac)
                        self.assertTrue(
                            font.table("OS/2").fsSelection & (1 << USE_TYPO_METRICS_BIT)
                        )
                    finally:
                        font.close()

    def test_fix_italic_metadata_sets_ribbi_bold_bits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for style, slant, is_bold, weight, exp_fs, exp_mac in (
                ("Regular", 0.0, False, 400, 0xC0, 0x00),
                ("Bold", 0.0, True, 700, 0xA0, 0x01),
                ("Italic", 10.0, False, 400, 0x81, 0x02),
                ("BoldItalic", 10.0, True, 700, 0xA1, 0x03),
            ):
                with self.subTest(style=style):
                    font = _build_ribbi_test_font(
                        root / f"Fix-{style}.ttf",
                        italic_angle_deg=slant,
                        fs_selection=0xC0,
                        mac_style=0x00,
                        weight_class=weight,
                    )
                    try:
                        fix_italic_metadata(font, is_bold=is_bold)
                        self.assertEqual(font.table("OS/2").fsSelection, exp_fs)
                        self.assertEqual(font.table("head").macStyle, exp_mac)
                    finally:
                        font.close()

    def test_update_italic_metadata_supports_bold_and_preserves_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bold_font = _build_ribbi_test_font(
                root / "Bold.ttf", fs_selection=0xA0, mac_style=0x01
            )
            stale_font = _build_ribbi_test_font(
                root / "Stale.ttf", fs_selection=0xC0, mac_style=0x00
            )
            try:
                update_italic_metadata(bold_font, 10.0)
                self.assertEqual(bold_font.table("OS/2").fsSelection, 0xA1)
                self.assertEqual(bold_font.table("head").macStyle, 0x03)

                update_italic_metadata(stale_font, 10.0, is_bold=True)
                self.assertEqual(stale_font.table("OS/2").fsSelection, 0xA1)
                self.assertEqual(stale_font.table("head").macStyle, 0x03)
            finally:
                bold_font.close()
                stale_font.close()

    def test_cjk_static_and_base_postprocess_fix_ribbi_bits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            font_config = make_font_config()
            font_config.behavior.apply_fea_file = True
            runtime_context = make_runtime_context(root)
            features_dir = root / "sources" / "features"
            features_dir.mkdir(parents=True)
            (features_dir / "regular_cn.fea").write_text("", encoding="utf-8")
            (features_dir / "italic_cn.fea").write_text("", encoding="utf-8")
            runtime_context.src_dir = str(root / "sources")
            entry = make_custom_entry("CN")
            cjk_config = CJKBuildConfig(
                source=CJKSourceConfig(
                    path=root / "source.ttf",
                    masters={
                        100: {"wght": 100},
                        400: {"wght": 400},
                        800: {"wght": 800},
                    },
                ),
                locale_name="CN",
            )

            cases = (
                ("Regular", False, 0xC0, 0x00, 400),
                ("Bold", False, 0xA0, 0x01, 700),
                ("Italic", True, 0x81, 0x02, 400),
                ("Bold", True, 0xA1, 0x03, 700),
                ("SemiBold", False, 0xC0, 0x00, 600),
                ("SemiBold", True, 0x81, 0x02, 600),
            )
            for name, is_italic, expected_fs, expected_mac, weight in cases:
                style_compact = (f"{name}Italic" if is_italic else name).replace(
                    "RegularItalic", "Italic"
                )
                with self.subTest(style=style_compact):
                    initial_fs = 0x81 if is_italic else 0xC0
                    initial_mac = 0x02 if is_italic else 0x00

                    ext_font = _build_ribbi_test_font(
                        root / f"ext-{style_compact}.ttf",
                        italic_angle_deg=10.0 if is_italic else 0.0,
                        fs_selection=initial_fs,
                        mac_style=initial_mac,
                        weight_class=weight,
                    )
                    try:
                        postprocess_cjk_extended_static_font(
                            ext_font,
                            entry,
                            font_config,
                            runtime_context,
                            style_compact,
                        )
                        self.assertEqual(
                            ext_font.table("OS/2").fsSelection, expected_fs
                        )
                        self.assertEqual(ext_font.table("head").macStyle, expected_mac)
                    finally:
                        ext_font.close()

                    base_font = _build_ribbi_test_font(
                        root / f"base-{style_compact}.ttf",
                        italic_angle_deg=10.0 if is_italic else 0.0,
                        fs_selection=initial_fs,
                        mac_style=initial_mac,
                        weight_class=weight,
                    )
                    out_path = root / f"out-{style_compact}.ttf"
                    try:
                        finalize_static_font_instance(
                            base_font,
                            str(out_path),
                            name,
                            is_italic,
                            cjk_config,
                            font_config,
                        )
                    finally:
                        base_font.close()
                    saved = load_font(out_path)
                    try:
                        self.assertEqual(saved.table("OS/2").fsSelection, expected_fs)
                        self.assertEqual(saved.table("head").macStyle, expected_mac)
                    finally:
                        saved.close()

    def test_build_nf_syncs_ribbi_bits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            font_config = make_font_config()
            runtime_context = make_runtime_context(root)
            for style, expected_fs, expected_mac, weight in (
                ("Regular", 0xC0, 0x00, 400),
                ("Bold", 0xA0, 0x01, 700),
                ("Italic", 0x81, 0x02, 400),
                ("BoldItalic", 0xA1, 0x03, 700),
            ):
                with self.subTest(style=style):
                    src = root / f"MapleMono-{style}.ttf"
                    out = root / "nf" / f"MapleMono-NF-{style}.ttf"
                    stale_font = _build_ribbi_test_font(
                        src,
                        italic_angle_deg=10.0 if "Italic" in style else 0.0,
                        fs_selection=0x81 if "Italic" in style else 0xC0,
                        mac_style=0x02 if "Italic" in style else 0x00,
                        weight_class=weight,
                    )
                    build_nf(
                        src,
                        out,
                        lambda _p, _c, _r, font=stale_font: font,
                        use_font_patcher=False,
                        font_config=font_config,
                        runtime_context=runtime_context,
                    )
                    reopened = load_font(out)
                    try:
                        self.assertEqual(
                            reopened.table("OS/2").fsSelection, expected_fs
                        )
                        self.assertEqual(reopened.table("head").macStyle, expected_mac)
                    finally:
                        reopened.close()

    def test_googlefonts_meta_updates_googlefonts_outputs_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ttf_path = root / "MapleMono-Regular.ttf"
            static_path = root / "MapleMono-Bold.ttf"
            woff2_path = root / "MapleMono[wght].woff2"
            debug_path = root / "MapleMonoDebug-Regular.ttf"
            self._write_font(ttf_path, "Maple Mono", meta=("Old", "Old"))
            self._write_font(static_path, "Maple Mono Bold")
            self._write_font(woff2_path, "Maple Mono", flavor="woff2")
            self._write_font(debug_path, "Maple Mono Debug")
            debug_bytes = debug_path.read_bytes()

            updated = apply_googlefonts_meta((root,))

            self.assertCountEqual(updated, (ttf_path, static_path, woff2_path))
            self._assert_meta_table(ttf_path)
            self._assert_meta_table(static_path)
            self._assert_meta_table(woff2_path)
            self.assertEqual(debug_path.read_bytes(), debug_bytes)

    def test_googlefonts_run_applies_meta_after_successful_build(self) -> None:
        with (
            patch.object(googlefonts, "run_gftools_builder") as build,
            patch.object(googlefonts, "apply_googlefonts_meta") as apply_meta,
        ):
            googlefonts.run(Namespace(rebuild=False, qa=False))

        build.assert_called_once_with()
        apply_meta.assert_called_once_with()

    def _write_font(
        self,
        path: Path,
        family_name: str,
        *,
        flavor: str | None = None,
        meta: tuple[str, str] | None = None,
    ) -> None:
        source_path = path.with_suffix(".source.ttf")
        font = build_test_font(source_path)
        name_table = cast("Any", font["name"])
        for record in list(name_table.names):
            if record.nameID == 1:
                name_table.setName(
                    family_name,
                    record.nameID,
                    record.platformID,
                    record.platEncID,
                    record.langID,
                )
        if meta is not None:
            set_meta_table(font, *meta)
        if flavor is not None:
            font.flavor = flavor
        try:
            font.save(path)
        finally:
            font.close()

    def _assert_meta_table(self, path: Path) -> None:
        font = load_font(path)
        try:
            self.assertEqual(
                cast("MetaTable", font["meta"]).data,
                {
                    "dlng": DESIGN_LANGUAGES,
                    "slng": SUPPORTED_LANGUAGES,
                },
            )
        finally:
            font.close()


if __name__ == "__main__":
    unittest.main()
