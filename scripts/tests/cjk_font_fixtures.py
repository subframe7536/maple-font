from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables.TupleVariation import TupleVariation

from scripts.font_ops.fonttools import TTFont, load_font

if TYPE_CHECKING:
    from pathlib import Path

GLYPH_ORDER = [".notdef", "box", "box.component", "cjk"]
CMAP = {0x0041: "box", 0x0042: "box.component", 0x4E00: "cjk"}


def build_test_font(
    path: Path,
    *,
    glyph_order: list[str] | None = None,
    cmap: dict[int, str] | None = None,
    box_width: int = 300,
    cjk_width: int = 420,
    component_target: Literal["box", "cjk"] = "box",
    curved_box: bool = False,
    variable: bool = False,
) -> TTFont:
    """Build, serialize, and reopen a small real TrueType fixture."""
    order = glyph_order if glyph_order is not None else GLYPH_ORDER
    glyphs = _build_glyphs(
        box_width=box_width,
        cjk_width=cjk_width,
        component_target=component_target,
        curved_box=curved_box,
    )
    metrics = {
        ".notdef": (600, 0),
        "box": (box_width + 250, 50),
        "box.component": (box_width + 350, 90),
        "cjk": (cjk_width + 250, 80),
    }

    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap(
        {
            codepoint: name
            for codepoint, name in (CMAP if cmap is None else cmap).items()
            if name in order
        }
    )
    builder.setupGlyf({name: glyphs[name] for name in order})
    builder.setupHorizontalMetrics({name: metrics[name] for name in order})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable(
        {
            "familyName": "CJK Operation Fixture",
            "styleName": "Regular",
            "uniqueFontIdentifier": "CJK Operation Fixture Regular",
            "fullName": "CJK Operation Fixture Regular",
            "psName": "CJKOperationFixture-Regular",
        }
    )
    builder.setupOS2(
        sTypoAscender=800,
        sTypoDescender=-200,
        usWinAscent=800,
        usWinDescent=200,
    )
    builder.setupPost()
    builder.setupMaxp()
    builder.setupHead(created=2082844800, modified=2082844800)
    if variable:
        builder.setupFvar([("wght", 100, 400, 900, "Weight")], [])
        builder.setupGvar(_build_variations(builder.font, order))

    path.parent.mkdir(parents=True, exist_ok=True)
    builder.font.recalcTimestamp = False
    builder.save(path)
    return load_font(path)


def roundtrip_font(font: TTFont, path: Path) -> TTFont:
    """Serialize and reopen a font before assertions inspect its tables."""
    font.recalcTimestamp = False
    font.save(path)
    font.close()
    return load_font(path)


def glyph_coordinates(font: TTFont, glyph_name: str) -> list[tuple[int, int]]:
    glyph = font["glyf"][glyph_name]
    coordinates, _, _ = glyph.getCoordinates(font["glyf"])
    return [(round(x), round(y)) for x, y in coordinates]


def _build_glyphs(
    *,
    box_width: int,
    cjk_width: int,
    component_target: Literal["box", "cjk"],
    curved_box: bool,
) -> dict[str, Any]:
    notdef = TTGlyphPen(None).glyph()
    box = (
        _quadratic_box_glyph(box_width)
        if curved_box
        else _rectangle_glyph(50, box_width, 500)
    )
    cjk = _rectangle_glyph(80, cjk_width, 560)
    glyphs = {".notdef": notdef, "box": box, "cjk": cjk}

    component_pen = TTGlyphPen(glyphs)
    component_pen.addComponent(component_target, (1, 0, 0, 1, 40, 60))
    glyphs["box.component"] = component_pen.glyph()
    return glyphs


def _rectangle_glyph(x_min: int, width: int, height: int):
    pen = TTGlyphPen(None)
    pen.moveTo((x_min, 0))
    pen.lineTo((x_min + width, 0))
    pen.lineTo((x_min + width, height))
    pen.lineTo((x_min, height))
    pen.closePath()
    return pen.glyph()


def _quadratic_box_glyph(width: int):
    pen = TTGlyphPen(None)
    pen.moveTo((50, 0))
    pen.qCurveTo((50 + width // 2, -80), (50 + width, 0))
    pen.lineTo((50 + width, 500))
    pen.lineTo((50, 500))
    pen.closePath()
    return pen.glyph()


def _build_variations(font: Any, glyph_order: list[str]):
    glyf = font["glyf"]
    h_metrics = font["hmtx"].metrics
    variations: dict[str, list[TupleVariation]] = {}
    for glyph_name in glyph_order:
        glyph = glyf[glyph_name]
        if glyph.isComposite() or getattr(glyph, "numberOfContours", 0) <= 0:
            variations[glyph_name] = []
            continue

        coordinates, controls = glyf._getCoordinatesAndControls(
            glyph_name, h_metrics, None
        )
        point_count = controls.endPts[-1] + 1
        x_max = max(x for x, _ in coordinates[:point_count])
        min_deltas = [
            (-40, 0) if index < point_count and x == x_max else (0, 0)
            for index, (x, _) in enumerate(coordinates)
        ]
        max_deltas = [
            (60, 0) if index < point_count and x == x_max else (0, 0)
            for index, (x, _) in enumerate(coordinates)
        ]
        variations[glyph_name] = [
            TupleVariation({"wght": (-1.0, -1.0, 0.0)}, min_deltas),
            TupleVariation({"wght": (0.0, 1.0, 1.0)}, max_deltas),
        ]
    return variations
