from __future__ import annotations

import threading
from array import array
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Literal, TypeVar, cast

from fontTools.pens.cu2quPen import Cu2QuMultiPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

from scripts.cjk.variable import (
    drop_font_tables,
    get_unicode_cmap,
)
from scripts.font_ops.fonttools import GlyfTable, TTFont, load_font, newTable
from scripts.utils.logging import configure_logging

if TYPE_CHECKING:
    from collections.abc import Sequence
    from concurrent.futures import Executor
    from pathlib import Path

    from fontTools.ttLib.tables.DefaultTable import DefaultTable

CFF_GLYPH_CHUNK_SIZE = 256
_T = TypeVar("_T")


@dataclass(frozen=True)
class CFFGlyphChunkJob:
    input_paths: tuple[str, str, str]
    glyph_names: tuple[str, ...]


def detect_outline_format(
    font: TTFont,
    source_path: str | Path,
) -> Literal["glyf", "cff2"]:
    """Detect the single supported variable outline format in a source font."""
    has_glyf = "glyf" in font
    has_cff2 = "CFF2" in font
    if has_glyf and has_cff2:
        raise ValueError(
            f"CJK source font contains both glyf and CFF2 outlines: {source_path}; "
            "expected exactly one variable outline format"
        )
    if has_glyf:
        return "glyf"
    if has_cff2:
        return "cff2"
    if "CFF " in font:
        raise ValueError(
            f"CJK source font uses static CFF outlines: {source_path}; "
            "use a variable font containing glyf or CFF2 outlines"
        )
    raise ValueError(
        f"CJK source font has no supported outlines: {source_path}; "
        "expected exactly one of glyf or CFF2"
    )


class CFFChunkWorkerState:
    """Lazily cache CFF masters per worker thread and input path set."""

    _states: ClassVar[
        dict[
            int,
            tuple[
                tuple[str, str, str],
                tuple[TTFont, TTFont, TTFont],
                dict[str, str],
            ],
        ]
    ] = {}

    @classmethod
    def require(
        cls,
        input_paths: tuple[str, str, str],
    ) -> tuple[tuple[TTFont, TTFont, TTFont], dict[str, str]]:
        worker_id = threading.get_ident()
        state = cls._states.get(worker_id)
        if state is not None and state[0] == input_paths:
            return state[1], state[2]
        if state is not None:
            for font in state[1]:
                font.close()

        fonts = cast(
            "tuple[TTFont, TTFont, TTFont]",
            tuple(load_font(path, decompile=True) for path in input_paths),
        )
        labels = glyph_labels(fonts[0], fonts[0].getGlyphOrder())
        cls._states[worker_id] = (input_paths, fonts, labels)
        return fonts, labels


def build_glyf_table(glyph_order: list[str]) -> DefaultTable:
    """Create an empty glyf table for the provided glyph order."""
    table = newTable("glyf")
    glyf = cast("GlyfTable", table)
    glyf.glyphs = {}
    glyf.setGlyphOrder(glyph_order)
    return table


def as_fonttools_glyph_mapping(glyph_set: Any) -> dict[str, Any]:
    """Adapt FontTools' runtime glyph-set mapping to its narrower pen stub type."""
    return cast("dict[str, Any]", glyph_set)


def chunked(items: Sequence[_T], chunk_size: int) -> tuple[tuple[_T, ...], ...]:
    """Split items into stable non-empty chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    return tuple(
        tuple(items[index : index + chunk_size])
        for index in range(0, len(items), chunk_size)
    )


def glyph_labels(font: TTFont, glyph_names: Sequence[str]) -> dict[str, str]:
    """Format glyph labels with Unicode context without repeated cmap scans."""
    codepoints_by_glyph: dict[str, list[int]] = {}
    for codepoint, glyph_name in get_unicode_cmap(font).items():
        codepoints_by_glyph.setdefault(glyph_name, []).append(codepoint)

    labels = {}
    for glyph_name in glyph_names:
        codepoints = sorted(codepoints_by_glyph.get(glyph_name, ()))
        if not codepoints:
            labels[glyph_name] = glyph_name
            continue
        unicode_label = ", ".join(f"U+{codepoint:04X}" for codepoint in codepoints[:3])
        if len(codepoints) > 3:
            unicode_label += ", ..."
        labels[glyph_name] = f"{glyph_name} ({unicode_label})"
    return labels


def reverse_ttglyph_contours(_glyph_name: str, glyph):
    """Reverse a quadratic glyph's contour direction without changing point count."""
    if getattr(glyph, "numberOfContours", 0) == 0:
        return glyph
    coordinates = glyph.coordinates
    flags = glyph.flags
    end_points = list(glyph.endPtsOfContours)
    reversed_coordinates: list[tuple[int | float, int | float]] = []
    reversed_flags = array("B")
    rebuilt_end_points: list[int] = []
    start = 0
    for end in end_points:
        contour_coordinates = list(coordinates[start : end + 1])
        contour_flags = list(flags[start : end + 1])
        if len(contour_coordinates) > 1:
            contour_coordinates = contour_coordinates[:1] + contour_coordinates[:0:-1]
            contour_flags = contour_flags[:1] + contour_flags[:0:-1]
        reversed_coordinates.extend(contour_coordinates)
        reversed_flags.extend(contour_flags)
        rebuilt_end_points.append(len(reversed_coordinates) - 1)
        start = end + 1
    glyph.coordinates[:] = reversed_coordinates
    glyph.flags = reversed_flags
    glyph.endPtsOfContours = rebuilt_end_points
    return glyph


def record_glyph_commands(
    glyph_set, glyph_name: str
) -> list[tuple[str, tuple[Any, ...]]]:
    """Record segment-pen commands for one glyph."""
    pen = RecordingPen()
    glyph_set[glyph_name].draw(pen)
    return pen.value


def validate_compatible_glyph_commands(
    glyph_name: str,
    recordings: Sequence[list[tuple[str, tuple[Any, ...]]]],
) -> None:
    """Require all masters to expose the same segment command structure."""
    if not recordings:
        return
    reference = recordings[0]
    for master_index, recording in enumerate(recordings[1:], start=1):
        if len(recording) != len(reference):
            raise ValueError(
                f"Incompatible source outlines for {glyph_name}: "
                f"command count {len(reference)} != {len(recording)} "
                f"(master index 0 vs {master_index})"
            )
        for op_index, ((ref_op, ref_args), (op, args)) in enumerate(
            zip(reference, recording, strict=False)
        ):
            if op != ref_op or len(args) != len(ref_args):
                raise ValueError(
                    f"Incompatible source outlines for {glyph_name}: "
                    f"command #{op_index} {ref_op}/{len(ref_args)} != "
                    f"{op}/{len(args)} (master index 0 vs {master_index})"
                )
            if op == "addComponent" and args[0] != ref_args[0]:
                raise ValueError(
                    f"Incompatible source outlines for {glyph_name}: "
                    f"component mismatch {ref_args[0]} != {args[0]} "
                    f"(master index 0 vs {master_index})"
                )


def _dispatch_pen_command(
    multi_pen: Cu2QuMultiPen,
    glyph_name: str,
    operation: str,
    args_list: list[tuple[Any, ...]],
) -> None:
    if operation == "moveTo":
        multi_pen.moveTo(args_list)
    elif operation == "lineTo":
        multi_pen.lineTo(args_list)
    elif operation == "curveTo":
        multi_pen.curveTo(args_list)
    elif operation == "qCurveTo":
        multi_pen.qCurveTo(args_list)
    elif operation == "closePath":
        multi_pen.closePath()
    elif operation == "endPath":
        multi_pen.endPath()
    elif operation == "addComponent":
        component_names = {args[0] for args in args_list}
        if len(component_names) != 1:
            raise ValueError(
                f"Incompatible source outlines for {glyph_name}: "
                f"component names differ across masters"
            )
        multi_pen.addComponent(args_list[0][0], [args[1] for args in args_list])
    else:
        raise ValueError(
            f"Unsupported segment operation {operation!r} while converting "
            f"{glyph_name} from CFF to glyf"
        )


def replay_multi_glyph_commands(
    glyph_name: str,
    recordings: Sequence[list[tuple[str, tuple[Any, ...]]]],
    multi_pen: Cu2QuMultiPen,
) -> None:
    """Replay recorded glyph commands into a multi-master cu2qu pen."""
    validate_compatible_glyph_commands(glyph_name, recordings)
    for commands in zip(*recordings, strict=False):
        operation = commands[0][0]
        args_list = [args for _, args in commands]
        _dispatch_pen_command(multi_pen, glyph_name, operation, args_list)


def convert_cff_glyphs_from_loaded_fonts(
    fonts: Sequence[TTFont],
    glyph_names: Sequence[str],
    labels: dict[str, str] | None = None,
) -> dict[str, tuple[Any, ...]]:
    """Convert glyphs jointly across loaded compatible CFF masters."""
    glyph_sets = [font.getGlyphSet() for font in fonts]
    labels = labels if labels is not None else glyph_labels(fonts[0], glyph_names)
    converted_glyphs: dict[str, tuple[Any, ...]] = {}

    for glyph_name in glyph_names:
        tt_pens = [
            TTGlyphPen(
                as_fonttools_glyph_mapping(glyph_set),
                outputImpliedClosingLine=True,
            )
            for glyph_set in glyph_sets
        ]
        recordings = [
            record_glyph_commands(glyph_set, glyph_name) for glyph_set in glyph_sets
        ]
        replay_multi_glyph_commands(
            labels[glyph_name],
            recordings,
            Cu2QuMultiPen(tt_pens, max_err=1.0, reverse_direction=False),
        )
        converted_glyphs[glyph_name] = tuple(
            reverse_ttglyph_contours(glyph_name, tt_pen.glyph()) for tt_pen in tt_pens
        )
    return converted_glyphs


def validate_cff_master_fonts(fonts: Sequence[TTFont]) -> list[str]:
    """Validate compatible CFF inputs and return the shared glyph order."""
    if not fonts or "CFF " not in fonts[0]:
        return []
    glyph_order = fonts[0].getGlyphOrder()
    glyph_orders = [font.getGlyphOrder() for font in fonts]
    if any(order != glyph_order for order in glyph_orders[1:]):
        raise ValueError("CFF source master glyph orders must match before cu2qu")
    return glyph_order


def install_glyf_tables(
    fonts: Sequence[TTFont],
    glyph_order: list[str],
    converted_glyphs: dict[str, tuple[Any, ...]],
) -> None:
    """Install converted quadratic glyphs into fonts."""
    glyf_tables = [build_glyf_table(glyph_order) for _ in fonts]
    for glyph_name in glyph_order:
        glyphs = converted_glyphs[glyph_name]
        for glyph, table in zip(glyphs, glyf_tables, strict=False):
            glyf = cast("GlyfTable", table)
            glyf.glyphs[glyph_name] = glyph
            if getattr(glyph, "numberOfContours", 0) > 0:
                glyph.recalcBounds(glyf)
            else:
                glyph.xMin = glyph.yMin = glyph.xMax = glyph.yMax = 0

    for font, table in zip(fonts, glyf_tables, strict=False):
        font["glyf"] = table
        font["loca"] = newTable("loca")
        drop_font_tables(font, ("CFF ", "CFF2", "VORG", "VVAR", "vhea", "vmtx"))
        update_maxp_for_glyf(font)


def install_existing_glyf_tables(
    fonts: Sequence[TTFont],
    glyf_tables: Sequence[Any],
) -> None:
    """Install already-built glyf tables into fonts."""
    for font, glyf in zip(fonts, glyf_tables, strict=False):
        font["glyf"] = glyf
        font["loca"] = newTable("loca")
        drop_font_tables(font, ("CFF ", "CFF2", "VORG", "VVAR", "vhea", "vmtx"))
        update_maxp_for_glyf(font)


def convert_cff_fonts_to_glyf(fonts: Sequence[TTFont]) -> None:
    """Convert one or more compatible static CFF fonts to TrueType glyf outlines."""
    glyph_order = validate_cff_master_fonts(fonts)
    if not glyph_order:
        return
    converted_glyphs = convert_cff_glyphs_from_loaded_fonts(fonts, glyph_order)
    install_glyf_tables(fonts, glyph_order, converted_glyphs)


def convert_cff_glyph_chunk_from_worker(
    job: CFFGlyphChunkJob,
) -> dict[str, tuple[Any, ...]]:
    """Convert one glyph chunk using worker-local, lazily loaded masters."""
    configure_logging()
    fonts, labels = CFFChunkWorkerState.require(job.input_paths)
    return convert_cff_glyphs_from_loaded_fonts(
        fonts,
        job.glyph_names,
        labels,
    )


def cff_master_glyph_order(input_paths: tuple[str, str, str]) -> list[str]:
    """Read and validate shared glyph order from CFF master files."""
    expected_order: list[str] | None = None
    for path in input_paths:
        font = load_font(path, decompile=True)
        try:
            if "CFF " not in font:
                return []
            glyph_order = font.getGlyphOrder()
            if expected_order is None:
                expected_order = glyph_order
            elif glyph_order != expected_order:
                raise ValueError(
                    "CFF source master glyph orders must match before cu2qu"
                )
        finally:
            font.close()
    return expected_order or []


def add_converted_glyphs_to_glyf_tables(
    glyf_tables: Sequence[Any],
    converted_glyphs: dict[str, tuple[Any, ...]],
) -> None:
    """Append one converted chunk into output glyf tables."""
    for glyph_name, glyphs in converted_glyphs.items():
        for glyph, glyf in zip(glyphs, glyf_tables, strict=False):
            glyf.glyphs[glyph_name] = glyph
            if getattr(glyph, "numberOfContours", 0) > 0:
                glyph.recalcBounds(glyf)
            else:
                glyph.xMin = glyph.yMin = glyph.xMax = glyph.yMax = 0


def convert_cff_master_files_to_glyf_tables_parallel(
    input_paths: tuple[str, str, str],
    glyph_order: list[str],
    executor: Executor,
    chunk_size: int = CFF_GLYPH_CHUNK_SIZE,
) -> tuple[Any, Any, Any]:
    """Convert compatible CFF masters into glyf tables with glyph chunks."""
    if not glyph_order:
        return cast(
            "tuple[Any, Any, Any]", tuple(build_glyf_table([]) for _ in input_paths)
        )

    chunks = chunked(tuple(glyph_order), chunk_size)
    glyf_tables = [build_glyf_table(glyph_order) for _ in input_paths]
    futures = [
        executor.submit(
            convert_cff_glyph_chunk_from_worker,
            CFFGlyphChunkJob(input_paths, glyph_chunk),
        )
        for glyph_chunk in chunks
    ]
    for future in futures:
        add_converted_glyphs_to_glyf_tables(glyf_tables, future.result())

    return cast("tuple[Any, Any, Any]", tuple(glyf_tables))


def convert_cff_static_to_glyf(font: TTFont) -> None:
    """Convert a static CFF font to TrueType glyf outlines."""
    convert_cff_fonts_to_glyf((font,))


def update_maxp_for_glyf(font: TTFont) -> None:
    """Populate TrueType maxp fields after CFF to glyf conversion."""
    font["maxp"].tableVersion = 0x00010000
    for attr, value in {
        "maxZones": 2,
        "maxTwilightPoints": 0,
        "maxStorage": 0,
        "maxFunctionDefs": 0,
        "maxInstructionDefs": 0,
        "maxStackElements": 0,
        "maxSizeOfInstructions": 0,
        "maxComponentElements": 0,
        "maxComponentDepth": 0,
    }.items():
        setattr(font["maxp"], attr, value)
    font["maxp"].numGlyphs = len(font.getGlyphOrder())
    font["maxp"].recalc(font)
