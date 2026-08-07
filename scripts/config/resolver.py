from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from scripts.cjk.presets import build_preset_config, get_preset
from scripts.cjk.resolver import config_from_data
from scripts.config.base import (
    BUILTIN_CJK_LOCALES,
    WIDTH_MAP,
    BuildBehaviorConfig,
    BuildIdentityConfig,
    BuildMetricsConfig,
    CJKBuildSelection,
    CJKCommonBuildOptions,
    CJKLocaleSelection,
    CustomCJKEntryConfig,
    FeatureBuildConfig,
    NerdFontBuildConfig,
    ResolvedCJKBuildEntry,
    ResolvedConfig,
    default_feature_freeze,
    default_weight_mapping,
    normalize_build_formats,
    normalize_cjk_locale_list,
    normalize_cjk_output_format,
    parse_codepoint_alias,
    parse_scale_factor,
)
from scripts.config.runtime import BuildRuntimeContext
from scripts.feature.compiler import normal_enabled_features
from scripts.font_ops.opentype import DEFAULT_COMPAT_ALIASES
from scripts.utils.logging import logger
from scripts.utils.version import font_version_for_core, parse_font_version


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be a boolean")
    return value


def _require_string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be an array of strings")
    return list(value)


class BuildConfigResolver:
    def __init__(self, project_root: str | Path = ".", version_tag: str = "v7.9"):
        self.project_root = Path(project_root)
        self.version_tag = version_tag

    def load_defaults(self) -> ResolvedConfig:
        config = ResolvedConfig(
            behavior=BuildBehaviorConfig(),
            feature=FeatureBuildConfig(),
            nerd_font=NerdFontBuildConfig(),
            cjk=CJKBuildSelection(),
            identity=BuildIdentityConfig(),
            metrics=BuildMetricsConfig(
                weight_mapping=default_weight_mapping(),
            ),
            feature_freeze=default_feature_freeze(),
        )
        self._apply_identity(config)
        return config

    def resolve(self, args) -> ResolvedConfig:
        config = self.resolve_project_config()
        self._apply_cli_overrides(config, args)
        self._apply_identity(config)
        return config

    def resolve_project_config(self) -> ResolvedConfig:
        """Resolve project defaults and JSON configuration without CLI overrides."""
        config = self.load_defaults()
        self._apply_json_config(config)
        self._apply_identity(config)
        return config

    def _config_path(self) -> Path:
        return self.project_root / "config.json"

    def _apply_json_config(self, config: ResolvedConfig) -> None:
        data = self._read_json_config()
        if data is None:
            return

        self._apply_identity_json_config(config, data)
        self._apply_metrics_json_config(config, data)
        self._apply_feature_json_config(config, data)
        self._apply_behavior_json_config(config, data)
        self._apply_nerd_font_json_config(config, data)
        config.cjk = self._resolve_cjk_selection(data.get("cjk"), data.get("cn"))

    def _read_json_config(self) -> dict[str, Any] | None:
        config_path = self._config_path()
        if not config_path.exists():
            logger.warning(
                "Config file not found; using defaults: path=%s", config_path
            )
            return None
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON in config file: {config_path}") from error
        if not isinstance(data, dict):
            raise ValueError(f"Config file must contain a JSON object: {config_path}")
        return data

    def _apply_identity_json_config(
        self,
        config: ResolvedConfig,
        data: dict[str, Any],
    ) -> None:
        if "family_name" in data:
            config.identity.base_family_name = str(data["family_name"])
        if "font_version" in data:
            font_version = data["font_version"]
            if not isinstance(font_version, str):
                raise ValueError("font_version must be a string")
            try:
                parse_font_version(font_version)
            except ValueError as error:
                raise ValueError(f"Invalid font_version: {font_version}") from error
            config.identity.font_version = font_version

    def _apply_metrics_json_config(
        self,
        config: ResolvedConfig,
        data: dict[str, Any],
    ) -> None:
        if "pool_size" in data:
            config.metrics.pool_size = int(data["pool_size"])
        if "ttfautohint_param" in data:
            config.metrics.ttfautohint_param = dict(data["ttfautohint_param"])
        if "github_mirror" in data:
            config.metrics.github_mirror = str(data["github_mirror"])
        if "weight_mapping" in data:
            config.metrics.weight_mapping = {
                **config.metrics.weight_mapping,
                **dict(data["weight_mapping"]),
            }
        if "codepoint_alias" in data:
            codepoint_alias = parse_codepoint_alias(data["codepoint_alias"])
            builtin_aliases = sorted(
                set(codepoint_alias).intersection(DEFAULT_COMPAT_ALIASES)
            )
            if builtin_aliases:
                aliases = ", ".join(f"0x{value:04X}" for value in builtin_aliases)
                raise ValueError(
                    f"Codepoint aliases are built in and cannot be changed: {aliases}"
                )
            config.metrics.codepoint_alias = codepoint_alias

    def _apply_feature_json_config(
        self,
        config: ResolvedConfig,
        data: dict[str, Any],
    ) -> None:
        if "use_hinted" in data:
            config.feature.hinted = _require_bool(data["use_hinted"], "use_hinted")
        if "ligature" in data:
            config.feature.liga = _require_bool(data["ligature"], "ligature")
        if "infinite_arrow" in data:
            infinite_arrow = data["infinite_arrow"]
            config.feature.infinite_arrow = (
                None
                if infinite_arrow is None
                else _require_bool(infinite_arrow, "infinite_arrow")
            )
        if "line_height" in data:
            config.feature.line_height = float(data["line_height"])
        if "width" in data:
            width = str(data["width"])
            if width not in WIDTH_MAP:
                choices = ", ".join(WIDTH_MAP)
                raise ValueError(f"width must be one of: {choices}")
            config.feature.width = width
        if "remove_tag_liga" in data:
            config.feature.remove_tag_liga = _require_bool(
                data["remove_tag_liga"], "remove_tag_liga"
            )
        if "feature_freeze" in data:
            raw_feature_freeze = data["feature_freeze"]
            if not isinstance(raw_feature_freeze, dict):
                raise ValueError("feature_freeze must be an object")
            for feature, value in raw_feature_freeze.items():
                if value not in ("ignore", "disable", "enable"):
                    raise ValueError(
                        f"feature_freeze.{feature} must be one of: "
                        "ignore, disable, enable"
                    )
            config.feature_freeze.update(raw_feature_freeze)

    def _apply_behavior_json_config(
        self,
        config: ResolvedConfig,
        data: dict[str, Any],
    ) -> None:
        if "formats" in data:
            config.behavior.formats = normalize_build_formats(data["formats"])
        raw_cjk = data.get("cjk")
        if isinstance(raw_cjk, dict) and "variable" in raw_cjk:
            cjk_variable = _require_bool(raw_cjk["variable"], "cjk.variable")
            config.behavior.cjk_output_format = normalize_cjk_output_format(
                "variable" if cjk_variable else "static"
            )

    def _apply_nerd_font_json_config(
        self,
        config: ResolvedConfig,
        data: dict[str, Any],
    ) -> None:
        if "nerd_font" in data:
            nerd_font = dict(data["nerd_font"])
            if "enable" in nerd_font:
                config.nerd_font.enable = _require_bool(
                    nerd_font["enable"], "nerd_font.enable"
                )
            if "version" in nerd_font:
                config.nerd_font.version = str(nerd_font["version"])
            if "mono" in nerd_font:
                config.nerd_font.mono = _require_bool(
                    nerd_font["mono"], "nerd_font.mono"
                )
            if "propo" in nerd_font:
                config.nerd_font.propo = _require_bool(
                    nerd_font["propo"], "nerd_font.propo"
                )
            if "variable" in nerd_font:
                config.nerd_font.variable = _require_bool(
                    nerd_font["variable"], "nerd_font.variable"
                )
            if "use_font_patcher" in nerd_font:
                config.nerd_font.use_font_patcher = _require_bool(
                    nerd_font["use_font_patcher"], "nerd_font.use_font_patcher"
                )
            if "glyphs" in nerd_font:
                config.nerd_font.glyphs = _require_string_list(
                    nerd_font["glyphs"], "nerd_font.glyphs"
                )
            if "extra_args" in nerd_font:
                config.nerd_font.extra_args = _require_string_list(
                    nerd_font["extra_args"], "nerd_font.extra_args"
                )

    def _resolve_cjk_selection(
        self,
        raw_cjk: dict[str, Any] | None,
        legacy_cn: dict[str, Any] | None,
    ) -> CJKBuildSelection:
        selection = CJKBuildSelection(
            locales=self._resolve_cjk_locales(raw_cjk),
            common_options=self._resolve_cjk_common_options(raw_cjk),
        )
        self._apply_legacy_cn_config(selection, legacy_cn)
        selection.entries = self._build_cjk_entries(
            selection.locales,
            selection.common_options,
        )
        return selection

    def _resolve_cjk_locales(
        self,
        raw_cjk: dict[str, Any] | None,
    ) -> CJKLocaleSelection:
        selection = CJKLocaleSelection()
        if not isinstance(raw_cjk, dict):
            return selection

        raw_locales = raw_cjk.get("locales")
        if not isinstance(raw_locales, dict):
            return selection

        for locale in BUILTIN_CJK_LOCALES:
            enabled = False
            if locale in raw_locales:
                enabled = _require_bool(raw_locales[locale], f"cjk.locales.{locale}")
            selection.set_builtin_enabled(locale, enabled)

        raw_custom = raw_locales.get("custom", [])
        if not isinstance(raw_custom, list):
            raise ValueError(
                f"cjk.locales.custom must be a list, got {type(raw_custom).__name__}"
            )
        for index, raw_entry in enumerate(raw_custom):
            if not isinstance(raw_entry, dict):
                raise ValueError(
                    f"cjk.locales.custom[{index}] must be an object, "
                    f"got {type(raw_entry).__name__}"
                )
            entry_data = dict(raw_entry)
            raw_enable = entry_data.pop("enable", True)
            enable = _require_bool(raw_enable, f"cjk.locales.custom[{index}].enable")
            selection.custom.append(
                CustomCJKEntryConfig(
                    enable=enable,
                    build_config=config_from_data(entry_data, self.project_root),
                )
            )

        return selection

    def _resolve_cjk_common_options(
        self,
        raw_cjk: dict[str, Any] | None,
    ) -> CJKCommonBuildOptions:
        options = CJKCommonBuildOptions()
        if not isinstance(raw_cjk, dict):
            return options

        for key in (
            "with_nerd_font",
            "fix_meta_table",
            "clean_cache",
            "narrow",
            "use_hinted",
        ):
            if key in raw_cjk:
                setattr(options, key, _require_bool(raw_cjk[key], f"cjk.{key}"))
        if "scale_factor" in raw_cjk:
            options.scale_factor = parse_scale_factor(raw_cjk["scale_factor"])
        return options

    def _apply_legacy_cn_config(
        self,
        selection: CJKBuildSelection,
        legacy_cn: dict[str, Any] | None,
    ) -> None:
        if not isinstance(legacy_cn, dict):
            return

        if "enable" in legacy_cn and _require_bool(legacy_cn["enable"], "cn.enable"):
            selection.locales.cn = True
        for key in (
            "with_nerd_font",
            "fix_meta_table",
            "clean_cache",
            "narrow",
            "use_hinted",
        ):
            if key in legacy_cn:
                setattr(
                    selection.common_options,
                    key,
                    _require_bool(legacy_cn[key], f"cn.{key}"),
                )
        if "scale_factor" in legacy_cn:
            selection.common_options.scale_factor = parse_scale_factor(
                legacy_cn["scale_factor"]
            )

    def _build_cjk_entries(
        self,
        locale_selection: CJKLocaleSelection,
        common_options: CJKCommonBuildOptions,
    ) -> list[ResolvedCJKBuildEntry]:
        entries: list[ResolvedCJKBuildEntry] = []
        used_entry_ids: set[str] = set()
        used_locale_names: set[str] = set()

        for preset_id in locale_selection.builtin_enabled_locales():
            preset_spec = get_preset(preset_id)
            preset_config = build_preset_config(preset_id)
            entries.append(
                ResolvedCJKBuildEntry(
                    entry_id=preset_id,
                    locale_name=preset_config.locale_name,
                    build_config=preset_config,
                    common_options=replace(common_options),
                    is_builtin=True,
                    preset_id=preset_id,
                    preset_spec=preset_spec,
                )
            )

        for custom_entry in locale_selection.custom:
            if not custom_entry.enable:
                continue
            locale_name = custom_entry.build_config.locale_name
            entries.append(
                ResolvedCJKBuildEntry(
                    entry_id=f"custom:{locale_name.lower()}",
                    locale_name=locale_name,
                    build_config=custom_entry.build_config,
                    common_options=replace(common_options),
                    is_builtin=False,
                )
            )

        for entry in entries:
            locale_key = entry.locale_name.lower()
            if entry.entry_id in used_entry_ids:
                raise ValueError(f"Duplicate CJK build entry id: {entry.entry_id}")
            if locale_key in used_locale_names:
                raise ValueError(
                    f"Duplicate CJK locale_name detected in build entries: {entry.locale_name}"
                )
            used_entry_ids.add(entry.entry_id)
            used_locale_names.add(locale_key)

        return entries

    def _apply_cli_overrides(self, config: ResolvedConfig, args) -> None:
        # ========== Build behavior overrides ============
        config.behavior.archive = bool(args.archive)
        config.behavior.debug = bool(args.debug)
        config.behavior.cache = bool(args.cache)
        config.behavior.least_styles = bool(args.least_styles)
        config.behavior.apply_fea_file = bool(args.apply_fea_file)
        if args.cjk_variable:
            config.behavior.cjk_output_format = "variable"
        config.behavior.use_cjk_both = bool(args.cjk_both or args.cn_both)

        if args.cn_both:
            logger.warning("--cn-both is deprecated; use --cjk-both instead")

        if args.formats is not None:
            config.behavior.formats = list(args.formats)

        if args.ttf_only:
            logger.warning("--ttf-only is deprecated; use --format ttf instead")
            config.behavior.formats = ["ttf"]

        # ============== Feature overrides ============
        if args.normal:
            config.feature.normal = True
            for feature in normal_enabled_features:
                config.feature_freeze[feature] = "enable"

        if args.feat:
            config.feature.feat = list(args.feat)
            for feature in args.feat:
                if feature in config.feature_freeze:
                    config.feature_freeze[feature] = "enable"

        if args.hinted is not None:
            config.feature.hinted = bool(args.hinted)
        if args.liga is not None:
            config.feature.liga = bool(args.liga)
        if args.infinite_arrow:
            config.feature.infinite_arrow = True
        if args.remove_tag_liga:
            config.feature.remove_tag_liga = True
        if args.width is not None:
            config.feature.width = args.width
        if args.line_height is not None:
            config.feature.line_height = float(args.line_height)

        # ============== Nerd Font overrides ============
        if config.debug:
            config.nerd_font.enable = False
        if args.nf_mono:
            config.nerd_font.mono = True
            config.nerd_font.enable = True
        if args.nf_propo:
            config.nerd_font.propo = True
            config.nerd_font.enable = True
        if args.nf_variable:
            config.nerd_font.variable = True
            config.nerd_font.enable = True
        if args.nerd_font is not None:
            config.nerd_font.enable = bool(args.nerd_font)
        if args.font_patcher:
            config.nerd_font.use_font_patcher = True

        # ============== CJK overrides ============
        enabled_locales = set(config.cjk.locales.builtin_enabled_locales())
        enabled_locales.update(normalize_cjk_locale_list(getattr(args, "cjk", None)))

        if args.cn is not None:
            logger.warning("--cn is deprecated; use --cjk cn instead")
            if args.cn:
                enabled_locales.add("cn")
            else:
                enabled_locales.discard("cn")

        if args.cjk_narrow:
            config.cjk.common_options.narrow = True
        if args.cjk_scale_factor is not None:
            config.cjk.common_options.scale_factor = args.cjk_scale_factor
        if args.cjk_hinted is not None:
            config.cjk.common_options.use_hinted = bool(args.cjk_hinted)

        if args.cn_narrow:
            logger.warning("--cn-narrow is deprecated; use --cjk-narrow instead")
            config.cjk.common_options.narrow = True
        if args.cn_scale_factor is not None:
            logger.warning(
                "--cn-scale-factor is deprecated; use --cjk-scale-factor instead"
            )
            config.cjk.common_options.scale_factor = args.cn_scale_factor
        if args.cn_rebuild:
            logger.warning(
                "--cn-rebuild is deprecated; use task.py cjk --preset cn instead"
            )
            enabled_locales.add("cn")

        for locale in BUILTIN_CJK_LOCALES:
            config.cjk.locales.set_builtin_enabled(locale, locale in enabled_locales)
        config.cjk.entries = self._build_cjk_entries(
            config.cjk.locales,
            config.cjk.common_options,
        )

        if (
            config.nerd_font.enable
            and config.nerd_font.variable
            and config.cjk.entries
            and config.cjk_output_format != "variable"
        ):
            raise ValueError(
                "nerd_font.variable requires cjk.variable=true when CJK is enabled"
            )

    def _apply_identity(self, config: ResolvedConfig) -> None:
        version_tag = self.version_tag
        base_name = config.identity.base_family_name
        name_parts = [word.capitalize() for word in base_name.split(" ")]
        if config.feature.normal:
            name_parts.append("Normal")
        if not config.feature.liga:
            name_parts.append("NL")

        width_name = config.get_width_name()
        if width_name:
            name_parts.append(width_name)
        if config.debug:
            name_parts.append("Debug")

        version_core = version_tag.removeprefix("v").split("-", 1)[0]
        major, minor = version_core.split(".")
        if config.identity.font_version is None:
            config.identity.font_version = font_version_for_core(version_core)

        beta = None
        if "-" in version_tag:
            beta = version_tag.split("-", 1)[1]

        config.identity.family_name = " ".join(name_parts)
        config.identity.family_name_compact = "".join(name_parts)
        config.identity.version_tag = version_tag
        config.identity.version = f"{major}.{minor}"
        config.identity.version_str = f"Version {config.identity.font_version}"
        config.identity.beta = beta


def resolve_default_build_config() -> ResolvedConfig:
    """Resolve the project build configuration for standalone CJK builds."""
    from scripts.utils.version import version_tag

    return BuildConfigResolver(version_tag=version_tag()).resolve_project_config()


__all__ = [
    "BuildConfigResolver",
    "BuildRuntimeContext",
    "ResolvedConfig",
    "resolve_default_build_config",
]
