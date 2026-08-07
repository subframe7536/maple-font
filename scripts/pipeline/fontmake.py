from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from scripts.external.process import create_process_executor, run_process_jobs
from scripts.feature.apply import prepare_designspace_features
from scripts.font_ops.fonttools import load_font
from scripts.font_ops.glyphs import (
    FontmakeBranchJob,
    SourceStyle,
    compile_fontmake_branches,
    materialize_prepared_source,
    prepare_designspace_source,
)
from scripts.font_ops.metadata import (
    fix_italic_metadata,
    set_monospace_metadata,
    strip_name_whitespace,
)
from scripts.font_ops.metrics import adjust_line_height, verify_glyph_width
from scripts.font_ops.names import parse_style_name, update_font_names
from scripts.font_ops.opentype import (
    add_ital_axis_to_stat,
    add_weight_axis_values_to_stat,
    alias_codepoints,
)
from scripts.pipeline.artifacts import is_target_style_file
from scripts.utils.logging import (
    TaskName,
    log_task,
    log_task_complete,
    logger,
    set_log_task,
)

if TYPE_CHECKING:
    from concurrent.futures import Executor

    from scripts.config.base import ResolvedConfig
    from scripts.config.runtime import BuildRuntimeContext


@dataclass(frozen=True)
class StaticPostprocessJob:
    input_path: str
    output_dir: str
    font_config: ResolvedConfig
    runtime_context: BuildRuntimeContext


@dataclass(frozen=True)
class FontmakeSourceJob:
    source_path: str
    style: SourceStyle
    workspace: str
    feature_file_path: str
    issue_fea_dir: str
    font_config: ResolvedConfig
    target_width: int | None
    original_ref_width: int
    weight_mapping: dict[str, int]
    line_height: float


@dataclass(frozen=True)
class PreparedFontmakeSource:
    style: SourceStyle
    designspace_path: str
    vertical_metric: tuple[int, int]


@dataclass(frozen=True)
class VariablePostprocessJob:
    raw_path: str
    style: SourceStyle
    font_config: ResolvedConfig
    runtime_context: BuildRuntimeContext


@dataclass(frozen=True)
class FontmakeBuildContext:
    temp_path: Path
    raw_variable_dir: Path
    raw_ttf_dir: Path
    raw_otf_dir: Path
    sources: tuple[PreparedFontmakeSource, ...]
    width_transform: tuple[int, int] | None = None


def postprocess_static_font(
    input_path: str | Path,
    output_dir: str | Path,
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
) -> Path:
    source_path = Path(input_path)
    logger.debug("Postprocess static font: source=%s", source_path.name)
    font = load_font(source_path)
    is_ttf = source_path.suffix.lower() == ".ttf"
    fix_italic_metadata(font)
    set_monospace_metadata(font)
    strip_name_whitespace(font)

    style_compact = source_path.stem.split("-")[-1]
    style_with_prefix_space, style_in_2, style_in_17, is_skip_subfamily, _ = (
        parse_style_name(style_name_compact=style_compact)
    )
    postscript_name = f"{font_config.family_name_compact}-{style_compact}"

    update_font_names(
        font=font,
        font_config=font_config,
        family_name=font_config.family_name + style_with_prefix_space,
        style_name=style_in_2,
        full_name=f"{font_config.family_name} {style_in_17}",
        postscript_name=postscript_name,
        is_skip_subfamily=is_skip_subfamily,
        preferred_family_name=font_config.family_name,
        preferred_style_name=style_in_17,
    )

    if style_with_prefix_space == " Thin":
        font.table("OS/2").usWeightClass = 250
    elif style_with_prefix_space == " ExtraLight":
        font.table("OS/2").usWeightClass = 275

    if font_config.line_height != 1:
        adjust_line_height(
            font,
            font_config.line_height,
            runtime_context.resolved_vertical_metric,
        )

    alias_codepoints(font, font_config.codepoint_alias)
    verify_glyph_width(
        font=font,
        expect_widths=font_config.get_valid_glyph_width_list(),
        file_name=postscript_name,
    )

    if not is_ttf:
        font["CFF "].cff.topDictIndex[0].version = font_config.font_version

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{postscript_name}{source_path.suffix.lower()}"
    try:
        font.save(target_path)
    finally:
        font.close()
    return target_path


def postprocess_static_font_job(job: StaticPostprocessJob) -> Path:
    set_log_task(Path(job.input_path).suffix.removeprefix(".").lower())
    target_path = postprocess_static_font(
        job.input_path,
        job.output_dir,
        job.font_config,
        job.runtime_context,
    )
    logger.info("Saved static font to %s", target_path)
    return target_path


def build_fontmake_source_job(job: FontmakeSourceJob) -> PreparedFontmakeSource:
    set_log_task("prepare")
    logger.debug("Prepare source: %s", Path(job.source_path).name)
    prepared = prepare_designspace_source(
        job.source_path,
        job.style,
        target_width=job.target_width,
        original_ref_width=job.original_ref_width,
        weight_mapping=job.weight_mapping,
        line_height=job.line_height,
    )
    prepare_designspace_features(
        job.font_config,
        prepared.designspace,
        issue_fea_dir=job.issue_fea_dir,
        is_italic=job.style == "italic",
        fea_path=job.feature_file_path,
    )
    return PreparedFontmakeSource(
        job.style,
        str(materialize_prepared_source(prepared, job.workspace)),
        prepared.vertical_metric,
    )


def prepare_fontmake_sources(
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    executor: Executor | None = None,
) -> FontmakeBuildContext:
    """Prepare committed Designspace/UFO sources for later format tasks."""
    started_at = log_task(TaskName.PREPARE, "Prepare font sources")
    source_dir = Path(runtime_context.src_dir)
    temp_path = Path(runtime_context.output_dir) / "temp"
    raw_variable_dir = temp_path / "variable"
    raw_ttf_dir = temp_path / "ttf"
    raw_otf_dir = temp_path / "otf"
    source_specs: tuple[tuple[Path, SourceStyle], ...] = (
        (source_dir / "MapleMono[wght].designspace", "regular"),
        (source_dir / "MapleMono-Italic[wght].designspace", "italic"),
    )

    shutil.rmtree(temp_path, ignore_errors=True)
    temp_path.mkdir(parents=True)
    target_width = (
        font_config.get_target_width() if font_config.get_width_name() else None
    )
    jobs = [
        FontmakeSourceJob(
            source_path=str(source_path),
            style=style,
            workspace=str(temp_path / "prepared" / style),
            feature_file_path=runtime_context.feature_file_path(style == "italic"),
            issue_fea_dir=runtime_context.output_dir,
            font_config=font_config,
            target_width=target_width,
            original_ref_width=font_config.glyph_width,
            weight_mapping=font_config.weight_mapping,
            line_height=font_config.line_height,
        )
        for source_path, style in source_specs
    ]
    try:
        if executor is None:
            with create_process_executor(
                max_workers=len(jobs), fallback_to_threads=True
            ) as process_executor:
                prepared_sources = tuple(
                    process_executor.map(build_fontmake_source_job, jobs)
                )
        else:
            prepared_sources = tuple(executor.map(build_fontmake_source_job, jobs))
        if font_config.line_height != 1:
            regular_source = next(
                source for source in prepared_sources if source.style == "regular"
            )
            runtime_context.resolved_vertical_metric = regular_source.vertical_metric
    except Exception:
        shutil.rmtree(temp_path, ignore_errors=True)
        raise

    context = FontmakeBuildContext(
        temp_path,
        raw_variable_dir,
        raw_ttf_dir,
        raw_otf_dir,
        prepared_sources,
        (target_width, font_config.glyph_width) if target_width is not None else None,
    )
    log_task_complete(started_at, f"{len(prepared_sources)} sources")
    return context


def compile_fontmake_formats(
    context: FontmakeBuildContext,
    build_formats: tuple[Literal["variable", "ttf", "otf"], ...],
    executor: Executor | None = None,
    *,
    target_styles: list[str] | None = None,
) -> None:
    """Compile all requested Fontmake branches in one shared job batch."""
    static_interpolate: bool | str = True
    if target_styles is not None:
        style_pattern = "|".join(re.escape(style) for style in target_styles)
        static_interpolate = rf".* (?:{style_pattern})"

    compile_fontmake_branches(
        [
            FontmakeBranchJob(
                designspace_path=Path(source.designspace_path),
                output=build_format,
                target=(
                    context.raw_variable_dir / f"{source.style}.ttf"
                    if build_format == "variable"
                    else {
                        "ttf": context.raw_ttf_dir,
                        "otf": context.raw_otf_dir,
                    }[build_format]
                ),
                interpolate=False if build_format == "variable" else static_interpolate,
                source_label=source.style,
                width_transform=context.width_transform,
            )
            for build_format in build_formats
            for source in context.sources
        ],
        use_processes=True,
        executor=executor,
    )


def postprocess_variable_font_job(job: VariablePostprocessJob) -> Path:
    """Postprocess one variable font after the parallel Fontmake compilation."""
    set_log_task("variable")
    raw_path = Path(job.raw_path)
    logger.debug("Postprocess variable font: source=%s", raw_path.name)
    is_italic = job.style == "italic"
    file_name = job.font_config.family_name_compact
    if is_italic:
        file_name += "-Italic"
    output_name = f"{file_name}[wght].ttf"
    font = load_font(raw_path)
    try:
        style_name = "Italic" if is_italic else "Regular"
        postscript_name = f"{job.font_config.family_name_compact}-{style_name}"
        update_font_names(
            font=font,
            font_config=job.font_config,
            family_name=job.font_config.family_name,
            style_name=style_name,
            full_name=f"{job.font_config.family_name} {style_name}",
            postscript_name=postscript_name,
            is_skip_subfamily=True,
            variable=True,
        )
        add_weight_axis_values_to_stat(font, italic=is_italic)
        if is_italic:
            add_ital_axis_to_stat(font)
        alias_codepoints(font, job.font_config.codepoint_alias)
        verify_glyph_width(
            font=font,
            expect_widths=job.font_config.get_valid_glyph_width_list(),
            file_name=output_name,
        )
        output_dir = Path(job.runtime_context.output_variable)
        output_dir.mkdir(parents=True, exist_ok=True)
        variable_path = output_dir / output_name
        font.save(variable_path)
        logger.info("Saved variable font to %s", variable_path)
    finally:
        font.close()
    return variable_path


def build_variable_fonts(
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    context: FontmakeBuildContext,
    executor: Executor | None = None,
) -> list[Path]:
    """Postprocess all compiled variable outputs in parallel."""
    jobs = [
        VariablePostprocessJob(
            raw_path=str(context.raw_variable_dir / f"{source.style}.ttf"),
            style=source.style,
            font_config=font_config,
            runtime_context=runtime_context,
        )
        for source in context.sources
    ]
    if executor is None:
        with create_process_executor(
            max_workers=len(jobs), fallback_to_threads=True
        ) as process_executor:
            return list(process_executor.map(postprocess_variable_font_job, jobs))
    return list(executor.map(postprocess_variable_font_job, jobs))


def build_static_fonts(
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    context: FontmakeBuildContext,
    build_format: Literal["ttf", "otf"],
    target_styles: list[str] | None,
    executor: Executor | None = None,
) -> list[Path]:
    """Postprocess one compiled static output format."""
    output_dir = Path(
        runtime_context.output_ttf
        if build_format == "ttf"
        else runtime_context.output_otf
    )
    raw_dir = context.raw_ttf_dir if build_format == "ttf" else context.raw_otf_dir
    static_jobs = [
        StaticPostprocessJob(
            input_path=str(font_path),
            output_dir=str(output_dir),
            font_config=font_config,
            runtime_context=runtime_context,
        )
        for font_path in sorted(raw_dir.glob(f"*.{build_format}"))
        if is_target_style_file(font_path.name, target_styles)
    ]
    return run_process_jobs(
        font_config.pool_size,
        postprocess_static_font_job,
        static_jobs,
        executor,
    )
