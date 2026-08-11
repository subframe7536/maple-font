from __future__ import annotations

from pathlib import Path


def variable_output_dir(output_root: str | Path, locale: str | None = None) -> Path:
    root = Path(output_root)
    if locale is None:
        return root / "Variable"
    return root / f"Variable-{locale}"


def static_output_dir(output_root: str | Path, locale: str) -> Path:
    return Path(output_root) / locale


def merged_variable_name(postscript_prefix: str, italic: bool) -> str:
    suffix = "-Italic" if italic else ""
    return f"{postscript_prefix}{suffix}[wght].ttf"
