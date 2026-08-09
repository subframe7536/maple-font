from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import MagicMock, patch

from scripts.cjk.builder import (
    CJKBuilder,
    autohint_static_fonts,
    create_font_executor,
    instantiate_cjk_static_from_variable,
    instantiate_variable_font_file,
)
from scripts.cjk.config import (
    CJKBuildConfig,
    CJKDownloadConfig,
    CJKOutputConfig,
    CJKSourceConfig,
    CJKWeightInstance,
)
from scripts.cjk.outlines import (
    convert_cff_master_files_to_glyf_tables_parallel,
    detect_outline_format,
)
from scripts.config.resolver import BuildConfigResolver
from scripts.errors import CJKSourceUnavailable

if TYPE_CHECKING:
    from concurrent.futures import Executor

    from scripts.font_ops.fonttools import TTFont


def make_config(output_dir: Path) -> CJKBuildConfig:
    source_path = output_dir / "source.ttf"
    source_path.write_bytes(b"source")
    return CJKBuildConfig(
        source=CJKSourceConfig(
            path=source_path,
            masters={100: {"wght": 100}, 400: {"wght": 400}, 800: {"wght": 800}},
            download=CJKDownloadConfig(
                url="https://example.com/source.7z",
                path_in_archive="source.ttf",
            ),
        ),
        output=CJKOutputConfig(dir=output_dir),
    )


class CJKExecutorOwnershipTest(unittest.TestCase):
    def test_static_autohint_uses_the_caller_executor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Regular.ttf").write_bytes(b"font")
            (root / "Bold.ttf").write_bytes(b"font")
            executor = cast("Executor", MagicMock())

            with patch("scripts.cjk.builder.run_process_jobs") as run_jobs:
                autohint_static_fonts(
                    root,
                    {},
                    pool_size=4,
                    executor=executor,
                )

            run_jobs.assert_called_once()
            self.assertIs(run_jobs.call_args.args[3], executor)
            jobs = run_jobs.call_args.args[2]
            self.assertEqual(
                [Path(job.input_path).name for job in jobs],
                ["Bold.ttf", "Regular.ttf"],
            )

    def test_static_instantiation_filters_compact_styles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_config(Path(tmp))
            static_dir = config.output.dir / config.output.static_dir
            existing_regular = (
                static_dir / f"{config.naming.static_file_prefix}-Regular.ttf"
            )
            existing_regular.parent.mkdir(parents=True)
            existing_regular.write_bytes(b"stale")
            stale_bold = static_dir / f"{config.naming.static_file_prefix}-Bold.ttf"
            stale_bold.write_bytes(b"stale")
            unrelated_font = static_dir / "OtherFamily-Bold.ttf"
            unrelated_font.write_bytes(b"unrelated")
            marker = static_dir / "existing-cache-marker"
            marker.write_text("preserve", encoding="utf-8")
            executor = cast("Executor", MagicMock())
            feature_font = MagicMock()
            regular_font = MagicMock()
            italic_font = MagicMock()
            axis = SimpleNamespace(minValue=100, defaultValue=400, maxValue=700)
            completed_future = MagicMock()
            cast("MagicMock", executor).submit.return_value = completed_future

            def assert_jobs_completed(*_args) -> None:
                self.assertEqual(completed_future.result.call_count, 2)

            with (
                patch(
                    "scripts.cjk.builder.load_feature_variable_font",
                    return_value=feature_font,
                ),
                patch(
                    "scripts.cjk.builder.load_font",
                    side_effect=(regular_font, italic_font),
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
                    "scripts.cjk.builder.write_static_hash",
                    side_effect=assert_jobs_completed,
                ) as write_hash,
            ):
                instantiate_cjk_static_from_variable(
                    config,
                    BuildConfigResolver().load_defaults(),
                    executor,
                    {"Regular", "Italic"},
                )

            jobs = [
                call.args[1]
                for call in cast("MagicMock", executor).submit.call_args_list
            ]
            self.assertEqual(
                [Path(job.output_path).stem for job in jobs],
                [
                    f"{config.naming.static_file_prefix}-Regular",
                    f"{config.naming.static_file_prefix}-Italic",
                ],
            )
            self.assertEqual(Path(jobs[0].output_path), existing_regular)
            self.assertFalse(stale_bold.exists())
            self.assertEqual(unrelated_font.read_bytes(), b"unrelated")
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")
            write_hash.assert_called_once_with(config, static_dir)
            cast("MagicMock", executor).shutdown.assert_not_called()

    def test_static_instantiation_without_filter_schedules_all_styles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_config(Path(tmp))
            executor = cast("Executor", MagicMock())
            axis = SimpleNamespace(minValue=100, defaultValue=400, maxValue=700)

            with (
                patch(
                    "scripts.cjk.builder.load_feature_variable_font",
                    return_value=MagicMock(),
                ),
                patch(
                    "scripts.cjk.builder.load_font",
                    side_effect=(MagicMock(), MagicMock()),
                ),
                patch("scripts.cjk.builder.weight_axis", return_value=axis),
                patch(
                    "scripts.cjk.builder.feature_weight_instances",
                    return_value=(
                        CJKWeightInstance("Regular", 400),
                        CJKWeightInstance("Bold", 700),
                    ),
                ),
                patch("scripts.cjk.builder.write_static_hash"),
            ):
                instantiate_cjk_static_from_variable(
                    config,
                    BuildConfigResolver().load_defaults(),
                    executor,
                )

            jobs = [
                call.args[1]
                for call in cast("MagicMock", executor).submit.call_args_list
            ]
            self.assertEqual(
                [Path(job.output_path).stem for job in jobs],
                [
                    f"{config.naming.static_file_prefix}-Regular",
                    f"{config.naming.static_file_prefix}-Bold",
                    f"{config.naming.static_file_prefix}-Italic",
                    f"{config.naming.static_file_prefix}-BoldItalic",
                ],
            )

    def test_static_instantiation_preserves_existing_cache_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_config(Path(tmp))
            static_dir = config.output.dir / config.output.static_dir
            sentinel = static_dir / "existing-cache-marker"
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text("preserve", encoding="utf-8")

            with (
                patch.object(
                    CJKBuilder,
                    "_build_static_fonts",
                    return_value=static_dir,
                ),
                patch("scripts.cjk.builder.write_static_hash"),
            ):
                result = instantiate_cjk_static_from_variable(
                    config,
                    BuildConfigResolver().load_defaults(),
                    cast("Executor", MagicMock()),
                )

            self.assertEqual(result, static_dir)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")

    def test_pool_size_one_uses_inline_execution(self) -> None:
        with patch("scripts.cjk.builder.create_process_executor") as create_process:
            executor = create_font_executor(1)
            future = executor.submit(lambda: "done")

        self.assertEqual(future.result(), "done")
        create_process.assert_not_called()

    def test_ci_uses_inline_execution_even_with_configured_pool(self) -> None:
        with (
            patch("scripts.cjk.builder.is_ci", return_value=True),
            patch("scripts.cjk.builder.create_process_executor") as create_process,
        ):
            executor = create_font_executor(4)
            future = executor.submit(lambda: "done")

        self.assertEqual(future.result(), "done")
        create_process.assert_not_called()

    def test_variable_instantiation_reads_raw_fonttools_tables(self) -> None:
        class RawFont:
            def __init__(self) -> None:
                self.head = SimpleNamespace(unitsPerEm=1000)
                self.saved = False
                self.closed = False

            def __contains__(self, tag: str) -> bool:
                return tag == "head"

            def __getitem__(self, tag: str) -> SimpleNamespace:
                if tag != "head":
                    raise KeyError(tag)
                return self.head

            def save(self, _path: str) -> None:
                self.saved = True

            def close(self) -> None:
                self.closed = True

        source = RawFont()
        instance = RawFont()
        with (
            patch("scripts.cjk.builder.load_font", return_value=source),
            patch(
                "scripts.cjk.builder.instantiate_variable_font", return_value=instance
            ),
        ):
            instantiate_variable_font_file(
                "source.ttf",
                "output.ttf",
                {"wght": 400},
                target_upem=1000,
            )

        self.assertTrue(instance.saved)
        self.assertTrue(instance.closed)
        self.assertTrue(source.closed)

    def test_builder_resolves_source_before_creating_executor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            builder = CJKBuilder(
                make_config(Path(tmp)), BuildConfigResolver().load_defaults()
            )
            download = builder.config.source.download
            assert download is not None

            with (
                patch(
                    "scripts.cjk.builder.resolve_cached_download",
                    side_effect=FileNotFoundError("download failed"),
                ) as resolve_source,
                patch("scripts.cjk.builder.create_font_executor") as create_executor,
                self.assertRaisesRegex(CJKSourceUnavailable, "download failed"),
            ):
                builder.build()

            resolve_source.assert_called_once_with(
                "CJK source font",
                builder.config.source.path,
                download.url,
                "github.com",
                path_in_archive="source.ttf",
            )
            create_executor.assert_not_called()

    def test_variable_artifacts_include_only_regular_and_italic_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = make_config(Path(tmp))
            regular = config.output.dir / config.output.regular_variable
            italic = config.output.dir / config.output.italic_variable
            unrelated = config.output.dir / "unrelated.ttf"
            for path in (regular, italic, unrelated):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"font")
            builder = CJKBuilder(config, BuildConfigResolver().load_defaults())

            with (
                patch("scripts.cjk.builder.write_variable_hash") as write_hash,
                patch("scripts.cjk.builder.archive") as create_archive,
            ):
                builder._write_variable_artifacts()

            write_hash.assert_called_once_with(config)
            create_archive.assert_called_once()
            self.assertEqual(
                create_archive.call_args.args[:2],
                (
                    str(config.output.dir),
                    str(config.output.dir / config.output.variable_archive_name),
                ),
            )
            include = create_archive.call_args.args[2]
            self.assertTrue(include(str(regular)))
            self.assertTrue(include(str(italic)))
            self.assertFalse(include(str(unrelated)))

    def test_builder_does_not_close_a_caller_owned_executor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            executor = cast("Executor", MagicMock())
            builder = CJKBuilder(
                make_config(Path(tmp)),
                BuildConfigResolver().load_defaults(),
                executor,
            )

            with (
                patch.object(
                    builder,
                    "_build_regular_variable_font",
                    side_effect=RuntimeError("stop"),
                ),
                self.assertRaisesRegex(RuntimeError, "stop"),
            ):
                builder.build()

            cast("MagicMock", executor).shutdown.assert_not_called()

    def test_builder_closes_an_executor_it_creates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            executor = MagicMock()
            builder = CJKBuilder(
                make_config(Path(tmp)), BuildConfigResolver().load_defaults()
            )

            with (
                patch(
                    "scripts.cjk.builder.create_font_executor", return_value=executor
                ),
                patch.object(
                    builder,
                    "_build_regular_variable_font",
                    side_effect=RuntimeError("stop"),
                ),
                self.assertRaisesRegex(RuntimeError, "stop"),
            ):
                builder.build()

            executor.shutdown.assert_called_once_with(
                wait=True,
                cancel_futures=True,
            )

    def test_cff_chunks_reuse_the_caller_owned_executor(self) -> None:
        executor = cast("Executor", MagicMock())
        future = MagicMock()
        future.result.return_value = {}
        cast("MagicMock", executor).submit.return_value = future

        with patch(
            "scripts.cjk.outlines.build_glyf_table",
            side_effect=(MagicMock(), MagicMock(), MagicMock()),
        ):
            tables = convert_cff_master_files_to_glyf_tables_parallel(
                ("thin.otf", "regular.otf", "bold.otf"),
                [".notdef"],
                executor,
            )

        self.assertEqual(len(tables), 3)
        cast("MagicMock", executor).submit.assert_called_once()


class CJKOutlineDetectionTest(unittest.TestCase):
    def make_font(self, *tables: str) -> TTFont:
        return cast("TTFont", {table: object() for table in tables})

    def test_detects_glyf_outline(self) -> None:
        self.assertEqual(
            detect_outline_format(self.make_font("glyf"), "source.ttf"),
            "glyf",
        )

    def test_detects_cff2_outline(self) -> None:
        self.assertEqual(
            detect_outline_format(self.make_font("CFF2"), "source.otf"),
            "cff2",
        )

    def test_rejects_static_cff_outline(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "static CFF.*source.otf.*variable font containing glyf or CFF2",
        ):
            detect_outline_format(self.make_font("CFF "), "source.otf")

    def test_rejects_missing_outline(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "no supported outlines.*source.bin.*exactly one of glyf or CFF2",
        ):
            detect_outline_format(self.make_font("name"), "source.bin")

    def test_rejects_ambiguous_variable_outlines(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "both glyf and CFF2.*source.ttf.*exactly one",
        ):
            detect_outline_format(
                self.make_font("glyf", "CFF2"),
                "source.ttf",
            )


if __name__ == "__main__":
    unittest.main()
