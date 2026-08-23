from __future__ import annotations

import unittest

from ttfautohint import StemWidthMode

from scripts.font_ops.hinting import get_ttfautohint_options


class AutoHintOptionsTest(unittest.TestCase):
    def test_converts_stem_width_modes_without_mutating_config(self) -> None:
        params = {
            "hinting_limit": 180,
            "stem_width_mode": {
                "gray": "natural",
                "dw_cleartype": "quantized",
            },
        }

        options = get_ttfautohint_options(params)

        self.assertEqual(params["stem_width_mode"]["gray"], "natural")
        self.assertEqual(options["hinting_limit"], 180)
        self.assertNotIn("stem_width_mode", options)
        self.assertEqual(options["gray_stem_width_mode"], StemWidthMode.NATURAL)
        self.assertEqual(
            options["dw_cleartype_stem_width_mode"], StemWidthMode.QUANTIZED
        )

    def test_rejects_unknown_stem_width_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown stem width mode"):
            get_ttfautohint_options({"stem_width_mode": {"gray": "unsupported"}})
