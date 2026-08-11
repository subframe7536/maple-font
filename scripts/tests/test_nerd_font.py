from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.config.resolver import BuildConfigResolver
from scripts.config.runtime import BuildRuntimeContext
from scripts.font_ops.nerd_font import NerdFontVariant, parse_codes_from_json
from scripts.pipeline.nerd_fonts import (
    build_nerd_font_variable_fonts,
    build_nerd_fonts,
)


class NerdFontHelpersTest(unittest.TestCase):
    def test_variant_preserves_nf_output_names(self) -> None:
        self.assertEqual(NerdFontVariant.from_options().symbol, "NF")
        self.assertEqual(NerdFontVariant.from_options(mono=True).suffix, "Mono")
        self.assertEqual(NerdFontVariant.from_options(mono=True).symbol, "NFM")
        self.assertEqual(
            NerdFontVariant.from_options(mono=True).directory_name, "NFMono"
        )
        self.assertEqual(
            NerdFontVariant.from_options(mono=True).cjk_directory_name("CN"),
            "NFMono-CN",
        )
        self.assertEqual(NerdFontVariant.from_options(propo=True).symbol, "NFP")
        self.assertEqual(
            NerdFontVariant.from_options(propo=True).directory_name, "NFPropo"
        )
        self.assertEqual(
            NerdFontVariant.from_options(mono=True, propo=True).suffix,
            "Propo",
        )

    def test_variant_resolves_font_patcher_flags(self) -> None:
        variant = NerdFontVariant.from_options(extra_args=("--mono",))
        self.assertEqual(variant.suffix, "Mono")
        with self.assertRaises(ValueError):
            NerdFontVariant.from_options(mono=True, propo=True, reject_conflict=True)

    def test_variant_builds_shared_paths(self) -> None:
        variant = NerdFontVariant.from_options(mono=True)
        self.assertEqual(
            variant.base_path("source"),
            Path("source/MapleMono-NF-Base-Mono.ttf"),
        )
        self.assertEqual(
            variant.patched_style_path("fonts", "MapleMono", "Italic"),
            Path("fonts/MapleMono-NFM-Italic.ttf"),
        )
        self.assertEqual(
            variant.patched_font_path("fonts", "MapleMono-Regular.ttf"),
            Path("fonts/MapleMonoNerdFontMono-Regular.ttf"),
        )

    def test_runtime_context_uses_variant_directories(self) -> None:
        config = BuildConfigResolver().load_defaults()
        for flags, directory in (
            ({}, "NF"),
            ({"mono": True}, "NFMono"),
            ({"propo": True}, "NFPropo"),
        ):
            with self.subTest(directory=directory):
                config.nerd_font.mono = flags.get("mono", False)
                config.nerd_font.propo = flags.get("propo", False)
                runtime_context = BuildRuntimeContext.from_config(config)
                self.assertEqual(
                    runtime_context.output_nf, str(Path("fonts") / directory)
                )
                self.assertEqual(
                    runtime_context.output_nf_variable,
                    str(Path("fonts") / f"Variable-{directory}"),
                )

    def test_parse_codes_from_json_loads_and_sorts_codes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "glyphnames.json"
            path.write_text(
                json.dumps(
                    {
                        "z": {"code": "e001"},
                        "a": {"code": "f0001"},
                        "duplicate": {"code": "e001"},
                        "metadata": {"name": "ignored"},
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(parse_codes_from_json(path), [0xE001, 0xF0001])

    def test_build_uses_explicit_inputs_and_preserves_stale_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = BuildConfigResolver().load_defaults()
            runtime_context = BuildRuntimeContext(
                src_dir="source",
                output_root=str(root / "fonts"),
                output_otf=str(root / "fonts" / "OTF"),
                output_ttf=str(root / "fonts" / "TTF"),
                output_ttf_hinted=str(root / "fonts" / "TTF-AutoHint"),
                output_variable=str(root / "fonts" / "Variable"),
                output_woff2=str(root / "fonts" / "Woff2"),
                output_nf=str(root / "fonts" / "NF"),
                ttf_base_dir=str(root / "fonts" / "TTF-AutoHint"),
                has_cache=False,
                is_nf_built=False,
                is_cjk_built=False,
                effective_github_mirror="github.com",
                font_forge_bin=None,
                resolved_vertical_metric=(1020, -300),
            )
            source_dir = Path(runtime_context.output_ttf_hinted)
            source_dir.mkdir(parents=True)
            current = source_dir / "MapleMono-Regular.ttf"
            stale = source_dir / "OldFamily-Regular.ttf"
            current.touch()
            stale.touch()
            executor = MagicMock()

            with patch(
                "scripts.pipeline.nerd_fonts.run_process_jobs",
                side_effect=lambda _size, _worker, jobs, _executor: [
                    job.output_path for job in jobs
                ],
            ) as run_jobs:
                outputs = build_nerd_fonts(
                    config,
                    runtime_context,
                    [current],
                    executor,
                )

            expected = Path(runtime_context.output_nf) / "MapleMono-NF-Regular.ttf"
            self.assertEqual(outputs, [expected])
            self.assertEqual(
                [job.font_path for job in run_jobs.call_args.args[2]],
                [current],
            )
            self.assertTrue(stale.is_file())

    def test_variable_build_uses_variable_output_names_and_preserves_inputs(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = BuildConfigResolver().load_defaults()
            config.nerd_font.variable = True
            runtime_context = BuildRuntimeContext(
                src_dir="source",
                output_root=str(root / "fonts"),
                output_otf=str(root / "fonts" / "OTF"),
                output_ttf=str(root / "fonts" / "TTF"),
                output_ttf_hinted=str(root / "fonts" / "TTF-AutoHint"),
                output_variable=str(root / "fonts" / "Variable"),
                output_woff2=str(root / "fonts" / "Woff2"),
                output_nf=str(root / "fonts" / "NF"),
                ttf_base_dir=str(root / "fonts" / "TTF"),
                has_cache=False,
                is_nf_built=False,
                is_cjk_built=False,
                effective_github_mirror="github.com",
                font_forge_bin=None,
                resolved_vertical_metric=(1020, -300),
            )
            variable_paths = [
                Path(runtime_context.output_variable) / "MapleMono[wght].ttf",
                Path(runtime_context.output_variable) / "MapleMono-Italic[wght].ttf",
            ]
            for variable_path in variable_paths:
                variable_path.parent.mkdir(parents=True, exist_ok=True)
                variable_path.touch()

            with patch(
                "scripts.pipeline.nerd_fonts.run_process_jobs",
                side_effect=lambda _size, _worker, jobs, _executor: [
                    job.output_path for job in jobs
                ],
            ):
                outputs = build_nerd_font_variable_fonts(
                    config,
                    runtime_context,
                    variable_paths,
                    executor=MagicMock(),
                )

            self.assertEqual(
                outputs,
                [
                    Path(runtime_context.output_nf_variable) / "MapleMono-NF[wght].ttf",
                    Path(runtime_context.output_nf_variable)
                    / "MapleMono-NF-Italic[wght].ttf",
                ],
            )
            self.assertTrue(all(path.is_file() for path in variable_paths))


if __name__ == "__main__":
    unittest.main()
