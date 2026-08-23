from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from scripts.font_ops.fonttools import load_font
from scripts.utils.logging import logger, set_log_task
from scripts.utils.process import create_process_executor, run_jobs

if TYPE_CHECKING:
    from collections.abc import Sequence
    from concurrent.futures import Executor

WebFontFlavor = Literal["woff", "woff2"]


@dataclass(frozen=True, slots=True)
class WebFontConversionJob:
    font_path: Path
    target_dir: Path
    flavor: WebFontFlavor


def _web_font_name(font_path: Path, flavor: WebFontFlavor) -> str:
    if flavor == "woff2":
        return f"{font_path.stem}.woff2"
    return f"{font_path.name}.{flavor}"


def _convert_font_to_web(
    job: WebFontConversionJob,
) -> Path:
    set_log_task(job.flavor)
    target_path = job.target_dir / _web_font_name(job.font_path, job.flavor)
    font = load_font(job.font_path)
    try:
        font.flavor = job.flavor
        font.save(target_path, reorderTables=False)
    finally:
        font.close()
    logger.info("Saved %s font to %s", job.flavor.upper(), target_path)
    return target_path


def convert_to_web(
    input_path: str | Path | Sequence[str | Path],
    output_dir: str | Path | None = None,
    flavor: WebFontFlavor = "woff2",
    executor: Executor | None = None,
) -> list[Path]:
    """Convert an SFNT font, flat directory, or explicit font sequence."""
    source: Path | None
    if isinstance(input_path, (str, Path)):
        source = Path(input_path)
        font_paths = (
            [source]
            if source.is_file()
            else sorted(
                path
                for path in source.iterdir()
                if path.is_file() and path.suffix.lower() in {".ttf", ".otf"}
            )
        )
    else:
        source = None
        font_paths = [Path(path) for path in input_path]
        invalid = [
            path for path in font_paths if path.suffix.lower() not in {".ttf", ".otf"}
        ]
        if invalid:
            formatted = ", ".join(str(path) for path in invalid)
            raise ValueError(f"Explicit inputs must be SFNT fonts: {formatted}")
        missing = [path for path in font_paths if not path.is_file()]
        if missing:
            formatted = ", ".join(str(path) for path in missing)
            raise FileNotFoundError(
                f"Missing {flavor.upper()} conversion input files: {formatted}"
            )

    if not font_paths:
        location = source if source is not None else "explicit input sequence"
        raise FileNotFoundError(f"No SFNT fonts found in {location}")

    if output_dir is not None:
        target_dir = Path(output_dir)
    elif source is None:
        raise ValueError("output_dir is required for an explicit input sequence")
    else:
        target_dir = source.parent if source.is_file() else source

    target_paths = [target_dir / _web_font_name(path, flavor) for path in font_paths]
    if len(set(target_paths)) != len(target_paths):
        raise ValueError(f"Duplicate {flavor.upper()} conversion output paths")
    target_dir.mkdir(parents=True, exist_ok=True)
    jobs = [WebFontConversionJob(path, target_dir, flavor) for path in font_paths]
    if executor is not None:
        return run_jobs(executor, _convert_font_to_web, jobs)

    with create_process_executor(
        min(len(font_paths), 4), fallback_to_threads=True
    ) as process_executor:
        return run_jobs(process_executor, _convert_font_to_web, jobs)
