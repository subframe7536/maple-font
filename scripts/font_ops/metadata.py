from __future__ import annotations

import math
from typing import TYPE_CHECKING, cast

from fontTools.misc.roundTools import otRound
from fontTools.pens.statisticsPen import StatisticsPen

from scripts.font_ops.fonttools import MetaTable, newTable

if TYPE_CHECKING:
    from scripts.font_ops.fonttools import TTFont

ITALIC_BIT = 0
BOLD_BIT = 5
REGULAR_BIT = 6
OBLIQUE_BIT = 9
MAC_BOLD_BIT = 0
MAC_ITALIC_BIT = 1


def sync_ribbi_style_metadata(
    font: TTFont,
    *,
    is_bold: bool,
    is_italic: bool,
    clear_oblique: bool = True,
) -> None:
    """Synchronize OS/2.fsSelection and head.macStyle RIBBI style bits."""
    if "OS/2" in font:
        os2 = font.table("OS/2")
        os2.fsSelection = _set_bit(os2.fsSelection, ITALIC_BIT, is_italic)
        os2.fsSelection = _set_bit(os2.fsSelection, BOLD_BIT, is_bold)
        os2.fsSelection = _set_bit(
            os2.fsSelection, REGULAR_BIT, not is_italic and not is_bold
        )
        if clear_oblique and os2.version >= 4:
            os2.fsSelection = _set_bit(os2.fsSelection, OBLIQUE_BIT, False)
    if "head" in font:
        head = font.table("head")
        head.macStyle = _set_bit(head.macStyle, MAC_BOLD_BIT, is_bold)
        head.macStyle = _set_bit(head.macStyle, MAC_ITALIC_BIT, is_italic)


def fix_italic_metadata(
    font: TTFont,
    min_slant: float = 2.0,
    *,
    is_bold: bool = False,
) -> float:
    """Recalculate the italic angle and synchronize related font metadata."""
    glyph_set = font.getGlyphSet()
    glyph_name = next((name for name in ("H", "uni0048") if name in glyph_set), None)
    if glyph_name is None:
        raise ValueError("The font does not contain the glyph 'H' or 'uni0048'.")

    pen = StatisticsPen(glyphset=glyph_set)
    glyph_set[glyph_name].draw(pen)
    italic_angle = -math.degrees(math.atan(pen.slant))
    if abs(italic_angle) < abs(min_slant):
        italic_angle = 0.0

    head = font.table("head")
    hhea = font.table("hhea")
    post = font.table("post")

    is_italic = italic_angle != 0
    sync_ribbi_style_metadata(font, is_bold=is_bold, is_italic=is_italic)

    post.italicAngle = italic_angle
    if is_italic:
        hhea.caretSlopeRise = head.unitsPerEm
        hhea.caretSlopeRun = otRound(
            math.tan(math.radians(-italic_angle)) * head.unitsPerEm
        )
    else:
        hhea.caretSlopeRise = 1
        hhea.caretSlopeRun = 0

    return italic_angle


def set_monospace_metadata(font: TTFont) -> None:
    """Set the OpenType metadata used to identify a monospaced font."""
    metrics = font["hmtx"].metrics
    if not metrics:
        raise ValueError("The font does not contain horizontal metrics.")

    os2 = font.table("OS/2")
    hhea = font.table("hhea")
    post = font.table("post")

    post.isFixedPitch = True
    os2.fsType = 0
    os2.panose.bFamilyType = 2
    os2.panose.bProportion = 9
    hhea.advanceWidthMax = max(width for width, _ in metrics.values())
    os2.recalcAvgCharWidth(font)

    if "CFF " in font:
        font["CFF "].cff.topDictIndex[0].isFixedPitch = True


def set_meta_table(
    font: TTFont, design_languages: str, supported_languages: str
) -> None:
    """Set the ScriptLangTags declared in the OpenType META table."""
    meta = newTable("meta")
    cast("MetaTable", meta).data = {
        "dlng": design_languages,
        "slng": supported_languages,
    }
    font["meta"] = meta


def strip_name_whitespace(font: TTFont) -> None:
    """Remove leading and trailing whitespace from every name record."""
    name_table = font["name"]
    for record in list(name_table.names):
        name_table.setName(
            record.toUnicode().strip(),
            record.nameID,
            record.platformID,
            record.platEncID,
            record.langID,
        )


def _set_bit(value: int, bit: int, enabled: bool) -> int:
    mask = 1 << bit
    return value | mask if enabled else value & ~mask
