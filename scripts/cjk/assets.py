from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.cjk.cache import (
    static_hash_path,
    variable_hash_path,
    variable_paths,
    verify_static_archive,
    verify_variable_archive,
)
from scripts.utils.downloads import download_zip_and_extract
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from scripts.cjk.config import CJKBuildConfig
    from scripts.config.base import BuiltinCJKLocaleId, ResolvedCJKBuildEntry


CJK_BASE_DOWNLOAD_LOCALES = frozenset(("cn", "jp", "tc", "kr"))


def static_base_dir(config: CJKBuildConfig) -> Path:
    """Return the static CJK base directory for one resolved configuration."""
    return config.output.dir / config.output.static_dir


def static_style_names(static_dir: Path, prefix: str) -> set[str]:
    """Return the available static style names for a CJK base directory."""
    if not static_dir.is_dir():
        return set()
    marker = f"{prefix}-"
    return {
        font.stem.removeprefix(marker)
        for font in static_dir.glob("*.ttf")
        if font.name.startswith(marker)
    }


class CJKBaseArchiveStore:
    """Install validated local or remote CJK base archives into their output paths."""

    def __init__(self, github_mirror: str) -> None:
        self.github_mirror = github_mirror

    @staticmethod
    def _archive_name(locale: BuiltinCJKLocaleId, kind: str) -> str:
        return f"{locale}-base-{kind}.zip"

    @classmethod
    def _download_url(cls, locale: BuiltinCJKLocaleId, kind: str) -> str:
        return (
            "https://github.com/subframe7536/maple-font/"
            + f"releases/download/cjk-base/{cls._archive_name(locale, kind)}"
        )

    def _install_static_archive(
        self,
        archive: Path,
        expected_hash: Path,
        output_dir: Path,
        name: str,
        url: str | None,
    ) -> bool:
        with tempfile.TemporaryDirectory(
            prefix=f".{output_dir.name}-static-", dir=output_dir.parent
        ) as temporary_dir:
            extracted_dir = Path(temporary_dir) / "files"
            if not download_zip_and_extract(
                name,
                url,
                archive,
                extracted_dir,
                github_mirror=self.github_mirror,
            ):
                return False
            verify_static_archive(archive, expected_hash, extracted_dir=extracted_dir)
            extracted_dir.replace(output_dir)
        return True

    def _install_variable_archive(
        self,
        archive: Path,
        expected_hash: Path,
        expected_paths: tuple[Path, Path],
        output_dir: Path,
        locale_name: str,
        url: str | None,
    ) -> bool:
        with tempfile.TemporaryDirectory(
            prefix=f".{output_dir.name}-variable-", dir=output_dir.parent
        ) as temporary_dir:
            extracted_dir = Path(temporary_dir) / "files"
            if not download_zip_and_extract(
                f"{locale_name} variable CJK base font",
                url,
                archive,
                extracted_dir,
                github_mirror=self.github_mirror,
            ):
                return False
            verify_variable_archive(
                archive,
                expected_hash,
                tuple(path.name for path in expected_paths),
                extracted_dir=extracted_dir,
            )
            for source_path, target_path in zip(
                (extracted_dir / path.name for path in expected_paths),
                expected_paths,
                strict=True,
            ):
                temporary_path = target_path.with_name(f".{target_path.name}.tmp")
                shutil.copy2(source_path, temporary_path)
                temporary_path.replace(target_path)
        return True

    def _install_local_archive(
        self, local_archive: Path, archive_name: str, output_dir: Path, installer
    ) -> bool:
        with tempfile.TemporaryDirectory(
            prefix=f".{output_dir.name}-local-archive-", dir=output_dir.parent
        ) as temporary_dir:
            archive_copy = Path(temporary_dir) / archive_name
            shutil.copy2(local_archive, archive_copy)
            return installer(archive_copy)

    def install_static_base(
        self, locale: BuiltinCJKLocaleId, config: CJKBuildConfig
    ) -> bool:
        output_dir = static_base_dir(config)
        if locale not in CJK_BASE_DOWNLOAD_LOCALES or output_dir.exists():
            return False
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        archive_name = self._archive_name(locale, "static")
        expected_hash = static_hash_path(config)
        local_archive = config.output.dir / config.output.archive_name
        try:
            if local_archive.is_file() and self._install_local_archive(
                local_archive,
                archive_name,
                output_dir,
                lambda archive: self._install_static_archive(
                    archive,
                    expected_hash,
                    output_dir,
                    f"{config.locale_name} local static CJK base font",
                    None,
                ),
            ):
                logger.info(
                    "Reuse local CJK static base archive: locale=%s", config.locale_name
                )
                return True
        except (OSError, ValueError) as error:
            logger.warning(
                "Local CJK static base archive is invalid; locale=%s, error=%s",
                config.locale_name,
                error,
            )
        try:
            with tempfile.TemporaryDirectory(
                prefix=f".{output_dir.name}-remote-static-", dir=output_dir.parent
            ) as temporary_dir:
                archive = Path(temporary_dir) / archive_name
                if not self._install_static_archive(
                    archive,
                    expected_hash,
                    output_dir,
                    f"{config.locale_name} static CJK base font",
                    self._download_url(locale, "static"),
                ):
                    return False
            logger.info(
                "Downloaded CJK static base archive: locale=%s", config.locale_name
            )
            return True
        except (OSError, ValueError) as error:
            logger.warning(
                "Downloaded CJK static base archive is invalid: locale=%s, error=%s",
                config.locale_name,
                error,
            )
            return False

    def ensure_variable_base(self, entry: ResolvedCJKBuildEntry) -> bool:
        """Populate a preset's reusable variable base from a verified archive."""
        locale = entry.download_locale
        config = entry.build_config
        if locale is None or locale not in CJK_BASE_DOWNLOAD_LOCALES:
            return False
        expected_hash = variable_hash_path(config)
        if not expected_hash.is_file():
            return False
        output_dir = config.output.dir
        output_dir.mkdir(parents=True, exist_ok=True)
        archive_name = self._archive_name(locale, "variable")
        archive = output_dir / f".{archive_name}.download.zip"
        expected_paths = variable_paths(config)

        try:
            local_archive = output_dir / config.output.variable_archive_name
            if local_archive.is_file() and self._install_local_archive(
                local_archive,
                archive_name,
                output_dir,
                lambda copy: self._install_variable_archive(
                    copy,
                    expected_hash,
                    expected_paths,
                    output_dir,
                    config.locale_name,
                    None,
                ),
            ):
                logger.info(
                    "Reuse local CJK variable base archive: locale=%s",
                    config.locale_name,
                )
                return True
        except (OSError, ValueError) as error:
            logger.warning(
                "Local CJK variable base archive is invalid; locale=%s, error=%s",
                config.locale_name,
                error,
            )

        try:
            if not self._install_variable_archive(
                archive,
                expected_hash,
                expected_paths,
                output_dir,
                config.locale_name,
                self._download_url(locale, "variable"),
            ):
                return False
            logger.info("Downloaded CJK variable base: locale=%s", config.locale_name)
            return True
        except (OSError, ValueError) as error:
            logger.warning(
                "Downloaded CJK variable base is invalid: locale=%s, error=%s",
                config.locale_name,
                error,
            )
            return False
        finally:
            archive.unlink(missing_ok=True)
