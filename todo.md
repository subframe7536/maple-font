# TODO

## Ligatures

- [x] `[erro]` / `[dbug]` / `[crit]` / `[alert]` / `[success]` / `[tracing]` / `[critical]` #767 #777
- [x] add missing `>:` / `:>:` / `:<:`
- [x] https://lobste.rs/s/ahca9t/maple_mono_open_source_monospace_font#c_un8dnc
- [x] fix wrong italic tags #854

## Character Variant

- [x] cv12 / cv45: `u` without tail, like JetBrains Mono #785
- [x] cv67: longer bar (`|`), top + 50, bottom - 100 #732
  - [x] relative ligatures
- [x] ss12 / ss13: like monaspace cv12 / cv13 #782
- [x] cv68: `===` become 2 bars
- [x] round Y and y #846

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
- [x] U+21B5 #771
- [x] more mathmatical glyphs #852
  - [x] high-usage symbols (first):
    - [x] long arrows: U+27F9, U+27F8, U+27FA, U+27FC, U+290F, U+290E (single 600-unit cell, same as U+27F6)
    - [x] floor / ceiling: U+230A, U+230B, U+2308, U+2309
    - [x] harpoons: U+21C0, U+21BD, U+21CC
    - [x] diagonal double arrows: U+21D6, U+21D7, U+21D8, U+21D9
    - [x] circled operators: U+2A02
    - [x] Isabelle markup: U+2759, U+2015, U+2710, U+25A9, U+27A7, U+2B1A
    - [x] others: U+2322, U+291C, U+2AA2, U+03F5, U+2311
  - [x] remaining BMP symbols (selection):
    - [x] arrows: U+21C1, U+21BC, U+21C3, U+21C2, U+21BF, U+21D5
    - [x] brackets: U+2983, U+2984, U+2989, U+298A
    - [x] operators and relations: U+2A85, U+2A86, U+2A04, U+2323, U+2A1D, U+2AF4, U+2AFD, U+2AFF, U+2A01, U+2A3F, U+2135, U+2127, U+2118
    - [x] Z notation: U+2A3E, U+2914, U+2915, U+2900, U+21F8, U+21FB, U+2A64, U+2A65, U+2981, U+2A1F, U+2A21, U+2982, U+29F9, U+2040
    - [x] document markup: U+2756, U+204B
    - [x] icons: U+261B
  - not planned: math letters (script / Fraktur / double-struck / sans-serif) and anything in U+1xxxx
- [x] u+2605 , u+2606 #849

### CN

- [x] 易经六十四卦符号 #580
- [x] 文渊圆体 1.110
- [x] 部分全宽圆圈数字需要变成半宽

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

~~`family/win_ascent_and_descent` — set `OS/2.usWinAscent` to at least 1120 and `OS/2.usWinDescent` to at least 400 after confirming the intended line-spacing behavior.~~

- [x] `case_mapping` — add the missing case-swapping counterparts for U+01D5/U+01D7/U+01D9/U+01DB, U+0186, U+A7AE, U+01A9, U+01B1, U+0245, U+01B7, U+03F2, U+1F41, and U+1F64.
- [x] `legacy_accents` — remove the GDEF mark class assignment from `dieresis`, `macron`, `acute`, `cedilla`, `circumflex`, `caron`, `breve`, `dotaccent`, `ring`, `ogonek`, `tilde`, and `hungarumlaut`.
- [x] `googlefonts/glyphsets/shape_languages` — add the mandatory missing Cyrillic characters required by `GF_Phonetics_SinoExt`, including Bashkir, Chuvash, Azerbaijani Cyrillic, Kabardian/Adyghe/Dargwa/Lezghian/Ingush, Chechen, Avaric, Mari, and Sakha.
