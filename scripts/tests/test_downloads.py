from __future__ import annotations

import json
import os
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import py7zr

from scripts.errors import DownloadError
from scripts.utils.downloads import (
    download_file,
    download_json,
    download_zip_and_extract,
    github_mirror_from_config,
    resolve_cached_download,
    resolve_download_url,
    validate_archive_path,
)


class FakeResponse:
    def __init__(self, payload: bytes, content_length: str | None) -> None:
        self._stream = BytesIO(payload)
        self.headers = {}
        if content_length is not None:
            self.headers["Content-Length"] = content_length

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        self._stream.close()

    def read(self, size: int) -> bytes:
        return self._stream.read(size)


class DownloadProgressTest(unittest.TestCase):
    def test_passes_socket_timeout_to_urlopen(self) -> None:
        response = FakeResponse(b"font data", "9")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "font.ttf"
            with patch(
                "scripts.utils.downloads.urlopen",
                return_value=response,
            ) as urlopen:
                download_file("https://example.com/font.ttf", target)

        self.assertEqual(urlopen.call_args.kwargs, {"timeout": 60})

    def test_accepts_matching_content_length(self) -> None:
        payload = b"font data"
        response = FakeResponse(payload, str(len(payload)))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "font.ttf"
            with patch("scripts.utils.downloads.urlopen", return_value=response):
                download_file("https://example.com/font.ttf", target)

            self.assertEqual(target.read_bytes(), payload)

    def test_reports_percentage_progress_on_one_terminal_line(self) -> None:
        payload = b"a" * 16384
        response = FakeResponse(payload, str(len(payload)))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "archive.zip"
            with (
                patch("scripts.utils.downloads.urlopen", return_value=response),
                patch("scripts.utils.downloads.log_progress") as progress,
            ):
                download_file("https://example.com/archive.zip", target)

            self.assertEqual(target.read_bytes(), payload)
            messages = [call.args[0] for call in progress.call_args_list]
            self.assertIn("archive.zip:   0%", messages[0])
            self.assertIn("archive.zip:  50%", messages[1])
            self.assertIn("archive.zip: 100%", messages[2])
            self.assertEqual(progress.call_args_list[-1].kwargs, {"complete": True})

    def test_skips_percentage_when_content_length_is_unavailable(self) -> None:
        for content_length in (None, "unknown"):
            with self.subTest(content_length=content_length):
                response = FakeResponse(b"font data", content_length)
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp) / "font.ttf"
                    with (
                        patch("scripts.utils.downloads.urlopen", return_value=response),
                        patch("scripts.utils.downloads.log_progress") as progress,
                    ):
                        download_file("https://example.com/font.ttf", target)

                    progress.assert_not_called()

    def test_accepts_unknown_content_length(self) -> None:
        payload = b"font data"
        response = FakeResponse(payload, "unknown")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "font.ttf"
            with patch("scripts.utils.downloads.urlopen", return_value=response):
                download_file("https://example.com/font.ttf", target)

            self.assertEqual(target.read_bytes(), payload)

    def test_rejects_declared_download_over_limit_and_cleans_up(self) -> None:
        response = FakeResponse(b"", "5")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "font.ttf"
            with (
                patch("scripts.utils.downloads.MAX_DOWNLOAD_BYTES", 4),
                patch("scripts.utils.downloads.urlopen", return_value=response),
                self.assertRaisesRegex(FileNotFoundError, "exceeds limit"),
            ):
                resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.ttf",
                )

            self.assertFalse(target.exists())
            self.assertFalse((target.parent / ".font.ttf.download").exists())

    def test_rejects_streamed_download_over_limit_and_cleans_up(self) -> None:
        response = FakeResponse(b"12345", None)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "font.ttf"
            with (
                patch("scripts.utils.downloads.MAX_DOWNLOAD_BYTES", 4),
                patch("scripts.utils.downloads.urlopen", return_value=response),
                self.assertRaisesRegex(FileNotFoundError, "exceeds limit"),
            ):
                resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.ttf",
                )

            self.assertFalse(target.exists())
            self.assertFalse((target.parent / ".font.ttf.download").exists())

    def test_rejects_json_over_limit(self) -> None:
        response = FakeResponse(b'{"value": 1}', None)
        with (
            patch("scripts.utils.downloads.MAX_JSON_BYTES", 4),
            patch(
                "scripts.utils.downloads.urlopen",
                return_value=response,
            ) as urlopen,
            self.assertRaisesRegex(ValueError, "JSON download exceeds limit"),
        ):
            download_json("https://example.com/data.json")

        self.assertEqual(urlopen.call_args.kwargs, {"timeout": 60})


class DownloadUrlResolutionTest(unittest.TestCase):
    def test_resolves_github_release_through_mirror(self) -> None:
        url = "https://github.com/owner/repository/releases/download/v1/font.ttf"

        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                resolve_download_url(url, "github.example.com"),
                "https://github.example.com/owner/repository/releases/download/v1/font.ttf",
            )

    def test_resolves_github_raw_url_through_mirror(self) -> None:
        url = "https://raw.githubusercontent.com/owner/repository/v1/font.ttf"

        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                resolve_download_url(url, "github.example.com"),
                "https://github.example.com/owner/repository/raw/v1/font.ttf",
            )

    def test_normalizes_github_raw_url_without_mirror(self) -> None:
        url = "https://raw.githubusercontent.com/owner/repository/v1/font.ttf"

        with patch.dict(os.environ, {}, clear=True):
            resolved = resolve_download_url(url)

        self.assertEqual(
            resolved,
            "https://github.com/owner/repository/raw/v1/font.ttf",
        )

    def test_leaves_non_github_url_unchanged(self) -> None:
        url = "https://example.com/font.ttf"

        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(resolve_download_url(url, "github.example.com"), url)

    def test_preserves_mirror_path_prefix(self) -> None:
        url = "https://github.com/owner/repository/releases/download/v1/font.ttf"

        with patch.dict(os.environ, {}, clear=True):
            resolved = resolve_download_url(
                url,
                "github.example.com/github.com",
            )

        self.assertEqual(
            resolved,
            "https://github.example.com/github.com/owner/repository/releases/download/v1/font.ttf",
        )

    def test_environment_mirror_overrides_configured_mirror(self) -> None:
        url = "https://github.com/owner/repository/releases/download/v1/font.ttf"

        with patch.dict(os.environ, {"GITHUB": "env.example.com"}):
            resolved = resolve_download_url(url, "config.example.com")

        self.assertEqual(
            resolved,
            "https://env.example.com/owner/repository/releases/download/v1/font.ttf",
        )

    def test_reads_task_mirror_from_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            config_path.write_text(
                json.dumps({"github_mirror": "config.example.com"}),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(
                    github_mirror_from_config(config_path),
                    "config.example.com",
                )


class CachedDownloadTest(unittest.TestCase):
    def test_rejects_mismatched_content_length_and_cleans_up(self) -> None:
        for payload in (b"short", b"longer than expected"):
            with (
                self.subTest(received_size=len(payload)),
                tempfile.TemporaryDirectory() as tmp,
            ):
                target = Path(tmp) / "font.ttf"
                response = FakeResponse(payload, "10")
                with (
                    patch("scripts.utils.downloads.urlopen", return_value=response),
                    self.assertRaisesRegex(
                        FileNotFoundError,
                        rf"expected 10 bytes, received {len(payload)} bytes",
                    ),
                ):
                    resolve_cached_download(
                        "font",
                        target,
                        "https://example.com/font.ttf",
                    )

                self.assertFalse(target.exists())
                self.assertFalse((target.parent / ".font.ttf.download").exists())

    def test_reuses_existing_file_without_downloading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "font.ttf"
            target.write_bytes(b"cached")

            with patch("scripts.utils.downloads.download_file") as download:
                resolved = resolve_cached_download(
                    "font", target, "https://example.com/font.ttf"
                )

            self.assertEqual(resolved, target)
            download.assert_not_called()

    def test_downloads_missing_file_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "cache" / "font.ttf"

            def fake_download(
                url: str,
                temporary_path: str | Path,
                github_mirror: str,
            ) -> None:
                self.assertEqual(url, "https://example.com/font.ttf")
                self.assertEqual(github_mirror, "github.example.com")
                Path(temporary_path).write_bytes(b"downloaded")

            with patch(
                "scripts.utils.downloads.download_file", side_effect=fake_download
            ):
                resolved = resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.ttf",
                    "github.example.com",
                )

            self.assertEqual(resolved, target)
            self.assertEqual(target.read_bytes(), b"downloaded")
            self.assertFalse((target.parent / ".font.ttf.download").exists())

    def test_plain_file_finalization_failure_is_a_download_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "font.ttf"

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                Path(temporary_path).write_bytes(b"downloaded")

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=fake_download,
                ),
                patch.object(Path, "replace", side_effect=OSError("disk full")),
                self.assertRaisesRegex(
                    DownloadError,
                    "Failed to finalize font.*disk full",
                ),
            ):
                resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.ttf",
                )

            self.assertFalse(target.exists())
            self.assertFalse((target.parent / ".font.ttf.download").exists())

    def test_missing_file_without_url_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "font.ttf"

            with self.assertRaisesRegex(FileNotFoundError, "font not found"):
                resolve_cached_download("font", target, None)

    def test_download_failure_removes_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "font.ttf"

            def fail_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                Path(temporary_path).write_bytes(b"partial")
                raise OSError("network unavailable")

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=fail_download,
                ),
                self.assertRaisesRegex(FileNotFoundError, "Failed to download font"),
            ):
                resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.ttf",
                )

            self.assertFalse(target.exists())
            self.assertFalse((target.parent / ".font.ttf.download").exists())

    def test_extracts_selected_file_from_7z_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "cache" / "font.otf"
            payload = root / "payload.otf"
            payload.write_bytes(b"font data")

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                with py7zr.SevenZipFile(temporary_path, mode="w") as archive:
                    archive.write(payload, "fonts/font.otf")

            with patch(
                "scripts.utils.downloads.download_file",
                side_effect=fake_download,
            ):
                resolved = resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.bin",
                    path_in_archive="fonts/font.otf",
                )

            self.assertEqual(resolved, target)
            self.assertEqual(target.read_bytes(), b"font data")
            self.assertEqual(list(target.parent.glob(".font.otf.*")), [])

    def test_7z_archive_requires_selected_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "font.otf"
            payload = root / "payload.otf"
            payload.write_bytes(b"font data")

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                with py7zr.SevenZipFile(temporary_path, mode="w") as archive:
                    archive.write(payload, "font.otf")

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=fake_download,
                ),
                self.assertRaisesRegex(
                    FileNotFoundError, "path_in_archive is required"
                ),
            ):
                resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.7z",
                )

            self.assertFalse(target.exists())
            self.assertFalse((root / ".font.otf.download").exists())

    def test_rejects_archive_path_for_direct_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "font.otf"

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                Path(temporary_path).write_bytes(b"font data")

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=fake_download,
                ),
                self.assertRaisesRegex(FileNotFoundError, "only valid for a 7z"),
            ):
                resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.otf",
                    path_in_archive="font.otf",
                )

            self.assertFalse(target.exists())

    def test_rejects_missing_archive_member_and_cleans_up(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "font.otf"
            payload = root / "payload.otf"
            payload.write_bytes(b"font data")

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                with py7zr.SevenZipFile(temporary_path, mode="w") as archive:
                    archive.write(payload, "other.otf")

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=fake_download,
                ),
                self.assertRaisesRegex(FileNotFoundError, "matched 0"),
            ):
                resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.7z",
                    path_in_archive="font.otf",
                )

            self.assertFalse(target.exists())
            self.assertEqual(list(root.glob(".font.otf.*")), [])

    def test_rejects_7z_archives_over_member_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "font.otf"
            payload = root / "payload.otf"
            payload.write_bytes(b"font data")

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                with py7zr.SevenZipFile(temporary_path, mode="w") as archive:
                    archive.write(payload, "font.otf")

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=fake_download,
                ),
                patch("scripts.utils.downloads.MAX_ARCHIVE_MEMBERS", 0),
                self.assertRaisesRegex(FileNotFoundError, "member limit"),
            ):
                resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.7z",
                    path_in_archive="font.otf",
                )

            self.assertFalse(target.exists())
            self.assertEqual(list(root.glob(".font.otf.*")), [])

    def test_rejects_selected_7z_member_over_size_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "font.otf"
            payload = root / "payload.otf"
            payload.write_bytes(b"font data")

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                with py7zr.SevenZipFile(temporary_path, mode="w") as archive:
                    archive.write(payload, "font.otf")

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=fake_download,
                ),
                patch("scripts.utils.downloads.MAX_EXTRACTED_BYTES", 4),
                self.assertRaisesRegex(FileNotFoundError, "extracted size limit"),
            ):
                resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.7z",
                    path_in_archive="font.otf",
                )

            self.assertFalse(target.exists())
            self.assertEqual(list(root.glob(".font.otf.*")), [])


class ZipDownloadTest(unittest.TestCase):
    def test_replaces_corrupt_cached_archive_before_extracting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_path = root / "cache.zip"
            archive_path.write_bytes(b"partial")
            output_dir = root / "output"

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                with ZipFile(temporary_path, "w") as archive:
                    archive.writestr("font.ttf", b"font")

            with patch(
                "scripts.utils.downloads.download_file",
                side_effect=fake_download,
            ) as download:
                result = download_zip_and_extract(
                    "font cache",
                    "https://example.com/cache.zip",
                    archive_path,
                    output_dir,
                )

            self.assertTrue(result)
            download.assert_called_once()
            self.assertEqual((output_dir / "font.ttf").read_bytes(), b"font")

    def test_failed_download_does_not_leave_archive_or_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_path = root / "cache.zip"
            output_dir = root / "output"

            def fail_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                Path(temporary_path).write_bytes(b"partial")
                raise OSError("network unavailable")

            with patch(
                "scripts.utils.downloads.download_file",
                side_effect=fail_download,
            ):
                result = download_zip_and_extract(
                    "font cache",
                    "https://example.com/cache.zip",
                    archive_path,
                    output_dir,
                )

            self.assertFalse(result)
            self.assertFalse(archive_path.exists())
            self.assertFalse(output_dir.exists())

    def test_rejects_zip_archives_over_member_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_path = root / "cache.zip"
            output_dir = root / "output"

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                with ZipFile(temporary_path, "w") as archive:
                    archive.writestr("font.ttf", b"font")

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=fake_download,
                ),
                patch("scripts.utils.downloads.MAX_ARCHIVE_MEMBERS", 0),
            ):
                result = download_zip_and_extract(
                    "font cache",
                    "https://example.com/cache.zip",
                    archive_path,
                    output_dir,
                )

            self.assertFalse(result)
            self.assertFalse(archive_path.exists())
            self.assertFalse(output_dir.exists())

    def test_rejects_zip_archives_over_extracted_size_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_path = root / "cache.zip"
            output_dir = root / "output"

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                with ZipFile(temporary_path, "w") as archive:
                    archive.writestr("font.ttf", b"font")

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=fake_download,
                ),
                patch("scripts.utils.downloads.MAX_EXTRACTED_BYTES", 3),
            ):
                result = download_zip_and_extract(
                    "font cache",
                    "https://example.com/cache.zip",
                    archive_path,
                    output_dir,
                )

            self.assertFalse(result)
            self.assertFalse(archive_path.exists())
            self.assertFalse(output_dir.exists())

    def test_rejects_duplicate_archive_members(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "font.otf"
            payload = root / "payload.otf"
            payload.write_bytes(b"font data")

            def fake_download(
                _url: str,
                temporary_path: str | Path,
                _github_mirror: str,
            ) -> None:
                with py7zr.SevenZipFile(temporary_path, mode="w") as archive:
                    archive.write(payload, "font.otf")
                    archive.write(payload, "font.otf")

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=fake_download,
                ),
                self.assertRaisesRegex(FileNotFoundError, "matched 2"),
            ):
                resolve_cached_download(
                    "font",
                    target,
                    "https://example.com/font.7z",
                    path_in_archive="font.otf",
                )

            self.assertFalse(target.exists())
            self.assertEqual(list(root.glob(".font.otf.*")), [])


class ArchivePathValidationTest(unittest.TestCase):
    def test_accepts_relative_slash_separated_file_path(self) -> None:
        self.assertEqual(
            validate_archive_path("fonts/cjk/font.otf"),
            "fonts/cjk/font.otf",
        )

    def test_rejects_unsafe_or_ambiguous_paths(self) -> None:
        for path in ("", " font.otf", "/font.otf", "C:/font.otf", "a//b", "a/../b"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_archive_path(path)


if __name__ == "__main__":
    unittest.main()
