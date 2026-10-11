# `build.py` CLI Reference

This page is generated from the output of `build.py --help` (run with `COLUMNS=80 uv run build.py --help`). Regenerate it whenever a `build.py` flag is added or changed.

Command-line options have a higher priority than options in [`config.json`](../config.json). For explanations of what the options do, see [Build Options](./build-options.md) and [CJK Build](./cjk.md).

```text
usage: build.py [-h] [-v] [-d] [--debug] [-n] [--standard-zero]
                [--legacy-thin-weight-class] [--feat FEAT] [--apply-fea-file]
                [--hinted | --no-hinted] [--liga | --no-liga]
                [--infinite-arrow | --no-infinite-arrow] [--remove-tag-liga]
                [--line-height LINE_HEIGHT] [--width {default,narrow,slim}]
                [--format FORMATS] [--least-styles] [--cache] [--archive]
                [--nf | --no-nf] [--nf-mono] [--nf-propo] [--nf-variable]
                [--font-patcher] [--cjk CJK] [--cjk-variable] [--cjk-narrow]
                [--cjk-scale-factor CJK_SCALE_FACTOR] [--cjk-both]
                [--cjk-hinted | --no-cjk-hinted] [--cn | --no-cn]
                [--cn-narrow] [--cn-scale-factor CN_SCALE_FACTOR] [--cn-both]

Builder and optimizer for Maple Mono

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -d, --dry             Output config and exit
  --debug               Use a fast debug build: add `Debug`, enable debug
                        logging, build Regular/Italic only, and skip
                        OTF/WOFF2/Nerd Font outputs

Feature Options:
  -n, --normal          Use normal preset, just like `JetBrains Mono` with
                        slashed zero
  --standard-zero       Use standard zero semantics: default dotted zero and
                        slashed zero when `zero` is enabled
  --legacy-thin-weight-class
                        Use legacy weight class values (250/275 instead of
                        100/200) for Thin and ExtraLight static fonts to work
                        around GDI fake-bold in JetBrains IDEs on Windows
  --feat FEAT           Enable and freeze the listed features, split by `,`
                        (e.g. `--feat zero,cv01,ss07,ss08`); contextual rules
                        are enabled through `calt`
  --apply-fea-file      Apply matching
                        `sources/features/{regular,italic}{_cn,}.fea` to
                        static and variable fonts
  --hinted              Use hinted font as base font in NF / CJK / NF-CJK
                        (default)
  --no-hinted           Use unhinted font as base font in NF / CJK / NF-CJK
  --liga                Preserve all the ligatures (default)
  --no-liga             Remove all the ligatures
  --infinite-arrow      Add infinite arrow ligature support (default)
  --no-infinite-arrow   Do not add infinite arrow ligature support
  --remove-tag-liga     Remove plain text tag ligatures like `[TODO]`
  --line-height LINE_HEIGHT
                        Scale factor for line height (e.g., 1.1)
  --width {default,narrow,slim}
                        Set glyph width: default (600), narrow (550), slim
                        (500)

Build Options:
  --format FORMATS      Select requested base output formats as a comma-
                        separated list: ttf,otf,woff2; the variable base is
                        always built
  --least-styles        Only build Regular / Bold / Italic / BoldItalic style
  --cache               Reuse valid cached pipeline stages under `fonts/` and
                        preserve existing unrelated outputs
  --archive             Archive each existing non-JSON output directory with
                        config and license

Nerd Font Options:
  --nf, --nerd-font     Build Nerd-Font version (default)
  --no-nf, --no-nerd-font
                        Do not build the Nerd-Font version
  --nf-mono             Make Nerd Font icons' width fixed
  --nf-propo            Make Nerd Font icons' width variable, override `--nf-
                        mono`
  --nf-variable         Build Nerd Font as a variable font
  --font-patcher        Force the use of Nerd Font Patcher to build NF format

CJK Options:
  --cjk CJK             Build Maple Mono + CJK extended fonts for locales: cn,
                        jp, tc, kr. Repeat or use comma-separated values.
  --cjk-variable        Persist CJK-extended output as merged variable fonts.
  --cjk-narrow          Apply narrow CJK spacing to the selected locales.
  --cjk-scale-factor CJK_SCALE_FACTOR
                        Scale factor for selected CJK locales. Format:
                        <factor> or <width_factor>,<height_factor>.
  --cjk-both            When Nerd Font is enabled, build both NF CJK and non-
                        NF CJK outputs.
  --cjk-hinted          Auto-hint final static CJK fonts.
  --no-cjk-hinted       Do not auto-hint final static CJK fonts (default).

Deprecated CN Options:
  --cn                  Deprecated alias for `--cjk cn`.
  --no-cn               Deprecated alias for removing `cn` from the selected
                        CJK locales.
  --cn-narrow           Deprecated alias for `--cjk-narrow` when targeting
                        `cn`.
  --cn-scale-factor CN_SCALE_FACTOR
                        Deprecated alias for `--cjk-scale-factor` when
                        targeting `cn`.
  --cn-both             Deprecated alias for `--cjk-both`.
```
