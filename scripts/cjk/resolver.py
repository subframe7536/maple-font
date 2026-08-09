from __future__ import annotations

import json
import math
import re
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fontTools.subset import parse_unicodes

from scripts.cjk.config import (
    CJK_MASTER_WEIGHTS,
    DEFAULT_CJK_RANGES,
    UNICODE_PRESETS,
    CJKBuildConfig,
    CJKDownloadConfig,
    CJKMasterLocations,
    CJKNamingConfig,
    CJKOutputConfig,
    CJKSourceConfig,
    CJKTransformConfig,
    CJKUnicodeConfig,
)
from scripts.cjk.variable import weight_axis
from scripts.font_ops.fonttools import load_font
from scripts.utils.downloads import validate_archive_path

if TYPE_CHECKING:
    import argparse
    from collections.abc import Iterable

LOCALE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9]+$")
AXIS_TAG_PATTERN = re.compile(r"^[ -~]{1,4}$")
TABLE_TAG_PATTERN = re.compile(r"^[A-Za-z0-9/ ]{1,32}$")
FEATURE_TAG_PATTERN = re.compile(r"^(?:cv\d{2}|ss\d{2}|zero)$")


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


def _validate_transform(
    target_advance_width: Any,
    x_scale: Any,
    y_scale: Any,
    x_shift: Any,
    y_shift: Any,
    italic_angle: Any,
) -> CJKTransformConfig:
    target_width = _integer(target_advance_width, "transform.target_advance_width")
    scale_x = _finite_number(x_scale, "transform.x_scale")
    scale_y = _finite_number(y_scale, "transform.y_scale")
    shift_x = _integer(x_shift, "transform.x_shift")
    shift_y = _integer(y_shift, "transform.y_shift")
    angle = _finite_number(italic_angle, "transform.italic_angle")
    if target_width <= 0:
        raise ValueError("target advance width must be greater than zero")
    if scale_x <= 0 or scale_y <= 0:
        raise ValueError("CJK scale factors must be greater than zero")
    return CJKTransformConfig(
        target_advance_width=target_width,
        x_scale=scale_x,
        y_scale=scale_y,
        x_shift=shift_x,
        y_shift=shift_y,
        italic_angle=angle,
    )


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


def resolve_cli_path(value: str | None) -> Path | None:
    """Resolve an optional CLI path relative to the current working directory."""
    return Path(value).expanduser() if value else None


def validate_locale_name(value: Any) -> str:
    """Validate the compact locale suffix used to derive CJK output names."""
    if not isinstance(value, str) or not value:
        raise ValueError("locale_name must be a non-empty ASCII token")
    if not LOCALE_NAME_PATTERN.fullmatch(value):
        raise ValueError("locale_name must contain only ASCII letters and digits")
    return value


def output_config_from_locale(locale_name: str) -> CJKOutputConfig:
    """Derive uncustomizable output paths from the locale suffix."""
    locale_dir = locale_name.lower()
    return CJKOutputConfig(
        dir=Path("source/cjk") / locale_dir,
        regular_variable=f"MapleMono-{locale_name}-VF.ttf",
        italic_variable=f"MapleMono-{locale_name}-Italic-VF.ttf",
        static_dir="static",
        static_hash=f"static-{locale_dir}.sha256",
        archive_name=f"{locale_dir}-base-static.zip",
        variable_hash=f"variable-{locale_dir}.sha256",
        variable_archive_name=f"{locale_dir}-base-variable.zip",
    )


def naming_config_from_locale(locale_name: str) -> CJKNamingConfig:
    """Derive uncustomizable CJK font naming from the locale suffix."""
    return CJKNamingConfig(
        family_name=f"Maple Mono {locale_name}",
        postscript_prefix=f"MapleMono{locale_name}",
        static_file_prefix=f"MapleMono{locale_name}",
    )


def temp_dir_from_locale(locale_name: str) -> Path:
    """Derive the uncustomizable temporary directory from the locale suffix."""
    return Path("source/cjk") / locale_name.lower() / "temp"


def resolve_config_path(base_dir: Path, value: str | None, default: str) -> Path:
    """Resolve a config path relative to the repo root or the config file."""
    raw = Path(value or default)
    if raw.is_absolute():
        return raw
    repo_relative = Path.cwd() / raw
    if repo_relative.exists() or str(raw).startswith("source/"):
        return repo_relative
    return base_dir / raw


def apply_cli_overrides(
    config: CJKBuildConfig, args: argparse.Namespace
) -> CJKBuildConfig:
    """Apply direct CLI overrides on top of a JSON or default config."""
    source_override = resolve_cli_path(getattr(args, "source", None))
    source_path = source_override or config.source.path
    fixed_axes = parse_axis_assignments(getattr(args, "axis", None))
    has_master_override = fixed_axes or any(
        getattr(args, name, None) is not None
        for name in ("wght_min", "wght_regular", "wght_max")
    )
    masters = (
        build_master_locations(
            source_path,
            fixed_axes,
            getattr(args, "wght_min", None),
            getattr(args, "wght_regular", None),
            getattr(args, "wght_max", None),
        )
        if has_master_override
        else config.source.masters
    )
    source = CJKSourceConfig(
        path=source_path,
        masters=masters,
        download=None if source_override is not None else config.source.download,
        drop_tables=tuple(
            getattr(args, "drop_table", None) or config.source.drop_tables
        ),
    )

    unicode = config.unicode
    if getattr(args, "filter_encoding", None) is not None:
        unicode = replace(unicode, filter_encoding=args.filter_encoding)
    if getattr(args, "include_feature_codepoints", False):
        unicode = replace(unicode, exclude_feature_codepoints=False)

    x_shift = getattr(args, "x_shift", None)
    y_shift = getattr(args, "y_shift", None)
    target_advance_width = getattr(args, "target_advance_width", None)
    x_scale = getattr(args, "x_scale", None)
    y_scale = getattr(args, "y_scale", None)
    italic_angle = getattr(args, "italic_angle", None)

    resolved_target_width = (
        config.transform.target_advance_width
        if target_advance_width is None
        else target_advance_width
    )
    resolved_x_scale = config.transform.x_scale if x_scale is None else x_scale
    resolved_y_scale = config.transform.y_scale if y_scale is None else y_scale
    transform = _validate_transform(
        resolved_target_width,
        resolved_x_scale,
        resolved_y_scale,
        config.transform.x_shift if x_shift is None else x_shift,
        config.transform.y_shift if y_shift is None else y_shift,
        config.transform.italic_angle if italic_angle is None else italic_angle,
    )

    return replace(
        config,
        source=source,
        unicode=unicode,
        transform=transform,
    )


def config_from_cli(args: argparse.Namespace) -> CJKBuildConfig:
    """Build a CJK config from direct CLI flags."""
    source_path = resolve_cli_path(getattr(args, "source", None))
    if source_path is None:
        raise ValueError("--source is required when --config is not provided")
    locale_name = validate_locale_name(getattr(args, "locale_name", None) or "CJK")
    config = CJKBuildConfig(
        source=CJKSourceConfig(
            path=source_path,
            masters=build_master_locations(
                source_path,
                parse_axis_assignments(getattr(args, "axis", None)),
                getattr(args, "wght_min", None),
                getattr(args, "wght_regular", None),
                getattr(args, "wght_max", None),
            ),
            drop_tables=tuple(getattr(args, "drop_table", None) or ()),
        ),
        locale_name=locale_name,
        output=output_config_from_locale(locale_name),
        naming=naming_config_from_locale(locale_name),
        temp_dir=temp_dir_from_locale(locale_name),
    )
    return apply_cli_overrides(config, args)


def config_from_data(
    data: dict[str, Any], base_dir: str | Path = "."
) -> CJKBuildConfig:
    """Load a CJK build config from a parsed JSON object."""
    data = _require_object(data, "CJK config")
    config_base_dir = Path(base_dir)
    allowed_keys = {
        "$schema",
        "locale_name",
        "freeze_feature",
        "source",
        "unicode",
        "transform",
    }
    unknown_keys = sorted(set(data) - allowed_keys)
    if unknown_keys:
        raise ValueError(
            "Unsupported CJK config field(s): "
            f"{', '.join(unknown_keys)}. "
            "Output, naming, temp_dir, and incompatible glyph behavior are derived "
            "from locale_name and are not customizable."
        )

    source_data = _require_object(data.get("source", {}), "source")
    source_path = source_data.get("path")
    if not isinstance(source_path, str) or not source_path:
        raise ValueError("source.path is required")
    if "outline_mode" in source_data:
        raise ValueError(
            "source.outline_mode was removed; delete it because the source font "
            "outline format is detected automatically"
        )
    allowed_source_keys = {"path", "download", "masters", "drop_tables"}
    unknown_source_keys = sorted(set(source_data) - allowed_source_keys)
    if unknown_source_keys:
        raise ValueError(
            "Unsupported source field(s): "
            f"{', '.join(unknown_source_keys)}. Supported fields: "
            f"{', '.join(sorted(allowed_source_keys))}."
        )
    locale_name = validate_locale_name(data.get("locale_name"))
    freeze_feature = data.get("freeze_feature")
    if freeze_feature is not None and (
        not isinstance(freeze_feature, str)
        or not FEATURE_TAG_PATTERN.fullmatch(freeze_feature)
    ):
        raise ValueError(
            "freeze_feature must be a feature tag such as cv99, ss01, or zero"
        )
    download_data = source_data.get("download")
    download: CJKDownloadConfig | None = None
    if "download" in source_data:
        if not isinstance(download_data, dict):
            raise ValueError("source.download must be an object")
        allowed_download_keys = {"url", "path_in_archive"}
        unknown_download_keys = sorted(set(download_data) - allowed_download_keys)
        if unknown_download_keys:
            raise ValueError(
                "Unsupported source.download field(s): "
                f"{', '.join(unknown_download_keys)}. Supported fields: "
                f"{', '.join(sorted(allowed_download_keys))}."
            )
        url = download_data.get("url")
        if not isinstance(url, str) or not url.strip():
            raise ValueError("source.download.url must be a non-empty string")
        path_in_archive = download_data.get("path_in_archive")
        if path_in_archive is not None:
            if not isinstance(path_in_archive, str):
                raise ValueError("source.download.path_in_archive must be a string")
            try:
                validate_archive_path(path_in_archive)
            except ValueError as error:
                raise ValueError(
                    f"Invalid source.download.path_in_archive: {error}"
                ) from error
        download = CJKDownloadConfig(
            url=url,
            path_in_archive=path_in_archive,
        )

    drop_tables = source_data.get("drop_tables", [])
    if not isinstance(drop_tables, list) or not all(
        isinstance(tag, str) and TABLE_TAG_PATTERN.fullmatch(tag) for tag in drop_tables
    ):
        raise ValueError("source.drop_tables must be a list of valid table tags")
    if len(drop_tables) != len(set(drop_tables)):
        raise ValueError("source.drop_tables must not contain duplicates")

    unicode_data = _require_object(data.get("unicode", {}), "unicode")
    allowed_unicode_keys = {
        "ranges",
        "filter_encoding",
        "exclude_feature_codepoints",
    }
    unknown_unicode_keys = sorted(set(unicode_data) - allowed_unicode_keys)
    if unknown_unicode_keys:
        raise ValueError(
            "Unsupported unicode field(s): " + ", ".join(unknown_unicode_keys)
        )
    ranges_data = unicode_data.get("ranges", [])
    if not isinstance(ranges_data, list):
        raise ValueError("unicode.ranges must be a list")
    filter_encoding = unicode_data.get("filter_encoding")
    if filter_encoding is not None and (
        not isinstance(filter_encoding, str) or not filter_encoding
    ):
        raise ValueError("unicode.filter_encoding must be a non-empty string or null")
    exclude_feature_codepoints = unicode_data.get("exclude_feature_codepoints", True)
    if not isinstance(exclude_feature_codepoints, bool):
        raise ValueError("unicode.exclude_feature_codepoints must be a boolean")

    transform_data = _require_object(data.get("transform", {}), "transform")
    allowed_transform_keys = {
        "target_advance_width",
        "x_scale",
        "y_scale",
        "x_shift",
        "y_shift",
        "italic_angle",
    }
    unknown_transform_keys = sorted(set(transform_data) - allowed_transform_keys)
    if unknown_transform_keys:
        raise ValueError(
            "Unsupported transform field(s): " + ", ".join(unknown_transform_keys)
        )

    return CJKBuildConfig(
        source=CJKSourceConfig(
            path=resolve_config_path(config_base_dir, source_path, ""),
            masters=parse_master_locations(source_data.get("masters")),
            download=download,
            drop_tables=tuple(drop_tables),
        ),
        locale_name=locale_name,
        freeze_feature=freeze_feature,
        output=output_config_from_locale(locale_name),
        naming=naming_config_from_locale(locale_name),
        unicode=CJKUnicodeConfig(
            ranges=validate_ranges(parse_range(item) for item in ranges_data)
            or DEFAULT_CJK_RANGES,
            filter_encoding=filter_encoding,
            exclude_feature_codepoints=exclude_feature_codepoints,
        ),
        transform=_validate_transform(
            transform_data.get("target_advance_width", 1200),
            transform_data.get("x_scale", 1),
            transform_data.get("y_scale", 1),
            transform_data.get("x_shift", 0),
            transform_data.get("y_shift", 0),
            transform_data.get("italic_angle", 10),
        ),
        temp_dir=temp_dir_from_locale(locale_name),
    )


def config_from_json(config_path: str | Path) -> CJKBuildConfig:
    """Load a CJK build config from JSON."""
    path = Path(config_path)
    data = json.loads(path.read_text())
    return config_from_data(data, path.parent)


def serialize_cjk_build_config(config: CJKBuildConfig) -> dict[str, Any]:
    """Serialize the customizable portion of a CJK build config."""
    source: dict[str, Any] = {
        "path": str(config.source.path),
        "masters": {
            str(weight): dict(axes) for weight, axes in config.source.masters.items()
        },
        "drop_tables": list(config.source.drop_tables),
    }
    if config.source.download is not None:
        source["download"] = {"url": config.source.download.url}
        if config.source.download.path_in_archive is not None:
            source["download"]["path_in_archive"] = (
                config.source.download.path_in_archive
            )
    result = {
        "locale_name": config.locale_name,
        "source": source,
        "unicode": {
            "ranges": [list(range_pair) for range_pair in config.unicode.ranges],
            "filter_encoding": config.unicode.filter_encoding,
            "exclude_feature_codepoints": config.unicode.exclude_feature_codepoints,
        },
        "transform": {
            "target_advance_width": config.transform.target_advance_width,
            "x_scale": config.transform.x_scale,
            "y_scale": config.transform.y_scale,
            "x_shift": config.transform.x_shift,
            "y_shift": config.transform.y_shift,
            "italic_angle": config.transform.italic_angle,
        },
    }
    if config.freeze_feature is not None:
        result["freeze_feature"] = config.freeze_feature
    return result


def add_cjk_arguments(parser: argparse.ArgumentParser) -> None:
    """Add custom CJK build arguments to an argparse parser."""
    parser.add_argument(
        "--config",
        type=str,
        help="Path to a CJK build JSON config",
    )
    parser.add_argument("--source", help="Source glyf/CFF2 variable font path")
    parser.add_argument(
        "--locale-name",
        default="CJK",
        help="Compact locale suffix used for derived output names in direct CLI builds",
    )
    parser.add_argument(
        "--axis",
        action="append",
        help="Fixed source axis coordinate, for example ROND=100",
    )
    parser.add_argument("--wght-min", type=float, help="Source minimum wght coordinate")
    parser.add_argument(
        "--wght-regular",
        type=float,
        help="Source regular/default wght coordinate",
    )
    parser.add_argument("--wght-max", type=float, help="Source maximum wght coordinate")
    parser.add_argument(
        "--drop-table",
        action="append",
        help="Source table tag to drop before subsetting; repeat as needed",
    )
    parser.add_argument("--filter-encoding", help="Optional Unicode encoding filter")
    parser.add_argument(
        "--include-feature-codepoints",
        action="store_true",
        help="Do not exclude codepoints already covered by the feature font",
    )
    parser.add_argument(
        "--unicodes",
        help=(
            "Unicode preset (cn, jp, tc, kr) or pyftsubset-style range, "
            "for example 4E00-9FFF,3000-303F"
        ),
    )
    parser.add_argument("--target-advance-width", type=int, help="Target CJK width")
    parser.add_argument("--x-scale", type=float, help="CJK glyph X scale")
    parser.add_argument("--y-scale", type=float, help="CJK glyph Y scale")
    parser.add_argument("--x-shift", type=int, help="CJK glyph X shift")
    parser.add_argument("--y-shift", type=int, help="CJK glyph Y shift")
    parser.add_argument("--italic-angle", type=float, help="Generated italic angle")
    parser.add_argument(
        "--vf-only",
        action="store_true",
        help="only rebuild variable fonts and skip static font generation",
    )
