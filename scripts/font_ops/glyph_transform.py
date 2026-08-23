from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from fontTools.misc.transform import Transform
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from ufo2ft.filters import BaseFilter

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from ufoLib2 import Font as UFOFont

    from scripts.font_ops.fonttools import TTFont

# Type aliases
Coordinate = tuple[float, float]


@dataclass(frozen=True)
class GlyphWidthScaleParams:
    scale_x: float
    scale_y: float
    match_width: int
    target_width: int
    translate_x: float = 0.0


def reduce_glyph_side_bearings(
    font: TTFont,
    glyph_names: Iterable[str],
    width_mapping: Mapping[int, int],
) -> None:
    """Reduce advances symmetrically without scaling glyph outlines."""
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    target_widths = {
        glyph_name: width_mapping[advance]
        for glyph_name in glyph_names
        if glyph_name in hmtx.metrics
        and (advance := hmtx.metrics[glyph_name][0]) in width_mapping
        and width_mapping[advance] != advance
    }

    for glyph_name, target_width in target_widths.items():
        glyph = glyf[glyph_name]
        advance, lsb = hmtx.metrics[glyph_name]
        shift_x = round((target_width - advance) / 2)

        if glyph.isComposite():
            for component in glyph.components:
                if component.glyphName in target_widths:
                    continue
                if not hasattr(component, "x"):
                    raise ValueError(
                        "Cannot adjust point-aligned composite side bearings: "
                        f"{glyph_name}"
                    )
                component.x += shift_x
        elif glyph.numberOfContours > 0:
            glyph.coordinates.translate((shift_x, 0))
            glyph.coordinates.toInt()
            glyph.recalcBounds(glyf)

        hmtx.metrics[glyph_name] = (target_width, lsb + shift_x)

    for glyph_name in target_widths:
        glyph = glyf[glyph_name]
        if glyph.isComposite():
            glyph.recalcBounds(glyf)

    if "hhea" in font:
        font.table("hhea").advanceWidthMax = max(
            advance for advance, _ in hmtx.metrics.values()
        )


def _calculate_normal(
    prev_point: Coordinate, current: Coordinate, next_point: Coordinate
) -> Coordinate:
    """Calculate the normalized miter vector (bisecting normal) at a vertex."""
    # Input vectors
    dx_in, dy_in = current[0] - prev_point[0], current[1] - prev_point[1]
    dx_out, dy_out = next_point[0] - current[0], next_point[1] - current[1]

    # Perpendicular normals (rotated 90 degrees counter-clockwise)
    nx_in, ny_in = -dy_in, dx_in
    nx_out, ny_out = -dy_out, dx_out

    # Average vector
    vx, vy = (nx_in + nx_out) / 2, (ny_in + ny_out) / 2

    # Normalize using hypot (faster/cleaner than sqrt(x**2 + y**2))
    length = math.hypot(vx, vy)

    return (vx / length, vy / length) if length > 0 else (0.0, 0.0)


def _apply_smart_thicken(coords: list[Coordinate], strength: float) -> list[Coordinate]:
    """
    Apply intelligent thickening to a specific contour.
    internal logic for _process_glyph_geometry.
    """
    n = len(coords)
    if n < 3:
        return list(coords)

    # Calculate bounds for this specific contour to determine relative thickness
    x_vals = [p[0] for p in coords]
    y_vals = [p[1] for p in coords]
    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = min(y_vals), max(y_vals)
    width, height = x_max - x_min, y_max - y_min

    if width == 0 or height == 0:
        return list(coords)

    # Heuristic: Thicken less near the center, more near edges
    max_expansion = min(width, height) * 0.3 * abs(strength)
    center_x, center_y = (x_min + x_max) / 2, (y_min + y_max) / 2

    # Bounds for clamping (prevent points from exploding too far out)
    clamp_pad_x, clamp_pad_y = width * 0.1, height * 0.1
    c_x_min, c_x_max = x_min - clamp_pad_x, x_max + clamp_pad_x
    c_y_min, c_y_max = y_min - clamp_pad_y, y_max + clamp_pad_y

    new_coords = []

    f_coords = list(coords)

    for i in range(n):
        prev_p = f_coords[i - 1]
        curr_p = f_coords[i]
        next_p = f_coords[(i + 1) % n]

        normal = _calculate_normal(prev_p, curr_p, next_p)

        # Distance from center factor (0.0 at center, 1.0 at edge ellipse)
        # Using simple ellipse distance approximation
        dx_norm = (curr_p[0] - center_x) / width
        dy_norm = (curr_p[1] - center_y) / height
        # Note: 2.0 factor because width is diameter, we want radius distance
        center_dist = math.hypot(dx_norm, dy_norm) * 2.0

        # Expansion fades out towards the center
        expansion = max_expansion * max(0.0, (1.0 - 0.5 * center_dist))
        if strength < 0:
            expansion = -expansion

        # Apply
        nx = curr_p[0] + expansion * normal[0]
        ny = curr_p[1] + expansion * normal[1]

        # Clamp
        nx = max(c_x_min, min(c_x_max, nx))
        ny = max(c_y_min, min(c_y_max, ny))

        new_coords.append((nx, ny))

    return new_coords


def _process_glyph_geometry(
    glyph: Glyph,
    glyf_table: Any,
    scale_x: float,
    scale_y: float,
    thicken_strength: float = 0.0,
    translate_x: float = 0.0,
) -> int:
    """
    Shared core logic to transform a glyph.
    Handles scaling, composite offsets, thickening, and centering.

    Returns:
        The new Left Side Bearing (LSB) or xMin.
    """
    # 1. Handle Composite Glyphs (References to other glyphs)
    if glyph.isComposite():
        for component in glyph.components:
            # Scale the offset position (x)
            if hasattr(component, "x"):
                component.x = round(component.x * scale_x)

        # Composites need bounds recalc after component shift
        glyph.recalcBounds(glyf_table)
        return glyph.xMin if hasattr(glyph, "xMin") else 0

    # 2. Handle Empty Glyphs (Space, etc)
    if glyph.numberOfContours == 0:
        return 0

    # 3. Handle Simple Glyphs (Coordinate scaling)
    # Scale in-place
    glyph.coordinates.scale((scale_x, scale_y))

    if translate_x != 0:
        glyph.coordinates.translate((translate_x, 0))

    # 4. Apply Smart Thickening (if requested)
    # We only thicken if scaling down usually, or explicit request
    if thicken_strength != 0 and hasattr(glyph, "endPtsOfContours"):
        new_coords = []
        start = 0

        # Iterate over contours defined by endpoints
        for end in glyph.endPtsOfContours:
            contour: Any = glyph.coordinates[start : end + 1]
            # Process contour
            thickened = _apply_smart_thicken(contour, thicken_strength)
            new_coords.extend(thickened)
            start = end + 1

        # Write back to glyph
        glyph.coordinates = GlyphCoordinates(new_coords)

    # 6. Final cleanup
    glyph.coordinates.toInt()  # Ensure integer coordinates for TTF
    glyph.recalcBounds(glyf_table)

    return glyph.xMin


def _change_glyph_width(
    glyf: Any,
    hmtx: Any,
    glyph_name: str,
    params: GlyphWidthScaleParams,
) -> None:
    """
    Global font resizer. Scales target glyphs horizontally and applies
    smart thickening to counteract the "squashed" look.
    """
    if glyph_name not in glyf:
        return

    # Update Metrics (hmtx)
    old_width, old_lsb = hmtx[glyph_name]

    if old_width == params.match_width:
        new_width = params.target_width
    elif old_width == 0:
        # Scale zero-width combining marks, keep width at 0
        new_lsb = _process_glyph_geometry(
            glyph=glyf[glyph_name],
            glyf_table=glyf,
            scale_x=params.scale_x,
            scale_y=params.scale_y,
            thicken_strength=0.0,
            translate_x=0.0,
        )
        hmtx[glyph_name] = (0, new_lsb)
        return
    else:
        return

    # Update Glyph Geometry
    new_lsb = _process_glyph_geometry(
        glyph=glyf[glyph_name],
        glyf_table=glyf,
        scale_x=params.scale_x,
        scale_y=params.scale_y,
        # Heuristic: If we compress the font (scale < 1), lines get thin.
        # We add weight back based on how much we squeezed.
        thicken_strength=(1 - params.scale_x) / 3,
        translate_x=params.translate_x,
    )

    # If the glyph was empty or composite, new_lsb comes from calculation
    # or scaling the old lsb
    if glyf[glyph_name].numberOfContours == 0 and not glyf[glyph_name].isComposite():
        final_lsb = round(old_lsb * params.scale_x)
    else:
        final_lsb = new_lsb

    hmtx[glyph_name] = (new_width, final_lsb)


def smart_change_width(
    font: TTFont,
    target_width: int,
    original_ref_width: int,
    also_scale_y: bool = False,
    scale_zero_width: bool = True,
) -> None:
    """
    Global font resizer. Scales all glyphs horizontally and applies
    smart thickening to counteract the "squashed" look.

    For non-CN glyphs in the build process.
    """
    if original_ref_width <= 0:
        raise ValueError("Original reference width must be positive")

    font["hhea"].advanceWidthMax = target_width
    hmtx: Any = font["hmtx"]
    glyf: Any = font["glyf"]

    scale_factor = target_width / original_ref_width
    params = GlyphWidthScaleParams(
        scale_x=scale_factor,
        scale_y=scale_factor if also_scale_y else 1.0,
        match_width=original_ref_width,
        target_width=target_width,
    )
    composites: list[str] = []

    for glyph_name in font.getGlyphOrder():
        if not scale_zero_width and font["hmtx"][glyph_name][0] == 0:
            continue
        _change_glyph_width(
            glyf=glyf,
            hmtx=hmtx,
            glyph_name=glyph_name,
            params=params,
        )
        if glyf[glyph_name].isComposite():
            composites.append(glyph_name)

    # Recalculate composite bounds after all components (including combining
    # marks that appear later in glyph order) have been scaled
    for glyph_name in composites:
        glyph = glyf[glyph_name]
        glyph.recalcBounds(glyf)
        new_lsb = glyph.xMin if hasattr(glyph, "xMin") else 0
        hmtx[glyph_name] = (hmtx[glyph_name][0], new_lsb)


class SmartWidthThickenFilter(BaseFilter):
    """Apply Maple's width-aware thickening after outline conversion."""

    _args = ("target_width", "original_ref_width")

    def start(self) -> None:
        if self.options.original_ref_width <= 0:
            raise ValueError("Original reference width must be positive")
        if self.options.target_width <= 0:
            raise ValueError("Target width must be positive")
        self._strength = (
            1 - self.options.target_width / self.options.original_ref_width
        ) / 3

    def filter(self, glyph: Any) -> bool:
        if glyph.width != self.options.target_width or not len(glyph):
            return False

        for contour in glyph:
            transformed = _apply_smart_thicken(
                [(point.x, point.y) for point in contour],
                self._strength,
            )
            for point, (x, y) in zip(contour, transformed, strict=True):
                point.x = x
                point.y = y
        return True


def scale_ufo_width(
    font: UFOFont,
    target_width: int,
    original_ref_width: int,
) -> None:
    """Scale UFO geometry without changing cross-master contour compatibility."""
    if original_ref_width <= 0:
        raise ValueError("Original reference width must be positive")

    scale_x = target_width / original_ref_width

    for glyph in font:
        if glyph.width not in {0, original_ref_width}:
            continue

        for contour in glyph:
            for point in contour:
                point.x *= scale_x

        for component in glyph.components:
            transform = component.transformation
            component.transformation = Transform(
                transform.xx,
                transform.xy,
                transform.yx,
                transform.yy,
                transform.dx * scale_x,
                transform.dy,
            )

        for anchor in glyph.anchors:
            anchor.x *= scale_x

        if glyph.width == original_ref_width:
            glyph.width = target_width


def change_glyph_width_or_scale(
    font: TTFont,
    match_width: int,
    target_width: int,
    scale_factor: tuple[float, float],
    special_names: list[str] | None = None,
):
    """
    Adjusts the width or scales the glyphs in a font based on the specified parameters.

    This function modifies the glyphs in the given font by either changing their width
    or scaling their coordinates. It also updates the horizontal metrics and bounding
    box values accordingly.

    For CN glyphs in the build process.

    Args:
        font (TTFont): The font object to be modified.
        match_width (int): The width of glyphs to match for modification.
        target_width (int): The new width to set for matching glyphs.
        scale_factor (tuple[float, float]): A tuple containing the scaling factors for
            width and height (scale_w, scale_h).
        special_names (list[str], optional): A list of glyph names that require special
            handling instead of trim whitespace only. Defaults to an empty list.

    Notes:
        - Glyphs with a width that does not match `match_width` are skipped.
        - Glyphs with zero contours are only updated in the horizontal metrics.
        - The scaling and translation are applied to the glyph coordinates, and the
          bounding box values are recalculated.
    """
    special_names = special_names or []
    font["hhea"].advanceWidthMax = target_width
    glyf: Any = font["glyf"]
    hmtx: Any = font["hmtx"]
    factor = target_width / match_width
    composites: list[str] = []
    for glyph_name in font.getGlyphOrder():
        if glyph_name in special_names:
            _change_special_cjk_glyph(
                glyf, hmtx, glyph_name, factor, match_width, target_width
            )
            if glyf[glyph_name].isComposite():
                composites.append(glyph_name)
            continue

        glyph = glyf[glyph_name]
        width, lsb = hmtx[glyph_name]
        if width == 0:
            _scale_zero_width_cjk_glyph(glyph, glyf, hmtx, glyph_name, scale_factor)
            continue
        if width != match_width:
            continue
        if glyph.isComposite():
            composites.append(glyph_name)
        if glyph.numberOfContours == 0:
            hmtx[glyph_name] = (target_width, lsb)
            continue
        _scale_simple_cjk_glyph(glyph, hmtx, glyph_name, scale_factor, target_width)

    _recalculate_cjk_composite_metrics(glyf, hmtx, composites)


def _change_special_cjk_glyph(
    glyf: Any,
    hmtx: Any,
    glyph_name: str,
    factor: float,
    match_width: int,
    target_width: int,
) -> None:
    translate_x = 0.0
    if "quote" in glyph_name:
        if "right" in glyph_name:
            translate_x = target_width * 0.15
        elif "left" in glyph_name:
            translate_x = target_width * -0.15
    _change_glyph_width(
        glyf=glyf,
        hmtx=hmtx,
        glyph_name=glyph_name,
        params=GlyphWidthScaleParams(
            scale_x=factor,
            scale_y=1.0,
            match_width=match_width,
            target_width=target_width,
            translate_x=translate_x,
        ),
    )


def _scale_zero_width_cjk_glyph(
    glyph: Glyph,
    glyf: Any,
    hmtx: Any,
    glyph_name: str,
    scale_factor: tuple[float, float],
) -> None:
    scale_w, scale_h = scale_factor
    _process_glyph_geometry(
        glyph=glyph,
        glyf_table=glyf,
        scale_x=scale_w,
        scale_y=scale_h,
        thicken_strength=0.0,
    )
    _, lsb = hmtx[glyph_name]
    new_lsb = glyph.xMin if hasattr(glyph, "xMin") else lsb
    hmtx[glyph_name] = (0, new_lsb)


def _scale_simple_cjk_glyph(
    glyph: Glyph,
    hmtx: Any,
    glyph_name: str,
    scale_factor: tuple[float, float],
    target_width: int,
) -> None:
    width, lsb = hmtx[glyph_name]
    scale_w, scale_h = scale_factor
    glyph.coordinates.scale((scale_w, scale_h))
    glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax = glyph.coordinates.calcIntBounds()
    delta = (target_width - round(width * scale_w)) / 2
    glyph.coordinates.translate((delta, 0))
    glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax = glyph.coordinates.calcIntBounds()
    hmtx[glyph_name] = (target_width, lsb + round(delta))


def _recalculate_cjk_composite_metrics(
    glyf: Any, hmtx: Any, composites: list[str]
) -> None:
    """Refresh composite bounds after their referenced glyphs have been changed."""
    for glyph_name in composites:
        glyph = glyf[glyph_name]
        glyph.recalcBounds(glyf)
        new_lsb = glyph.xMin if hasattr(glyph, "xMin") else 0
        hmtx[glyph_name] = (hmtx[glyph_name][0], new_lsb)
