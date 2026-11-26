from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

from fontTools.ttLib.tables.ttProgram import Program

from scripts.font_ops.fonttools import load_font, newTable
from scripts.pipeline.cache import (
    CACHE_SCHEMA,
)
from scripts.pipeline.cjk_outputs import (
    CJKStaticMergeJob,
    _merge_cjk_variable_font,
    cjk_static_base_profiles,
    merge_cached_cjk_static_font_job,
)
from scripts.pipeline.orchestrator import MapleBuildPipeline
from scripts.tests.cjk_font_fixtures import build_test_font
from scripts.tests.pipeline_fixtures import (
    make_custom_entry,
    make_font_config,
    make_runtime_context,
    write_test_font,
)
from scripts.utils.errors import BuildDependencyError


class PipelineCJKOutputsTest(unittest.TestCase):
    def test_vf_autohint_failure_does_not_publish_font(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            core, extra = root / "core.ttf", root / "cjk.ttf"
            core.touch()
            extra.touch()
            entry = make_custom_entry("CN")
            entry.common_options.variable_autohint = True
            with (
                patch("scripts.pipeline.cjk_outputs.load_font"),
                patch(
                    "scripts.pipeline.cjk_outputs.merge_vf",
                    return_value=(MagicMock(), [], 0),
                ),
                patch("scripts.pipeline.cjk_outputs._postprocess_cjk_variable_font"),
                patch(
                    "scripts.pipeline.cjk_outputs._update_cjk_variable_names",
                    return_value="MapleMono-CN",
                ),
                patch(
                    "scripts.pipeline.cjk_outputs.autohint_variable_han",
                    side_effect=BuildDependencyError("invalid hint output"),
                ),
                patch("scripts.pipeline.cjk_outputs.save_font_atomic") as publish,
                self.assertRaisesRegex(BuildDependencyError, "invalid hint output"),
            ):
                _merge_cjk_variable_font(
                    entry, make_font_config(), core, extra, root, False, "CN", None
                )
            publish.assert_not_called()

    def test_cached_static_merge_removes_extra_overlaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            entry = make_custom_entry("JP")
            runtime_context = make_runtime_context(Path(tmp))
            font = MagicMock()
            job = CJKStaticMergeJob(
                entry=entry,
                style_compact="Regular",
                core_path="core.ttf",
                cjk_base_path="cjk-base.ttf",
                output_dir=tmp,
                font_config=make_font_config(),
                runtime_context=runtime_context,
                locale_suffix="JP",
            )

            with (
                patch(
                    "scripts.pipeline.cjk_outputs.merge_ttfonts", return_value=font
                ) as merge,
                patch(
                    "scripts.pipeline.cjk_outputs.postprocess_cjk_extended_static_font",
                    return_value="MapleMono-JP-Regular",
                ),
                patch("scripts.pipeline.cjk_outputs.save_font_atomic"),
            ):
                merge_cached_cjk_static_font_job(job)

            merge.assert_called_once_with(
                base_font_path="core.ttf",
                extra_font_path="cjk-base.ttf",
                remove_extra_overlaps=True,
            )
            font.close.assert_called_once()

    def test_cached_static_merge_preserves_existing_base_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            core_path, cjk_path = root / "core.ttf", root / "cjk.ttf"
            with build_test_font(
                core_path, glyph_order=[".notdef", "box"], box_width=350
            ) as core:
                glyphs = core.table("glyf")
                instructions = b"\xb0\x00\x2b"  # PUSHB 0; CALL
                program = Program()
                program.fromBytecode(instructions)
                glyphs["box"].program = program
                glyphs.glyphs["box.1"] = deepcopy(glyphs["box"])
                core.setGlyphOrder([*core.getGlyphOrder(), "box.1"])
                core.table("hmtx")["box.1"] = (600, 50)
                expected_tables = {
                    "fpgm": b"\xb0\x00\x2c\x2d",  # Define empty function 0.
                    "prep": b"\x18",  # RTG
                    "cvt ": b"\x00\x40",
                }
                for tag, data in expected_tables.items():
                    table = newTable(tag)
                    table.decompile(data, core)
                    core[tag] = table
                maxp = core.table("maxp")
                maxp.maxFunctionDefs = 1
                maxp.maxStackElements = 1
                maxp.maxSizeOfInstructions = len(instructions)
                core.save(core_path)
            with build_test_font(
                cjk_path, glyph_order=[".notdef", "cjk"], cjk_width=950
            ):
                pass

            config = make_font_config()
            config.feature.hinted = True
            config.behavior.apply_fea_file = True
            runtime_context = make_runtime_context(root)
            runtime_context.src_dir = tmp
            feature_path = Path(runtime_context.feature_file_path(False, True))
            feature_path.parent.mkdir()
            feature_path.write_text("languagesystem DFLT dflt;\n", encoding="utf-8")
            entry = make_custom_entry("CN")
            merge_cached_cjk_static_font_job(
                CJKStaticMergeJob(
                    entry=entry,
                    style_compact="Regular",
                    core_path=str(core_path),
                    cjk_base_path=str(cjk_path),
                    output_dir=tmp,
                    font_config=config,
                    runtime_context=runtime_context,
                    locale_suffix="NF-CN",
                )
            )

            with load_font(root / "MapleMono-NF-CN-Regular.ttf") as output:
                self.assertEqual(len(output.getGlyphOrder()), 3)
                cmap = output.getBestCmap() or {}
                self.assertEqual(set(cmap), {0x41, 0x4E00})
                glyphs = output.table("glyf")
                self.assertEqual(glyphs[cmap[0x41]].program.getBytecode(), instructions)
                self.assertFalse(glyphs[cmap[0x4E00]].program.getBytecode())
                for tag, expected in expected_tables.items():
                    self.assertEqual(output.getTableData(tag), expected, tag)

    def test_cjk_stage_invalidation_preserves_other_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "fonts"
            root.mkdir()
            font_config = make_font_config()
            font_config.behavior.cache = True
            pipeline = MapleBuildPipeline(font_config, make_runtime_context(Path(tmp)))
            pipeline._cache_tracker._cache_record = {
                "schema": CACHE_SCHEMA,
                "stages": {
                    "jp-static": {"key": "old-jp"},
                    "cn-static": {"key": "keep-cn"},
                },
            }
            pipeline._invalidate_recorded_stage("jp-static")

            record = json.loads((root / "build-cache.json").read_text())
            self.assertEqual(record["stages"], {"cn-static": {"key": "keep-cn"}})

    def test_cjk_stage_paths_only_include_target_styles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            font_config = make_font_config()
            font_config.behavior.debug = True
            font_config.cjk.entries = [make_custom_entry("JP")]
            runtime_context = make_runtime_context(Path(tmp))
            output_dir = Path(runtime_context.output_root) / "JP"
            write_test_font(output_dir / "MapleMono-JP-Regular.ttf")
            write_test_font(output_dir / "MapleMono-JP-Italic.ttf")
            write_test_font(output_dir / "MapleMono-JP-Bold.ttf")

            pipeline = MapleBuildPipeline(font_config, runtime_context)
            self.assertEqual(
                {path.name for path in pipeline._cjk_stage_paths("JP")},
                {"MapleMono-JP-Regular.ttf", "MapleMono-JP-Italic.ttf"},
            )

    def test_cjk_variable_stage_paths_only_include_current_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            font_config = make_font_config()
            font_config.behavior.cjk_output_format = "variable"
            font_config.cjk.entries = [make_custom_entry("JP")]
            runtime_context = make_runtime_context(Path(tmp))
            output_dir = Path(runtime_context.output_root) / "Variable-JP"
            write_test_font(output_dir / "MapleMono-JP[wght].ttf")
            write_test_font(output_dir / "MapleMono-JP-Italic[wght].ttf")
            write_test_font(output_dir / "MapleMono-OLD[wght].ttf")

            pipeline = MapleBuildPipeline(font_config, runtime_context)
            self.assertEqual(
                {path.name for path in pipeline._cjk_stage_paths("JP")},
                {"MapleMono-JP[wght].ttf", "MapleMono-JP-Italic[wght].ttf"},
            )

    def test_cjk_cache_stages_split_locale_and_nf_profiles(self) -> None:
        runtime_context = make_runtime_context(Path("/tmp/maple-font-stage-test"))
        font_config = make_font_config()
        font_config.behavior.use_cjk_both = True
        font_config.cjk.entries = [make_custom_entry("HK"), make_custom_entry("JP")]
        runtime_context.is_nf_built = True
        pipeline = MapleBuildPipeline(font_config, runtime_context)

        self.assertEqual(
            [stage for stage, _entry, _locale in pipeline._cjk_stage_targets()],
            [
                "nf-hk-static",
                "hk-static",
                "nf-jp-static",
                "jp-static",
            ],
        )
        self.assertNotEqual(
            pipeline._stage_cache_identity("hk-static"),
            pipeline._stage_cache_identity("jp-static"),
        )

    def test_cjk_cache_record_uses_the_upstream_stage_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            font_config = make_font_config()
            font_config.behavior.cache = True
            font_config.behavior.debug = True
            font_config.cjk.entries = [make_custom_entry("JP")]
            runtime_context = make_runtime_context(Path(tmp))
            pipeline = MapleBuildPipeline(font_config, runtime_context)
            paths = pipeline._cjk_stage_expected_paths("JP")
            for path in paths:
                write_test_font(path)

            pipeline._mark_stage_rebuilt("jp-static", paths)
            pipeline.write_cache_record()

            record = json.loads(
                (Path(runtime_context.output_root) / "build-cache.json").read_text()
            )
            self.assertEqual(
                record["stages"]["jp-static"]["key"],
                pipeline._stage_cache_identity("jp-static"),
            )

    def test_static_cjk_profiles_use_nfpropo_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_context = make_runtime_context(Path(tmp))
            runtime_context.is_nf_built = True
            font_config = make_font_config()
            font_config.nerd_font.propo = True
            entry = make_custom_entry("HK")

            profiles = cjk_static_base_profiles(font_config, runtime_context, entry)

            self.assertEqual(
                [profile.output_locale for profile in profiles], ["NFPropo-HK"]
            )
            self.assertEqual(profiles[0].base_dir, runtime_context.output_nf)


if __name__ == "__main__":
    unittest.main()
