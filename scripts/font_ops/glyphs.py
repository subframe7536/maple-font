from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from fontmake.font_project import CFFOptimization, FontProject
from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument
from ufo2ft.filters import DecomposeTransformedComponentsFilter
from ufoLib2 import Font as UFOFont

from scripts.external.process import (
    create_process_executor,
    create_thread_executor,
    run_jobs,
)
from scripts.font_ops.glyph_transform import (
    SmartWidthThickenFilter,
    scale_ufo_width,
)
from scripts.font_ops.metrics import calculate_line_height_metrics
from scripts.utils.logging import logger, set_log_task

if TYPE_CHECKING:
    from concurrent.futures import Executor

SourceStyle = Literal["regular", "italic"]
FontmakeOutput = Literal["variable", "ttf", "otf"]


@dataclass(frozen=True, slots=True)
class PreparedDesignspaceSource:
    source_path: Path
    style: SourceStyle
    designspace: DesignSpaceDocument
    vertical_metric: tuple[int, int]


@dataclass(frozen=True, slots=True)
class FontmakeBranchJob:
    designspace_path: Path
    output: FontmakeOutput
    target: Path
    interpolate: bool | str = False
    source_label: str = ""
    width_transform: tuple[int, int] | None = None


def compile_fontmake_branches(
    jobs: list[FontmakeBranchJob],
    use_processes: bool = False,
    executor: Executor | None = None,
) -> None:
    """Compile one output format for all prepared sources in parallel."""
    if not jobs:
        return
    if executor is not None:
        run_jobs(executor, _compile_fontmake_branch, jobs)
        return
    if use_processes:
        with create_process_executor(
            len(jobs), fallback_to_threads=True
        ) as process_executor:
            run_jobs(process_executor, _compile_fontmake_branch, jobs)
        return
    with create_thread_executor(len(jobs)) as thread_executor:
        run_jobs(thread_executor, _compile_fontmake_branch, jobs)


def _fontmake_options(job: FontmakeBranchJob) -> dict[str, Any]:
    options: dict[str, Any] = {
        "output": (job.output,),
        "use_production_names": False,
        "autohint": False,
        "subset": False,
        "feature_writers": [],
        "generate_GDEF": False,
        "check_compatibility": True,
    }
    width_filters = (
        [SmartWidthThickenFilter(*job.width_transform)]
        if job.width_transform is not None
        else []
    )
    if job.output == "variable":
        options.update(
            output_path=str(job.target),
            remove_overlaps=False,
        )
        if width_filters:
            options["filters"] = width_filters
        return options

    options.update(
        output_dir=str(job.target),
        interpolate=job.interpolate,
        remove_overlaps=True,
        overlaps_backend="pathops",
        filters=[DecomposeTransformedComponentsFilter(), *width_filters],
    )
    if job.output == "otf":
        options["optimize_cff"] = CFFOptimization.SUBROUTINIZE
    return options


def _compile_fontmake_branch(job: FontmakeBranchJob) -> None:
    set_log_task(job.output)
    logger.debug(
        "Compiling %s source: %s",
        job.output,
        job.source_label or job.designspace_path.parent.name,
    )
    project = FontProject()
    if job.output == "variable":
        job.target.parent.mkdir(parents=True, exist_ok=True)
    else:
        job.target.mkdir(parents=True, exist_ok=True)
    project.run_from_designspace(job.designspace_path, **_fontmake_options(job))


def prepare_designspace_source(
    source_path: str | Path,
    style: SourceStyle,
    target_width: int | None = None,
    original_ref_width: int = 600,
    weight_mapping: dict[str, int] | None = None,
    line_height: float = 1,
) -> PreparedDesignspaceSource:
    """Load committed Designspace/UFO sources and apply current build settings."""
    path = Path(source_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Generated font source is missing: {path}; "
            "run `python task.py designspace`"
        )

    designspace = DesignSpaceDocument.fromfile(path)
    opened_fonts: list[UFOFont] = []
    try:
        for source in designspace.sources:
            ufo_path = Path(source.path) if source.path is not None else None
            if ufo_path is None or not ufo_path.is_dir():
                label = source.filename or source.name or "Unknown"
                raise FileNotFoundError(
                    f"Generated UFO source is missing: {label}; "
                    "run `python task.py designspace`"
                )
            source.font = UFOFont.open(ufo_path)
            opened_fonts.append(source.font)

        _apply_designspace_weight_mapping(designspace, weight_mapping)
        weight_axis = next(
            (axis for axis in designspace.axes if axis.tag == "wght"),
            None,
        )
        if not isinstance(weight_axis, AxisDescriptor) or weight_axis.name is None:
            raise ValueError(
                f"Designspace source requires a continuous named wght axis: {path}"
            )
        weight_axis.default = 400
        axis_name = weight_axis.name
        sources = list(designspace.sources)
        default_source = next(
            (source for source in sources if source.location.get(axis_name) == 400),
            None,
        )
        if default_source is None or default_source.font is None:
            raise ValueError(f"Designspace source is missing a wght 400 master: {path}")
        info = default_source.font.info
        ascender = info.openTypeHheaAscender
        descender = info.openTypeHheaDescender
        if ascender is None:
            ascender = info.ascender
        if descender is None:
            descender = info.descender
        if ascender is None or descender is None:
            raise ValueError("UFO source is missing vertical metrics")
        vertical_metric = round(ascender), round(descender)
        target_vertical_metric = (
            calculate_line_height_metrics(line_height, vertical_metric)
            if line_height != 1
            else None
        )
        for source in sources:
            if source.font is None:
                raise ValueError(f"Designspace source master has no UFO font: {path}")
            if target_vertical_metric is not None:
                target_ascender, target_descender = target_vertical_metric
                info = source.font.info
                info.openTypeHheaAscender = target_ascender
                info.openTypeHheaDescender = target_descender
                info.openTypeOS2TypoAscender = target_ascender
                info.openTypeOS2TypoDescender = target_descender
                info.openTypeOS2WinAscent = target_ascender
                info.openTypeOS2WinDescent = -target_descender
            if target_width is not None:
                scale_ufo_width(
                    source.font,
                    target_width=target_width,
                    original_ref_width=original_ref_width,
                )

        return PreparedDesignspaceSource(
            source_path=path,
            style=style,
            designspace=designspace,
            vertical_metric=vertical_metric,
        )
    except BaseException:
        for font in opened_fonts:
            with suppress(Exception):
                font.close()
        raise


def _apply_designspace_weight_mapping(
    designspace: DesignSpaceDocument,
    weight_mapping: dict[str, int] | None,
) -> None:
    """Apply configured user weights while preserving source design locations."""
    if weight_mapping is None:
        return
    if weight_mapping["thin"] != 100:
        raise ValueError("Font weight of 'thin' must be 100")
    if weight_mapping["extrabold"] != 800:
        raise ValueError("Font weight of 'extrabold' must be 800")

    weight_axis = next((axis for axis in designspace.axes if axis.tag == "wght"), None)
    if weight_axis is None:
        raise ValueError("Designspace source is missing a wght axis")
    if not isinstance(weight_axis, AxisDescriptor) or weight_axis.name is None:
        raise ValueError("Designspace wght axis must be continuous and named")
    axis_name = weight_axis.name

    mapping: list[tuple[float, float]] = []
    for source in designspace.sources:
        style_name = source.styleName or source.name or ""
        base_style = style_name.removesuffix("Italic") or "Regular"
        weight_name = base_style.replace(" ", "").lower()
        design_weight = source.location.get(axis_name)
        if weight_name in weight_mapping and design_weight is not None:
            mapping.append((weight_mapping[weight_name], design_weight))
    for instance in designspace.instances:
        style_name = instance.styleName or instance.name or ""
        base_style = style_name.removesuffix("Italic") or "Regular"
        weight_name = base_style.replace(" ", "").lower()
        design_weight = instance.designLocation.get(axis_name)
        if (
            weight_name in weight_mapping
            and design_weight is not None
            and not isinstance(design_weight, tuple)
        ):
            mapping.append((weight_mapping[weight_name], design_weight))
    if mapping:
        weight_axis.map = sorted(dict(mapping).items())
        weight_axis.minimum = weight_axis.map[0][0]
        weight_axis.maximum = weight_axis.map[-1][0]
        weight_axis.default = 400


def materialize_prepared_source(
    prepared: PreparedDesignspaceSource,
    workspace: str | Path,
) -> Path:
    """Write one immutable Designspace/UFO tree for all fontmake branches."""
    root = Path(workspace)
    root.mkdir(parents=True, exist_ok=True)
    designspace_path = root / f"{prepared.style}.designspace"
    prepared.designspace.path = str(designspace_path.resolve())

    fonts_to_close = []
    try:
        missing_source = None
        for source in prepared.designspace.sources:
            if source.font is None:
                missing_source = source
                continue
            fonts_to_close.append((source, source.font))
        if missing_source is not None:
            raise ValueError(f"Prepared source has no UFO font: {missing_source.name}")

        for index, (source, font) in enumerate(fonts_to_close):
            filename = Path(source.filename or f"master-{index}.ufo").name
            ufo_path = root / filename
            font.save(ufo_path, overwrite=True)
            source.path = str(ufo_path.resolve())

        while fonts_to_close:
            source, font = fonts_to_close.pop()
            try:
                font.close()
            finally:
                source.font = None

        for instance in prepared.designspace.instances:
            if instance.filename is not None:
                instance.path = str((root / Path(instance.filename)).resolve())

        prepared.designspace.write(designspace_path.resolve())
        return designspace_path
    finally:
        while fonts_to_close:
            source, font = fonts_to_close.pop()
            try:
                with suppress(Exception):
                    font.close()
            finally:
                source.font = None
