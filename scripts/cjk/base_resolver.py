from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from scripts.cjk.builder import build_cjk_fonts, instantiate_cjk_static_from_variable
from scripts.cjk.cache import (
    has_valid_cjk_static_cache,
    static_hash_path,
    variable_hash_path,
    variable_paths,
    verify_static_archive,
    verify_variable_archive,
    write_static_hash,
)
from scripts.errors import CJKBaseUnavailable
from scripts.utils.downloads import download_zip_and_extract
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from concurrent.futures import Executor

    from scripts.cjk.config import CJKBuildConfig
    from scripts.config.base import (
        BuiltinCJKLocaleId,
        ResolvedCJKBuildEntry,
        ResolvedConfig,
    )
    from scripts.config.runtime import BuildRuntimeContext


CJK_STATIC_DOWNLOAD_LOCALES = frozenset(("cn", "jp", "tc", "kr"))
CJKStaticBaseSource = Literal[
    "local-static", "remote-static", "local-variable", "remote-variable"
]


@dataclass(frozen=True, slots=True)
class CJKStaticBaseResolution:
    static_dir: Path
    static_file_prefix: str
    source_kind: CJKStaticBaseSource


class CJKBaseResolver:
    """Resolve reusable CJK bases without coupling runtime paths to CJK I/O."""

    def __init__(
        self,
        runtime_context: BuildRuntimeContext,
        font_config: ResolvedConfig,
        executor: Executor | None = None,
    ) -> None:
        self.runtime_context = runtime_context
        self.font_config = font_config
        self.executor = executor

    @staticmethod
    def static_dir(config: CJKBuildConfig) -> Path:
        return config.output.dir / config.output.static_dir

    @staticmethod
    def _archive_name(locale: BuiltinCJKLocaleId, kind: str) -> str:
        return f"{locale}-base-{kind}.zip"

    @classmethod
    def _download_url(cls, locale: BuiltinCJKLocaleId, kind: str) -> str:
        return (
            "https://github.com/subframe7536/maple-font/"
            + f"releases/download/cjk-base/{cls._archive_name(locale, kind)}"
        )

    @staticmethod
    def _style_names(static_dir: Path, prefix: str) -> set[str]:
        if not static_dir.is_dir():
            return set()
        marker = f"{prefix}-"
        return {
            font.stem.removeprefix(marker)
            for font in static_dir.glob("*.ttf")
            if font.name.startswith(marker)
        }

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
                github_mirror=self.runtime_context.effective_github_mirror,
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
                github_mirror=self.runtime_context.effective_github_mirror,
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

    def _download_static_base(
        self, locale: BuiltinCJKLocaleId, config: CJKBuildConfig
    ) -> bool:
        output_dir = self.static_dir(config)
        if locale not in CJK_STATIC_DOWNLOAD_LOCALES or output_dir.exists():
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
        if locale is None or locale not in CJK_STATIC_DOWNLOAD_LOCALES:
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

    def _resolution(
        self, config: CJKBuildConfig, source_kind: CJKStaticBaseSource
    ) -> CJKStaticBaseResolution:
        return CJKStaticBaseResolution(
            self.static_dir(config), config.naming.static_file_prefix, source_kind
        )

    def resolve_static_base(
        self, entry: ResolvedCJKBuildEntry, required_styles: list[str]
    ) -> CJKStaticBaseResolution:
        """Resolve local static, remote static, then variable CJK base outputs."""
        config = entry.build_config
        required_styles = sorted(set(required_styles))
        static_dir = self.static_dir(config)
        if has_valid_cjk_static_cache(config, static_dir, set(required_styles)):
            return self._resolution(config, "local-static")
        if static_dir.exists():
            logger.warning(
                "Cached CJK static fonts are invalid; preserving cache: locale=%s",
                config.locale_name,
            )
        if entry.download_locale and self._download_static_base(
            entry.download_locale, config
        ):
            missing = [
                style
                for style in required_styles
                if style
                not in self._style_names(static_dir, config.naming.static_file_prefix)
            ]
            if not missing:
                write_static_hash(config, static_dir)
                return self._resolution(config, "remote-static")
            logger.warning(
                "Downloaded CJK static fonts are incomplete; locale=%s",
                config.locale_name,
            )

        resolved_variable_base, failures = self._resolve_variable_static_base(
            entry, required_styles
        )
        if resolved_variable_base is not None:
            return resolved_variable_base
        try:
            build_cjk_fonts(
                config,
                self.font_config,
                vf_only=True,
                executor=self.executor,
                github_mirror=self.runtime_context.effective_github_mirror,
            )
            instantiate_cjk_static_from_variable(
                config,
                self.font_config,
                executor=self.executor,
                required_styles=required_styles,
            )
            return self._resolution(config, "remote-variable")
        except Exception as error:
            failures.append(f"remote variable source: {error}")
            raise CJKBaseUnavailable(
                f"Unable to resolve {config.locale_name} CJK base: "
                + "; ".join(failures)
            ) from error

    def _resolve_variable_static_base(
        self, entry: ResolvedCJKBuildEntry, required_styles: list[str]
    ) -> tuple[CJKStaticBaseResolution | None, list[str]]:
        config = entry.build_config
        failures: list[str] = []
        if entry.common_options.clean_cache:
            return None, [
                "local variable outputs unavailable or clean_cache is enabled"
            ]
        if all(path.is_file() for path in variable_paths(config)):
            try:
                self._instantiate_static_from_variable(config, required_styles)
                return self._resolution(config, "local-variable"), failures
            except Exception as error:
                failures.append(f"local variable instantiation: {error}")
        else:
            failures.append(
                "local variable outputs unavailable or clean_cache is enabled"
            )
        if self.ensure_variable_base(entry):
            try:
                self._instantiate_static_from_variable(config, required_styles)
                return self._resolution(config, "remote-variable"), failures
            except Exception as error:
                failures.append(f"remote variable archive: {error}")
        return None, failures

    def _instantiate_static_from_variable(
        self, config: CJKBuildConfig, required_styles: list[str]
    ) -> None:
        instantiate_cjk_static_from_variable(
            config,
            self.font_config,
            executor=self.executor,
            required_styles=required_styles,
        )
