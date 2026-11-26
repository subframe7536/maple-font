from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, cast

from scripts.font_ops.names import set_font_name
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from scripts.font_ops.fonttools import TTFont


class _OTTables(Protocol):
    AxisRecord: Callable[[], Any]
    AxisValue: Callable[[], Any]
    AxisValueArray: Callable[[], Any]


def add_ital_axis_to_stat(font: TTFont):
    """Add a fake ``ital`` axis to italic variable fonts."""
    logger.debug("Add italic STAT axis")
    from fontTools.ttLib.tables import otTables as ot

    ot_tables = cast("_OTTables", ot)
    name = font["name"]
    stat_table = font["STAT"].table
    name_id = name._findUnusedNameID()
    set_font_name(font, "Italic", name_id, True)

    axis_factory = ot_tables.AxisRecord
    axis = axis_factory()
    axis.AxisTag = "ital"
    axis.AxisOrdering = len(stat_table.DesignAxisRecord.Axis)
    axis.AxisNameID = name_id
    stat_table.DesignAxisRecord.Axis.append(axis)
    stat_table.DesignAxisCount += 1

    axis_value_factory = ot_tables.AxisValue
    axis_value = axis_value_factory()
    axis_value.AxisIndex = axis.AxisOrdering
    axis_value.Flags = 0
    axis_value.Format = 1
    axis_value.ValueNameID = name_id
    axis_value.Value = 1.0
    if stat_table.AxisValueArray is None:
        axis_value_array_factory = ot_tables.AxisValueArray
        stat_table.AxisValueArray = axis_value_array_factory()
        stat_table.AxisValueArray.AxisValue = []
        stat_table.AxisValueCount = 0
    stat_table.AxisValueArray.AxisValue.append(axis_value)
    stat_table.AxisValueCount += 1


def add_weight_axis_values_to_stat(font: TTFont, italic: bool = False) -> None:
    """Expose each named weight instance through the STAT table."""
    if "fvar" not in font or "STAT" not in font or "name" not in font:
        return

    stat_table = font["STAT"].table
    axes = stat_table.DesignAxisRecord.Axis
    weight_axis_index = next(
        (index for index, axis in enumerate(axes) if axis.AxisTag == "wght"), None
    )
    if weight_axis_index is None:
        return

    from fontTools.ttLib.tables import otTables as ot

    ot_tables = cast("_OTTables", ot)

    if stat_table.AxisValueArray is None:
        axis_value_array_factory = ot_tables.AxisValueArray
        stat_table.AxisValueArray = axis_value_array_factory()
        stat_table.AxisValueArray.AxisValue = []

    values = stat_table.AxisValueArray.AxisValue
    existing_values = {
        float(value.Value): value
        for value in values
        if value.AxisIndex == weight_axis_index and value.Format in (1, 3)
    }
    default_weight = next(
        axis.defaultValue for axis in font["fvar"].axes if axis.axisTag == "wght"
    )
    for instance in font["fvar"].instances:
        weight = float(instance.coordinates.get("wght", default_weight))
        value_name_id = instance.subfamilyNameID
        if italic:
            instance_name = font["name"].getDebugName(value_name_id) or "Regular"
            weight_name = instance_name.removesuffix("Italic").rstrip() or "Regular"
            value_name_id = _find_or_add_name_id(font, weight_name)
        existing_value = existing_values.get(weight)
        if existing_value is not None:
            existing_value.ValueNameID = value_name_id
            existing_value.Flags = (existing_value.Flags & ~2) | (
                2 if weight == default_weight else 0
            )
            continue
        axis_value_factory = ot_tables.AxisValue
        value = axis_value_factory()
        value.Format = 1
        value.AxisIndex = weight_axis_index
        value.Flags = 2 if weight == default_weight else 0
        value.ValueNameID = value_name_id
        value.Value = weight
        values.append(value)
        existing_values[weight] = value
    stat_table.AxisValueCount = len(values)


def _find_or_add_name_id(font: TTFont, value: str) -> int:
    for record in font["name"].names:
        try:
            if record.toUnicode() == value:
                return int(record.nameID)
        except UnicodeDecodeError:  # noqa: PERF203
            continue
    name_id = font["name"]._findUnusedNameID()
    set_font_name(font, value, name_id)
    return name_id


def remove_target_glyph(font: TTFont, glyph_name_suffix: str) -> None:
    """Subset out glyphs with the given suffix without stripping retained hints."""
    from scripts.font_ops.subset import SubsetConfig, subset_to_glyphs

    keep_glyphs = [
        glyph_name
        for glyph_name in font.getGlyphOrder()
        if not glyph_name.endswith(glyph_name_suffix)
    ]

    subset_to_glyphs(
        font,
        keep_glyphs,
        options=SubsetConfig(hinting=True, notdef_outline=True),
    )


def alias_codepoints(
    font: TTFont,
    code_mapping: dict[int, int] | None = None,
) -> None:
    if code_mapping is None:
        return

    dst_glyphs: dict[int, str] = {}
    for source, destination in code_mapping.items():
        glyph = next(
            (
                table.cmap[destination]
                for table in font["cmap"].tables
                if table.isUnicode() and destination in table.cmap
            ),
            None,
        )
        if glyph is not None:
            dst_glyphs[source] = glyph

    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap.update(dst_glyphs)
