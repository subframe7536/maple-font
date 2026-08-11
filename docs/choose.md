# Naming and Choosing Fonts

Maple Mono release packages are split by font features, character width, font format, and character set. The examples below use the default base name `MapleMono`; if you customize the base name, the other components follow the same rules.

## Quick Selection

| Use case                     | Recommended choice                    | Why                                                                                                    |
| ---------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| General coding               | `TTF` or `OTF`                        | TTF has the broadest compatibility; OTF or unhinted TTF can be preferable on high-resolution displays. |
| Low-resolution displays      | `TTF-AutoHint`                        | Autohinting improves small-size TrueType rasterization.                                                |
| Web pages                    | `WOFF2`                               | The compressed format is smaller and works well with CSS font loading.                                 |
| Terminal icons               | `NF`, `NFMono`, or `NFPropo`           | Includes Nerd Font icons; choose default, fixed-width, or proportional icon spacing for the terminal.   |
| Icons and CJK together       | `NF-CN`, `NF-TC`, `NF-JP`, or `NF-KR` | Includes Nerd Font icons and the selected CJK locale.                                                  |
| Continuous weight adjustment | `Variable`                            | Use the `wght` axis to select a weight without installing multiple static files.                       |

## Filename Components

### Features and Character Widths

Filename components are combined in this order: base name, feature preset, width, and style. Feature and width suffixes are compact, so they are not separated by additional hyphens.

| Configuration                      | Suffix     | Example family name    | Description                                                                                                                  |
| ---------------------------------- | ---------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Default ligatures                  | None       | `Maple Mono`           | The default glyph design and ligature behavior.                                                                              |
| Ligatures disabled                 | `NL`       | `Maple Mono NL`        | Disables the default ligatures; for example, `MapleMonoNL-Regular.ttf`.                                                      |
| `--normal` preset                  | `Normal`   | `Maple Mono Normal`    | Uses glyph designs closer to common programming fonts; see the [`--normal` preset in README.md](../README.md#normal-preset). |
| `--normal` with ligatures disabled | `NormalNL` | `Maple Mono Normal NL` | Applies both `Normal` and `NL`.                                                                                              |
| Default width                      | None       | `Maple Mono`           | Latin glyph target width is 600.                                                                                             |
| Narrow width                       | `NR`       | `Maple Mono NR`        | The `narrow` mode, with a Latin glyph target width of 550.                                                                   |
| Slim width                         | `SL`       | `Maple Mono SL`        | The `slim` mode, with a Latin glyph target width of 500.                                                                     |

For example, `--normal --no-liga --width narrow` produces `MapleMonoNormalNLNR-Regular.ttf`. Width settings also apply to Variable, NF, and CJK outputs.

### Font Formats

| Format or marker | Example                    | Description                                                                                         |
| ---------------- | -------------------------- | --------------------------------------------------------------------------------------------------- |
| `Variable`       | `MapleMono[wght].ttf`      | A variable font whose weight is controlled through the `wght` axis. Italic files include `-Italic`. |
| `TTF`            | `MapleMono-Regular.ttf`    | A static TrueType font with broad application compatibility.                                        |
| `OTF`            | `MapleMono-Regular.otf`    | A static OpenType font for desktop applications with OpenType support.                              |
| `WOFF2`          | `MapleMono-Regular.woff2`  | A compressed WOFF2 font intended mainly for web pages.                                              |
| `NF`             | `MapleMono-NF-Regular.ttf` | Includes Nerd Font icons; `NF` can also be combined with feature and width suffixes.                |
| `NFMono`         | `MapleMono-NFM-Regular.ttf` | Fixed-width Nerd Font icons; release packages use the `NFMono` label and output directory.           |
| `NFPropo`        | `MapleMono-NFP-Regular.ttf` | Proportional Nerd Font icons; release packages use the `NFPropo` label and output directory.         |

### CJK Character Sets

CJK outputs use a locale suffix. The coverage below follows each built-in locale configuration, including its Unicode ranges and source-font encoding filter. Regular CJK and NF-CJK fonts are written to `fonts/<LOCALE>/` and `fonts/NF-<LOCALE>/`; Variable outputs use the corresponding `Variable-<LOCALE>` and `Variable-NF-<LOCALE>` directories.

| Locale | Real coverage                                                                                                                                                                                                                                                                                                     | Regular CJK example        | NF-CJK example                |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ----------------------------- |
| `CN`   | Simplified Chinese, common Traditional Chinese and Japanese kana; includes CJK radicals, ideographic description characters, Bopomofo, CJK punctuation and symbols, Han ideographs (`U+3400–U+9FFF`), compatibility ideographs, and fullwidth forms. See the [CN configuration](../source/cjk/cn/config-cn.json). | `MapleMono-CN-Regular.ttf` | `MapleMono-NF-CN-Regular.ttf` |
| `TC`   | Traditional Chinese; includes CJK radicals, ideographic description characters, Bopomofo, CJK punctuation and symbols, Han ideographs (`U+3400–U+9FFF`), compatibility ideographs, and fullwidth forms. It does not add Japanese kana. See the [TC configuration](../source/cjk/tc/config-tc.json).               | `MapleMono-TC-Regular.ttf` | `MapleMono-NF-TC-Regular.ttf` |
| `JP`   | Japanese CP932 coverage: Hiragana, Katakana and Katakana Phonetic Extensions, Japanese punctuation and symbols, enclosed CJK characters, and CP932 Kanji. See the [JP configuration](../source/cjk/jp/config-jp.json).                                                                                            | `MapleMono-JP-Regular.ttf` | `MapleMono-NF-JP-Regular.ttf` |
| `KR`   | Korean script coverage: Hangul syllables (`U+AC00–U+D7A3`), Hangul Compatibility Jamo, halfwidth Hangul, Korean punctuation and symbols, plus selected enclosed and unit characters. The KR locale does not add the Han ideograph range. See the [KR configuration](../source/cjk/kr/config-kr.json).             | `MapleMono-KR-Regular.ttf` | `MapleMono-NF-KR-Regular.ttf` |

Locales can be combined with feature and width settings. For example, `--cjk jp --nf --width slim` produces the static file `MapleMonoSL-NF-JP-Regular.ttf`; Mono and Propo custom builds use `NFMono-JP` / `Variable-NFMono-JP` and `NFPropo-JP` / `Variable-NFPropo-JP` directories while preserving the `NFM` and `NFP` internal filename markers. CJK builds are disabled by default; see the [build guide](build.md) for configuration details. Release packages include default NF locales only.

## Hinted and Unhinted Fonts

Hinted fonts include TrueType rasterization instructions and are suited to low-resolution displays and small font sizes. Choose `TTF-AutoHint`, or use the default hinted `NF` and `NF-CJK` outputs.

Unhinted fonts omit those instructions and are suited to high-resolution displays such as modern MacBooks. Choose `OTF`, regular `TTF`, or an `NF` / CJK release package whose name includes `-unhinted`; on low-resolution displays, unhinted fonts may look blurry, misaligned, or uneven in weight.

`-AutoHint` and `-unhinted` identify release packages or output directories; they are not OpenType features. `-AutoHint` is used only for automatically hinted TTF output, and both suffixes are retained for compatibility with existing installation workflows and naming conventions. NFMono and NFPropo release packages are unhinted static outputs; their custom VF and CJK directories are available to local builds but are not published.
