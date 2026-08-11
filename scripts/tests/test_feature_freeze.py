from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from ufoLib2 import Font as UFOFont
from ufoLib2.objects import Anchor

from scripts.config.base import ResolvedConfig, normalize_feature_freeze
from scripts.feature.apply import (
    FeatureSubstitution,
    apply_standard_zero,
    apply_ufo_substitutions,
    prepare_feature_source,
)
from scripts.feature.compiler import generate_fea_string, generate_fea_string_cn_only
from scripts.font_ops.fonttools import TTFont


class FeatureFreezeConfigTest(unittest.TestCase):
    def test_normalizes_enabled_disabled_and_ignored_features(self) -> None:
        self.assertEqual(
            normalize_feature_freeze(
                {
                    "cv01": "enabled",
                    "cv02": "disabled",
                    "cv03": "ignore",
                },
                calt=True,
            ),
            {"cv01": "1", "cv02": "-1", "cv03": "0", "calt": "1"},
        )

    def test_rejects_invalid_feature_freeze_value(self) -> None:
        with self.assertRaisesRegex(
            TypeError,
            r"Invalid freeze config item: \{ cv01: unexpected \}",
        ):
            normalize_feature_freeze({"cv01": "unexpected"}, calt=False)

    def test_resolved_config_uses_normalized_freeze_values(self) -> None:
        config = ResolvedConfig(feature_freeze={"cv01": "enable", "cv02": "disable"})
        config.feature.liga = False

        self.assertEqual(config.freeze_config_str, "-calt;+cv01;-cv02;")


class FeatureApplicationTest(unittest.TestCase):
    @staticmethod
    def _add_zero_glyph(font: UFOFont, name: str, width: int, unicode: int | None):
        glyph = font.newGlyph(name)
        glyph.width = width
        if unicode is not None:
            glyph.unicodes = [unicode]
        pen = glyph.getPointPen()
        pen.beginPath()
        pen.addPoint((0, 0), "move")
        pen.addPoint((width // 2, 100), "line")
        pen.addPoint((width, 0), "line")
        pen.endPath()
        return glyph

    def test_standard_zero_swaps_roles_without_replacing_glyph_metadata(self) -> None:
        font = UFOFont()
        zero = self._add_zero_glyph(font, "zero", 600, 0x30)
        dotted_zero = self._add_zero_glyph(font, "zero.zero", 500, None)
        zero.lib["role"] = "default"
        dotted_zero.lib["role"] = "alternate"
        descriptor = SourceDescriptor()
        descriptor.font = font
        designspace = DesignSpaceDocument()
        designspace.addSource(descriptor)

        apply_standard_zero(designspace)

        self.assertEqual(zero.width, 500)
        self.assertEqual(dotted_zero.width, 600)
        self.assertEqual(zero.unicodes, [0x30])
        self.assertEqual(dotted_zero.unicodes, [])
        self.assertEqual(zero.lib["role"], "default")
        self.assertEqual(dotted_zero.lib["role"], "alternate")
        self.assertEqual(zero.getBounds(font), (0, 0, 500, 100))
        self.assertEqual(dotted_zero.getBounds(font), (0, 0, 600, 100))

        apply_ufo_substitutions(
            designspace,
            (FeatureSubstitution("zero", "zero", "zero.zero"),),
        )
        self.assertEqual(zero.width, 600)
        self.assertEqual(zero.getBounds(font), (0, 0, 600, 100))

    def _prepare_file(
        self,
        root: Path,
        source: str,
        config: ResolvedConfig,
        glyph_names: tuple[str, ...] = (".notdef", "a", "a.alt", "b", "b.alt"),
    ):
        feature_path = root / "test.fea"
        feature_path.write_text(source, encoding="utf-8")
        config.behavior.apply_fea_file = True
        prepared = prepare_feature_source(
            config,
            glyph_names=glyph_names,
            issue_fea_dir=root,
            is_italic=False,
            is_cn=False,
            is_hinted=False,
            fea_path=str(feature_path),
        )
        self.assertIsNotNone(prepared)
        return prepared

    def _compiled_feature_counts(
        self,
        source: str,
        glyph_names: tuple[str, ...] = (".notdef", "a", "a.alt", "b", "b.alt"),
    ) -> dict[str, int]:
        font = TTFont()
        font.setGlyphOrder(list(glyph_names))
        addOpenTypeFeaturesFromString(font, source)
        try:
            if "GSUB" not in font:
                return {}
            counts: dict[str, int] = {}
            for record in font["GSUB"].table.FeatureList.FeatureRecord:
                counts[record.FeatureTag] = (
                    counts.get(record.FeatureTag, 0) + record.Feature.LookupCount
                )
            return counts
        finally:
            font.close()

    def _compiled_feature_lookup_indexes(
        self,
        source: str,
        tag: str,
        glyph_names: tuple[str, ...] = (".notdef", "a", "a.alt", "b", "b.alt"),
    ) -> list[list[int]]:
        font = TTFont()
        font.setGlyphOrder(list(glyph_names))
        addOpenTypeFeaturesFromString(font, source)
        try:
            if "GSUB" not in font:
                return []
            return [
                list(record.Feature.LookupListIndex)
                for record in font["GSUB"].table.FeatureList.FeatureRecord
                if record.FeatureTag == tag
            ]
        finally:
            font.close()

    def test_prepares_enabled_disabled_and_ignored_features(self) -> None:
        config = ResolvedConfig()
        config.feature_freeze.update(
            {"cv01": "enable", "cv02": "disable", "cv03": "ignore"}
        )
        with tempfile.TemporaryDirectory() as tmp:
            prepared = self._prepare_file(
                Path(tmp),
                """
feature cv01 { sub a by a.alt; } cv01;
feature cv02 { sub b by b.alt; } cv02;
feature cv03 { sub b by b.alt; } cv03;
""",
                config,
            )
        self.assertEqual(
            prepared.substitutions,
            (FeatureSubstitution("cv01", "a", "a.alt"),),
        )
        counts = self._compiled_feature_counts(prepared.source)
        self.assertEqual(counts["cv01"], 1)
        self.assertNotIn("cv02", counts)
        self.assertEqual(counts["cv03"], 1)

    def test_disables_every_repeated_feature_block(self) -> None:
        config = ResolvedConfig()
        config.feature_freeze["cv01"] = "disable"
        with tempfile.TemporaryDirectory() as tmp:
            prepared = self._prepare_file(
                Path(tmp),
                """
feature cv01 { sub a by a.alt; } cv01;
feature cv01 { sub b by b.alt; } cv01;
""",
                config,
            )

        self.assertEqual(prepared.substitutions, ())
        self.assertNotIn("cv01", self._compiled_feature_counts(prepared.source))

    def test_moves_every_repeated_feature_block_into_calt(self) -> None:
        config = ResolvedConfig()
        config.feature_freeze["ss03"] = "enable"
        with tempfile.TemporaryDirectory() as tmp:
            prepared = self._prepare_file(
                Path(tmp),
                """
feature calt { sub b by b.alt; } calt;
feature ss03 {
  lookup first { sub b a' by a.alt; } first;
} ss03;
feature ss03 {
  lookup second { sub a b' by b.alt; } second;
} ss03;
""",
                config,
            )

        counts = self._compiled_feature_counts(prepared.source)
        self.assertEqual(prepared.substitutions, ())
        self.assertEqual(counts["calt"], 3)
        self.assertEqual(counts["ss03"], 2)

    def test_moves_repeated_blocks_into_every_repeated_calt_block(self) -> None:
        config = ResolvedConfig()
        config.feature_freeze["ss03"] = "enable"
        with tempfile.TemporaryDirectory() as tmp:
            prepared = self._prepare_file(
                Path(tmp),
                """
feature calt {
  lookup firstCalt { sub a by a.alt; } firstCalt;
} calt;
feature calt {
  lookup secondCalt { sub b by b.alt; } secondCalt;
} calt;
feature ss03 {
  lookup first { sub b a' by a.alt; } first;
} ss03;
feature ss03 {
  lookup second { sub a b' by b.alt; } second;
} ss03;
""",
                config,
            )

        calt_lookups = self._compiled_feature_lookup_indexes(prepared.source, "calt")
        ss03_lookups = self._compiled_feature_lookup_indexes(prepared.source, "ss03")
        calt_blocks = prepared.source.split("feature calt {")[1:]
        self.assertEqual(len(calt_blocks), 2)
        for block in calt_blocks:
            self.assertLess(block.index("lookup first;"), block.index("lookup second;"))
        self.assertEqual([len(lookups) for lookups in calt_lookups], [4])
        self.assertEqual([len(lookups) for lookups in ss03_lookups], [2])
        moved_lookups = ss03_lookups[0]
        self.assertEqual(calt_lookups[0][1:3], moved_lookups)

    def test_ignores_every_repeated_feature_block(self) -> None:
        config = ResolvedConfig()
        config.feature_freeze["cv01"] = "ignore"
        with tempfile.TemporaryDirectory() as tmp:
            prepared = self._prepare_file(
                Path(tmp),
                """
feature cv01 { sub a by a.alt; } cv01;
feature cv01 { sub b by b.alt; } cv01;
""",
                config,
            )

        self.assertEqual(prepared.substitutions, ())
        self.assertEqual(self._compiled_feature_counts(prepared.source)["cv01"], 2)

    def test_keeps_a_single_feature_block_behavior_unchanged(self) -> None:
        config = ResolvedConfig()
        config.feature_freeze["cv01"] = "enable"
        with tempfile.TemporaryDirectory() as tmp:
            prepared = self._prepare_file(
                Path(tmp),
                "feature cv01 { sub a by a.alt; } cv01;",
                config,
            )

        self.assertEqual(
            prepared.substitutions,
            (FeatureSubstitution("cv01", "a", "a.alt"),),
        )
        self.assertEqual(self._compiled_feature_counts(prepared.source)["cv01"], 1)

    def test_moves_contextual_lookup_into_calt(self) -> None:
        config = ResolvedConfig()
        config.feature_freeze["ss03"] = "enable"
        with tempfile.TemporaryDirectory() as tmp:
            prepared = self._prepare_file(
                Path(tmp),
                """
feature calt { sub b by b.alt; } calt;
feature ss03 {
  lookup contextual {
    sub b a' by a.alt;
  } contextual;
} ss03;
""",
                config,
            )
        counts = self._compiled_feature_counts(prepared.source)
        self.assertEqual(prepared.substitutions, ())
        self.assertEqual(counts["calt"], 2)
        self.assertEqual(counts["ss03"], 1)

    def test_disabling_calt_preserves_referenced_lookup_definitions(self) -> None:
        config = ResolvedConfig()
        config.feature.liga = False
        with tempfile.TemporaryDirectory() as tmp:
            prepared = self._prepare_file(
                Path(tmp),
                """
feature calt {
  lookup shared { sub a by a.alt; } shared;
} calt;
feature ss12 { lookup shared; } ss12;
""",
                config,
            )
        counts = self._compiled_feature_counts(prepared.source)
        self.assertNotIn("calt", counts)
        self.assertEqual(counts["ss12"], 1)

    def test_disabling_feature_preserves_externally_referenced_lookup(self) -> None:
        config = ResolvedConfig()
        config.feature_freeze["cv02"] = "disable"
        with tempfile.TemporaryDirectory() as tmp:
            prepared = self._prepare_file(
                Path(tmp),
                """
feature cv02 {
  lookup shared { sub a by a.alt; } shared;
} cv02;
feature ss12 { lookup shared; } ss12;
""",
                config,
            )
        counts = self._compiled_feature_counts(prepared.source)
        self.assertNotIn("cv02", counts)
        self.assertEqual(counts["ss12"], 1)

    def test_custom_feature_file_follows_includes(self) -> None:
        config = ResolvedConfig()
        config.behavior.apply_fea_file = True
        config.feature_freeze["cv01"] = "enable"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "included.fea").write_text(
                "feature cv01 { sub a by a.alt; } cv01;",
                encoding="utf-8",
            )
            (root / "test.fea").write_text(
                "include(included.fea);",
                encoding="utf-8",
            )
            prepared = prepare_feature_source(
                config,
                glyph_names=(".notdef", "a", "a.alt"),
                issue_fea_dir=root,
                is_italic=False,
                is_cn=False,
                is_hinted=False,
                fea_path=str(root / "test.fea"),
            )
        self.assertIsNotNone(prepared)
        self.assertEqual(
            prepared.substitutions,
            (FeatureSubstitution("cv01", "a", "a.alt"),),
        )

    def test_invalid_feature_writes_issue_source(self) -> None:
        config = ResolvedConfig()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(SyntaxError, "Error preparing feature source"):
                self._prepare_file(root, "feature cv01 {", config)
            issue_path = root / "issue.fea"
            self.assertTrue(issue_path.is_file())
            self.assertIn("feature cv01 {", issue_path.read_text(encoding="utf-8"))

    def test_ufo_freeze_preserves_source_metadata(self) -> None:
        font = UFOFont()
        source = font.newGlyph("a")
        source.unicodes = [0x61]
        source.lib["preserve"] = True
        source.anchors.append(Anchor(x=10, y=20, name="top"))
        source.width = 400
        target = font.newGlyph("a.alt")
        target.unicodes = [0xE001]
        target.width = 600
        pen = target.getPen()
        pen.moveTo((0, 0))
        pen.lineTo((100, 0))
        pen.lineTo((100, 100))
        pen.closePath()
        descriptor = SourceDescriptor()
        descriptor.font = font
        designspace = DesignSpaceDocument()
        designspace.addSource(descriptor)

        apply_ufo_substitutions(
            designspace,
            (FeatureSubstitution("cv01", "a", "a.alt"),),
        )

        self.assertEqual(source.width, 600)
        self.assertEqual(source.unicodes, [0x61])
        self.assertEqual(source.lib["preserve"], True)
        self.assertEqual(source.anchors[0].name, "top")
        self.assertEqual(source.getBounds(font), target.getBounds(font))

    def test_ufo_freeze_skips_missing_glyphs(self) -> None:
        font = UFOFont()
        font.newGlyph("a")
        descriptor = SourceDescriptor()
        descriptor.font = font
        designspace = DesignSpaceDocument()
        designspace.addSource(descriptor)

        apply_ufo_substitutions(
            designspace,
            (FeatureSubstitution("cv01", "a", "missing"),),
        )

    def test_ufo_freeze_avoids_self_referential_cycle_when_target_references_source(
        self,
    ) -> None:
        # Reproduces the cyclical component reference crash from issue #810.
        # z.cv10 uses z as a component, so freezing z -> z.cv10 must not create z => z.
        font = UFOFont()

        # Set up z: a simple contour glyph.
        z = font.newGlyph("z")
        z.width = 600
        pen = z.getPen()
        pen.moveTo((100, 0))
        pen.lineTo((500, 0))
        pen.lineTo((100, 500))
        pen.lineTo((500, 500))
        pen.closePath()

        # Set up decorator: another simple glyph.
        decorator = font.newGlyph("decorator")
        decorator.width = 600
        pen = decorator.getPen()
        pen.moveTo((200, 200))
        pen.lineTo((400, 200))
        pen.lineTo((400, 300))
        pen.closePath()

        # Set up z.cv10: composite referencing z and decorator (no transformation).
        z_cv10 = font.newGlyph("z.cv10")
        z_cv10.width = 600
        comp_pen = z_cv10.getPointPen()
        comp_pen.addComponent("z", (1, 0, 0, 1, 0, 0))
        comp_pen.addComponent("decorator", (1, 0, 0, 1, 100, -50))

        descriptor = SourceDescriptor()
        descriptor.font = font
        designspace = DesignSpaceDocument()
        designspace.addSource(descriptor)

        # Freezing z -> z.cv10 must not cause a cyclical component reference.
        apply_ufo_substitutions(
            designspace,
            (FeatureSubstitution("cv10", "z", "z.cv10"),),
        )

        # After freeze, z should have no components that reference itself.
        for component in z.components:
            self.assertNotEqual(
                component.baseGlyph,
                "z",
                "z must not contain a self-referential component",
            )
        # z should visually match z.cv10: it contains the decorator component.
        component_bases = {c.baseGlyph for c in z.components}
        self.assertIn("decorator", component_bases)
        # z should carry the original contours from the pre-freeze z glyph.
        self.assertGreater(len(z.contours), 0)


class FeatureGenerationLoggingTest(unittest.TestCase):
    def test_feature_generation_logs_all_output_affecting_options(self) -> None:
        with self.assertLogs("scripts", level="DEBUG") as logs:
            generate_fea_string(
                is_italic=False,
                is_cn=False,
                is_normal=True,
                is_calt=False,
                enable_infinite=False,
                enable_tag=False,
                remove_italic_calt=True,
            )
            generate_fea_string(
                is_italic=True,
                is_cn=True,
            )
            generate_fea_string_cn_only()

        output = "\n".join(logs.output)
        self.assertIn("italic=False, cn=False, normal=True, calt=False", output)
        self.assertIn("infinite=False, tag=False", output)
        self.assertIn("remove_italic_calt=True", output)
        self.assertIn("italic=True, cn=True", output)
        self.assertIn("cn_only=True", output)
