from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path
from typing import Any, cast

from scripts.cjk.cli import (
    add_cjk_arguments,
    apply_cli_overrides,
)
from scripts.cjk.config import (
    CJKSourceConfig,
    config_from_data,
    config_from_json,
    serialize_cjk_build_config,
)
from scripts.cjk.presets import build_preset_config, get_preset


def custom_config_data() -> dict[str, Any]:
    return {
        "locale_name": "HK",
        "source": {
            "path": "source.ttf",
            "masters": {
                "100": {"wght": 100},
                "400": {"wght": 400},
                "800": {"wght": 800},
            },
        },
    }


class CJKConfigSurfaceTest(unittest.TestCase):
    def test_freeze_feature_round_trips(self) -> None:
        data = custom_config_data()
        data["freeze_feature"] = "cv99"

        config = config_from_data(data)

        self.assertEqual(config.freeze_feature, "cv99")
        self.assertEqual(serialize_cjk_build_config(config)["freeze_feature"], "cv99")

    def test_rejects_non_object_config_sections(self) -> None:
        for field in (None, "source", "unicode", "transform"):
            data: Any = [] if field is None else custom_config_data()
            if field is not None:
                data[field] = []
            message = "CJK config" if field is None else field
            with (
                self.subTest(field=field),
                self.assertRaisesRegex(ValueError, rf"{message} must be an object"),
            ):
                config_from_data(cast("Any", data))

    def test_rejects_invalid_master_axes_and_coordinates(self) -> None:
        for axis, coordinate, message in (
            ("", 100, "axis tags"),
            ("ROUND", 100, "axis tags"),
            ("圆", 100, "axis tags"),
            ("wght", "100", "finite number"),
            ("wght", float("nan"), "finite number"),
            ("wght", float("inf"), "finite number"),
        ):
            data = custom_config_data()
            data["source"]["masters"]["100"] = {axis: coordinate}
            with (
                self.subTest(axis=axis, coordinate=coordinate),
                self.assertRaisesRegex(ValueError, message),
            ):
                config_from_data(data)

    def test_rejects_invalid_transform_numbers(self) -> None:
        for field, value, message in (
            ("target_advance_width", 0, "greater than zero"),
            ("target_advance_width", 1.5, "must be an integer"),
            ("x_scale", "1", "finite number"),
            ("x_scale", 0, "scale factors"),
            ("y_scale", -1, "scale factors"),
            ("x_scale", float("nan"), "finite number"),
            ("italic_angle", float("inf"), "finite number"),
            ("x_shift", 1.5, "must be an integer"),
        ):
            data = custom_config_data()
            data["transform"] = {field: value}
            with (
                self.subTest(field=field, value=value),
                self.assertRaisesRegex(ValueError, message),
            ):
                config_from_data(data)

    def test_rejects_invalid_collection_and_boolean_fields(self) -> None:
        cases = (
            ("source", "drop_tables", "GPOS", "drop_tables"),
            ("source", "drop_tables", ["GPOS", "GPOS"], "duplicates"),
            ("unicode", "ranges", "0x3000", "ranges must be a list"),
            (
                "unicode",
                "exclude_feature_codepoints",
                1,
                "must be a boolean",
            ),
        )
        for section, field, value, message in cases:
            data = custom_config_data()
            data.setdefault(section, {})[field] = value
            with (
                self.subTest(section=section, field=field),
                self.assertRaisesRegex(ValueError, message),
            ):
                config_from_data(data)

    def test_outline_mode_is_removed_from_public_config(self) -> None:
        parser = argparse.ArgumentParser()
        add_cjk_arguments(parser)
        schema = json.loads(
            Path("sources/cjk/cjk_schema.json").read_text(encoding="utf-8")
        )
        config = build_preset_config("cn")

        self.assertNotIn(
            "outline_mode", {field.name for field in fields(CJKSourceConfig)}
        )
        self.assertNotIn("outline_mode", {action.dest for action in parser._actions})
        self.assertNotIn(
            "outline_mode",
            schema["properties"]["source"]["properties"],
        )
        self.assertNotIn(
            "outline_mode",
            serialize_cjk_build_config(config)["source"],
        )

    def test_rejects_removed_outline_mode_with_migration_help(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "outline_mode was removed; delete it.*detected automatically",
        ):
            config_from_data(
                {
                    "locale_name": "HK",
                    "source": {
                        "path": "source.ttf",
                        "outline_mode": "glyf",
                        "masters": {
                            "100": {"wght": 100},
                            "400": {"wght": 400},
                            "800": {"wght": 800},
                        },
                    },
                }
            )

    def test_rejects_unknown_source_field_with_supported_names(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Unsupported source field.*unexpected.*Supported fields",
        ):
            config_from_data(
                {
                    "locale_name": "HK",
                    "source": {
                        "path": "source.ttf",
                        "unexpected": True,
                        "masters": {
                            "100": {"wght": 100},
                            "400": {"wght": 400},
                            "800": {"wght": 800},
                        },
                    },
                }
            )

    def test_download_round_trips_when_configured(self) -> None:
        config = config_from_data(
            {
                "locale_name": "HK",
                "source": {
                    "path": "source.ttf",
                    "download": {
                        "url": "https://example.com/source.7z",
                        "path_in_archive": "fonts/source.ttf",
                    },
                    "masters": {
                        "100": {"wght": 100},
                        "400": {"wght": 400},
                        "800": {"wght": 800},
                    },
                },
            }
        )

        self.assertIsNotNone(config.source.download)
        assert config.source.download is not None
        self.assertEqual(config.source.download.url, "https://example.com/source.7z")
        self.assertEqual(
            config.source.download.path_in_archive,
            "fonts/source.ttf",
        )
        self.assertEqual(
            serialize_cjk_build_config(config)["source"]["download"],
            {
                "url": "https://example.com/source.7z",
                "path_in_archive": "fonts/source.ttf",
            },
        )

    def test_download_is_omitted_when_not_configured(self) -> None:
        config = config_from_data(
            {
                "locale_name": "HK",
                "source": {
                    "path": "source.ttf",
                    "masters": {
                        "100": {"wght": 100},
                        "400": {"wght": 400},
                        "800": {"wght": 800},
                    },
                },
            }
        )

        self.assertNotIn("download", serialize_cjk_build_config(config)["source"])

    def test_rejects_unsafe_download_archive_paths(self) -> None:
        for path in ("", "/font.otf", "C:/font.otf", "../font.otf", "a\\font.otf"):
            with (
                self.subTest(path=path),
                self.assertRaisesRegex(
                    ValueError,
                    "path_in_archive",
                ),
            ):
                config_from_data(
                    {
                        "locale_name": "HK",
                        "source": {
                            "path": "source.ttf",
                            "download": {
                                "url": "https://example.com/source.7z",
                                "path_in_archive": path,
                            },
                            "masters": {
                                "100": {"wght": 100},
                                "400": {"wght": 400},
                                "800": {"wght": 800},
                            },
                        },
                    }
                )

    def test_rejects_invalid_download_object(self) -> None:
        base_source = {
            "path": "source.ttf",
            "masters": {
                "100": {"wght": 100},
                "400": {"wght": 400},
                "800": {"wght": 800},
            },
        }
        for download, message in (
            (None, "must be an object"),
            ({}, "download.url"),
            ({"url": ""}, "download.url"),
            (
                {"url": "https://example.com/source.ttf", "unexpected": True},
                "Unsupported source.download field",
            ),
        ):
            with (
                self.subTest(download=download),
                self.assertRaisesRegex(
                    ValueError,
                    message,
                ),
            ):
                config_from_data(
                    {
                        "locale_name": "HK",
                        "source": {**base_source, "download": download},
                    }
                )

    def test_zero_italic_angle_is_an_explicit_override(self) -> None:
        parser = argparse.ArgumentParser()
        add_cjk_arguments(parser)
        args = parser.parse_args(["--italic-angle", "0"])

        config = apply_cli_overrides(build_preset_config("cn"), args)

        self.assertEqual(config.transform.italic_angle, 0)

    def test_source_override_does_not_reuse_preset_download(self) -> None:
        parser = argparse.ArgumentParser()
        add_cjk_arguments(parser)
        args = parser.parse_args(["--source", "custom.ttf"])

        config = apply_cli_overrides(build_preset_config("cn"), args)

        self.assertEqual(config.source.path, Path("custom.ttf"))
        self.assertIsNone(config.source.download)

    def test_non_positive_scale_is_rejected(self) -> None:
        parser = argparse.ArgumentParser()
        add_cjk_arguments(parser)
        args = parser.parse_args(["--x-scale", "0"])

        with self.assertRaisesRegex(ValueError, "scale factors"):
            apply_cli_overrides(build_preset_config("cn"), args)

    def test_config_from_json_rejects_feature_font(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "custom.json"
            config_path.write_text(
                json.dumps(
                    {
                        "locale_name": "HK",
                        "feature_font": "feature.ttf",
                        "source": {
                            "path": "source.ttf",
                            "masters": {
                                "100": {"wght": 100},
                                "400": {"wght": 400},
                                "800": {"wght": 800},
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "feature_font"):
                config_from_json(config_path)

    def test_add_cjk_arguments_does_not_expose_feature_font(self) -> None:
        parser = argparse.ArgumentParser()
        add_cjk_arguments(parser)

        self.assertNotIn(
            "feature_font",
            {action.dest for action in parser._actions},
        )

    def test_cjk_schema_removes_feature_font(self) -> None:
        schema = json.loads(
            Path("sources/cjk/cjk_schema.json").read_text(encoding="utf-8")
        )

        self.assertNotIn("feature_font", schema["properties"])

    def test_cjk_schema_exposes_optional_download_object(self) -> None:
        schema = json.loads(
            Path("sources/cjk/cjk_schema.json").read_text(encoding="utf-8")
        )
        source_schema = schema["properties"]["source"]

        self.assertIn("download", source_schema["properties"])
        self.assertNotIn("download", source_schema["required"])
        self.assertEqual(
            source_schema["properties"]["download"]["required"],
            ["url"],
        )
        self.assertNotIn("download_url", source_schema["properties"])

    def test_builtin_jp_download_selects_fixed_archive_member(self) -> None:
        config = config_from_json("sources/cjk/jp/config-jp.json")

        self.assertEqual(
            get_preset("jp").config_path,
            Path("sources/cjk/jp/config-jp.json"),
        )
        self.assertEqual(
            config.source.path.resolve(),
            Path("sources/cjk/variable-source/ResourceHanRoundedJP-VF.otf").resolve(),
        )
        self.assertIsNotNone(config.source.download)
        assert config.source.download is not None
        self.assertEqual(
            config.source.download.url,
            "https://github.com/CyanoHao/Resource-Han-Rounded/releases/"
            "download/v1.910/RHR-CFF2-JP-1.910.7z",
        )
        self.assertEqual(
            config.source.download.path_in_archive,
            "ResourceHanRoundedJP-VF.otf",
        )

    def test_top_level_schema_wraps_custom_entries_with_enable(self) -> None:
        schema = json.loads(Path("sources/schema.json").read_text(encoding="utf-8"))
        custom_item = schema["properties"]["cjk"]["properties"]["locales"][
            "properties"
        ]["custom"]["items"]

        self.assertEqual(
            custom_item["allOf"][1]["properties"]["enable"]["type"], "boolean"
        )


if __name__ == "__main__":
    unittest.main()
