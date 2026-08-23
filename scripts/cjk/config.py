from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from scripts.utils.downloads import validate_archive_path

UnicodePreset = Literal["cn", "jp", "tc", "kr"]
CJK_MASTER_WEIGHTS = (100, 400, 800)
CJKMasterLocations = dict[int, dict[str, float]]

DEFAULT_MAPLE_HHEA_METRICS: dict[str, int] = {
    "ascent": 990,
    "descent": -270,
    "lineGap": 0,
    "caretSlopeRise": 1,
    "caretSlopeRun": 0,
    "caretOffset": 0,
}

DEFAULT_MAPLE_OS2_METRICS: dict[str, int] = {
    "sTypoAscender": 990,
    "sTypoDescender": -270,
    "sTypoLineGap": 0,
    "usWinAscent": 1020,
    "usWinDescent": 300,
    "sxHeight": 550,
    "sCapHeight": 730,
    "usWidthClass": 5,
    "fsSelection": 64,
}

DEFAULT_MAPLE_POST_METRICS: dict[str, int] = {
    "isFixedPitch": 1,
    "underlinePosition": -125,
    "underlineThickness": 50,
    "italicAngle": 0,
}

DEFAULT_CJK_RANGES: tuple[tuple[int, int], ...] = (
    (0x2460, 0x24FF),
    (0x2E80, 0x2EFF),
    (0x2F00, 0x2FDF),
    (0x2FF0, 0x2FFF),
    (0x3000, 0x303F),
    (0x3040, 0x30FF),
    (0x3100, 0x312F),
    (0x31A0, 0x31EF),
    (0x3200, 0x33FF),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0xFE30, 0xFE6F),
    (0xFF00, 0xFFEF),
)

DEFAULT_CN_RANGES = DEFAULT_CJK_RANGES
DEFAULT_JP_RANGES: tuple[tuple[int, int], ...] = (
    (0x2460, 0x24FF),
    (0x3000, 0x303F),
    (0x3040, 0x30FF),
    (0x31F0, 0x31FF),
    (0x3200, 0x33FF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0xFE30, 0xFE6F),
    (0xFF00, 0xFFEF),
)
DEFAULT_TC_RANGES: tuple[tuple[int, int], ...] = (
    (0x2460, 0x24FF),
    (0x2E80, 0x2EFF),
    (0x2F00, 0x2FDF),
    (0x2FF0, 0x2FFF),
    (0x3000, 0x303F),
    (0x3100, 0x312F),
    (0x31A0, 0x31EF),
    (0x3200, 0x33FF),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0xFE30, 0xFE6F),
    (0xFF00, 0xFFEF),
)
DEFAULT_KR_RANGES: tuple[tuple[int, int], ...] = (
    (0x2460, 0x24FF),
    (0x3000, 0x303F),
    (0x3130, 0x318F),
    (0x3200, 0x33FF),
    (0x4E00, 0x9FFF),
    (0xA960, 0xA97F),
    (0xAC00, 0xD7AF),
    (0xD7B0, 0xD7FF),
    (0xF900, 0xFAFF),
    (0xFE30, 0xFE6F),
    (0xFF00, 0xFFEF),
)
DEFAULT_FEATURE_FONT_PATH = Path(
    "sources/cjk/variable-source/MapleMono-CJK-Base-VF.ttf"
)


@dataclass(frozen=True)
class CJKWeightInstance:
    """Named weight instance copied from the feature font."""

    name: str
    coordinate: float


@dataclass(frozen=True)
class CJKDownloadConfig:
    """Optional download used to populate a CJK source cache."""

    url: str
    path_in_archive: str | None = None


@dataclass(frozen=True)
class CJKSourceConfig:
    """Input CJK variable font configuration."""

    path: Path
    masters: CJKMasterLocations
    download: CJKDownloadConfig | None = None
    drop_tables: tuple[str, ...] = ()


@dataclass(frozen=True)
class CJKUnicodeConfig:
    """Unicode filtering configuration for the source font."""

    ranges: tuple[tuple[int, int], ...] = DEFAULT_CJK_RANGES
    filter_encoding: str | None = None
    exclude_feature_codepoints: bool = True


UNICODE_PRESETS: dict[UnicodePreset, CJKUnicodeConfig] = {
    "cn": CJKUnicodeConfig(ranges=DEFAULT_CN_RANGES),
    "jp": CJKUnicodeConfig(ranges=DEFAULT_JP_RANGES, filter_encoding="cp932"),
    "tc": CJKUnicodeConfig(ranges=DEFAULT_TC_RANGES),
    "kr": CJKUnicodeConfig(ranges=DEFAULT_KR_RANGES),
}


@dataclass(frozen=True)
class CJKTransformConfig:
    """Width and outline normalization applied to added CJK glyphs."""

    target_advance_width: int = 1200
    x_scale: float = 1
    y_scale: float = 1
    x_shift: int = 0
    y_shift: int = 0
    italic_angle: float = 10


@dataclass(frozen=True)
class CJKOutputConfig:
    """Output file layout."""

    dir: Path = Path("sources/cjk")
    regular_variable: str = "MapleMono-CJK-VF.ttf"
    italic_variable: str = "MapleMono-CJK-Italic-VF.ttf"
    static_dir: str = "static"
    static_hash: str = "static.sha256"
    archive_name: str = "cjk-base-static.zip"
    variable_hash: str = "variable.sha256"
    variable_archive_name: str = "cjk-base-variable.zip"


@dataclass(frozen=True)
class CJKNamingConfig:
    """Font family and file naming configuration."""

    family_name: str = "Maple Mono CJK"
    postscript_prefix: str = "MapleMonoCJK"
    static_file_prefix: str = "MapleMonoCJK"


@dataclass(frozen=True)
class CJKBuildConfig:
    """Complete CJK build configuration."""

    source: CJKSourceConfig
    locale_name: str = "CJK"
    freeze_feature: str | None = None
    feature_font_path: Path = DEFAULT_FEATURE_FONT_PATH
    output: CJKOutputConfig = field(default_factory=CJKOutputConfig)
    naming: CJKNamingConfig = field(default_factory=CJKNamingConfig)
    unicode: CJKUnicodeConfig = field(default_factory=CJKUnicodeConfig)
    transform: CJKTransformConfig = field(default_factory=CJKTransformConfig)
    temp_dir: Path = Path("sources/cjk/temp")
    hhea_metrics: dict[str, int] = field(
        default_factory=lambda: dict(DEFAULT_MAPLE_HHEA_METRICS)
    )
    os2_metrics: dict[str, int] = field(
        default_factory=lambda: dict(DEFAULT_MAPLE_OS2_METRICS)
    )
    post_metrics: dict[str, int] = field(
        default_factory=lambda: dict(DEFAULT_MAPLE_POST_METRICS)
    )


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


def _source_config_from_data(
    source_data: dict[str, Any], config_base_dir: Path
) -> CJKSourceConfig:
    from scripts.cjk.masters import parse_master_locations
    from scripts.cjk.paths import resolve_config_path

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
    download = _download_config_from_data(source_data)
    drop_tables = source_data.get("drop_tables", [])
    if not isinstance(drop_tables, list) or not all(
        isinstance(tag, str) and TABLE_TAG_PATTERN.fullmatch(tag) for tag in drop_tables
    ):
        raise ValueError("source.drop_tables must be a list of valid table tags")
    if len(drop_tables) != len(set(drop_tables)):
        raise ValueError("source.drop_tables must not contain duplicates")
    return CJKSourceConfig(
        path=resolve_config_path(config_base_dir, source_path, ""),
        masters=parse_master_locations(source_data.get("masters")),
        download=download,
        drop_tables=tuple(drop_tables),
    )


def _download_config_from_data(
    source_data: dict[str, Any],
) -> CJKDownloadConfig | None:
    if "download" not in source_data:
        return None
    download_data = source_data["download"]
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
    return CJKDownloadConfig(url=url, path_in_archive=path_in_archive)


def _unicode_config_from_data(unicode_data: dict[str, Any]) -> CJKUnicodeConfig:
    from scripts.cjk.masters import parse_range, validate_ranges

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
    return CJKUnicodeConfig(
        ranges=validate_ranges(parse_range(item) for item in ranges_data)
        or DEFAULT_CJK_RANGES,
        filter_encoding=filter_encoding,
        exclude_feature_codepoints=exclude_feature_codepoints,
    )


def _transform_config_from_data(transform_data: dict[str, Any]) -> CJKTransformConfig:
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
    return _validate_transform(
        transform_data.get("target_advance_width", 1200),
        transform_data.get("x_scale", 1),
        transform_data.get("y_scale", 1),
        transform_data.get("x_shift", 0),
        transform_data.get("y_shift", 0),
        transform_data.get("italic_angle", 10),
    )


def config_from_data(
    data: dict[str, Any], base_dir: str | Path = "."
) -> CJKBuildConfig:
    """Load a CJK build config from a parsed JSON object."""
    from scripts.cjk.paths import (
        naming_config_from_locale,
        output_config_from_locale,
        temp_dir_from_locale,
        validate_locale_name,
    )

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
    locale_name = validate_locale_name(data.get("locale_name"))
    freeze_feature = data.get("freeze_feature")
    if freeze_feature is not None and (
        not isinstance(freeze_feature, str)
        or not FEATURE_TAG_PATTERN.fullmatch(freeze_feature)
    ):
        raise ValueError(
            "freeze_feature must be a feature tag such as cv99, ss01, or zero"
        )
    unicode_data = _require_object(data.get("unicode", {}), "unicode")
    transform_data = _require_object(data.get("transform", {}), "transform")

    return CJKBuildConfig(
        source=_source_config_from_data(source_data, config_base_dir),
        locale_name=locale_name,
        freeze_feature=freeze_feature,
        output=output_config_from_locale(locale_name),
        naming=naming_config_from_locale(locale_name),
        unicode=_unicode_config_from_data(unicode_data),
        transform=_transform_config_from_data(transform_data),
        temp_dir=temp_dir_from_locale(locale_name),
    )


def config_from_json(config_path: str | Path) -> CJKBuildConfig:
    """Load a CJK build config from JSON."""
    path = Path(config_path)
    data = json.loads(path.read_text(encoding="utf-8"))
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
