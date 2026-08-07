"""Typed FontTools boundary for Maple's font operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Protocol, cast, overload

from fontTools.ttLib import TTFont as FontToolsTTFont
from fontTools.ttLib import newTable
from fontTools.varLib.instancer import (
    instantiateVariableFont as _instantiate_variable_font,
)


class PanoseTable(Protocol):
    bFamilyType: int
    bProportion: int
    bSpacing: int


class OS2Table(Protocol):
    fsSelection: int
    panose: PanoseTable
    sCapHeight: int
    sTypoAscender: int
    sTypoDescender: int
    sxHeight: int
    ulCodePageRange1: int
    usWeightClass: int
    usWinAscent: int
    usWinDescent: int
    version: int
    xAvgCharWidth: int

    def recalcAvgCharWidth(self, ttFont: Any) -> None: ...

    def recalcUnicodeRanges(self, ttFont: Any) -> None: ...

    def recalcCodePageRanges(self, ttFont: Any) -> None: ...


class HeadTable(Protocol):
    created: int
    flags: int
    macStyle: int
    modified: int
    unitsPerEm: int
    yMax: int
    yMin: int


class HheaTable(Protocol):
    advanceWidthMax: int
    ascent: int
    caretSlopeRise: int
    caretSlopeRun: int
    descent: int
    ascender: int
    descender: int
    numberOfHMetrics: int

    def recalc(self, ttFont: Any) -> None: ...


class PostTable(Protocol):
    isFixedPitch: bool
    italicAngle: float


class GlyfTable(Protocol):
    glyphs: dict[str, Any]

    def __contains__(self, glyph_name: str) -> bool: ...

    def __getitem__(self, glyph_name: str) -> Any: ...

    def setGlyphOrder(self, glyph_order: list[str]) -> None: ...

    def _setCoordinates(
        self,
        glyph_name: str,
        coordinates: Any,
        h_metrics: dict[str, tuple[int, int]],
        v_metrics: dict[str, tuple[int, int]] | None,
    ) -> None: ...

    def _getCoordinatesAndControls(
        self,
        glyph_name: str,
        h_metrics: dict[str, tuple[int, int]],
        v_metrics: dict[str, tuple[int, int]] | None,
    ) -> Any: ...


class CFFTable(Protocol):
    cff: Any


class GaspTable(Protocol):
    gaspRange: dict[int, int]


class MaxpTable(Protocol):
    maxZones: int


class MetaTable(Protocol):
    data: dict[str, str | bytes]


class MetricsTable(Protocol):
    metrics: dict[str, tuple[int, int]]

    def __getitem__(self, glyph_name: str) -> tuple[int, int]: ...

    def __setitem__(self, glyph_name: str, value: tuple[int, int]) -> None: ...


class SubsetOptions(Protocol):
    layout_features: list[str]
    name_IDs: list[int | str]
    name_legacy: bool
    name_languages: list[int | str]
    notdef_outline: bool
    recalc_bounds: bool
    recalc_timestamp: bool
    recommended_glyphs: bool


class TTFont(FontToolsTTFont):
    """FontTools font with typed access for tables used by the build."""

    @overload
    def table(self, tag: Literal["OS/2"]) -> OS2Table: ...

    @overload
    def table(self, tag: Literal["head"]) -> HeadTable: ...

    @overload
    def table(self, tag: Literal["hhea"]) -> HheaTable: ...

    @overload
    def table(self, tag: Literal["post"]) -> PostTable: ...

    @overload
    def table(self, tag: Literal["glyf"]) -> GlyfTable: ...

    @overload
    def table(self, tag: Literal["CFF ", "CFF2"]) -> CFFTable: ...

    @overload
    def table(self, tag: Literal["gasp"]) -> GaspTable: ...

    @overload
    def table(self, tag: Literal["maxp"]) -> MaxpTable: ...

    @overload
    def table(self, tag: Literal["hmtx", "vmtx"]) -> MetricsTable: ...

    @overload
    def table(self, tag: str | bytes) -> object: ...

    def table(self, tag: str | bytes) -> object:
        return super().__getitem__(tag)


def load_font(font_path: str | Path, *, decompile: bool = False) -> TTFont:
    """Load a font into memory without retaining a source-file handle."""
    font = TTFont(font_path, lazy=False, recalcTimestamp=False)
    try:
        if decompile:
            font.ensureDecompiled()
    except Exception:
        font.close()
        raise
    return font


def adapt_ttfont(font: FontToolsTTFont) -> TTFont:
    """View a FontTools font through the project's structural typed boundary."""
    return cast("TTFont", font)


def instantiate_variable_font(
    font: TTFont,
    axis_limits: dict[str, float],
    *,
    optimize: bool = True,
    static: bool = False,
    downgrade_cff2: bool = False,
) -> TTFont:
    """Instantiate a wrapper font while preserving its concrete type."""
    instance = _instantiate_variable_font(
        font,
        axis_limits,
        inplace=False,
        optimize=optimize,
        static=static,
        downgradeCFF2=downgrade_cff2,
    )
    return adapt_ttfont(instance)


def save_font_atomic(font: TTFont, target_path: str | Path) -> Path:
    """Save a font through a sibling temporary file and atomically publish it."""
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    temporary.unlink(missing_ok=True)
    try:
        font.save(temporary)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


__all__ = [
    "CFFTable",
    "GaspTable",
    "GlyfTable",
    "HeadTable",
    "HheaTable",
    "MaxpTable",
    "MetaTable",
    "MetricsTable",
    "OS2Table",
    "PanoseTable",
    "PostTable",
    "SubsetOptions",
    "TTFont",
    "adapt_ttfont",
    "instantiate_variable_font",
    "newTable",
    "save_font_atomic",
]
