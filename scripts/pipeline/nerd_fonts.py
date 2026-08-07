from __future__ import annotations

from dataclasses import dataclass
from os import makedirs, path, remove
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.cjk.variable import (
    drop_font_tables,
    merge_masters_into_vf,
    recalculate_font_metrics,
)
from scripts.errors import BuildDependencyError
from scripts.external.process import run as run_command
from scripts.external.process import run_process_jobs
from scripts.font_ops.fonttools import TTFont, load_font, save_font_atomic
from scripts.font_ops.glyph_transform import smart_change_width
from scripts.font_ops.merge import merge_ttfonts
from scripts.font_ops.metrics import adjust_line_height, verify_glyph_width
from scripts.font_ops.names import parse_style_name, update_font_names
from scripts.font_ops.nerd_font import parse_codes_from_json
from scripts.font_ops.opentype import (
    add_ital_axis_to_stat,
    add_weight_axis_values_to_stat,
)
from scripts.font_ops.subset import subset_to_codepoints
from scripts.pipeline.artifacts import require_existing_files, require_unique_targets
from scripts.utils.downloads import check_font_patcher
from scripts.utils.logging import (
    TaskName,
    log_task,
    log_task_complete,
    logger,
    set_log_task,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from concurrent.futures import Executor

    from scripts.config.base import ResolvedConfig
    from scripts.config.runtime import BuildRuntimeContext


@dataclass(frozen=True)
class NerdFontBuildJob:
    font_path: Path
    output_path: Path
    use_font_patcher: bool
    font_config: ResolvedConfig
    runtime_context: BuildRuntimeContext


@dataclass(frozen=True)
class NerdFontVariableBuildJob:
    variable_path: Path
    static_source_path: Path | None
    output_path: Path
    is_italic: bool
    font_config: ResolvedConfig
    runtime_context: BuildRuntimeContext


def should_use_font_patcher(config: ResolvedConfig) -> bool:
    return config.nerd_font.uses_font_patcher()


def ensure_font_patcher_available(
    config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
) -> None:
    if not should_use_font_patcher(config):
        return
    if not runtime_context.font_forge_bin or not path.exists(
        runtime_context.font_forge_bin
    ):
        raise BuildDependencyError(
            f"FontForge bin ({runtime_context.font_forge_bin}) not found, "
            "cannot build with Nerd Font Patcher"
        )
    if not check_font_patcher(
        version=config.nerd_font.version,
        github_mirror=runtime_context.effective_github_mirror,
    ):
        raise BuildDependencyError(
            "Nerd Font Patcher assets are unavailable for the requested version"
        )


def build_nf_by_prebuild_nerd_font(
    font_path: Path,
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
) -> TTFont:
    variant = font_config.get_nf_variant()
    nf_base_font_path = str(variant.base_path(runtime_context.src_dir))
    temporary_path = None
    if font_config.get_width_name():
        temporary_font = load_font(nf_base_font_path)
        try:
            smart_change_width(
                font=temporary_font,
                target_width=font_config.get_target_width(),
                original_ref_width=font_config.glyph_width,
                also_scale_y=True,
            )
            temporary_path = f"{runtime_context.output_dir}/NF-Base-{font_path.name}"
            save_font_atomic(temporary_font, temporary_path)
        finally:
            temporary_font.close()

    try:
        return merge_ttfonts(
            base_font_path=str(font_path),
            extra_font_path=temporary_path or nf_base_font_path,
        )
    finally:
        if temporary_path is not None:
            remove(temporary_path)


def build_nf_by_font_patcher(
    font_path: Path,
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    output_dir: str | Path | None = None,
) -> TTFont:
    """Patch a base font with FontPatcher and return the generated font."""
    if runtime_context.font_forge_bin is None:
        raise BuildDependencyError(
            "FontForge bin is unavailable after dependency validation"
        )
    patcher_output_dir = output_dir or runtime_context.output_nf
    makedirs(patcher_output_dir, exist_ok=True)
    patcher_args = [
        runtime_context.font_forge_bin,
        "FontPatcher/font-patcher",
        "-l",
        "--careful",
        "--outputdir",
        str(patcher_output_dir),
        *font_config.nerd_font.glyphs,
    ]
    if font_config.nerd_font.propo:
        patcher_args.append("--variable-width-glyphs")
    elif font_config.nerd_font.mono:
        patcher_args.append("--mono")
    patcher_args.extend(font_config.nerd_font.extra_args)
    patcher_args.append(str(font_path))
    run_command(patcher_args)

    variant = font_config.get_nf_variant()
    generated_path = str(variant.patched_font_path(patcher_output_dir, font_path.name))
    font = load_font(generated_path)
    remove(generated_path)
    if "nonmarkingreturn" in font.getGlyphNames():
        font["hmtx"]["nonmarkingreturn"] = (600, 0)
    return font


def load_nerd_font_variable_source(
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    source_font_path: Path | None = None,
) -> TTFont:
    """Load the static glyph source used to add Nerd Font glyphs to a VF."""
    variant = font_config.get_nf_variant()
    if should_use_font_patcher(font_config):
        patched_path = variant.patched_style_path(
            runtime_context.output_nf,
            font_config.family_name_compact,
        )
        if source_font_path is None and patched_path.is_file():
            font = load_font(patched_path, decompile=True)
        else:
            if source_font_path is None:
                source_font_path = (
                    Path(runtime_context.ttf_base_dir)
                    / f"{font_config.family_name_compact}-Regular.ttf"
                )
            font = build_nf_by_font_patcher(
                source_font_path,
                font_config,
                runtime_context,
                output_dir=Path(runtime_context.output_root) / "temp" / "nf-patcher",
            )
        return subset_to_codepoints(font, parse_codes_from_json())

    font = load_font(variant.base_path(runtime_context.src_dir), decompile=True)
    if font_config.get_width_name():
        smart_change_width(
            font=font,
            target_width=font_config.get_target_width(),
            original_ref_width=font_config.glyph_width,
            also_scale_y=True,
        )
    return font


def build_nf(
    font_path: Path,
    output_path: Path,
    load_source: Callable[[Path, ResolvedConfig, BuildRuntimeContext], TTFont],
    use_font_patcher: bool,
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
) -> Path:
    logger.debug(
        "Build Nerd Font variant: source=%s, suffix=%s",
        font_path.name,
        font_config.get_nf_variant().suffix,
    )
    font = load_source(font_path, font_config, runtime_context)
    try:
        style_compact = font_path.stem.rsplit("-", 1)[-1]
        (
            style_prefix,
            legacy_style,
            preferred_style,
            skip_subfamily,
            _,
        ) = parse_style_name(style_name_compact=style_compact)
        symbol = font_config.get_nf_variant().symbol
        postscript_name = f"{font_config.family_name_compact}-{symbol}-{style_compact}"
        update_font_names(
            font=font,
            font_config=font_config,
            family_name=f"{font_config.family_name} {symbol}{style_prefix}",
            style_name=legacy_style,
            full_name=f"{font_config.family_name} {symbol} {preferred_style}",
            postscript_name=postscript_name,
            is_skip_subfamily=skip_subfamily,
            preferred_family_name=f"{font_config.family_name} {symbol}",
            preferred_style_name=preferred_style,
        )
        if font_config.line_height != 1:
            adjust_line_height(
                font,
                font_config.line_height,
                runtime_context.resolved_vertical_metric,
            )
        if not (use_font_patcher or font_config.get_nf_suffix() == "Propo"):
            verify_glyph_width(
                font=font,
                expect_widths=font_config.get_valid_glyph_width_list(),
                file_name=postscript_name,
            )
        save_font_atomic(font, output_path)
        logger.info("Saved Nerd Font to %s", output_path)
    finally:
        font.close()
    return output_path


def build_nf_job(job: NerdFontBuildJob) -> Path:
    set_log_task("nerd-font")
    load_source = (
        build_nf_by_font_patcher
        if job.use_font_patcher
        else build_nf_by_prebuild_nerd_font
    )
    return build_nf(
        job.font_path,
        job.output_path,
        load_source,
        job.use_font_patcher,
        job.font_config,
        job.runtime_context,
    )


def build_nf_variable_job(job: NerdFontVariableBuildJob) -> Path:
    set_log_task("nerd-font")
    logger.debug(
        "Build variable Nerd Font: source=%s, output=%s",
        job.variable_path.name,
        job.output_path,
    )
    font = load_font(job.variable_path, decompile=True)
    try:
        source = load_nerd_font_variable_source(
            font_config=job.font_config,
            runtime_context=job.runtime_context,
            source_font_path=job.static_source_path,
        )
        try:
            merge_masters_into_vf(font, source, source, source)
            drop_font_tables(font, ("HVAR", "VVAR"))
            recalculate_font_metrics(font)

            symbol = job.font_config.get_nf_variant().symbol
            style_name = "Italic" if job.is_italic else "Regular"
            postscript_prefix = f"{job.font_config.family_name_compact}-{symbol}"
            update_font_names(
                font=font,
                font_config=job.font_config,
                family_name=f"{job.font_config.family_name} {symbol}",
                style_name=style_name,
                full_name=f"{job.font_config.family_name} {symbol} {style_name}",
                postscript_name=f"{postscript_prefix}-{style_name}",
                is_skip_subfamily=True,
                variable=True,
            )
            add_weight_axis_values_to_stat(font, italic=job.is_italic)
            if job.is_italic:
                add_ital_axis_to_stat(font)
            save_font_atomic(font, job.output_path)
            logger.info("Saved variable Nerd Font to %s", job.output_path)
        finally:
            source.close()
    finally:
        font.close()
    return job.output_path


def build_nerd_fonts(
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    font_paths: list[Path],
    executor: Executor | None = None,
) -> list[Path]:
    """Build configured Nerd Font variants."""
    if not font_config.nerd_font.enable:
        return []

    started_at = log_task(TaskName.NERD_FONT, "Build Nerd Font outputs")
    require_existing_files(font_paths, "Nerd Font")
    symbol = font_config.get_nf_variant().symbol
    use_font_patcher = should_use_font_patcher(font_config)
    jobs = [
        NerdFontBuildJob(
            font_path=font_path,
            output_path=Path(runtime_context.output_nf)
            / (
                f"{font_config.family_name_compact}-{symbol}-"
                f"{font_path.stem.rsplit('-', 1)[-1]}.ttf"
            ),
            use_font_patcher=use_font_patcher,
            font_config=font_config,
            runtime_context=runtime_context,
        )
        for font_path in font_paths
    ]
    require_unique_targets([job.output_path for job in jobs], "Nerd Font")

    ensure_font_patcher_available(font_config, runtime_context)
    makedirs(runtime_context.output_nf, exist_ok=True)
    logger.debug(
        "Patch Nerd Font: version=%s, method=%s",
        font_config.nerd_font.version,
        "Font Patcher" if use_font_patcher else "prebuilt base font",
    )
    output_paths = run_process_jobs(
        font_config.pool_size,
        build_nf_job,
        jobs,
        executor,
    )
    runtime_context.is_nf_built = True
    log_task_complete(started_at, f"{len(output_paths)} fonts")
    return output_paths


def build_nerd_font_variable_fonts(
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    variable_paths: list[Path],
    static_source_paths: list[Path] | None = None,
    executor: Executor | None = None,
) -> list[Path]:
    """Build variable Nerd Font outputs by merging static icon glyph sources."""
    if not font_config.nerd_font.enable or not font_config.nerd_font.variable:
        return []

    started_at = log_task(TaskName.NERD_FONT, "Build variable Nerd Font outputs")
    require_existing_files(variable_paths, "variable Nerd Font")
    resolved_static_source_paths: list[Path | None]
    if should_use_font_patcher(font_config):
        if static_source_paths is None:
            raise ValueError("FontPatcher variable NF builds require static sources")
        require_existing_files(static_source_paths, "variable Nerd Font patcher")
        resolved_static_source_paths = list(static_source_paths)
    else:
        resolved_static_source_paths = (
            list(static_source_paths)
            if static_source_paths is not None
            else [None] * len(variable_paths)
        )

    if len(variable_paths) != len(resolved_static_source_paths):
        raise ValueError("Variable NF inputs and static sources must have equal length")

    symbol = font_config.get_nf_variant().symbol
    jobs = []
    output_dir = Path(runtime_context.output_nf_variable)
    for variable_path, static_source_path in zip(
        variable_paths, resolved_static_source_paths, strict=False
    ):
        is_italic = variable_path.name.endswith("-Italic[wght].ttf")
        style_suffix = "-Italic" if is_italic else ""
        jobs.append(
            NerdFontVariableBuildJob(
                variable_path=variable_path,
                static_source_path=static_source_path,
                output_path=output_dir
                / f"{font_config.family_name_compact}-{symbol}{style_suffix}[wght].ttf",
                is_italic=is_italic,
                font_config=font_config,
                runtime_context=runtime_context,
            )
        )
    require_unique_targets([job.output_path for job in jobs], "variable Nerd Font")

    ensure_font_patcher_available(font_config, runtime_context)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = run_process_jobs(
        font_config.pool_size,
        build_nf_variable_job,
        jobs,
        executor,
    )
    log_task_complete(started_at, f"{len(output_paths)} fonts")
    return output_paths
