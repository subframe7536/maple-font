from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, cast

from fontTools.ttLib.scaleUpem import scale_upem

from scripts.cjk.config import CJKBuildConfig, CJKMasterLocations, CJKWeightInstance
from scripts.cjk.masters import ordered_master_locations
from scripts.cjk.outlines import convert_cff_static_to_glyf
from scripts.cjk.postprocess import finalize_static_font_instance
from scripts.cjk.variable import (
    drop_font_tables,
    recalculate_font_metrics,
    skew_glyphs,
    update_italic_metadata,
)
from scripts.font_ops.fonttools import (
    HeadTable,
    TTFont,
    instantiate_variable_font,
    load_font,
)
from scripts.utils.logging import logger, set_log_task

if TYPE_CHECKING:
    from collections.abc import Iterable
    from concurrent.futures import Executor
    from pathlib import Path

    from scripts.font_ops.names import FontNameConfig


@dataclass(frozen=True)
class MasterBuildJob:
    input_path: str
    output_path: str
    axes: dict[str, float]
    static: bool = True
    optimize: bool = False
    drop_table_tags: tuple[str, ...] = ()
    target_upem: int | None = None
    transform_config: CJKBuildConfig | None = None
    convert_cff_to_glyf: bool = True


@dataclass(frozen=True)
class ItalicMasterJob:
    input_path: str
    output_path: str
    axes: dict[str, float]
    italic_angle: float
    task: str = "cjk"


@dataclass(frozen=True)
class StaticInstanceJob:
    input_path: str
    output_path: str
    coordinate: float
    name: str
    is_italic: bool
    config: CJKBuildConfig
    font_config: FontNameConfig


class StaticFontCache:
    """Worker-local cache for repeated variable font instantiation."""

    _fonts: ClassVar[dict[tuple[str, int], TTFont]] = {}

    @classmethod
    def get(cls, input_path: str) -> TTFont:
        cache_key = (input_path, threading.get_ident())
        font = cls._fonts.get(cache_key)
        if font is None:
            font = load_font(input_path, decompile=True)
            drop_font_tables(font, ("STAT",))
            cls._fonts[cache_key] = font
        return font

    @classmethod
    def clear(cls) -> None:
        while cls._fonts:
            _, font = cls._fonts.popitem()
            font.close()


def instantiate_variable_font_file(
    input_path: str,
    output_path: str,
    axes: dict[str, float],
    static: bool = False,
    optimize: bool = True,
    drop_table_tags: Iterable[str] = (),
    target_upem: int | None = None,
    transform_config: CJKBuildConfig | None = None,
    convert_cff_to_glyf: bool = True,
) -> None:
    """Instantiate a variable font from disk and save it to disk."""
    from scripts.cjk.source import (
        apply_source_master_transform,
        normalize_widths,
        recalculate_font,
    )

    set_log_task(transform_config.locale_name.lower() if transform_config else "cjk")
    font = load_font(input_path, decompile=True)
    try:
        logger.debug("Instantiate variable font: path=%s, axes=%s", input_path, axes)
        instance = instantiate_variable_font(
            font,
            axes,
            optimize=optimize,
            static=static,
            downgrade_cff2=static and "CFF2" in font,
        )
        try:
            if target_upem is not None and "head" in instance:
                source_upem = cast("HeadTable", instance["head"]).unitsPerEm
                if source_upem != target_upem:
                    logger.debug(
                        "Scale source UPEM: source=%s, target=%s",
                        source_upem,
                        target_upem,
                    )
                    scale_upem(instance, target_upem)
            drop_font_tables(instance, drop_table_tags)
            if transform_config:
                apply_source_master_transform(instance, transform_config)
                normalize_widths(instance, transform_config)
                if convert_cff_to_glyf and "CFF " in instance:
                    convert_cff_static_to_glyf(instance)
                recalculate_font(instance, transform_config)
            instance.save(output_path)
        finally:
            instance.close()
    finally:
        font.close()


def instantiate_variable_font_job(job: MasterBuildJob) -> None:
    """Top-level process-pool entrypoint for source master instantiation."""
    instantiate_variable_font_file(
        job.input_path,
        job.output_path,
        job.axes,
        job.static,
        job.optimize,
        job.drop_table_tags,
        job.target_upem,
        job.transform_config,
        job.convert_cff_to_glyf,
    )


def instantiate_masters_from_vf(
    vf_path: Path,
    output_dir: Path,
    masters: CJKMasterLocations,
    process_pool: Executor,
    output_suffix: str = ".ttf",
    drop_table_tags: Iterable[str] = (),
    target_upem: int | None = None,
    transform_config: CJKBuildConfig | None = None,
    convert_cff_to_glyf: bool = True,
) -> tuple[Path, Path, Path]:
    """Instantiate the configured static masters from a variable font."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(
        "Instantiate CJK masters: input=%s, output_dir=%s",
        vf_path,
        output_dir,
    )
    futures = []
    paths: list[Path] = []
    for output_weight, axes in ordered_master_locations(masters):
        output_path = output_dir / f"{output_weight}-master{output_suffix}"
        paths.append(output_path)
        job = MasterBuildJob(
            input_path=str(vf_path),
            output_path=str(output_path),
            axes=axes,
            static=True,
            optimize=False,
            drop_table_tags=tuple(drop_table_tags),
            target_upem=target_upem,
            transform_config=transform_config,
            convert_cff_to_glyf=convert_cff_to_glyf,
        )
        futures.append(process_pool.submit(instantiate_variable_font_job, job))
    for future in futures:
        future.result()
    logger.debug("CJK masters ready: output_dir=%s", output_dir)
    return cast("tuple[Path, Path, Path]", tuple(paths))


def instantiate_italic_master_file(
    input_path: str,
    output_path: str,
    axes: dict[str, float],
    italic_angle: float,
    task: str = "cjk",
) -> None:
    """Instantiate one static master from a VF, skew it, and save it."""
    set_log_task(task)
    font = load_font(input_path, decompile=True)
    try:
        logger.debug("Instantiate italic font: path=%s, axes=%s", input_path, axes)
        instance = instantiate_variable_font(
            font,
            axes,
            optimize=False,
            static=True,
            downgrade_cff2="CFF2" in font,
        )
        try:
            skew_glyphs(instance, italic_angle)
            update_italic_metadata(instance, italic_angle)
            recalculate_font_metrics(instance)
            instance.save(output_path)
        finally:
            instance.close()
    finally:
        font.close()


def instantiate_italic_master_job(job: ItalicMasterJob) -> None:
    """Top-level process-pool entrypoint for italic master instantiation."""
    instantiate_italic_master_file(
        job.input_path,
        job.output_path,
        job.axes,
        job.italic_angle,
        job.task,
    )


def instantiate_italic_masters_from_vf(
    vf_path: Path,
    output_dir: Path,
    masters: CJKMasterLocations,
    process_pool: Executor,
    italic_angle: float,
    task: str = "cjk",
) -> tuple[Path, Path, Path]:
    """Instantiate and skew configured static masters from a variable font."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(
        "Instantiate italic CJK masters: input=%s, output_dir=%s, angle=%s",
        vf_path,
        output_dir,
        italic_angle,
    )
    futures = []
    paths: list[Path] = []
    for output_weight, axes in ordered_master_locations(masters):
        output_path = output_dir / f"{output_weight}-italic-master.ttf"
        paths.append(output_path)
        job = ItalicMasterJob(
            input_path=str(vf_path),
            output_path=str(output_path),
            axes=axes,
            italic_angle=italic_angle,
            task=task,
        )
        futures.append(process_pool.submit(instantiate_italic_master_job, job))
    for future in futures:
        future.result()
    logger.debug("Italic CJK masters ready: output_dir=%s", output_dir)
    return cast("tuple[Path, Path, Path]", tuple(paths))


def map_weight_coordinate(
    coordinate: float,
    source_min: float,
    source_default: float,
    source_max: float,
    target_min: float,
    target_default: float,
    target_max: float,
) -> float:
    """Map a feature-font weight coordinate onto another weight axis."""
    if coordinate <= source_default:
        if source_default == source_min:
            return target_default
        ratio = (coordinate - source_min) / (source_default - source_min)
        return target_min + ratio * (target_default - target_min)
    if source_max == source_default:
        return target_default
    ratio = (coordinate - source_default) / (source_max - source_default)
    return target_default + ratio * (target_max - target_default)


def feature_weight_instances(feature_font: TTFont) -> tuple[CJKWeightInstance, ...]:
    """Read static weight instances from the Maple feature font."""
    if "fvar" not in feature_font:
        raise ValueError("Feature font is missing fvar table")
    instances: list[CJKWeightInstance] = []
    for instance in feature_font["fvar"].instances:
        if "wght" not in instance.coordinates:
            continue
        name = feature_font["name"].getDebugName(instance.subfamilyNameID)
        if not name:
            raise ValueError(
                f"Feature font is missing instance name ID {instance.subfamilyNameID}"
            )
        instances.append(CJKWeightInstance(name, float(instance.coordinates["wght"])))
    return tuple(sorted(instances, key=lambda item: item.coordinate))


def get_static_worker_font(input_path: str) -> TTFont:
    """Load each variable font once per worker process or thread."""
    return StaticFontCache.get(input_path)


def instantiate_static_font_file(
    input_path: str,
    output_path: str,
    coordinate: float,
    name: str,
    is_italic: bool,
    config: CJKBuildConfig,
    font_config: FontNameConfig,
) -> None:
    """Instantiate one static CJK font and apply final naming cleanup."""
    set_log_task(config.locale_name.lower())
    logger.debug(
        "Instantiate CJK static font: name=%s, italic=%s",
        name,
        is_italic,
    )
    var_font = get_static_worker_font(input_path)
    instance = instantiate_variable_font(
        var_font,
        {"wght": coordinate},
        static=True,
        downgrade_cff2="CFF2" in var_font,
    )
    try:
        finalize_static_font_instance(
            instance,
            output_path,
            name,
            is_italic,
            config,
            font_config,
        )
    finally:
        instance.close()


def instantiate_static_font_job(job: StaticInstanceJob) -> None:
    """Top-level process-pool entrypoint for static font instantiation."""
    instantiate_static_font_file(
        job.input_path,
        job.output_path,
        job.coordinate,
        job.name,
        job.is_italic,
        job.config,
        job.font_config,
    )
