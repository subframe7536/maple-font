# DEPRECATED

## merge_font

Short utilities for merging and polishing TrueType/OpenType fonts used by the build tasks.

### Requirements

- Python packages: `foundrytools`.

### Usage

From Python build tasks:

```sh
uv run task.py merge
```

If config file not exists, it will be auto created. Example:

```json
{
  "family_name": "Maple Mono",
  "output_dir": "./fonts",
  "line_height": [850, -200],
  "instances": {
    "regular": [
      "base_font.ttf",
      {
        "enable": true,
        "path": "override_font.ttf",
        "unicode_range": ["U+0030-0039", "U+2190-2199"],
        "width_scale": 1.06,
        "axes": {"wght": 400, "wdth": 100}
      }
    ],
    "bold": [
      "/path/to/static/font.ttf",
      {
        "path": "/path/to/variable/font.ttf",
        "axes": {"wght": 700, "wdth": 110},
        "width_scale": 0.98,
        "unicode_range": ["U+4E00-9FFF"]
      },
      {
        "enable": false,
        "path": "disabled_font.ttf"
      }
    ]
  }
}
```

### Configuration Options

- **family_name**: The family name of the resulting font family (required)
- **output_dir**: Output directory for generated fonts (required)
- **line_height**: Line height config, formats:
  - Scaling factor (number, e.g. `1.02`)
  - Simple `[top, bottom]` (e.g. `[950, -200]`)
  - Full config `{ "top": num, "bottom": num, "safe_top": num, "safe_bottom": num }`
- **instances**: Object mapping style names to font configuration arrays

Each instance style contains an array where:
- First element is the base font (string path or object with axes)
- Subsequent elements are override fonts with configuration options

### Override Font Configuration

Each override font supports:
- **path**: Path to the override font file (required)
- **enable**: Enable/disable this override (default: true)
- **unicode_range**: Array of Unicode ranges to include (e.g., `["U+0030-0039"]` for digits)
- **width_scale**: Scale factor for glyph widths (e.g., 1.06 makes 6% wider)
- **axes**: Variable font axis values for instantiation

### Features

- **Multiple Overrides**: Merge base font with unlimited override fonts
- **Unicode Range Filtering**: Subset overrides to specific Unicode ranges
- **Width Scaling**: Adjust glyph proportions with configurable scaling
- **Custom Vertical Metrics**: Set custom ascender/descender or scale existing line height
- **Enable/Disable Overrides**: Toggle individual override fonts via configuration
- **Variable Font Support**: Instantiate variable fonts with custom axis values

All fonts for a given style are merged in a single FontForge process, using the first font as the base.