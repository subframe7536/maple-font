from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, cast

from fontTools.ttLib.tables._m_e_t_a import table__m_e_t_a

from scripts.feature.apply import apply_binary_features
from scripts.feature.catalog import CJK_FEATURES
from scripts.font_ops.glyph_transform import (
    change_glyph_width_or_scale,
    smart_change_width,
)
from scripts.font_ops.metrics import adjust_line_height, verify_glyph_width
from scripts.font_ops.names import (
    parse_style_name,
    update_font_names,
)
from scripts.font_ops.opentype import remove_target_glyph
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from scripts.config.base import (
        CJKCommonBuildOptions,
        ResolvedCJKBuildEntry,
        ResolvedConfig,
    )
    from scripts.config.runtime import BuildRuntimeContext
    from scripts.font_ops.fonttools import MetaTable, TTFont


def build_cjk_family_name(font_config: ResolvedConfig, locale_suffix: str) -> str:
    return f"{font_config.family_name} {_cjk_locale_name(font_config, locale_suffix)}"


def build_cjk_postscript_prefix(font_config: ResolvedConfig, locale_suffix: str) -> str:
    return f"{font_config.family_name_compact}-{_cjk_locale_name(font_config, locale_suffix)}"


def _cjk_locale_name(font_config: ResolvedConfig, locale_suffix: str) -> str:
    """Avoid repeating the NF profile marker in generated CJK names."""
    nf_prefix = f"{font_config.get_nf_variant().directory_name}-"
    if locale_suffix.startswith(nf_prefix) and font_config.family_name_compact.endswith(
        f"-{font_config.get_nf_variant().symbol}"
    ):
        return locale_suffix.removeprefix(nf_prefix)
    return locale_suffix


def apply_cjk_meta_table(
    font: TTFont, language_tag: str, code_page_range1: int
) -> None:
    font.table("OS/2").ulCodePageRange1 = code_page_range1
    meta = table__m_e_t_a("meta")
    cast("MetaTable", meta).data = {
        "dlng": language_tag,
        "slng": language_tag,
    }
    font["meta"] = meta


def apply_cjk_names(
    font: TTFont,
    font_config: ResolvedConfig,
    locale_suffix: str,
    style_compact: str,
    narrow: bool,
) -> str:
    style_with_prefix_space, style_in_2, style_in_17, is_skip_subfamily, _ = (
        parse_style_name(style_name_compact=style_compact)
    )
    family_name = build_cjk_family_name(font_config, locale_suffix)
    postscript_prefix = build_cjk_postscript_prefix(font_config, locale_suffix)
    postscript_name = f"{postscript_prefix}-{style_compact}"
    update_font_names(
        font=font,
        font_config=font_config,
        family_name=f"{family_name}{style_with_prefix_space}",
        style_name=style_in_2,
        full_name=f"{family_name} {style_in_17}",
        postscript_name=postscript_name,
        is_skip_subfamily=is_skip_subfamily,
        preferred_family_name=family_name,
        preferred_style_name=style_in_17,
        narrow=narrow,
    )
    return postscript_name


def apply_cjk_metrics(
    font: TTFont,
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
) -> None:
    font.table("OS/2").xAvgCharWidth = font_config.get_target_width()
    adjust_line_height(
        font, font_config.line_height, runtime_context.resolved_vertical_metric
    )


def apply_cjk_width_transform(
    font: TTFont,
    font_config: ResolvedConfig,
    common_options: CJKCommonBuildOptions,
) -> bool:
    target_width = font_config.glyph_width_cn_narrow if common_options.narrow else None
    scale_factor: tuple[float, float] | None = (
        common_options.scale_factor
        if common_options.scale_factor != (1.0, 1.0)
        else None
    )
    special_scale_names = [
        "ellipsis.full",
        "quoteleft.full",
        "quoteright.full",
        "quotedblleft.full",
        "quotedblright.full",
    ]

    skip_verify = font_config.get_nf_variant().suffix == "Propo"
    if target_width or scale_factor:
        match_width = 2 * font_config.glyph_width
        is_slim = font_config.get_width_name() != "SL"
        if target_width and is_slim:
            font.table("hhea").advanceWidthMax = target_width
            logger.warning(
                "Changed CJK glyph width; mark font as proportional and skip width checks"
            )
        elif target_width is None:
            target_width = match_width

        if scale_factor:
            logger.debug(
                "Scale CJK glyphs: width_factor=%s, height_factor=%s",
                scale_factor[0],
                scale_factor[1],
            )
        else:
            scale_factor = (1.0, 1.0)

        change_glyph_width_or_scale(
            font=font,
            match_width=match_width,
            target_width=target_width,
            scale_factor=scale_factor,
            special_names=special_scale_names,
        )
        skip_verify = skip_verify or bool(target_width and is_slim)
    elif font_config.get_width_name():
        change_glyph_width_or_scale(
            font=font,
            match_width=2 * font_config.glyph_width,
            target_width=2 * font_config.get_target_width(),
            scale_factor=(1.0, 1.0),
            special_names=special_scale_names,
        )

    if font_config.get_width_name():
        previous_advance_width_max = font.table("hhea").advanceWidthMax
        smart_change_width(
            font=font,
            target_width=font_config.get_target_width(),
            original_ref_width=font_config.glyph_width,
            scale_zero_width=False,
        )
        font.table("hhea").advanceWidthMax = previous_advance_width_max

    if skip_verify:
        font.table("post").isFixedPitch = False
        os2 = font.table("OS/2")
        os2.panose.bProportion = 0
        os2.panose.bSpacing = 0

    return skip_verify


def verify_cjk_widths(
    font: TTFont,
    font_config: ResolvedConfig,
    file_name: str,
    skip_verify: bool,
    cjk_narrow: bool,
) -> None:
    if skip_verify:
        return
    verify_glyph_width(
        font=font,
        expect_widths=font_config.get_valid_glyph_width_list(True, cjk_narrow),
        file_name=file_name,
    )


def postprocess_cjk_extended_static_font(
    font: TTFont,
    entry: ResolvedCJKBuildEntry,
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    style_compact: str,
    locale_suffix: str | None = None,
) -> str:
    logger.debug(
        "Postprocess CJK static font: locale=%s, style=%s",
        entry.display_name,
        style_compact,
    )
    if entry.build_config.freeze_feature is not None:
        font_config = deepcopy(font_config)
        font_config.feature_freeze[entry.build_config.freeze_feature] = "enable"
    remove_target_glyph(font, ".1")
    postscript_name = apply_cjk_names(
        font,
        font_config,
        locale_suffix or entry.locale_name,
        style_compact,
        entry.common_options.narrow,
    )
    skip_verify = apply_cjk_width_transform(font, font_config, entry.common_options)
    if entry.is_builtin and entry.common_options.fix_meta_table and entry.preset_spec:
        apply_cjk_meta_table(
            font,
            entry.preset_spec.meta_languages,
            entry.preset_spec.code_page_range1,
        )
    apply_cjk_metrics(font, font_config, runtime_context)
    apply_binary_features(
        config=font_config,
        font=font,
        issue_fea_dir=runtime_context.output_dir,
        is_italic="Italic" in style_compact,
        is_cn=True,
        is_hinted=False,
        fea_path=runtime_context.feature_file_path("Italic" in style_compact, True),
        outline_tags=frozenset(feature.tag for feature in CJK_FEATURES),
    )
    verify_cjk_widths(
        font,
        font_config,
        postscript_name,
        skip_verify,
        entry.common_options.narrow,
    )
    return postscript_name


def get_static_style_name(font_path: Path, static_file_prefix: str) -> str | None:
    prefix = f"{static_file_prefix}-"
    if not font_path.name.startswith(prefix) or font_path.suffix.lower() != ".ttf":
        return None
    return font_path.stem.removeprefix(prefix)


def get_core_static_font_styles(
    base_dir: str | Path,
    family_name_compact: str,
    target_styles: list[str] | None,
) -> list[tuple[str, Path]]:
    prefix = f"{family_name_compact}-"
    styles: list[tuple[str, Path]] = []
    for font_path in sorted(Path(base_dir).glob(f"{prefix}*.ttf")):
        style_compact = font_path.stem.removeprefix(prefix)
        if target_styles and style_compact not in target_styles:
            continue
        styles.append((style_compact, font_path))
    return styles
