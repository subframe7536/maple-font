from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from scripts.external.process import run as run_command
from scripts.font_ops.constant import INSTANCE_WEIGHT_MAPPING
from scripts.font_ops.conversion import convert_to_web
from scripts.pipeline import main as build_main
from scripts.utils.files import join_path
from scripts.utils.logging import logger
from scripts.utils.version import (
    font_version_for_core,
    parse_font_version,
    parse_project_version,
    project_version,
    version_tag,
)

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable

ReleaseBump = Literal["minor", "major", "pre-minor", "pre-major"]
ReleaseWidth = Literal["default", "narrow", "slim"]
RELEASE_BUMPS: tuple[ReleaseBump, ...] = (
    "minor",
    "major",
    "pre-minor",
    "pre-major",
)
RELEASE_VARIABLE_WIDTHS: tuple[ReleaseWidth, ...] = ("default", "narrow", "slim")


@dataclass(frozen=True)
class ReleasePlan:
    tag: str
    build_args: tuple[str, ...]
    fontsource_dir: str = "cdn/fontsource"
    requirements_file: str = "requirements.txt"
    variable_woff2_dir: str = "woff2/variable"
    project_version: str = ""
    font_version: str = ""

    def describe(self) -> str:
        return "\n".join(
            (
                f"Tag: {self.tag}",
                f"Project version: {self.project_version}",
                f"Font version: {self.font_version}",
                f"Build: build.py {' '.join(self.build_args)}",
                f"Fontsource output: {self.fontsource_dir}",
                f"Variable WOFF2 output: {self.variable_woff2_dir}",
                f"Requirements output: {self.requirements_file}",
            )
        )


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser = subparsers.add_parser("release", help="Release new version")
    parser.add_argument("--dry", action="store_true", help="Dry run")
    return parser


def format_fontsource_name(filename: str):
    match = re.match(r"MapleMono-(.*)\.(.*)$", filename.replace(".ttf", ""))
    if not match:
        return None

    style = match.group(1)
    base_style = style[:-6] if style.endswith("Italic") and style != "Italic" else style

    weight = INSTANCE_WEIGHT_MAPPING.get(
        base_style.lower(), INSTANCE_WEIGHT_MAPPING.get("regular", 400)
    )
    suffix = "italic" if "italic" in style.lower() else "normal"
    return f"maple-mono-latin-{weight}-{suffix}.{match.group(2)}"


def format_woff2_name(filename: str):
    return filename.replace(".ttf.woff2", "-VF.woff2")


def rename_woff_files(dir_path: str, fn: Callable[[str], str | None]):
    for filename in os.listdir(dir_path):
        if not filename.endswith(".woff") and not filename.endswith(".woff2"):
            continue
        new_name = fn(filename)
        if new_name:
            os.rename(join_path(dir_path, filename), join_path(dir_path, new_name))
            logger.info(
                "Renamed release font: source=%s, target=%s", filename, new_name
            )


def _target_core(current: str, bump: ReleaseBump) -> str:
    parsed = parse_project_version(current)
    if bump in ("minor", "pre-minor"):
        return f"{parsed.major}.{parsed.minor + 1}"
    return f"{parsed.major + 1}.0"


def next_version(current: str, bump: ReleaseBump) -> str:
    """Calculate the next PEP 440 project version without changing files."""
    parsed = parse_project_version(current)
    if bump not in RELEASE_BUMPS:
        raise ValueError(f"Unsupported version bump: {bump}")

    is_matching_finalize = parsed.beta is not None and (
        (bump == "minor" and parsed.minor != 0)
        or (bump == "major" and parsed.minor == 0)
    )
    if is_matching_finalize:
        return parsed.core

    matching_pre = (bump == "pre-minor" and parsed.minor != 0) or (
        bump == "pre-major" and parsed.minor == 0
    )
    if bump.startswith("pre-") and parsed.beta is not None and matching_pre:
        return f"{parsed.core}b{parsed.beta + 1}"

    target_core = _target_core(parsed.core, bump)

    if bump.startswith("pre-"):
        return f"{target_core}b1"
    return target_core


def read_font_version(config_path: str = "config.json") -> str:
    path = Path(config_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        font_version = data["font_version"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read font_version from {config_path}") from error
    if not isinstance(font_version, str):
        raise ValueError(f"font_version must be a string in {config_path}")
    parse_font_version(font_version)
    return font_version


def next_font_version(
    current_version: str,
    current_font_version: str,
    target_version: str,
) -> str:
    current = parse_project_version(current_version)
    target = parse_project_version(target_version)
    major, minor = parse_font_version(current_font_version)
    if major != current.major:
        raise ValueError(
            f"font_version {current_font_version} does not match project version {current_version}"
        )

    base = font_version_for_core(target.core)
    if target.beta is not None or (
        current.beta is not None and target.core == current.core
    ):
        next_minor = (
            minor + 1
            if target.core == current.core
            else parse_font_version(base)[1] + 1
        )
        if next_minor > 999:
            raise ValueError(f"Font version sequence is exhausted for {target.core}")
        return f"{target.major}.{next_minor:03}"
    return base


def update_font_version(font_version: str, config_path: str = "config.json") -> None:
    path = Path(config_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["font_version"] = font_version
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _format_release_choice(bump: ReleaseBump, plan: ReleasePlan) -> str:
    return f"{bump:<11} → {plan.tag:<16} (font {plan.font_version})"


def create_release_plans() -> dict[ReleaseBump, ReleasePlan]:
    current_version = project_version()
    current_font_version = read_font_version()
    return {
        bump: create_release_plan(
            bump,
            current_version=current_version,
            current_font_version=current_font_version,
        )
        for bump in RELEASE_BUMPS
    }


def select_release_bump(
    plans: dict[ReleaseBump, ReleasePlan],
) -> ReleaseBump | None:
    import questionary

    choices = [
        questionary.Choice(
            title=_format_release_choice(bump, plans[bump]),
            value=bump,
        )
        for bump in RELEASE_BUMPS
    ]
    try:
        answer = questionary.select(
            "Select release type:",
            choices=choices,
            default=RELEASE_BUMPS[0],
        ).ask()
    except (EOFError, KeyboardInterrupt):
        return None
    if answer is None:
        return None
    if answer not in RELEASE_BUMPS:
        raise ValueError(f"Unsupported release selection: {answer}")
    return answer


def git_release_commit(tag, files):
    run_command(["git", "add", *files])
    run_command(["git", "commit", "-m", f"Release {tag}"])
    run_command(["git", "tag", tag])
    logger.info("Committed release and created tag")

    run_command(["git", "push", "origin"])
    run_command(["git", "push", "origin", tag])
    logger.info("Pushed release to origin")


def create_release_plan(
    bump: ReleaseBump,
    *,
    current_version: str | None = None,
    current_font_version: str | None = None,
) -> ReleasePlan:
    current_version = current_version or project_version()
    target_version = next_version(current_version, bump)
    current_font_version = current_font_version or read_font_version()
    target_font_version = next_font_version(
        current_version,
        current_font_version,
        target_version,
    )
    return ReleasePlan(
        tag=version_tag(target_version),
        build_args=("--ttf-only", "--no-nerd-font", "--cn", "--no-hinted"),
        project_version=target_version,
        font_version=target_font_version,
    )


def generate_release_assets(plan: ReleasePlan) -> None:
    build_main(list(plan.build_args), plan.tag)

    shutil.rmtree("./cdn", ignore_errors=True)
    convert_to_web("./fonts/TTF", plan.fontsource_dir, flavor="woff2")
    convert_to_web("./fonts/TTF", plan.fontsource_dir, flavor="woff")
    rename_woff_files(plan.fontsource_dir, format_fontsource_name)
    logger.info("Generated Fontsource files")

    run_command(
        [
            "uv",
            "export",
            "--locked",
            "--no-dev",
            "--no-hashes",
            "--output-file",
            "requirements.txt",
        ]
    )

    shutil.copytree("./fonts/CN", "./cdn/cn")
    logger.info("Generated CN files")

    shutil.rmtree(plan.variable_woff2_dir, ignore_errors=True)
    for width in RELEASE_VARIABLE_WIDTHS:
        if width != "default":
            build_args = [arg for arg in plan.build_args if arg != "--cn"]
            build_main([*build_args, "--width", width], plan.tag)
        convert_to_web("./fonts/Variable", plan.variable_woff2_dir, flavor="woff2")
        rename_woff_files(plan.variable_woff2_dir, format_woff2_name)
        logger.info("Generated %s variable WOFF2 files", width)


def publish_release(plan: ReleasePlan) -> None:
    git_release_commit(
        plan.tag,
        [
            "woff2",
            plan.requirements_file,
            "config.json",
            "pyproject.toml",
            "uv.lock",
        ],
    )


def release(bump: ReleaseBump | None, dry: bool) -> None:
    if bump is None:
        plans = create_release_plans()
        bump = select_release_bump(plans)
        if bump is None:
            logger.info("Release aborted")
            return
        plan = plans[bump]
    else:
        plan = create_release_plan(bump)

    print(plan.describe())

    if dry:
        return

    choose = input("Create this release? (Y or n) ")
    if choose != "" and choose.lower() != "y":
        logger.info("Release aborted")
        return

    run_command(["uv", "version", plan.project_version])
    update_font_version(plan.font_version)
    generate_release_assets(plan)
    publish_release(plan)


def run(args: argparse.Namespace) -> None:
    release(None, args.dry)
