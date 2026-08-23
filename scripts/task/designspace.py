from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from fontmake.compatibility import CompatibilityChecker
from fontTools.designspaceLib import (
    AxisDescriptor,
    DesignSpaceDocument,
    SourceDescriptor,
)
from glyphsLib import load, to_designspace
from ufo2ft.constants import FEATURE_WRITERS_KEY

from scripts.feature.compiler import generate_fea_string
from scripts.utils.files import write_json
from scripts.utils.logging import TaskName, log_task, logger

if TYPE_CHECKING:
    import argparse

SourceStyle = Literal["regular", "italic"]
SOURCE_ISSUE_REPORT = Path("fonts/source-issues.json")


@dataclass(frozen=True, slots=True)
class ConvertedGlyphsSource:
    source_path: Path
    style: SourceStyle
    designspace: DesignSpaceDocument


@dataclass(frozen=True, slots=True)
class PreparedGlyphsSource:
    source_path: Path
    style: SourceStyle
    designspace: DesignSpaceDocument
    errors: tuple[dict[str, Any], ...]


class SourceCompatibilityError(RuntimeError):
    """Raised after all generated source issues have been written."""


class IssueCollectingCompatibilityChecker(CompatibilityChecker):
    """Run fontmake's compatibility checks without logging every glyph."""

    def __init__(self, fonts: list[Any], default_source_idx: int):
        super().__init__(fonts, default_source_idx)
        self.glyph_issues: dict[str, set[str]] = {}

    def ensure_all_same(self, func: Any, objs: list[Any], what: str) -> bool:
        values = {func(value) for value in objs}
        if len(values) < 2:
            return True

        glyph_context = self.context[0]
        glyph_name = glyph_context.removeprefix("glyph ")
        detail = " ".join((*self.context[1:], what))
        if what == "base glyph":
            master_values = ", ".join(
                f"{font.info.styleName or 'Unknown'}={func(value)}"
                for font, value in zip(self.current_fonts, objs, strict=False)
            )
            detail = f"{detail}: {master_values}"
        self.glyph_issues.setdefault(glyph_name, set()).add(detail)
        self.okay = False
        return False


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser = subparsers.add_parser(
        "designspace",
        help="Generate committed Designspace and UFO sources from Glyphs exports",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("sources"),
        help="Directory containing exported .glyphs files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("sources"),
        help="Directory for generated Designspace and UFO sources",
    )
    return parser


def infer_source_style(source_path: str | Path) -> SourceStyle:
    """Infer the source style from the exported Glyphs filename."""
    return "italic" if "-italic" in Path(source_path).stem.lower() else "regular"


def convert_glyphs_source(
    source_path: str | Path,
    style: SourceStyle | None = None,
    *,
    feature_source: str = "",
) -> ConvertedGlyphsSource:
    """Convert one Glyphs export and attach the provided OpenType feature source."""
    path = Path(source_path)
    resolved_style = style or infer_source_style(path)
    with path.open(encoding="utf-8") as source_file:
        glyphs_font = load(source_file)
    # Project-generated features are authoritative and also avoid GlyphsLib
    # interpreting FontLab-specific tokens embedded in exported feature names.
    glyphs_font.classes = []
    glyphs_font.featurePrefixes = []
    glyphs_font.features = []
    designspace = to_designspace(
        glyphs_font,
        generate_GDEF=False,
        minimal=True,
        store_editor_state=False,
        write_skipexportglyphs=True,
    )
    for source in designspace.sources:
        if source.font is None:
            raise ValueError(f"Glyphs source master has no UFO font: {path}")
        source.font.features.text = feature_source

    weight_axis = next((axis for axis in designspace.axes if axis.tag == "wght"), None)
    if weight_axis is None:
        raise ValueError(f"Glyphs source is missing a wght axis: {path}")
    weight_axis.default = 400

    if resolved_style == "italic":
        _rename_italic_masters(designspace)

    return ConvertedGlyphsSource(path, resolved_style, designspace)


def _rename_italic_masters(designspace: DesignSpaceDocument) -> None:
    """Give italic UFO masters unique names without changing instance names."""
    for source in designspace.sources:
        if source.font is None:
            raise ValueError(f"Glyphs source master has no UFO font: {source.name}")
        current_style = source.styleName or source.font.info.styleName or ""
        if current_style == "Regular":
            italic_style = "Italic"
        elif current_style.endswith("Italic"):
            italic_style = current_style
        else:
            italic_style = f"{current_style}Italic"

        family_name = source.font.info.familyName or "Untitled"
        family_compact = family_name.replace(" ", "")
        source.name = f"{family_name} {italic_style}"
        source.styleName = italic_style
        source.filename = f"{family_compact}-{italic_style}.ufo"
        source.font.info.styleName = italic_style


def _configure_weight_axis_and_defaults(
    designspace: DesignSpaceDocument, path: Path
) -> tuple[str, SourceDescriptor]:
    weight_axis = next((axis for axis in designspace.axes if axis.tag == "wght"), None)
    if not isinstance(weight_axis, AxisDescriptor) or weight_axis.name is None:
        raise ValueError(f"Glyphs source requires a continuous named wght axis: {path}")
    weight_axis.default = 400
    axis_name = weight_axis.name

    sources = list(designspace.sources)
    default_source = next(
        (source for source in sources if source.location.get(axis_name) == 400),
        None,
    )
    if default_source is None or default_source.font is None:
        raise ValueError(f"Glyphs source is missing a wght 400 master: {path}")
    return axis_name, default_source


def _normalize_source_master_infos(
    sources: list[SourceDescriptor], default_source: SourceDescriptor, path: Path
) -> None:
    for source in sources:
        is_default = source is default_source
        source.copyLib = is_default
        source.copyGroups = is_default
        source.copyFeatures = is_default
        source.copyInfo = is_default
        if source.font is None:
            raise ValueError(f"Glyphs source master has no UFO font: {path}")
        info = source.font.info
        info.postscriptIsFixedPitch = True
        info.openTypeOS2Type = []
        panose: list[int] = list(info.openTypeOS2Panose or (0,) * 10)
        panose[0] = 2
        panose[3] = 9
        info.openTypeOS2Panose = panose
        info.openTypeGaspRangeRecords = [
            {
                "rangeMaxPPEM": 65535,
                "rangeGaspBehavior": [0, 1, 2, 3],
            }
        ]
        source.font.lib[FEATURE_WRITERS_KEY] = [
            writer
            for writer in source.font.lib.get(FEATURE_WRITERS_KEY, [])
            if writer.get("class") == "GdefFeatureWriter"
        ]


def _backfill_missing_glyphs_from_default(
    sources: list[SourceDescriptor],
    default_source: SourceDescriptor,
    designspace: DesignSpaceDocument,
) -> list[dict[str, Any]]:
    skip_export = set(designspace.lib.get("public.skipExportGlyphs", ()))
    glyph_names = sorted(
        set().union(
            *(set(source.font.keys()) for source in sources if source.font is not None)
        )
        - skip_export
    )
    errors: list[dict[str, Any]] = []
    default_font = default_source.font
    assert default_font is not None

    for glyph_name in glyph_names:
        available_sources = [
            source
            for source in sources
            if source.font is not None and glyph_name in source.font
        ]
        missing_sources = [
            source
            for source in sources
            if source.font is not None and glyph_name not in source.font
        ]
        if not missing_sources:
            continue
        if glyph_name not in default_font:
            errors.append(
                {
                    "glyph": glyph_name,
                    "kind": "missing_regular_master_layer",
                    "available_masters": [
                        source.styleName or source.name or "Unknown"
                        for source in available_sources
                    ],
                    "missing_masters": [
                        source.styleName or source.name or "Unknown"
                        for source in missing_sources
                    ],
                }
            )
            continue
        default_glyph = default_font[glyph_name]
        for source in missing_sources:
            assert source.font is not None
            source.font.addGlyph(default_glyph.copy())

    return errors


def _collect_master_compatibility_errors(
    sources: list[SourceDescriptor], default_source: SourceDescriptor
) -> list[dict[str, Any]]:
    source_fonts = [source.font for source in sources]
    checker = IssueCollectingCompatibilityChecker(
        source_fonts,
        sources.index(default_source),
    )
    checker.check()
    return [
        {
            "glyph": glyph_name,
            "kind": "incompatible_masters",
            "details": sorted(details),
        }
        for glyph_name, details in sorted(checker.glyph_issues.items())
    ]


def prepare_static_source(converted: ConvertedGlyphsSource) -> PreparedGlyphsSource:
    """Apply configuration-independent normalization before committing UFOs."""
    path = converted.source_path
    designspace = converted.designspace
    _, default_source = _configure_weight_axis_and_defaults(designspace, path)
    sources = list(designspace.sources)

    _normalize_source_master_infos(sources, default_source, path)

    errors = _backfill_missing_glyphs_from_default(sources, default_source, designspace)
    errors.extend(_collect_master_compatibility_errors(sources, default_source))
    errors.sort(key=lambda item: (item["glyph"], item["kind"]))

    return PreparedGlyphsSource(
        source_path=path,
        style=converted.style,
        designspace=designspace,
        errors=tuple(errors),
    )


def write_source_issue_report(
    sources: tuple[PreparedGlyphsSource, ...],
) -> Path | None:
    """Write one deterministic report for every converted source."""
    error_count = sum(len(source.errors) for source in sources)
    if error_count == 0:
        SOURCE_ISSUE_REPORT.unlink(missing_ok=True)
        return None

    SOURCE_ISSUE_REPORT.parent.mkdir(parents=True, exist_ok=True)
    ordered_sources = sorted(
        sources,
        key=lambda source: 0 if source.style == "regular" else 1,
    )
    write_json(
        SOURCE_ISSUE_REPORT,
        {
            source.style: {
                "source": source.source_path.as_posix(),
                "reused_regular_master_layers": [],
                "errors": list(source.errors),
            }
            for source in ordered_sources
        },
    )
    logger.info(
        "Wrote source compatibility report: path=%s, errors=%s",
        SOURCE_ISSUE_REPORT,
        error_count,
    )
    return SOURCE_ISSUE_REPORT


def validate_source_reports(sources: tuple[PreparedGlyphsSource, ...]) -> None:
    report_path = write_source_issue_report(sources)
    if any(source.errors for source in sources):
        raise SourceCompatibilityError(
            f"Glyphs source compatibility failed; see {report_path}"
        )


def write_designspace_source(
    prepared: PreparedGlyphsSource,
    output_dir: Path,
    designspace_name: str,
) -> Path:
    """Write one generated Designspace/UFO tree."""
    output_dir.mkdir(parents=True, exist_ok=True)
    designspace_path = output_dir / designspace_name
    prepared.designspace.path = str(designspace_path.resolve())

    for index, source in enumerate(prepared.designspace.sources):
        if source.font is None:
            raise ValueError(f"Converted source has no UFO font: {source.name}")
        filename = Path(source.filename or f"master-{index}.ufo").name
        ufo_path = output_dir / filename
        source.font.save(ufo_path, overwrite=True)
        source.font = None
        source.path = str(ufo_path.resolve())

    prepared.designspace.write(designspace_path.resolve())
    return designspace_path


def _generated_paths(
    prepared: PreparedGlyphsSource,
    designspace_path: Path,
) -> list[Path]:
    paths = [designspace_path]
    for source in prepared.designspace.sources:
        if source.filename is None:
            raise ValueError(f"Generated master has no filename: {source.name}")
        paths.append(designspace_path.parent / Path(source.filename).name)
    return paths


def _existing_generated_paths(
    glyphs_paths: list[Path],
    output_dir: Path,
) -> set[Path]:
    existing: set[Path] = set()
    for glyphs_path in glyphs_paths:
        designspace_path = output_dir / glyphs_path.with_suffix(".designspace").name
        if not designspace_path.is_file():
            continue
        existing.add(designspace_path)
        designspace = DesignSpaceDocument.fromfile(designspace_path)
        existing.update(
            output_dir / Path(source.filename).name
            for source in designspace.sources
            if source.filename is not None
        )
    return existing


def _install_generated_paths(
    staged: list[Path],
    output_dir: Path,
    obsolete: set[Path],
) -> None:
    backup_dir = staged[0].parent / ".backup"
    backup_dir.mkdir()
    targets = {output_dir / source_path.name for source_path in staged}
    backups: list[tuple[Path, Path]] = []
    installed: list[tuple[Path, Path]] = []
    try:
        for target_path in sorted(targets | obsolete):
            if not target_path.exists():
                continue
            backup_path = backup_dir / target_path.name
            os.replace(target_path, backup_path)
            backups.append((target_path, backup_path))
        for source_path in staged:
            target_path = output_dir / source_path.name
            os.replace(source_path, target_path)
            installed.append((target_path, source_path))
    except Exception:
        for target_path, source_path in reversed(installed):
            if target_path.exists():
                os.replace(target_path, source_path)
        for target_path, backup_path in reversed(backups):
            if backup_path.exists():
                os.replace(backup_path, target_path)
        raise


def generate_designspaces(source_dir: Path, output_dir: Path) -> list[Path]:
    glyphs_paths = sorted(source_dir.glob("*.glyphs"))
    if not glyphs_paths:
        raise FileNotFoundError(f"No .glyphs exports found in {source_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    existing_paths = _existing_generated_paths(glyphs_paths, output_dir)
    prepared_list: list[PreparedGlyphsSource] = []
    for glyphs_path in glyphs_paths:
        log_task(TaskName.DESIGNSPACE, "Converting %s", glyphs_path.name)
        style = infer_source_style(glyphs_path)
        feature_source = generate_fea_string(
            is_italic=style == "italic",
            is_cn=False,
        )
        prepared_list.append(
            prepare_static_source(
                convert_glyphs_source(
                    glyphs_path,
                    style,
                    feature_source=feature_source,
                )
            )
        )
    prepared_sources = tuple(prepared_list)
    validate_source_reports(prepared_sources)
    with tempfile.TemporaryDirectory(prefix=".designspace-", dir=output_dir) as tmp:
        staging_dir = Path(tmp)
        staged_paths: list[Path] = []
        seen_names: set[str] = set()
        for prepared in prepared_sources:
            designspace_name = prepared.source_path.with_suffix(
                ".designspace"
            ).name.replace("[wght]", "")
            designspace_path = write_designspace_source(
                prepared,
                staging_dir,
                designspace_name,
            )
            DesignSpaceDocument.fromfile(designspace_path)
            generated = _generated_paths(prepared, designspace_path)
            collisions = seen_names.intersection(path.name for path in generated)
            if collisions:
                names = ", ".join(sorted(collisions))
                raise ValueError(f"Generated source names conflict: {names}")
            seen_names.update(path.name for path in generated)
            staged_paths.extend(generated)

        installed = {output_dir / path.name for path in staged_paths}
        _install_generated_paths(
            staged_paths,
            output_dir,
            existing_paths - installed,
        )

    installed_paths = [output_dir / path.name for path in staged_paths]
    for path in installed_paths:
        logger.info("Saved generated font source to %s", path)
    return installed_paths


def run(args: argparse.Namespace) -> None:
    generate_designspaces(args.source_dir, args.output_dir)
