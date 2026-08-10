from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import MagicMock, patch
from zipfile import ZipFile

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from scripts.cjk.cache import write_static_hash, write_variable_hash
from scripts.cjk.config import (
    CJKBuildConfig,
    CJKNamingConfig,
    CJKOutputConfig,
    CJKSourceConfig,
    CJKWeightInstance,
)
from scripts.cjk.presets import CJKPresetId, get_preset
from scripts.config.base import CJKCommonBuildOptions, ResolvedCJKBuildEntry
from scripts.config.cli import parse_args
from scripts.config.resolver import BuildConfigResolver
from scripts.config.runtime import BuildRuntimeContext
from scripts.errors import BuildDependencyError
from scripts.external.process import SynchronousExecutor
from scripts.pipeline.nerd_fonts import (
    ensure_font_patcher_available,
    should_use_font_patcher,
)
from scripts.tests.cjk_font_fixtures import build_test_font
from scripts.utils.files import get_directory_hash

if TYPE_CHECKING:
    from concurrent.futures import Executor


def make_runtime_context(tmp_path: Path) -> BuildRuntimeContext:
    return BuildRuntimeContext(
        src_dir="source",
        output_root=str(tmp_path / "fonts"),
        output_otf=str(tmp_path / "fonts" / "OTF"),
        output_ttf=str(tmp_path / "fonts" / "TTF"),
        output_ttf_hinted=str(tmp_path / "fonts" / "TTF-AutoHint"),
        output_variable=str(tmp_path / "fonts" / "Variable"),
        output_woff2=str(tmp_path / "fonts" / "Woff2"),
        output_nf=str(tmp_path / "fonts" / "NF"),
        ttf_base_dir=str(tmp_path / "fonts" / "TTF-AutoHint"),
        has_cache=False,
        is_nf_built=False,
        is_cjk_built=False,
        effective_github_mirror="github.com",
        font_forge_bin=None,
        resolved_vertical_metric=(1020, -300),
    )


def make_font_config():
    return BuildConfigResolver().load_defaults()


class ProjectConfigResolutionTest(unittest.TestCase):
    def test_project_config_resolves_without_cli_namespace(self) -> None:
        config = BuildConfigResolver().resolve_project_config()

        self.assertEqual(config.family_name, "Maple Mono")
        self.assertEqual(config.formats, ["ttf", "otf", "woff2"])

    def test_project_config_loads_the_embedded_font_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config.json").write_text(
                json.dumps({"family_name": "Fixture Mono", "font_version": "8.001"}),
                encoding="utf-8",
            )

            config = BuildConfigResolver(
                project_root=root,
                version_tag="v8.0-beta.1",
            ).resolve_project_config()

            self.assertEqual(config.font_version, "8.001")
            self.assertEqual(config.version_str, "Version 8.001")

    def test_project_config_rejects_an_invalid_embedded_font_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config.json").write_text(
                json.dumps({"font_version": "8.01"}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Invalid font_version"):
                BuildConfigResolver(project_root=root).resolve_project_config()


def make_preset(tmp_path: Path, locale_name: str = "CN") -> CJKBuildConfig:
    locale_dir = tmp_path / locale_name.lower()
    return CJKBuildConfig(
        source=CJKSourceConfig(
            path=tmp_path / "source.ttf",
            masters={100: {"wght": 100}, 400: {"wght": 400}, 800: {"wght": 800}},
        ),
        locale_name=locale_name,
        output=CJKOutputConfig(
            dir=locale_dir,
            regular_variable=f"MapleMono-{locale_name}-VF.ttf",
            italic_variable=f"MapleMono-{locale_name}-Italic-VF.ttf",
            static_dir="static",
            static_hash=f"static-{locale_name.lower()}.sha256",
            archive_name=f"{locale_name.lower()}-base-static.zip",
        ),
        naming=CJKNamingConfig(
            family_name=f"Maple Mono {locale_name}",
            postscript_prefix=f"MapleMono{locale_name}",
            static_file_prefix=f"MapleMono{locale_name}",
        ),
    )


def make_entry(
    tmp_path: Path,
    locale_name: str = "CN",
    preset_id: CJKPresetId | None = "cn",
    *,
    clean_cache: bool = False,
) -> ResolvedCJKBuildEntry:
    preset_spec = get_preset(preset_id) if preset_id else None
    return ResolvedCJKBuildEntry(
        entry_id=preset_id or f"custom:{locale_name.lower()}",
        locale_name=locale_name,
        build_config=make_preset(tmp_path, locale_name),
        common_options=CJKCommonBuildOptions(clean_cache=clean_cache),
        is_builtin=bool(preset_id),
        preset_id=preset_id,
        preset_spec=preset_spec,
    )


def write_static_fonts(static_dir: Path, prefix: str, styles: list[str]) -> None:
    static_dir.mkdir(parents=True, exist_ok=True)
    for style in styles:
        write_test_font(static_dir / f"{prefix}-{style}.ttf")


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


def write_variable_fonts(config: CJKBuildConfig) -> None:
    write_test_font(config.output.dir / config.output.regular_variable)
    write_test_font(config.output.dir / config.output.italic_variable)


def write_real_variable_fonts(config: CJKBuildConfig) -> tuple[Path, Path]:
    paths = (
        config.output.dir / config.output.regular_variable,
        config.output.dir / config.output.italic_variable,
    )
    for path in paths:
        font = build_test_font(path, variable=True)
        font.close()
    return paths


def resolve_quietly(
    runtime_context: BuildRuntimeContext,
    entry: ResolvedCJKBuildEntry,
    required_styles: list[str],
):
    def build_variable(
        config: CJKBuildConfig,
        *_args,
        **_kwargs,
    ) -> None:
        write_variable_fonts(config)

    with redirect_stdout(StringIO()):
        return runtime_context.resolve_cjk_static_base(
            entry,
            required_styles,
            make_font_config(),
            build_variable,
        )


class BuildRuntimeContextCJKStaticBaseTest(unittest.TestCase):
    def test_static_download_uses_effective_github_mirror(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            runtime_context.effective_github_mirror = "mirror.example.com/github.com"
            entry = make_entry(tmp_path)
            config = entry.build_config
            expected_dir = tmp_path / "expected-static"
            write_static_fonts(
                expected_dir, config.naming.static_file_prefix, ["Regular"]
            )
            write_static_hash(config, expected_dir)

            def fake_download(*, zip_path, output_dir, **_kwargs) -> bool:
                extracted_dir = Path(output_dir)
                write_static_fonts(
                    extracted_dir,
                    config.naming.static_file_prefix,
                    ["Regular"],
                )
                with ZipFile(zip_path, "w") as archive:
                    for font_path in extracted_dir.glob("*.ttf"):
                        archive.write(font_path, font_path.name)
                return True

            with (
                patch(
                    "scripts.config.runtime.download_zip_and_extract",
                    side_effect=fake_download,
                ) as download,
                patch("zipfile.ZipFile.extractall") as extractall,
            ):
                downloaded = runtime_context.download_cjk_static_base(
                    "cn",
                    config,
                )

            self.assertTrue(downloaded)
            self.assertEqual(
                download.call_args.kwargs["github_mirror"],
                "mirror.example.com/github.com",
            )
            self.assertEqual(
                download.call_args.kwargs["url"],
                "https://github.com/subframe7536/maple-font/releases/download/cjk-base/cn-base-static.zip",
            )
            extractall.assert_not_called()
            self.assertTrue(
                (
                    runtime_context.cjk_static_dir(config) / "MapleMonoCN-Regular.ttf"
                ).is_file()
            )

    def test_remote_static_archive_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            config = entry.build_config
            static_dir = runtime_context.cjk_static_dir(config)
            write_static_fonts(
                static_dir,
                config.naming.static_file_prefix,
                ["Regular"],
            )
            write_static_hash(config, static_dir)
            shutil.rmtree(static_dir)

            def fake_download(*, zip_path, output_dir, **_kwargs) -> bool:
                extracted_dir = Path(output_dir)
                write_static_fonts(
                    extracted_dir,
                    config.naming.static_file_prefix,
                    ["Regular", "Bold"],
                )
                with ZipFile(zip_path, "w") as archive:
                    for font_path in extracted_dir.glob("*.ttf"):
                        archive.write(font_path, font_path.name)
                return True

            with patch(
                "scripts.config.runtime.download_zip_and_extract",
                side_effect=fake_download,
            ):
                downloaded = runtime_context.download_cjk_static_base("cn", config)

            self.assertFalse(downloaded)
            self.assertFalse(static_dir.exists())

    def test_local_static_archive_is_used_before_remote_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            config = entry.build_config
            static_dir = runtime_context.cjk_static_dir(config)
            write_static_fonts(
                static_dir,
                config.naming.static_file_prefix,
                ["Regular"],
            )
            write_static_hash(config, static_dir)
            local_archive = config.output.dir / config.output.archive_name
            with ZipFile(local_archive, "w") as archive:
                for font_path in static_dir.glob("*.ttf"):
                    archive.write(font_path, font_path.name)
            shutil.rmtree(static_dir)

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=AssertionError("remote download should not run"),
                ) as download,
                patch.object(
                    ZipFile,
                    "extractall",
                    autospec=True,
                    side_effect=ZipFile.extractall,
                ) as extractall,
            ):
                downloaded = runtime_context.download_cjk_static_base("cn", config)

            self.assertTrue(downloaded)
            self.assertTrue((static_dir / "MapleMonoCN-Regular.ttf").is_file())
            download.assert_not_called()
            extractall.assert_called_once()

    def test_variable_download_uses_effective_github_mirror_and_validates_archive(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            runtime_context.effective_github_mirror = "mirror.example.com/github.com"
            entry = make_entry(tmp_path)
            config = entry.build_config
            paths = write_real_variable_fonts(config)
            write_variable_hash(config)
            remote_archive = tmp_path / "remote-variable.zip"
            with ZipFile(remote_archive, "w") as archive:
                for path in paths:
                    archive.write(path, path.name)
            for path in paths:
                path.unlink()

            def fake_download(
                *,
                zip_path: str | Path,
                output_dir: str | Path,
                **_kwargs,
            ) -> bool:
                shutil.copy2(remote_archive, zip_path)
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                with ZipFile(zip_path) as archive:
                    archive.extractall(output_dir)
                return True

            with (
                patch(
                    "scripts.config.runtime.download_zip_and_extract",
                    side_effect=fake_download,
                ) as download,
                patch.object(
                    ZipFile,
                    "extractall",
                    autospec=True,
                    side_effect=ZipFile.extractall,
                ) as extractall,
            ):
                downloaded = runtime_context.download_cjk_variable_base(
                    "cn",
                    config,
                )

            self.assertTrue(downloaded)
            self.assertTrue(all(path.is_file() for path in paths))
            self.assertEqual(
                download.call_args.kwargs["github_mirror"],
                "mirror.example.com/github.com",
            )
            self.assertEqual(
                download.call_args.kwargs["url"],
                "https://github.com/subframe7536/maple-font/releases/download/cjk-base/cn-base-variable.zip",
            )
            extractall.assert_called_once()
            self.assertFalse(
                config.output.dir.joinpath(
                    ".cn-base-variable.zip.download.zip"
                ).exists()
            )

    def test_local_variable_archive_is_used_before_remote_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            config = entry.build_config
            paths = write_real_variable_fonts(config)
            write_variable_hash(config)
            local_archive = config.output.dir / config.output.variable_archive_name
            with ZipFile(local_archive, "w") as archive:
                for font_path in paths:
                    archive.write(font_path, font_path.name)
            for font_path in paths:
                font_path.unlink()

            with (
                patch(
                    "scripts.utils.downloads.download_file",
                    side_effect=AssertionError("remote download should not run"),
                ) as download,
                patch.object(
                    ZipFile,
                    "extractall",
                    autospec=True,
                    side_effect=ZipFile.extractall,
                ) as extractall,
            ):
                downloaded = runtime_context.download_cjk_variable_base("cn", config)

            self.assertTrue(downloaded)
            self.assertTrue(all(font_path.is_file() for font_path in paths))
            download.assert_not_called()
            extractall.assert_called_once()

    def test_remote_variable_fallback_precedes_source_rebuild(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)

            def fake_instantiate(
                config: CJKBuildConfig,
                _font_config,
                **_kwargs,
            ) -> None:
                static_dir = runtime_context.cjk_static_dir(config)
                write_static_fonts(
                    static_dir,
                    config.naming.static_file_prefix,
                    ["Regular"],
                )
                write_static_hash(config, static_dir)

            with (
                patch.object(
                    BuildRuntimeContext,
                    "download_cjk_static_base",
                    return_value=False,
                ),
                patch.object(
                    BuildRuntimeContext,
                    "download_cjk_variable_base",
                    return_value=True,
                ) as download_variable,
                patch(
                    "scripts.config.runtime.instantiate_cjk_static_from_variable",
                    side_effect=fake_instantiate,
                ),
                patch.object(
                    BuildRuntimeContext,
                    "build_cjk_static_base_from_variable",
                ) as build_source,
            ):
                result = resolve_quietly(runtime_context, entry, ["Regular"])

            self.assertEqual(result.source_kind, "remote-variable")
            download_variable.assert_called_once_with("cn", entry.build_config)
            build_source.assert_not_called()

    def test_variable_fallback_uses_effective_github_mirror(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_context = make_runtime_context(Path(tmp))
            runtime_context.effective_github_mirror = "mirror.example.com"
            config = make_preset(Path(tmp))

            with patch("scripts.cjk.builder.build_cjk_fonts") as build:
                runtime_context.build_cjk_static_base_from_variable(
                    config,
                    make_font_config(),
                    build,
                )

            build.assert_called_once_with(
                config,
                make_font_config(),
                vf_only=True,
                executor=None,
                github_mirror="mirror.example.com",
            )

    def test_local_variable_fallback_forwards_executor_and_styles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            write_variable_fonts(entry.build_config)
            executor = cast("Executor", MagicMock())

            def fake_instantiate(
                config: CJKBuildConfig,
                _font_config,
                *,
                executor: Executor | None,
                required_styles,
            ) -> None:
                self.assertIs(executor, sentinel_executor)
                self.assertEqual(required_styles, ["Bold", "Regular"])
                static_dir = runtime_context.cjk_static_dir(config)
                write_static_fonts(
                    static_dir,
                    config.naming.static_file_prefix,
                    required_styles,
                )
                write_static_hash(config, static_dir)

            sentinel_executor = executor
            with (
                patch.object(
                    BuildRuntimeContext,
                    "download_cjk_static_base",
                    return_value=False,
                ),
                patch(
                    "scripts.config.runtime.instantiate_cjk_static_from_variable",
                    side_effect=fake_instantiate,
                ) as instantiate,
            ):
                result = runtime_context.resolve_cjk_static_base(
                    entry,
                    ["Regular", "Bold"],
                    make_font_config(),
                    MagicMock(),
                    executor,
                )

            self.assertEqual(result.source_kind, "local-variable")
            instantiate.assert_called_once()

    def test_source_rebuild_forwards_executor_and_styles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            executor = cast("Executor", MagicMock())
            variable_builder = MagicMock(
                side_effect=lambda config, _font_config, **_kwargs: (
                    write_variable_fonts(config)
                )
            )

            def fake_instantiate(
                config: CJKBuildConfig,
                _font_config,
                *,
                executor: Executor | None,
                required_styles,
            ) -> None:
                self.assertIs(executor, sentinel_executor)
                self.assertEqual(required_styles, ["Italic", "Regular"])
                static_dir = runtime_context.cjk_static_dir(config)
                write_static_fonts(
                    static_dir,
                    config.naming.static_file_prefix,
                    required_styles,
                )
                write_static_hash(config, static_dir)

            sentinel_executor = executor
            with (
                patch.object(
                    BuildRuntimeContext,
                    "download_cjk_static_base",
                    return_value=False,
                ),
                patch(
                    "scripts.config.runtime.instantiate_cjk_static_from_variable",
                    side_effect=fake_instantiate,
                ),
            ):
                result = runtime_context.resolve_cjk_static_base(
                    entry,
                    ["Regular", "Italic"],
                    make_font_config(),
                    variable_builder,
                    executor,
                )

            self.assertEqual(result.source_kind, "remote-variable")
            variable_builder.assert_called_once_with(
                entry.build_config,
                make_font_config(),
                vf_only=True,
                executor=executor,
                github_mirror="github.com",
            )

    def test_reuses_valid_local_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            static_dir = runtime_context.cjk_static_dir(entry.build_config)
            write_static_fonts(
                static_dir,
                entry.build_config.naming.static_file_prefix,
                ["Regular"],
            )
            write_static_hash(entry.build_config, static_dir)

            result = resolve_quietly(runtime_context, entry, ["Regular"])

            self.assertEqual(result.source_kind, "local-static")
            self.assertEqual(result.static_dir, static_dir)

    def test_existing_static_cache_hashes_contents_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            static_dir = runtime_context.cjk_static_dir(entry.build_config)
            write_static_fonts(
                static_dir,
                entry.build_config.naming.static_file_prefix,
                ["Regular"],
            )
            write_static_hash(entry.build_config, static_dir)

            with patch(
                "scripts.cjk.cache.get_directory_hash",
                wraps=get_directory_hash,
            ) as directory_hash:
                result = resolve_quietly(runtime_context, entry, ["Regular"])

            self.assertEqual(result.source_kind, "local-static")
            directory_hash.assert_called_once_with(str(static_dir))

    def test_downloaded_static_cache_hashes_contents_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            static_dir = runtime_context.cjk_static_dir(entry.build_config)

            def fake_download(
                self: BuildRuntimeContext,
                _locale: str,
                config: CJKBuildConfig,
            ) -> bool:
                write_static_fonts(
                    self.cjk_static_dir(config),
                    config.naming.static_file_prefix,
                    ["Regular"],
                )
                return True

            with (
                patch.object(
                    BuildRuntimeContext,
                    "download_cjk_static_base",
                    fake_download,
                ),
                patch(
                    "scripts.cjk.cache.get_directory_hash",
                    wraps=get_directory_hash,
                ) as directory_hash,
            ):
                result = runtime_context._resolve_downloaded_cjk_static_base(
                    "cn",
                    entry.build_config,
                    static_dir,
                    entry.build_config.naming.static_file_prefix,
                    ["Regular"],
                )

            self.assertIsNotNone(result)
            directory_hash.assert_called_once_with(str(static_dir))

    def test_instantiated_static_cache_hashes_contents_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            static_dir = runtime_context.cjk_static_dir(entry.build_config)
            write_variable_fonts(entry.build_config)

            def fake_instantiate(
                config: CJKBuildConfig,
                _font_config,
                **_kwargs,
            ) -> None:
                write_static_fonts(
                    static_dir,
                    config.naming.static_file_prefix,
                    ["Regular"],
                )
                write_static_hash(config, static_dir)

            with (
                patch.object(
                    BuildRuntimeContext,
                    "download_cjk_static_base",
                    return_value=False,
                ),
                patch(
                    "scripts.config.runtime.instantiate_cjk_static_from_variable",
                    fake_instantiate,
                ),
                patch(
                    "scripts.cjk.cache.get_directory_hash",
                    wraps=get_directory_hash,
                ) as directory_hash,
            ):
                result = resolve_quietly(runtime_context, entry, ["Regular"])

            self.assertEqual(result.source_kind, "local-variable")
            directory_hash.assert_called_once_with(str(static_dir))

    def test_invalid_static_hash_preserves_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            static_dir = runtime_context.cjk_static_dir(entry.build_config)
            write_static_fonts(
                static_dir,
                entry.build_config.naming.static_file_prefix,
                ["Regular"],
            )
            write_static_hash(entry.build_config, static_dir)
            entry.build_config.output.dir.joinpath(
                entry.build_config.output.static_hash
            ).write_text("bad-hash", encoding="utf-8")

            result = runtime_context._resolve_local_cjk_static_base(
                False,
                entry.build_config,
                static_dir,
                entry.build_config.naming.static_file_prefix,
                ["Regular"],
                entry.build_config.locale_name,
            )

            self.assertIsNone(result)
            self.assertTrue(static_dir.is_dir())
            self.assertEqual(
                entry.build_config.output.dir.joinpath(
                    entry.build_config.output.static_hash
                ).read_text(encoding="utf-8"),
                "bad-hash",
            )

    def test_existing_static_cache_skips_remote_download(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            static_dir = runtime_context.cjk_static_dir(entry.build_config)
            static_dir.mkdir(parents=True)
            marker = static_dir / "existing-cache-marker"
            marker.write_text("preserve", encoding="utf-8")

            with patch("scripts.config.runtime.download_zip_and_extract") as download:
                result = runtime_context.download_cjk_static_base(
                    "cn",
                    entry.build_config,
                )

            self.assertFalse(result)
            download.assert_not_called()
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")

    def test_incomplete_download_preserves_source_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            static_dir = runtime_context.cjk_static_dir(entry.build_config)

            def fake_download(
                self: BuildRuntimeContext,
                _locale: str,
                config: CJKBuildConfig,
            ) -> bool:
                write_static_fonts(
                    self.cjk_static_dir(config),
                    config.naming.static_file_prefix,
                    ["Regular"],
                )
                return True

            with patch.object(
                BuildRuntimeContext,
                "download_cjk_static_base",
                fake_download,
            ):
                result = runtime_context._resolve_downloaded_cjk_static_base(
                    "cn",
                    entry.build_config,
                    static_dir,
                    entry.build_config.naming.static_file_prefix,
                    ["Regular", "Bold"],
                )

            self.assertIsNone(result)
            self.assertTrue(static_dir.is_dir())
            self.assertTrue((static_dir / "MapleMonoCN-Regular.ttf").is_file())

    def test_custom_entry_skips_download_and_uses_variable_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path, locale_name="HK", preset_id=None)

            def fake_build(
                _self: BuildRuntimeContext,
                config: CJKBuildConfig,
                *_args,
            ) -> None:
                write_variable_fonts(config)

            def fake_instantiate(
                config: CJKBuildConfig,
                _font_config,
                **_kwargs,
            ) -> None:
                static_dir = runtime_context.cjk_static_dir(config)
                write_static_fonts(
                    static_dir,
                    config.naming.static_file_prefix,
                    ["Regular"],
                )
                write_static_hash(config, static_dir)

            with (
                patch.object(
                    BuildRuntimeContext,
                    "download_cjk_static_base",
                    return_value=True,
                ) as download_mock,
                patch.object(
                    BuildRuntimeContext,
                    "build_cjk_static_base_from_variable",
                    fake_build,
                ),
                patch(
                    "scripts.config.runtime.instantiate_cjk_static_from_variable",
                    fake_instantiate,
                ),
            ):
                result = resolve_quietly(runtime_context, entry, ["Regular"])

            download_mock.assert_not_called()
            self.assertEqual(result.source_kind, "remote-variable")

    def test_clean_cache_reuses_valid_static_without_instantiation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path, clean_cache=True)
            static_dir = runtime_context.cjk_static_dir(entry.build_config)
            write_static_fonts(
                static_dir,
                entry.build_config.naming.static_file_prefix,
                ["Regular"],
            )
            write_static_hash(entry.build_config, static_dir)

            with patch(
                "scripts.config.runtime.instantiate_cjk_static_from_variable"
            ) as instantiate:
                result = resolve_quietly(runtime_context, entry, ["Regular"])

            self.assertEqual(result.source_kind, "local-static")
            instantiate.assert_not_called()

    def test_variable_fallback_does_not_require_variable_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)

            def fake_build(
                _self: BuildRuntimeContext,
                config: CJKBuildConfig,
                *_args,
            ) -> None:
                write_variable_fonts(config)

            def fake_instantiate(
                config: CJKBuildConfig,
                _font_config,
                **_kwargs,
            ) -> None:
                static_dir = runtime_context.cjk_static_dir(config)
                write_static_fonts(
                    static_dir,
                    config.naming.static_file_prefix,
                    ["Regular"],
                )
                write_static_hash(config, static_dir)

            with (
                patch.object(
                    BuildRuntimeContext,
                    "download_cjk_static_base",
                    return_value=False,
                ),
                patch.object(
                    BuildRuntimeContext,
                    "build_cjk_static_base_from_variable",
                    fake_build,
                ),
                patch(
                    "scripts.config.runtime.instantiate_cjk_static_from_variable",
                    fake_instantiate,
                ),
            ):
                result = resolve_quietly(runtime_context, entry, ["Regular"])

            self.assertEqual(result.source_kind, "remote-variable")
            self.assertTrue(
                entry.build_config.output.dir.joinpath(
                    entry.build_config.output.static_hash
                ).exists()
            )

    def test_partial_cache_is_completed_by_a_broader_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)
            config = entry.build_config
            static_dir = runtime_context.cjk_static_dir(config)
            write_variable_fonts(config)
            write_static_fonts(
                static_dir,
                config.naming.static_file_prefix,
                ["Regular", "Bold", "Italic", "BoldItalic"],
            )
            marker = static_dir / "existing-cache-marker"
            marker.write_text("preserve", encoding="utf-8")
            unrelated_font = static_dir / "OtherFamily-Bold.ttf"
            unrelated_font.write_bytes(b"unrelated")
            scheduled: list[str] = []
            axis = SimpleNamespace(minValue=100, defaultValue=400, maxValue=700)

            def instantiate_job(job) -> None:
                style = f"{job.name}{'Italic' if job.is_italic else ''}".replace(
                    "RegularItalic", "Italic"
                )
                scheduled.append(style)
                Path(job.output_path).write_bytes(f"generated-{style}".encode())

            with (
                patch.object(
                    BuildRuntimeContext,
                    "download_cjk_static_base",
                    return_value=False,
                ),
                patch(
                    "scripts.cjk.builder.load_feature_variable_font",
                    return_value=MagicMock(),
                ),
                patch(
                    "scripts.cjk.builder.load_font",
                    return_value=MagicMock(),
                ),
                patch("scripts.cjk.builder.weight_axis", return_value=axis),
                patch(
                    "scripts.cjk.builder.feature_weight_instances",
                    return_value=(
                        CJKWeightInstance("Regular", 400),
                        CJKWeightInstance("Bold", 700),
                    ),
                ),
                patch(
                    "scripts.cjk.builder.instantiate_static_font_job",
                    side_effect=instantiate_job,
                ),
            ):
                partial = runtime_context.resolve_cjk_static_base(
                    entry,
                    ["Regular", "Italic"],
                    make_font_config(),
                    MagicMock(),
                    SynchronousExecutor(),
                )
                partial_digest = config.output.dir.joinpath(
                    config.output.static_hash
                ).read_text(encoding="utf-8")
                self.assertEqual(scheduled, ["Regular", "Italic"])
                self.assertFalse(
                    static_dir.joinpath(
                        f"{config.naming.static_file_prefix}-Bold.ttf"
                    ).exists()
                )
                self.assertFalse(
                    static_dir.joinpath(
                        f"{config.naming.static_file_prefix}-BoldItalic.ttf"
                    ).exists()
                )
                self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")
                self.assertEqual(unrelated_font.read_bytes(), b"unrelated")
                self.assertFalse(
                    runtime_context.has_valid_cjk_static_base(
                        config,
                        static_dir,
                        ["Regular", "Bold", "Italic", "BoldItalic"],
                    )
                )

                completed = runtime_context.resolve_cjk_static_base(
                    entry,
                    ["Regular", "Bold", "Italic", "BoldItalic"],
                    make_font_config(),
                    MagicMock(),
                    SynchronousExecutor(),
                )

            complete_digest = config.output.dir.joinpath(
                config.output.static_hash
            ).read_text(encoding="utf-8")
            self.assertEqual(partial.source_kind, "local-variable")
            self.assertEqual(completed.source_kind, "local-variable")
            self.assertEqual(
                scheduled,
                [
                    "Regular",
                    "Italic",
                    "Regular",
                    "Bold",
                    "Italic",
                    "BoldItalic",
                ],
            )
            self.assertNotEqual(partial_digest, complete_digest)
            self.assertTrue(
                runtime_context.has_valid_cjk_static_base(
                    config,
                    completed.static_dir,
                    ["Regular", "Bold", "Italic", "BoldItalic"],
                )
            )

    def test_missing_styles_after_fallback_raise_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime_context = make_runtime_context(tmp_path)
            entry = make_entry(tmp_path)

            with (
                patch.object(
                    BuildRuntimeContext,
                    "download_cjk_static_base",
                    return_value=False,
                ),
                patch.object(
                    BuildRuntimeContext,
                    "build_cjk_static_base_from_variable",
                    return_value=None,
                ),
                self.assertRaisesRegex(Exception, "Unable to resolve"),
            ):
                resolve_quietly(runtime_context, entry, ["Regular"])


class BuildConfigResolverJsonTest(unittest.TestCase):
    def _resolve_with_config(
        self,
        config_data: dict,
        args: list[str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            config_path.write_text(json.dumps(config_data), encoding="utf-8")
            return BuildConfigResolver(project_root=Path(tmp)).resolve(
                parse_args(args or [])
            )

    def test_standard_zero_is_opt_in_and_normal_does_not_enable_it(self) -> None:
        default = self._resolve_with_config({})
        self.assertFalse(default.feature.standard_zero)
        self.assertEqual(default.feature_freeze["zero"], "ignore")

        standard = self._resolve_with_config({}, ["--standard-zero"])
        self.assertTrue(standard.feature.standard_zero)

        configured = self._resolve_with_config({"standard_zero": True})
        self.assertTrue(configured.feature.standard_zero)

        normal = self._resolve_with_config({}, ["--normal"])
        self.assertFalse(normal.feature.standard_zero)
        self.assertEqual(normal.feature_freeze["zero"], "ignore")
        self.assertFalse(normal.to_build_record()["standard_zero"])

    def test_all_top_level_config_sections_resolve_to_runtime_values(self) -> None:
        font_config = self._resolve_with_config(
            {
                "family_name": "Fixture Mono",
                "pool_size": 3,
                "weight_mapping": {"regular": 450},
                "codepoint_alias": {"0xE000": "0x0041"},
                "use_hinted": False,
                "ligature": False,
                "infinite_arrow": True,
                "remove_tag_liga": True,
                "line_height": 1.15,
                "width": "narrow",
                "ttfautohint_param": {"hinting_limit": 180},
                "feature_freeze": {"cv01": "enable"},
                "github_mirror": "mirror.example.com/github.com",
                "nerd_font": {
                    "enable": False,
                    "version": "3.4.0",
                    "mono": True,
                    "propo": False,
                    "variable": True,
                    "use_font_patcher": True,
                    "glyphs": ["--codicons"],
                    "extra_args": ["--careful"],
                },
                "formats": ["otf"],
                "cjk": {
                    "variable": True,
                    "locales": {"jp": True},
                    "with_nerd_font": False,
                    "narrow": True,
                    "scale_factor": [1.1, 0.9],
                },
                "cn": {"enable": True},
            }
        )

        self.assertEqual(font_config.identity.base_family_name, "Fixture Mono")
        self.assertEqual(font_config.pool_size, 3)
        self.assertEqual(font_config.weight_mapping["regular"], 450)
        self.assertEqual(font_config.codepoint_alias, {0xE000: 0x0041})
        self.assertFalse(font_config.use_hinted)
        self.assertFalse(font_config.feature.liga)
        self.assertTrue(font_config.infinite_arrow)
        self.assertTrue(font_config.remove_tag_liga)
        self.assertEqual(font_config.line_height, 1.15)
        self.assertEqual(font_config.width, "narrow")
        self.assertEqual(font_config.ttfautohint_param, {"hinting_limit": 180})
        self.assertEqual(font_config.feature_freeze["cv01"], "enable")
        self.assertEqual(font_config.github_mirror, "mirror.example.com/github.com")
        self.assertFalse(font_config.nerd_font.enable)
        self.assertEqual(font_config.nerd_font.version, "3.4.0")
        self.assertTrue(font_config.nerd_font.mono)
        self.assertFalse(font_config.nerd_font.propo)
        self.assertTrue(font_config.nerd_font.variable)
        self.assertTrue(font_config.nerd_font.use_font_patcher)
        self.assertEqual(font_config.nerd_font.glyphs, ["--codicons"])
        self.assertEqual(font_config.nerd_font.extra_args, ["--careful"])
        self.assertEqual(font_config.formats, ["otf"])
        self.assertEqual(font_config.cjk_output_format, "variable")
        self.assertEqual(
            font_config.cjk.locales.builtin_enabled_locales(), ["cn", "jp"]
        )
        self.assertFalse(font_config.cjk.common_options.with_nerd_font)
        self.assertTrue(font_config.cjk.common_options.narrow)
        self.assertEqual(font_config.cjk.common_options.scale_factor, (1.1, 0.9))

    def test_cli_values_override_project_config_across_all_build_sections(self) -> None:
        font_config = self._resolve_with_config(
            {
                "use_hinted": False,
                "ligature": False,
                "line_height": 1.1,
                "width": "narrow",
                "formats": ["otf"],
                "nerd_font": {
                    "enable": False,
                    "mono": False,
                    "propo": False,
                    "variable": False,
                    "use_font_patcher": False,
                },
                "cjk": {
                    "variable": False,
                    "locales": {"cn": False, "jp": False},
                    "narrow": False,
                    "scale_factor": 1.0,
                },
            },
            [
                "--normal",
                "--feat",
                "zero,cv01",
                "--apply-fea-file",
                "--hinted",
                "--liga",
                "--infinite-arrow",
                "--remove-tag-liga",
                "--line-height",
                "1.25",
                "--width",
                "slim",
                "--format",
                "ttf,woff2",
                "--least-styles",
                "--cache",
                "--archive",
                "--nf-mono",
                "--nf-propo",
                "--nf-variable",
                "--font-patcher",
                "--cjk",
                "jp",
                "--cjk-variable",
                "--cjk-narrow",
                "--cjk-scale-factor",
                "1.2",
                "--cjk-hinted",
                "--cjk-both",
            ],
        )

        self.assertTrue(font_config.feature.normal)
        self.assertFalse(font_config.feature.standard_zero)
        self.assertEqual(font_config.feature.feat, ["zero", "cv01"])
        self.assertEqual(font_config.feature_freeze["zero"], "enable")
        self.assertTrue(font_config.apply_fea_file)
        self.assertTrue(font_config.use_hinted)
        self.assertTrue(font_config.feature.liga)
        self.assertTrue(font_config.infinite_arrow)
        self.assertTrue(font_config.remove_tag_liga)
        self.assertEqual(font_config.line_height, 1.25)
        self.assertEqual(font_config.width, "slim")
        self.assertEqual(font_config.formats, ["ttf", "woff2"])
        self.assertTrue(font_config.least_styles)
        self.assertTrue(font_config.cache)
        self.assertTrue(font_config.archive)
        self.assertTrue(font_config.nerd_font.enable)
        self.assertFalse(font_config.nerd_font.mono)
        self.assertTrue(font_config.nerd_font.propo)
        self.assertTrue(font_config.nerd_font.variable)
        self.assertTrue(font_config.nerd_font.use_font_patcher)
        self.assertEqual(font_config.cjk_output_format, "variable")
        self.assertEqual(font_config.cjk.locales.builtin_enabled_locales(), ["jp"])
        self.assertTrue(font_config.cjk.common_options.narrow)
        self.assertEqual(font_config.cjk.common_options.scale_factor, (1.2, 1.2))
        self.assertTrue(font_config.cjk.common_options.use_hinted)
        self.assertTrue(font_config.use_cjk_both)

    def test_schema_constrained_config_values_are_rejected_during_resolution(
        self,
    ) -> None:
        cases = (
            ({"width": "wide"}, "width"),
            ({"feature_freeze": {"cv01": "sometimes"}}, "cv01"),
            ({"nerd_font": {"glyphs": "--complete"}}, "nerd_font.glyphs"),
            ({"nerd_font": {"extra_args": "--careful"}}, "nerd_font.extra_args"),
        )
        for config_data, field in cases:
            with self.subTest(field=field):
                with self.assertRaises(ValueError) as error:
                    self._resolve_with_config(config_data)

                self.assertIn(field, str(error.exception))

    def test_variable_nerd_font_rejects_static_cjk_output(self) -> None:
        with self.assertRaisesRegex(ValueError, "cjk.variable=true"):
            self._resolve_with_config(
                {
                    "nerd_font": {"variable": True},
                    "cjk": {"locales": {"jp": True}},
                }
            )

    def test_variable_nerd_font_allows_variable_cjk_output(self) -> None:
        config = self._resolve_with_config(
            {
                "nerd_font": {"variable": True},
                "cjk": {
                    "variable": True,
                    "locales": {"jp": True},
                },
            }
        )
        self.assertTrue(config.nerd_font.variable)
        self.assertEqual(config.cjk_output_format, "variable")

    def test_rejects_non_object_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            config_path.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "JSON object"):
                BuildConfigResolver(project_root=Path(tmp)).resolve(parse_args([]))

    def test_feature_boolean_rejects_non_boolean_values(self) -> None:
        for field in ("use_hinted", "standard_zero"):
            for value in ("false", "true", 0, 1, None):
                with (
                    self.subTest(field=field, value=value),
                    self.assertRaises(ValueError) as error,
                ):
                    self._resolve_with_config({field: value})

                self.assertIn(field, str(error.exception))

    def test_json_boolean_fields_report_their_full_paths(self) -> None:
        common_options = (
            "with_nerd_font",
            "fix_meta_table",
            "clean_cache",
            "narrow",
            "use_hinted",
        )
        cases: list[tuple[dict[str, Any], str]] = [
            ({"ligature": None}, "ligature"),
            ({"remove_tag_liga": 0}, "remove_tag_liga"),
            ({"nerd_font": {"enable": "false"}}, "nerd_font.enable"),
            ({"nerd_font": {"mono": 1}}, "nerd_font.mono"),
            ({"nerd_font": {"propo": None}}, "nerd_font.propo"),
            ({"nerd_font": {"variable": "true"}}, "nerd_font.variable"),
            (
                {"nerd_font": {"use_font_patcher": "true"}},
                "nerd_font.use_font_patcher",
            ),
            ({"cjk": {"locales": {"cn": "false"}}}, "cjk.locales.cn"),
            (
                {"cjk": {"locales": {"custom": [{"enable": 1}]}}},
                "cjk.locales.custom[0].enable",
            ),
        ]
        cases.extend(({"cjk": {key: "false"}}, f"cjk.{key}") for key in common_options)
        cases.append(({"cn": {"enable": None}}, "cn.enable"))
        cases.extend(({"cn": {key: "true"}}, f"cn.{key}") for key in common_options)

        for config_data, field in cases:
            with self.subTest(field=field), self.assertRaises(ValueError) as error:
                self._resolve_with_config(config_data)

            self.assertIn(field, str(error.exception))

    def test_real_booleans_remain_supported(self) -> None:
        font_config = self._resolve_with_config(
            {
                "use_hinted": False,
                "standard_zero": True,
                "ligature": True,
                "remove_tag_liga": True,
                "nerd_font": {
                    "enable": True,
                    "mono": False,
                    "propo": True,
                    "use_font_patcher": False,
                },
                "cjk": {
                    "locales": {"cn": False, "jp": True},
                    "with_nerd_font": True,
                    "fix_meta_table": False,
                    "clean_cache": True,
                    "narrow": False,
                    "use_hinted": True,
                },
            }
        )

        self.assertFalse(font_config.feature.hinted)
        self.assertTrue(font_config.feature.standard_zero)
        self.assertTrue(font_config.feature.liga)
        self.assertTrue(font_config.feature.remove_tag_liga)
        self.assertTrue(font_config.nerd_font.enable)
        self.assertFalse(font_config.nerd_font.mono)
        self.assertTrue(font_config.nerd_font.propo)
        self.assertFalse(font_config.nerd_font.use_font_patcher)
        self.assertEqual(font_config.cjk.locales.builtin_enabled_locales(), ["jp"])
        self.assertEqual(
            font_config.cjk.common_options,
            CJKCommonBuildOptions(
                with_nerd_font=True,
                fix_meta_table=False,
                clean_cache=True,
                narrow=False,
                use_hinted=True,
            ),
        )

    def test_false_legacy_cn_enable_preserves_cjk_locale_selection(self) -> None:
        font_config = self._resolve_with_config(
            {
                "cjk": {"locales": {"cn": True}},
                "cn": {"enable": False},
            }
        )

        self.assertEqual(font_config.cjk.locales.builtin_enabled_locales(), ["cn"])

    def test_infinite_arrow_accepts_boolean_or_null(self) -> None:
        for value in (None, True, False):
            with self.subTest(value=value):
                font_config = self._resolve_with_config({"infinite_arrow": value})

            self.assertIs(font_config.feature.infinite_arrow, value)

    def test_infinite_arrow_rejects_strings_and_integers(self) -> None:
        for value in ("false", "true", 0, 1):
            with self.subTest(value=value), self.assertRaises(ValueError) as error:
                self._resolve_with_config({"infinite_arrow": value})

            self.assertIn("infinite_arrow", str(error.exception))


class BuildConfigResolverCJKEntryTest(unittest.TestCase):
    def _resolve_with_config(
        self,
        config_data: dict,
        args: list[str] | None = None,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "config.json").write_text(
                json.dumps(config_data),
                encoding="utf-8",
            )
            resolver = BuildConfigResolver(project_root=tmp_path)
            return resolver.resolve(parse_args(args or []))

    def test_builtin_locale_booleans_resolve_to_entries(self) -> None:
        font_config = self._resolve_with_config(
            {
                "cjk": {
                    "locales": {
                        "cn": True,
                        "jp": False,
                        "tc": True,
                        "kr": False,
                        "custom": [],
                    }
                }
            }
        )

        self.assertEqual(
            [entry.entry_id for entry in font_config.get_selected_cjk_entries()],
            ["cn", "tc"],
        )

    def test_cjk_variable_resolves_from_project_config(self) -> None:
        font_config = self._resolve_with_config(
            {
                "cjk": {
                    "variable": True,
                    "locales": {},
                }
            }
        )

        self.assertEqual(font_config.cjk_output_format, "variable")

    def test_cjk_variable_cli_override_takes_precedence(self) -> None:
        font_config = self._resolve_with_config(
            {
                "cjk": {
                    "variable": False,
                    "locales": {},
                }
            },
            ["--cjk-variable"],
        )

        self.assertEqual(font_config.cjk_output_format, "variable")

    def test_rejects_non_boolean_cjk_variable(self) -> None:
        with self.assertRaisesRegex(ValueError, "cjk.variable must be a boolean"):
            self._resolve_with_config(
                {
                    "cjk": {
                        "variable": "yes",
                        "locales": {},
                    }
                }
            )

    def test_custom_enable_controls_resolved_entries(self) -> None:
        font_config = self._resolve_with_config(
            {
                "cjk": {
                    "locales": {
                        "cn": False,
                        "jp": False,
                        "tc": False,
                        "kr": False,
                        "custom": [
                            {
                                "enable": True,
                                "locale_name": "HK",
                                "source": {
                                    "path": "hk.ttf",
                                    "masters": {
                                        "100": {"wght": 100},
                                        "400": {"wght": 400},
                                        "800": {"wght": 800},
                                    },
                                },
                            },
                            {
                                "enable": False,
                                "locale_name": "MO",
                                "source": {
                                    "path": "mo.ttf",
                                    "masters": {
                                        "100": {"wght": 100},
                                        "400": {"wght": 400},
                                        "800": {"wght": 800},
                                    },
                                },
                            },
                        ],
                    }
                }
            }
        )

        entries = font_config.get_selected_cjk_entries()
        self.assertEqual([entry.entry_id for entry in entries], ["custom:hk"])
        self.assertEqual(entries[0].locale_name, "HK")

    def test_cjk_cli_only_enables_builtin_entries(self) -> None:
        font_config = self._resolve_with_config(
            {
                "cjk": {
                    "locales": {
                        "cn": False,
                        "jp": False,
                        "tc": False,
                        "kr": False,
                        "custom": [
                            {
                                "enable": True,
                                "locale_name": "HK",
                                "source": {
                                    "path": "hk.ttf",
                                    "masters": {
                                        "100": {"wght": 100},
                                        "400": {"wght": 400},
                                        "800": {"wght": 800},
                                    },
                                },
                            }
                        ],
                    }
                }
            },
            ["--cjk", "jp"],
        )

        self.assertEqual(
            [entry.entry_id for entry in font_config.get_selected_cjk_entries()],
            ["jp", "custom:hk"],
        )


class BuildConfigResolverCodepointAliasTest(unittest.TestCase):
    def _resolve(self, codepoint_alias):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config.json").write_text(
                json.dumps({"codepoint_alias": codepoint_alias}),
                encoding="utf-8",
            )
            return BuildConfigResolver(project_root=root).resolve(parse_args([]))

    def test_resolves_and_serializes_extra_codepoint_aliases(self) -> None:
        font_config = self._resolve({"0xE000": "0x004B"})

        self.assertEqual(font_config.codepoint_alias, {0xE000: 0x004B})
        self.assertEqual(
            font_config.to_dict()["metrics"]["codepoint_alias"],
            {"0xE000": "0x004B"},
        )
        self.assertEqual(
            font_config.to_build_record()["codepoint_alias"],
            {"0xE000": "0x004B"},
        )

    def test_empty_mapping_adds_no_extra_aliases(self) -> None:
        self.assertEqual(self._resolve({}).codepoint_alias, {})

    def test_rejects_invalid_unicode_scalars(self) -> None:
        for mapping in (
            {"2126": "0x03A9"},
            {"0x110000": "0x004B"},
            {"0xE000": "0xD800"},
            {"0xE000": "0xE000"},
        ):
            with self.subTest(mapping=mapping), self.assertRaises(ValueError):
                self._resolve(mapping)

    def test_rejects_overriding_builtin_alias(self) -> None:
        with self.assertRaisesRegex(ValueError, "built in"):
            self._resolve({"0x212A": "0x0041"})


class NerdFontDependencyTest(unittest.TestCase):
    def test_should_use_font_patcher_is_pure_decision(self) -> None:
        font_config = make_font_config()

        self.assertFalse(should_use_font_patcher(font_config))

        font_config.nerd_font.use_font_patcher = True
        self.assertTrue(should_use_font_patcher(font_config))

    def test_ensure_font_patcher_available_raises_for_missing_fontforge(self) -> None:
        runtime_context = make_runtime_context(Path("."))
        font_config = make_font_config()
        font_config.nerd_font.use_font_patcher = True

        with self.assertRaisesRegex(BuildDependencyError, "FontForge bin"):
            ensure_font_patcher_available(font_config, runtime_context)

    def test_ensure_font_patcher_available_raises_for_missing_patcher_assets(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fontforge_bin = tmp_path / "fontforge"
            fontforge_bin.write_text("", encoding="utf-8")

            runtime_context = make_runtime_context(tmp_path)
            runtime_context.font_forge_bin = str(fontforge_bin)
            font_config = make_font_config()
            font_config.nerd_font.use_font_patcher = True

            with (
                patch(
                    "scripts.pipeline.nerd_fonts.check_font_patcher",
                    return_value=False,
                ),
                self.assertRaisesRegex(
                    BuildDependencyError,
                    "Nerd Font Patcher assets",
                ),
            ):
                ensure_font_patcher_available(font_config, runtime_context)


class BuildRuntimeContextCacheTest(unittest.TestCase):
    def test_cache_skips_hinted_directory_when_not_required(self) -> None:
        font_config = make_font_config()
        font_config.behavior.formats = ["otf"]
        font_config.nerd_font.enable = False
        checked_paths: list[str] = []

        def record_check(dir_path: str, **_kwargs) -> bool:
            checked_paths.append(dir_path)
            return True

        with (
            patch("scripts.config.runtime.check_file_count", record_check),
            patch("scripts.config.runtime.get_font_forge_bin", return_value=None),
        ):
            runtime_context = BuildRuntimeContext.from_config(font_config)

        self.assertTrue(runtime_context.has_cache)
        self.assertFalse(any(path.endswith("TTF-AutoHint") for path in checked_paths))

    def test_cache_requires_hinted_directory_for_ttf_outputs(self) -> None:
        font_config = make_font_config()

        def reject_hinted(dir_path: str, **_kwargs) -> bool:
            return not dir_path.endswith("TTF-AutoHint")

        with (
            patch("scripts.config.runtime.check_file_count", reject_hinted),
            patch("scripts.config.runtime.get_font_forge_bin", return_value=None),
        ):
            runtime_context = BuildRuntimeContext.from_config(font_config)

        self.assertFalse(runtime_context.has_cache)


if __name__ == "__main__":
    unittest.main()
