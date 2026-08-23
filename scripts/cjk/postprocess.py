from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scripts.cjk.outlines import convert_cff_static_to_glyf
from scripts.cjk.variable import (
    drop_font_tables,
    recalculate_font_metrics,
    update_italic_metadata,
    weight_axis,
)
from scripts.font_ops.fonttools import load_font
from scripts.font_ops.names import set_font_name, update_font_names
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from pathlib import Path

    from scripts.cjk.config import CJKBuildConfig
    from scripts.font_ops.fonttools import TTFont
    from scripts.font_ops.names import FontNameConfig

RESERVED_NAME_IDS = {1, 2, 4, 6, 16, 17, 25}


def remove_mac_name_records(font: TTFont) -> bool:
    """Remove legacy Mac name records from a font."""
    if "name" not in font:
        return False
    before = len(font["name"].names)
    font["name"].removeNames(platformID=1)
    return len(font["name"].names) != before


def prune_stat(font: TTFont) -> None:
    """Prune STAT table to weight axis only."""
    if "STAT" not in font:
        return
    stat = font["STAT"].table
    if getattr(stat, "DesignAxisRecord", None):
        axes = [axis for axis in stat.DesignAxisRecord.Axis if axis.AxisTag == "wght"]
        stat.DesignAxisRecord.Axis = axes
        stat.DesignAxisRecord.AxisCount = len(axes)
        stat.DesignAxisCount = len(axes)


def recalculate_font(font: TTFont, config: CJKBuildConfig) -> None:
    """Recalculate common font metrics."""
    recalculate_font_metrics(font)
    if "OS/2" in font:
        font["OS/2"].xAvgCharWidth = config.transform.target_advance_width // 2


def load_feature_variable_font(input_path: Path) -> TTFont:
    """Load and validate the Maple feature variable font used as merge base."""
    logger.debug("Load feature variable font: path=%s", input_path)
    font = load_font(input_path, decompile=True)
    if "fvar" not in font:
        raise ValueError(f"Font is missing fvar table: {input_path}")
    axis = weight_axis(font)
    if axis is None:
        raise ValueError(f"Font is missing wght axis: {input_path}")
    return font


def update_variable_font_names(
    font: TTFont,
    subfamily: str,
    config: CJKBuildConfig,
    font_config: FontNameConfig,
) -> None:
    """Update variable font naming after merging CJK glyphs into the feature base."""
    family_name = config.naming.family_name
    full_name = f"{family_name} {subfamily}"
    postscript_name = f"{config.naming.postscript_prefix}-{subfamily.replace(' ', '')}"
    name_table = font["name"]
    move_fvar_instances_from_reserved_name_ids(font)
    for name_id in RESERVED_NAME_IDS:
        name_table.removeNames(nameID=name_id)

    update_font_names(
        font=font,
        font_config=font_config,
        family_name=family_name,
        style_name=subfamily,
        full_name=full_name,
        postscript_name=postscript_name,
        is_skip_subfamily=False,
        preferred_family_name=family_name,
        preferred_style_name=subfamily,
    )
    set_font_name(font, config.naming.postscript_prefix, 25)


def move_fvar_instances_from_reserved_name_ids(font: TTFont) -> None:
    """Keep fvar instance names independent from family/style name records."""
    if "fvar" not in font or "name" not in font:
        return
    name_table = font["name"]
    next_name_id = max(record.nameID for record in name_table.names) + 1
    for instance in font["fvar"].instances:
        if instance.subfamilyNameID not in RESERVED_NAME_IDS:
            continue
        name = name_table.getDebugName(instance.subfamilyNameID)
        if not name:
            continue
        replacement = find_name_id(name_table, name, RESERVED_NAME_IDS)
        if replacement is None:
            replacement = next_name_id
            next_name_id += 1
            name_table.setName(name, replacement, 3, 1, 0x409)
        instance.subfamilyNameID = replacement


def find_name_id(name_table: Any, value: str, excluded: set[int]) -> int | None:
    """Find an existing name ID for a string outside a reserved ID set."""
    for record in name_table.names:
        if record.nameID in excluded:
            continue
        try:
            if record.toUnicode() == value:
                return int(record.nameID)
        except UnicodeDecodeError:
            continue
    return None


def finalize_variable_font(
    font: TTFont,
    added_glyphs: set[str],
    protected_glyphs: set[str],
    subfamily: str,
    config: CJKBuildConfig,
    font_config: FontNameConfig,
    is_italic: bool = False,
) -> None:
    """Apply final metrics, naming, axis, and table cleanup."""
    from scripts.cjk.source import apply_horizontal_metrics, normalize_widths

    apply_horizontal_metrics(font, config)
    if is_italic:
        update_italic_metadata(font, config.transform.italic_angle)
    normalize_widths(
        font, config, glyph_names=added_glyphs, protected_glyphs=protected_glyphs
    )
    prune_stat(font)
    recalculate_font(font, config)
    update_variable_font_names(font, subfamily, config, font_config)


def finalize_static_font_instance(
    instance: TTFont,
    output_path: str,
    name: str,
    is_italic: bool,
    config: CJKBuildConfig,
    font_config: FontNameConfig,
) -> None:
    """Apply static font cleanup and save one instantiated font."""
    subfamily = (f"{name} Italic" if is_italic else name).replace(
        "Regular Italic", "Italic"
    )
    if "CFF " in instance:
        if is_italic:
            update_italic_metadata(instance, config.transform.italic_angle)
        convert_cff_static_to_glyf(instance)
        recalculate_font(instance, config)

    postscript_name = f"{config.naming.postscript_prefix}-{subfamily.replace(' ', '')}"
    update_font_names(
        font=instance,
        font_config=font_config,
        family_name=config.naming.family_name,
        style_name=subfamily,
        full_name=f"{config.naming.family_name} {subfamily}",
        postscript_name=postscript_name,
        is_skip_subfamily=True,
    )
    drop_font_tables(instance, ("kern", "GPOS"))
    remove_mac_name_records(instance)
    instance.save(output_path)
    logger.info("Instantiate CJK base static font to %s", output_path)
