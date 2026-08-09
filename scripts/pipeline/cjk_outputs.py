from __future__ import annotations

import shutil
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.cjk.builder import (
    StaticFontCache,
    autohint_static_fonts,
    build_cjk_fonts,
    feature_weight_instances,
)
from scripts.cjk.static import (
    apply_cjk_meta_table,
    build_cjk_family_name,
    build_cjk_postscript_prefix,
    get_core_static_font_styles,
    get_static_style_name,
    postprocess_cjk_extended_static_font,
)
from scripts.cjk.variable import (
    drop_font_tables,
    merge_masters_into_vf,
    merge_vf,
    recalculate_font_metrics,
)
from scripts.config.paths import (
    merged_variable_name,
    static_output_dir,
    variable_output_dir,
)
from scripts.external.process import is_ci, run_process_jobs
from scripts.font_ops.fonttools import (
    instantiate_variable_font,
    load_font,
    save_font_atomic,
)
from scripts.font_ops.glyph_transform import (
    reduce_glyph_side_bearings,
)
from scripts.font_ops.merge import merge_ttfonts
from scripts.font_ops.names import update_font_names
from scripts.font_ops.opentype import add_weight_axis_values_to_stat
from scripts.pipeline.nerd_fonts import load_nerd_font_variable_source
from scripts.utils.logging import (
    TaskName,
    log_task,
    log_task_complete,
    logger,
    set_log_task,
)

if TYPE_CHECKING:
    from concurrent.futures import Executor

    from scripts.config.base import ResolvedCJKBuildEntry, ResolvedConfig
    from scripts.config.runtime import BuildRuntimeContext


@dataclass(frozen=True)
class CJKStaticMergeJob:
    entry: ResolvedCJKBuildEntry
    style_compact: str
    core_path: str
    cjk_base_path: str
    output_dir: str
    font_config: ResolvedConfig
    runtime_context: BuildRuntimeContext
    locale_suffix: str


@dataclass(frozen=True)
class CJKStaticBaseProfile:
    output_locale: str
    base_dir: str
    family_name_compact: str
    font_config: ResolvedConfig


@dataclass(frozen=True)
class CJKStaticInstanceJob:
    entry: ResolvedCJKBuildEntry
    input_path: str
    output_dir: str
    coordinate: float
    style_compact: str
    font_config: ResolvedConfig
    runtime_context: BuildRuntimeContext
    locale_suffix: str


def ensure_cjk_variable_fonts(
    entry: ResolvedCJKBuildEntry,
    font_config: ResolvedConfig,
    github_mirror: str,
    executor: Executor | None = None,
    runtime_context: BuildRuntimeContext | None = None,
) -> tuple[Path, Path]:
    preset_config = entry.build_config
    regular_path = preset_config.output.dir / preset_config.output.regular_variable
    italic_path = preset_config.output.dir / preset_config.output.italic_variable

    if (
        not entry.common_options.clean_cache
        and regular_path.is_file()
        and italic_path.is_file()
    ):
        logger.info("Reuse cached CJK variable fonts: %s", entry.display_name)
        logger.debug(
            "Cached CJK variable paths: regular=%s, italic=%s",
            regular_path,
            italic_path,
        )
        return regular_path, italic_path

    if (
        not entry.common_options.clean_cache
        and runtime_context is not None
        and runtime_context.download_cjk_variable_base(
            entry.download_locale,
            preset_config,
        )
        and regular_path.is_file()
        and italic_path.is_file()
    ):
        logger.info("Reuse downloaded CJK variable fonts: %s", entry.display_name)
        return regular_path, italic_path

    logger.info("Build CJK variable fonts: %s", entry.display_name)
    build_cjk_fonts(
        preset_config,
        font_config,
        vf_only=True,
        executor=executor,
        github_mirror=github_mirror,
    )

    return regular_path, italic_path


def build_cjk_extended_variable_fonts(
    entry: ResolvedCJKBuildEntry,
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    output_dir: Path,
    executor: Executor | None = None,
    output_locale: str | None = None,
    include_nerd_font: bool = False,
) -> tuple[Path, Path]:
    base_variable_paths = ensure_cjk_variable_fonts(
        entry,
        font_config,
        runtime_context.effective_github_mirror,
        executor,
        runtime_context,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    core_pairs = (
        (
            False,
            Path(runtime_context.output_variable)
            / f"{font_config.family_name_compact}[wght].ttf",
        ),
        (
            True,
            Path(runtime_context.output_variable)
            / f"{font_config.family_name_compact}-Italic[wght].ttf",
        ),
    )
    base_pairs = (
        (False, base_variable_paths[0]),
        (True, base_variable_paths[1]),
    )
    output_paths: list[Path] = []
    nerd_font = (
        load_nerd_font_variable_source(font_config, runtime_context)
        if include_nerd_font
        else None
    )

    try:
        for (is_italic, base_path), (_, extra_path) in zip(
            core_pairs, base_pairs, strict=False
        ):
            if not base_path.exists():
                raise FileNotFoundError(f"Core variable font not found: {base_path}")
            if not extra_path.exists():
                raise FileNotFoundError(f"CJK variable font not found: {extra_path}")

            merged_font = load_font(base_path, decompile=True)
            try:
                nf_added_glyphs = 0
                nf_added_codepoints = 0
                if nerd_font is not None:
                    added, added_codepoints = merge_masters_into_vf(
                        merged_font,
                        nerd_font,
                        nerd_font,
                        nerd_font,
                    )
                    nf_added_glyphs = len(added)
                    nf_added_codepoints = added_codepoints

                merged_font, cjk_added_glyphs, cjk_added_codepoints = merge_vf(
                    merged_font, extra_path
                )
                if font_config.get_width_name():
                    reduce_glyph_side_bearings(
                        merged_font,
                        cjk_added_glyphs,
                        {
                            font_config.glyph_width: font_config.get_target_width(),
                            2 * font_config.glyph_width: 2
                            * font_config.get_target_width(),
                        },
                    )
                recalculate_font_metrics(merged_font)
                merged_font.table("OS/2").xAvgCharWidth = font_config.get_target_width()
                drop_font_tables(merged_font, ("HVAR", "VVAR"))

                locale_suffix = output_locale or entry.locale_name
                nf_directory_name = font_config.get_nf_variant().directory_name
                nf_prefix = f"{nf_directory_name}-"
                if locale_suffix.startswith(nf_prefix):
                    locale_name = locale_suffix.removeprefix(nf_prefix)
                    nf_symbol = font_config.get_nf_variant().symbol
                    family_name = f"{font_config.family_name} {nf_symbol} {locale_name}"
                    postscript_prefix = (
                        f"{font_config.family_name_compact}-{nf_symbol}-{locale_name}"
                    )
                else:
                    family_name = build_cjk_family_name(font_config, locale_suffix)
                    postscript_prefix = build_cjk_postscript_prefix(
                        font_config, locale_suffix
                    )
                postscript_name = postscript_prefix + ("-Italic" if is_italic else "")
                style_name = "Italic" if is_italic else "Regular"
                update_font_names(
                    font=merged_font,
                    font_config=font_config,
                    family_name=family_name,
                    style_name=style_name,
                    full_name=f"{family_name} {style_name}",
                    postscript_name=postscript_name,
                    is_skip_subfamily=True,
                    narrow=entry.common_options.narrow,
                    variable=True,
                )
                add_weight_axis_values_to_stat(merged_font, italic=is_italic)
                if (
                    entry.is_builtin
                    and entry.common_options.fix_meta_table
                    and entry.preset_spec
                ):
                    apply_cjk_meta_table(
                        merged_font,
                        entry.preset_spec.meta_languages,
                        entry.preset_spec.code_page_range1,
                    )
                output_path = output_dir / merged_variable_name(
                    postscript_prefix, is_italic
                )
                logger.debug(
                    "Merge CJK variable font: locale=%s, nf_glyphs_added=%s, "
                    "nf_unicodes_added=%s, cjk_glyphs_added=%s, "
                    "cjk_unicodes_added=%s",
                    entry.display_name,
                    nf_added_glyphs,
                    nf_added_codepoints,
                    len(cjk_added_glyphs),
                    cjk_added_codepoints,
                )
                save_font_atomic(merged_font, output_path)
                logger.info("Saved merged variable font to %s", output_path)
                output_paths.append(output_path)
            finally:
                merged_font.close()
    finally:
        if nerd_font is not None:
            nerd_font.close()

    return output_paths[0], output_paths[1]


def cjk_static_base_profiles(
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    entry: ResolvedCJKBuildEntry,
) -> list[CJKStaticBaseProfile]:
    profiles: list[CJKStaticBaseProfile] = []
    should_build_nf_cjk = (
        runtime_context.is_nf_built and entry.common_options.with_nerd_font
    )
    if should_build_nf_cjk:
        nf_variant = font_config.get_nf_variant()
        nf_suffix = nf_variant.symbol
        nf_font_config = deepcopy(font_config)
        nf_font_config.identity.family_name = f"{font_config.family_name} {nf_suffix}"
        nf_font_config.identity.family_name_compact = (
            f"{font_config.family_name_compact}-{nf_suffix}"
        )
        profiles.append(
            CJKStaticBaseProfile(
                output_locale=nf_variant.cjk_directory_name(entry.locale_name),
                base_dir=runtime_context.output_nf,
                family_name_compact=f"{font_config.family_name_compact}-{nf_suffix}",
                font_config=nf_font_config,
            )
        )

    if not should_build_nf_cjk or font_config.use_cjk_both:
        profiles.append(
            CJKStaticBaseProfile(
                output_locale=entry.locale_name,
                base_dir=runtime_context.ttf_base_dir,
                family_name_compact=font_config.family_name_compact,
                font_config=font_config,
            )
        )

    return profiles


def instantiate_cjk_extended_static_fonts(
    entry: ResolvedCJKBuildEntry,
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    merged_paths: tuple[Path, Path],
    target_styles: list[str] | None,
    output_locale: str | None = None,
    executor: Executor | None = None,
) -> Path:
    output_dir = static_output_dir(
        runtime_context.output_dir,
        output_locale or entry.locale_name,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    jobs: list[CJKStaticInstanceJob] = []
    for is_italic, merged_path in ((False, merged_paths[0]), (True, merged_paths[1])):
        var_font = load_font(merged_path, decompile=True)
        try:
            instances = feature_weight_instances(var_font)
            for instance in instances:
                style_compact = (
                    f"{instance.name}Italic" if is_italic else instance.name
                ).replace("RegularItalic", "Italic")
                if target_styles and style_compact not in target_styles:
                    continue
                jobs.append(
                    CJKStaticInstanceJob(
                        entry=entry,
                        input_path=str(merged_path),
                        output_dir=str(output_dir),
                        coordinate=instance.coordinate,
                        style_compact=style_compact,
                        font_config=font_config,
                        runtime_context=runtime_context,
                        locale_suffix=output_locale or entry.locale_name,
                    )
                )
        finally:
            var_font.close()

    run_process_jobs(
        font_config.pool_size,
        instantiate_cjk_extended_static_font_job,
        jobs,
        executor,
    )

    if entry.common_options.use_hinted:
        logger.debug("Auto-hint CJK static fonts: locale=%s", entry.display_name)
        autohint_static_fonts(
            output_dir,
            font_config.ttfautohint_param,
            pool_size=font_config.pool_size,
            executor=executor,
        )

    return output_dir


def instantiate_cjk_extended_static_font_job(job: CJKStaticInstanceJob) -> None:
    set_log_task(job.entry.locale_name.lower())
    logger.debug(
        "Instantiate CJK static font: locale=%s, style=%s",
        job.entry.display_name,
        job.style_compact,
    )
    var_font = StaticFontCache.get(job.input_path)
    static_font = instantiate_variable_font(
        var_font,
        {"wght": job.coordinate},
        static=True,
        downgrade_cff2="CFF2" in var_font,
    )
    try:
        postscript_name = postprocess_cjk_extended_static_font(
            static_font,
            job.entry,
            job.font_config,
            job.runtime_context,
            job.style_compact,
            job.locale_suffix,
        )
        output_path = Path(job.output_dir) / f"{postscript_name}.ttf"
        save_font_atomic(static_font, output_path)
        logger.info("Saved CJK static font to %s", output_path)
    finally:
        static_font.close()


def merge_cached_cjk_static_font_job(job: CJKStaticMergeJob) -> None:
    set_log_task(job.entry.locale_name.lower())
    logger.debug(
        "Merge cached CJK static font: locale=%s, style=%s",
        job.entry.display_name,
        job.style_compact,
    )
    static_font = merge_ttfonts(
        base_font_path=job.core_path,
        extra_font_path=job.cjk_base_path,
    )
    try:
        postscript_name = postprocess_cjk_extended_static_font(
            static_font,
            job.entry,
            job.font_config,
            job.runtime_context,
            job.style_compact,
            job.locale_suffix,
        )
        output_path = Path(job.output_dir) / f"{postscript_name}.ttf"
        save_font_atomic(static_font, output_path)
        logger.info("Saved CJK static font to %s", output_path)
    finally:
        static_font.close()


def load_cached_cjk_static_fonts(
    cache_dir: Path,
    static_file_prefix: str,
) -> dict[str, Path]:
    cached_fonts: dict[str, Path] = {}
    if not cache_dir.is_dir():
        return cached_fonts
    for font_path in sorted(cache_dir.glob("*.ttf")):
        style_compact = get_static_style_name(font_path, static_file_prefix)
        if not style_compact:
            continue
        cached_fonts[style_compact] = font_path
    return cached_fonts


def build_cjk_extended_static_fonts_from_cache(
    entry: ResolvedCJKBuildEntry,
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    target_styles: list[str] | None,
    executor: Executor | None = None,
    output_locales: set[str] | None = None,
) -> bool:
    base_profiles = cjk_static_base_profiles(
        font_config,
        runtime_context,
        entry,
    )
    if output_locales is not None:
        base_profiles = [
            profile
            for profile in base_profiles
            if profile.output_locale in output_locales
        ]
    profile_core_fonts = [
        (
            profile,
            get_core_static_font_styles(
                profile.base_dir,
                profile.family_name_compact,
                target_styles,
            ),
        )
        for profile in base_profiles
    ]
    profile_core_fonts = [
        (profile, core_fonts)
        for profile, core_fonts in profile_core_fonts
        if core_fonts
    ]
    if not profile_core_fonts:
        return False

    required_styles = sorted(
        {style for _, core_fonts in profile_core_fonts for style, _ in core_fonts}
    )
    resolved_base = runtime_context.resolve_cjk_static_base(
        entry,
        required_styles,
        font_config,
        build_cjk_fonts,
        executor,
    )
    cached_fonts = load_cached_cjk_static_fonts(
        resolved_base.static_dir,
        resolved_base.static_file_prefix,
    )
    missing_styles = [style for style in required_styles if style not in cached_fonts]

    if missing_styles:
        raise FileNotFoundError(
            f"Resolved {entry.locale_name} static CJK base from "
            f"{resolved_base.source_kind}, but style(s) are missing: "
            f"{', '.join(missing_styles)}"
        )

    logger.debug(
        "Use cached CJK static fonts: locale=%s, source=%s, path=%s",
        entry.display_name,
        resolved_base.source_kind,
        resolved_base.static_dir,
    )

    jobs: list[CJKStaticMergeJob] = []
    for profile, core_fonts in profile_core_fonts:
        output_dir = static_output_dir(
            runtime_context.output_dir, profile.output_locale
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        jobs.extend(
            CJKStaticMergeJob(
                entry=entry,
                style_compact=style_compact,
                core_path=str(core_path),
                cjk_base_path=str(cached_fonts[style_compact]),
                output_dir=str(output_dir),
                font_config=profile.font_config,
                runtime_context=runtime_context,
                locale_suffix=profile.output_locale,
            )
            for style_compact, core_path in core_fonts
        )

    run_process_jobs(
        font_config.pool_size,
        merge_cached_cjk_static_font_job,
        jobs,
        executor,
    )

    if entry.common_options.use_hinted:
        logger.debug("Auto-hint CJK static fonts: locale=%s", entry.display_name)
        for profile, _ in profile_core_fonts:
            autohint_static_fonts(
                static_output_dir(
                    runtime_context.output_dir,
                    profile.output_locale,
                ),
                font_config.ttfautohint_param,
                pool_size=font_config.pool_size,
                executor=executor,
            )

    return True


def build_cjk_extended_variable_outputs(
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    executor: Executor | None = None,
    output_locales: set[str] | None = None,
    started_at: float | None = None,
) -> None:
    entries = font_config.get_selected_cjk_entries()
    if not entries:
        if is_ci():
            logger.debug("Skip CJK outputs because no locale is selected")
        else:
            logger.info("Skip CJK outputs: reason=no CJK locale selected")
        return

    for entry in entries:
        task_started_at = (
            started_at
            if started_at is not None
            else log_task(
                TaskName.CJK,
                "Build CJK variable outputs (%s)",
                entry.display_name,
                task_label=entry.locale_name.lower(),
            )
        )
        started_at = None
        include_nf = (
            font_config.nerd_font.enable and entry.common_options.with_nerd_font
        )
        profiles = []
        if include_nf:
            profiles.append(
                (
                    font_config.get_nf_variant().cjk_directory_name(entry.locale_name),
                    True,
                )
            )
        if not include_nf or font_config.use_cjk_both:
            profiles.append((entry.locale_name, False))
        if output_locales is not None:
            profiles = [profile for profile in profiles if profile[0] in output_locales]

        output_paths: list[Path] = []
        for output_locale, profile_include_nf in profiles:
            output_paths.extend(
                build_cjk_extended_variable_fonts(
                    entry,
                    font_config,
                    runtime_context,
                    variable_output_dir(runtime_context.output_dir, output_locale),
                    executor,
                    output_locale=output_locale,
                    include_nerd_font=profile_include_nf,
                )
            )
        log_task_complete(task_started_at, f"{len(output_paths)} fonts")

    runtime_context.is_cjk_built = True


def build_cjk_extended_static_outputs(
    font_config: ResolvedConfig,
    runtime_context: BuildRuntimeContext,
    target_styles: list[str] | None,
    executor: Executor | None = None,
    output_locales: set[str] | None = None,
    started_at: float | None = None,
) -> None:
    entries = font_config.get_selected_cjk_entries()
    if not entries:
        if is_ci():
            logger.debug("Skip CJK outputs because no locale is selected")
        else:
            logger.info("Skip CJK outputs: reason=no CJK locale selected")
        return

    temp_root = Path(runtime_context.output_dir) / ".cjk-temp"
    built_any = False
    for entry in entries:
        task_started_at = (
            started_at
            if started_at is not None
            else log_task(
                TaskName.CJK,
                "Build CJK static outputs (%s)",
                entry.display_name,
                task_label=entry.locale_name.lower(),
            )
        )
        started_at = None
        built_from_cache = build_cjk_extended_static_fonts_from_cache(
            entry,
            font_config,
            runtime_context,
            target_styles,
            executor,
            output_locales,
        )
        if built_from_cache:
            built_any = True
            output_locales_for_count = output_locales or {
                entry.locale_name,
                font_config.get_nf_variant().cjk_directory_name(entry.locale_name),
            }
            output_count = sum(
                len(
                    list(
                        static_output_dir(
                            runtime_context.output_dir,
                            locale,
                        ).glob("*.ttf")
                    )
                )
                for locale in output_locales_for_count
            )
            log_task_complete(task_started_at, f"{output_count} fonts")
            continue

        profiles = cjk_static_base_profiles(font_config, runtime_context, entry)
        if output_locales is not None:
            profiles = [
                profile
                for profile in profiles
                if profile.output_locale in output_locales
            ]
        output_count = 0
        for profile in profiles:
            locale_output_dir = temp_root / profile.output_locale.upper()
            merged_paths = build_cjk_extended_variable_fonts(
                entry,
                font_config,
                runtime_context,
                locale_output_dir,
                executor,
                output_locale=profile.output_locale,
                include_nerd_font=profile.output_locale.startswith(
                    f"{font_config.get_nf_variant().directory_name}-"
                ),
            )
            built_any = True
            instantiate_cjk_extended_static_fonts(
                entry,
                profile.font_config,
                runtime_context,
                merged_paths,
                target_styles,
                profile.output_locale,
                executor,
            )
            output_count += len(
                list(
                    static_output_dir(
                        runtime_context.output_dir,
                        profile.output_locale,
                    ).glob("*.ttf")
                )
            )
            shutil.rmtree(locale_output_dir, ignore_errors=True)
        log_task_complete(task_started_at, f"{output_count} fonts")

    shutil.rmtree(temp_root, ignore_errors=True)
    runtime_context.is_cjk_built = built_any
    if not built_any:
        logger.warning(
            "Skip CJK outputs: locales=%s, mode=%s, reason=all selected locale builds failed",
            ",".join(entry.locale_name for entry in entries),
            font_config.cjk_output_format,
        )
