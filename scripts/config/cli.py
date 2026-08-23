"""Argument parsing helpers for the Maple build pipeline."""

from __future__ import annotations

import argparse

from scripts.config.base import (
    WIDTH_MAP,
    normalize_build_formats,
    parse_scale_factor,
)
from scripts.utils.version import project_version


def _add_general_arguments(
    parser: argparse.ArgumentParser, version: str | None
) -> None:
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"Maple Mono Builder {version or f'v{project_version()}'}",
    )
    parser.add_argument(
        "-d",
        "--dry",
        dest="dry",
        action="store_true",
        help="Output config and exit",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Use a fast debug build: add `Debug`, enable debug logging, build Regular/Italic only, and skip OTF/WOFF2/Nerd Font outputs",
    )


def _add_feature_arguments(parser: argparse.ArgumentParser) -> None:
    feature_group = parser.add_argument_group("Feature Options")
    feature_group.add_argument(
        "-n",
        "--normal",
        dest="normal",
        action="store_true",
        help="Use normal preset, just like `JetBrains Mono` with slashed zero",
    )
    feature_group.add_argument(
        "--standard-zero",
        action="store_true",
        help="Use standard zero semantics: default dotted zero and slashed zero when `zero` is enabled",
    )
    feature_group.add_argument(
        "--feat",
        type=lambda x: x.strip().split(","),
        help="Enable and freeze the listed features, split by `,` (e.g. `--feat zero,cv01,ss07,ss08`); contextual rules are enabled through `calt`",
    )
    feature_group.add_argument(
        "--apply-fea-file",
        default=None,
        action="store_true",
        help="Apply matching `sources/features/{regular,italic}{_cn,}.fea` to static and variable fonts",
    )
    hint_group = feature_group.add_mutually_exclusive_group()
    hint_group.add_argument(
        "--hinted",
        dest="hinted",
        default=None,
        action="store_true",
        help="Use hinted font as base font in NF / CJK / NF-CJK (default)",
    )
    hint_group.add_argument(
        "--no-hinted",
        dest="hinted",
        default=None,
        action="store_false",
        help="Use unhinted font as base font in NF / CJK / NF-CJK",
    )
    liga_group = feature_group.add_mutually_exclusive_group()
    liga_group.add_argument(
        "--liga",
        dest="liga",
        default=None,
        action="store_true",
        help="Preserve all the ligatures (default)",
    )
    liga_group.add_argument(
        "--no-liga",
        dest="liga",
        default=None,
        action="store_false",
        help="Remove all the ligatures",
    )
    infinite_arrow_group = feature_group.add_mutually_exclusive_group()
    infinite_arrow_group.add_argument(
        "--infinite-arrow",
        default=None,
        action="store_true",
        dest="infinite_arrow",
        help="Add infinite arrow ligature support (default)",
    )
    infinite_arrow_group.add_argument(
        "--no-infinite-arrow",
        default=None,
        action="store_false",
        dest="infinite_arrow",
        help="Do not add infinite arrow ligature support",
    )
    feature_group.add_argument(
        "--remove-tag-liga",
        default=None,
        action="store_true",
        help="Remove plain text tag ligatures like `[TODO]`",
    )
    feature_group.add_argument(
        "--line-height",
        type=float,
        help="Scale factor for line height (e.g., 1.1)",
    )
    feature_group.add_argument(
        "--width",
        type=str,
        choices=WIDTH_MAP.keys(),
        default=None,
        help="Set glyph width: default (600), narrow (550), slim (500)",
    )


def _add_build_arguments(parser: argparse.ArgumentParser) -> None:
    build_group = parser.add_argument_group("Build Options")
    build_group.add_argument(
        "--format",
        dest="formats",
        type=normalize_build_formats,
        help="Select requested base output formats as a comma-separated list: ttf,otf,woff2; the variable base is always built",
    )
    build_group.add_argument(
        "--ttf-only",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    build_group.add_argument(
        "--least-styles",
        action="store_true",
        help="Only build Regular / Bold / Italic / BoldItalic style",
    )
    build_group.add_argument(
        "--cache",
        action="store_true",
        help="Reuse valid cached pipeline stages under `fonts/` and preserve existing unrelated outputs",
    )
    build_group.add_argument(
        "--archive",
        action="store_true",
        help="Archive each existing non-JSON output directory with config and license",
    )


def _add_nerd_font_arguments(parser: argparse.ArgumentParser) -> None:
    nerd_font_group = parser.add_argument_group("Nerd Font Options")
    nerd_font_enable_group = nerd_font_group.add_mutually_exclusive_group()
    nerd_font_enable_group.add_argument(
        "--nf",
        "--nerd-font",
        dest="nerd_font",
        default=None,
        action="store_true",
        help="Build Nerd-Font version (default)",
    )
    nerd_font_enable_group.add_argument(
        "--no-nf",
        "--no-nerd-font",
        dest="nerd_font",
        default=None,
        action="store_false",
        help="Do not build the Nerd-Font version",
    )
    nerd_font_group.add_argument(
        "--nf-mono",
        action="store_true",
        help="Make Nerd Font icons' width fixed",
    )
    nerd_font_group.add_argument(
        "--nf-propo",
        action="store_true",
        help="Make Nerd Font icons' width variable, override `--nf-mono`",
    )
    nerd_font_group.add_argument(
        "--nf-variable",
        action="store_true",
        help="Build Nerd Font as a variable font",
    )
    nerd_font_group.add_argument(
        "--font-patcher",
        action="store_true",
        help="Force the use of Nerd Font Patcher to build NF format",
    )


def _add_cjk_arguments(parser: argparse.ArgumentParser) -> None:
    cjk_group = parser.add_argument_group("CJK Options")
    cjk_group.add_argument(
        "--cjk",
        action="append",
        help="Build Maple Mono + CJK extended fonts for locales: cn, jp, tc, kr. Repeat or use comma-separated values.",
    )
    cjk_group.add_argument(
        "--cjk-variable",
        action="store_true",
        default=None,
        help="Persist CJK-extended output as merged variable fonts.",
    )
    cjk_group.add_argument(
        "--cjk-narrow",
        action="store_true",
        help="Apply narrow CJK spacing to the selected locales.",
    )
    cjk_group.add_argument(
        "--cjk-scale-factor",
        type=parse_scale_factor,
        help="Scale factor for selected CJK locales. Format: <factor> or <width_factor>,<height_factor>.",
    )
    cjk_group.add_argument(
        "--cjk-both",
        action="store_true",
        help="When Nerd Font is enabled, build both NF CJK and non-NF CJK outputs.",
    )
    cjk_hint_group = cjk_group.add_mutually_exclusive_group()
    cjk_hint_group.add_argument(
        "--cjk-hinted",
        dest="cjk_hinted",
        default=None,
        action="store_true",
        help="Auto-hint final static CJK fonts.",
    )
    cjk_hint_group.add_argument(
        "--no-cjk-hinted",
        dest="cjk_hinted",
        default=None,
        action="store_false",
        help="Do not auto-hint final static CJK fonts (default).",
    )


def _add_deprecated_cn_arguments(parser: argparse.ArgumentParser) -> None:
    deprecated_cn_group = parser.add_argument_group("Deprecated CN Options")
    cn_group = deprecated_cn_group.add_mutually_exclusive_group()
    cn_group.add_argument(
        "--cn",
        dest="cn",
        default=None,
        action="store_true",
        help="Deprecated alias for `--cjk cn`.",
    )
    cn_group.add_argument(
        "--no-cn",
        dest="cn",
        default=None,
        action="store_false",
        help="Deprecated alias for removing `cn` from the selected CJK locales.",
    )
    deprecated_cn_group.add_argument(
        "--cn-narrow",
        action="store_true",
        help="Deprecated alias for `--cjk-narrow` when targeting `cn`.",
    )
    deprecated_cn_group.add_argument(
        "--cn-scale-factor",
        type=parse_scale_factor,
        help="Deprecated alias for `--cjk-scale-factor` when targeting `cn`.",
    )
    deprecated_cn_group.add_argument(
        "--cn-both",
        action="store_true",
        help="Deprecated alias for `--cjk-both`.",
    )
    deprecated_cn_group.add_argument(
        "--cn-rebuild",
        action="store_true",
        help=argparse.SUPPRESS,
    )


def build_parser(version: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Builder and optimizer for Maple Mono",
    )
    _add_general_arguments(parser, version)
    _add_feature_arguments(parser)
    _add_build_arguments(parser)
    _add_nerd_font_arguments(parser)
    _add_cjk_arguments(parser)
    _add_deprecated_cn_arguments(parser)
    return parser


def parse_args(
    args: list[str] | None = None, version: str | None = None
) -> argparse.Namespace:
    return build_parser(version=version).parse_args(args)


__all__ = ["build_parser", "parse_args"]
