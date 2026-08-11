from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.cjk.config import CJKBuildConfig, CJKSourceConfig
from scripts.cjk.presets import build_preset_config, get_preset
from scripts.cjk.static import (
    apply_cjk_width_transform,
    postprocess_cjk_extended_static_font,
)
from scripts.config.base import (
    CJKCommonBuildOptions,
    ResolvedCJKBuildEntry,
)
from scripts.config.resolver import BuildConfigResolver, BuildRuntimeContext
from scripts.feature.catalog import CJK_FEATURES
from scripts.font_ops.fonttools import TTFont


def make_runtime_context() -> BuildRuntimeContext:
    return BuildRuntimeContext(
        src_dir="source",
        output_root="fonts",
        output_otf="fonts/OTF",
        output_ttf="fonts/TTF",
        output_ttf_hinted="fonts/TTF-AutoHint",
        output_variable="fonts/Variable",
        output_woff2="fonts/Woff2",
        output_nf="fonts/NF",
        ttf_base_dir="fonts/TTF-AutoHint",
        has_cache=False,
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
    def test_slim_width_transforms_full_and_residual_half_widths(self) -> None:
        font_config = BuildConfigResolver().load_defaults()
        font_config.feature.width = "slim"
        font = MagicMock()

        with (
            patch("scripts.cjk.static.change_glyph_width_or_scale") as full_width,
            patch("scripts.cjk.static.smart_change_width") as half_width,
        ):
            skip_verify = apply_cjk_width_transform(
                font,
                font_config,
                CJKCommonBuildOptions(),
            )

        self.assertFalse(skip_verify)
        full_width.assert_called_once_with(
            font=font,
            match_width=1200,
            target_width=1000,
            scale_factor=(1.0, 1.0),
            special_names=[
                "ellipsis.full",
                "quoteleft.full",
                "quoteright.full",
                "quotedblleft.full",
                "quotedblright.full",
            ],
        )
        half_width.assert_called_once_with(
            font=font,
            target_width=500,
            original_ref_width=600,
            scale_zero_width=False,
        )

    def test_builtin_entry_applies_meta_table(self) -> None:
        font_config = BuildConfigResolver().load_defaults()
        runtime_context = make_runtime_context()
        with (
            patch("scripts.cjk.static.remove_target_glyph"),
            patch(
                "scripts.cjk.static.apply_cjk_names",
                return_value="MapleMono-CN-Regular",
            ),
            patch(
                "scripts.cjk.static.apply_cjk_width_transform",
                return_value=False,
            ),
            patch("scripts.cjk.static.apply_cjk_meta_table") as apply_meta_mock,
            patch("scripts.cjk.static.apply_cjk_metrics"),
            patch("scripts.cjk.static.verify_cjk_widths"),
            patch("scripts.cjk.static.apply_binary_features") as apply_binary_features,
        ):
            postprocess_cjk_extended_static_font(
                TTFont(),
                make_builtin_entry(),
                font_config,
                runtime_context,
                "Regular",
            )

        apply_meta_mock.assert_called_once()
        self.assertEqual(
            apply_binary_features.call_args.kwargs["outline_tags"],
            frozenset(feature.tag for feature in CJK_FEATURES),
        )

    def test_custom_entry_skips_meta_table_even_when_enabled(self) -> None:
        font_config = BuildConfigResolver().load_defaults()
        runtime_context = make_runtime_context()
        with (
            patch("scripts.cjk.static.remove_target_glyph"),
            patch(
                "scripts.cjk.static.apply_cjk_names",
                return_value="MapleMono-HK-Regular",
            ),
            patch(
                "scripts.cjk.static.apply_cjk_width_transform",
                return_value=False,
            ),
            patch("scripts.cjk.static.apply_cjk_meta_table") as apply_meta_mock,
            patch("scripts.cjk.static.apply_cjk_metrics"),
            patch("scripts.cjk.static.verify_cjk_widths"),
            patch("scripts.cjk.static.apply_binary_features"),
        ):
            postprocess_cjk_extended_static_font(
                TTFont(),
                make_custom_entry(),
                font_config,
                runtime_context,
                "Regular",
            )

        apply_meta_mock.assert_not_called()

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


if __name__ == "__main__":
    unittest.main()
