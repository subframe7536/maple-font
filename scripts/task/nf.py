from __future__ import annotations

import json
from os import path, remove
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.external.process import get_font_forge_bin
from scripts.external.process import run as run_command
from scripts.font_ops.fonttools import load_font
from scripts.font_ops.metadata import set_monospace_metadata
from scripts.font_ops.names import (
    del_font_name,
    set_font_name,
)
from scripts.font_ops.nerd_font import NerdFontVariant, parse_codes_from_json
from scripts.font_ops.subset import subset_to_codepoints
from scripts.utils.downloads import (
    check_font_patcher,
    download_json,
    github_mirror_from_config,
)
from scripts.utils.logging import logger

if TYPE_CHECKING:
    import argparse

BASE_FONT_PATH = "fonts/TTF/MapleMono-Regular.ttf"
FAMILY_NAME = "Maple Mono"
FONT_FORGE_BIN = get_font_forge_bin()


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser = subparsers.add_parser("nf", help="Build Nerd-Font base font")
    parser.add_argument(
        "--no-update",
        action="store_true",
        help="Do not check version and update if available",
    )
    return parser


def update_config_json(config_path: str, version: str) -> None:
    config_file = Path(config_path)
    with config_file.open(encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid config JSON: expected an object in {config_file}")
    nerd_font = data.get("nerd_font")
    if not isinstance(nerd_font, dict):
        raise ValueError(
            f"Invalid config JSON: missing nerd_font object in {config_file}"
        )
    if not isinstance(nerd_font.get("version"), str):
        raise ValueError(
            f"Invalid config JSON: missing nerd_font.version in {config_file}"
        )

    nerd_font["version"] = version
    with config_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def check_update(config_path: str = "config.json") -> None:
    github_mirror = github_mirror_from_config()
    with open(config_path, encoding="utf-8") as file:
        data = json.load(file)
    current_version = data["nerd_font"]["version"]

    latest_version = current_version
    logger.info("Fetch latest Nerd Font version")
    data = download_json(
        "https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest",
        github_mirror,
    )
    for key in data:
        if key == "tag_name":
            latest_version = str(data[key])[1:]
            break

    if latest_version == current_version:
        logger.info("Nerd Font version is current: version=%s", current_version)
        if not check_font_patcher(latest_version, github_mirror):
            logger.error("FontPatcher is unavailable after download attempt")
            exit(1)
        return

    logger.info(
        "Update Nerd Font version: current=%s, latest=%s",
        current_version,
        latest_version,
    )
    if not check_font_patcher(latest_version, github_mirror):
        logger.error("Failed to update FontPatcher")
        exit(1)
    update_config_json(config_path, latest_version)


def get_nerd_font_patcher_args(mono: bool, propo: bool = False):
    if FONT_FORGE_BIN is None:
        raise RuntimeError("FontForge is required to build Nerd Font assets")
    nf_args = [
        FONT_FORGE_BIN,
        "FontPatcher/font-patcher",
        "-l",
        "-c",
        "--careful",
    ]
    if mono:
        nf_args += ["--mono"]
    elif propo:
        nf_args += ["--variable-width-glyphs"]
    return nf_args


def build_nf(mono: bool, propo: bool = False):
    variant = NerdFontVariant.from_options(mono, propo, reject_conflict=True)
    suffix = variant.suffix
    nf_args = get_nerd_font_patcher_args(mono, propo)

    style_name = "Regular"

    run_command([*nf_args, BASE_FONT_PATH])
    output_path = variant.patched_font_path(
        ".", f"{FAMILY_NAME.replace(' ', '')}-{style_name}.ttf"
    )
    nf_font = load_font(output_path)
    remove(output_path)

    full_family_name = f"{FAMILY_NAME} NF Base{f' {suffix}' if suffix else ''}"
    set_font_name(nf_font, full_family_name, 1)
    set_font_name(nf_font, style_name, 2)
    set_font_name(nf_font, f"{full_family_name} {style_name}", 4)
    set_font_name(
        nf_font,
        f"{FAMILY_NAME.replace(' ', '-')}-NF-Base{f'-{suffix}' if suffix else ''}-{style_name}",
        6,
    )
    del_font_name(nf_font, 16)
    del_font_name(nf_font, 17)

    return nf_font


def subset(mono: bool, propo: bool, unicodes: list[int]):
    font = build_nf(mono, propo)
    subset_to_codepoints(font, unicodes)

    variant = NerdFontVariant.from_options(mono, propo, reject_conflict=True)
    output_path = str(variant.base_path("source"))

    if not propo:
        set_monospace_metadata(font)
    font.save(output_path)
    font.close()


def nerd_font(no_update: bool):
    if not path.exists(BASE_FONT_PATH):
        logger.error(
            "Base font is missing; run: python build.py --format ttf --no-nerd-font --least-styles"
        )
        exit(1)

    if not no_update:
        check_update()

    unicodes = parse_codes_from_json()
    subset(mono=False, propo=False, unicodes=unicodes)
    subset(mono=True, propo=False, unicodes=unicodes)
    subset(mono=False, propo=True, unicodes=unicodes)


def run(args: argparse.Namespace) -> None:
    nerd_font(args.no_update)
