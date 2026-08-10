from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from scripts.cjk.cache import (
    has_valid_cjk_static_cache,
    verify_static_archive,
    verify_variable_archive,
    write_static_hash,
    write_variable_hash,
)
from scripts.cjk.config import CJKBuildConfig, CJKOutputConfig, CJKSourceConfig
from scripts.tests.cjk_font_fixtures import build_test_font


def write_test_font(path: Path) -> None:
    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder([".notdef"])
    builder.setupCharacterMap({})
    builder.setupGlyf({".notdef": TTGlyphPen(None).glyph()})
    builder.setupHorizontalMetrics({".notdef": (600, 0)})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable(
        {
            "familyName": "Test",
            "styleName": "Regular",
            "uniqueFontIdentifier": "Test Regular",
            "fullName": "Test Regular",
            "psName": "Test-Regular",
        }
    )
    builder.setupOS2()
    builder.setupPost()
    builder.setupMaxp()
    path.parent.mkdir(parents=True, exist_ok=True)
    builder.save(path)


def write_variable_test_font(path: Path) -> None:
    font = build_test_font(path, variable=True)
    font.close()


class CJKStaticCacheTest(unittest.TestCase):
    def make_config(self, root: Path) -> CJKBuildConfig:
        return CJKBuildConfig(
            source=CJKSourceConfig(
                path=root / "source.ttf",
                masters={
                    100: {"wght": 100},
                    400: {"wght": 400},
                    800: {"wght": 800},
                },
            ),
            output=CJKOutputConfig(
                dir=root / "output",
                static_hash="static-cn.sha256",
            ),
        )

    def write_static(self, config: CJKBuildConfig) -> Path:
        static_dir = config.output.dir / config.output.static_dir
        write_test_font(static_dir / "MapleMonoCJK-Regular.ttf")
        write_static_hash(config, static_dir)
        return static_dir

    def write_archive(self, static_dir: Path, archive_path: Path) -> None:
        with ZipFile(archive_path, "w") as archive:
            for font_path in static_dir.glob("*.ttf"):
                archive.write(font_path, font_path.name)

    def write_variable(self, config: CJKBuildConfig) -> tuple[Path, Path]:
        regular = config.output.dir / config.output.regular_variable
        italic = config.output.dir / config.output.italic_variable
        write_variable_test_font(regular)
        write_variable_test_font(italic)
        write_variable_hash(config)
        return regular, italic

    def write_variable_archive(
        self,
        paths: tuple[Path, Path],
        archive_path: Path,
        names: tuple[str, str] | None = None,
    ) -> None:
        member_names = names or tuple(path.name for path in paths)
        with ZipFile(archive_path, "w") as archive:
            for path, name in zip(paths, member_names, strict=True):
                archive.write(path, name)

    def test_static_archive_matches_committed_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            static_dir = self.write_static(config)
            archive_path = Path(tmp) / "cn-base-static.zip"
            self.write_archive(static_dir, archive_path)

            verify_static_archive(
                archive_path, config.output.dir / config.output.static_hash
            )

    def test_static_archive_reuses_existing_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            static_dir = self.write_static(config)
            archive_path = Path(tmp) / "cn-base-static.zip"
            self.write_archive(static_dir, archive_path)
            extracted_dir = Path(tmp) / "extracted"
            with ZipFile(archive_path) as archive:
                archive.extractall(extracted_dir)

            with patch.object(
                ZipFile,
                "extractall",
                side_effect=AssertionError("archive should not be extracted again"),
            ):
                verify_static_archive(
                    archive_path,
                    config.output.dir / config.output.static_hash,
                    extracted_dir=extracted_dir,
                )

    def test_static_archive_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            self.write_static(config)
            archive_path = Path(tmp) / "cn-base-static.zip"
            with ZipFile(archive_path, "w") as archive:
                archive.writestr("MapleMonoCJK-Regular.ttf", b"changed")

            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify_static_archive(
                    archive_path, config.output.dir / config.output.static_hash
                )

    def test_static_archive_rejects_duplicate_members(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            static_dir = self.write_static(config)
            archive_path = Path(tmp) / "duplicate.zip"
            font_data = (static_dir / "MapleMonoCJK-Regular.ttf").read_bytes()
            with ZipFile(archive_path, "w") as archive:
                archive.writestr("MapleMonoCJK-Regular.ttf", font_data)
                archive.writestr("MapleMonoCJK-Regular.ttf", font_data)

            with self.assertRaisesRegex(ValueError, "duplicate members"):
                verify_static_archive(
                    archive_path, config.output.dir / config.output.static_hash
                )

    def test_static_archive_rejects_invalid_members(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            self.write_static(config)
            archive_path = Path(tmp) / "invalid.zip"
            for member_name in (
                "nested/font.ttf",
                "README.md",
                "../font.ttf",
                r"..\font.ttf",
            ):
                with self.subTest(member_name=member_name):
                    with ZipFile(archive_path, "w") as archive:
                        archive.writestr(member_name, b"font")

                    with self.assertRaisesRegex(ValueError, "root-level TTF"):
                        verify_static_archive(
                            archive_path, config.output.dir / config.output.static_hash
                        )

    def test_static_archive_rejects_corrupt_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            self.write_static(config)
            archive_path = Path(tmp) / "corrupt.zip"
            archive_path.write_bytes(b"not a zip")

            with self.assertRaisesRegex(ValueError, "Invalid static archive"):
                verify_static_archive(
                    archive_path, config.output.dir / config.output.static_hash
                )

    def test_static_archive_rejects_empty_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            self.write_static(config)
            archive_path = Path(tmp) / "empty.zip"
            with ZipFile(archive_path, "w"):
                pass

            with self.assertRaisesRegex(ValueError, "empty"):
                verify_static_archive(
                    archive_path, config.output.dir / config.output.static_hash
                )

    def test_directory_hash_validates_static_stage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            static_dir = self.write_static(config)

            self.assertTrue(has_valid_cjk_static_cache(config, static_dir, {"Regular"}))

            (static_dir / "MapleMonoCJK-Regular.ttf").write_bytes(b"changed")
            self.assertFalse(
                has_valid_cjk_static_cache(config, static_dir, {"Regular"})
            )

    def test_missing_hash_or_style_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            static_dir = self.write_static(config)
            config.output.dir.joinpath(config.output.static_hash).unlink()
            self.assertFalse(
                has_valid_cjk_static_cache(config, static_dir, {"Regular"})
            )

            write_static_hash(config, static_dir)
            self.assertFalse(has_valid_cjk_static_cache(config, static_dir, {"Bold"}))

    def test_variable_files_are_not_verified_by_cjk_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            regular = config.output.dir / config.output.regular_variable
            italic = config.output.dir / config.output.italic_variable
            regular.parent.mkdir(parents=True)
            regular.write_bytes(b"not inspected")
            italic.write_bytes(b"not inspected")

            self.assertFalse(
                has_valid_cjk_static_cache(
                    config,
                    config.output.dir / config.output.static_dir,
                    {"Regular"},
                )
            )

    def test_variable_archive_matches_hash_and_ignores_static_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            paths = self.write_variable(config)
            archive_path = Path(tmp) / "cn-base-variable.zip"
            self.write_variable_archive(paths, archive_path)
            expected_names = tuple(path.name for path in paths)

            verify_variable_archive(
                archive_path,
                config.output.dir / config.output.variable_hash,
                expected_names,
            )

            write_test_font(config.output.dir / "static" / "unrelated.ttf")
            verify_variable_archive(
                archive_path,
                config.output.dir / config.output.variable_hash,
                expected_names,
            )

    def test_variable_archive_reuses_existing_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            paths = self.write_variable(config)
            archive_path = Path(tmp) / "cn-base-variable.zip"
            self.write_variable_archive(paths, archive_path)
            extracted_dir = Path(tmp) / "extracted"
            with ZipFile(archive_path) as archive:
                archive.extractall(extracted_dir)

            with patch.object(
                ZipFile,
                "extractall",
                side_effect=AssertionError("archive should not be extracted again"),
            ):
                verify_variable_archive(
                    archive_path,
                    config.output.dir / config.output.variable_hash,
                    tuple(path.name for path in paths),
                    extracted_dir=extracted_dir,
                )

    def test_variable_archive_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            paths = self.write_variable(config)
            archive_path = Path(tmp) / "cn-base-variable.zip"
            self.write_variable_archive(paths, archive_path)
            config.output.dir.joinpath(config.output.variable_hash).write_text(
                "0" * 64,
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify_variable_archive(
                    archive_path,
                    config.output.dir / config.output.variable_hash,
                    tuple(path.name for path in paths),
                )

    def test_variable_archive_rejects_invalid_members_and_corrupt_fonts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            paths = self.write_variable(config)
            hash_path = config.output.dir / config.output.variable_hash

            invalid_archive = Path(tmp) / "invalid-variable.zip"
            with ZipFile(invalid_archive, "w") as archive:
                archive.write(paths[0], "nested/font.ttf")
                archive.write(paths[1], paths[1].name)
            with self.assertRaisesRegex(ValueError, "root-level TTF"):
                verify_variable_archive(invalid_archive, hash_path)

            wrong_names_archive = Path(tmp) / "wrong-names-variable.zip"
            self.write_variable_archive(
                paths,
                wrong_names_archive,
                ("regular.ttf", "italic.ttf"),
            )
            with self.assertRaisesRegex(ValueError, "expected regular"):
                verify_variable_archive(wrong_names_archive, hash_path)

            corrupt_archive = Path(tmp) / "corrupt-variable.zip"
            with ZipFile(corrupt_archive, "w") as archive:
                archive.writestr(paths[0].name, b"not a font")
                archive.write(paths[1], paths[1].name)
            with self.assertRaisesRegex(ValueError, "valid font"):
                verify_variable_archive(corrupt_archive, hash_path)

            broken_archive = Path(tmp) / "broken-variable.zip"
            broken_archive.write_bytes(b"not a zip")
            with self.assertRaisesRegex(ValueError, "Invalid variable archive"):
                verify_variable_archive(broken_archive, hash_path)

    def test_variable_archive_rejects_non_variable_font(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = self.make_config(Path(tmp))
            regular, italic = self.write_variable(config)
            write_test_font(regular)
            archive_path = Path(tmp) / "not-variable.zip"
            self.write_variable_archive((regular, italic), archive_path)

            with self.assertRaisesRegex(ValueError, "not variable"):
                verify_variable_archive(
                    archive_path,
                    config.output.dir / config.output.variable_hash,
                    (regular.name, italic.name),
                )


if __name__ == "__main__":
    unittest.main()
