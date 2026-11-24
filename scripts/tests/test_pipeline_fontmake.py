from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING, cast
from unittest.mock import MagicMock

from scripts.font_ops.fonttools import load_font
from scripts.pipeline.fontmake import (
    PreparedFontmakeSource,
    postprocess_static_font,
    prepare_fontmake_sources,
)
from scripts.tests.pipeline_fixtures import (
    make_font_config,
    make_runtime_context,
)
from scripts.tests.test_font_ops_metadata import _build_ribbi_test_font

if TYPE_CHECKING:
    from concurrent.futures import Executor


class PipelineFontmakeTest(unittest.TestCase):
    def test_prepare_sources_resolves_regular_vertical_metric(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            font_config = make_font_config()
            font_config.feature.line_height = 1.2
            runtime_context = make_runtime_context(tmp_path)
            executor_mock = MagicMock()
            executor_mock.map.return_value = (
                PreparedFontmakeSource(
                    "regular",
                    "regular.designspace",
                    (1100, -300),
                ),
                PreparedFontmakeSource(
                    "italic",
                    "italic.designspace",
                    (1080, -320),
                ),
            )

            context = prepare_fontmake_sources(
                font_config,
                runtime_context,
                cast("Executor", executor_mock),
            )

            self.assertEqual(runtime_context.resolved_vertical_metric, (1100, -300))
            self.assertEqual(len(context.sources), 2)
            jobs = executor_mock.map.call_args.args[1]
            self.assertEqual(
                {job.feature_file_path for job in jobs},
                {
                    runtime_context.feature_file_path(False),
                    runtime_context.feature_file_path(True),
                },
            )
            self.assertTrue(all(job.font_config is font_config for job in jobs))

    def test_postprocess_static_font_sets_ribbi_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            font_config = make_font_config()
            runtime_context = make_runtime_context(root)
            for style, is_italic, weight, exp_fs, exp_mac in (
                ("Regular", False, 400, 0xC0, 0x00),
                ("Bold", False, 700, 0xA0, 0x01),
                ("Italic", True, 400, 0x81, 0x02),
                ("BoldItalic", True, 700, 0xA1, 0x03),
                ("SemiBold", False, 600, 0xC0, 0x00),
                ("SemiBoldItalic", True, 600, 0x81, 0x02),
            ):
                with self.subTest(style=style):
                    src = root / "raw" / f"MapleMono-{style}.ttf"
                    font = _build_ribbi_test_font(
                        src,
                        italic_angle_deg=10.0 if is_italic else 0.0,
                        fs_selection=0xC0,
                        mac_style=0x00,
                        weight_class=weight,
                    )
                    font.close()
                    out_path = postprocess_static_font(
                        src,
                        root / "out",
                        font_config,
                        runtime_context,
                    )
                    saved = load_font(out_path)
                    try:
                        self.assertEqual(saved.table("OS/2").fsSelection, exp_fs)
                        self.assertEqual(saved.table("head").macStyle, exp_mac)
                    finally:
                        saved.close()


if __name__ == "__main__":
    unittest.main()
