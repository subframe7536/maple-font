from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scripts.config.base import (
    BuiltinCJKLocaleId,
    CJKBuildSelection,
    ResolvedConfig,
    parse_scale_factor,
)
from scripts.utils.logging import logger

if TYPE_CHECKING:
    import argparse


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be a boolean")
    return value


def apply_legacy_cn_config(
    selection: CJKBuildSelection,
    legacy_cn: dict[str, Any] | None,
) -> None:
    """Apply the supported top-level ``cn`` configuration compatibility input."""
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


def apply_deprecated_cli_overrides(
    config: ResolvedConfig,
    args: argparse.Namespace,
    enabled_locales: set[BuiltinCJKLocaleId],
) -> None:
    """Apply public deprecated CLI aliases after their modern equivalents."""
    if args.cn_both:
        logger.warning("--cn-both is deprecated; use --cjk-both instead")
        config.behavior.use_cjk_both = True

    if args.ttf_only:
        logger.warning("--ttf-only is deprecated; use --format ttf instead")
        config.behavior.formats = ["ttf"]

    if args.cn is not None:
        logger.warning("--cn is deprecated; use --cjk cn instead")
        if args.cn:
            enabled_locales.add("cn")
        else:
            enabled_locales.discard("cn")

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
