from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from scripts.config.paths import static_output_dir, variable_output_dir
from scripts.utils.files import archive_fonts, archive_output_label


class FontArchiveTest(unittest.TestCase):
    def test_variable_output_labels_use_vf_suffix(self) -> None:
        self.assertEqual(archive_output_label("Variable"), "VF")
        self.assertEqual(archive_output_label("Variable-NF"), "NF-VF")
        self.assertEqual(archive_output_label("Variable-NF-CN"), "NF-CN-VF")
        self.assertEqual(archive_output_label("NF-CN"), "NF-CN")
        self.assertEqual(archive_output_label("NFMono"), "NFMono")
        self.assertEqual(archive_output_label("Variable-NFMono"), "NFMono-VF")
        self.assertEqual(archive_output_label("NFMono-CN"), "NFMono-CN")
        self.assertEqual(archive_output_label("Variable-NFPropo-CN"), "NFPropo-CN-VF")

    def test_output_dirs_preserve_variant_casing(self) -> None:
        root = Path("fonts")
        self.assertEqual(static_output_dir(root, "CN"), root / "CN")
        self.assertEqual(static_output_dir(root, "NFMono-CN"), root / "NFMono-CN")
        self.assertEqual(variable_output_dir(root, "JP"), root / "Variable-JP")
        self.assertEqual(
            variable_output_dir(root, "NFPropo-CN"),
            root / "Variable-NFPropo-CN",
        )

    def test_archive_readme_links_only_relative_font_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "Variable-NF-CN"
            source.mkdir()
            (source / "MapleMono-NF-CN[wght].ttf").write_bytes(b"font")
            (source / "README.md").write_text("stale", encoding="utf-8")
            config = root / "build-config.json"
            config.write_text("{}", encoding="utf-8")
            target = root / "archive"
            target.mkdir()

            _, name = archive_fonts(
                source_file_or_dir_path=str(source),
                target_parent_dir_path=str(target),
                family_name_compact="MapleMonoNR",
                suffix="",
                build_config_path=str(config),
            )

            self.assertEqual(name, "MapleMonoNR-NF-CN-VF")
            with ZipFile(target / f"{name}.zip") as archive:
                readme = archive.read("README.md").decode("utf-8")
                self.assertIn(
                    "[MapleMono-NF-CN[wght].ttf](./MapleMono-NF-CN%5Bwght%5D.ttf)",
                    readme,
                )
                self.assertNotIn("stale", readme)
                self.assertNotIn("config.json", archive.namelist())

    def test_archive_requires_a_source_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "issue.fea"
            source.write_text("feature liga {} liga;", encoding="utf-8")
            target = root / "archive"
            target.mkdir()
            config = root / "build-config.json"
            config.write_text("{}", encoding="utf-8")

            with self.assertRaisesRegex(NotADirectoryError, "archive source"):
                archive_fonts(
                    source_file_or_dir_path=str(source),
                    target_parent_dir_path=str(target),
                    family_name_compact="MapleMono",
                    suffix="",
                    build_config_path=str(config),
                )

    def test_archive_bytes_ignore_source_mtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "TTF"
            source.mkdir()
            font = source / "MapleMono-Regular.ttf"
            font.write_bytes(b"font")
            config = root / "build-config.json"
            config.write_text("{}", encoding="utf-8")
            target = root / "archive"
            target.mkdir()

            with patch.dict(os.environ, {"SOURCE_DATE_EPOCH": "946684800"}):
                digest_before, name = archive_fonts(
                    source_file_or_dir_path=str(source),
                    target_parent_dir_path=str(target),
                    family_name_compact="MapleMono",
                    suffix="",
                    build_config_path=str(config),
                )
                archive_path = target / f"{name}.zip"
                bytes_before = archive_path.read_bytes()

                os.utime(font, (1_700_000_000, 1_700_000_000))
                digest_after, _ = archive_fonts(
                    source_file_or_dir_path=str(source),
                    target_parent_dir_path=str(target),
                    family_name_compact="MapleMono",
                    suffix="",
                    build_config_path=str(config),
                )

            self.assertEqual(digest_after, digest_before)
            self.assertEqual(archive_path.read_bytes(), bytes_before)

    def test_archive_bytes_ignore_source_creation_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_bytes: list[bytes] = []
            for index, file_names in enumerate(
                (
                    ("nested/MapleMono-Bold.ttf", "MapleMono-Regular.ttf"),
                    ("MapleMono-Regular.ttf", "nested/MapleMono-Bold.ttf"),
                )
            ):
                case_root = root / str(index)
                source = case_root / "TTF"
                target = case_root / "archive"
                target.mkdir(parents=True)
                for file_name in file_names:
                    font_path = source / file_name
                    font_path.parent.mkdir(parents=True, exist_ok=True)
                    font_path.write_bytes(file_name.encode())
                config = case_root / "build-config.json"
                config.write_text("{}", encoding="utf-8")

                _, name = archive_fonts(
                    source_file_or_dir_path=source,
                    target_parent_dir_path=str(target),
                    family_name_compact="MapleMono",
                    suffix="",
                    build_config_path=str(config),
                )
                archive_bytes.append((target / f"{name}.zip").read_bytes())

            self.assertEqual(archive_bytes[0], archive_bytes[1])

    def test_source_date_epoch_controls_every_archive_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "Variable"
            source.mkdir()
            (source / "MapleMono[wght].ttf").write_bytes(b"font")
            config = root / "build-config.json"
            config.write_text("{}", encoding="utf-8")
            target = root / "archive"
            target.mkdir()

            with patch.dict(os.environ, {"SOURCE_DATE_EPOCH": "946684800"}):
                _, name = archive_fonts(
                    source_file_or_dir_path=str(source),
                    target_parent_dir_path=str(target),
                    family_name_compact="MapleMono",
                    suffix="",
                    build_config_path=str(config),
                )

            with ZipFile(target / f"{name}.zip") as archive:
                self.assertEqual(
                    {info.date_time for info in archive.infolist()},
                    {(2000, 1, 1, 0, 0, 0)},
                )
                self.assertEqual(archive.namelist(), sorted(archive.namelist()))
                self.assertEqual(
                    {(info.external_attr >> 16) & 0o777 for info in archive.infolist()},
                    {0o644},
                )

    def test_source_date_epoch_rejects_invalid_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "Variable"
            source.mkdir()
            (source / "MapleMono[wght].ttf").write_bytes(b"font")
            config = root / "build-config.json"
            config.write_text("{}", encoding="utf-8")
            target = root / "archive"
            target.mkdir()

            for value in ("invalid", "-1"):
                with (
                    self.subTest(value=value),
                    patch.dict(os.environ, {"SOURCE_DATE_EPOCH": value}),
                    self.assertRaisesRegex(ValueError, "SOURCE_DATE_EPOCH"),
                ):
                    archive_fonts(
                        source_file_or_dir_path=str(source),
                        target_parent_dir_path=str(target),
                        family_name_compact="MapleMono",
                        suffix="",
                        build_config_path=str(config),
                    )

    def test_source_date_epoch_is_clamped_to_zip_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "Variable"
            source.mkdir()
            (source / "MapleMono[wght].ttf").write_bytes(b"font")
            config = root / "build-config.json"
            config.write_text("{}", encoding="utf-8")
            target = root / "archive"
            target.mkdir()

            for value, expected in (
                ("0", (1980, 1, 1, 0, 0, 0)),
                ("9999999999", (2107, 12, 31, 23, 59, 58)),
            ):
                with (
                    self.subTest(value=value),
                    patch.dict(
                        os.environ,
                        {"SOURCE_DATE_EPOCH": value},
                    ),
                ):
                    _, name = archive_fonts(
                        source_file_or_dir_path=source,
                        target_parent_dir_path=str(target),
                        family_name_compact="MapleMono",
                        suffix="",
                        build_config_path=str(config),
                    )
                    with ZipFile(target / f"{name}.zip") as archive:
                        self.assertEqual(
                            {info.date_time for info in archive.infolist()},
                            {expected},
                        )


if __name__ == "__main__":
    unittest.main()
