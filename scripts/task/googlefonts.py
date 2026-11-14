from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.font_ops.fonttools import load_font, save_font_atomic
from scripts.font_ops.metadata import set_meta_table
from scripts.utils.logging import logger

if TYPE_CHECKING:
    import argparse


VARIABLE_OUTPUT_DIR = Path("fonts/variable")
GOOGLEFONTS_OUTPUT_DIRS = (
    VARIABLE_OUTPUT_DIR,
    Path("fonts/ttf"),
    Path("fonts/otf"),
    Path("fonts/webfonts"),
)
GOOGLEFONTS_FAMILY_NAME = "Maple Mono"
GOOGLEFONTS_FONT_SUFFIXES = frozenset({".ttf", ".otf", ".woff2"})
DESIGN_LANGUAGES = "Latn"
SUPPORTED_LANGUAGES = "Latn, Cyrl, Grek"
SOURCE_DIR = Path("sources")
BUILDER_CONFIG = Path("sources/config.yaml")
FONTBAKERY_ARGS = (
    "check-googlefonts",
    "--exclude-checkid",
    "family/win_ascent_and_descent",
    "--ghmarkdown",
    "fonts/report.md",
    "fonts/variable/*.ttf",
)
INTERPOLATABLE_LOGGER_NAME = "fontTools.varLib.interpolatable"


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser = subparsers.add_parser(
        "googlefonts",
        help="Regenerate designspaces and build Google Fonts assets",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild UFO + designspace from Glyphs source files before building variable fonts",
    )
    parser.add_argument(
        "--qa",
        action="store_true",
        help="Clean variable outputs, build, and run FontBakery QA",
    )
    return parser


def regenerate_designspace() -> None:
    """Regenerate the gftools input designspaces from the exported Glyphs files."""
    from scripts.task.designspace import generate_designspaces

    generate_designspaces(SOURCE_DIR, SOURCE_DIR)


def run_gftools_builder() -> None:
    """Run gftools' builder entrypoint without spawning a second uv process."""
    from gftools.builder import main as builder_main

    original_cwd = Path.cwd()
    exit_code = 0
    try:
        try:
            exit_code = builder_main([str(BUILDER_CONFIG)])
        except SystemExit as error:
            exit_code = error.code
    finally:
        os.chdir(original_cwd)

    if exit_code not in (None, 0):
        raise SystemExit(exit_code)


def apply_googlefonts_meta(
    output_dirs: tuple[Path, ...] = GOOGLEFONTS_OUTPUT_DIRS,
    family_name: str = GOOGLEFONTS_FAMILY_NAME,
) -> list[Path]:
    """Apply META ScriptLangTags to Google Fonts artifacts in place."""
    updated_paths: list[Path] = []
    for output_dir in output_dirs:
        if not output_dir.is_dir():
            continue
        for font_path in sorted(output_dir.iterdir()):
            if (
                not font_path.is_file()
                or font_path.suffix not in GOOGLEFONTS_FONT_SUFFIXES
            ):
                continue
            font = load_font(font_path)
            try:
                font_family_name = font["name"].getDebugName(1)
                if not _is_googlefonts_family(font_family_name, family_name):
                    continue
                set_meta_table(font, DESIGN_LANGUAGES, SUPPORTED_LANGUAGES)
                save_font_atomic(font, font_path)
                updated_paths.append(font_path)
            finally:
                font.close()
    logger.info("Applied Google Fonts META table to %s fonts", len(updated_paths))
    return updated_paths


def _is_googlefonts_family(font_family_name: str | None, family_name: str) -> bool:
    if font_family_name == family_name:
        return True
    return (
        font_family_name is not None
        and font_family_name.startswith(f"{family_name} ")
        and font_family_name != f"{family_name} Debug"
    )


def run_fontbakery() -> None:
    """Run FontBakery with argv equivalent to the documented command."""
    from fontbakery.cli import main as fontbakery_main

    interpolatable_logger = logging.getLogger(INTERPOLATABLE_LOGGER_NAME)
    previous_log_level = interpolatable_logger.level
    interpolatable_logger.setLevel(logging.WARNING)
    original_argv = sys.argv
    try:
        sys.argv = ["fontbakery", *FONTBAKERY_ARGS]
        result = fontbakery_main()
    finally:
        sys.argv = original_argv
        interpolatable_logger.setLevel(previous_log_level)

    if result:
        raise SystemExit(result)


def run(args: argparse.Namespace) -> None:
    if args.rebuild:
        regenerate_designspace()

    if args.qa and VARIABLE_OUTPUT_DIR.exists():
        logger.info("Clean Google Fonts variable output: path=%s", VARIABLE_OUTPUT_DIR)
        shutil.rmtree(VARIABLE_OUTPUT_DIR)

    run_gftools_builder()
    apply_googlefonts_meta()

    if args.qa:
        run_fontbakery()
