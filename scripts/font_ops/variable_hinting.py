"""Conservative native TrueType alignment for merged variable Han glyphs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fontTools.ttLib.tables.ttProgram import Program
from fontTools.unicodedata import script

from scripts.utils.errors import BuildDependencyError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from scripts.font_ops.fonttools import TTFont


# Include the program revision in the opt-in stage cache key.
VARIABLE_HINTING_REVISION = 1


def _horizontal_anchor(
    points: Sequence[tuple[int, int]],
    ends: Sequence[int],
    flags: Sequence[int],
    upem: int,
) -> int | None:
    best: tuple[int, int, int] | None = None
    start = 0
    for end in ends:
        for i in range(start, end + 1):
            j = start if i == end else i + 1
            if not flags[i] & flags[j] & 1:
                continue
            x, y = points[i]
            x_next, y_next = points[j]
            width = abs(x - x_next)
            if y == y_next and 5 * width >= upem:
                rank = (width, -abs(20 * y - 7 * upem), -i)
                if best is None or rank > best:
                    best = rank
        start = end + 1
    return -best[2] if best is not None else None


def _alignment_program(anchor: int, contours: int) -> Program:
    # Use the interpolated anchor position at runtime. Apply the same bounded
    # displacement to every contour, leaving phantom points and stems intact.
    instructions = [
        "MPPEM[] PUSHB[] 9 GTEQ[] MPPEM[] PUSHB[] 20 LTEQ[] AND[] IF[]",
        "SVTCA[0] RTG[]",
        f"PUSHW[] {anchor} MDAP[0] PUSHW[] {anchor} {anchor} GC[0]",
        "DUP[] ROUND[00] PUSHB[] 2 CINDEX[] SUB[]",
        "PUSHW[] -8 MAX[] PUSHB[] 8 MIN[] ADD[] SCFS[]",
        *(f"PUSHW[] {i} SHC[1]" for i in range(contours)),
        "EIF[]",
    ]
    program = Program()
    program.fromAssembly(" ".join(instructions).split())
    return program


def autohint_variable_han(font: TTFont) -> int:
    """Add bounded small-size Y alignment to eligible Han outlines in place."""
    if not {"fvar", "gvar", "glyf", "maxp"}.issubset(font.keys()):
        raise BuildDependencyError("CJK VF AutoHint requires a TrueType variable font")
    if not any(axis.axisTag == "wght" for axis in font["fvar"].axes):
        raise BuildDependencyError("CJK VF AutoHint requires a wght axis")

    glyphs = font.table("glyf")
    upem = font.table("head").unitsPerEm
    maxp = font.table("maxp")
    names = {
        name for cp, name in (font.getBestCmap() or {}).items() if script(cp) == "Hani"
    }
    hinted = 0
    for name in sorted(names):
        glyph = glyphs[name]
        if glyph.numberOfContours <= 0:
            continue
        if glyph.program.getBytecode():
            raise BuildDependencyError(
                f"CJK VF AutoHint cannot replace existing hints on {name}"
            )
        anchor = _horizontal_anchor(
            glyph.coordinates, glyph.endPtsOfContours, glyph.flags, upem
        )
        if anchor is None:
            continue
        if anchor > 0x7FFF:
            raise BuildDependencyError(
                f"CJK VF AutoHint anchor index out of range on {name}"
            )
        program = _alignment_program(anchor, glyph.numberOfContours)
        size = len(program.getBytecode())
        if not 0 < size <= 0xFFFF:
            raise BuildDependencyError(
                f"CJK VF AutoHint generated invalid program size on {name}"
            )
        glyph.program = program
        maxp.maxSizeOfInstructions = max(maxp.maxSizeOfInstructions, size)
        hinted += 1

    if not hinted:
        raise BuildDependencyError("CJK VF AutoHint found no eligible Han glyphs")
    maxp.maxStackElements = max(maxp.maxStackElements, 5)
    return hinted
