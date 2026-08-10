from __future__ import annotations

import shutil
import tempfile
from dataclasses import asdict, dataclass
from os import environ, listdir, path
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from scripts.cjk.builder import instantiate_cjk_static_from_variable
from scripts.cjk.cache import (
    has_valid_cjk_static_cache,
    static_hash_path,
    variable_hash_path,
    variable_paths,
    verify_static_archive,
    verify_variable_archive,
    write_static_hash,
)
from scripts.config.base import (
    BUILTIN_CJK_LOCALES,
    BuiltinCJKLocaleId,
    ResolvedCJKBuildEntry,
    ResolvedConfig,
)
from scripts.errors import CJKBaseUnavailable
from scripts.external.process import get_font_forge_bin
from scripts.utils.downloads import download_zip_and_extract
from scripts.utils.files import join_path
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from concurrent.futures import Executor

    from scripts.cjk.config import CJKBuildConfig


def check_file_count(
    dir_path: str, min_count: int = 16, end: str | None = None
) -> bool:
    if not path.isdir(dir_path):
        return False
    return (
        len([file for file in listdir(dir_path) if end is None or file.endswith(end)])
        >= min_count
    )


CJK_STATIC_DOWNLOAD_LOCALES = frozenset(BUILTIN_CJK_LOCALES)
CJKStaticBaseSource = Literal[
    "local-static",
    "remote-static",
    "local-variable",
    "remote-variable",
]


@dataclass(frozen=True, slots=True)
class CJKStaticBaseResolution:
    static_dir: Path
    static_file_prefix: str
    source_kind: CJKStaticBaseSource


@dataclass(slots=True)
class BuildRuntimeContext:
    src_dir: str
    output_root: str
    output_otf: str
    output_ttf: str
    output_ttf_hinted: str
    output_variable: str
    output_woff2: str
    output_nf: str
    ttf_base_dir: str
    has_cache: bool
    is_nf_built: bool
    is_cjk_built: bool
    effective_github_mirror: str
    font_forge_bin: str | None
    resolved_vertical_metric: tuple[int, int]

    @classmethod
    def from_config(cls, config: ResolvedConfig) -> BuildRuntimeContext:
        output_root = "fonts"
        output_ttf = join_path(output_root, "TTF")
        output_ttf_hinted = join_path(output_root, "TTF-AutoHint")
        nf_variant = config.get_nf_variant()
        return cls(
            src_dir="source",
            output_root=output_root,
            output_otf=join_path(output_root, "OTF"),
            output_ttf=output_ttf,
            output_ttf_hinted=output_ttf_hinted,
            output_variable=join_path(output_root, "Variable"),
            output_woff2=join_path(output_root, "Woff2"),
            output_nf=join_path(output_root, nf_variant.directory_name),
            ttf_base_dir=output_ttf_hinted if config.use_hinted else output_ttf,
            has_cache=(
                check_file_count(
                    join_path(output_root, "Variable"), min_count=2, end=".ttf"
                )
                and check_file_count(output_ttf, min_count=4, end=".ttf")
                and (
                    not config.needs_hinted_ttf()
                    or check_file_count(output_ttf_hinted, min_count=4, end=".ttf")
                )
                and (
                    not config.wants_format("otf")
                    or check_file_count(
                        join_path(output_root, "OTF"),
                        min_count=4,
                        end=".otf",
                    )
                )
                and (
                    not config.wants_format("woff2")
                    or check_file_count(
                        join_path(output_root, "Woff2"),
                        min_count=4,
                        end=".woff2",
                    )
                )
            ),
            is_nf_built=False,
            is_cjk_built=False,
            effective_github_mirror=environ.get("GITHUB", config.github_mirror),
            font_forge_bin=get_font_forge_bin(),
            resolved_vertical_metric=config.vertical_metric,
        )

    @property
    def output_dir(self) -> str:
        return self.output_root

    @property
    def output_nf_variable(self) -> str:
        return join_path(
            self.output_root,
            f"Variable-{Path(self.output_nf).name}",
        )

    def feature_file_path(self, is_italic: bool, is_cjk: bool = False) -> str:
        return join_path(
            self.src_dir,
            "features",
            ("italic" if is_italic else "regular") + ("_cn" if is_cjk else "") + ".fea",
        )

    def cjk_static_dir(self, preset_config: CJKBuildConfig) -> Path:
        return preset_config.output.dir / preset_config.output.static_dir

    def cjk_static_archive_name(self, locale: BuiltinCJKLocaleId) -> str:
        return f"{locale}-base-static.zip"

    def cjk_static_download_url(self, locale: BuiltinCJKLocaleId) -> str:
        archive_name = self.cjk_static_archive_name(locale)
        return (
            "https://github.com/subframe7536/maple-font/"
            f"releases/download/cjk-base/{archive_name}"
        )

    def cjk_variable_archive_name(self, locale: BuiltinCJKLocaleId) -> str:
        return f"{locale}-base-variable.zip"

    def cjk_variable_download_url(self, locale: BuiltinCJKLocaleId) -> str:
        archive_name = self.cjk_variable_archive_name(locale)
        return (
            "https://github.com/subframe7536/maple-font/"
            f"releases/download/cjk-base/{archive_name}"
        )

    def static_style_names(
        self,
        static_dir: Path,
        static_file_prefix: str,
    ) -> set[str]:
        if not static_dir.is_dir():
            return set()
        prefix = f"{static_file_prefix}-"
        return {
            font_path.stem.removeprefix(prefix)
            for font_path in static_dir.glob("*.ttf")
            if font_path.name.startswith(prefix)
        }

    def missing_cjk_static_styles(
        self,
        static_dir: Path,
        static_file_prefix: str,
        required_styles: list[str],
    ) -> list[str]:
        available_styles = self.static_style_names(static_dir, static_file_prefix)
        return [style for style in required_styles if style not in available_styles]

    def has_valid_cjk_static_base(
        self,
        preset_config: CJKBuildConfig,
        static_dir: Path,
        required_styles: list[str],
    ) -> bool:
        return has_valid_cjk_static_cache(
            preset_config,
            static_dir,
            set(required_styles),
        )

    def should_download_cjk_static_base(
        self, locale: BuiltinCJKLocaleId | None
    ) -> bool:
        return locale in CJK_STATIC_DOWNLOAD_LOCALES

    def _use_local_archive(
        self,
        local_archive: Path,
        archive_name: str,
        output_dir: Path,
        installer: Callable[[Path], bool],
    ) -> bool:
        """Run an archive installer against a temporary local copy."""
        with tempfile.TemporaryDirectory(
            prefix=f".{output_dir.name}-local-archive-",
            dir=output_dir.parent,
        ) as temporary_dir:
            local_copy = Path(temporary_dir) / archive_name
            shutil.copy2(local_archive, local_copy)
            return installer(local_copy)

    def _install_cjk_static_archive(
        self,
        archive_path: Path,
        expected_hash_path: Path,
        output_dir: Path,
        name: str,
        download_url: str | None,
    ) -> bool:
        with tempfile.TemporaryDirectory(
            prefix=f".{output_dir.name}-static-",
            dir=output_dir.parent,
        ) as temporary_dir:
            extracted_dir = Path(temporary_dir) / "files"
            downloaded = download_zip_and_extract(
                name=name,
                url=download_url,
                zip_path=archive_path,
                output_dir=extracted_dir,
                remove_zip=False,
                github_mirror=self.effective_github_mirror,
            )
            if not downloaded:
                return False
            verify_static_archive(
                archive_path,
                expected_hash_path,
                extracted_dir=extracted_dir,
            )
            extracted_dir.replace(output_dir)
        return True

    def download_cjk_static_base(
        self,
        locale: BuiltinCJKLocaleId,
        preset_config: CJKBuildConfig,
    ) -> bool:
        if not self.should_download_cjk_static_base(locale):
            logger.info("Skip CJK static base download: unsupported locale=%s", locale)
            return False

        static_dir = self.cjk_static_dir(preset_config)
        if static_dir.exists():
            logger.info(
                "Skip CJK static base download because source cache exists: locale=%s",
                preset_config.locale_name,
            )
            return False

        static_dir.parent.mkdir(parents=True, exist_ok=True)
        archive_name = self.cjk_static_archive_name(locale)
        static_hash = static_hash_path(preset_config)
        local_archive = preset_config.output.dir / preset_config.output.archive_name
        if local_archive.is_file():
            try:

                def install_local_archive(local_copy: Path) -> bool:
                    return self._install_cjk_static_archive(
                        local_copy,
                        static_hash,
                        static_dir,
                        f"{preset_config.locale_name} local static CJK base font",
                        None,
                    )

                if self._use_local_archive(
                    local_archive,
                    archive_name,
                    static_dir,
                    install_local_archive,
                ):
                    logger.info(
                        "Reuse local CJK static base archive: locale=%s",
                        preset_config.locale_name,
                    )
                    return True
            except (OSError, ValueError) as error:
                logger.warning(
                    "Local CJK static base archive is invalid; try remote asset: "
                    "locale=%s, error=%s",
                    preset_config.locale_name,
                    error,
                )
        try:
            with tempfile.TemporaryDirectory(
                prefix=f".{static_dir.name}-remote-static-",
                dir=static_dir.parent,
            ) as temporary_dir:
                temporary_root = Path(temporary_dir)
                archive_path = temporary_root / archive_name
                if not self._install_cjk_static_archive(
                    archive_path,
                    static_hash,
                    static_dir,
                    f"{preset_config.locale_name} static CJK base font",
                    self.cjk_static_download_url(locale),
                ):
                    return False
            logger.info(
                "Downloaded CJK static base archive: locale=%s",
                preset_config.locale_name,
            )
            return True
        except (OSError, ValueError) as error:
            logger.warning(
                "Downloaded CJK static base archive is invalid: locale=%s, error=%s",
                preset_config.locale_name,
                error,
            )
            return False

    def _install_cjk_variable_archive(
        self,
        archive_path: Path,
        hash_path: Path,
        expected_paths: tuple[Path, Path],
        output_dir: Path,
        locale_name: str,
        download_url: str | None,
    ) -> bool:
        with tempfile.TemporaryDirectory(
            prefix=f".{output_dir.name}-variable-",
            dir=output_dir.parent,
        ) as temporary_dir:
            extracted_dir = Path(temporary_dir) / "files"
            downloaded = download_zip_and_extract(
                name=f"{locale_name} variable CJK base font",
                url=download_url,
                zip_path=archive_path,
                output_dir=extracted_dir,
                remove_zip=False,
                github_mirror=self.effective_github_mirror,
            )
            if not downloaded:
                return False
            verify_variable_archive(
                archive_path,
                hash_path,
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

    def download_cjk_variable_base(
        self,
        locale: BuiltinCJKLocaleId | None,
        preset_config: CJKBuildConfig,
    ) -> bool:
        """Resolve and validate the preprocessed variable base for a locale."""
        if locale is None or locale not in CJK_STATIC_DOWNLOAD_LOCALES:
            logger.info(
                "Skip CJK variable base download: unsupported locale=%s",
                preset_config.locale_name,
            )
            return False

        hash_path = variable_hash_path(preset_config)
        if not hash_path.is_file():
            logger.warning(
                "Skip CJK variable base download because its hash is missing: path=%s",
                hash_path,
            )
            return False

        output_dir = preset_config.output.dir
        archive_name = self.cjk_variable_archive_name(locale)
        archive_path = output_dir / f".{archive_name}.download.zip"
        expected_paths = variable_paths(preset_config)
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            local_archive = output_dir / preset_config.output.variable_archive_name
            if local_archive.is_file():
                try:

                    def install_local_archive(local_copy: Path) -> bool:
                        return self._install_cjk_variable_archive(
                            local_copy,
                            hash_path,
                            expected_paths,
                            output_dir,
                            preset_config.locale_name,
                            None,
                        )

                    if self._use_local_archive(
                        local_archive,
                        archive_name,
                        output_dir,
                        install_local_archive,
                    ):
                        logger.info(
                            "Reuse local CJK variable base archive: locale=%s",
                            preset_config.locale_name,
                        )
                        return True
                except (OSError, ValueError) as error:
                    logger.warning(
                        "Local CJK variable base archive is invalid; try remote asset: "
                        "locale=%s, error=%s",
                        preset_config.locale_name,
                        error,
                    )

            if not self._install_cjk_variable_archive(
                archive_path,
                hash_path,
                expected_paths,
                output_dir,
                preset_config.locale_name,
                self.cjk_variable_download_url(locale),
            ):
                return False
            logger.info(
                "Downloaded CJK variable base: locale=%s",
                preset_config.locale_name,
            )
            return True
        except (OSError, ValueError) as error:
            logger.warning(
                "Downloaded CJK variable base is invalid: locale=%s, error=%s",
                preset_config.locale_name,
                error,
            )
            return False
        finally:
            archive_path.unlink(missing_ok=True)

    def build_cjk_static_base_from_variable(
        self,
        preset_config: CJKBuildConfig,
        build_config: ResolvedConfig,
        builder: Callable[..., None],
        executor: Executor | None = None,
    ) -> None:
        builder(
            preset_config,
            build_config,
            vf_only=True,
            executor=executor,
            github_mirror=self.effective_github_mirror,
        )

    def _resolve_local_cjk_static_base(
        self,
        _clean_cache: bool,
        preset_config: CJKBuildConfig,
        static_dir: Path,
        static_file_prefix: str,
        required_styles: list[str],
        locale_name: str,
    ) -> CJKStaticBaseResolution | None:
        if self.has_valid_cjk_static_base(
            preset_config,
            static_dir,
            required_styles,
        ):
            return CJKStaticBaseResolution(
                static_dir=static_dir,
                static_file_prefix=static_file_prefix,
                source_kind="local-static",
            )

        if static_dir.exists():
            logger.warning(
                "Cached CJK static fonts are invalid; preserving cache: locale=%s",
                locale_name,
            )

        return None

    def _resolve_downloaded_cjk_static_base(
        self,
        locale: BuiltinCJKLocaleId | None,
        preset_config: CJKBuildConfig,
        static_dir: Path,
        static_file_prefix: str,
        required_styles: list[str],
    ) -> CJKStaticBaseResolution | None:
        if not locale or not self.should_download_cjk_static_base(locale):
            logger.info(
                "Skip CJK static base download: unsupported locale=%s",
                preset_config.locale_name,
            )
            return None

        if not self.download_cjk_static_base(locale, preset_config):
            return None

        if self.missing_cjk_static_styles(
            static_dir,
            preset_config.naming.static_file_prefix,
            required_styles,
        ):
            logger.warning(
                "Downloaded CJK static fonts are incomplete; preserving cache and falling back to variable build: locale=%s",
                preset_config.locale_name,
            )
            return None

        write_static_hash(preset_config, static_dir)
        return CJKStaticBaseResolution(
            static_dir=static_dir,
            static_file_prefix=static_file_prefix,
            source_kind="remote-static",
        )

    def _resolve_variable_cjk_static_base(
        self,
        entry: ResolvedCJKBuildEntry,
        required_styles: list[str],
        build_config: ResolvedConfig,
        builder: Callable[..., None],
        executor: Executor | None = None,
    ) -> CJKStaticBaseResolution:
        preset_config = entry.build_config
        static_dir = self.cjk_static_dir(preset_config)
        static_file_prefix = preset_config.naming.static_file_prefix
        clean_cache = entry.common_options.clean_cache
        download_locale = entry.download_locale
        failures: list[str] = []
        variable_output_paths = variable_paths(preset_config)
        if not clean_cache and all(path.is_file() for path in variable_output_paths):
            try:
                instantiate_cjk_static_from_variable(
                    preset_config,
                    build_config,
                    executor=executor,
                    required_styles=required_styles,
                )
                return CJKStaticBaseResolution(
                    static_dir=static_dir,
                    static_file_prefix=static_file_prefix,
                    source_kind="local-variable",
                )
            except Exception as error:
                failures.append(f"local variable instantiation: {error}")
        else:
            failures.append(
                "local variable outputs unavailable or clean_cache is enabled"
            )

        if not clean_cache and download_locale is not None:
            try:
                if not self.download_cjk_variable_base(
                    download_locale,
                    preset_config,
                ):
                    raise FileNotFoundError("remote variable base unavailable")
                instantiate_cjk_static_from_variable(
                    preset_config,
                    build_config,
                    executor=executor,
                    required_styles=required_styles,
                )
                return CJKStaticBaseResolution(
                    static_dir=static_dir,
                    static_file_prefix=static_file_prefix,
                    source_kind="remote-variable",
                )
            except Exception as error:
                failures.append(f"remote variable archive: {error}")

        try:
            self.build_cjk_static_base_from_variable(
                preset_config,
                build_config,
                builder,
                executor,
            )
            instantiate_cjk_static_from_variable(
                preset_config,
                build_config,
                executor=executor,
                required_styles=required_styles,
            )
            return CJKStaticBaseResolution(
                static_dir=static_dir,
                static_file_prefix=static_file_prefix,
                source_kind="remote-variable",
            )
        except Exception as error:
            failures.append(f"remote variable source: {error}")
            raise CJKBaseUnavailable(
                f"Unable to resolve {preset_config.locale_name} CJK base: "
                + "; ".join(failures)
            ) from error

    def resolve_cjk_static_base(
        self,
        entry: ResolvedCJKBuildEntry,
        required_styles: list[str],
        font_config: ResolvedConfig,
        variable_builder: Callable[..., None],
        executor: Executor | None = None,
    ) -> CJKStaticBaseResolution:
        preset_config = entry.build_config
        static_dir = self.cjk_static_dir(preset_config)
        static_file_prefix = preset_config.naming.static_file_prefix
        required_styles = sorted(set(required_styles))
        local_resolution = self._resolve_local_cjk_static_base(
            entry.common_options.clean_cache,
            preset_config,
            static_dir,
            static_file_prefix,
            required_styles,
            preset_config.locale_name,
        )
        if local_resolution is not None:
            return local_resolution

        download_resolution = self._resolve_downloaded_cjk_static_base(
            entry.download_locale,
            preset_config,
            static_dir,
            static_file_prefix,
            required_styles,
        )
        if download_resolution is not None:
            return download_resolution

        return self._resolve_variable_cjk_static_base(
            entry,
            required_styles,
            font_config,
            variable_builder,
            executor,
        )

    def to_dict(self, config: ResolvedConfig | None = None) -> dict[str, Any]:
        data = asdict(self)
        data["output_nf_variable"] = self.output_nf_variable
        if config is not None:
            data["use_font_patcher"] = bool(
                config.nerd_font.extra_args
                or config.nerd_font.use_font_patcher
                or config.nerd_font.glyphs != ["--complete"]
            )
        return data
