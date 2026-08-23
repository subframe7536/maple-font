from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from scripts.cjk.config import CJKBuildConfig, CJKSourceConfig
from scripts.cjk.presets import CJKPresetId, build_preset_config, get_preset
from scripts.config.base import CJKCommonBuildOptions, ResolvedCJKBuildEntry
from scripts.config.resolver import BuildConfigResolver
from scripts.config.runtime import BuildRuntimeContext
from scripts.pipeline.cache import output_snapshot

if TYPE_CHECKING:
    from scripts.pipeline.orchestrator import MapleBuildPipeline

TEST_STYLES = (
    "Thin",
    "ThinItalic",
    "ExtraLight",
    "ExtraLightItalic",
    "Light",
    "LightItalic",
    "Regular",
    "Italic",
    "Medium",
    "MediumItalic",
    "SemiBold",
    "SemiBoldItalic",
    "Bold",
    "BoldItalic",
    "ExtraBold",
    "ExtraBoldItalic",
)


def make_font_config():
    return BuildConfigResolver().load_defaults()


def make_runtime_context(tmp_path: Path) -> BuildRuntimeContext:
    return BuildRuntimeContext(
        src_dir="sources",
        output_root=str(tmp_path / "fonts"),
        output_otf=str(tmp_path / "fonts" / "OTF"),
        output_ttf=str(tmp_path / "fonts" / "TTF"),
        output_ttf_hinted=str(tmp_path / "fonts" / "TTF-AutoHint"),
        output_variable=str(tmp_path / "fonts" / "Variable"),
        output_woff2=str(tmp_path / "fonts" / "Woff2"),
        output_nf=str(tmp_path / "fonts" / "NF"),
        ttf_base_dir=str(tmp_path / "fonts" / "TTF-AutoHint"),
        is_nf_built=False,
        is_cjk_built=False,
        effective_github_mirror="github.com",
        font_forge_bin=None,
        resolved_vertical_metric=(1020, -300),
    )


def write_test_font(path: Path) -> None:
    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder([".notdef"])
    builder.setupCharacterMap({})
    builder.setupGlyf({".notdef": TTGlyphPen(None).glyph()})
    builder.setupHorizontalMetrics({".notdef": (600, 0)})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable(
        {
            "familyName": "Maple Mono",
            "styleName": "Regular",
            "uniqueFontIdentifier": "Maple Mono Regular",
            "fullName": "Maple Mono Regular",
            "psName": "MapleMono-Regular",
        }
    )
    builder.setupOS2()
    builder.setupPost()
    builder.setupMaxp()
    path.parent.mkdir(parents=True, exist_ok=True)
    builder.save(path)


def make_stage_record(
    pipeline: MapleBuildPipeline,
    stage: str,
    paths: list[Path],
) -> dict[str, object]:
    return {
        "key": pipeline._stage_cache_identity(stage),
        "snapshot": output_snapshot(
            Path(pipeline.runtime_context.output_root),
            stage,
            paths,
        ),
    }


def make_builtin_entry(locale: CJKPresetId = "cn") -> ResolvedCJKBuildEntry:
    preset_config = build_preset_config(locale)
    return ResolvedCJKBuildEntry(
        entry_id=locale,
        locale_name=preset_config.locale_name,
        build_config=preset_config,
        common_options=CJKCommonBuildOptions(),
        is_builtin=True,
        preset_id=locale,
        preset_spec=get_preset(locale),
    )


def make_custom_entry(locale_name: str = "HK") -> ResolvedCJKBuildEntry:
    return ResolvedCJKBuildEntry(
        entry_id=f"custom:{locale_name.lower()}",
        locale_name=locale_name,
        build_config=CJKBuildConfig(
            source=CJKSourceConfig(
                path=Path("source.ttf"),
                masters={
                    100: {"wght": 100},
                    400: {"wght": 400},
                    800: {"wght": 800},
                },
            ),
            locale_name=locale_name,
        ),
        common_options=CJKCommonBuildOptions(),
        is_builtin=False,
    )


def write_cjk_profile_outputs(
    pipeline: MapleBuildPipeline,
    output_locales: set[str],
) -> None:
    for output_locale in output_locales:
        for path in pipeline._cjk_stage_expected_paths(output_locale):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"font")
