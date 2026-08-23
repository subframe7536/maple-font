from __future__ import annotations

from typing import TYPE_CHECKING, cast

from scripts.font_ops.fonttools import TTFont, load_font, remove_overlaps
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from collections.abc import Iterable

    from scripts.font_ops.fonttools import MetricsTable


def _supports_codepoint(table_format: int, codepoint: int) -> bool:
    if table_format == 0:
        return codepoint <= 0xFF
    if table_format in (2, 4, 6):
        return codepoint <= 0xFFFF
    if table_format in (10, 12, 13):
        return codepoint <= 0x10FFFF
    return codepoint <= 0xFFFF


def merge_cmap_entries(
    base_font: TTFont,
    extra_font: TTFont,
    glyph_names: Iterable[str],
) -> set[int]:
    """Merge new Unicode mappings supported by each base cmap subtable."""
    allowed_glyphs = set(glyph_names)
    base_codepoints = set(base_font["cmap"].getBestCmap() or {})
    entries = {
        codepoint: glyph_name
        for codepoint, glyph_name in (extra_font["cmap"].getBestCmap() or {}).items()
        if glyph_name in allowed_glyphs and codepoint not in base_codepoints
    }

    merged_codepoints: set[int] = set()
    for table in base_font["cmap"].tables:
        if not table.isUnicode():
            continue
        supported_entries = {
            codepoint: glyph_name
            for codepoint, glyph_name in entries.items()
            if _supports_codepoint(table.format, codepoint)
        }
        table.cmap.update(supported_entries)
        merged_codepoints.update(supported_entries)
    return merged_codepoints


def merge_ttfonts(
    base_font_path: str,
    extra_font_path: str,
    *,
    remove_extra_overlaps: bool = False,
) -> TTFont:
    """Merge glyphs missing from the base, optionally simplifying extra outlines."""
    base_font: TTFont | None = None
    extra_font: TTFont | None = None
    try:
        base_font = load_font(base_font_path)
        extra_font = load_font(extra_font_path)
        base_glyf = base_font["glyf"]
        extra_glyf = extra_font["glyf"]
        base_glyph_order = base_font.getGlyphOrder()
        extra_glyph_order = extra_font.getGlyphOrder()
        base_hmtx = cast("MetricsTable | None", base_font.get("hmtx", None))
        extra_hmtx = cast("MetricsTable | None", extra_font.get("hmtx", None))
        base_glyph_names = set(base_glyph_order)
        glyphs_to_add = [
            glyph_name
            for glyph_name in extra_glyph_order
            if glyph_name not in base_glyph_names
        ]

        if not glyphs_to_add:
            logger.debug("Skip font merge because no new glyphs were found")
            return base_font

        if remove_extra_overlaps:
            remove_overlaps(extra_font, glyphs_to_add)

        for glyph_name in glyphs_to_add:
            base_glyf.glyphs[glyph_name] = extra_glyf.glyphs[glyph_name]
            if base_hmtx and extra_hmtx and glyph_name in extra_hmtx.metrics:
                base_hmtx.metrics[glyph_name] = extra_hmtx.metrics[glyph_name]
            elif base_hmtx:
                base_hmtx.metrics[glyph_name] = (0, 0)

        updated_glyph_order = base_glyph_order + glyphs_to_add
        base_font.setGlyphOrder(updated_glyph_order)
        base_font["maxp"].numGlyphs = len(updated_glyph_order)

        if "cmap" in extra_font and "cmap" in base_font:
            merge_cmap_entries(base_font, extra_font, glyphs_to_add)

        if "hhea" in base_font:
            if base_hmtx:
                base_font.table("hhea").numberOfHMetrics = len(base_hmtx.metrics)
            base_font.table("hhea").recalc(base_font)
        return base_font
    except Exception:
        if base_font is not None:
            base_font.close()
        raise
    finally:
        if extra_font is not None:
            extra_font.close()
