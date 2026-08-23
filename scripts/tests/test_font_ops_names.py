from __future__ import annotations

import unittest
from pathlib import Path

from fontTools.ttLib.tables._f_v_a_r import NamedInstance

from scripts.cjk.config import CJKBuildConfig, CJKSourceConfig
from scripts.cjk.postprocess import update_variable_font_names
from scripts.cjk.static import (
    apply_cjk_names,
    build_cjk_family_name,
    build_cjk_postscript_prefix,
)
from scripts.config.resolver import BuildConfigResolver
from scripts.font_ops.fonttools import TTFont, newTable
from scripts.font_ops.names import get_font_name, set_font_name, update_font_names


def make_font() -> TTFont:
    font = TTFont()
    font["name"] = newTable("name")
    font["name"].names = []
    return font


def make_font_config():
    config = BuildConfigResolver().load_defaults()
    config.identity.beta = "beta.1"
    return config


def get_unicode_name(font: TTFont, name_id: int) -> str:
    record = font["name"].getName(
        nameID=name_id, platformID=3, platEncID=1, langID=0x409
    )
    assert record is not None
    return record.toUnicode()


class FontNameTest(unittest.TestCase):
    def test_variable_instances_have_unique_names(self) -> None:
        font = make_font()
        font["fvar"] = newTable("fvar")
        font["fvar"].axes = []
        font["fvar"].instances = []
        for weight in (100, 400, 700):
            instance = NamedInstance()
            instance.subfamilyNameID = 2
            instance.postscriptNameID = 0xFFFF
            instance.coordinates = {"wght": weight}
            font["fvar"].instances.append(instance)

        config = make_font_config()
        update_font_names(
            font=font,
            font_config=config,
            family_name="Maple Mono",
            style_name="Regular",
            full_name="Maple Mono Regular",
            postscript_name="MapleMono-Regular",
            is_skip_subfamily=True,
            variable=True,
        )

        self.assertEqual(
            [
                font["name"].getDebugName(instance.subfamilyNameID)
                for instance in font["fvar"].instances
            ],
            ["Thin", "Regular", "Bold"],
        )
        self.assertEqual(
            [
                font["name"].getDebugName(instance.postscriptNameID)
                for instance in font["fvar"].instances
            ],
            ["MapleMono-Thin", "MapleMono-Regular", "MapleMono-Bold"],
        )

    def test_update_font_names_builds_identifier_from_config(self) -> None:
        font = make_font()
        config = make_font_config()

        update_font_names(
            font=font,
            font_config=config,
            family_name="Maple Mono NF CN",
            style_name="Regular",
            full_name="Maple Mono NF CN Regular",
            postscript_name="MapleMono-NF-CN-Regular",
            is_skip_subfamily=True,
            narrow=True,
            variable=True,
        )

        self.assertEqual(get_font_name(font, 5), "Version 7.900")
        self.assertEqual(
            get_font_name(font, 3),
            "Version 7.900-beta.1;SUBF;MapleMono-NF-CN-Regular;"
            f"2026;FL830;Variable;NF{config.nerd_font.version};Narrow;+calt;",
        )

    def test_cjk_variable_names_use_project_identifier(self) -> None:
        font = make_font()
        config = make_font_config()
        cjk_config = CJKBuildConfig(
            source=CJKSourceConfig(
                path=Path("source.ttf"),
                masters={100: {"wght": 100}, 400: {"wght": 400}, 800: {"wght": 800}},
            ),
        )

        update_variable_font_names(font, "Regular", cjk_config, config)

        self.assertEqual(get_font_name(font, 5), "Version 7.900")
        self.assertEqual(
            get_font_name(font, 3),
            "Version 7.900-beta.1;SUBF;MapleMonoCJK-Regular;2026;FL830;+calt;",
        )

    def test_cjk_static_names_use_project_identifier(self) -> None:
        font = make_font()
        config = make_font_config()

        apply_cjk_names(font, config, "CN", "Regular", narrow=True)

        self.assertEqual(get_font_name(font, 5), "Version 7.900")
        self.assertEqual(
            get_font_name(font, 3),
            "Version 7.900-beta.1;SUBF;MapleMono-CN-Regular;2026;FL830;Narrow;+calt;",
        )

    def test_nf_cjk_static_names_do_not_repeat_nf_marker(self) -> None:
        config = make_font_config()
        config.identity.family_name = "Maple Mono NF"
        config.identity.family_name_compact = "MapleMono-NF"

        self.assertEqual(build_cjk_family_name(config, "NF-CN"), "Maple Mono NF CN")
        self.assertEqual(
            build_cjk_postscript_prefix(config, "NF-CN"), "MapleMono-NF-CN"
        )

    def test_skip_subfamily_removes_stale_name_ids_16_and_17(self) -> None:
        font = make_font()
        # Pre-seed stale base-font values to simulate what NF merging inherits
        set_font_name(font, "Maple Mono", 16)
        set_font_name(font, "Bold", 17)
        config = make_font_config()

        update_font_names(
            font=font,
            font_config=config,
            family_name="Maple Mono NF",
            style_name="Bold",
            full_name="Maple Mono NF Bold",
            postscript_name="MapleMono-NF-Bold",
            is_skip_subfamily=True,
        )

        self.assertIsNone(
            font["name"].getName(nameID=16, platformID=3, platEncID=1, langID=0x409)
        )
        self.assertIsNone(
            font["name"].getName(nameID=17, platformID=3, platEncID=1, langID=0x409)
        )

    def test_skip_subfamily_writes_name_ids_16_and_17_for_variable(self) -> None:
        font = make_font()
        font["fvar"] = newTable("fvar")
        font["fvar"].axes = []
        font["fvar"].instances = []
        config = make_font_config()

        # With explicit preferred names
        update_font_names(
            font=font,
            font_config=config,
            family_name="Maple Mono NF",
            style_name="Regular",
            full_name="Maple Mono NF Regular",
            postscript_name="MapleMono-NF-Regular",
            is_skip_subfamily=True,
            preferred_family_name="Maple Mono NF",
            preferred_style_name="Regular",
            variable=True,
        )

        self.assertEqual(
            get_unicode_name(font, 16),
            "Maple Mono NF",
        )
        self.assertEqual(
            get_unicode_name(font, 17),
            "Regular",
        )

    def test_variable_falls_back_to_family_name_for_ids_16_and_17(self) -> None:
        font = make_font()
        font["fvar"] = newTable("fvar")
        font["fvar"].axes = []
        font["fvar"].instances = []
        config = make_font_config()

        # Without preferred names — should fall back to family_name / style_name
        update_font_names(
            font=font,
            font_config=config,
            family_name="Maple Mono NF",
            style_name="Bold",
            full_name="Maple Mono NF Bold",
            postscript_name="MapleMono-NF-Bold",
            is_skip_subfamily=True,
            variable=True,
        )

        self.assertEqual(
            get_unicode_name(font, 16),
            "Maple Mono NF",
        )
        self.assertEqual(
            get_unicode_name(font, 17),
            "Bold",
        )


if __name__ == "__main__":
    unittest.main()
