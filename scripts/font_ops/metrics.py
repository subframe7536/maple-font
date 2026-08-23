from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.font_ops.fonttools import load_font
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from pathlib import Path

    from scripts.font_ops.fonttools import TTFont


def read_font_vertical_metric(font_path: str | Path) -> tuple[int, int]:
    font = load_font(font_path)
    try:
        return (font["hhea"].ascender, font["hhea"].descender)
    finally:
        font.close()


def verify_glyph_width(
    font: TTFont, expect_widths: list[int], file_name: str | None = None
):
    result = []
    for name in font.getGlyphNames():
        width, _ = font["hmtx"][name]
        if width not in expect_widths:
            result.append([name, width])

    if not result:
        logger.debug("Verified glyph widths: file=%s", file_name)
        return

    unexpected_glyphs = "\n".join(f"{name}  =>  {width}" for name, width in result)
    raise Exception(
        f"{file_name or 'The font'} may contains glyphs that width is not in {expect_widths}, which may broke monospace rule.\n{unexpected_glyphs}"
    )


def adjust_line_height(
    font: TTFont, factor: float, metric: tuple[float, float]
) -> None:
    if "hhea" not in font:
        raise ValueError("No hhea table found.")
    if "OS/2" not in font:
        raise ValueError("No OS/2 table found.")

    new_ascender, new_descender = calculate_line_height_metrics(factor, metric)

    logger.debug(
        "Update vertical metrics: ascender=%s, descender=%s",
        new_ascender,
        new_descender,
    )
    font.table("head").yMax = new_ascender
    font.table("head").yMin = new_descender
    font.table("hhea").ascent = new_ascender
    font.table("hhea").descent = new_descender
    os2 = font.table("OS/2")
    os2.sTypoAscender = new_ascender
    os2.sTypoDescender = new_descender
    os2.usWinAscent = new_ascender
    os2.usWinDescent = -new_descender


def calculate_line_height_metrics(
    factor: float,
    metric: tuple[float, float],
) -> tuple[int, int]:
    ascender, descender = metric
    total_height = ascender - descender
    ascender_ratio = ascender / total_height
    target_total_height = round(factor * total_height)
    target_ascender = round(target_total_height * ascender_ratio)
    return target_ascender, target_ascender - target_total_height
