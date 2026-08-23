#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import time
from copy import deepcopy
from dataclasses import dataclass
from os import environ, makedirs
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from scripts.config.resolver import BuildConfigResolver
from scripts.config.runtime import BuildRuntimeContext
from scripts.font_ops.metrics import read_font_vertical_metric
from scripts.pipeline.artifacts import (
    IGNORED_OUTPUT_DIRS,
    cleanup_unselected_base_formats,
    ensure_base_output_dirs,
    expected_static_font_paths,
    expected_static_styles,
    merged_variable_name,
    static_output_dir,
    variable_output_dir,
)
from scripts.pipeline.base_fonts import build_base_fonts, build_woff2_fonts
from scripts.pipeline.cache import StageCacheTracker
from scripts.pipeline.cjk_outputs import (
    build_cjk_extended_static_outputs,
    build_cjk_extended_variable_outputs,
)
from scripts.pipeline.fontmake import (
    build_static_fonts,
    build_variable_fonts,
    compile_fontmake_formats,
    prepare_fontmake_sources,
)
from scripts.pipeline.nerd_fonts import (
    build_nerd_font_variable_fonts,
    build_nerd_fonts,
    should_use_font_patcher,
)
from scripts.utils.errors import BuildDependencyError
from scripts.utils.files import archive_fonts, join_path, write_json
from scripts.utils.logging import (
    ENVIRONMENT_VARIABLE,
    TaskName,
    configure_logging,
    log_task,
    log_task_complete,
    logger,
    set_log_task,
)
from scripts.utils.process import (
    SynchronousExecutor,
    create_process_executor,
    is_ci,
)
from scripts.utils.version import version_tag

if TYPE_CHECKING:
    from concurrent.futures import Executor

    from scripts.config.base import ResolvedCJKBuildEntry, ResolvedConfig


@dataclass(frozen=True)
class BuildPlan:
    """Content stages and output policy derived from resolved configuration."""

    target_styles: list[str] | None
    required_base_formats: tuple[Literal["variable", "ttf", "otf"], ...]
    build_woff2: bool
    build_nerd_font: bool
    build_nerd_font_variable: bool
    cjk_mode: Literal["variable", "static"] | None
    cleanup_base_static: bool
    archive: bool

    @classmethod
    def from_config(cls, config: ResolvedConfig) -> BuildPlan:
        if config.least_styles:
            target_styles = ["Regular", "Bold", "Italic", "BoldItalic"]
        elif config.debug:
            target_styles = ["Regular", "Italic"]
        else:
            target_styles = None

        base_formats: list[Literal["variable", "ttf", "otf"]] = ["variable"]
        if (
            config.wants_format("ttf")
            or config.wants_format("woff2")
            or config.needs_hinted_ttf()
            or config.needs_nerd_font_static_base()
        ):
            base_formats.append("ttf")
        if config.wants_format("otf") and not config.debug:
            base_formats.append("otf")

        cjk_mode: Literal["variable", "static"] | None = None
        if config.get_selected_cjk_entries():
            cjk_mode = config.cjk_output_format

        return cls(
            target_styles=target_styles,
            required_base_formats=tuple(base_formats),
            build_woff2=config.wants_format("woff2") and not config.debug,
            build_nerd_font=config.nerd_font.enable and not config.nerd_font.variable,
            build_nerd_font_variable=(
                config.nerd_font.enable and config.nerd_font.variable
            ),
            cjk_mode=cjk_mode,
            cleanup_base_static=not config.wants_format("ttf"),
            archive=config.archive,
        )


class MapleBuildPipeline:
    """Coordinate the Maple Mono build pipeline without crossing process boundaries."""

    def __init__(
        self,
        font_config: ResolvedConfig,
        runtime_context: BuildRuntimeContext,
    ) -> None:
        self.font_config = font_config
        self.runtime_context = runtime_context
        self.should_use_cache = font_config.cache
        self.plan = BuildPlan.from_config(font_config)
        self.target_styles = self.plan.target_styles
        self.start_time = 0.0
        self._cache_tracker = StageCacheTracker(font_config, runtime_context, self.plan)

    def build(self) -> None:
        self.start_build_timer()
        self.prepare_output_root()
        self.write_build_config()

        process_executor = (
            SynchronousExecutor()
            if self.font_config.pool_size <= 1
            else create_process_executor(
                max_workers=self.font_config.pool_size,
                fallback_to_threads=True,
            )
        )
        with process_executor:
            base_formats = self.base_formats_to_build()
            self._build_base_outputs(base_formats, process_executor)
            self._build_derived_outputs(base_formats, process_executor)
            self._build_cjk_outputs(process_executor)

        if self.plan.cleanup_base_static:
            cleanup_unselected_base_formats(self.font_config, self.runtime_context)

        self.write_build_record()

        if self.plan.archive:
            self.archive_outputs()

        self.finish_build()

    def _build_base_outputs(
        self,
        base_formats: tuple[Literal["variable", "ttf", "otf"], ...],
        process_executor: Executor,
    ) -> None:
        if not base_formats:
            self.reuse_base_output_cache()
            return

        fontmake_context = prepare_fontmake_sources(
            self.font_config,
            self.runtime_context,
            process_executor,
        )
        try:
            format_labels = ", ".join(
                "Variable" if item == "variable" else item.upper()
                for item in base_formats
            )
            started_at = log_task(TaskName.FONTMAKE, "Build %s", format_labels)
            compile_fontmake_formats(
                fontmake_context,
                base_formats,
                process_executor,
                target_styles=self.target_styles,
            )
            output_counts: list[tuple[str, int]] = []
            if "variable" in base_formats:
                variable_paths = build_variable_fonts(
                    self.font_config,
                    self.runtime_context,
                    fontmake_context,
                    process_executor,
                )
                self._mark_stage_rebuilt(
                    "variable",
                    self._base_stage_expected_paths("variable"),
                )
                output_counts.append(("Variable", len(variable_paths or ())))
            for build_format in ("ttf", "otf"):
                if build_format in base_formats:
                    static_paths = build_static_fonts(
                        self.font_config,
                        self.runtime_context,
                        fontmake_context,
                        build_format,
                        self.target_styles,
                        process_executor,
                    )
                    self._mark_stage_rebuilt(
                        build_format,
                        self._base_stage_expected_paths(build_format),
                    )
                    output_counts.append(
                        (build_format.upper(), len(static_paths or ()))
                    )
            summary = ", ".join(f"{label}: {count}" for label, count in output_counts)
            log_task_complete(started_at, summary)
        finally:
            shutil.rmtree(fontmake_context.temp_path, ignore_errors=True)

    def _build_derived_outputs(
        self,
        base_formats: tuple[Literal["variable", "ttf", "otf"], ...],
        process_executor: Executor,
    ) -> None:
        ttf_paths = self._base_stage_expected_paths("ttf")
        hinted_paths = self._base_stage_expected_paths("ttf-autohint")
        if self.should_build_hinted_ttf(base_formats):
            self._invalidate_recorded_stage("ttf-autohint")
            hinted_paths = build_base_fonts(
                self.font_config,
                self.runtime_context,
                ttf_paths,
                process_executor,
            )
            self._mark_stage_rebuilt(
                "ttf-autohint",
                self._base_stage_expected_paths("ttf-autohint"),
            )
        if self.should_build_woff2_outputs(base_formats):
            self._invalidate_recorded_stage("woff2")
            build_woff2_fonts(
                ttf_paths,
                self.runtime_context,
                process_executor,
            )
            self._mark_stage_rebuilt(
                "woff2",
                self._base_stage_expected_paths("woff2"),
            )
        elif self.font_config.wants_format("woff2") and self.font_config.debug:
            set_log_task("woff2")
            logger.debug("Skip WOFF2 conversion for a debug build")

        if self.plan.build_nerd_font:
            if self._validate_recorded_stage("nf"):
                logger.info("Reuse cached NF outputs")
                self.runtime_context.is_nf_built = True
            else:
                self._invalidate_recorded_stage("nf")
                nf_inputs = hinted_paths if self.font_config.use_hinted else ttf_paths
                build_nerd_fonts(
                    self.font_config,
                    self.runtime_context,
                    nf_inputs,
                    process_executor,
                )
                self._mark_stage_rebuilt("nf", self._nf_stage_expected_paths())
        else:
            set_log_task("nerd-font")
            logger.debug("Skip Nerd Font outputs because the stage is disabled")

        if self.plan.build_nerd_font_variable:
            if self._validate_recorded_stage("nf-variable"):
                logger.info("Reuse cached variable NF outputs")
            else:
                self._invalidate_recorded_stage("nf-variable")
                variable_paths = self._base_stage_expected_paths("variable")
                static_source_paths = (
                    hinted_paths if self.font_config.use_hinted else ttf_paths
                )
                build_nerd_font_variable_fonts(
                    self.font_config,
                    self.runtime_context,
                    variable_paths,
                    static_source_paths
                    if should_use_font_patcher(self.font_config)
                    else None,
                    process_executor,
                )
                self._mark_stage_rebuilt(
                    "nf-variable",
                    self._nf_variable_stage_expected_paths(),
                )
            self.runtime_context.is_nf_built = True
        else:
            set_log_task("nerd-font")
            logger.debug(
                "Skip variable Nerd Font outputs because the stage is disabled"
            )

    def _cjk_stage_targets(
        self,
    ) -> list[tuple[str, ResolvedCJKBuildEntry, str]]:
        if not self.plan.cjk_mode:
            return []

        targets: list[tuple[str, ResolvedCJKBuildEntry, str]] = []
        for entry in self.font_config.get_selected_cjk_entries():
            if self.plan.cjk_mode == "variable":
                include_nf = (
                    self.font_config.nerd_font.enable
                    and entry.common_options.with_nerd_font
                )
            else:
                include_nf = (
                    self.runtime_context.is_nf_built
                    and entry.common_options.with_nerd_font
                )
            output_locales: list[str] = []
            if include_nf:
                output_locales.append(
                    self.font_config.get_nf_variant().cjk_directory_name(
                        entry.locale_name
                    )
                )
            if not include_nf or self.font_config.use_cjk_both:
                output_locales.append(entry.locale_name)
            for output_locale in output_locales:
                stage = f"{output_locale.lower()}-{self.plan.cjk_mode}"
                targets.append((stage, entry, output_locale))
        return targets

    def _cjk_stage_target(
        self,
        stage: str,
    ) -> tuple[ResolvedCJKBuildEntry, str]:
        for target_stage, entry, output_locale in self._cjk_stage_targets():
            if target_stage == stage:
                return entry, output_locale
        raise ValueError(f"Unknown CJK stage: {stage}")

    def _cjk_stage_expected_paths(self, output_locale: str) -> list[Path]:
        nf_directory_name = self.font_config.get_nf_variant().directory_name
        nf_prefix = f"{nf_directory_name}-"
        is_nf_output = output_locale.startswith(nf_prefix)
        locale_name = output_locale.removeprefix(nf_prefix)
        if self.plan.cjk_mode == "variable":
            directory = variable_output_dir(
                self.runtime_context.output_dir,
                output_locale,
            )
            prefix = f"{self.font_config.family_name_compact}-{locale_name}"
            if is_nf_output:
                prefix = (
                    f"{self.font_config.family_name_compact}-"
                    f"{self.font_config.get_nf_variant().symbol}-{locale_name}"
                )
            return [
                directory / merged_variable_name(prefix, italic)
                for italic in (False, True)
            ]
        directory = static_output_dir(self.runtime_context.output_dir, output_locale)
        prefix = f"{self.font_config.family_name_compact}-{locale_name}"
        if is_nf_output:
            prefix = (
                f"{self.font_config.family_name_compact}-"
                f"{self.font_config.get_nf_variant().symbol}-{locale_name}"
            )
        return [
            directory / f"{prefix}-{style}.ttf"
            for style in expected_static_styles(self.target_styles)
        ]

    def _cjk_stage_paths(self, output_locale: str) -> list[Path]:
        return [
            path
            for path in self._cjk_stage_expected_paths(output_locale)
            if path.is_file()
        ]

    def _build_cjk_outputs(self, process_executor: Executor) -> None:
        if self.plan.cjk_mode:
            built_any = False
            stage_groups: list[tuple[ResolvedCJKBuildEntry, list[tuple[str, str]]]] = []
            for stage, entry, output_locale in self._cjk_stage_targets():
                for grouped_entry, profiles in stage_groups:
                    if grouped_entry is entry:
                        profiles.append((stage, output_locale))
                        break
                else:
                    stage_groups.append((entry, [(stage, output_locale)]))

            for entry, profiles in stage_groups:
                output_locales = [output_locale for _stage, output_locale in profiles]
                task_message = (
                    "Build CJK variable outputs (%s)"
                    if self.plan.cjk_mode == "variable"
                    else "Build CJK static outputs (%s)"
                )
                started_at = log_task(
                    TaskName.CJK,
                    task_message,
                    ", ".join(output_locales),
                    task_label=entry.locale_name.lower(),
                    force_separator=True,
                )
                missing_profiles: list[tuple[str, str]] = []
                reused_count = 0
                for stage, output_locale in profiles:
                    if self._validate_recorded_stage(stage):
                        logger.info(
                            "Reuse cached CJK %s outputs (%s)",
                            self.plan.cjk_mode,
                            output_locale,
                        )
                        reused_count += len(self._cjk_stage_paths(output_locale))
                        built_any = True
                        continue
                    self._invalidate_recorded_stage(stage)
                    missing_profiles.append((stage, output_locale))

                if not missing_profiles:
                    log_task_complete(started_at, f"{reused_count} fonts")
                    continue

                missing_locales = [
                    output_locale for _stage, output_locale in missing_profiles
                ]
                scoped_config = deepcopy(self.font_config)
                scoped_config.cjk.entries = [entry]
                output_locale_set = set(missing_locales)
                if self.plan.cjk_mode == "variable":
                    build_cjk_extended_variable_outputs(
                        scoped_config,
                        self.runtime_context,
                        process_executor,
                        output_locale_set,
                        started_at=started_at,
                    )
                else:
                    build_cjk_extended_static_outputs(
                        scoped_config,
                        self.runtime_context,
                        self.target_styles,
                        process_executor,
                        output_locale_set,
                        started_at=started_at,
                    )

                output_error: FileNotFoundError | None = None
                for stage, output_locale in missing_profiles:
                    try:
                        self._mark_stage_rebuilt(
                            stage,
                            self._cjk_stage_expected_paths(output_locale),
                        )
                    except FileNotFoundError as error:  # noqa: PERF203
                        if output_error is None:
                            output_error = error
                if output_error is not None:
                    raise output_error
                built_any = True
            self.runtime_context.is_cjk_built = built_any
        else:
            if is_ci():
                set_log_task("cjk")
                logger.debug("Skip CJK outputs because no locale is selected")
            else:
                log_task(
                    TaskName.CJK,
                    "Skip CJK outputs: reason=no CJK locale selected",
                )

    def prepare_output_root(self) -> None:
        if not self.should_use_cache:
            logger.info("Cache disabled: rebuild requested")
            shutil.rmtree(self.runtime_context.output_dir, ignore_errors=True)
            shutil.rmtree(self.runtime_context.output_woff2, ignore_errors=True)
        else:
            self._cache_matches_build()
        ensure_base_output_dirs(self.runtime_context)

    def start_build_timer(self) -> None:
        self.start_time = time.time()
        cjk_entries = self.font_config.get_selected_cjk_entries()
        cjk_summary = "off"
        if cjk_entries:
            locales = ", ".join(entry.display_name for entry in cjk_entries)
            cjk_summary = f"{self.font_config.cjk_output_format} ({locales})"
        options = [
            label
            for enabled, label in (
                (self.font_config.use_hinted, "hinting"),
                (self.font_config.enable_ligature, "ligatures"),
            )
            if enabled
        ]
        details = [
            f"  Formats: {', '.join(item.upper() for item in self.font_config.formats)}",
            f"  Styles: {', '.join(self.target_styles) if self.target_styles else 'all'}",
            f"  Options: {', '.join(options) or 'none'}",
            f"  Nerd Font: {'on' if self.font_config.nerd_font.enable else 'off'}",
            f"  CJK: {cjk_summary}",
            f"  Cache: {'on' if self.font_config.cache else 'off'}",
        ]
        if self.font_config.archive:
            details.append("  Archive: on")
        if self.font_config.width != "default":
            details.append(
                "  Width: "
                f"{self.font_config.width} "
                f"({self.font_config.glyph_width} -> "
                f"{self.font_config.get_target_width()}, "
                f"suffix {self.font_config.get_width_name()})",
            )
        if self.font_config.line_height != 1:
            details.append(f"  Line height: {self.font_config.line_height:g}")
        version = self.font_config.version_str.removeprefix("Version ")
        log_task(
            TaskName.BUILD,
            "%s %s\n%s",
            self.font_config.family_name,
            version,
            "\n".join(details),
        )

    def base_formats_to_build(
        self,
    ) -> tuple[Literal["variable", "ttf", "otf"], ...]:
        """Return only the base formats that are missing from the cache."""
        if not self.should_use_cache:
            return self.plan.required_base_formats

        missing_formats: list[Literal["variable", "ttf", "otf"]] = []
        for build_format in self.plan.required_base_formats:
            if self._has_cached_base_format(build_format):
                self._log_cache_reuse(build_format)
            else:
                self._invalidate_recorded_stage(build_format)
                missing_formats.append(build_format)
        return tuple(missing_formats)

    def _cache_matches_build(self) -> bool:
        return self._cache_tracker.cache_matches_build()

    def _current_build_identity(self) -> dict[str, object]:
        return self._cache_tracker.current_build_identity()

    def _log_cache_reuse(
        self,
        build_format: Literal["variable", "ttf", "otf"],
    ) -> None:
        self._cache_tracker.log_cache_reuse(build_format)

    def _has_cached_base_format(
        self,
        build_format: Literal["variable", "ttf", "otf"],
    ) -> bool:
        return self._validate_cached_stage(
            build_format,
            self._base_stage_expected_paths(build_format),
        )

    def _base_stage_expected_paths(self, stage: str) -> list[Path]:
        if stage == "variable":
            output_dir = Path(self.runtime_context.output_variable)
            return [
                output_dir / f"{self.font_config.family_name_compact}[wght].ttf",
                output_dir / f"{self.font_config.family_name_compact}-Italic[wght].ttf",
            ]

        if stage in {"ttf", "otf"}:
            output_dir = Path(
                self.runtime_context.output_ttf
                if stage == "ttf"
                else self.runtime_context.output_otf
            )
            return expected_static_font_paths(
                output_dir,
                self.font_config.family_name_compact,
                self.target_styles,
                f".{stage}",
            )

        if stage == "ttf-autohint":
            return expected_static_font_paths(
                self.runtime_context.output_ttf_hinted,
                self.font_config.family_name_compact,
                self.target_styles,
            )

        if stage == "woff2":
            return expected_static_font_paths(
                self.runtime_context.output_woff2,
                self.font_config.family_name_compact,
                self.target_styles,
                ".woff2",
            )

        raise ValueError(f"Unknown base stage: {stage}")

    def _validate_cached_stage(
        self,
        stage: str,
        paths: list[Path],
    ) -> bool:
        return self._cache_tracker.validate_cached_stage(stage, paths)

    def _validate_recorded_stage(self, stage: str) -> bool:
        return self._cache_tracker.validate_recorded_stage(
            stage,
            self._cjk_stage_targets(),
            self._nf_stage_expected_paths(),
            self._nf_variable_stage_expected_paths(),
            self._cjk_stage_expected_paths,
        )

    def _nf_stage_expected_paths(self) -> list[Path]:
        upstream = "ttf-autohint" if self.font_config.use_hinted else "ttf"
        symbol = self.font_config.get_nf_variant().symbol
        return [
            Path(self.runtime_context.output_nf)
            / (
                f"{self.font_config.family_name_compact}-{symbol}-"
                f"{path.stem.rsplit('-', 1)[-1]}.ttf"
            )
            for path in self._base_stage_expected_paths(upstream)
        ]

    def _nf_variable_stage_expected_paths(self) -> list[Path]:
        output_dir = Path(self.runtime_context.output_nf_variable)
        symbol = self.font_config.get_nf_variant().symbol
        prefix = f"{self.font_config.family_name_compact}-{symbol}"
        return [
            output_dir / f"{prefix}[wght].ttf",
            output_dir / f"{prefix}-Italic[wght].ttf",
        ]

    def _invalidate_recorded_stage(self, stage: str) -> None:
        self._cache_tracker.invalidate_recorded_stage(stage)

    def _mark_stage_rebuilt(self, stage: str, paths: list[Path]) -> None:
        self._cache_tracker.mark_stage_rebuilt(stage, paths)

    def _stage_cache_identity(self, stage: str) -> str:
        return self._cache_tracker.stage_cache_identity(
            stage, self._cjk_stage_targets()
        )

    def should_build_hinted_ttf(
        self,
        base_formats: tuple[Literal["variable", "ttf", "otf"], ...],
    ) -> bool:
        if not self.font_config.needs_hinted_ttf():
            return False
        if "ttf" in base_formats:
            return True
        if not self.should_use_cache:
            return True
        if self._has_cached_hinted_ttf():
            logger.info("Reuse cached TTF-AutoHint outputs")
            logger.debug(
                "Cached TTF-AutoHint output path: %s",
                self.runtime_context.output_ttf_hinted,
            )
            return False
        return True

    def _has_cached_hinted_ttf(self) -> bool:
        return self._validate_cached_stage(
            "ttf-autohint",
            self._base_stage_expected_paths("ttf-autohint"),
        )

    def reuse_base_output_cache(self) -> None:
        regular_variable_path = Path(self.runtime_context.output_variable) / (
            f"{self.font_config.family_name_compact}[wght].ttf"
        )
        if not regular_variable_path.exists():
            raise FileNotFoundError(
                f"Cached variable font not found: {regular_variable_path}"
            )
        self.runtime_context.resolved_vertical_metric = read_font_vertical_metric(
            regular_variable_path
        )
        logger.debug("Reuse cached base font outputs")

    def should_build_woff2_outputs(
        self,
        base_formats: tuple[Literal["variable", "ttf", "otf"], ...] = (),
    ) -> bool:
        if not self.font_config.wants_format("woff2") or self.font_config.debug:
            return False
        if "ttf" in base_formats or not self.should_use_cache:
            return True
        expected = self._base_stage_expected_paths("woff2")
        if not self._validate_cached_stage("woff2", expected):
            return True
        logger.info("Reuse cached WOFF2 outputs")
        logger.debug("Cached WOFF2 output path: %s", self.runtime_context.output_woff2)
        return False

    def write_build_config(self) -> None:
        write_json(
            Path(self.runtime_context.output_dir) / "build-config.json",
            self.font_config.to_build_record(),
            indent=4,
            atomic=True,
        )

    def write_build_record(self) -> None:
        """Write the public config and the completed cache record."""
        self.write_build_config()
        self.write_cache_record()

    def _requested_cache_stages(self) -> list[str]:
        stages = ["variable"]
        if self.font_config.wants_format("ttf"):
            stages.append("ttf")
            if self.font_config.needs_hinted_ttf():
                stages.append("ttf-autohint")
        if self.font_config.wants_format("otf") and not self.font_config.debug:
            stages.append("otf")
        if self.plan.build_woff2:
            stages.append("woff2")
        if self.plan.build_nerd_font:
            stages.append("nf")
        if self.plan.build_nerd_font_variable:
            stages.append("nf-variable")
        stages.extend(stage for stage, _entry, _locale in self._cjk_stage_targets())
        return stages

    def write_cache_record(self) -> None:
        self._cache_tracker.write_cache_record(
            self._requested_cache_stages(),
            self._cjk_stage_targets(),
        )

    def archive_outputs(self) -> None:
        started_at = log_task(TaskName.ARCHIVE, "Archive build outputs")
        archive_dir_name = "archive"
        archive_dir = join_path(self.runtime_context.output_dir, archive_dir_name)
        makedirs(archive_dir, exist_ok=True)

        archive_count = 0
        output_root = Path(self.runtime_context.output_dir)
        for output_path in sorted(output_root.iterdir(), key=lambda path: path.name):
            file_name = output_path.name
            if (
                not output_path.is_dir()
                or file_name == archive_dir_name
                or file_name in IGNORED_OUTPUT_DIRS
            ):
                continue

            suffix = ""
            cjk_locale_names = {
                entry.locale_name
                for entry in self.font_config.get_selected_cjk_entries()
            }
            cjk_archive_dirs = {locale_name.upper() for locale_name in cjk_locale_names}
            nf_directory_name = self.font_config.get_nf_variant().directory_name
            nf_cjk_archive_dirs = {
                f"{nf_directory_name}-{locale_name}".upper()
                for locale_name in cjk_locale_names
            }
            if (
                file_name
                in {nf_directory_name, *cjk_archive_dirs, *nf_cjk_archive_dirs}
                and not self.font_config.use_hinted
            ):
                suffix = "-unhinted"

            _, zip_file_name_without_ext = archive_fonts(
                family_name_compact=self.font_config.family_name_compact,
                suffix=suffix,
                source_file_or_dir_path=output_path,
                build_config_path=join_path(
                    self.runtime_context.output_dir,
                    "build-config.json",
                ),
                target_parent_dir_path=archive_dir,
            )
            archive_count += 1
            logger.info(
                "Saved archive to %s",
                join_path(archive_dir, f"{zip_file_name_without_ext}.zip"),
            )
        log_task_complete(started_at, f"{archive_count} archives")

    def finish_build(self) -> None:
        freeze_str = (
            self.font_config.freeze_config_str
            if self.font_config.freeze_config_str != ""
            else "default config"
        )
        time_diff = time.time() - self.start_time
        output_root = Path(self.runtime_context.output_dir).resolve()
        cjk_locales = (
            ", ".join(
                entry.locale_name
                for entry in self.font_config.get_selected_cjk_entries()
            )
            or "none"
        )
        log_task(
            TaskName.BUILD,
            "Build completed, took %.2fs:\n"
            "  Directory: %s\n"
            "  Family: %s\n"
            "  Width: %s units\n"
            "  Feature configuration: %s\n"
            "  Nerd Font: %s\n"
            "  CJK: %s (%s)",
            time_diff,
            output_root,
            self.font_config.family_name,
            self.font_config.get_target_width(),
            freeze_str,
            "built" if self.runtime_context.is_nf_built else "not built",
            cjk_locales,
            "built" if self.runtime_context.is_cjk_built else "not built",
        )


def main(args: list[str] | None = None, version: str | None = None) -> None:
    from scripts.config.cli import parse_args

    resolved_version = version or version_tag()
    parsed_args = parse_args(args, version=resolved_version)
    use_debug_log_default = parsed_args.debug and ENVIRONMENT_VARIABLE not in environ
    if use_debug_log_default:
        environ[ENVIRONMENT_VARIABLE] = "DEBUG"
    try:
        configure_logging()
        resolver = BuildConfigResolver(version_tag=resolved_version)
        font_config = resolver.resolve(parsed_args)
        runtime_context = BuildRuntimeContext.from_config(font_config)

        if parsed_args.dry:
            if is_ci():
                print(json.dumps(font_config.to_dict(), indent=4))
            else:
                print("resolved_config:", json.dumps(font_config.to_dict(), indent=4))
                print(
                    "runtime_context:",
                    json.dumps(runtime_context.to_dict(font_config), indent=4),
                )
            return

        MapleBuildPipeline(font_config, runtime_context).build()
    except BuildDependencyError as error:
        logger.error("Build failed: %s", error)
        raise SystemExit(1) from error
    finally:
        if use_debug_log_default:
            del environ[ENVIRONMENT_VARIABLE]
