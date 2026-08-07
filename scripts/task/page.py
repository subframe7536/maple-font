from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

from python_minifier import minify

from scripts.external.process import run as run_command
from scripts.feature.compiler import (
    get_cv_cn_version_info,
    get_cv_italic_version_info,
    get_cv_version_info,
    get_ss_version_info,
    get_total_feat_ts,
)
from scripts.font_ops.conversion import convert_to_web
from scripts.utils.files import (
    join_path,
    read_json,
    read_text,
    write_json,
    write_text,
)
from scripts.utils.logging import logger

if TYPE_CHECKING:
    import argparse


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser = subparsers.add_parser("page", help="Update landing page data")
    parser.add_argument("--woff2", action="store_true", help="Generate new woff2 fonts")
    parser.add_argument(
        "--sync", action="store_true", help="Sync latest page data and commit"
    )
    return parser


def run_git_command(args: list[str], cwd=None, check=True):
    try:
        result = subprocess.run(
            args, cwd=cwd, check=check, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as error:
        logger.error(
            "Command failed: command=%s, cwd=%s, error=%s",
            " ".join(args),
            cwd or os.getcwd(),
            error.stderr.strip(),
        )
        sys.exit(1)


def update_page(
    submodule_path: str,
    var_dir: str,
    woff2: bool = False,
    sync: bool = False,
) -> None:
    abs_submodule_path = os.path.abspath(submodule_path)

    if not os.path.exists(abs_submodule_path):
        logger.error(
            "Landing-page submodule is missing: path=%s; run git submodule update --init",
            submodule_path,
        )
        sys.exit(1)

    if sync:
        run_git_command(["git", "submodule", "update", "--remote"])
        logger.info("Check out landing-page main branch")
        run_git_command(["git", "checkout", "main"], cwd=abs_submodule_path)
        run_git_command(["git", "pull"], cwd=abs_submodule_path)
        logger.info("Synced landing-page remote")

    logger.info("Update landing-page feature data")
    feature_data_base = join_path(submodule_path, "data", "features")
    os.makedirs(feature_data_base, exist_ok=True)
    write_json(join_path(feature_data_base, "cv.json"), get_cv_version_info())
    write_json(join_path(feature_data_base, "cn.json"), get_cv_cn_version_info())
    write_json(
        join_path(feature_data_base, "italic.json"), get_cv_italic_version_info()
    )
    write_json(join_path(feature_data_base, "ss.json"), get_ss_version_info())
    write_text(join_path(feature_data_base, "features.ts"), get_total_feat_ts())

    logger.info("Update landing-page configuration")
    data = read_json("config.json")
    del data["$schema"]
    write_json(join_path(submodule_path, "data", "config.json"), data)

    logger.info("Update landing-page browser script")
    script_content = read_text(join_path("scripts", "in_browser.py"))
    write_text(
        join_path(submodule_path, "data", "script.py"),
        "# Source: https://github.com/subframe7536/maple-font/blob/variable/scripts/in_browser.py\n"
        + minify(script_content),
    )

    if woff2:
        logger.info("Update landing-page WOFF2 fonts")
        font_dir = join_path(submodule_path, "public", "fonts")
        run_command(
            ["python", "build.py", "--ttf-only", "--no-nerd-font", "--least-styles"]
        )
        convert_to_web(var_dir, flavor="woff2")
        shutil.rmtree(font_dir, ignore_errors=True)
        os.makedirs(font_dir, exist_ok=True)
        for filename in os.listdir(var_dir):
            if filename.endswith(".woff2"):
                os.rename(
                    join_path(var_dir, filename),
                    join_path(font_dir, filename.replace(".ttf.woff2", "-VF.woff2")),
                )

    if sync:
        run_git_command(["git", "add", "."], cwd=abs_submodule_path)
        logger.info("Commit landing-page submodule")
        run_git_command(
            ["git", "commit", "-m", "Update landing page data"], cwd=abs_submodule_path
        )
        logger.info("Push landing-page submodule")
        run_git_command(["git", "push", "origin", "main"], cwd=abs_submodule_path)
        run_git_command(["git", "submodule", "update", "--remote"])
        run_git_command(["git", "add", "."])
        logger.info("Commit main repository")
        run_git_command(["git", "commit", "-m", "sync landing page"])
        logger.info("Push main repository")
        run_git_command(["git", "push", "origin"])


def run(args: argparse.Namespace) -> None:
    update_page("./maple-font-page", "./fonts/Variable", args.woff2, args.sync)
