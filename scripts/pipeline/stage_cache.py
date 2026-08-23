from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from scripts.cjk.resolver import serialize_cjk_build_config
from scripts.pipeline.artifacts import base_cache_identity
from scripts.pipeline.cache import (
    CACHE_SCHEMA,
    output_snapshot,
    read_cache_record,
    relative_cache_path,
    stage_identity,
    validated_stage_record,
)
from scripts.pipeline.cache import (
    write_cache_record as persist_cache_record,
)
from scripts.pipeline.nerd_fonts import should_use_font_patcher
from scripts.utils.logging import TaskName, log_task, logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from scripts.config.base import ResolvedCJKBuildEntry, ResolvedConfig
    from scripts.config.runtime import BuildRuntimeContext
    from scripts.pipeline.orchestrator import BuildPlan

_CACHE_STAGE_TASKS = {
    "variable": TaskName.VARIABLE,
    "ttf": TaskName.TTF,
    "otf": TaskName.OTF,
    "ttf-autohint": TaskName.TTF_AUTOHINT,
    "woff2": TaskName.WOFF2,
    "nf": TaskName.NERD_FONT,
    "nf-variable": TaskName.NERD_FONT,
}


class StageCacheTracker:
    """Manages cache validation, stage identities, and cache persistence."""

    def __init__(
        self,
        font_config: ResolvedConfig,
        runtime_context: BuildRuntimeContext,
        plan: BuildPlan,
    ) -> None:
        self.font_config = font_config
        self.runtime_context = runtime_context
        self.plan = plan
        self.should_use_cache = font_config.cache
        self.target_styles = plan.target_styles
        self._cache_identity_checked = False
        self._cache_identity_valid = True
        self._cache_reuse_logged: set[str] = set()
        self._cache_record: dict[str, Any] | None = None
        self._validated_stage_records: dict[str, dict[str, object]] = {}
        self._rebuilt_stage_paths: dict[str, list[Path]] = {}
        self._build_identity: dict[str, object] | None = None

    def cache_matches_build(self) -> bool:
        if not self.should_use_cache or self._cache_identity_checked:
            return self._cache_identity_valid

        self._cache_identity_checked = True
        self._cache_record = read_cache_record(Path(self.runtime_context.output_root))
        if not self._cache_record:
            self._cache_identity_valid = False
        return self._cache_identity_valid

    def current_build_identity(self) -> dict[str, object]:
        if self._build_identity is None:
            self._build_identity = base_cache_identity(
                self.font_config,
                self.runtime_context,
            )
        return self._build_identity

    def log_cache_reuse(
        self,
        build_format: Literal["variable", "ttf", "otf"],
    ) -> None:
        if build_format in self._cache_reuse_logged:
            return
        self._cache_reuse_logged.add(build_format)
        output_dir = {
            "variable": self.runtime_context.output_variable,
            "ttf": self.runtime_context.output_ttf,
            "otf": self.runtime_context.output_otf,
        }[build_format]
        logger.info("Reuse cached %s outputs", build_format.upper())
        logger.debug("Cached %s output path: %s", build_format, output_dir)

    def log_stage_cache_validation(self, stage: str) -> None:
        task = _CACHE_STAGE_TASKS.get(stage)
        if task is not None:
            log_task(
                task,
                "Validate stage cache: stage=%s",
                stage,
                force_separator=True,
            )
            return

        logger.info(
            "Validate stage cache: stage=%s",
            stage,
        )

    def stage_cache_record_available(self, stage: str) -> bool:
        if self.cache_matches_build():
            return True
        logger.info(
            "Cache miss: stage=%s, reason=missing-cache-record path=%s",
            stage,
            "build-cache.json",
        )
        return False

    def validate_cached_stage(
        self,
        stage: str,
        paths: list[Path],
    ) -> bool:
        if not self.should_use_cache:
            return False
        self.log_stage_cache_validation(stage)
        return self.validate_cached_stage_after_log(stage, paths)

    def validate_cached_stage_after_log(
        self,
        stage: str,
        paths: list[Path],
    ) -> bool:
        self._validated_stage_records.pop(stage, None)
        if not self.stage_cache_record_available(stage):
            return False
        stage_record = validated_stage_record(
            Path(self.runtime_context.output_root),
            self._cache_record,
            stage,
            self.stage_cache_identity(stage),
            paths,
        )
        if stage_record is None:
            return False
        self._validated_stage_records[stage] = stage_record
        return True

    def validate_recorded_stage(
        self,
        stage: str,
        cjk_targets: list[tuple[str, ResolvedCJKBuildEntry, str]],
        nf_expected_paths: list[Path],
        nf_variable_expected_paths: list[Path],
        cjk_expected_paths_fn: Callable[[str], list[Path]],
    ) -> bool:
        if not self.should_use_cache:
            return False
        self.log_stage_cache_validation(stage)
        if not self.stage_cache_record_available(stage):
            return False
        stages = (self._cache_record or {}).get("stages")
        stage_record = stages.get(stage) if isinstance(stages, dict) else None
        if not isinstance(stage_record, dict):
            logger.info("Cache miss: stage=%s, reason=missing-record", stage)
            return False
        snapshot = stage_record.get("snapshot")
        files = snapshot.get("files") if isinstance(snapshot, dict) else None
        if not isinstance(files, list) or not files:
            logger.info("Cache miss: stage=%s, reason=missing-output", stage)
            return False
        if stage in {"nf", "nf-variable"}:
            return self.validate_cached_stage_after_log(
                stage,
                nf_expected_paths if stage == "nf" else nf_variable_expected_paths,
            )
        root = Path(self.runtime_context.output_root)
        cjk_stages = {
            target_stage for target_stage, _entry, _output_locale in cjk_targets
        }
        if stage not in cjk_stages:
            try:
                if not all(isinstance(relative, str) for relative in files):
                    raise ValueError("cache file list is invalid")
                paths = [root / Path(relative) for relative in sorted(files)]
                if any(
                    relative_cache_path(root, path) != relative
                    for relative, path in zip(sorted(files), paths, strict=False)
                ):
                    raise ValueError("cache path is outside the output root")
            except ValueError:
                logger.info("Cache miss: stage=%s, reason=invalid-record", stage)
                return False
            return self.validate_cached_stage_after_log(
                stage,
                paths,
            )

        cjk_target = next(
            (
                (entry, output_locale)
                for target_stage, entry, output_locale in cjk_targets
                if target_stage == stage
            ),
            None,
        )
        if cjk_target is None:
            raise ValueError(f"Unknown CJK stage: {stage}")
        _entry, output_locale = cjk_target
        paths = cjk_expected_paths_fn(output_locale)
        expected_files = {
            path.resolve().relative_to(root.resolve()).as_posix() for path in paths
        }
        if (
            not all(isinstance(relative, str) for relative in files)
            or set(files) != expected_files
        ):
            logger.info("Cache miss: stage=%s, reason=missing-output", stage)
            return False
        return self.validate_cached_stage_after_log(
            stage,
            paths,
        )

    def invalidate_recorded_stage(self, stage: str) -> None:
        self._validated_stage_records.pop(stage, None)
        self._rebuilt_stage_paths.pop(stage, None)
        if not self.should_use_cache or self._cache_record is None:
            return
        stages = self._cache_record.get("stages")
        if not isinstance(stages, dict) or stage not in stages:
            return
        del stages[stage]
        persist_cache_record(
            Path(self.runtime_context.output_root),
            self._cache_record,
        )

    def mark_stage_rebuilt(self, stage: str, paths: list[Path]) -> None:
        if not paths or any(
            not path.is_file() or path.stat().st_size == 0 for path in paths
        ):
            raise FileNotFoundError(
                f"Stage {stage} did not produce all expected output files"
            )
        self._validated_stage_records.pop(stage, None)
        self._rebuilt_stage_paths[stage] = list(paths)

    def stage_cache_identity(
        self,
        stage: str,
        cjk_targets: list[tuple[str, ResolvedCJKBuildEntry, str]] | None = None,
    ) -> str:
        record = self.font_config.to_dict()
        dependencies: dict[str, str] = {}
        if stage in {"variable", "ttf", "otf"}:
            inputs: dict[str, object] = {
                "base": self.current_build_identity(),
                "target_styles": (
                    list(self.target_styles) if self.target_styles is not None else None
                ),
            }
            if stage == "variable":
                inputs["target_styles"] = None
        elif stage == "ttf-autohint":
            dependencies["ttf"] = self.stage_cache_identity("ttf")
            inputs = {
                "ttfautohint_param": self.font_config.ttfautohint_param,
                "use_hinted": self.font_config.use_hinted,
            }
        elif stage == "woff2":
            dependencies["ttf"] = self.stage_cache_identity("ttf")
            inputs = {"format": "woff2"}
        elif stage == "nf":
            upstream = "ttf-autohint" if self.font_config.use_hinted else "ttf"
            dependencies[upstream] = self.stage_cache_identity(upstream)
            inputs = {
                "nerd_font": record.get("nerd_font"),
                "width": self.font_config.width,
                "line_height": self.font_config.line_height,
            }
        elif stage == "nf-variable":
            dependencies["variable"] = self.stage_cache_identity("variable")
            if should_use_font_patcher(self.font_config):
                upstream = "ttf-autohint" if self.font_config.use_hinted else "ttf"
                dependencies[upstream] = self.stage_cache_identity(upstream)
            inputs = {
                "nerd_font": record.get("nerd_font"),
                "width": self.font_config.width,
                "line_height": self.font_config.line_height,
            }
        elif self.plan.cjk_mode and (
            cjk_targets is None
            or stage in {target_stage for target_stage, _entry, _locale in cjk_targets}
        ):
            cjk_target = (
                next(
                    (
                        (entry, output_locale)
                        for target_stage, entry, output_locale in cjk_targets
                        if target_stage == stage
                    ),
                    None,
                )
                if cjk_targets
                else None
            )
            if cjk_target is not None:
                entry, output_locale = cjk_target
                upstream = "ttf-autohint" if self.font_config.use_hinted else "ttf"
                if self.plan.cjk_mode == "variable":
                    upstream = "variable"
                dependencies[upstream] = self.stage_cache_identity(upstream)
                if output_locale.startswith(
                    f"{self.font_config.get_nf_variant().directory_name}-"
                ):
                    dependencies["nf"] = self.stage_cache_identity("nf")
                inputs = {
                    "entry": serialize_cjk_build_config(entry.build_config),
                    "common_options": entry.common_options.to_dict(),
                    "output_locale": output_locale,
                    "cjk_format": self.plan.cjk_mode,
                    "ttfautohint_param": self.font_config.ttfautohint_param,
                }
            else:
                inputs = {"record": record}
        else:
            inputs = {"record": record}
        return stage_identity(inputs, stage, dependencies)

    def write_cache_record(self, requested_stages: list[str]) -> None:
        log_task(TaskName.BUILD, "Write cache record", force_separator=True)
        root = Path(self.runtime_context.output_root)
        stages: dict[str, dict[str, object]] = {}
        for stage in requested_stages:
            rebuilt_paths = self._rebuilt_stage_paths.get(stage)
            if rebuilt_paths is not None:
                if any(
                    not path.is_file() or path.stat().st_size == 0
                    for path in rebuilt_paths
                ):
                    raise FileNotFoundError(
                        f"Stage {stage} outputs changed before cache recording"
                    )
                stages[stage] = {
                    "key": self.stage_cache_identity(stage),
                    "snapshot": output_snapshot(
                        root,
                        stage,
                        rebuilt_paths,
                    ),
                }
                continue
            validated_record = self._validated_stage_records.get(stage)
            if validated_record is not None:
                stages[stage] = validated_record
        record: dict[str, Any] = {
            "schema": CACHE_SCHEMA,
            "stages": stages,
        }
        persist_cache_record(root, record)
        self._cache_record = record
        self._cache_identity_checked = True
        self._cache_identity_valid = True
