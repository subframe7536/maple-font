from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from fontTools.misc.transform import Transform
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen

from scripts.cjk.masters import ordered_master_locations
from scripts.cjk.outlines import (
    as_fonttools_glyph_mapping,
    cff_master_glyph_order,
    convert_cff_master_files_to_glyf_tables_parallel,
    install_existing_glyf_tables,
)
from scripts.cjk.postprocess import recalculate_font
from scripts.cjk.variable import (
    drop_font_tables,
    get_cmap_codepoints,
    get_unicode_cmap,
)
from scripts.font_ops.fonttools import TTFont, load_font
from scripts.font_ops.subset import SubsetConfig, subset_to_codepoints
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from concurrent.futures import Executor

    from scripts.cjk.config import CJKBuildConfig, CJKTransformConfig


@dataclass(frozen=True)
class SourceBuildState:
    outline_format: Literal["glyf", "cff2"]
    subset_path: Path
    source_codepoints: set[int]
    keep_codepoints: set[int]
    master_paths: tuple[Path, Path, Path]


def get_allowed_codepoints(source_font: TTFont, config: CJKBuildConfig) -> set[int]:
    """Select source codepoints allowed by configured ranges and encoding."""
    allowed = {
        codepoint
        for codepoint in get_cmap_codepoints(source_font)
        if any(start <= codepoint <= end for start, end in config.unicode.ranges)
    }
    if not config.unicode.filter_encoding:
        return allowed

    filtered: set[int] = set()
    for codepoint in allowed:
        try:
            chr(codepoint).encode(config.unicode.filter_encoding)
        except UnicodeEncodeError:
            continue
        filtered.add(codepoint)
    return filtered


def prepare_source_subset(
    source_path: Path,
    keep_codepoints: set[int],
    excluded_codepoints: set[int],
    config: CJKBuildConfig,
    out_path: Path,
) -> int:
    """Subset the CJK source to configured codepoints not already in the feature font."""
    font = load_font(source_path, decompile=True)
    try:
        drop_font_tables(font, config.source.drop_tables)
        filtered_codepoints = (
            keep_codepoints - excluded_codepoints
            if config.unicode.exclude_feature_codepoints
            else keep_codepoints
        )
        removed = len(keep_codepoints) - len(filtered_codepoints)
        if "gvar" in font:
            variations = font["gvar"].variations
            for glyph_name in font.getGlyphOrder():
                if glyph_name not in variations:
                    variations[glyph_name] = []
        subset_to_codepoints(
            font,
            filtered_codepoints,
            options=SubsetConfig(
                layout_features=(),
                name_ids=("*",),
                name_legacy=True,
                name_languages=("*",),
                notdef_outline=True,
                recalc_bounds=True,
                recalc_timestamp=False,
                recommended_glyphs=False,
            ),
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        font.save(out_path)
        return removed
    finally:
        font.close()


def apply_horizontal_metrics(font: TTFont, config: CJKBuildConfig) -> None:
    """Apply Maple Mono horizontal metrics to font."""
    for attr, value in config.hhea_metrics.items():
        setattr(font["hhea"], attr, value)
    for attr, value in config.os2_metrics.items():
        if hasattr(font["OS/2"], attr):
            setattr(font["OS/2"], attr, value)
    for attr, value in config.post_metrics.items():
        setattr(font["post"], attr, value)


def transform_glyph(
    font: TTFont,
    glyph_name: str,
    transform: CJKTransformConfig,
) -> None:
    """Apply configured scale and translation to one glyf glyph."""
    if "glyf" not in font:
        return
    glyf = font["glyf"]
    glyph = glyf[glyph_name]
    if glyph.isComposite():
        for component in glyph.components:
            if hasattr(component, "x"):
                component.x += transform.x_shift
            elif hasattr(component, "arg1") and not component.flags & 0x0002:
                component.arg1 += transform.x_shift
    elif getattr(glyph, "numberOfContours", 0) > 0:
        coordinates = glyph.coordinates
        if coordinates is None:
            coordinates, _, _ = glyph.getCoordinates(glyf)
            glyph.coordinates = coordinates
        coordinates.scale((transform.x_scale, transform.y_scale))
        coordinates.translate((transform.x_shift, transform.y_shift))
    glyph.recalcBounds(glyf)


def normalize_widths(
    font: TTFont,
    config: CJKBuildConfig,
    glyph_names: set[str] | None = None,
    protected_glyphs: set[str] | None = None,
) -> None:
    """Normalize CJK glyph advance widths without changing outlines."""
    target_glyphs, zero_width_glyphs = width_target_glyphs(
        font, glyph_names, protected_glyphs
    )
    for glyph_name in target_glyphs:
        if glyph_name not in font["hmtx"].metrics:
            continue
        _, lsb = font["hmtx"].metrics[glyph_name]
        width = (
            0
            if glyph_name in zero_width_glyphs
            else config.transform.target_advance_width
        )
        font["hmtx"].metrics[glyph_name] = (width, lsb)
    if "hhea" in font:
        font["hhea"].advanceWidthMax = config.transform.target_advance_width
    if "HVAR" in font:
        del font["HVAR"]


def width_target_glyphs(
    font: TTFont,
    glyph_names: set[str] | None = None,
    protected_glyphs: set[str] | None = None,
) -> tuple[set[str], set[str]]:
    """Resolve glyphs affected by width normalization."""
    cmap = get_unicode_cmap(font)
    zero_width_glyphs = {glyph for cp, glyph in cmap.items() if 0x0300 <= cp <= 0x036F}
    zero_width_glyphs.add(".notdef")
    target_glyphs = (
        glyph_names if glyph_names is not None else set(font.getGlyphOrder())
    )
    if protected_glyphs:
        target_glyphs = target_glyphs - protected_glyphs
    return target_glyphs, zero_width_glyphs


def apply_source_master_transform(font: TTFont, config: CJKBuildConfig) -> None:
    """Apply configured outline transform to a freshly instantiated source master."""
    target_glyphs, zero_width_glyphs = width_target_glyphs(font)
    transform_glyphs = {
        glyph_name
        for glyph_name in target_glyphs
        if glyph_name in font["hmtx"].metrics and glyph_name not in zero_width_glyphs
    }

    if "CFF " in font or "CFF2" in font:
        transform_cff_source_glyphs(font, config.transform, transform_glyphs)
    else:
        for glyph_name in transform_glyphs:
            transform_glyph(font, glyph_name, config.transform)

    if config.transform.x_shift:
        for glyph_name in transform_glyphs:
            advance_width, lsb = font["hmtx"].metrics[glyph_name]
            font["hmtx"].metrics[glyph_name] = (
                advance_width,
                lsb + config.transform.x_shift,
            )


def transform_cff_source_glyphs(
    font: TTFont,
    transform: CJKTransformConfig,
    glyph_names: set[str],
) -> None:
    """Apply configured source-master transform to CFF/CFF2 outlines."""
    transform_cff_glyphs(
        font,
        Transform(
            transform.x_scale,
            0,
            0,
            transform.y_scale,
            transform.x_shift,
            transform.y_shift,
        ),
        glyph_names,
    )


def transform_cff_glyphs(
    font: TTFont,
    glyph_transform: Transform,
    glyph_names: set[str] | None = None,
) -> None:
    """Draw CFF/CFF2 glyphs through an affine transform."""
    table_tag = "CFF2" if "CFF2" in font else "CFF " if "CFF " in font else None
    if table_tag is None:
        return

    is_cff2 = table_tag == "CFF2"
    top_dict = font.table(table_tag).cff.topDictIndex[0]
    char_strings = top_dict.CharStrings
    glyph_set = font.getGlyphSet()
    target_glyphs = (
        glyph_names if glyph_names is not None else set(font.getGlyphOrder())
    )

    for glyph_name in target_glyphs:
        if glyph_name not in char_strings or glyph_name not in glyph_set:
            continue
        pen = T2CharStringPen(None, as_fonttools_glyph_mapping(glyph_set), CFF2=is_cff2)
        glyph_set[glyph_name].draw(TransformPen(pen, glyph_transform))
        old_char_string = char_strings[glyph_name]
        char_strings[glyph_name] = pen.getCharString(
            private=old_char_string.private,
            globalSubrs=old_char_string.globalSubrs,
        )


def convert_cff_master_files_to_glyf(
    input_paths: tuple[str, str, str],
    output_paths: tuple[str, str, str],
    executor: Executor,
    transform_config: CJKBuildConfig | None = None,
) -> None:
    """Convert three compatible CFF source masters to TTF together."""
    glyph_order = cff_master_glyph_order(input_paths)
    glyf_tables = convert_cff_master_files_to_glyf_tables_parallel(
        input_paths,
        glyph_order,
        executor,
    )
    fonts = [load_font(path, decompile=True) for path in input_paths]
    try:
        install_existing_glyf_tables(fonts, glyf_tables)
        for font, output_path in zip(fonts, output_paths, strict=False):
            if transform_config is not None:
                apply_source_master_transform(font, transform_config)
                normalize_widths(font, transform_config)
                recalculate_font(font, transform_config)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            font.save(output_path)
    finally:
        for font in fonts:
            font.close()


def prepare_source_masters(
    subset_path: Path,
    config: CJKBuildConfig,
    process_pool: Executor,
    target_upem: int,
    outline_format: Literal["glyf", "cff2"],
) -> tuple[Path, Path, Path]:
    """Instantiate transformed source masters for the variable-base pipeline."""
    from scripts.cjk.instances import instantiate_masters_from_vf

    logger.debug(
        "Prepare CJK source masters: subset=%s, outline=%s",
        subset_path,
        outline_format,
    )
    if outline_format != "cff2":
        paths = instantiate_masters_from_vf(
            subset_path,
            config.temp_dir / "source-masters",
            config.source.masters,
            process_pool,
            ".ttf",
            target_upem=target_upem,
            transform_config=config,
        )
        logger.debug("CJK source masters prepared: output_dir=%s", paths[0].parent)
        return paths

    cff_master_paths = instantiate_masters_from_vf(
        subset_path,
        config.temp_dir / "source-masters-cff",
        config.source.masters,
        process_pool,
        ".otf",
        target_upem=target_upem,
        convert_cff_to_glyf=False,
    )
    ttf_master_paths = tuple(
        config.temp_dir / "source-masters" / f"{weight}-master.ttf"
        for weight, _ in ordered_master_locations(config.source.masters)
    )
    cff_master_path_strings = (
        str(cff_master_paths[0]),
        str(cff_master_paths[1]),
        str(cff_master_paths[2]),
    )
    ttf_master_path_strings = (
        str(ttf_master_paths[0]),
        str(ttf_master_paths[1]),
        str(ttf_master_paths[2]),
    )
    convert_cff_master_files_to_glyf(
        cff_master_path_strings,
        ttf_master_path_strings,
        process_pool,
        config,
    )
    logger.debug(
        "CFF2 source masters converted to glyf: output_dir=%s",
        ttf_master_paths[0].parent,
    )
    return (ttf_master_paths[0], ttf_master_paths[1], ttf_master_paths[2])
