from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen
from zipfile import ZipFile

import py7zr

from scripts.errors import ArchiveError, ArchiveMemberNotFoundError, DownloadError
from scripts.utils.logging import log_progress, logger

GITHUB_HOST = "github.com"
GITHUB_RAW_HOST = "raw.githubusercontent.com"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)
DOWNLOAD_TIMEOUT_SECONDS = 60
MAX_DOWNLOAD_BYTES = 512 * 1024 * 1024
MAX_JSON_BYTES = 8 * 1024 * 1024
MAX_EXTRACTED_BYTES = 2 * 1024 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 10_000


def github_host(default: str = GITHUB_HOST) -> str:
    configured = os.environ.get("GITHUB", default).strip().rstrip("/")
    return configured or GITHUB_HOST


def github_mirror_from_config(config_path: str | Path = "config.json") -> str:
    """Return the task download mirror, with GITHUB taking precedence."""
    data = json.loads(Path(config_path).read_text(encoding="utf-8"))
    configured = data.get("github_mirror", GITHUB_HOST)
    if not isinstance(configured, str):
        raise ValueError("github_mirror must be a string")
    return github_host(configured)


def resolve_download_url(url: str, github_mirror: str = GITHUB_HOST) -> str:
    """Resolve GitHub release and raw URLs through the configured mirror host."""
    mirror = github_host(github_mirror)
    parsed = urlsplit(url)
    host = parsed.hostname
    if host == GITHUB_RAW_HOST:
        path_parts = parsed.path.lstrip("/").split("/", 2)
        if len(path_parts) == 3:
            owner, repository, remainder = path_parts
            parsed = parsed._replace(
                scheme="https",
                netloc=GITHUB_HOST,
                path=f"/{owner}/{repository}/raw/{remainder}",
            )
            host = GITHUB_HOST
    if mirror == GITHUB_HOST:
        return urlunsplit(parsed)
    mirror_url = mirror if "://" in mirror else f"https://{mirror}"
    parsed_mirror = urlsplit(mirror_url)

    def mirrored_url(path: str) -> str:
        mirror_path = f"{parsed_mirror.path.rstrip('/')}/{path.lstrip('/')}"
        return urlunsplit(
            (
                parsed_mirror.scheme or "https",
                parsed_mirror.netloc,
                mirror_path,
                parsed.query,
                parsed.fragment,
            )
        )

    if host == GITHUB_HOST:
        return mirrored_url(parsed.path)
    return url


def _download_request(url: str, github_mirror: str) -> Request:
    resolved_url = resolve_download_url(url, github_mirror)
    if resolved_url != url:
        logger.info("Use GitHub mirror: url=%s", resolved_url)
    return Request(resolved_url, headers={"User-Agent": USER_AGENT})


def download_json(
    url: str,
    github_mirror: str = GITHUB_HOST,
) -> dict[str, Any]:
    """Download a JSON object after resolving its GitHub mirror URL."""
    with urlopen(
        _download_request(url, github_mirror),
        timeout=DOWNLOAD_TIMEOUT_SECONDS,
    ) as response:
        payload = response.read(MAX_JSON_BYTES + 1)
    if len(payload) > MAX_JSON_BYTES:
        raise ValueError(
            f"JSON download exceeds limit of {_format_size(MAX_JSON_BYTES)}: {url}"
        )
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError(f"Downloaded JSON must be an object: {url}")
    return data


def _format_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{size} B"
        value /= 1024
    raise AssertionError("unreachable")


def _download_progress_message(
    target_path: str | Path,
    downloaded_size: int,
    total_size: int,
) -> str:
    percentage = min(downloaded_size * 100 // total_size, 100)
    return (
        f"Downloading {Path(target_path).name}: {percentage:3d}% "
        f"({_format_size(downloaded_size)} / {_format_size(total_size)})"
    )


def download_file(
    url: str,
    target_path: str | Path,
    github_mirror: str = GITHUB_HOST,
) -> None:
    request = _download_request(url, github_mirror)
    with (
        urlopen(
            request,
            timeout=DOWNLOAD_TIMEOUT_SECONDS,
        ) as response,
        Path(target_path).open("wb") as output,
    ):
        downloaded_size = 0
        try:
            total_size = int(response.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            total_size = 0
        if total_size > MAX_DOWNLOAD_BYTES:
            raise OSError(
                "Declared download size exceeds limit: "
                f"{_format_size(total_size)} > {_format_size(MAX_DOWNLOAD_BYTES)}"
            )
        last_percentage = -1
        progress_message: str | None = None
        if total_size > 0:
            progress_message = _download_progress_message(target_path, 0, total_size)
            log_progress(progress_message)
            last_percentage = 0
        try:
            while chunk := response.read(8192):
                downloaded_size += len(chunk)
                if downloaded_size > MAX_DOWNLOAD_BYTES:
                    raise OSError(
                        "Downloaded file exceeds limit of "
                        f"{_format_size(MAX_DOWNLOAD_BYTES)}"
                    )
                output.write(chunk)
                if total_size <= 0:
                    continue
                percentage = min(downloaded_size * 100 // total_size, 100)
                if percentage == last_percentage or percentage == 100:
                    continue
                last_percentage = percentage
                progress_message = _download_progress_message(
                    target_path,
                    downloaded_size,
                    total_size,
                )
                log_progress(progress_message)
            if total_size > 0 and downloaded_size != total_size:
                raise OSError(
                    "Downloaded file size does not match Content-Length: "
                    f"expected {total_size} bytes, received {downloaded_size} bytes"
                )
        finally:
            if total_size > 0:
                progress_message = _download_progress_message(
                    target_path,
                    downloaded_size,
                    total_size,
                )
                log_progress(progress_message, complete=True)
    logger.info("Downloaded file: path=%s, bytes=%s", target_path, downloaded_size)


def resolve_cached_download(
    name: str,
    target_path: str | Path,
    url: str | None,
    github_mirror: str = GITHUB_HOST,
    *,
    path_in_archive: str | None = None,
) -> Path:
    """Return a cached file or atomically populate it from a file or 7z URL."""
    target = Path(target_path)
    if target.is_file():
        return target
    if not url:
        raise FileNotFoundError(f"{name} not found: {target}")

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = target.with_name(f".{target.name}.download")
    temporary_path.unlink(missing_ok=True)
    is_archive = False
    try:
        try:
            download_file(url, temporary_path, github_mirror)
        except Exception as error:
            raise DownloadError(
                f"Failed to download {name} from {url}: {error}"
            ) from error
        is_archive = py7zr.is_7zfile(temporary_path)
        if is_archive:
            if path_in_archive is None:
                raise ArchiveError(
                    "download.path_in_archive is required for a 7z archive"
                )
            archive_path = validate_archive_path(path_in_archive)
            with tempfile.TemporaryDirectory(
                prefix=f".{target.name}.extract-",
                dir=target.parent,
            ) as extract_tmp:
                extract_dir = Path(extract_tmp)
                with py7zr.SevenZipFile(temporary_path, mode="r") as archive:
                    members = archive.list()
                    if len(members) > MAX_ARCHIVE_MEMBERS:
                        raise ArchiveError(
                            "7z archive exceeds member limit: "
                            f"{len(members)} > {MAX_ARCHIVE_MEMBERS}"
                        )
                    matches = [
                        member for member in members if member.filename == archive_path
                    ]
                    if len(matches) != 1:
                        raise ArchiveMemberNotFoundError(
                            "download.path_in_archive must match exactly one archive "
                            f"member: {archive_path!r} matched {len(matches)}"
                        )
                    if not matches[0].is_file or matches[0].is_symlink:
                        raise ArchiveError(
                            "download.path_in_archive must select a regular file: "
                            f"{archive_path!r}"
                        )
                    extracted_size = matches[0].uncompressed
                    if (
                        not isinstance(extracted_size, int)
                        or extracted_size < 0
                        or extracted_size > MAX_EXTRACTED_BYTES
                    ):
                        raise ArchiveError(
                            "Selected 7z member exceeds extracted size limit: "
                            f"{archive_path!r}"
                        )
                    archive.extract(path=extract_dir, targets=[archive_path])
                extracted_path = extract_dir.joinpath(*archive_path.split("/"))
                if not extracted_path.is_file():
                    raise ArchiveError(
                        f"extracted archive member is not a file: {archive_path!r}"
                    )
                if extracted_path.stat().st_size > MAX_EXTRACTED_BYTES:
                    raise ArchiveError(
                        "Selected 7z member exceeds extracted size limit: "
                        f"{archive_path!r}"
                    )
                extracted_path.replace(target)
        else:
            if path_in_archive is not None:
                raise ArchiveError(
                    "download.path_in_archive is only valid for a 7z archive"
                )
            temporary_path.replace(target)
    except (DownloadError, ArchiveError):
        temporary_path.unlink(missing_ok=True)
        raise
    except Exception as error:
        temporary_path.unlink(missing_ok=True)
        if is_archive:
            raise ArchiveError(
                f"Failed to extract {name} to {target}: {error}"
            ) from error
        raise DownloadError(
            f"Failed to finalize {name} at {target}: {error}"
        ) from error
    temporary_path.unlink(missing_ok=True)
    return target


def validate_archive_path(value: str) -> str:
    """Validate a slash-separated file path relative to an archive root."""
    if not value or value != value.strip():
        raise ValueError("must be a non-empty path without surrounding whitespace")
    if "\\" in value:
        raise ValueError("must use '/' as the path separator")
    if value.startswith("/") or PureWindowsPath(value).drive:
        raise ValueError("must be relative to the archive root")
    if any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError("must not contain empty, '.' or '..' path segments")
    return value


def _validate_zip_resources(zip_file: ZipFile) -> None:
    members = zip_file.infolist()
    if len(members) > MAX_ARCHIVE_MEMBERS:
        raise ValueError(
            f"ZIP archive exceeds member limit: {len(members)} > {MAX_ARCHIVE_MEMBERS}"
        )
    extracted_size = sum(member.file_size for member in members)
    if extracted_size > MAX_EXTRACTED_BYTES:
        raise ValueError(
            "ZIP archive exceeds extracted size limit: "
            f"{_format_size(extracted_size)} > "
            f"{_format_size(MAX_EXTRACTED_BYTES)}"
        )


def download_zip_and_extract(
    name: str,
    url: str | None,
    zip_path: str | Path,
    output_dir: str | Path,
    remove_zip: bool = False,
    github_mirror: str = GITHUB_HOST,
) -> bool:
    archive_path = Path(zip_path)
    if archive_path.exists():
        try:
            with ZipFile(archive_path, "r") as zip_file:
                if zip_file.testzip() is not None:
                    raise ValueError("archive contains a corrupt member")
                _validate_zip_resources(zip_file)
        except Exception:
            logger.warning("Remove invalid cached archive: path=%s", archive_path)
            archive_path.unlink(missing_ok=True)

    if not archive_path.exists():
        if url is None:
            return False
        logger.info("Download archive: name=%s, url=%s", name, url)
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_archive = archive_path.with_name(f".{archive_path.name}.download")
        temporary_archive.unlink(missing_ok=True)
        try:
            download_file(url, temporary_archive, github_mirror)
            with ZipFile(temporary_archive, "r") as zip_file:
                if zip_file.testzip() is not None:
                    raise ValueError("downloaded archive contains a corrupt member")
                _validate_zip_resources(zip_file)
            temporary_archive.replace(archive_path)
        except Exception as error:
            temporary_archive.unlink(missing_ok=True)
            logger.error(
                "Failed to download archive: name=%s, url=%s, error=%s",
                name,
                url,
                error,
            )
            return False

    output_path = Path(output_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(
            prefix=f".{output_path.name}.extract-",
            dir=output_path.parent,
        ) as temporary_dir:
            temporary_output = Path(temporary_dir)
            with ZipFile(archive_path, "r") as zip_file:
                _validate_zip_resources(zip_file)
                for member in zip_file.infolist():
                    member_path = PurePosixPath(member.filename)
                    if member_path.is_absolute() or ".." in member_path.parts:
                        raise ValueError(
                            f"archive member escapes extraction root: {member.filename}"
                        )
                zip_file.extractall(temporary_output)
            if output_path.exists():
                shutil.rmtree(output_path)
            temporary_output.replace(output_path)
        if remove_zip:
            archive_path.unlink()
        return True
    except Exception as error:
        shutil.rmtree(output_path, ignore_errors=True)
        archive_path.unlink(missing_ok=True)
        logger.error("Failed to extract archive: name=%s, error=%s", name, error)
        return False


def check_font_patcher(
    version: str,
    github_mirror: str = GITHUB_HOST,
    target_dir: str | Path = "FontPatcher",
) -> bool:
    target_path = Path(target_dir)
    patcher_path = target_path / "font-patcher"
    if target_path.exists():
        if f"# Nerd Fonts Version: {version}" in patcher_path.read_text(
            encoding="utf-8"
        ):
            return True
        logger.info("Remove mismatched FontPatcher version: path=%s", target_path)
        shutil.rmtree(target_path, ignore_errors=True)

    zip_path = Path("FontPatcher.zip")
    url = (
        "https://github.com/ryanoasis/nerd-fonts/releases/"
        f"download/v{version}/{zip_path.name}"
    )
    if not download_zip_and_extract(
        name="Nerd Font Patcher",
        url=url,
        zip_path=zip_path,
        output_dir=target_path,
        github_mirror=github_mirror,
    ):
        return False

    if f"# Nerd Fonts Version: {version}" in patcher_path.read_text(encoding="utf-8"):
        return True

    logger.error("FontPatcher version mismatch: version=%s, url=%s", version, url)
    return False
