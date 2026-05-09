#!/usr/bin/env python
import sys
import json

try:
    import fontforge  # type: ignore
except ImportError:
    print(
        "Cannot import fontforge module. Please ensure FontForge is installed "
        "and use its Python environment to run this script."
    )
    sys.exit(1)


def merge_fonts(config_path: str, output_path: str) -> None:
    """
    Merge fonts based on config file.

    This script handles ALL FontForge operations:
    - Opening fonts
    - Applying width scales
    - Normalizing UPEM
    - Merging fonts
    - Generating output

    Config format:
    {
        "base_font": "/path/to/base.ttf",
        "overrides": [
            {"path": "/path/to/override1.ttf", "width_scale": 1.06},
            {"path": "/path/to/override2.ttf", "width_scale": null}
        ]
    }

    Args:
        config_path: Path to JSON config file
        output_path: Path for merged font output
    """
    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    base_font_path = config["base_font"]
    overrides = config["overrides"]

    print("FontForge merger started")
    print(f"  Base font: {base_font_path}")
    print(f"  Overrides: {len(overrides)}")

    # Open base font
    base_font = fontforge.open(base_font_path)
    upem_base = base_font.em
    print(f"  Base UPEM: {upem_base}")

    # Merge each override font
    for idx, override in enumerate(overrides):
        override_path = override["path"]
        width_scale = override.get("width_scale")

        print(f"\nProcessing override {idx + 1}/{len(overrides)}: {override_path}")

        # Open override font
        override_font = fontforge.open(override_path)
        upem_override = override_font.em

        # Normalize UPEM to match base font
        if upem_base != upem_override:
            scale = upem_base / upem_override
            print(
                f"  Normalizing UPEM: {upem_override} -> {upem_base} (scale: {scale:.4f})"
            )
            override_font.transform((scale, 0, 0, scale, 0, 0))
            override_font.em = upem_base

        # Apply width scale if specified
        if width_scale is not None:
            print(f"  Applying width scale: {width_scale}")

        for g in override_font.glyphs():
            uni = g.unicode
            if uni != -1:
                try:
                    base_font.removeGlyph(uni)
                except Exception:
                    continue
            if width_scale is not None:
                g.width = int(g.width * width_scale)

        # Merge into base font
        print("  Merging into base font...")
        base_font.mergeFonts(override_font)
        override_font.close()

    # Generate output
    print(f"\nGenerating output: {output_path}")
    base_font.generate(output_path)
    base_font.close()

    print("FontForge merger completed successfully")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: /path/to/fontforge -script merger.py <config_path> <output_path>")
        sys.exit(1)

    config_path = sys.argv[1]
    output_path = sys.argv[2]
    merge_fonts(config_path, output_path)
