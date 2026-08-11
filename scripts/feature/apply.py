from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fontTools.feaLib import ast as fea_ast
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.feaLib.parser import Parser
from fontTools.pens.pointPen import AbstractPointPen, PointToSegmentPen
from fontTools.pens.transformPen import TransformPen

from scripts.config.base import ResolvedConfig, normalize_feature_freeze
from scripts.feature.compiler import generate_fea_string, get_freeze_moving_rules
from scripts.font_ops.fonttools import TTFont
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from fontTools.designspaceLib import DesignSpaceDocument
    from ufoLib2.objects.glyph import Glyph


@dataclass(frozen=True, slots=True)
class FeatureSubstitution:
    tag: str
    source: str
    target: str


@dataclass(frozen=True, slots=True)
class PreparedFeatureSource:
    source: str
    substitutions: tuple[FeatureSubstitution, ...]


def _feature_source(
    config: ResolvedConfig,
    *,
    is_italic: bool,
    is_cn: bool,
    is_hinted: bool,
    fea_path: str,
) -> tuple[str, Path | None]:
    if config.apply_fea_file:
        if not fea_path:
            return "", None
        path = Path(fea_path)
        logger.debug("Load feature file: path=%s", path)
        return path.read_text(encoding="utf-8"), path

    enable_infinite = (
        config.infinite_arrow if config.infinite_arrow is not None else not is_hinted
    )
    return (
        generate_fea_string(
            is_italic=is_italic,
            is_cn=is_cn,
            is_normal=config.feature.normal,
            # Keep lookup definitions available when calt is disabled. The
            # parsed feature tree detaches them from calt without deleting
            # lookups referenced by other features.
            is_calt=True,
            enable_infinite=enable_infinite,
            enable_tag=not config.remove_tag_liga,
            remove_italic_calt=config.feature_freeze["cv35"]
            .upper()
            .startswith("ENABLE"),
        ),
        None,
    )


def _write_feature_issue(
    issue_fea_dir: str | Path,
    feature_source: str,
    *,
    is_italic: bool,
    is_cn: bool,
) -> Path:
    issue_path = Path(issue_fea_dir) / "issue.fea"
    banner = f"Prepared feature with italic={is_italic}, cn={is_cn}"
    issue_path.write_text(
        f"# {banner}\n\n{feature_source}",
        encoding="utf-8",
    )
    return issue_path


def _parse_feature_source(
    feature_source: str,
    feature_path: Path | None,
    glyph_names: tuple[str, ...],
) -> fea_ast.FeatureFile:
    if feature_path is not None:
        return Parser(
            feature_path,
            glyphNames=glyph_names,
            includeDir=feature_path.parent,
        ).parse()
    return Parser(StringIO(feature_source), glyphNames=glyph_names).parse()


def _feature_blocks(
    feature_file: fea_ast.FeatureFile,
) -> dict[str, list[fea_ast.FeatureBlock]]:
    blocks: dict[str, list[fea_ast.FeatureBlock]] = {}
    for statement in feature_file.statements:
        if isinstance(statement, fea_ast.FeatureBlock):
            blocks.setdefault(statement.name, []).append(statement)
    return blocks


def _non_rule_statements(statements: list[Any]) -> list[Any]:
    return [
        statement
        for statement in statements
        if isinstance(statement, (fea_ast.Comment, fea_ast.NestedBlock))
    ]


def _moving_statements(statements: list[Any]) -> list[Any]:
    result: list[Any] = []
    for statement in statements:
        if isinstance(statement, fea_ast.LookupBlock):
            result.append(fea_ast.LookupReferenceStatement(statement))
        elif isinstance(
            statement,
            (
                fea_ast.LookupReferenceStatement,
                fea_ast.AlternateSubstStatement,
                fea_ast.ChainContextSubstStatement,
                fea_ast.IgnoreSubstStatement,
                fea_ast.LigatureSubstStatement,
                fea_ast.MultipleSubstStatement,
                fea_ast.ReverseChainSingleSubstStatement,
                fea_ast.SingleSubstStatement,
            ),
        ):
            result.append(deepcopy(statement))
    return result


def _rewrite_feature_tree(
    feature_file: fea_ast.FeatureFile,
    freeze_config: dict[str, str],
) -> None:
    blocks = _feature_blocks(feature_file)
    calt_blocks = [
        statement
        for statement in feature_file.statements
        if isinstance(statement, fea_ast.FeatureBlock) and statement.name == "calt"
    ]
    enable_calt = freeze_config.get("calt") == "1"

    if not enable_calt:
        detached_definitions: list[Any] = []
        for block in calt_blocks:
            detached_definitions.extend(
                statement
                for statement in block.statements
                if isinstance(
                    statement,
                    (fea_ast.GlyphClassDefinition, fea_ast.LookupBlock),
                )
            )
            block.statements = _non_rule_statements(block.statements)
        if detached_definitions:
            first_feature_index = next(
                (
                    index
                    for index, statement in enumerate(feature_file.statements)
                    if isinstance(statement, fea_ast.FeatureBlock)
                ),
                len(feature_file.statements),
            )
            feature_file.statements[first_feature_index:first_feature_index] = (
                detached_definitions
            )
        for statement in feature_file.statements:
            if not isinstance(statement, fea_ast.FeatureBlock):
                continue
            statement.statements = [
                child
                for child in statement.statements
                if not (
                    isinstance(child, fea_ast.FeatureReferenceStatement)
                    and child.featureName == "calt"
                )
            ]

    moving_rules = frozenset(get_freeze_moving_rules())
    detached_feature_definitions: list[Any] = []
    for tag, status in freeze_config.items():
        if tag == "calt":
            continue
        matching_blocks = blocks.get(tag)
        if not matching_blocks:
            continue
        if status == "-1":
            for block in matching_blocks:
                detached_feature_definitions.extend(
                    statement
                    for statement in block.statements
                    if isinstance(
                        statement,
                        (fea_ast.GlyphClassDefinition, fea_ast.LookupBlock),
                    )
                )
                block.statements = _non_rule_statements(block.statements)
        elif status == "1" and enable_calt and tag in moving_rules:
            additions: list[Any] = []
            for block in matching_blocks:
                rewritten_statements: list[Any] = []
                for statement in block.statements:
                    if isinstance(statement, fea_ast.GlyphClassDefinition):
                        detached_feature_definitions.append(statement)
                    elif isinstance(statement, fea_ast.LookupBlock):
                        detached_feature_definitions.append(statement)
                        rewritten_statements.append(
                            fea_ast.LookupReferenceStatement(statement)
                        )
                    else:
                        rewritten_statements.append(statement)
                block.statements = rewritten_statements
                additions.extend(_moving_statements(block.statements))
            for calt_block in calt_blocks:
                calt_block.statements.extend(deepcopy(additions))
    if detached_feature_definitions:
        first_feature_index = next(
            (
                index
                for index, statement in enumerate(feature_file.statements)
                if isinstance(statement, fea_ast.FeatureBlock)
            ),
            len(feature_file.statements),
        )
        feature_file.statements[first_feature_index:first_feature_index] = (
            detached_feature_definitions
        )


def _compile_feature_source(
    feature_source: str,
    glyph_names: tuple[str, ...],
) -> TTFont:
    font = TTFont(recalcTimestamp=False)
    font.setGlyphOrder(list(glyph_names))
    addOpenTypeFeaturesFromString(font, feature_source)
    return font


def _single_substitutions(
    font: TTFont,
    freeze_config: dict[str, str],
) -> tuple[FeatureSubstitution, ...]:
    if "GSUB" not in font:
        return ()
    gsub = font["GSUB"].table
    if gsub.FeatureList is None or gsub.LookupList is None:
        return ()
    feature_records = {
        record.FeatureTag: record.Feature
        for record in gsub.FeatureList.FeatureRecord
        if record.FeatureTag != "calt"
    }
    moving_rules = frozenset(get_freeze_moving_rules())
    result: list[FeatureSubstitution] = []
    for tag, status in freeze_config.items():
        if status != "1" or tag in moving_rules:
            continue
        feature = feature_records.get(tag)
        if feature is None:
            continue
        for lookup_index in feature.LookupListIndex:
            lookup = gsub.LookupList.Lookup[lookup_index]
            if lookup.LookupType != 1:
                continue
            for subtable in lookup.SubTable:
                mapping = getattr(subtable, "mapping", None)
                if mapping is None:
                    extension = getattr(subtable, "ExtSubTable", None)
                    mapping = getattr(extension, "mapping", None)
                if not mapping:
                    continue
                result.extend(
                    FeatureSubstitution(tag, source, target)
                    for source, target in mapping.items()
                )
    return tuple(result)


def prepare_feature_source(
    config: ResolvedConfig,
    *,
    glyph_names: tuple[str, ...],
    issue_fea_dir: str | Path,
    is_italic: bool,
    is_cn: bool,
    is_hinted: bool,
    fea_path: str,
) -> PreparedFeatureSource | None:
    """Resolve feature input, apply freeze policy, and collect outline mappings."""
    if is_hinted and config.infinite_arrow and not config.apply_fea_file:
        return None

    source, source_path = _feature_source(
        config,
        is_italic=is_italic,
        is_cn=is_cn,
        is_hinted=is_hinted,
        fea_path=fea_path,
    )
    if not source:
        return PreparedFeatureSource("", ())

    freeze_config = normalize_feature_freeze(
        config.feature_freeze,
        config.enable_ligature,
    )
    try:
        feature_file = _parse_feature_source(source, source_path, glyph_names)
        original_source = feature_file.asFea()
        feature_font = _compile_feature_source(original_source, glyph_names)
        try:
            substitutions = _single_substitutions(feature_font, freeze_config)
        finally:
            feature_font.close()
        _rewrite_feature_tree(feature_file, freeze_config)
        return PreparedFeatureSource(feature_file.asFea(), substitutions)
    except Exception as error:
        issue_path = _write_feature_issue(
            issue_fea_dir,
            source,
            is_italic=is_italic,
            is_cn=is_cn,
        )
        raise SyntaxError(
            f"Error preparing feature source: {error}\n\n"
            f"See feature source in {issue_path}"
        ) from error


_IDENTITY_TRANSFORM = (1, 0, 0, 1, 0, 0)


class _InlineSelfRefPointPen(AbstractPointPen):
    """A PointPen wrapper that replaces self-referential component calls with the
    snapshot glyph's own outline, preserving the drawing order of the target."""

    def __init__(
        self, output_pen: AbstractPointPen, source_name: str, snapshot: Glyph
    ) -> None:
        self._output_pen = output_pen
        self._source_name = source_name
        self._snapshot = snapshot

    def beginPath(self, identifier: str | None = None, **kwargs: Any) -> None:
        self._output_pen.beginPath(identifier, **kwargs)

    def endPath(self) -> None:
        self._output_pen.endPath()

    def addPoint(
        self,
        pt: tuple[float, float],
        segmentType: str | None = None,
        smooth: bool = False,
        name: str | None = None,
        identifier: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._output_pen.addPoint(pt, segmentType, smooth, name, identifier, **kwargs)

    def addComponent(
        self,
        baseGlyphName: str,
        transformation: Any,
        identifier: Any = None,
        **kwargs: Any,
    ) -> None:
        if baseGlyphName == self._source_name:
            # Replace the self-referential component with the snapshot's actual
            # outline so that no glyph ends up referencing itself.
            if transformation == _IDENTITY_TRANSFORM:
                self._snapshot.drawPoints(self._output_pen)
            else:
                self._snapshot.draw(
                    TransformPen(PointToSegmentPen(self._output_pen), transformation)
                )
        else:
            self._output_pen.addComponent(
                baseGlyphName, transformation, identifier, **kwargs
            )


def _copy_ufo_outline(source: Glyph, target: Glyph) -> None:
    source_name = source.name

    # If target contains a component that directly references source, copying it
    # verbatim would create a self-referential cycle (e.g. z.cv10 -> z => z).
    # Snapshot source first so the self-referential component can be inlined.
    has_self_ref = source_name is not None and any(
        c.baseGlyph == source_name for c in target.components
    )
    snapshot = deepcopy(source) if has_self_ref else None

    source.clearContours()
    source.clearComponents()

    if snapshot is not None:
        assert source_name is not None
        point_pen = source.getPointPen()
        target.drawPoints(_InlineSelfRefPointPen(point_pen, source_name, snapshot))
    else:
        target.drawPoints(source.getPointPen())

    source.width = target.width
    source.height = target.height


def apply_standard_zero(designspace: DesignSpaceDocument) -> None:
    """Swap zero glyph roles so the registered `zero` feature selects slashes."""
    for descriptor in designspace.sources:
        font = descriptor.font
        if font is None:
            raise ValueError(f"Designspace source master has no UFO font: {descriptor}")
        if "zero" not in font or "zero.zero" not in font:
            continue

        zero = font["zero"]
        slashed_zero = font["zero.zero"]
        zero_snapshot = deepcopy(zero)
        slashed_zero_snapshot = deepcopy(slashed_zero)
        _copy_ufo_outline(zero, slashed_zero_snapshot)
        _copy_ufo_outline(slashed_zero, zero_snapshot)


def apply_ufo_substitutions(
    designspace: DesignSpaceDocument,
    substitutions: tuple[FeatureSubstitution, ...],
) -> None:
    """Bake single substitutions into every master without replacing metadata."""
    for descriptor in designspace.sources:
        font = descriptor.font
        if font is None:
            raise ValueError(f"Designspace source master has no UFO font: {descriptor}")
        for substitution in substitutions:
            if substitution.source not in font or substitution.target not in font:
                continue
            _copy_ufo_outline(
                font[substitution.source],
                font[substitution.target],
            )


def prepare_designspace_features(
    config: ResolvedConfig,
    designspace: DesignSpaceDocument,
    *,
    issue_fea_dir: str | Path,
    is_italic: bool,
    fea_path: str,
) -> PreparedFeatureSource:
    """Freeze master outlines and attach final feature source before Fontmake."""
    default_source = designspace.findDefault()
    if default_source is None or default_source.font is None:
        raise ValueError("Designspace source is missing a default UFO font")
    glyph_names = tuple(default_source.font.keys())
    prepared = prepare_feature_source(
        config,
        glyph_names=glyph_names,
        issue_fea_dir=issue_fea_dir,
        is_italic=is_italic,
        is_cn=False,
        is_hinted=False,
        fea_path=fea_path,
    )
    if prepared is None:
        raise AssertionError("Base source feature preparation cannot be skipped")
    if config.feature.standard_zero:
        apply_standard_zero(designspace)
    apply_ufo_substitutions(designspace, prepared.substitutions)
    for descriptor in designspace.sources:
        if descriptor.font is None:
            raise ValueError(f"Designspace source master has no UFO font: {descriptor}")
        descriptor.font.features.text = prepared.source
    return prepared


def _apply_ttfont_substitutions(
    font: TTFont,
    substitutions: tuple[FeatureSubstitution, ...],
    outline_tags: frozenset[str],
) -> None:
    if not substitutions or "glyf" not in font or "hmtx" not in font:
        return
    glyphs = font.table("glyf").glyphs
    metrics = font.table("hmtx").metrics
    for substitution in substitutions:
        if substitution.tag not in outline_tags:
            continue
        if (
            substitution.source not in glyphs
            or substitution.source not in metrics
            or substitution.target not in glyphs
            or substitution.target not in metrics
        ):
            continue
        glyphs[substitution.source] = glyphs[substitution.target]
        metrics[substitution.source] = metrics[substitution.target]


def apply_binary_features(
    config: ResolvedConfig,
    font: TTFont,
    issue_fea_dir: str | Path,
    *,
    is_italic: bool,
    is_cn: bool,
    is_hinted: bool,
    fea_path: str,
    outline_tags: frozenset[str] = frozenset(),
) -> None:
    """Apply prepared tables and optionally freeze late-available binary glyphs."""
    prepared = prepare_feature_source(
        config,
        glyph_names=tuple(font.getGlyphOrder()),
        issue_fea_dir=issue_fea_dir,
        is_italic=is_italic,
        is_cn=is_cn,
        is_hinted=is_hinted,
        fea_path=fea_path,
    )
    if prepared is None:
        return
    if prepared.source:
        addOpenTypeFeaturesFromString(font, prepared.source)
    _apply_ttfont_substitutions(font, prepared.substitutions, outline_tags)
