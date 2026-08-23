from __future__ import annotations

import unittest
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
