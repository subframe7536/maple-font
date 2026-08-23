from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ttfautohint import StemWidthMode, ttfautohint

from scripts.font_ops.fonttools import load_font
from scripts.utils.process import run_process_jobs

if TYPE_CHECKING:
    from concurrent.futures import Executor


@dataclass(frozen=True)
class AutoHintJob:
    input_path: str
    params: dict[str, Any]


def get_ttfautohint_options(params: dict[str, Any]) -> dict[str, Any]:
    """Translate build configuration into ttfautohint-py options."""
    options = dict(params)
    stem_width_modes = options.pop("stem_width_mode", None)
    if not stem_width_modes:
        return options

    mode_options = {
        "gray": "gray_stem_width_mode",
        "gdi_cleartype": "gdi_cleartype_stem_width_mode",
        "dw_cleartype": "dw_cleartype_stem_width_mode",
    }
    for source_key, target_key in mode_options.items():
        mode = stem_width_modes.get(source_key)
        if mode is not None:
            options[target_key] = _stem_width_mode(mode)
    return options


def autohint_static_fonts(
    input_path: str | Path,
    params: dict[str, Any],
    *,
    pool_size: int = 1,
    executor: Executor | None = None,
) -> None:
    """Autohint a TTF file or every TTF in a flat directory in place."""
    path = Path(input_path)
    font_paths = [path] if path.is_file() else sorted(path.glob("*.ttf"))
    if not font_paths:
        raise FileNotFoundError(f"No TrueType fonts found in {path}")
    jobs = [AutoHintJob(str(font_path), dict(params)) for font_path in font_paths]
    run_process_jobs(pool_size, autohint_static_font_job, jobs, executor)


def autohint_static_font_job(job: AutoHintJob) -> None:
    """Top-level process-pool entrypoint for in-place static font hinting."""
    font = load_font(job.input_path)
    try:
        if "glyf" not in font:
            raise ValueError(f"Autohinting requires a TrueType font: {job.input_path}")
        buffer = BytesIO()
        font.save(buffer, reorderTables=None)
    finally:
        font.close()

    options = {
        "in_buffer": buffer.getvalue(),
        "out_file": job.input_path,
        "no_info": True,
    }
    options.update(get_ttfautohint_options(job.params))
    ttfautohint(**options)


def _stem_width_mode(mode: str) -> StemWidthMode:
    modes = {
        "natural": StemWidthMode.NATURAL,
        "strong": StemWidthMode.STRONG,
        "quantized": StemWidthMode.QUANTIZED,
    }
    try:
        return modes[mode]
    except KeyError as error:
        raise ValueError(f"Unknown stem width mode: {mode}") from error
