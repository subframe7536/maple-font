from __future__ import annotations

import hashlib
import json
import shutil
import stat
from datetime import datetime, timezone
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote
from zipfile import ZIP_BZIP2, ZIP_DEFLATED, ZipFile, ZipInfo

from scripts.utils.logging import logger

if TYPE_CHECKING:
    from collections.abc import Callable

SOURCE_DATE_EPOCH = "SOURCE_DATE_EPOCH"
ZIP_MIN_EPOCH = 315_532_800
ZIP_MAX_EPOCH = 4_354_819_198
ZIP_FILE_MODE = stat.S_IFREG | 0o644


def join_path(*parts: str | Path) -> str:
    if not parts:
        raise ValueError("At least one path part is required")
    result = Path(parts[0])
    for part in parts[1:]:
        result /= part
    return str(result)


def write_text(
    file_path: str | Path,
    content: str,
    mode: str = "w",
) -> None:
    if not isinstance(content, str):
        raise ValueError("Invalid content")
    with Path(file_path).open(encoding="utf-8", mode=mode, newline="\n") as file:
        file.write(content)


def write_json(file_path: str | Path, data: dict[str, Any]) -> None:
    with Path(file_path).open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, indent=2)


def read_json(file_path: str | Path) -> dict[str, Any]:
    with Path(file_path).open("r", encoding="utf-8") as file:
        return json.load(file)


def read_text(file_path: str | Path) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def _archive_timestamp() -> tuple[int, int, int, int, int, int]:
    raw_value = environ.get(SOURCE_DATE_EPOCH)
    if raw_value is None:
        epoch = ZIP_MIN_EPOCH
    else:
        try:
            epoch = int(raw_value)
        except ValueError as error:
            raise ValueError(f"{SOURCE_DATE_EPOCH} must be an integer") from error
        if epoch < 0:
            raise ValueError(f"{SOURCE_DATE_EPOCH} must not be negative")
        epoch = min(max(epoch, ZIP_MIN_EPOCH), ZIP_MAX_EPOCH)
    value = datetime.fromtimestamp(epoch, timezone.utc)
    return (value.year, value.month, value.day, value.hour, value.minute, value.second)


def _archive_info(
    archive_path: str,
    timestamp: tuple[int, int, int, int, int, int],
    compression: int,
) -> ZipInfo:
    info = ZipInfo(archive_path, timestamp)
    info.compress_type = compression
    info.create_system = 3
    info.external_attr = ZIP_FILE_MODE << 16
    return info


def _write_archive_file(
    archive: ZipFile,
    source: Path,
    archive_path: str,
    timestamp: tuple[int, int, int, int, int, int],
    compression: int,
) -> None:
    info = _archive_info(archive_path, timestamp, compression)
    with (
        source.open("rb") as input_file,
        archive.open(
            info,
            "w",
            force_zip64=True,
        ) as output_file,
    ):
        shutil.copyfileobj(input_file, output_file, length=1024 * 1024)


def _write_archive_text(
    archive: ZipFile,
    content: str,
    archive_path: str,
    timestamp: tuple[int, int, int, int, int, int],
    compression: int,
) -> None:
    archive.writestr(
        _archive_info(archive_path, timestamp, compression),
        content.encode("utf-8"),
    )


def archive(
    source: str | Path,
    target: str | Path,
    include: Callable[[str], bool],
) -> None:
    source_path = Path(source)
    if not source_path.is_dir():
        raise NotADirectoryError(f"Invalid archive source directory: {source_path}")
    timestamp = _archive_timestamp()
    with ZipFile(target, "w", compression=ZIP_BZIP2, compresslevel=9) as zip_file:
        for child in sorted(source_path.iterdir()):
            if include(str(child)):
                _write_archive_file(
                    zip_file,
                    child,
                    child.name,
                    timestamp,
                    ZIP_BZIP2,
                )
    logger.info("Created archive: path=%s", target)


def archive_fonts(
    source_file_or_dir_path: str | Path,
    target_parent_dir_path: str,
    family_name_compact: str,
    suffix: str,
    build_config_path: str,
) -> tuple[str, str]:
    source_path = Path(source_file_or_dir_path)
    if not source_path.is_dir():
        raise NotADirectoryError(f"Invalid archive source directory: {source_path}")
    source_folder_name = source_path.name
    archive_label = archive_output_label(source_folder_name)
    zip_name_without_ext = f"{family_name_compact}-{archive_label}{suffix}"
    zip_path = join_path(target_parent_dir_path, f"{zip_name_without_ext}.zip")
    timestamp = _archive_timestamp()

    source_files = {
        file_path.relative_to(source_path).as_posix(): file_path
        for file_path in source_path.rglob("*")
        if file_path.is_file()
    }
    source_files.pop("README.md", None)
    font_files = [
        relative_path
        for relative_path, file_path in source_files.items()
        if file_path.suffix.lower() in {".otf", ".ttf", ".woff2"}
    ]
    source_files["LICENSE.txt"] = Path("OFL.txt")
    if not source_folder_name.startswith("Variable"):
        source_files["config.json"] = Path(build_config_path)
    generated_text = {
        "README.md": archive_font_readme(zip_name_without_ext, font_files),
    }

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=5) as zip_file:
        for archive_path in sorted(source_files.keys() | generated_text.keys()):
            if archive_path in generated_text:
                _write_archive_text(
                    zip_file,
                    generated_text[archive_path],
                    archive_path,
                    timestamp,
                    ZIP_DEFLATED,
                )
                continue
            _write_archive_file(
                zip_file,
                source_files[archive_path],
                archive_path,
                timestamp,
                ZIP_DEFLATED,
            )

    sha256 = hashlib.sha256()
    with Path(zip_path).open("rb") as zip_file:
        while data := zip_file.read(1024 * 1024):
            sha256.update(data)
    return sha256.hexdigest(), zip_name_without_ext


def archive_output_label(source_folder_name: str) -> str:
    if source_folder_name == "Variable":
        return "VF"
    if source_folder_name.startswith("Variable-"):
        return f"{source_folder_name.removeprefix('Variable-')}-VF"
    return source_folder_name


def archive_font_readme(archive_name: str, font_files: list[str]) -> str:
    lines = [f"# {archive_name}", "", "## Font Files", ""]
    lines.extend(
        f"- [{font_file}](./{quote(font_file, safe='/')})"
        for font_file in sorted(font_files)
    )
    return "\n".join(lines) + "\n"


def get_directory_hash(dir_path: str) -> str:
    """Return the canonical tree digest (kept for archive-task compatibility)."""
    from scripts.cache.digest import digest_tree

    return digest_tree(Path(dir_path))
