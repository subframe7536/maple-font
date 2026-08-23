from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from scripts.cjk.config import CJKBuildConfig, CJKSourceConfig, _validate_transform
from scripts.cjk.masters import build_master_locations, parse_axis_assignments
from scripts.cjk.paths import (
    naming_config_from_locale,
    output_config_from_locale,
    resolve_cli_path,
    temp_dir_from_locale,
    validate_locale_name,
)

if TYPE_CHECKING:
    import argparse


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
