from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from scripts.external.process import is_ci
from scripts.utils.files import archive_fonts
from scripts.utils.logging import logger
from scripts.utils.version import parse_version_tag, version_tag

if TYPE_CHECKING:
    import argparse

ReleaseTaskKind = Literal["base", "cjk"]
RELEASE_ASSET_DIR = Path("release")
RELEASE_TASK_DIR = Path("release-task")
BUILD_ARCHIVE_DIR = Path("fonts/archive")


@dataclass(frozen=True, slots=True)
class ReleaseProfile:
    id: str
    args: tuple[str, ...]
    family_suffix: str


@dataclass(frozen=True, slots=True)
class ReleaseWidth:
    id: str
    value: str
    family_suffix: str


@dataclass(frozen=True, slots=True)
class ReleaseLocale:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class ReleaseTask:
    kind: ReleaseTaskKind
    profile: ReleaseProfile
    width: ReleaseWidth
    locale: ReleaseLocale | None = None

    @property
    def id(self) -> str:
        parts = [self.kind, self.profile.id, self.width.id]
        if self.locale is not None:
            parts.append(self.locale.id)
        return "-".join(parts)

    @property
    def family_name(self) -> str:
        return "MapleMono" + self.profile.family_suffix + self.width.family_suffix

    def archive_names(self) -> tuple[str, ...]:
        if self.kind == "base":
            targets = BASE_ARCHIVE_TARGETS
        else:
            if self.locale is None:
                raise ValueError("CJK release task requires a locale")
            targets = tuple(
                target.format(locale=self.locale.name) for target in CJK_ARCHIVE_TARGETS
            )
        return tuple(f"{self.family_name}-{target}.zip" for target in targets)


RELEASE_PROFILES = (
    ReleaseProfile("default", ("--liga",), ""),
    ReleaseProfile("normal", ("--normal", "--liga"), "Normal"),
    ReleaseProfile("no-ligature", ("--no-liga",), "NL"),
    ReleaseProfile(
        "normal-no-ligature",
        ("--normal", "--no-liga"),
        "NormalNL",
    ),
)
RELEASE_WIDTHS = (
    ReleaseWidth("default", "default", ""),
    ReleaseWidth("narrow", "narrow", "NR"),
    ReleaseWidth("slim", "slim", "SL"),
)
RELEASE_CJK_LOCALES = (
    ReleaseLocale("cn", "CN"),
    ReleaseLocale("tc", "TC"),
    ReleaseLocale("jp", "JP"),
    ReleaseLocale("kr", "KR"),
)
BASE_ARCHIVE_TARGETS = (
    "VF",
    "TTF",
    "TTF-AutoHint",
    "OTF",
    "Woff2",
    "NF",
    "NF-unhinted",
    "NF-VF",
)
CJK_ARCHIVE_TARGETS = (
    "NF-{locale}-VF",
    "NF-{locale}",
    "NF-{locale}-unhinted",
)


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser = subparsers.add_parser(
        "publish", help="Build and publish GitHub Release font archives"
    )
    actions = parser.add_subparsers(dest="publish_action", required=True)

    matrix_parser = actions.add_parser(
        "matrix", help="Print a GitHub Actions release task matrix"
    )
    matrix_parser.add_argument("kind", choices=("base", "cjk"))

    build_parser = actions.add_parser("build", help="Run one release build task")
    build_parser.add_argument("task", help="Task id emitted by the matrix command")
    build_parser.add_argument(
        "--build-args",
        default="",
        help="Additional build.py arguments used by workflow dispatch",
    )

    release_parser = actions.add_parser(
        "release", help="Validate assets and create a draft GitHub Release"
    )
    release_parser.add_argument(
        "--write",
        action="store_true",
        help="Write changelog to release note file (auto write in CI)",
    )
    release_parser.add_argument(
        "--tag",
        help="Git tag to publish (defaults to the unique tag pointing at HEAD)",
    )
    return parser


def release_tasks(kind: ReleaseTaskKind | None = None) -> tuple[ReleaseTask, ...]:
    base_tasks = tuple(
        ReleaseTask("base", profile, width)
        for profile in RELEASE_PROFILES
        for width in RELEASE_WIDTHS
    )
    cjk_tasks = tuple(
        ReleaseTask("cjk", profile, width, locale)
        for profile in RELEASE_PROFILES
        for width in RELEASE_WIDTHS
        for locale in RELEASE_CJK_LOCALES
    )
    if kind == "base":
        return base_tasks
    if kind == "cjk":
        return cjk_tasks
    return (*base_tasks, *cjk_tasks)


def release_matrix(kind: ReleaseTaskKind) -> dict[str, list[dict[str, str]]]:
    return {"include": [{"task": task.id} for task in release_tasks(kind)]}


def release_manifest() -> dict[str, Any]:
    return {
        "profiles": [
            {"id": profile.id, "family_suffix": profile.family_suffix}
            for profile in RELEASE_PROFILES
        ],
        "widths": [
            {
                "id": width.id,
                "value": width.value,
                "family_suffix": width.family_suffix,
            }
            for width in RELEASE_WIDTHS
        ],
        "base": {"targets": list(BASE_ARCHIVE_TARGETS)},
        "cjk": {
            "locales": [
                {"id": locale.id, "name": locale.name} for locale in RELEASE_CJK_LOCALES
            ],
            "targets": list(CJK_ARCHIVE_TARGETS),
        },
    }


def resolve_release_task(task_id: str) -> ReleaseTask:
    try:
        return next(task for task in release_tasks() if task.id == task_id)
    except StopIteration as error:
        raise ValueError(f"Unknown release task: {task_id}") from error


def release_build_steps(
    task: ReleaseTask,
    extra_args: tuple[str, ...] = (),
) -> tuple[list[str], ...]:
    common = [
        *extra_args,
        "--nf",
        "--width",
        task.width.value,
        *task.profile.args,
    ]
    if task.kind == "base":
        return (
            [*common, "--format", "ttf,otf,woff2", "--hinted"],
            [
                *common,
                "--format",
                "ttf,otf,woff2",
                "--no-hinted",
                "--cache",
            ],
            [
                *extra_args,
                "--archive",
                "--nf-variable",
                "--width",
                task.width.value,
                *task.profile.args,
                "--format",
                "ttf,otf,woff2",
                "--no-hinted",
                "--cache",
            ],
        )
    if task.locale is None:
        raise ValueError("CJK release task requires a locale")
    cjk = [*common, "--format", "ttf", "--cjk", task.locale.id]
    return (
        [
            *cjk,
            "--hinted",
        ],
        [
            *cjk,
            "--no-hinted",
            "--no-cjk-hinted",
            "--cache",
        ],
        [
            *cjk,
            "--cjk-variable",
            "--no-hinted",
            "--no-cjk-hinted",
            "--cache",
        ],
    )


def collect_release_task_archives(
    task: ReleaseTask,
    archive_dir: Path = BUILD_ARCHIVE_DIR,
    output_dir: Path = RELEASE_TASK_DIR,
) -> None:
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True)
    missing = [
        name for name in task.archive_names() if not (archive_dir / name).is_file()
    ]
    if missing:
        raise FileNotFoundError(
            f"Release task {task.id} did not produce: {', '.join(missing)}"
        )
    for archive_name in task.archive_names():
        shutil.copy2(archive_dir / archive_name, output_dir / archive_name)


def archive_overwritten_release_output(task: ReleaseTask) -> None:
    """Snapshot the hinted NF archive before later steps replace its files."""
    if task.kind == "base":
        folder = "NF"
    else:
        if task.locale is None:
            raise ValueError("CJK release task requires a locale")
        folder = f"NF-{task.locale.name}"
    source_dir = BUILD_ARCHIVE_DIR.parent / folder
    if not source_dir.is_dir():
        raise FileNotFoundError(
            f"Release task output directory is missing: {source_dir}"
        )
    BUILD_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_fonts(
        source_dir,
        str(BUILD_ARCHIVE_DIR),
        task.family_name,
        "",
        str(BUILD_ARCHIVE_DIR.parent / "build-config.json"),
    )


def build_release_task(task_id: str, build_args: str = "") -> None:
    from scripts.pipeline import main as build_main

    task = resolve_release_task(task_id)
    for index, build_step in enumerate(
        release_build_steps(task, tuple(shlex.split(build_args)))
    ):
        build_main(build_step)
        if index == 0:
            archive_overwritten_release_output(task)
    collect_release_task_archives(task)


def expected_release_archives() -> set[str]:
    return {
        archive_name
        for task in release_tasks()
        for archive_name in task.archive_names()
    }


def prepare_release_assets(release_dir: Path = RELEASE_ASSET_DIR) -> None:
    archives = sorted(release_dir.rglob("*.zip"), key=lambda path: path.name)
    archive_names = [path.name for path in archives]
    if len(archive_names) != len(set(archive_names)):
        raise ValueError("Release assets contain duplicate archive names")

    expected = expected_release_archives()
    actual = set(archive_names)
    if actual != expected:
        missing = ", ".join(sorted(expected - actual)) or "none"
        unexpected = ", ".join(sorted(actual - expected)) or "none"
        raise ValueError(
            f"Release archive mismatch; missing: {missing}; unexpected: {unexpected}"
        )

    (release_dir / "release-manifest.json").write_text(
        json.dumps(release_manifest(), indent=2) + "\n",
        encoding="utf-8",
    )


def get_output(cmd: list[str]) -> str:
    return subprocess.check_output(cmd).decode("utf-8").strip()


def resolve_release_tags(tag: str | None) -> tuple[str, str]:
    if tag is not None:
        try:
            get_output(["git", "rev-parse", "--verify", f"refs/tags/{tag}"])
        except subprocess.CalledProcessError as error:
            raise ValueError(f"Unknown release tag: {tag}") from error
    else:
        tags = get_output(["git", "tag", "--points-at", "HEAD"]).splitlines()
        if not tags:
            raise ValueError("No release tag points at HEAD; pass --tag explicitly")
        if len(tags) > 1:
            raise ValueError(
                "Multiple release tags point at HEAD; pass --tag explicitly: "
                + ", ".join(tags)
            )
        tag = tags[0]

    prev_tag = get_output(
        ["git", "describe", "--tags", "--match", "v*", "--abbrev=0", f"{tag}^"]
    )
    return prev_tag, tag


def publish(write: bool, tag: str | None = None, dry: bool = not is_ci()):
    prev_tag, tag = resolve_release_tags(tag)
    expected_tag = version_tag()
    try:
        tags_match = parse_version_tag(tag) == parse_version_tag(expected_tag)
    except ValueError:
        tags_match = False
    if not tags_match:
        raise ValueError(
            f"Release tag {tag} does not match the project version tag {expected_tag}"
        )
    logger.info("Publish release: previous_tag=%s, tag=%s", prev_tag, tag)

    changelog = get_output(
        ["git", "log", "--pretty=format:- %s\n%b", f"{prev_tag}..{tag}"]
    )

    template_path = Path(".github/release_template.md")
    title = " ".join(part.capitalize() for part in tag.split("-"))
    cmd = [
        "gh",
        "release",
        "create",
        tag,
        "release/*.zip",
        "release/release-manifest.json",
        "--notes-file",
        template_path.as_posix(),
        "-t",
        title,
        "--draft",
    ]

    template = (
        template_path.read_text()
        .replace("<!-- changelog -->", changelog)
        .replace(
            "https://<url>",
            f"https://github.com/subframe7536/maple-font/releases/download/{tag}",
        )
    )
    if write or not dry:
        template_path.write_text(template)

    if dry:
        print(f"changelog:\n{changelog}\n\nRun command: {' '.join(cmd)}")
    else:
        prepare_release_assets()
        subprocess.run(cmd, check=True)


def run(args: argparse.Namespace) -> None:
    if args.publish_action == "matrix":
        print(json.dumps(release_matrix(args.kind), separators=(",", ":")))
    elif args.publish_action == "build":
        build_release_task(args.task, args.build_args)
    else:
        publish(args.write, args.tag)
