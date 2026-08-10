from __future__ import annotations

import re
import tempfile
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING
from zipfile import BadZipFile, ZipFile, ZipInfo

from scripts.cache.digest import digest_paths, digest_tree
from scripts.font_ops.fonttools import load_font

if TYPE_CHECKING:
    from scripts.cjk.config import CJKBuildConfig

HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
VARIABLE_NAME_PATTERN = re.compile(
    r"^MapleMono-(?P<locale>[A-Za-z0-9]+)(?P<italic>-Italic)?-VF\.ttf$"
)


def get_directory_hash(directory: str) -> str:
    """Use the canonical digest behind the legacy CJK sidecar file format."""
    return digest_tree(Path(directory))


def static_hash_path(config: CJKBuildConfig) -> Path:
    """Return the sidecar hash path for a generated static base."""
    return config.output.dir / config.output.static_hash


def variable_hash_path(config: CJKBuildConfig) -> Path:
    """Return the sidecar hash path for generated variable base fonts."""
    return config.output.dir / config.output.variable_hash


def variable_paths(config: CJKBuildConfig) -> tuple[Path, Path]:
    """Return the regular and italic variable base paths in stable order."""
    return (
        config.output.dir / config.output.regular_variable,
        config.output.dir / config.output.italic_variable,
    )


def write_static_hash(config: CJKBuildConfig, static_dir: Path) -> None:
    """Write one directory digest for the complete static CJK stage."""
    digest = get_directory_hash(str(static_dir))
    hash_path = static_hash_path(config)
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = hash_path.with_name(f".{hash_path.name}.tmp")
    temporary.write_text(f"{digest}\n", encoding="utf-8")
    temporary.replace(hash_path)


def write_variable_hash(config: CJKBuildConfig) -> None:
    """Write a digest covering only the regular and italic variable outputs."""
    paths = variable_paths(config)
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Variable CJK base output is missing: "
            + ", ".join(str(path) for path in missing)
        )
    digest = digest_paths(config.output.dir, list(paths))
    hash_path = variable_hash_path(config)
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = hash_path.with_name(f".{hash_path.name}.tmp")
    temporary.write_text(f"{digest}\n", encoding="utf-8")
    temporary.replace(hash_path)


def _validate_root_level_ttf_members(
    members: list[ZipInfo], archive_label: str
) -> list[str]:
    """Validate archive member shape shared by static and variable bases."""
    names = [member.filename for member in members]
    if len(names) != len(set(names)):
        raise ValueError(f"{archive_label} archive contains duplicate members")
    for member in members:
        member_path = PurePosixPath(member.filename)
        if (
            member.is_dir()
            or "/" in member.filename
            or "\\" in member.filename
            or member.filename != member_path.name
            or member_path.name in {"", ".", ".."}
            or member_path.suffix.lower() != ".ttf"
        ):
            raise ValueError(
                f"{archive_label} archive must contain only root-level TTF files: "
                f"{member.filename!r}"
            )
    return names


def verify_static_archive(
    archive_path: Path,
    expected_hash_path: Path,
    extracted_dir: Path | None = None,
) -> None:
    """Verify a static archive against a committed directory hash."""
    expected_hash = expected_hash_path.read_text(encoding="utf-8").strip()
    if not HASH_PATTERN.fullmatch(expected_hash):
        raise ValueError(f"Invalid static hash: {expected_hash_path}")

    try:
        with ZipFile(archive_path) as archive:
            members = archive.infolist()
            if not members:
                raise ValueError(f"Static archive is empty: {archive_path}")
            _validate_root_level_ttf_members(members, "Static")
            bad_member = archive.testzip()
            if bad_member is not None:
                raise ValueError(f"Corrupt static archive member: {bad_member!r}")
            if extracted_dir is None:
                with tempfile.TemporaryDirectory(
                    prefix="cjk-static-verify-"
                ) as extract_dir:
                    archive.extractall(extract_dir)
                    actual_hash = get_directory_hash(extract_dir)
            else:
                actual_hash = get_directory_hash(str(extracted_dir))
    except BadZipFile as error:
        raise ValueError(f"Invalid static archive: {archive_path}") from error

    if actual_hash != expected_hash:
        raise ValueError(
            f"Static archive hash mismatch: expected {expected_hash}, got {actual_hash}"
        )


def _verify_variable_directory(names: list[str], extracted_dir: Path) -> str:
    """Validate variable fonts in an extracted archive and return their digest."""
    for name in names:
        font_path = extracted_dir / name
        try:
            font = load_font(font_path)
        except Exception as error:
            raise ValueError(
                f"Variable archive member is not a valid font: {name}"
            ) from error
        try:
            if "fvar" not in font:
                raise ValueError(f"Variable archive member is not variable: {name}")
        finally:
            font.close()
    return digest_tree(extracted_dir)


def verify_variable_archive(
    archive_path: Path,
    expected_hash_path: Path,
    expected_names: tuple[str, ...] | None = None,
    extracted_dir: Path | None = None,
) -> None:
    """Verify a variable base archive and its regular/italic font members."""
    expected_hash = expected_hash_path.read_text(encoding="utf-8").strip()
    if not HASH_PATTERN.fullmatch(expected_hash):
        raise ValueError(f"Invalid variable hash: {expected_hash_path}")

    try:
        with ZipFile(archive_path) as archive:
            members = archive.infolist()
            names = _validate_root_level_ttf_members(members, "Variable")
            if len(names) != 2:
                raise ValueError(
                    "Variable archive must contain exactly two TTF files: "
                    f"{archive_path}"
                )
            if expected_names is not None and set(names) != set(expected_names):
                raise ValueError(
                    "Variable archive members do not match the expected outputs: "
                    f"expected {sorted(expected_names)}, got {sorted(names)}"
                )
            if expected_names is None:
                parsed_names = [VARIABLE_NAME_PATTERN.fullmatch(name) for name in names]
                locales = {
                    match.group("locale") for match in parsed_names if match is not None
                }
                if (
                    any(match is None for match in parsed_names)
                    or len(locales) != 1
                    or sum(
                        match is not None and match.group("italic") is None
                        for match in parsed_names
                    )
                    != 1
                ):
                    raise ValueError(
                        "Variable archive members do not match the expected regular "
                        "and italic CJK variable font names"
                    )
            bad_member = archive.testzip()
            if bad_member is not None:
                raise ValueError(f"Corrupt variable archive member: {bad_member!r}")
            if extracted_dir is None:
                with tempfile.TemporaryDirectory(
                    prefix="cjk-variable-verify-"
                ) as extract_dir:
                    archive.extractall(extract_dir)
                    actual_hash = _verify_variable_directory(
                        names,
                        Path(extract_dir),
                    )
            else:
                actual_hash = _verify_variable_directory(names, extracted_dir)
    except BadZipFile as error:
        raise ValueError(f"Invalid variable archive: {archive_path}") from error

    if actual_hash != expected_hash:
        raise ValueError(
            f"Variable archive hash mismatch: expected {expected_hash}, got {actual_hash}"
        )


def has_valid_cjk_static_cache(
    config: CJKBuildConfig,
    static_dir: Path,
    required_styles: set[str],
) -> bool:
    """Validate required static styles and the stage-level directory digest."""
    if not static_dir.is_dir():
        return False

    prefix = f"{config.naming.static_file_prefix}-"
    available_styles = {
        path.stem.removeprefix(prefix)
        for path in static_dir.glob("*.ttf")
        if path.name.startswith(prefix)
    }
    if not required_styles.issubset(available_styles):
        return False

    hash_path = static_hash_path(config)
    if not hash_path.is_file():
        return False
    try:
        expected = hash_path.read_text(encoding="utf-8").strip()
        actual = get_directory_hash(str(static_dir))
    except Exception:
        return False
    return bool(expected) and expected == actual
