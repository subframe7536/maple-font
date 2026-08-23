from __future__ import annotations

import math
import re
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from fontTools.subset import parse_unicodes

from scripts.cjk.config import (
    CJK_MASTER_WEIGHTS,
    UNICODE_PRESETS,
    CJKBuildConfig,
    CJKMasterLocations,
    CJKUnicodeConfig,
)
from scripts.cjk.variable import weight_axis
from scripts.font_ops.fonttools import load_font

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

AXIS_TAG_PATTERN = re.compile(r"^[ -~]{1,4}$")


def _require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be a finite number")
    return number


def _integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be an integer")
    number = float(value)
    if not math.isfinite(number) or not number.is_integer():
        raise ValueError(f"{field} must be an integer")
    return int(number)


def ordered_master_locations(
    masters: CJKMasterLocations,
) -> tuple[
    tuple[int, dict[str, float]],
    tuple[int, dict[str, float]],
    tuple[int, dict[str, float]],
]:
    """Return CJK master locations in output weight order."""
    missing = [weight for weight in CJK_MASTER_WEIGHTS if weight not in masters]
    if missing:
        raise ValueError(f"source.masters is missing output weights: {missing}")
    return (
        (100, masters[100]),
        (400, masters[400]),
        (800, masters[800]),
    )


def parse_codepoint(value: str | int) -> int:
    """Parse decimal or hex codepoint values."""
    if isinstance(value, int):
        return value
    return int(value, 16 if value.lower().startswith("0x") else 10)


def ranges_from_codepoints(codepoints: Iterable[int]) -> tuple[tuple[int, int], ...]:
    """Compress codepoints into stable contiguous ranges."""
    ordered = sorted(set(codepoints))
    if not ordered:
        return ()

    ranges: list[tuple[int, int]] = []
    start = previous = ordered[0]
    for codepoint in ordered[1:]:
        if codepoint == previous + 1:
            previous = codepoint
            continue
        ranges.append((start, previous))
        start = previous = codepoint
    ranges.append((start, previous))
    return tuple(ranges)


def parse_range(value: str | list[Any] | tuple[Any, Any]) -> tuple[int, int]:
    """Parse a JSON Unicode range entry."""
    if isinstance(value, str):
        if not value.lower().startswith("0x") and "0x" not in value.lower():
            parsed = parse_unicodes(value)
            ranges = ranges_from_codepoints(parsed)
            if len(ranges) == 1:
                return ranges[0]
            raise ValueError(
                "JSON range entries must describe one range each; "
                f"use a list for multiple ranges: {value!r}"
            )
        delimiter = ".." if ".." in value else "-"
        if delimiter not in value:
            point = parse_codepoint(value)
            return point, point
        start, end = value.split(delimiter, 1)
        return parse_codepoint(start), parse_codepoint(end)
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return parse_codepoint(value[0]), parse_codepoint(value[1])
    raise ValueError(f"Invalid Unicode range: {value!r}")


def validate_ranges(ranges: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    """Validate parsed Unicode ranges."""
    result = tuple(ranges)
    for start, end in result:
        if start > end:
            raise ValueError(f"Invalid Unicode range order: {start:#x}-{end:#x}")
        if start < 0 or end > 0x10FFFF:
            raise ValueError(f"Unicode range out of bounds: {start:#x}-{end:#x}")
    return result


def parse_master_locations(value: Any) -> CJKMasterLocations:
    """Parse output-weight keyed source master locations from JSON."""
    if not isinstance(value, dict):
        raise ValueError(
            "source.masters must be an object keyed by output weights 100, 400, and 800"
        )
    masters: CJKMasterLocations = {}
    for raw_weight, raw_axes in value.items():
        try:
            output_weight = int(raw_weight)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid source master output weight: {raw_weight}"
            ) from exc
        if output_weight not in CJK_MASTER_WEIGHTS:
            raise ValueError(
                "source.masters keys must be exactly output weights 100, 400, and 800"
            )
        if not isinstance(raw_axes, dict):
            raise ValueError(f"source.masters.{output_weight} must be an object")
        axes: dict[str, float] = {}
        for raw_axis, coordinate in raw_axes.items():
            if not isinstance(raw_axis, str) or not AXIS_TAG_PATTERN.fullmatch(
                raw_axis
            ):
                raise ValueError(
                    f"source.masters.{output_weight} axis tags must be 1-4 "
                    "printable ASCII characters"
                )
            axes[raw_axis] = _finite_number(
                coordinate,
                f"source.masters.{output_weight}.{raw_axis}",
            )
        if "wght" not in axes:
            raise ValueError(f"source.masters.{output_weight} must include wght")
        masters[output_weight] = axes
    ordered_master_locations(masters)
    return masters


def unicode_config_from_spec(
    spec: str,
    exclude_feature_codepoints: bool = True,
) -> CJKUnicodeConfig:
    """Resolve a named Unicode preset or pyftsubset-style unicode range."""
    if spec in UNICODE_PRESETS:
        return replace(
            UNICODE_PRESETS[spec],
            exclude_feature_codepoints=exclude_feature_codepoints,
        )

    ranges = validate_ranges(ranges_from_codepoints(parse_unicodes(spec)))
    if not ranges:
        raise ValueError(f"No Unicode codepoints parsed from: {spec}")
    return CJKUnicodeConfig(
        ranges=ranges,
        exclude_feature_codepoints=exclude_feature_codepoints,
    )


def apply_unicode_override(
    config: CJKBuildConfig,
    unicode_spec: str | None,
) -> CJKBuildConfig:
    """Override a build config's Unicode filter from CLI input."""
    if not unicode_spec:
        return config
    unicode_config = unicode_config_from_spec(
        unicode_spec,
        exclude_feature_codepoints=config.unicode.exclude_feature_codepoints,
    )
    return replace(config, unicode=unicode_config)


def parse_axis_assignment(value: str) -> tuple[str, float]:
    """Parse a CLI axis assignment like ROND=100."""
    if "=" not in value:
        raise ValueError(f"Axis assignment must use TAG=VALUE syntax: {value}")
    axis, raw_value = value.split("=", 1)
    axis = axis.strip()
    if not AXIS_TAG_PATTERN.fullmatch(axis):
        raise ValueError(f"Axis tag must be 1-4 printable ASCII characters: {value}")
    try:
        coordinate = float(raw_value)
    except ValueError as error:
        raise ValueError(f"axis {axis} must be a finite number") from error
    return axis, _finite_number(coordinate, f"axis {axis}")


def parse_axis_assignments(values: Iterable[str] | None) -> dict[str, float]:
    """Parse CLI axis assignments into a dictionary."""
    axes: dict[str, float] = {}
    for value in values or ():
        axis, coordinate = parse_axis_assignment(value)
        axes[axis] = coordinate
    return axes


def infer_weight_values(
    source_path: Path,
    wght_min: float | None = None,
    wght_regular: float | None = None,
    wght_max: float | None = None,
) -> tuple[float, float, float]:
    """Infer missing weight coordinates from a source variable font."""
    font = load_font(source_path, decompile=True)
    try:
        if "fvar" not in font:
            raise ValueError(f"Source font must be variable: {source_path}")
        axis = weight_axis(font)
        if axis is None:
            raise ValueError(f"Source font is missing wght axis: {source_path}")
        return (
            float(axis.minValue if wght_min is None else wght_min),
            float(axis.defaultValue if wght_regular is None else wght_regular),
            float(axis.maxValue if wght_max is None else wght_max),
        )
    finally:
        font.close()


def build_master_locations(
    source_path: Path,
    fixed_axes: dict[str, float],
    wght_min: float | None = None,
    wght_regular: float | None = None,
    wght_max: float | None = None,
) -> CJKMasterLocations:
    """Build output-weight keyed master locations from source axis coordinates."""
    min_weight, regular_weight, max_weight = infer_weight_values(
        source_path,
        wght_min,
        wght_regular,
        wght_max,
    )
    if not min_weight <= regular_weight <= max_weight:
        raise ValueError("wght values must be ordered min <= regular <= max")

    return {
        100: {**fixed_axes, "wght": min_weight},
        400: {**fixed_axes, "wght": regular_weight},
        800: {**fixed_axes, "wght": max_weight},
    }
