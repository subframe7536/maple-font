from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from scripts.cjk.config import CJKNamingConfig, CJKOutputConfig

LOCALE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9]+$")


def resolve_cli_path(value: str | None) -> Path | None:
    """Resolve an optional CLI path relative to the current working directory."""
    return Path(value).expanduser() if value else None


def validate_locale_name(value: Any) -> str:
    """Validate the compact locale suffix used to derive CJK output names."""
    if not isinstance(value, str) or not value:
        raise ValueError("locale_name must be a non-empty ASCII token")
    if not LOCALE_NAME_PATTERN.fullmatch(value):
        raise ValueError("locale_name must contain only ASCII letters and digits")
    return value


def output_config_from_locale(locale_name: str) -> CJKOutputConfig:
    """Derive uncustomizable output paths from the locale suffix."""
    locale_dir = locale_name.lower()
    return CJKOutputConfig(
        dir=Path("sources/cjk") / locale_dir,
        regular_variable=f"MapleMono-{locale_name}-VF.ttf",
        italic_variable=f"MapleMono-{locale_name}-Italic-VF.ttf",
        static_dir="static",
        static_hash=f"static-{locale_dir}.sha256",
        archive_name=f"{locale_dir}-base-static.zip",
        variable_hash=f"variable-{locale_dir}.sha256",
        variable_archive_name=f"{locale_dir}-base-variable.zip",
    )


def naming_config_from_locale(locale_name: str) -> CJKNamingConfig:
    """Derive uncustomizable CJK font naming from the locale suffix."""
    return CJKNamingConfig(
        family_name=f"Maple Mono {locale_name}",
        postscript_prefix=f"MapleMono{locale_name}",
        static_file_prefix=f"MapleMono{locale_name}",
    )


def temp_dir_from_locale(locale_name: str) -> Path:
    """Derive the uncustomizable temporary directory from the locale suffix."""
    return Path("sources/cjk") / locale_name.lower() / "temp"


def resolve_config_path(base_dir: Path, value: str | None, default: str) -> Path:
    """Resolve a config path relative to the repo root or the config file."""
    raw = Path(value or default)
    if raw.is_absolute():
        return raw
    repo_relative = Path.cwd() / raw
    if repo_relative.exists() or str(raw).startswith("sources/"):
        return repo_relative
    return base_dir / raw
