# TODO

## Ligatures

- [x] `[erro]` / `[dbug]` / `[crit]` / `[alert]` / `[success]` / `[tracing]` / `[critical]` #767 #777
- [x] add missing `>:` / `:>:` / `:<:`
- [ ] https://lobste.rs/s/ahca9t/maple_mono_open_source_monospace_font#c_un8dnc

## Character Variant

- [x] cv12 / cv45: `u` without tail, like JetBrains Mono #785
- [x] cv67: longer bar (`|`), top + 50, bottom - 100 #732
  - [x] relative ligatures
- [x] ss12 / ss13: like monaspace cv12 / cv13 #782
- [x] cv68: `===` become 2 bars

## Unicode

- [x] full math glyphs U+2200–U+22FF, reference from Julia Mono's math symbols #709
- [x] from claude code:
  - [x] spinner: U+273B, U+2605, U+273D, U+2733, U+2722, U+2736, U+2726
  - [x] progress: U+25D0-25D3
  - [x] figures: U+21BB, U+21AF
  - [x] play/pause: U+23F5, U+23FA, U+23F8
  - [x] alarm/symbol: U+29C9, U+2694, U+2691, U+26F6, U+26DD, U+2764
- [x] `─→` should horizonly aligned
- [x] u+266a, u+2303, u+23ce #762
- [x] chess symbols #594
- [x] "♦", "♠", "♥", "♣" #771
- [x] U+2C6D, U+0E3F #772
- [x] U+21E0-U+21E3 #740
- [x] make u+E0B4 / u+E0B6 more rounded #780
- [x] fill ALL sub and sup glyphs, fix wrong unicodes #789
  - [x] pass verify_sup_sub.md visual page
- [x] more decorators #792 : U+2AA7, U+2A7A, U+2ABC, U+2AF8, U+15D9, U+15D3, U+1440, U+27A4, U+1368, U+1360, U+0FC7, U+232C, U+23E3, U+2732, U+2734, U+2735, U+2737, U+2738, U+2739, U+273A, U+273C, U+273E, U+273F, U+2740, U+2741, U+2742, U+2743, U+2744, U+2745, U+2746, U+2747, U+2748, U+2749, U+274A, U+274B, U+2626, U+2628, U+2670, U+2671, U+271D, U+2629, U+05D0
- [x] `🄯` (copyleft)
- [x] validate u+229e and other math symbols

### CN

- [x] 易经六十四卦符号 #580

## Build

- [x] cleanup
- [x] add more details in mermaid dataflow graph
- [x] customizable locale name
- [x] fix cjk base font load priority regression: local cache > download from github release > instantiate from variable font > error
  - [x] stabilize directory hash with config-derived static hash files
- [x] stabilize cjk sha
- [x] support object-based CJK source downloads, including direct files and a selected file inside 7z archives
- [x] review cjk base font cache invalidation and download logic, and add more tests

### Web

- [ ] use `document.fonts.ready` to detect font loaded in web page
- [ ] add cn/tc/jp/kr locale support in web page
- [ ] try to migrate to https://jsdmirror.com for fonttools load
- [ ] extend build in browser support:
  - [ ] support loading fea file, or maybe also python script?
  - [ ] cjk variable font instantiate?
  - [ ] full config support instead of just freezing features

## CJK

- [x] try not to convert CFF2 to glyf, directly use CFF2 to merge variable font and generate ttf when instantiating
- [x] WenYuanRoundedSCVF as SC part
- [x] ChironGoRoundTCVF as TC + KR (range should reference from Pretendard) part
  - Maple and ChironGoRoundTCVF weight mapping:
    - 100 -> 250
    - 400 -> 620
    - 800 -> 900
- [x] Resource Han Sans JP as JP part
- [x] cjk meta table language correction
- [x] figure out why maplemono-nf-tc-vf size is too large
- [x] freeze `cv99` for tc. (via a new `freeze_feature` option in `config-<locale>.json`)
- [ ] cjk hint effect test

## Google Fonts QA

`uv run fontbakery check-googlefonts fonts/variable/*.ttf` to check variable fonts, and `uv run fontbakery check-googlefonts fonts/*.ttf` to check static fonts.

- [x] verify glyphs in UFO
- [x] unify curve type, fix rotate issues
- [x] decompose glyphs that have different font weight(UFO does not support)
- [x] fix `fsType` to 0 for all fonts

### FAIL revalidation

The following items are based on `uv run fontbakery check-googlefonts fonts/variable/*.ttf`.
At baseline, each check failed for both the regular and italic variable fonts; the
checkboxes below reflect the latest revalidation.

- [x] `case_mapping` — add the missing case-swapping counterparts for U+01D5/U+01D7/U+01D9/U+01DB, U+0186, U+A7AE, U+01A9, U+01B1, U+0245, U+01B7, U+03F2, U+1F41, and U+1F64.
- [ ] `family/win_ascent_and_descent` — set `OS/2.usWinAscent` to at least 1120 and `OS/2.usWinDescent` to at least 400 after confirming the intended line-spacing behavior.
- [x] `legacy_accents` — remove the GDEF mark class assignment from `dieresis`, `macron`, `acute`, `cedilla`, `circumflex`, `caron`, `breve`, `dotaccent`, `ring`, `ogonek`, `tilde`, and `hungarumlaut`.
- [x] `googlefonts/glyphsets/shape_languages` — add the mandatory missing Cyrillic characters required by `GF_Phonetics_SinoExt`, including Bashkir, Chuvash, Azerbaijani Cyrillic, Kabardian/Adyghe/Dargwa/Lezghian/Ingush, Chechen, Avaric, Mari, and Sakha.
- [ ] `dotted_circle` — add dotted-circle attachment anchors for `acutecomb`, `dotbelowcomb`, `gravecomb`, `hookabovecomb`, `tildecomb`, U+0302, U+0304, U+0305, U+0306, U+0307, U+0308, U+030A, U+030B, U+030C, U+030F, U+0312, U+031B, U+0325, U+0326, U+0327, U+0328, U+0336, U+0337, and U+0338.
