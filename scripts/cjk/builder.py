#!/usr/bin/env python3
from __future__ import annotations

import threading
from dataclasses import dataclass
from io import BytesIO
from os import cpu_count, makedirs
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal, TypeVar, cast

from fontTools.misc.transform import Transform
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.subset import Options
from fontTools.ttLib.scaleUpem import scale_upem
from ttfautohint import StemWidthMode, ttfautohint

from scripts.cjk.cache import write_static_hash, write_variable_hash
from scripts.cjk.config import (
    CJKBuildConfig,
    CJKMasterLocations,
    CJKTransformConfig,
    CJKWeightInstance,
)
from scripts.cjk.outlines import (
    as_fonttools_glyph_mapping,
    cff_master_glyph_order,
    convert_cff_master_files_to_glyf_tables_parallel,
    convert_cff_static_to_glyf,
    detect_outline_format,
    install_existing_glyf_tables,
)
from scripts.cjk.resolver import (
    apply_cli_overrides,
    apply_unicode_override,
    config_from_cli,
    config_from_json,
    ordered_master_locations,
)
from scripts.cjk.variable import (
    drop_font_tables,
    get_cmap_codepoints,
    get_unicode_cmap,
    make_italic_master_file,
    make_italic_variable_font,
    merge_masters_into_vf,
    recalculate_font_metrics,
    skew_glyphs,
    update_italic_metadata,
    weight_axis,
)
from scripts.errors import CJKSourceUnavailable
from scripts.external.process import (
    SynchronousExecutor,
    create_process_executor,
    is_ci,
    run_process_jobs,
)
from scripts.font_ops.fonttools import (
    HeadTable,
    SubsetOptions,
    TTFont,
    instantiate_variable_font,
    load_font,
    save_font_atomic,
)
from scripts.font_ops.names import FontNameConfig, set_font_name, update_font_names
from scripts.font_ops.subset import subset_to_codepoints
from scripts.utils.downloads import resolve_cached_download
from scripts.utils.files import archive
from scripts.utils.logging import logger, set_log_task

if TYPE_CHECKING:
    import argparse
    from collections.abc import Collection, Iterable
    from concurrent.futures import Executor

RESERVED_NAME_IDS = {1, 2, 4, 6, 16, 17, 25}
CFF_GLYPH_CHUNK_SIZE = 256
_T = TypeVar("_T")


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


@dataclass(frozen=True)
class AutoHintJob:
    input_path: str
    params: dict[str, Any]


@dataclass(frozen=True)
class SourceBuildState:
    outline_format: Literal["glyf", "cff2"]
    subset_path: Path
    source_codepoints: set[int]
    keep_codepoints: set[int]
    master_paths: tuple[Path, Path, Path]


@dataclass(frozen=True)
class BuildStats:
    added_glyphs: tuple[str, ...]
    added_codepoints: int


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


def get_ttfautohint_options(params: dict[str, Any]) -> dict[str, Any]:
    """Translate build configuration into ttfautohint-py options."""
    options = dict(params)
    stem_width_modes = options.pop("stem_width_mode", None)
    if not stem_width_modes:
        return options

    mode_options = {
        "gray": "gray_stem_width_mode",
        "gdi_cleartype": "gdi_cleartype_stem_width_mode",
        "dw_cleartype": "dw_cleartype_stem_width_mode",
    }
    for source_key, target_key in mode_options.items():
        mode = stem_width_modes.get(source_key)
        if mode is not None:
            options[target_key] = _stem_width_mode(mode)
    return options


def autohint_static_fonts(
    input_path: str | Path,
    params: dict[str, Any],
    *,
    pool_size: int = 1,
    executor: Executor | None = None,
) -> None:
    """Autohint a TTF file or every TTF in a flat directory."""
    path = Path(input_path)
    font_paths = [path] if path.is_file() else sorted(path.glob("*.ttf"))
    if not font_paths:
        raise FileNotFoundError(f"No TrueType fonts found in {path}")

    jobs = [AutoHintJob(str(font_path), dict(params)) for font_path in font_paths]
    run_process_jobs(pool_size, autohint_static_font_job, jobs, executor)


def autohint_static_font_job(job: AutoHintJob) -> None:
    font_path = Path(job.input_path)
    font = load_font(font_path)
    try:
        if "glyf" not in font:
            raise ValueError(f"Autohinting requires a TrueType font: {font_path}")
        buffer = BytesIO()
        font.save(buffer, reorderTables=None)
    finally:
        font.close()

    options = {
        "in_buffer": buffer.getvalue(),
        "out_file": str(font_path),
        "no_info": True,
    }
    options.update(get_ttfautohint_options(job.params))
    ttfautohint(**options)


def _stem_width_mode(mode: str) -> StemWidthMode:
    modes = {
        "natural": StemWidthMode.NATURAL,
        "strong": StemWidthMode.STRONG,
        "quantized": StemWidthMode.QUANTIZED,
    }
    try:
        return modes[mode]
    except KeyError as error:
        raise ValueError(f"Unknown stem width mode: {mode}") from error


def remove_mac_name_records(font: TTFont) -> bool:
    """Remove legacy Mac name records from a font."""
    if "name" not in font:
        return False
    before = len(font["name"].names)
    font["name"].removeNames(platformID=1)
    return len(font["name"].names) != before


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


def get_allowed_codepoints(source_font: TTFont, config: CJKBuildConfig) -> set[int]:
    """Select source codepoints allowed by configured ranges and encoding."""
    allowed = {
        codepoint
        for codepoint in get_cmap_codepoints(source_font)
        if any(start <= codepoint <= end for start, end in config.unicode.ranges)
    }
    if not config.unicode.filter_encoding:
        return allowed

    filtered: set[int] = set()
    for codepoint in allowed:
        try:
            chr(codepoint).encode(config.unicode.filter_encoding)
        except UnicodeEncodeError:
            continue
        filtered.add(codepoint)
    return filtered


def prepare_source_subset(
    source_path: Path,
    keep_codepoints: set[int],
    excluded_codepoints: set[int],
    config: CJKBuildConfig,
    out_path: Path,
) -> int:
    """Subset the CJK source to configured codepoints not already in the feature font."""
    font = load_font(source_path, decompile=True)
    try:
        drop_font_tables(font, config.source.drop_tables)
        filtered_codepoints = (
            keep_codepoints - excluded_codepoints
            if config.unicode.exclude_feature_codepoints
            else keep_codepoints
        )
        removed = len(keep_codepoints) - len(filtered_codepoints)
        if "gvar" in font:
            variations = font["gvar"].variations
            for glyph_name in font.getGlyphOrder():
                if glyph_name not in variations:
                    variations[glyph_name] = []
        options = cast("SubsetOptions", Options())
        options.layout_features = []
        options.name_IDs = ["*"]
        options.name_legacy = True
        options.name_languages = ["*"]
        options.recalc_bounds = True
        options.recalc_timestamp = False
        options.notdef_outline = True
        options.recommended_glyphs = False
        subset_to_codepoints(font, filtered_codepoints, options=options)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        font.save(out_path)
        return removed
    finally:
        font.close()


def apply_horizontal_metrics(font: TTFont, config: CJKBuildConfig) -> None:
    """Apply Maple Mono horizontal metrics to font."""
    for attr, value in config.hhea_metrics.items():
        setattr(font["hhea"], attr, value)
    for attr, value in config.os2_metrics.items():
        if hasattr(font["OS/2"], attr):
            setattr(font["OS/2"], attr, value)
    for attr, value in config.post_metrics.items():
        setattr(font["post"], attr, value)


def transform_glyph(
    font: TTFont,
    glyph_name: str,
    transform: CJKTransformConfig,
) -> None:
    """Apply configured scale and translation to one glyf glyph."""
    if "glyf" not in font:
        return
    glyf = font["glyf"]
    glyph = glyf[glyph_name]
    if glyph.isComposite():
        for component in glyph.components:
            if hasattr(component, "x"):
                component.x += transform.x_shift
            elif hasattr(component, "arg1") and not component.flags & 0x0002:
                component.arg1 += transform.x_shift
    elif getattr(glyph, "numberOfContours", 0) > 0:
        coordinates = glyph.coordinates
        if coordinates is None:
            coordinates, _, _ = glyph.getCoordinates(glyf)
            glyph.coordinates = coordinates
        coordinates.scale((transform.x_scale, transform.y_scale))
        coordinates.translate((transform.x_shift, transform.y_shift))
    glyph.recalcBounds(glyf)


def normalize_widths(
    font: TTFont,
    config: CJKBuildConfig,
    glyph_names: set[str] | None = None,
    protected_glyphs: set[str] | None = None,
) -> None:
    """Normalize CJK glyph advance widths without changing outlines."""
    target_glyphs, zero_width_glyphs = width_target_glyphs(
        font, glyph_names, protected_glyphs
    )
    for glyph_name in target_glyphs:
        if glyph_name not in font["hmtx"].metrics:
            continue
        _, lsb = font["hmtx"].metrics[glyph_name]
        width = (
            0
            if glyph_name in zero_width_glyphs
            else config.transform.target_advance_width
        )
        font["hmtx"].metrics[glyph_name] = (width, lsb)
    if "hhea" in font:
        font["hhea"].advanceWidthMax = config.transform.target_advance_width
    if "HVAR" in font:
        del font["HVAR"]


def width_target_glyphs(
    font: TTFont,
    glyph_names: set[str] | None = None,
    protected_glyphs: set[str] | None = None,
) -> tuple[set[str], set[str]]:
    """Resolve glyphs affected by width normalization."""
    cmap = get_unicode_cmap(font)
    zero_width_glyphs = {glyph for cp, glyph in cmap.items() if 0x0300 <= cp <= 0x036F}
    zero_width_glyphs.add(".notdef")
    target_glyphs = (
        glyph_names if glyph_names is not None else set(font.getGlyphOrder())
    )
    if protected_glyphs:
        target_glyphs = target_glyphs - protected_glyphs
    return target_glyphs, zero_width_glyphs


def apply_source_master_transform(font: TTFont, config: CJKBuildConfig) -> None:
    """Apply configured outline transform to a freshly instantiated source master."""
    target_glyphs, zero_width_glyphs = width_target_glyphs(font)
    transform_glyphs = {
        glyph_name
        for glyph_name in target_glyphs
        if glyph_name in font["hmtx"].metrics and glyph_name not in zero_width_glyphs
    }

    if "CFF " in font or "CFF2" in font:
        transform_cff_source_glyphs(font, config.transform, transform_glyphs)
    else:
        for glyph_name in transform_glyphs:
            transform_glyph(font, glyph_name, config.transform)

    if config.transform.x_shift:
        for glyph_name in transform_glyphs:
            advance_width, lsb = font["hmtx"].metrics[glyph_name]
            font["hmtx"].metrics[glyph_name] = (
                advance_width,
                lsb + config.transform.x_shift,
            )


def transform_cff_source_glyphs(
    font: TTFont,
    transform: CJKTransformConfig,
    glyph_names: set[str],
) -> None:
    """Apply configured source-master transform to CFF/CFF2 outlines."""
    transform_cff_glyphs(
        font,
        Transform(
            transform.x_scale,
            0,
            0,
            transform.y_scale,
            transform.x_shift,
            transform.y_shift,
        ),
        glyph_names,
    )


def transform_cff_glyphs(
    font: TTFont,
    glyph_transform: Transform,
    glyph_names: set[str] | None = None,
) -> None:
    """Draw CFF/CFF2 glyphs through an affine transform."""
    table_tag = "CFF2" if "CFF2" in font else "CFF " if "CFF " in font else None
    if table_tag is None:
        return

    is_cff2 = table_tag == "CFF2"
    top_dict = font.table(table_tag).cff.topDictIndex[0]
    char_strings = top_dict.CharStrings
    glyph_set = font.getGlyphSet()
    target_glyphs = (
        glyph_names if glyph_names is not None else set(font.getGlyphOrder())
    )

    for glyph_name in target_glyphs:
        if glyph_name not in char_strings or glyph_name not in glyph_set:
            continue
        pen = T2CharStringPen(None, as_fonttools_glyph_mapping(glyph_set), CFF2=is_cff2)
        glyph_set[glyph_name].draw(TransformPen(pen, glyph_transform))
        old_char_string = char_strings[glyph_name]
        char_strings[glyph_name] = pen.getCharString(
            private=old_char_string.private,
            globalSubrs=old_char_string.globalSubrs,
        )


def convert_cff_master_files_to_glyf(
    input_paths: tuple[str, str, str],
    output_paths: tuple[str, str, str],
    executor: Executor,
    transform_config: CJKBuildConfig | None = None,
) -> None:
    """Convert three compatible CFF source masters to TTF together."""
    glyph_order = cff_master_glyph_order(input_paths)
    glyf_tables = convert_cff_master_files_to_glyf_tables_parallel(
        input_paths,
        glyph_order,
        executor,
    )
    fonts = [load_font(path, decompile=True) for path in input_paths]
    try:
        install_existing_glyf_tables(fonts, glyf_tables)
        for font, output_path in zip(fonts, output_paths, strict=False):
            if transform_config is not None:
                apply_source_master_transform(font, transform_config)
                normalize_widths(font, transform_config)
                recalculate_font(font, transform_config)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            font.save(output_path)
    finally:
        for font in fonts:
            font.close()


def prune_stat(font: TTFont) -> None:
    """Prune STAT table to weight axis only."""
    if "STAT" not in font:
        return
    stat = font["STAT"].table
    if getattr(stat, "DesignAxisRecord", None):
        axes = [axis for axis in stat.DesignAxisRecord.Axis if axis.AxisTag == "wght"]
        stat.DesignAxisRecord.Axis = axes
        stat.DesignAxisRecord.AxisCount = len(axes)
        stat.DesignAxisCount = len(axes)


def recalculate_font(font: TTFont, config: CJKBuildConfig) -> None:
    """Recalculate common font metrics."""
    recalculate_font_metrics(font)
    if "OS/2" in font:
        font["OS/2"].xAvgCharWidth = config.transform.target_advance_width // 2


def load_feature_variable_font(input_path: Path) -> TTFont:
    """Load and validate the Maple feature variable font used as merge base."""
    logger.debug("Load feature variable font: path=%s", input_path)
    font = load_font(input_path, decompile=True)
    if "fvar" not in font:
        raise ValueError(f"Font is missing fvar table: {input_path}")
    axis = weight_axis(font)
    if axis is None:
        raise ValueError(f"Font is missing wght axis: {input_path}")
    return font


def update_variable_font_names(
    font: TTFont,
    subfamily: str,
    config: CJKBuildConfig,
    font_config: FontNameConfig,
) -> None:
    """Update variable font naming after merging CJK glyphs into the feature base."""
    family_name = config.naming.family_name
    full_name = f"{family_name} {subfamily}"
    postscript_name = f"{config.naming.postscript_prefix}-{subfamily.replace(' ', '')}"
    name_table = font["name"]
    move_fvar_instances_from_reserved_name_ids(font)
    for name_id in RESERVED_NAME_IDS:
        name_table.removeNames(nameID=name_id)

    update_font_names(
        font=font,
        font_config=font_config,
        family_name=family_name,
        style_name=subfamily,
        full_name=full_name,
        postscript_name=postscript_name,
        is_skip_subfamily=False,
        preferred_family_name=family_name,
        preferred_style_name=subfamily,
    )
    set_font_name(font, config.naming.postscript_prefix, 25)


def move_fvar_instances_from_reserved_name_ids(font: TTFont) -> None:
    """Keep fvar instance names independent from family/style name records."""
    if "fvar" not in font or "name" not in font:
        return
    name_table = font["name"]
    next_name_id = max(record.nameID for record in name_table.names) + 1
    for instance in font["fvar"].instances:
        if instance.subfamilyNameID not in RESERVED_NAME_IDS:
            continue
        name = name_table.getDebugName(instance.subfamilyNameID)
        if not name:
            continue
        replacement = find_name_id(name_table, name, RESERVED_NAME_IDS)
        if replacement is None:
            replacement = next_name_id
            next_name_id += 1
            name_table.setName(name, replacement, 3, 1, 0x409)
        instance.subfamilyNameID = replacement


def find_name_id(name_table: Any, value: str, excluded: set[int]) -> int | None:
    """Find an existing name ID for a string outside a reserved ID set."""
    for record in name_table.names:
        if record.nameID in excluded:
            continue
        try:
            if record.toUnicode() == value:
                return int(record.nameID)
        except UnicodeDecodeError:
            continue
    return None


def prepare_source_masters(
    subset_path: Path,
    config: CJKBuildConfig,
    process_pool: Executor,
    target_upem: int,
    outline_format: Literal["glyf", "cff2"],
) -> tuple[Path, Path, Path]:
    """Instantiate transformed source masters for the variable-base pipeline."""
    logger.debug(
        "Prepare CJK source masters: subset=%s, outline=%s",
        subset_path,
        outline_format,
    )
    if outline_format != "cff2":
        paths = instantiate_masters_from_vf(
            subset_path,
            config.temp_dir / "source-masters",
            config.source.masters,
            process_pool,
            ".ttf",
            target_upem=target_upem,
            transform_config=config,
        )
        logger.debug("CJK source masters prepared: output_dir=%s", paths[0].parent)
        return paths

    cff_master_paths = instantiate_masters_from_vf(
        subset_path,
        config.temp_dir / "source-masters-cff",
        config.source.masters,
        process_pool,
        ".otf",
        target_upem=target_upem,
        convert_cff_to_glyf=False,
    )
    ttf_master_paths = tuple(
        config.temp_dir / "source-masters" / f"{weight}-master.ttf"
        for weight, _ in ordered_master_locations(config.source.masters)
    )
    cff_master_path_strings = (
        str(cff_master_paths[0]),
        str(cff_master_paths[1]),
        str(cff_master_paths[2]),
    )
    ttf_master_path_strings = (
        str(ttf_master_paths[0]),
        str(ttf_master_paths[1]),
        str(ttf_master_paths[2]),
    )
    convert_cff_master_files_to_glyf(
        cff_master_path_strings,
        ttf_master_path_strings,
        process_pool,
        config,
    )
    logger.debug(
        "CFF2 source masters converted to glyf: output_dir=%s",
        ttf_master_paths[0].parent,
    )
    return (ttf_master_paths[0], ttf_master_paths[1], ttf_master_paths[2])


def finalize_variable_font(
    font: TTFont,
    added_glyphs: set[str],
    protected_glyphs: set[str],
    subfamily: str,
    config: CJKBuildConfig,
    font_config: FontNameConfig,
    is_italic: bool = False,
) -> None:
    """Apply final metrics, naming, axis, and table cleanup."""
    apply_horizontal_metrics(font, config)
    if is_italic:
        update_italic_metadata(font, config.transform.italic_angle)
    normalize_widths(
        font, config, glyph_names=added_glyphs, protected_glyphs=protected_glyphs
    )
    prune_stat(font)
    recalculate_font(font, config)
    update_variable_font_names(font, subfamily, config, font_config)


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


def finalize_static_font_instance(
    instance: TTFont,
    output_path: str,
    name: str,
    is_italic: bool,
    config: CJKBuildConfig,
    font_config: FontNameConfig,
) -> None:
    """Apply static font cleanup and save one instantiated font."""
    subfamily = (f"{name} Italic" if is_italic else name).replace(
        "Regular Italic", "Italic"
    )
    if "CFF " in instance:
        if is_italic:
            update_italic_metadata(instance, config.transform.italic_angle)
        convert_cff_static_to_glyf(instance)
        recalculate_font(instance, config)

    postscript_name = f"{config.naming.postscript_prefix}-{subfamily.replace(' ', '')}"
    update_font_names(
        font=instance,
        font_config=font_config,
        family_name=config.naming.family_name,
        style_name=subfamily,
        full_name=f"{config.naming.family_name} {subfamily}",
        postscript_name=postscript_name,
        is_skip_subfamily=True,
    )
    drop_font_tables(instance, ("kern", "GPOS"))
    remove_mac_name_records(instance)
    instance.save(output_path)
    logger.info("Instantiate CJK base static font to %s", output_path)


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


def build_cjk_from_args(
    args: argparse.Namespace,
    github_mirror: str = "github.com",
) -> None:
    """Build CJK fonts from JSON config plus CLI overrides or direct CLI flags."""
    from scripts.config.resolver import resolve_default_build_config

    if args.config:
        config = apply_cli_overrides(config_from_json(args.config), args)
    else:
        config = config_from_cli(args)
    build_cjk_fonts(
        apply_unicode_override(config, args.unicodes),
        resolve_default_build_config(),
        args.vf_only,
        github_mirror=github_mirror,
    )
