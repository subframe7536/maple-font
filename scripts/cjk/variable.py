#!/usr/bin/env python3
from __future__ import annotations

import math
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib.instancer import otRound

from scripts.font_ops.fonttools import TTFont, load_font
from scripts.font_ops.merge import merge_cmap_entries
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from collections.abc import Iterable
    from concurrent.futures import Executor

FontInput = str | Path | TTFont

WEIGHT_AXIS_TAG = "wght"
MIN_WEIGHT_SUPPORT = (-1.0, -1.0, 0.0)
MAX_WEIGHT_SUPPORT = (0.0, 1.0, 1.0)
CORE_GLYF_TABLES = ("glyf", "hmtx")
VARIABLE_GLYF_TABLES = (*CORE_GLYF_TABLES, "gvar")


def drop_font_tables(font: TTFont, table_tags: Iterable[str]) -> bool:
    """Drop tables if they exist."""
    changed = False
    for table_tag in table_tags:
        if table_tag in font:
            del font[table_tag]
            changed = True
    return changed


def merge_vf(
    base_font: FontInput, extra_font: FontInput
) -> tuple[TTFont, list[str], int]:
    base: TTFont
    if isinstance(base_font, TTFont):
        base, should_close_base = base_font, False
    else:
        base, should_close_base = load_font(base_font, decompile=True), True
    extra: TTFont
    if isinstance(extra_font, TTFont):
        extra, should_close_extra = extra_font, False
    else:
        extra, should_close_extra = load_font(extra_font, decompile=True), True

    try:
        _validate_merge_inputs(base, extra)
        added_glyphs = _merge_glyph_tables(base, extra)
        added_codepoints = len(merge_cmap_entries(base, extra, added_glyphs))
        recalculate_font_metrics(base)
        # Glyph-order dependent variation maps become stale after merge.
        drop_font_tables(base, ("HVAR", "VVAR"))

        return base, added_glyphs, added_codepoints
    except Exception:
        if should_close_base:
            base.close()
        raise
    finally:
        if should_close_extra:
            extra.close()


def weight_axis(font: TTFont):
    if "fvar" not in font:
        return None
    return next((axis for axis in font["fvar"].axes if axis.axisTag == "wght"), None)


def get_unicode_cmap(font: TTFont) -> dict[int, str]:
    """Extract unicode cmap entries from font."""
    result: dict[int, str] = {}
    for table in font["cmap"].tables:
        if table.isUnicode():
            result.update(table.cmap)
    return result


def get_cmap_codepoints(font: TTFont) -> set[int]:
    """Extract all unicode codepoints from font."""
    return set(get_unicode_cmap(font))


def rebuild_weight_masters_with_regular_default(
    font: TTFont,
    min_master: TTFont,
    regular_master: TTFont,
    max_master: TTFont | None = None,
    axis_tag: str = "wght",
) -> None:
    """Replace weight masters with Regular as default and min/max deltas."""
    _require_tables(font, VARIABLE_GLYF_TABLES, "Font")
    _require_tables(min_master, CORE_GLYF_TABLES, "Min master")
    _require_tables(regular_master, CORE_GLYF_TABLES, "Regular master")
    if max_master is not None:
        _require_tables(max_master, CORE_GLYF_TABLES, "Max master")

    glyf = font.table("glyf")
    h_metrics = font.table("hmtx").metrics
    v_metrics = font.table("vmtx").metrics if "vmtx" in font else None
    variations: dict[str, list[TupleVariation]] = {}

    for glyph_name in font.getGlyphOrder():
        min_coords = _glyph_coordinates(min_master, glyph_name)
        reg_coords = _glyph_coordinates(regular_master, glyph_name)
        max_coords = (
            _glyph_coordinates(max_master, glyph_name)
            if max_master
            else _interpolated_coordinates(font, glyph_name, axis_tag, 1.0)
        )

        glyf._setCoordinates(glyph_name, reg_coords, h_metrics, v_metrics)

        variations[glyph_name] = _build_weight_variations(
            reg_coords, min_coords, max_coords, glyph_name, axis_tag
        )

    font["gvar"].variations = variations

    drop_font_tables(font, ("HVAR", "MVAR", "avar"))


def merge_masters_into_vf(
    base: TTFont,
    min_master: TTFont,
    regular_master: TTFont,
    max_master: TTFont,
    axis_tag: str = "wght",
) -> tuple[list[str], int]:
    """Merge static masters into a variable font as new glyphs with gvar deltas.

    For each glyph in *regular_master* not already in *base*:
    - Copy glyf / hmtx from the regular master.
    - Compute gvar deltas: min delta (-1 … 0) and max delta (0 … 1).
    - Update cmap with any new codepoints.

    Returns ``(added_glyph_names, added_codepoints)``.
    """
    _require_tables(base, (*VARIABLE_GLYF_TABLES, "cmap", "maxp"), "Base font")
    _require_tables(min_master, CORE_GLYF_TABLES, "Min master")
    _require_tables(regular_master, (*CORE_GLYF_TABLES, "cmap"), "Regular master")
    _require_tables(max_master, CORE_GLYF_TABLES, "Max master")

    base_glyph_order = base.getGlyphOrder()
    base_glyphs = set(base_glyph_order)
    glyphs_to_add = [
        glyph_name
        for glyph_name in regular_master.getGlyphOrder()
        if glyph_name not in base_glyphs
    ]

    base_glyf = base["glyf"]
    base_hmtx = base["hmtx"]
    base_gvar = base["gvar"]
    reg_glyf = regular_master["glyf"]
    reg_hmtx = regular_master["hmtx"]

    for glyph_name in glyphs_to_add:
        _copy_glyph_outline_and_metrics(
            glyph_name, base_glyf, base_hmtx, reg_glyf, reg_hmtx
        )

        reg_coords = _glyph_coordinates(regular_master, glyph_name)
        min_coords = _glyph_coordinates(min_master, glyph_name)
        max_coords = _glyph_coordinates(max_master, glyph_name)
        base_gvar.variations[glyph_name] = _build_weight_variations(
            reg_coords, min_coords, max_coords, glyph_name, axis_tag
        )

    _append_glyph_order(base, base_glyph_order, glyphs_to_add)

    added_codepoints = len(merge_cmap_entries(base, regular_master, glyphs_to_add))

    return glyphs_to_add, added_codepoints


def update_italic_metadata(font: TTFont, italic_angle_deg: float) -> None:
    """Update font metadata for italic style."""
    if "post" in font:
        font.table("post").italicAngle = -italic_angle_deg
    if "OS/2" in font:
        os2 = font.table("OS/2")
        os2.fsSelection = (os2.fsSelection & ~0x40) | 0x01
    if "head" in font:
        font.table("head").macStyle |= 0x02
    if "hhea" in font:
        hhea = font.table("hhea")
        hhea.caretSlopeRise = 1000
        hhea.caretSlopeRun = otRound(math.tan(math.radians(italic_angle_deg)) * 1000)


def skew_glyphs(font: TTFont, italic_angle_deg: float) -> None:
    """Apply skew transformation to all glyphs."""
    skew_factor = math.tan(math.radians(italic_angle_deg))
    glyf_table = font["glyf"]
    hmtx = font["hmtx"]
    original_metrics = hmtx.metrics
    composite_glyphs: list[str] = []

    for glyph_name in font.getGlyphOrder():
        glyph = glyf_table[glyph_name]
        advance_width, _ = original_metrics.get(glyph_name, (0, 0))
        if getattr(glyph, "numberOfContours", 0) == 0:
            continue
        if glyph.isComposite():
            for component in glyph.components:
                transform = getattr(component, "transform", None)
                if transform is None:
                    component.transform = [[1, 0], [skew_factor, 1]]
                else:
                    xx, xy = transform[0]
                    yx, yy = transform[1]
                    component.transform = [
                        [xx, xy],
                        [yx + skew_factor * xx, yy + skew_factor * xy],
                    ]
            composite_glyphs.append(glyph_name)
            continue
        if not hasattr(glyph, "coordinates") or glyph.coordinates is None:
            coordinates, _, _ = glyph.getCoordinates(glyf_table)
            glyph.coordinates = coordinates
        glyph.coordinates.transform(
            ((1, 0), (skew_factor, 1), (-otRound(skew_factor * advance_width / 2), 0))
        )
        glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax = (
            glyph.coordinates.calcIntBounds()
        )
        hmtx[glyph_name] = (advance_width, glyph.xMin)

    for glyph_name in composite_glyphs:
        glyph = glyf_table[glyph_name]
        glyph.recalcBounds(glyf_table)
        advance_width, _ = original_metrics.get(glyph_name, (0, 0))
        hmtx[glyph_name] = (advance_width, glyph.xMin)


def recalculate_font_metrics(font: TTFont) -> None:
    """Recalculate common horizontal and OS/2 metrics."""
    if "hhea" in font and "hmtx" in font:
        hhea = font.table("hhea")
        hhea.numberOfHMetrics = len(font.table("hmtx").metrics)
        hhea.recalc(font)

    if "OS/2" in font:
        font.table("OS/2").recalcAvgCharWidth(font)
        font.table("OS/2").recalcUnicodeRanges(font)
        font.table("OS/2").recalcCodePageRanges(font)


def make_italic_master_file(
    input_path: str,
    output_path: str,
    italic_angle_deg: float,
    drop_table_tags: tuple[str, ...] = (),
) -> None:
    """Load a prepared static master, skew it, and save an italic copy."""
    font = load_font(input_path, decompile=True)
    try:
        if drop_table_tags:
            drop_font_tables(font, drop_table_tags)
        skew_glyphs(font, italic_angle_deg)
        update_italic_metadata(font, italic_angle_deg)
        recalculate_font_metrics(font)
        font.save(output_path)
    finally:
        font.close()


def generated_italic_master_paths(temp_root: Path) -> tuple[Path, Path, Path]:
    """Return stable paths for generated italic masters."""
    italic_master_dir = temp_root / "italic-masters"
    italic_master_dir.mkdir(parents=True, exist_ok=True)
    return (
        italic_master_dir / "italic-min-master.ttf",
        italic_master_dir / "italic-regular-master.ttf",
        italic_master_dir / "italic-max-master.ttf",
    )


def make_italic_master_files(
    source_paths: tuple[Path, Path, Path],
    output_paths: tuple[Path, Path, Path],
    italic_angle_deg: float,
    process_pool: Executor,
    drop_table_tags: tuple[str, ...] = (),
) -> None:
    """Build italic copies of the configured static masters in parallel."""
    futures = [
        process_pool.submit(
            make_italic_master_file,
            str(source_path),
            str(output_path),
            italic_angle_deg,
            drop_table_tags,
        )
        for source_path, output_path in zip(source_paths, output_paths, strict=False)
    ]
    for future in futures:
        future.result()


def make_italic_variable_font(
    font: TTFont,
    italic_angle_deg: float,
    temp_root: Path,
    process_pool: Executor,
    master_paths: tuple[Path, Path, Path],
    drop_table_tags: tuple[str, ...] = (),
    masters_are_italic: bool = False,
) -> TTFont:
    """Convert a loaded variable font into an italic variable font in place."""
    skew_factor = math.tan(math.radians(italic_angle_deg))
    logger.debug(
        "Build italic CJK masters: angle=%g, skew_factor=%.6f, glyphs=%s",
        italic_angle_deg,
        skew_factor,
        len(font.getGlyphOrder()),
    )

    if masters_are_italic:
        italic_master_paths = master_paths
    else:
        italic_master_paths = generated_italic_master_paths(temp_root)
        make_italic_master_files(
            master_paths,
            italic_master_paths,
            italic_angle_deg,
            process_pool,
            drop_table_tags,
        )

    rebuild_weight_masters_from_paths(font, italic_master_paths)

    update_italic_metadata(font, italic_angle_deg)
    recalculate_font_metrics(font)
    return font


def rebuild_weight_masters_from_paths(
    font: TTFont,
    master_paths: tuple[Path, Path, Path],
) -> None:
    """Replace a variable font's weight masters from static master files."""
    masters: list[TTFont] = []
    try:
        masters.extend(
            load_font(master_path, decompile=True) for master_path in master_paths
        )
        rebuild_weight_masters_with_regular_default(
            font, masters[0], masters[1], masters[2]
        )
    finally:
        for master in masters:
            master.close()


def _glyph_coordinates(font: TTFont, glyph_name: str) -> GlyphCoordinates:
    glyf = font.table("glyf")
    h_metrics = font.table("hmtx").metrics
    v_metrics = font.table("vmtx").metrics if "vmtx" in font else None
    result = glyf._getCoordinatesAndControls(glyph_name, h_metrics, v_metrics)
    if result is None:
        return GlyphCoordinates()
    coordinates, _ = result
    return coordinates


def variation_scalar(support: tuple[float, ...], normalized_position: float) -> float:
    """Return the scalar for one normalized variation support region."""
    min_s, peak, max_s = (
        (support[0], support[1], support[2])
        if len(support) == 3
        else (support[0], support[0], support[0])
    )
    if peak == 0:
        return 0.0
    if normalized_position == peak:
        return 1.0
    if normalized_position < peak:
        if normalized_position < min_s or peak == min_s:
            return 0.0
        return (normalized_position - min_s) / (peak - min_s)
    if normalized_position > max_s or max_s == peak:
        return 0.0
    return (max_s - normalized_position) / (max_s - peak)


def _interpolated_coordinates(
    font: TTFont, glyph_name: str, axis_tag: str, normalized_position: float
) -> GlyphCoordinates:
    coordinates = _glyph_coordinates(font, glyph_name)
    for variation in font["gvar"].variations.get(glyph_name, []):
        support = variation.axes.get(axis_tag)
        if not support or variation.coordinates is None:
            continue

        scalar = variation_scalar(support, normalized_position)

        if scalar == 0:
            continue

        for index, delta in enumerate(variation.coordinates):
            if delta is None:
                continue
            dx, dy = delta
            x, y = coordinates[index]
            coordinates[index] = (x + dx * scalar, y + dy * scalar)

    return coordinates


def _require_tables(font: TTFont, table_tags: Iterable[str], font_role: str) -> None:
    for table_tag in table_tags:
        if table_tag not in font:
            raise ValueError(f"{font_role} is missing required table: {table_tag}")


def _build_weight_variations(
    default_coordinates: GlyphCoordinates,
    min_coordinates: GlyphCoordinates,
    max_coordinates: GlyphCoordinates,
    glyph_name: str,
    axis_tag: str = WEIGHT_AXIS_TAG,
) -> list[TupleVariation]:
    variations: list[TupleVariation] = []

    if (
        len(default_coordinates) != len(max_coordinates)
        or len(default_coordinates) != len(min_coordinates)
        or len(min_coordinates) != len(max_coordinates)
    ):
        raise ValueError(
            f"Point count mismatch for {glyph_name}: "
            f"default={len(default_coordinates)}, min={len(min_coordinates)}, max={len(max_coordinates)}"
        )

    min_delta = [
        (otRound(to_x - from_x), otRound(to_y - from_y))
        for (from_x, from_y), (to_x, to_y) in zip(
            cast("Iterable[tuple[float, float]]", default_coordinates),
            cast("Iterable[tuple[float, float]]", min_coordinates),
            strict=False,
        )
    ]

    max_delta = [
        (otRound(to_x - from_x), otRound(to_y - from_y))
        for (from_x, from_y), (to_x, to_y) in zip(
            cast("Iterable[tuple[float, float]]", default_coordinates),
            cast("Iterable[tuple[float, float]]", max_coordinates),
            strict=False,
        )
    ]

    if any(dx or dy for dx, dy in min_delta):
        variations.append(TupleVariation({axis_tag: MIN_WEIGHT_SUPPORT}, min_delta))
    if any(dx or dy for dx, dy in max_delta):
        variations.append(TupleVariation({axis_tag: MAX_WEIGHT_SUPPORT}, max_delta))
    return variations


def _validate_merge_inputs(base: TTFont, extra: TTFont) -> None:
    required_tables = (*VARIABLE_GLYF_TABLES, "cmap", "fvar", "head", "maxp")
    _require_tables(base, required_tables, "Base font")
    _require_tables(extra, required_tables, "Extra font")

    base_head = base.table("head")
    extra_head = extra.table("head")
    if base_head.unitsPerEm != extra_head.unitsPerEm:
        raise ValueError(
            "Cannot merge fonts with different UPEM values: "
            f"{base_head.unitsPerEm} != {extra_head.unitsPerEm}"
        )

    base_axes = [
        (axis.axisTag, axis.minValue, axis.defaultValue, axis.maxValue)
        for axis in base["fvar"].axes
    ]
    extra_axes = [
        (axis.axisTag, axis.minValue, axis.defaultValue, axis.maxValue)
        for axis in extra["fvar"].axes
    ]
    if base_axes != extra_axes:
        raise ValueError(
            "Cannot merge fonts with different variable axes: "
            f"{base_axes} != {extra_axes}"
        )


def _merge_glyph_tables(base: TTFont, extra: TTFont) -> list[str]:
    base_glyph_order = base.getGlyphOrder()
    extra_glyph_order = extra.getGlyphOrder()
    base_glyphs = set(base_glyph_order)
    glyphs_to_add = [
        glyph_name for glyph_name in extra_glyph_order if glyph_name not in base_glyphs
    ]

    base_glyf = base["glyf"]
    extra_glyf = extra["glyf"]
    base_hmtx = base["hmtx"]
    extra_hmtx = extra["hmtx"]
    base_gvar = base["gvar"]
    extra_gvar = extra["gvar"]

    for glyph_name in glyphs_to_add:
        _copy_glyph_outline_and_metrics(
            glyph_name, base_glyf, base_hmtx, extra_glyf, extra_hmtx
        )
        base_gvar.variations[glyph_name] = deepcopy(
            extra_gvar.variations.get(glyph_name, [])
        )

    _append_glyph_order(base, base_glyph_order, glyphs_to_add)
    return glyphs_to_add


def _copy_glyph_outline_and_metrics(
    glyph_name: str,
    target_glyf: Any,
    target_hmtx: Any,
    source_glyf: Any,
    source_hmtx: Any,
) -> None:
    target_glyf.glyphs[glyph_name] = deepcopy(source_glyf.glyphs[glyph_name])
    target_hmtx.metrics[glyph_name] = source_hmtx.metrics[glyph_name]


def _append_glyph_order(
    font: TTFont, base_glyph_order: list[str], glyphs_to_add: list[str]
) -> None:
    glyph_order = base_glyph_order + glyphs_to_add
    font.setGlyphOrder(glyph_order)
    font["maxp"].numGlyphs = len(glyph_order)
