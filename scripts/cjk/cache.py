from __future__ import annotations

import re
import tempfile
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING
from zipfile import BadZipFile, ZipFile

from scripts.cache.digest import digest_tree

if TYPE_CHECKING:
    from scripts.cjk.config import CJKBuildConfig

HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def get_directory_hash(directory: str) -> str:
    """Use the canonical digest behind the legacy CJK sidecar file format."""
    return digest_tree(Path(directory))


def static_hash_path(config: CJKBuildConfig) -> Path:
    """Return the sidecar hash path for a generated static base."""
    return config.output.dir / config.output.static_hash


def write_static_hash(config: CJKBuildConfig, static_dir: Path) -> None:
    """Write one directory digest for the complete static CJK stage."""
    digest = get_directory_hash(str(static_dir))
    hash_path = static_hash_path(config)
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = hash_path.with_name(f".{hash_path.name}.tmp")
    temporary.write_text(f"{digest}\n", encoding="utf-8")
    temporary.replace(hash_path)


def verify_static_archive(archive_path: Path, expected_hash_path: Path) -> None:
    """Verify a static archive against a committed directory hash."""
    expected_hash = expected_hash_path.read_text(encoding="utf-8").strip()
    if not HASH_PATTERN.fullmatch(expected_hash):
        raise ValueError(f"Invalid static hash: {expected_hash_path}")

    try:
        with ZipFile(archive_path) as archive:
            members = archive.infolist()
            names = [member.filename for member in members]
            if not members:
                raise ValueError(f"Static archive is empty: {archive_path}")
            if len(names) != len(set(names)):
                raise ValueError(
                    f"Static archive contains duplicate members: {archive_path}"
                )
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
                        "Static archive must contain only root-level TTF files: "
                        f"{member.filename!r}"
                    )
            bad_member = archive.testzip()
            if bad_member is not None:
                raise ValueError(f"Corrupt static archive member: {bad_member!r}")
            with tempfile.TemporaryDirectory(
                prefix="cjk-static-verify-"
            ) as extract_dir:
                archive.extractall(extract_dir)
                actual_hash = get_directory_hash(extract_dir)
    except BadZipFile as error:
        raise ValueError(f"Invalid static archive: {archive_path}") from error

    if actual_hash != expected_hash:
        raise ValueError(
            f"Static archive hash mismatch: expected {expected_hash}, got {actual_hash}"
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
