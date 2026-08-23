from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from scripts.cjk.assets import (
    CJKBaseArchiveStore,
    static_base_dir,
    static_style_names,
)
from scripts.cjk.builder import build_cjk_fonts, instantiate_cjk_static_from_variable
from scripts.cjk.cache import (
    has_valid_cjk_static_cache,
    variable_paths,
    write_static_hash,
)
from scripts.utils.errors import CJKBaseUnavailable
from scripts.utils.logging import logger

if TYPE_CHECKING:
    from concurrent.futures import Executor
    from pathlib import Path

    from scripts.cjk.config import CJKBuildConfig
    from scripts.config.base import ResolvedCJKBuildEntry, ResolvedConfig
    from scripts.config.runtime import BuildRuntimeContext


CJKStaticBaseSource = Literal[
    "local-static", "remote-static", "local-variable", "remote-variable"
]


@dataclass(frozen=True, slots=True)
class CJKStaticBaseResolution:
    static_dir: Path
    static_file_prefix: str
    source_kind: CJKStaticBaseSource


class CJKBaseResolver:
    """Resolve reusable CJK bases through cache, archive, and source fallbacks."""

    def __init__(
        self,
        runtime_context: BuildRuntimeContext,
        font_config: ResolvedConfig,
        executor: Executor | None = None,
    ) -> None:
        self.runtime_context = runtime_context
        self.font_config = font_config
        self.executor = executor
        self.archive_store = CJKBaseArchiveStore(
            runtime_context.effective_github_mirror
        )

    @staticmethod
    def static_dir(config: CJKBuildConfig) -> Path:
        return static_base_dir(config)

    def ensure_variable_base(self, entry: ResolvedCJKBuildEntry) -> bool:
        """Install a reusable variable base when the selected entry supports it."""
        return self.archive_store.ensure_variable_base(entry)

    def _resolution(
        self, config: CJKBuildConfig, source_kind: CJKStaticBaseSource
    ) -> CJKStaticBaseResolution:
        return CJKStaticBaseResolution(
            static_base_dir(config), config.naming.static_file_prefix, source_kind
        )

    def resolve_static_base(
        self, entry: ResolvedCJKBuildEntry, required_styles: list[str]
    ) -> CJKStaticBaseResolution:
        """Resolve local static, remote static, then variable CJK base outputs."""
        config = entry.build_config
        required_styles = sorted(set(required_styles))
        static_dir = static_base_dir(config)
        if has_valid_cjk_static_cache(config, static_dir, set(required_styles)):
            return self._resolution(config, "local-static")
        if static_dir.exists():
            logger.warning(
                "Cached CJK static fonts are invalid; preserving cache: locale=%s",
                config.locale_name,
            )
        if entry.download_locale and self.archive_store.install_static_base(
            entry.download_locale, config
        ):
            missing = [
                style
                for style in required_styles
                if style
                not in static_style_names(static_dir, config.naming.static_file_prefix)
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
        if self.archive_store.ensure_variable_base(entry):
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
