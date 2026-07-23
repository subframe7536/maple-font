from __future__ import annotations


from fontTools.merge import Merger
from scripts.font_ops.fonttools import TTFont, adapt_ttfont

from scripts.utils.logging import logger


def merge_ttfonts(
    base_font_path: str, extra_font_path: str, use_pyftmerge: bool = False
) -> TTFont:
    if use_pyftmerge:
        return adapt_ttfont(Merger().merge([base_font_path, extra_font_path]))

    try:
        base_font = TTFont(base_font_path)
        extra_font = TTFont(extra_font_path)
        base_glyf = base_font["glyf"]
        extra_glyf = extra_font["glyf"]
        base_glyph_order = base_font.getGlyphOrder()
        extra_glyph_order = extra_font.getGlyphOrder()
        base_hmtx = base_font["hmtx"] if "hmtx" in base_font else None
        extra_hmtx = extra_font["hmtx"] if "hmtx" in extra_font else None
        base_glyph_names = set(base_glyph_order)
        glyphs_to_add: list[str] = []

        for glyph_name in extra_glyph_order:
            if glyph_name in base_glyph_names:
                continue
            base_glyf.glyphs[glyph_name] = extra_glyf.glyphs[glyph_name]
            if base_hmtx and extra_hmtx and glyph_name in extra_hmtx.metrics:
                base_hmtx.metrics[glyph_name] = extra_hmtx.metrics[glyph_name]
            elif base_hmtx:
                base_hmtx.metrics[glyph_name] = (0, 0)
            glyphs_to_add.append(glyph_name)

        if not glyphs_to_add:
            logger.debug("Skip font merge because no new glyphs were found")
            return base_font

        updated_glyph_order = base_glyph_order + glyphs_to_add
        base_font.setGlyphOrder(updated_glyph_order)
        base_font["maxp"].numGlyphs = len(updated_glyph_order)

        if "cmap" in extra_font and "cmap" in base_font:
            _merge_cmap(base_font, extra_font, set(glyphs_to_add))

        if "hhea" in base_font:
            if base_hmtx:
                base_font.table("hhea").numberOfHMetrics = len(base_hmtx.metrics)
            base_font.table("hhea").recalc(base_font)
        return base_font
    except Exception:
        raise


def _merge_cmap(base_font: TTFont, extra_font: TTFont, glyphs_to_add: set[str]) -> None:
    base_codepoints = set(base_font["cmap"].getBestCmap() or {})
    extra_cmap = extra_font["cmap"].getBestCmap() or {}
    entries = {
        codepoint: glyph_name
        for codepoint, glyph_name in extra_cmap.items()
        if glyph_name in glyphs_to_add and codepoint not in base_codepoints
    }
    if not entries:
        return

    for table in base_font["cmap"].tables:
        if table.isUnicode():
            table.cmap.update(
                {
                    codepoint: glyph_name
                    for codepoint, glyph_name in entries.items()
                    if _cmap_supports_codepoint(table.format, codepoint)
                }
            )


def _cmap_supports_codepoint(table_format: int, codepoint: int) -> bool:
    if table_format == 0:
        return codepoint <= 0xFF
    if table_format in (2, 4, 6):
        return codepoint <= 0xFFFF
    if table_format in (10, 12, 13):
        return codepoint <= 0x10FFFF
    return codepoint <= 0xFFFF
