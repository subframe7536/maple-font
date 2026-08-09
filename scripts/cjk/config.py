from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

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
DEFAULT_FEATURE_FONT_PATH = Path("source/cjk/variable-source/MapleMono-CJK-Base-VF.ttf")


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

    dir: Path = Path("source/cjk")
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
    temp_dir: Path = Path("source/cjk/temp")
    hhea_metrics: dict[str, int] = field(
        default_factory=lambda: dict(DEFAULT_MAPLE_HHEA_METRICS)
    )
    os2_metrics: dict[str, int] = field(
        default_factory=lambda: dict(DEFAULT_MAPLE_OS2_METRICS)
    )
    post_metrics: dict[str, int] = field(
        default_factory=lambda: dict(DEFAULT_MAPLE_POST_METRICS)
    )
