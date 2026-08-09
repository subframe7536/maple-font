from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path
from stat import S_IMODE
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.task import cjk, nf


class TaskDownloadMirrorTest(unittest.TestCase):
    def test_cjk_cache_validate_task_verifies_archive_and_hash(self) -> None:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        cjk.register_parser(subparsers)
        args = parser.parse_args(
            [
                "cjk",
                "cache-validate",
                "--archive",
                "archive.zip",
                "--hash",
                "static.sha256",
            ]
        )

        with patch("scripts.task.cjk.verify_static_archive") as verify:
            cjk.run(args)

        verify.assert_called_once_with(Path("archive.zip"), Path("static.sha256"))

    def test_cjk_cache_validate_task_selects_variable_archive_validator(self) -> None:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        cjk.register_parser(subparsers)
        args = parser.parse_args(
            [
                "cjk",
                "cache-validate",
                "--archive",
                "archive.zip",
                "--hash",
                "variable.sha256",
                "--kind",
                "variable",
            ]
        )

        with patch("scripts.task.cjk.verify_variable_archive") as verify:
            cjk.run(args)

        verify.assert_called_once_with(Path("archive.zip"), Path("variable.sha256"))

    def test_cjk_task_builds_comma_separated_presets_independently(self) -> None:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        cjk.register_parser(subparsers)
        args = parser.parse_args(["cjk", "--preset", "cn,tc,jp,kr", "--vf-only"])

        with (
            patch(
                "scripts.task.cjk.github_mirror_from_config",
                return_value="mirror.example.com/github.com",
            ),
            patch("scripts.task.cjk.build_cjk_fonts") as build,
        ):
            cjk.run(args)

        self.assertEqual(
            [call.args[0].locale_name for call in build.call_args_list],
            ["CN", "TC", "JP", "KR"],
        )
        self.assertTrue(all(call.args[2] for call in build.call_args_list))
        self.assertTrue(
            all(
                call.kwargs["github_mirror"] == "mirror.example.com/github.com"
                for call in build.call_args_list
            )
        )

    def test_cjk_task_passes_configured_mirror_to_builder(self) -> None:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        cjk.register_parser(subparsers)
        args = parser.parse_args(["cjk", "--preset", "cn", "--vf-only"])

        with (
            patch(
                "scripts.task.cjk.github_mirror_from_config",
                return_value="mirror.example.com/github.com",
            ),
            patch("scripts.task.cjk.build_cjk_fonts") as build,
        ):
            cjk.run(args)

        self.assertEqual(
            build.call_args.kwargs["github_mirror"],
            "mirror.example.com/github.com",
        )

    def test_nerd_font_task_updates_config_and_passes_configured_mirror_to_download(
        self,
    ) -> None:
        with TemporaryDirectory() as directory:
            config_path = self.write_config(Path(directory), "3.2.0")

            with (
                patch(
                    "scripts.task.nf.github_mirror_from_config",
                    return_value="mirror.example.com/github.com",
                ),
                patch(
                    "scripts.task.nf.download_json",
                    return_value={"tag_name": "v3.2.1"},
                ) as download_metadata,
                patch("scripts.task.nf.check_font_patcher", return_value=True) as check,
            ):
                nf.check_update(str(config_path))

            self.assertEqual(self.read_version(config_path), "3.2.1")
            check.assert_called_once()
            self.assertEqual(check.call_args.args[1], "mirror.example.com/github.com")
            self.assertEqual(
                download_metadata.call_args.args[1],
                "mirror.example.com/github.com",
            )

    def test_nerd_font_task_keeps_current_config_bytes_unchanged(self) -> None:
        with TemporaryDirectory() as directory:
            config_path = self.write_config(Path(directory), "3.2.1")
            original_bytes = config_path.read_bytes()

            with (
                patch(
                    "scripts.task.nf.github_mirror_from_config",
                    return_value="github.com",
                ),
                patch(
                    "scripts.task.nf.download_json",
                    return_value={"tag_name": "v3.2.1"},
                ),
                patch("scripts.task.nf.check_font_patcher", return_value=True),
            ):
                nf.check_update(str(config_path))

            self.assertEqual(config_path.read_bytes(), original_bytes)

    def test_update_config_json_replaces_shorter_version_without_stale_bytes(
        self,
    ) -> None:
        with TemporaryDirectory() as directory:
            config_path = self.write_config(Path(directory), "3.2.1000")

            nf.update_config_json(str(config_path), "3.2.1")

            self.assertEqual(self.read_version(config_path), "3.2.1")
            self.assertEqual(config_path.read_text(encoding="utf-8")[-1], "\n")

    def test_update_config_json_preserves_file_permissions(self) -> None:
        with TemporaryDirectory() as directory:
            config_path = self.write_config(Path(directory), "3.2.0")
            config_path.chmod(0o640)
            original_mode = S_IMODE(config_path.stat().st_mode)

            nf.update_config_json(str(config_path), "3.2.1")

            self.assertEqual(S_IMODE(config_path.stat().st_mode), original_mode)

    def test_update_config_json_fails_clearly_for_missing_or_invalid_config(
        self,
    ) -> None:
        with TemporaryDirectory() as directory:
            directory_path = Path(directory)
            missing_path = directory_path / "missing.json"
            invalid_path = directory_path / "invalid.json"
            invalid_path.write_text("[]", encoding="utf-8")

            with self.assertRaises(FileNotFoundError):
                nf.update_config_json(str(missing_path), "3.2.1")
            with self.assertRaisesRegex(ValueError, "expected an object"):
                nf.update_config_json(str(invalid_path), "3.2.1")

    @staticmethod
    def write_config(directory: Path, version: str) -> Path:
        config_path = directory / "config.json"
        config_path.write_text(
            json.dumps({"nerd_font": {"version": version}}, indent=2) + "\n",
            encoding="utf-8",
        )
        return config_path

    @staticmethod
    def read_version(config_path: Path) -> str:
        return json.loads(config_path.read_text(encoding="utf-8"))["nerd_font"][
            "version"
        ]


if __name__ == "__main__":
    unittest.main()
