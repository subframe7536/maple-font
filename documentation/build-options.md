# Build Options

Maple Mono provides highly customizable builds. Modify [`config.json`](../config.json) or add command-line arguments to generate the font you need. Command-line options have a higher priority than options in `config.json`.

- For build methods (browser, GitHub Actions, Docker, local), see [Custom Build](./build.md).
- For every command-line flag, see the [`build.py` CLI reference](./cli.md).
- For CJK-specific options, see [CJK Build](./cjk.md).

## Character Width

V8 provides three character-width modes. Change the `"width"` field in [`config.json`](../config.json), or pass `--width <mode>` on the command line.

Available modes:

- default: 600
- narrow: 550
- slim: 500

![Width comparison](../resources/preview-widths.webp)

Width settings also apply to Variable, NF, and CJK outputs. See [Naming and Choosing Fonts](./choose.md#features-and-character-widths) for the resulting file names.

## OpenType Feature Freezing

OpenType features control built-in font variants and ligatures, and are supported by most modern operating systems, browsers, terminals, and editors. Enable or disable them to control ligatures and character styles. See [OpenType Features](./opentype-features.md) for the full list.

Maple Mono provides many fine-grained OpenType features. To reduce configuration effort, builds support three handling modes ([why](https://github.com/subframe7536/maple-font/issues/233#issuecomment-2410170270)), configured per feature in the `"feature_freeze"` field of [`config.json`](../config.json):

1. `enable`: Force these features on without setting `cvXX` / `ssXX` / `zero` in the font feature configuration, similar to default ligatures.
2. `disable`: Remove these features from `cvXX` / `ssXX` / `zero`, so they remain inactive even if enabled manually.
3. `ignore`: Keep the default behavior unchanged.

On the command line, `--feat` enables and freezes the listed features, split by `,` (e.g. `--feat zero,cv01,ss07,ss08`).

The [Playground](https://font.subf.dev/en/playground) "Custom Build" button can also freeze OpenType features in the browser.

## Normal Preset

Maple Mono's default glyph design is distinctive and personalized, which may not suit every taste or use case. The `--normal` build preset provides glyphs similar to `JetBrains Mono` (`0` has a slash in the middle instead of a dot).

![Normal preset](../resources/preview-normal.webp)

Release packages built with this preset use the `Normal` / `NormalNL` names; see [Naming and Choosing Fonts](./choose.md#features-and-character-widths).

## Custom OpenType Features

Most fonts do not support custom OpenType features, while Maple Mono supports defining them programmatically.

By default, the Python modules in [`scripts/feature/`](../scripts/feature) generate the OpenType feature code loaded during the build. Modify those modules to adjust behavior or customize labels. To edit `.fea` source files directly, pass `--apply-fea-file` to `build.py`; the build script will load [`sources/features/{regular,italic}{_cn,}.fea`](../sources/features).

See the [OpenType feature generation guide](../scripts/feature/README.md) for implementation details.

## Ligatures and Tag Ligatures

All ligatures are preserved by default (`--liga`). Pass `--no-liga` to remove all the ligatures; release packages built this way use the `NL` suffix. Pass `--remove-tag-liga`, or set `"remove_tag_liga": true` in `config.json`, to remove plain text tag ligatures like `[TODO]`.

## Infinite Arrow Ligatures

Inspired by Fira Code and Cascadia Code, Maple Mono supports infinite arrow ligatures.

Infinite arrow support is enabled by default during builds. Set `"infinite_arrow": false` in `config.json`, or pass `--no-infinite-arrow` on the command line, to disable it. Pass `--infinite-arrow` to override a disabled configuration. Discuss issues in [#508](https://github.com/subframe7536/maple-font/issues/508).

![Infinite arrow ligatures](../resources/preview-infinite-arrows.webp)

## Standard Zero Feature

By default, `0` uses the slashed style, and enabling `zero` displays the dotted form. Use `--standard-zero` (or `"standard_zero": true` in `config.json`) to restore the standard OpenType semantics: the default `0` is dotted, and enabling `zero` displays the slashed form.

## Custom Line Height

Maple Mono's default line height is `1`. Change the `"line_height"` field in [`config.json`](../config.json), or pass `--line-height <value>` on the command line. The final line height is calculated as `(ascender - descender) * line_height`.

## Custom Unicode Mapping

If Maple Mono lacks a Unicode code point, the corresponding character may not render. Customize the mapping through the `"codepoint_alias"` field in [`config.json`](../config.json).

For example, map existing characters to other Unicode code points:

```json
{
  "codepoint_alias": {
    "U+E000": "U+E001",
    "U+E002": "U+E003"
  }
}
```

## Custom Weight Mapping

Change the weight of static fonts through the `"weight_mapping"` field in `config.json`.

For example, make the regular weight slightly thinner by lowering `"weight_mapping.regular"` from 400 to 350:

```json
{
  "weight_mapping": {
    "thin": 100,
    "extralight": 200,
    "light": 300,
    "regular": 350,
    "semibold": 500,
    "medium": 600,
    "bold": 700,
    "extrabold": 800
  }
}
```

### Legacy Thin Weight Class

Pass `--legacy-thin-weight-class`, or set `"legacy_thin_weight_class": true` in `config.json`, to use legacy weight class values (250/275 instead of 100/200) for Thin and ExtraLight static fonts. This works around GDI fake-bold in JetBrains IDEs on Windows.

## Custom Nerd Font Configuration

Maple Mono includes Nerd Font icons and follows its naming rules. By default, each icon uses a one-Latin-character advance width, while its glyph width may vary.

- To make icons occupy one Latin-character width (Nerd Font Mono), set `"nerd_font.mono": true` in `config.json`, or add `--nf-mono` to the build arguments.
- To use variable-width icons (Nerd Font Propo), set `"nerd_font.propo": true` in `config.json`, or add `--nf-propo` to the build arguments.
- To skip the Nerd Font version, pass `--no-nf`. To build Nerd Font as a variable font, pass `--nf-variable`.

To customize `font-patcher` arguments, install `fontforge` (and possibly `python3-fontforge`). You may also need to change `"nerd_font.extra_args"` in [config.json](../config.json). Pass `--font-patcher` to force the use of Nerd Font Patcher.

![Nerd Font spacing modes](../resources/preview-nerd-fonts.webp)

### Argument Parsing Rules

Default arguments: `-l --careful --outputdir dir`

- When `"nerd_font.propo"` is `true`, add `--variable-width-glyphs`.
- When `"nerd_font.mono"` is `true`, add `--mono`.

## Hinting

`--hinted` (default) uses the hinted font as the base font in NF / CJK / NF-CJK outputs; `--no-hinted` uses the unhinted font instead. The equivalent `config.json` field is `"use_hinted"`. See [Hinted and Unhinted Fonts](./choose.md#hinted-and-unhinted-fonts) for which one to choose.

## Output Formats

`--format` selects the requested base output formats as a comma-separated list (`ttf,otf,woff2`); the variable base is always built. `--least-styles` only builds the Regular / Bold / Italic / BoldItalic styles. See the [CLI reference](./cli.md) for cache, archive, and debug options.
