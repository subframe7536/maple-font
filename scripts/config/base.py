from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from os import getenv
from typing import TYPE_CHECKING, Any, Literal

from scripts.cjk.config import serialize_cjk_build_config
from scripts.font_ops.names import INSTANCE_WEIGHT_MAPPING
from scripts.font_ops.nerd_font import NerdFontVariant

if TYPE_CHECKING:
    from scripts.cjk.config import CJKBuildConfig
    from scripts.cjk.presets import CJKPresetSpec

BuiltinCJKLocaleId = Literal["cn", "jp", "tc", "kr"]
BUILTIN_CJK_LOCALES: tuple[BuiltinCJKLocaleId, ...] = ("cn", "jp", "tc", "kr")
BuildFormatId = Literal["ttf", "otf", "woff2"]
BUILD_FORMATS: tuple[BuildFormatId, ...] = ("ttf", "otf", "woff2")
CJKOutputFormat = Literal["static", "variable"]
CJK_OUTPUT_FORMATS: tuple[CJKOutputFormat, ...] = ("static", "variable")

WIDTH_MAP = {
    "default": 600,
    "narrow": 550,
    "slim": 500,
}


def _parse_codepoint(value: Any, field: str) -> int:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"{field} must use 0x-prefixed hexadecimal notation")
    digits = value[2:]
    if not 4 <= len(digits) <= 6 or any(
        character not in "0123456789abcdefABCDEF" for character in digits
    ):
        raise ValueError(f"Invalid Unicode codepoint for {field}: {value}")
    codepoint = int(digits, 16)
    if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
        raise ValueError(f"Invalid Unicode scalar for {field}: {value}")
    return codepoint


def parse_codepoint_alias(value: Any) -> dict[int, int]:
    if not isinstance(value, dict):
        raise ValueError("codepoint_alias must be an object")
    mapping: dict[int, int] = {}
    for raw_alias, raw_source in value.items():
        alias = _parse_codepoint(raw_alias, "codepoint_alias key")
        source = _parse_codepoint(raw_source, f"codepoint_alias[{raw_alias}]")
        if alias == source:
            raise ValueError(f"Codepoint alias cannot map to itself: {raw_alias}")
        mapping[alias] = source
    return mapping


def serialize_codepoint_alias(mapping: dict[int, int]) -> dict[str, str]:
    return {
        f"0x{alias:04X}": f"0x{source:04X}" for alias, source in sorted(mapping.items())
    }


def default_feature_freeze() -> dict[str, str]:
    return {
        "cv01": "ignore",
        "cv02": "ignore",
        "cv03": "ignore",
        "cv04": "ignore",
        "cv05": "ignore",
        "cv06": "ignore",
        "cv07": "ignore",
        "cv08": "ignore",
        "cv09": "ignore",
        "cv10": "ignore",
        "cv11": "ignore",
        "cv12": "ignore",
        "cv31": "ignore",
        "cv32": "ignore",
        "cv33": "ignore",
        "cv34": "ignore",
        "cv35": "ignore",
        "cv36": "ignore",
        "cv37": "ignore",
        "cv38": "ignore",
        "cv39": "ignore",
        "cv40": "ignore",
        "cv41": "ignore",
        "cv42": "ignore",
        "cv43": "ignore",
        "cv44": "ignore",
        "cv45": "ignore",
        "cv61": "ignore",
        "cv62": "ignore",
        "cv63": "ignore",
        "cv64": "ignore",
        "cv65": "ignore",
        "cv66": "ignore",
        "cv67": "ignore",
        "cv96": "ignore",
        "cv97": "ignore",
        "cv98": "ignore",
        "cv99": "ignore",
        "ss01": "ignore",
        "ss02": "ignore",
        "ss03": "ignore",
        "ss04": "ignore",
        "ss05": "ignore",
        "ss06": "ignore",
        "ss07": "ignore",
        "ss08": "ignore",
        "ss09": "ignore",
        "ss10": "ignore",
        "ss11": "ignore",
        "ss12": "ignore",
        "ss13": "ignore",
        "zero": "ignore",
    }


def normalize_feature_freeze(config: dict[str, str], calt: bool) -> dict[str, str]:
    normalized: dict[str, str] = {}
    invalid_items: list[tuple[str, str]] = []
    for key, value in config.items():
        value_upper = value.upper()
        if value_upper.startswith("ENABLE"):
            normalized[key] = "1"
        elif value_upper.startswith("DISABLE"):
            normalized[key] = "-1"
        elif value_upper.startswith("IGNORE"):
            normalized[key] = "0"
        else:
            invalid_items.append((key, value))

    if invalid_items:
        report = ", ".join(f"{key}: {value}" for key, value in invalid_items)
        raise TypeError(f"Invalid freeze config item: {{ {report} }}")

    normalized["calt"] = "1" if calt else "0"
    return normalized


def format_freeze_config(config: dict[str, str]) -> str:
    """Format resolved feature freeze states for font metadata."""
    return "".join(
        f"+{tag};"
        if status == "1"
        else f"-{tag};"
        if status == "-1" or (tag == "calt" and status == "0")
        else ""
        for tag, status in sorted(config.items())
    )


def default_weight_mapping() -> dict[str, int]:
    return dict(INSTANCE_WEIGHT_MAPPING)


def parse_scale_factor(value: Any) -> tuple[float, float]:
    if isinstance(value, tuple) and len(value) == 2:
        return float(value[0]), float(value[1])
    if isinstance(value, float):
        return value, value
    if isinstance(value, int):
        factor = float(value)
        return factor, factor
    if isinstance(value, list):
        if len(value) != 2:
            raise argparse.ArgumentTypeError(
                "Invalid scale factor format. Use <factor> or <w_factor>,<h_factor>."
            )
        return float(value[0]), float(value[1])
    if not isinstance(value, str):
        raise argparse.ArgumentTypeError(
            "Invalid scale factor format. Use <factor> or <w_factor>,<h_factor>."
        )

    parts = [part.strip() for part in value.split(",") if part.strip()]
    if len(parts) == 1:
        factor = float(parts[0])
        return factor, factor
    if len(parts) == 2:
        return float(parts[0]), float(parts[1])
    raise argparse.ArgumentTypeError(
        "Invalid scale factor format. Use <factor> or <w_factor>,<h_factor>."
    )


def normalize_build_formats(value: Any) -> list[BuildFormatId]:
    if value is None:
        return list(BUILD_FORMATS)

    if isinstance(value, str):
        items = [item.strip().lower() for item in value.split(",")]
    else:
        items: list[str] = []
        for raw in value:
            items.extend(item.strip().lower() for item in str(raw).split(","))

    normalized: list[BuildFormatId] = []
    for item in items:
        if not item:
            continue
        if item not in BUILD_FORMATS:
            raise ValueError(f"Unsupported build format: {item}")
        build_format = item
        if build_format not in normalized:
            normalized.append(build_format)
    return normalized or list(BUILD_FORMATS)


def normalize_cjk_output_format(value: Any) -> CJKOutputFormat:
    normalized = str(value).strip().lower()
    if normalized not in CJK_OUTPUT_FORMATS:
        raise ValueError(f"Unsupported CJK output format: {value}")
    return normalized


def normalize_cjk_locale_list(value: Any) -> list[BuiltinCJKLocaleId]:
    if value is None:
        return []

    if isinstance(value, str):
        items = [item.strip().lower() for item in value.split(",")]
    else:
        items: list[str] = []
        for raw in value:
            items.extend(item.strip().lower() for item in str(raw).split(","))

    normalized: list[BuiltinCJKLocaleId] = []
    for item in items:
        if not item:
            continue
        if item not in BUILTIN_CJK_LOCALES:
            raise ValueError(f"Unsupported CJK locale: {item}")
        locale = item
        if locale not in normalized:
            normalized.append(locale)
    return normalized


@dataclass(slots=True)
class BuildBehaviorConfig:
    archive: bool = False
    debug: bool = False
    cache: bool = False
    least_styles: bool = False
    apply_fea_file: bool = False
    cjk_output_format: CJKOutputFormat = "static"
    formats: list[BuildFormatId] = field(default_factory=lambda: list(BUILD_FORMATS))
    use_cjk_both: bool = False


@dataclass(slots=True)
class FeatureBuildConfig:
    normal: bool = False
    standard_zero: bool = False
    feat: list[str] = field(default_factory=list)
    hinted: bool = True
    liga: bool = True
    infinite_arrow: bool = True
    remove_tag_liga: bool = False
    line_height: float = 1.0
    width: str = "default"


@dataclass(slots=True)
class NerdFontBuildConfig:
    enable: bool = True
    version: str = "3.5.0"
    mono: bool = False
    propo: bool = False
    variable: bool = False
    use_font_patcher: bool = False
    glyphs: list[str] = field(default_factory=lambda: ["--complete"])
    extra_args: list[str] = field(default_factory=list)

    def uses_font_patcher(self) -> bool:
        return bool(
            self.extra_args or self.use_font_patcher or self.glyphs != ["--complete"]
        )

    def to_dict(self, *, include_enable: bool = True) -> dict[str, Any]:
        data = asdict(self)
        if not include_enable:
            data.pop("enable", None)
        return data


@dataclass(slots=True)
class CJKCommonBuildOptions:
    with_nerd_font: bool = True
    fix_meta_table: bool = True
    clean_cache: bool = False
    narrow: bool = False
    use_hinted: bool = False
    scale_factor: tuple[float, float] = (1.0, 1.0)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scale_factor"] = list(self.scale_factor)
        return data


@dataclass(slots=True)
class CustomCJKEntryConfig:
    enable: bool
    build_config: CJKBuildConfig

    def to_dict(self) -> dict[str, Any]:
        data = serialize_cjk_build_config(self.build_config)
        data["enable"] = self.enable
        return data


@dataclass(slots=True)
class CJKLocaleSelection:
    cn: bool = False
    jp: bool = False
    tc: bool = False
    kr: bool = False
    custom: list[CustomCJKEntryConfig] = field(default_factory=list)

    def builtin_enabled_locales(self) -> list[BuiltinCJKLocaleId]:
        return [locale for locale in BUILTIN_CJK_LOCALES if bool(getattr(self, locale))]

    def set_builtin_enabled(self, locale: BuiltinCJKLocaleId, enabled: bool) -> None:
        setattr(self, locale, enabled)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cn": self.cn,
            "jp": self.jp,
            "tc": self.tc,
            "kr": self.kr,
            "custom": [entry.to_dict() for entry in self.custom],
        }


@dataclass(slots=True)
class ResolvedCJKBuildEntry:
    entry_id: str
    locale_name: str
    build_config: CJKBuildConfig
    common_options: CJKCommonBuildOptions
    is_builtin: bool
    preset_id: BuiltinCJKLocaleId | None = None
    preset_spec: CJKPresetSpec | None = None

    @property
    def display_name(self) -> str:
        return self.locale_name

    @property
    def download_locale(self) -> BuiltinCJKLocaleId | None:
        return self.preset_id if self.is_builtin else None


@dataclass(slots=True)
class CJKBuildSelection:
    locales: CJKLocaleSelection = field(default_factory=CJKLocaleSelection)
    common_options: CJKCommonBuildOptions = field(default_factory=CJKCommonBuildOptions)
    entries: list[ResolvedCJKBuildEntry] = field(default_factory=list)

    def selected_entries(self) -> list[ResolvedCJKBuildEntry]:
        return list(self.entries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "locales": self.locales.to_dict(),
            **self.common_options.to_dict(),
        }


@dataclass(slots=True)
class BuildIdentityConfig:
    base_family_name: str = "Maple Mono"
    family_name: str = "Maple Mono"
    family_name_compact: str = "MapleMono"
    version_tag: str = "v7.9"
    version: str = "7.9"
    version_str: str = "Version 7.900"
    font_version: str | None = None
    beta: str | None = None


@dataclass(slots=True)
class BuildMetricsConfig:
    weight_mapping: dict[str, int] = field(default_factory=default_weight_mapping)
    codepoint_alias: dict[int, int] = field(default_factory=dict)
    vertical_metric: tuple[int, int] = (1020, -300)
    glyph_width: int = 600
    glyph_width_cn_narrow: int = 1000
    ttfautohint_param: dict[str, Any] = field(default_factory=dict)
    pool_size: int = 1 if not getenv("CODESPACE_NAME") else 4
    github_mirror: str = "github.com"


@dataclass(slots=True)
class ResolvedConfig:
    behavior: BuildBehaviorConfig = field(default_factory=BuildBehaviorConfig)
    feature: FeatureBuildConfig = field(default_factory=FeatureBuildConfig)
    nerd_font: NerdFontBuildConfig = field(default_factory=NerdFontBuildConfig)
    cjk: CJKBuildSelection = field(default_factory=CJKBuildSelection)
    identity: BuildIdentityConfig = field(default_factory=BuildIdentityConfig)
    metrics: BuildMetricsConfig = field(default_factory=BuildMetricsConfig)
    feature_freeze: dict[str, str] = field(default_factory=default_feature_freeze)

    @property
    def archive(self) -> bool:
        return self.behavior.archive

    @property
    def debug(self) -> bool:
        return self.behavior.debug

    @property
    def cache(self) -> bool:
        return self.behavior.cache

    @property
    def least_styles(self) -> bool:
        return self.behavior.least_styles

    @property
    def apply_fea_file(self) -> bool:
        return self.behavior.apply_fea_file

    @property
    def cjk_output_format(self) -> CJKOutputFormat:
        return self.behavior.cjk_output_format

    @property
    def formats(self) -> list[BuildFormatId]:
        return self.behavior.formats

    @property
    def use_cjk_both(self) -> bool:
        return self.behavior.use_cjk_both

    @property
    def family_name(self) -> str:
        return self.identity.family_name

    @property
    def family_name_compact(self) -> str:
        return self.identity.family_name_compact

    @property
    def version(self) -> str:
        return self.identity.version

    @property
    def version_str(self) -> str:
        return self.identity.version_str

    @property
    def font_version(self) -> str:
        if self.identity.font_version is None:
            raise ValueError("Font version has not been resolved")
        return self.identity.font_version

    @property
    def version_tag(self) -> str:
        return self.identity.version_tag

    @property
    def beta(self) -> str | None:
        return self.identity.beta

    @property
    def use_hinted(self) -> bool:
        return self.feature.hinted

    @property
    def enable_ligature(self) -> bool:
        return self.feature.liga

    @property
    def infinite_arrow(self) -> bool:
        return self.feature.infinite_arrow

    @property
    def remove_tag_liga(self) -> bool:
        return self.feature.remove_tag_liga

    @property
    def line_height(self) -> float:
        return self.feature.line_height

    @property
    def width(self) -> str:
        return self.feature.width

    @property
    def pool_size(self) -> int:
        return self.metrics.pool_size

    @property
    def weight_mapping(self) -> dict[str, int]:
        return self.metrics.weight_mapping

    @property
    def codepoint_alias(self) -> dict[int, int]:
        return self.metrics.codepoint_alias

    @property
    def vertical_metric(self) -> tuple[int, int]:
        return self.metrics.vertical_metric

    @property
    def glyph_width(self) -> int:
        return self.metrics.glyph_width

    @property
    def glyph_width_cn_narrow(self) -> int:
        return self.metrics.glyph_width_cn_narrow

    @property
    def ttfautohint_param(self) -> dict[str, Any]:
        return self.metrics.ttfautohint_param

    @property
    def github_mirror(self) -> str:
        return self.metrics.github_mirror

    @property
    def freeze_config_str(self) -> str:
        return format_freeze_config(
            normalize_feature_freeze(self.feature_freeze, self.enable_ligature)
        )

    def get_target_width(self) -> int:
        return WIDTH_MAP.get(self.width, WIDTH_MAP["default"])

    def get_width_name(self) -> Literal["NR", "SL"] | None:
        if self.width == "narrow":
            return "NR"
        if self.width == "slim":
            return "SL"
        return None

    def get_selected_cjk_entries(self) -> list[ResolvedCJKBuildEntry]:
        return self.cjk.selected_entries()

    def wants_format(self, build_format: str) -> bool:
        return build_format in self.formats

    def needs_hinted_ttf(self) -> bool:
        """Return whether this build exposes or consumes hinted base TTFs."""
        if self.wants_format("ttf"):
            return True
        if not self.use_hinted:
            return False
        if self.nerd_font.enable and (
            not self.nerd_font.variable or self.nerd_font.uses_font_patcher()
        ):
            return True
        if self.cjk_output_format != "static":
            return False
        return any(
            self.use_cjk_both
            or not (self.nerd_font.enable and entry.common_options.with_nerd_font)
            for entry in self.get_selected_cjk_entries()
        )

    def needs_nerd_font_static_base(self) -> bool:
        """Return whether NF processing needs a static Maple base font."""
        return self.nerd_font.enable and (
            not self.nerd_font.variable or self.nerd_font.uses_font_patcher()
        )

    def get_nf_suffix(self) -> Literal["Mono", "Propo", ""]:
        return self.get_nf_variant().suffix

    def get_nf_variant(self) -> NerdFontVariant:
        return NerdFontVariant.from_options(
            mono=self.nerd_font.mono,
            propo=self.nerd_font.propo,
            extra_args=self.nerd_font.extra_args,
        )

    def get_valid_glyph_width_list(
        self,
        is_cjk: bool = False,
        cjk_narrow: bool = False,
    ) -> list[int]:
        result = [0]
        width_name = self.get_width_name()
        if width_name:
            width = self.get_target_width()
            result.append(width)
            if is_cjk:
                result.append(width * 2)
            return result

        result.append(self.glyph_width)
        if is_cjk:
            result.append(
                self.glyph_width_cn_narrow if cjk_narrow else 2 * self.glyph_width
            )
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "behavior": asdict(self.behavior),
            "feature": {
                **asdict(self.feature),
                "feature_freeze": dict(self.feature_freeze),
                "freeze_config_str": self.freeze_config_str,
            },
            "nerd_font": self.nerd_font.to_dict(),
            "cjk": self.cjk.to_dict(),
            "identity": asdict(self.identity),
            "metrics": {
                **asdict(self.metrics),
                "vertical_metric": list(self.metrics.vertical_metric),
                "codepoint_alias": serialize_codepoint_alias(
                    self.metrics.codepoint_alias
                ),
            },
        }

    def to_build_record(self) -> dict[str, Any]:
        return {
            "version": self.version_tag,
            "font_version": self.font_version,
            "family_name": self.family_name,
            "line_height": self.line_height,
            "width": self.width,
            "use_hinted": self.use_hinted,
            "ligature": self.enable_ligature,
            "remove_tag_liga": self.remove_tag_liga,
            "infinite_arrow": self.infinite_arrow,
            "standard_zero": self.feature.standard_zero,
            "weight_mapping": dict(self.weight_mapping),
            "codepoint_alias": serialize_codepoint_alias(self.codepoint_alias),
            "feature_freeze": dict(self.feature_freeze),
            "formats": list(self.formats),
            "nerd_font": self.nerd_font.to_dict(include_enable=False),
            "cjk_format": self.cjk_output_format,
            "cjk": self.cjk.to_dict(),
        }


__all__ = [
    "BUILD_FORMATS",
    "BUILTIN_CJK_LOCALES",
    "WIDTH_MAP",
    "BuildBehaviorConfig",
    "BuildFormatId",
    "BuildIdentityConfig",
    "BuildMetricsConfig",
    "BuiltinCJKLocaleId",
    "CJKBuildSelection",
    "CJKCommonBuildOptions",
    "CJKLocaleSelection",
    "CustomCJKEntryConfig",
    "FeatureBuildConfig",
    "NerdFontBuildConfig",
    "ResolvedCJKBuildEntry",
    "ResolvedConfig",
    "default_feature_freeze",
    "default_weight_mapping",
    "format_freeze_config",
    "normalize_build_formats",
    "normalize_cjk_locale_list",
    "normalize_cjk_output_format",
    "normalize_feature_freeze",
    "parse_codepoint_alias",
    "parse_scale_factor",
    "serialize_codepoint_alias",
]
