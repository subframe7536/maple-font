from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from scripts.utils.files import archive_fonts
from scripts.utils.logging import logger
from scripts.utils.process import is_ci
from scripts.utils.version import parse_version_tag, version_tag

if TYPE_CHECKING:
    import argparse

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
    full_release: bool


@dataclass(frozen=True, slots=True)
class ReleaseLocale:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class ReleaseNFVariant:
    id: str
    args: tuple[str, ...]
    directory_name: str
    static_modes: tuple[str, ...]
    variable: bool
    locales: bool

    def manifest(self) -> dict[str, object]:
        return {
            "id": self.id,
            "args": list(self.args),
            "directory": self.directory_name,
            "static_modes": list(self.static_modes),
            "variable": self.variable,
            "locales": self.locales,
        }


@dataclass(frozen=True, slots=True)
class ReleaseArchiveSpec:
    directory: str
    suffix: str = ""


@dataclass(frozen=True, slots=True)
class ReleaseBuildStep:
    args: tuple[str, ...]
    archives: tuple[ReleaseArchiveSpec, ...]


@dataclass(frozen=True, slots=True)
class ReleaseTask:
    profile: ReleaseProfile
    width: ReleaseWidth

    @property
    def id(self) -> str:
        return f"bundle-{self.profile.id}-{self.width.id}"

    @property
    def family_name(self) -> str:
        return "MapleMono" + self.profile.family_suffix + self.width.family_suffix

    @property
    def base_archive_targets(self) -> tuple[str, ...]:
        return (
            BASE_ARCHIVE_TARGETS
            if self.width.full_release
            else COMPACT_BASE_ARCHIVE_TARGETS
        )

    @property
    def cjk_archive_targets(self) -> tuple[str, ...]:
        return (
            CJK_ARCHIVE_TARGETS
            if self.width.full_release
            else COMPACT_CJK_ARCHIVE_TARGETS
        )

    def archive_names(self) -> tuple[str, ...]:
        base_targets = tuple(
            f"{self.family_name}-{target}.zip" for target in self.base_archive_targets
        )
        cjk_targets = tuple(
            f"{self.family_name}-{target.format(locale=locale.name)}.zip"
            for locale in RELEASE_CJK_LOCALES
            for target in self.cjk_archive_targets
        )
        return (*base_targets, *cjk_targets)


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
    ReleaseWidth("default", "default", "", True),
    ReleaseWidth("narrow", "narrow", "NR", False),
    ReleaseWidth("slim", "slim", "SL", False),
)
PROFILE_LABELS = {
    "default": "Ligature (default)",
    "normal": "Normal-Ligature",
    "no-ligature": "No-Ligature",
    "normal-no-ligature": "Normal-No-Ligature",
}
WIDTH_LABELS = {
    "default": "Default width",
    "narrow": "Narrow width (NR)",
    "slim": "Slim width (SL)",
}
RELEASE_CJK_LOCALES = (
    ReleaseLocale("cn", "CN"),
    ReleaseLocale("tc", "TC"),
    ReleaseLocale("jp", "JP"),
    ReleaseLocale("kr", "KR"),
)
RELEASE_NF_VARIANTS = (
    ReleaseNFVariant(
        "nf",
        ("--nf",),
        "NF",
        ("hinted", "unhinted"),
        True,
        True,
    ),
    ReleaseNFVariant(
        "nfmono",
        ("--nf-mono",),
        "NFMono",
        ("unhinted",),
        False,
        False,
    ),
    ReleaseNFVariant(
        "nfpropo",
        ("--nf-propo",),
        "NFPropo",
        ("unhinted",),
        False,
        False,
    ),
)
RELEASE_DEFAULT_NF_VARIANT = RELEASE_NF_VARIANTS[0]
BASE_CORE_ARCHIVE_TARGETS = (
    "VF",
    "TTF",
    "TTF-AutoHint",
    "OTF",
    "Woff2",
)
BASE_NF_COMMON_ARCHIVE_TARGETS = (
    "NF",
    "NF-unhinted",
)
BASE_NF_EXTENDED_ARCHIVE_TARGETS = (
    "NF-VF",
    "NFMono-unhinted",
    "NFPropo-unhinted",
)
BASE_NF_ARCHIVE_TARGETS = (
    *BASE_NF_COMMON_ARCHIVE_TARGETS,
    *BASE_NF_EXTENDED_ARCHIVE_TARGETS,
)
BASE_ARCHIVE_TARGETS = (
    *BASE_CORE_ARCHIVE_TARGETS,
    *BASE_NF_ARCHIVE_TARGETS,
)
COMPACT_BASE_ARCHIVE_TARGETS = (
    *BASE_CORE_ARCHIVE_TARGETS,
    *BASE_NF_COMMON_ARCHIVE_TARGETS,
)
CJK_ARCHIVE_TARGETS = (
    "NF-{locale}-VF",
    "NF-{locale}",
    "NF-{locale}-unhinted",
)
COMPACT_CJK_ARCHIVE_TARGETS = ("NF-{locale}-unhinted",)


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser = subparsers.add_parser(
        "publish", help="Build and publish GitHub Release font archives"
    )
    actions = parser.add_subparsers(dest="publish_action", required=True)

    actions.add_parser("matrix", help="Print a GitHub Actions release task matrix")

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


def release_tasks() -> tuple[ReleaseTask, ...]:
    return tuple(
        ReleaseTask(profile, width)
        for profile in RELEASE_PROFILES
        for width in RELEASE_WIDTHS
    )


def release_matrix() -> dict[str, list[str]]:
    return {"task": [task.id for task in release_tasks()]}


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
                "release_mode": "full" if width.full_release else "compact",
            }
            for width in RELEASE_WIDTHS
        ],
        "nf_variants": [variant.manifest() for variant in RELEASE_NF_VARIANTS],
        "base": {
            "targets": list(BASE_ARCHIVE_TARGETS),
            "compact_targets": list(COMPACT_BASE_ARCHIVE_TARGETS),
        },
        "cjk": {
            "locales": [
                {"id": locale.id, "name": locale.name} for locale in RELEASE_CJK_LOCALES
            ],
            "targets": list(CJK_ARCHIVE_TARGETS),
            "compact_targets": list(COMPACT_CJK_ARCHIVE_TARGETS),
        },
        "archives": sorted(expected_release_archives()),
    }


def resolve_release_task(task_id: str) -> ReleaseTask:
    try:
        return next(task for task in release_tasks() if task.id == task_id)
    except StopIteration as error:
        raise ValueError(f"Unknown release task: {task_id}") from error


def release_build_steps(
    task: ReleaseTask,
    extra_args: tuple[str, ...] = (),
) -> tuple[ReleaseBuildStep, ...]:
    common = [
        *extra_args,
        *RELEASE_DEFAULT_NF_VARIANT.args,
        "--width",
        task.width.value,
        *task.profile.args,
    ]
    core_nf_args = ("--nf-variable",) if task.width.full_release else ("--no-nf",)
    core_directories = [
        "Variable",
        "TTF",
        "TTF-AutoHint",
        "OTF",
        "Woff2",
    ]
    if task.width.full_release:
        core_directories.append("Variable-NF")

    base_steps: tuple[ReleaseBuildStep, ...] = (
        ReleaseBuildStep(
            (*common, "--format", "ttf,otf,woff2", "--hinted"),
            (ReleaseArchiveSpec("NF"),),
        ),
        ReleaseBuildStep(
            (
                *common,
                "--format",
                "ttf,otf,woff2",
                "--no-hinted",
                "--cache",
            ),
            (ReleaseArchiveSpec("NF", "-unhinted"),),
        ),
        ReleaseBuildStep(
            (
                *extra_args,
                *core_nf_args,
                "--width",
                task.width.value,
                *task.profile.args,
                "--format",
                "ttf,otf,woff2",
                "--no-hinted",
                "--cache",
            ),
            tuple(ReleaseArchiveSpec(directory) for directory in core_directories),
        ),
    )
    if task.width.full_release:
        base_steps = (
            *base_steps,
            *_release_nf_variant_steps(task, extra_args, RELEASE_NF_VARIANTS[1:]),
        )

    cjk_locales = ",".join(locale.id for locale in RELEASE_CJK_LOCALES)
    cjk = [*common, "--format", "ttf", "--cjk", cjk_locales]
    cjk_directories = tuple(
        f"{RELEASE_DEFAULT_NF_VARIANT.directory_name}-{locale.name}"
        for locale in RELEASE_CJK_LOCALES
    )
    cjk_unhinted_step = ReleaseBuildStep(
        (
            *cjk,
            "--no-hinted",
            "--no-cjk-hinted",
            "--cache",
        ),
        tuple(
            ReleaseArchiveSpec(directory, "-unhinted") for directory in cjk_directories
        ),
    )
    if not task.width.full_release:
        return (*base_steps, cjk_unhinted_step)

    return (
        *base_steps,
        ReleaseBuildStep(
            (*cjk, "--hinted", "--cache"),
            tuple(ReleaseArchiveSpec(directory) for directory in cjk_directories),
        ),
        cjk_unhinted_step,
        ReleaseBuildStep(
            (
                *cjk,
                "--cjk-variable",
                "--no-hinted",
                "--no-cjk-hinted",
                "--cache",
            ),
            tuple(
                ReleaseArchiveSpec(f"Variable-{directory}")
                for directory in cjk_directories
            ),
        ),
    )


def _release_nf_variant_steps(
    task: ReleaseTask,
    extra_args: tuple[str, ...],
    variants: tuple[ReleaseNFVariant, ...],
) -> tuple[ReleaseBuildStep, ...]:
    return tuple(
        ReleaseBuildStep(
            (
                *extra_args,
                *variant.args,
                "--width",
                task.width.value,
                *task.profile.args,
                "--format",
                "ttf",
                "--no-hinted",
                "--cache",
            ),
            (ReleaseArchiveSpec(variant.directory_name, "-unhinted"),),
        )
        for variant in variants
    )


def _archive_link(
    base_url: str,
    task: ReleaseTask,
    target: str,
    label: str = "Download",
) -> str:
    return f"[{label}]({base_url}/{task.family_name}-{target}.zip)"


def _release_table_cell(base_url: str, task: ReleaseTask, format_name: str) -> str:
    if format_name == "Variable":
        return _archive_link(base_url, task, "VF")
    if format_name == "TTF":
        return (
            f"{_archive_link(base_url, task, 'TTF')} / "
            f"{_archive_link(base_url, task, 'TTF-AutoHint', 'Hinted')}"
        )
    if format_name == "OTF":
        return _archive_link(base_url, task, "OTF")
    if format_name == "WOFF2":
        return _archive_link(base_url, task, "Woff2")
    if format_name == "NF":
        unhinted = _archive_link(base_url, task, "NF-unhinted")
        hinted = _archive_link(base_url, task, "NF", "Hinted")
        if not task.width.full_release:
            return f"{unhinted} / {hinted}"
        nfmono = _archive_link(base_url, task, "NFMono-unhinted", "NFMono")
        nfpropo = _archive_link(base_url, task, "NFPropo-unhinted", "NFPropo")
        variable = _archive_link(base_url, task, "NF-VF", "Variable")
        return f"{unhinted} ({nfmono} / {nfpropo}) / {hinted} / {variable}"
    if format_name.startswith("NF-"):
        locale = format_name.removeprefix("NF-")
        unhinted = _archive_link(base_url, task, f"NF-{locale}-unhinted")
        if not task.width.full_release:
            return unhinted
        hinted = _archive_link(base_url, task, f"NF-{locale}", "Hinted")
        variable = _archive_link(base_url, task, f"NF-{locale}-VF", "Variable")
        return f"{unhinted} / {hinted} / {variable}"
    raise ValueError(f"Unsupported release table format: {format_name}")


def render_download_matrix(base_url: str = "https://<url>") -> str:
    lines: list[str] = []
    formats = (
        "Variable",
        "TTF",
        "OTF",
        "WOFF2",
        "NF",
        *(f"NF-{locale.name}" for locale in RELEASE_CJK_LOCALES),
    )
    header = (
        "| Format | "
        + " | ".join(PROFILE_LABELS[profile.id] for profile in RELEASE_PROFILES)
        + " |"
    )
    separator = "| --- | " + " | ".join("---" for _ in RELEASE_PROFILES) + " |"

    for width in RELEASE_WIDTHS:
        lines.extend((f"### {WIDTH_LABELS[width.id]}", ""))
        if not width.full_release:
            lines.extend(
                (
                    "<details>",
                    "<summary>Click to expand</summary>",
                    "",
                    "Compact release: common base packages and unhinted NF-CJK packages.",
                    "",
                )
            )

        lines.extend((header, separator))
        for format_name in formats:
            cells = [
                _release_table_cell(
                    base_url,
                    ReleaseTask(profile, width),
                    format_name,
                )
                for profile in RELEASE_PROFILES
            ]
            lines.append(f"| {format_name} | " + " | ".join(cells) + " |")
        lines.append("")

        if not width.full_release:
            lines.extend(("</details>", ""))

    lines.extend(
        (
            "### Note",
            "",
            "- Default width publishes the full release matrix. Narrow (NR) and Slim (SL) publish the common compact matrix.",
            "- Static output is the default and has no Static suffix. Variable archives use the -VF suffix.",
            "- NFMono and NFPropo are published only for the default width as unhinted static fonts.",
            f"- The complete machine-readable matrix is available in [release-manifest.json]({base_url}/release-manifest.json).",
        )
    )
    return "\n".join(lines)


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


def archive_release_step(task: ReleaseTask, step: ReleaseBuildStep) -> None:
    BUILD_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    for archive in step.archives:
        source_dir = BUILD_ARCHIVE_DIR.parent / archive.directory
        if not source_dir.is_dir():
            raise FileNotFoundError(
                f"Release task {task.id} output directory is missing: {source_dir}"
            )
        archive_fonts(
            source_dir,
            str(BUILD_ARCHIVE_DIR),
            task.family_name,
            archive.suffix,
            str(BUILD_ARCHIVE_DIR.parent / "build-config.json"),
        )


def build_release_task(task_id: str, build_args: str = "") -> None:
    from scripts.pipeline import main as build_main

    task = resolve_release_task(task_id)
    for build_step in release_build_steps(task, tuple(shlex.split(build_args))):
        build_main(list(build_step.args))
        archive_release_step(task, build_step)
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

    template = template_path.read_text().replace("<!-- changelog -->", changelog)
    template = template.replace("<!-- download-matrix -->", render_download_matrix())
    template = template.replace(
        "https://<url>",
        f"https://github.com/subframe7536/maple-font/releases/download/{tag}",
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
        print(json.dumps(release_matrix(), separators=(",", ":")))
    elif args.publish_action == "build":
        build_release_task(args.task, args.build_args)
    else:
        publish(args.write, args.tag)
