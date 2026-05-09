from os import remove
from typing import Union
from uuid import uuid4
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
from fontTools.subset import Subsetter
import json

from source.py.utils import (
    get_font_forge_bin,
    joinPaths,
    parse_style_name,
    run,
    set_font_name,
    update_font_names,
)
from source.py.task._utils import default_weight_map
from foundrytools import Font
from foundrytools.app.var2static import run as var2static


def apply_unicode_subset(
    font_path: str, unicode_ranges: list[tuple[int, int]], output_path: str
) -> None:
    """
    Subset font to keep only specified unicode ranges using fontTools.

    Args:
        font_path: Path to input font
        unicode_ranges: List of (start, end) tuples (inclusive)
        output_path: Path to save subsetted font
    """
    subsetter = Subsetter()

    # Build list of unicodes to keep
    unicodes_to_keep = []
    for start, end in unicode_ranges:
        unicodes_to_keep.extend(range(start, end + 1))

    subsetter.populate(unicodes=unicodes_to_keep)

    font = TTFont(font_path)
    subsetter.subset(font)
    font.save(output_path)
    font.close()


def merge_fonts(
    output_dir: str,
    base_font_path: str,
    overrides: list[dict],
    tmp_dir: str,
) -> str:
    """
    Merge base font with multiple override fonts.

    Python side handles:
    - Unicode subsetting (using fontTools.subset)
    - Variable font instantiation

    FontForge side handles:
    - Width scaling
    - UPEM normalization
    - Font merging

    Args:
        output_dir: Output directory for merged font
        base_font_path: Path to base font
        overrides: List of dicts with keys: path, unicode_range, width_scale, is_temp
        tmp_dir: Temporary directory for intermediate files

    Returns:
        Path to merged font file
    """
    # Prepare each override font (Python side operations)
    prepared_overrides = []
    for idx, override in enumerate(overrides):
        override_path = override["path"]
        unicode_ranges = override.get("unicode_range")
        width_scale = override.get("width_scale")

        temp_file_path = override_path

        # Apply unicode subset if specified (Python side)
        if unicode_ranges:
            subset_filename = f"subset_{idx}_{uuid4().hex[:8]}.ttf"
            subset_path = joinPaths(tmp_dir, subset_filename)
            print(f"  Applying unicode subset to override {idx}...")
            apply_unicode_subset(override_path, unicode_ranges, subset_path)
            temp_file_path = subset_path

        prepared_overrides.append(
            {
                "path": temp_file_path,
                "width_scale": width_scale,
            }
        )

    # Create merger config JSON for FontForge
    merger_config = {
        "base_font": base_font_path,
        "overrides": prepared_overrides,
    }
    config_path = joinPaths(tmp_dir, f"merger_config_{uuid4().hex[:8]}.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(merger_config, f, indent=2)

    # Call FontForge merger
    bin = get_font_forge_bin()
    if bin is None:
        print("No fontforge bin detected, try to use the `fontforge` command directly")
        bin = "fontforge"

    merged_filename = f"merged_{uuid4().hex[:8]}.ttf"
    merged_path = joinPaths(output_dir, merged_filename)

    run(
        [
            bin,
            "-script",
            "source/py/task/merge_font/merger.py",
            config_path,
            merged_path,
        ]
    )

    # Cleanup merger config
    remove(config_path)

    return merged_path


def instantiate(input_font_path: str, output_font_path: str, config: dict) -> None:
    """
    Instantiate a variable font with the given configuration.

    :param input_font_path: The path to the input font file.
    :param output_font_path: The path to the output font file.
    :param config: A dictionary containing axis configurations.
    """
    f = Font(input_font_path)
    coordinates = {}
    instance = NamedInstance()
    for a in f.t_fvar.table.axes:
        axis_tag = a.axisTag
        min_value = a.minValue
        max_value = a.maxValue
        val = config.get(axis_tag, a.defaultValue)
        if min_value > val or max_value < val:
            raise Exception(f"Invalid axe value, range: [{min_value}, {max_value}]")
        coordinates[axis_tag] = val

    instance.coordinates = coordinates

    static_font, file_base_name = var2static(f, instance)
    static_font.save(output_font_path)
    static_font.close()
    f.close()


def _get_glyph_bounds(font, glyph_name):
    """Get (yMin, yMax) of a glyph by name from 'glyf' table."""
    glyph_order = font.getGlyphOrder()
    if glyph_name not in glyph_order:
        raise ValueError(f"Glyph '{glyph_name}' not found in font.")
    glyf = font["glyf"]
    glyph = glyf[glyph_name]
    if glyph.numberOfContours == 0:
        # Empty glyph
        return (0, 0)
    y_min = glyph.yMin
    y_max = glyph.yMax
    return (y_min, y_max)


def auto_xheight_capheight(font: TTFont):
    if "OS/2" not in font:
        raise ValueError("Font does not have an OS/2 table.")
    if "glyf" not in font:
        raise ValueError(
            "This script only supports TrueType (glyf) fonts. CFF support not implemented."
        )

    try:
        # Get bounds
        z_ymin, z_ymax = _get_glyph_bounds(font, "z")
        Z_ymin, Z_ymax = _get_glyph_bounds(font, "Z")

        x_height = round(z_ymax)  # xHeight = top of lowercase 'z'
        cap_height = round(Z_ymax)  # capHeight = top of uppercase 'Z'

        # Update OS/2 table
        os2 = font["OS/2"]
        os2.sxHeight = x_height  # type: ignore
        os2.sCapHeight = cap_height  # type: ignore
    except Exception as e:
        print(e)


weight_to_fsSelection = {
    100: 0x00,
    200: 0x00,
    300: 0x00,
    400: 0x40,
    500: 0x40,
    600: 0x20,
    700: 0x20,
    800: 0x20,
    900: 0x20,
}


def auto_weight_and_fsSelection(font: TTFont, style_name: str) -> None:
    """Set usWeightClass and fsSelection based on weight value."""
    base_style = style_name.lower().replace("italic", "").strip()
    if not base_style:
        base_style = "regular"

    if base_style not in default_weight_map:
        print(
            f"Error: Invalid style '{style_name}'. Must be one of: {list(default_weight_map.keys())} "
            f"(with optional 'Italic' suffix)."
        )
        exit(1)

    weight = default_weight_map[base_style]
    os2 = font["OS/2"]
    os2.usWeightClass = weight  # type: ignore

    fs = weight_to_fsSelection.get(weight, 0x00)

    is_italic = "Italic" in style_name
    if is_italic:
        fs |= 0x01

    os2.fsSelection = fs  # type: ignore


def change_line_height(
    font: TTFont,
    factor: float = 1.0,
    metric: tuple[float, float] | None = None,
    safe_metric: tuple[float, float] | None = None,
) -> None:
    """
    Adjust the line height of the font by modifying the hhea and OS/2 table.

    Args:
        font: The font to modify
        factor: Scale factor to apply to metrics
        metric: Tuple of (ascender, descender) for custom metrics
        safe_metric: Tuple of (safe_ascender, safe_descender) for safe metrics
    """

    if "hhea" not in font:
        raise ValueError("No hhea table found.")
    if "OS/2" not in font:
        raise ValueError("No OS/2 table found.")

    hhea = font["hhea"]
    os2 = font["OS/2"]

    if metric:
        asc, desc = metric
        safe_asc, safe_desc = safe_metric if safe_metric else (None, None)

        # Maintain original ascender/descender ratio
        ascender_ratio = asc / (asc - desc)  # type: ignore
        # Calculate target total height
        target_total_height = int(round(factor * (asc - desc)))

        # Calculate new metrics
        new_ascender = int(round(target_total_height * ascender_ratio))
        new_descender = new_ascender - target_total_height

        print(f"Change vertical metric to [{new_ascender}, {new_descender}]")

        # Apply changes to hhea table
        hhea.ascent = new_ascender  # type: ignore
        hhea.descent = new_descender  # type: ignore
        os2.usWinAscent = new_ascender  # type: ignore
        os2.usWinDescent = -new_descender  # type: ignore

        # Use safe metrics if provided, otherwise use calculated metrics
        if safe_asc is not None and safe_desc is not None:
            os2.sTypoAscender = safe_asc  # type: ignore
            os2.sTypoDescender = safe_desc  # type: ignore
    else:
        hhea.ascent = int(hhea.ascent * factor)  # type: ignore
        hhea.descent = int(hhea.descent * factor)  # type: ignore
        os2.sTypoAscender = int(os2.sTypoAscender * factor)  # type: ignore
        os2.sTypoDescender = int(os2.sTypoDescender * factor)  # type: ignore
        os2.usWinAscent = int(os2.usWinAscent * factor)  # type: ignore
        os2.usWinDescent = int(os2.usWinDescent * factor)  # type: ignore


def polish(
    font_path: str,
    output_dir: str,
    family_name: str,
    style_name: str,
    line_height_config: Union[float, dict, list[int], None],
) -> str:
    """
    Clean up the font by adjusting line height and updating font names.

    Args:
        font_path: Path to the font file
        output_dir: Output directory for cleaned font
        family_name: Family name of the font
        style_name: Style name of the font
        line_height_config:
            - float: scale factor to apply to existing vertical metric
            - dict: {ascender: <num>, descender: <num>, safe_ascender?: <num>, safe_descender?: <num>}
            - [ascender, descender]: custom vertical metrics
            - None: skip line height adjustment
    """
    font = TTFont(font_path)

    # Handle line height configuration
    if line_height_config is not None:
        if isinstance(line_height_config, (int, float)) and line_height_config != 1:
            # Scale factor: get original vertical metric from font
            change_line_height(font, line_height_config)
        elif isinstance(line_height_config, dict):
            # Object with ascender/descender and optional safe metrics
            ascender = line_height_config.get("top")
            descender = line_height_config.get("bottom")
            safe_ascender = line_height_config.get("safe_top")
            safe_descender = line_height_config.get("safe_bottom")

            if ascender is not None and descender is not None:
                change_line_height(
                    font,
                    1,
                    (ascender, descender),
                    (safe_ascender, safe_descender)
                    if safe_ascender is not None and safe_descender is not None
                    else None,
                )
            else:
                raise ValueError(
                    "line_height object must contain 'ascender' and 'descender' fields"
                )
        elif isinstance(line_height_config, list) and len(line_height_config) == 2:
            # Custom [ascender, descender] values
            change_line_height(
                font,
                1,
                (line_height_config[0], line_height_config[1]),
                (line_height_config[0], line_height_config[1]),
            )

    auto_xheight_capheight(font)

    postscript_name = f"{family_name.replace(' ', '')}-{style_name}"
    style_with_prefix_space, style_in_2, style_in_17, is_skip_subfamily, is_italic = (
        parse_style_name(
            style_name_compact=style_name,
        )
    )
    version = "1.000"
    font["name"] = table__n_a_m_e()
    update_font_names(
        font=font,
        family_name=family_name + style_with_prefix_space,
        style_name=style_in_2,
        full_name=f"{family_name} {style_in_17}",
        version_str=version,
        postscript_name=postscript_name,
        unique_identifier=f"{version};SUBF;{postscript_name};",
        is_skip_subfamily=is_skip_subfamily,
        preferred_family_name=family_name,
        preferred_style_name=style_in_17,
    )

    set_font_name(font, ":P", 0)
    prod_path = joinPaths(output_dir, f"{postscript_name}.ttf")
    font.save(prod_path)

    return prod_path
