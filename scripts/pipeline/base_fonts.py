from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

from ttfautohint import ttfautohint

from scripts.cjk.builder import get_ttfautohint_options
from scripts.external.process import run_process_jobs
from scripts.feature.apply import apply_binary_features
from scripts.font_ops.conversion import convert_to_web
from scripts.font_ops.fonttools import load_font
from scripts.pipeline.artifacts import require_existing_files, require_unique_targets
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
class MonoAutohintJob:
    font_path: Path
    reference_path: Path
    output_path: Path
    font_config: ResolvedConfig
    runtime_context: BuildRuntimeContext


def build_mono_autohint(
    font_path: Path,
    reference_path: Path,
    output_path: Path,
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
) -> Path:
    style_compact = font_path.stem.rsplit("-", 1)[-1]
    logger.debug("Auto-hint font: %s", output_path.name)

    font = load_font(font_path)
    try:
        is_italic = "Italic" in style_compact
        apply_binary_features(
            config=font_config,
            font=font,
            issue_fea_dir=runtime_context.output_dir,
            is_italic=is_italic,
            is_cn=False,
            is_hinted=True,
            fea_path=runtime_context.feature_file_path(is_italic),
        )
        head = font.table("head")
        head.flags |= 1 << 2 | 1 << 3
        buffer = BytesIO()
        font.save(buffer)
    finally:
        font.close()

    options = {
        "in_buffer": buffer.getvalue(),
        "reference_file": str(reference_path),
        "out_file": str(output_path),
        "windows_compatibility": True,
    }
    options.update(get_ttfautohint_options(font_config.ttfautohint_param))
    ttfautohint(**options)
    logger.info("Saved hinted font to %s", output_path)
    return output_path


def build_mono_autohint_job(job: MonoAutohintJob) -> Path:
    set_log_task("ttf-autohint")
    return build_mono_autohint(
        job.font_path,
        job.reference_path,
        job.output_path,
        job.font_config,
        job.runtime_context,
    )


def build_base_fonts(
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    font_paths: list[Path],
    executor: Executor | None = None,
) -> list[Path]:
    """Generate hinted TTF derivatives from production static TTF fonts."""
    started_at = log_task(TaskName.TTF_AUTOHINT, "Hint static TTF")
    require_existing_files(font_paths, "TTF auto-hint")
    reference_path = Path(runtime_context.output_ttf) / (
        f"{font_config.family_name_compact}-Regular.ttf"
    )
    require_existing_files([reference_path], "TTF auto-hint reference")
    jobs = [
        MonoAutohintJob(
            font_path=font_path,
            reference_path=reference_path,
            output_path=Path(runtime_context.output_ttf_hinted) / font_path.name,
            font_config=font_config,
            runtime_context=runtime_context,
        )
        for font_path in font_paths
    ]
    require_unique_targets(
        [job.output_path for job in jobs],
        "TTF auto-hint",
    )
    output_paths = run_process_jobs(
        font_config.pool_size,
        build_mono_autohint_job,
        jobs,
        executor,
    )
    log_task_complete(started_at, f"{len(output_paths)} fonts")
    return output_paths


def build_woff2_fonts(
    font_paths: list[Path],
    runtime_context: BuildRuntimeContext,
    executor: Executor | None = None,
) -> list[Path]:
    """Convert generated static TTF fonts to WOFF2."""
    started_at = log_task(TaskName.WOFF2, "Convert static TTF to WOFF2")
    output_paths = convert_to_web(
        font_paths,
        output_dir=runtime_context.output_woff2,
        flavor="woff2",
        executor=executor,
    )
    log_task_complete(started_at, f"{len(output_paths)} fonts")
    return output_paths
