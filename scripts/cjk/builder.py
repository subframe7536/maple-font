from __future__ import annotations

from dataclasses import dataclass
from os import cpu_count, makedirs
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.cjk.cache import write_static_hash, write_variable_hash
from scripts.cjk.config import CJKBuildConfig, CJKWeightInstance
from scripts.cjk.instances import (
    StaticInstanceJob,
    feature_weight_instances,
    instantiate_italic_masters_from_vf,
    instantiate_static_font_job,
    map_weight_coordinate,
)
from scripts.cjk.outlines import detect_outline_format
from scripts.cjk.postprocess import finalize_variable_font, load_feature_variable_font
from scripts.cjk.source import (
    SourceBuildState,
    get_allowed_codepoints,
    prepare_source_masters,
    prepare_source_subset,
)
from scripts.cjk.variable import (
    get_cmap_codepoints,
    get_unicode_cmap,
    make_italic_master_file,
    make_italic_variable_font,
    merge_masters_into_vf,
    weight_axis,
)
from scripts.font_ops.fonttools import TTFont, load_font, save_font_atomic
from scripts.utils.downloads import resolve_cached_download
from scripts.utils.errors import CJKSourceUnavailable
from scripts.utils.files import archive
from scripts.utils.logging import logger, set_log_task
from scripts.utils.process import SynchronousExecutor, create_process_executor, is_ci

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable
    from concurrent.futures import Executor

    from scripts.font_ops.names import FontNameConfig


@dataclass(frozen=True)
class BuildStats:
    added_glyphs: tuple[str, ...]
    added_codepoints: int


def create_font_executor(pool_size: int = 4) -> Executor:
    """Create a bounded executor for expensive font instantiation work."""
    if is_ci():
        pool_size = 1
    if pool_size <= 1:
        return SynchronousExecutor()
    return create_process_executor(
        min(pool_size, 4, cpu_count() or 4),
        fallback_to_threads=True,
    )


class CJKBuilder:
    """Coordinate the shared CJK build pipeline without holding live fonts."""

    def __init__(
        self,
        config: CJKBuildConfig,
        font_config: FontNameConfig,
        executor: Executor | None = None,
        github_mirror: str = "github.com",
    ) -> None:
        self.config = config
        self.font_config = font_config
        self.process_pool = executor
        self._owns_process_pool = executor is None
        self.github_mirror = github_mirror
        self.regular_output = config.output.dir / config.output.regular_variable
        self.italic_output = config.output.dir / config.output.italic_variable
        self.static_dir = config.output.dir / config.output.static_dir

    def build(self, vf_only: bool = False) -> None:
        task = self.config.locale_name.lower()
        set_log_task(task)
        logger.debug("Build CJK fonts")
        download = self.config.source.download
        try:
            resolve_cached_download(
                "CJK source font",
                self.config.source.path,
                None if download is None else download.url,
                self.github_mirror,
                path_in_archive=None if download is None else download.path_in_archive,
            )
        except FileNotFoundError as error:
            raise CJKSourceUnavailable(str(error)) from error
        if self.process_pool is None:
            self.process_pool = create_font_executor(
                getattr(self.font_config, "pool_size", 4)
            )
        try:
            self.config.output.dir.mkdir(parents=True, exist_ok=True)
            regular_font, source_state = self._build_regular_variable_font()
            try:
                italic_font = self._build_italic_variable_font(source_state)
                try:
                    self._write_variable_outputs(regular_font, italic_font)
                finally:
                    italic_font.close()
            finally:
                regular_font.close()

            self._write_variable_artifacts()

            if vf_only:
                logger.debug("Skip CJK static font generation because --vf-only is set")
                return

            logger.info(f"Instantiate {self.config.locale_name} static fonts")
            static_dir = self._build_static_fonts(
                (
                    self.config.output.regular_variable,
                    self.config.output.italic_variable,
                )
            )
            self._write_static_artifacts(static_dir)
            logger.debug("CJK build complete")
        finally:
            if self._owns_process_pool and self.process_pool is not None:
                self.process_pool.shutdown(wait=True, cancel_futures=True)
                self.process_pool = None

    def _require_process_pool(self) -> Executor:
        if self.process_pool is None:
            raise RuntimeError("CJKBuilder process pool is not initialized")
        return self.process_pool

    def _prepare_source_build_state(
        self,
        feature_font: TTFont,
    ) -> tuple[SourceBuildState, set[str]]:
        base_codepoints = get_cmap_codepoints(feature_font)
        protected_glyphs = set(get_unicode_cmap(feature_font).values())

        source_font = load_font(self.config.source.path, decompile=True)
        try:
            if "fvar" not in source_font:
                raise ValueError(
                    f"Source font must be variable: {self.config.source.path}"
                )
            outline_format = detect_outline_format(
                source_font,
                self.config.source.path,
            )
            source_codepoints = get_cmap_codepoints(source_font)
            keep_codepoints = get_allowed_codepoints(source_font, self.config)
        finally:
            source_font.close()

        if outline_format == "cff2":
            logger.debug("Convert CFF2 source masters to glyf TTF")
        logger.debug("CJK source Unicode count: count=%s", len(source_codepoints))
        logger.debug("CJK selected Unicode count: count=%s", len(keep_codepoints))

        subset_path = self.config.temp_dir / (
            "source-subset.otf" if outline_format == "cff2" else "source-subset.ttf"
        )
        logger.debug(
            "Subset CJK source font: source=%s, selected_unicodes=%s, output=%s",
            self.config.source.path,
            len(keep_codepoints),
            subset_path,
        )
        removed = prepare_source_subset(
            self.config.source.path,
            keep_codepoints,
            base_codepoints,
            self.config,
            subset_path,
        )
        logger.debug(
            "Removed base and feature Unicode values from CJK subset: count=%s", removed
        )
        logger.debug(
            "CJK source subset ready: output=%s, removed_unicodes=%s",
            subset_path,
            removed,
        )

        master_paths = prepare_source_masters(
            subset_path,
            self.config,
            self._require_process_pool(),
            feature_font.table("head").unitsPerEm,
            outline_format,
        )
        return (
            SourceBuildState(
                outline_format=outline_format,
                subset_path=subset_path,
                source_codepoints=source_codepoints,
                keep_codepoints=keep_codepoints,
                master_paths=master_paths,
            ),
            protected_glyphs,
        )

    def _build_regular_variable_font(self) -> tuple[TTFont, SourceBuildState]:
        logger.info("Build regular CJK variable font")
        feature_font = load_feature_variable_font(self.config.feature_font_path)
        try:
            source_state, protected_glyphs = self._prepare_source_build_state(
                feature_font
            )
            stats = self._merge_master_paths(feature_font, source_state.master_paths)
            self._log_build_stats("Regular", stats)
            finalize_variable_font(
                feature_font,
                set(stats.added_glyphs),
                protected_glyphs,
                "Regular",
                self.config,
                self.font_config,
            )
            logger.debug(
                "Regular CJK base font: glyphs=%s, unicodes=%s",
                len(feature_font.getGlyphOrder()),
                len(get_cmap_codepoints(feature_font)),
            )
            logger.debug("Regular CJK variable font ready")
            return feature_font, source_state
        except Exception:
            feature_font.close()
            raise

    def _build_italic_variable_font(self, source_state: SourceBuildState) -> TTFont:
        logger.info("Build italic CJK variable font")
        feature_font = load_feature_variable_font(self.config.feature_font_path)
        try:
            protected_glyphs = set(get_unicode_cmap(feature_font).values())
            feature_axis = weight_axis(feature_font)
            if feature_axis is None:
                raise ValueError("Feature font is missing wght axis")
            feature_masters = {
                100: {"wght": float(feature_axis.minValue)},
                400: {"wght": float(feature_axis.defaultValue)},
                800: {"wght": float(feature_axis.maxValue)},
            }
            feature_master_paths = instantiate_italic_masters_from_vf(
                self.config.feature_font_path,
                self.config.temp_dir / "feature-italic-masters",
                feature_masters,
                self._require_process_pool(),
                self.config.transform.italic_angle,
                self.config.locale_name.lower(),
            )
            logger.debug("Italic feature masters ready")
            italic_font = make_italic_variable_font(
                feature_font,
                self.config.transform.italic_angle,
                self.config.temp_dir,
                self._require_process_pool(),
                feature_master_paths,
                masters_are_italic=True,
            )
        except Exception:
            feature_font.close()
            raise

        try:
            italic_master_paths = self._build_source_italic_master_paths(
                source_state.master_paths
            )
            logger.debug("Italic source masters ready")
            stats = self._merge_master_paths(italic_font, italic_master_paths)
            self._log_build_stats("Italic", stats)
            finalize_variable_font(
                italic_font,
                set(stats.added_glyphs),
                protected_glyphs,
                "Italic",
                self.config,
                self.font_config,
                is_italic=True,
            )
            logger.debug(
                "Italic CJK base font: glyphs=%s, unicodes=%s",
                len(italic_font.getGlyphOrder()),
                len(get_cmap_codepoints(italic_font)),
            )
            logger.debug("Italic CJK variable font ready")
            return italic_font
        except Exception:
            italic_font.close()
            raise

    def _build_source_italic_master_paths(
        self,
        source_master_paths: tuple[Path, Path, Path],
    ) -> tuple[Path, Path, Path]:
        italic_master_dir = self.config.temp_dir / "source-italic-masters"
        italic_master_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Create italic source masters: output_dir=%s", italic_master_dir)
        italic_master_paths = (
            italic_master_dir / "source-italic-min-master.ttf",
            italic_master_dir / "source-italic-regular-master.ttf",
            italic_master_dir / "source-italic-max-master.ttf",
        )
        futures = []
        for source_path, output_path in zip(
            source_master_paths, italic_master_paths, strict=False
        ):
            futures.append(
                self._require_process_pool().submit(
                    make_italic_master_file,
                    str(source_path),
                    str(output_path),
                    self.config.transform.italic_angle,
                )
            )
        for future in futures:
            future.result()
        logger.debug("Italic source masters created: output_dir=%s", italic_master_dir)
        return italic_master_paths

    def _merge_master_paths(
        self,
        base_font: TTFont,
        master_paths: tuple[Path, Path, Path],
    ) -> BuildStats:
        masters = [
            load_font(master_path, decompile=True) for master_path in master_paths
        ]
        try:
            added, added_codepoints = merge_masters_into_vf(
                base_font,
                masters[0],
                masters[1],
                masters[2],
            )
            return BuildStats(
                added_glyphs=tuple(added),
                added_codepoints=added_codepoints,
            )
        finally:
            for master in masters:
                master.close()

    def _log_build_stats(self, label: str, stats: BuildStats) -> None:
        logger.debug(
            "%s CJK merge results: glyphs_added=%s, unicodes_added=%s",
            label,
            len(stats.added_glyphs),
            stats.added_codepoints,
        )

    def _write_variable_outputs(
        self, regular_font: TTFont, italic_font: TTFont
    ) -> None:
        save_font_atomic(regular_font, self.regular_output)
        logger.info("Saved CJK variable font to %s", self.regular_output)
        save_font_atomic(italic_font, self.italic_output)
        logger.info("Saved CJK variable font to %s", self.italic_output)

    def _write_variable_artifacts(self) -> None:
        write_variable_hash(self.config)
        archive_path = self.config.output.dir / self.config.output.variable_archive_name
        variable_names = {
            self.config.output.regular_variable,
            self.config.output.italic_variable,
        }
        logger.debug("Archive CJK variable fonts: path=%s", archive_path)
        archive(
            str(self.config.output.dir),
            str(archive_path),
            lambda path: Path(path).name in variable_names,
        )
        logger.debug("CJK variable font archive ready: path=%s", archive_path)

    def _build_static_fonts(
        self,
        var_font_names: Iterable[str],
        required_styles: Collection[str] | None = None,
    ) -> Path:
        static_dir = self.static_dir
        makedirs(static_dir, exist_ok=True)
        var_font_names = tuple(var_font_names)
        futures = []
        feature_font = load_feature_variable_font(self.config.feature_font_path)
        try:
            feature_axis = weight_axis(feature_font)
            if feature_axis is None:
                raise ValueError("Feature font is missing wght axis")
            feature_instances = feature_weight_instances(feature_font)
            logger.debug(
                "Generate CJK static fonts: variable_fonts=%s, instances=%s, output_dir=%s",
                len(var_font_names),
                len(var_font_names) * len(feature_instances),
                static_dir,
            )
            for font_name in var_font_names:
                is_italic = "Italic" in font_name
                input_path = self.config.output.dir / font_name
                var_font = load_font(input_path, decompile=True)
                try:
                    var_axis = weight_axis(var_font)
                    if var_axis is None:
                        raise ValueError(
                            "Both variable and feature fonts must contain wght axis"
                        )
                    mapped_instances = tuple(
                        CJKWeightInstance(
                            instance.name,
                            map_weight_coordinate(
                                instance.coordinate,
                                float(feature_axis.minValue),
                                float(feature_axis.defaultValue),
                                float(feature_axis.maxValue),
                                float(var_axis.minValue),
                                float(var_axis.defaultValue),
                                float(var_axis.maxValue),
                            ),
                        )
                        for instance in feature_instances
                    )
                finally:
                    var_font.close()

                for instance in mapped_instances:
                    style_name = f"{instance.name}{'Italic' if is_italic else ''}"
                    style_name = style_name.replace("RegularItalic", "Italic")
                    if (
                        required_styles is not None
                        and style_name not in required_styles
                    ):
                        continue
                    output_name = (
                        f"{self.config.naming.static_file_prefix}-{style_name}.ttf"
                    )
                    job = StaticInstanceJob(
                        input_path=str(input_path),
                        output_path=str(static_dir / output_name),
                        coordinate=instance.coordinate,
                        name=instance.name,
                        is_italic=is_italic,
                        config=self.config,
                        font_config=self.font_config,
                    )
                    futures.append(
                        self._require_process_pool().submit(
                            instantiate_static_font_job,
                            job,
                        )
                    )
        finally:
            feature_font.close()

        for future in futures:
            future.result()
        if required_styles is not None:
            static_prefix = f"{self.config.naming.static_file_prefix}-"
            for static_path in static_dir.glob(f"{static_prefix}*.ttf"):
                style_name = static_path.stem.removeprefix(static_prefix)
                if style_name not in required_styles:
                    static_path.unlink()
        logger.debug("CJK static fonts ready: output_dir=%s", static_dir)
        return static_dir

    def _write_static_artifacts(self, static_dir: Path) -> None:
        write_static_hash(self.config, static_dir)
        archive_path = self.config.output.dir / self.config.output.archive_name
        logger.debug("Archive CJK static fonts: path=%s", archive_path)
        archive(
            str(static_dir),
            str(archive_path),
            lambda path: path.endswith(".ttf"),
        )
        logger.debug("CJK static font archive ready: path=%s", archive_path)


def instantiate_cjk_static_from_variable(
    config: CJKBuildConfig,
    font_config: FontNameConfig,
    executor: Executor | None = None,
    required_styles: Collection[str] | None = None,
) -> Path:
    """Instantiate a static base from already-generated CJK variable fonts."""
    owns_executor = executor is None
    process_pool = executor or create_font_executor(
        getattr(font_config, "pool_size", 4)
    )
    builder = CJKBuilder(config, font_config, process_pool)
    try:
        static_dir = builder._build_static_fonts(
            (config.output.regular_variable, config.output.italic_variable),
            required_styles,
        )
        write_static_hash(config, static_dir)
        return static_dir
    finally:
        if owns_executor:
            process_pool.shutdown(wait=True, cancel_futures=True)


def build_cjk_fonts(
    build_config: CJKBuildConfig,
    name_config: FontNameConfig,
    vf_only: bool = False,
    executor: Executor | None = None,
    github_mirror: str = "github.com",
) -> None:
    """Build regular, italic, and optionally static CJK fonts."""
    CJKBuilder(build_config, name_config, executor, github_mirror).build(
        vf_only=vf_only
    )
