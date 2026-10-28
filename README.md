![Cover](./resources/header.png)

<p align="center">
  <a href="https://trendshift.io/repositories/13165" target="_blank"><img src="https://trendshift.io/api/badge/repositories/13165" alt="subframe7536%2Fmaple-font | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
  <a href="https://hellogithub.com/repository/0601f355bd824d88b58f1af3066c486a" target="_blank"><img src="https://api.hellogithub.com/v1/widgets/recommend.svg?rid=0601f355bd824d88b58f1af3066c486a&claim_uid=AO0yWRQ48ITGNqK" alt="Featured｜HelloGitHub" style="width: 250px; height: 54px;" width="250" height="54" /></a>
</p>
<p align="center">
  <img alt="GitHub Repo Stars" src="https://img.shields.io/github/stars/subframe7536/maple-font">
  <img alt="GitHub Repo Forks" src="https://img.shields.io/github/forks/subframe7536/maple-font">
  <img alt="X (formerly Twitter) Follow" src="https://img.shields.io/twitter/follow/subframe7536">
</p>
<p align="center">
  <img alt="GitHub Release" src="https://img.shields.io/github/v/release/subframe7536/maple-font">
  <img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/subframe7536/maple-font/total">
  <img alt="GitHub Repo License" src="https://img.shields.io/github/license/subframe7536/maple-font">
  <img alt="GitHub Repo Issues" src="https://img.shields.io/github/issues/subframe7536/maple-font">
</p>

<p align="center">
  <a href="#install">Download</a> |
  <a href="https://font.subf.dev">Website</a> |
  <a href="https://font.subf.dev/en/playground">Playground</a> |
  <a href="#documentation">Docs</a> |
  English |
  <a href="./README_CN.md">简中</a> |
  <a href="./README_TC.md">繁中</a> |
  <a href="./README_JP.md">日本語</a> |
  <a href="./README_KR.md">한국어</a>
</p>

> [!WARNING]
> This branch hosts V8, which is still under development and has not been officially released. For the stable version, use the [`v7` branch](https://github.com/subframe7536/maple-font/tree/v7).

# Maple Mono

Maple Mono is an open-source monospace font designed to make coding more comfortable and efficient. I created it to improve my own productivity, and hope it helps more people enjoy writing code.

## Highlights

- ✨ **Variable weight** - Adjust the weight continuously, with carefully refined italic glyphs for flexible typography.
- ☁️ **Rounded glyphs** - Rounded throughout, with redesigned `@ $ % & Q ->` and refined italic connections (`f i j k l x y`).
- 🪄 **Smart ligatures** - Extensive smart ligatures, character variants, OpenType stylistic sets, and built-in status-label ligatures make code easier to read and more expressive.
- 🔣 **Extended Unicode coverage** - Box-drawing characters, Braille, mathematical operators (U+2200–U+22FF), chess and card symbols, terminal status and progress symbols, and Claude Code loading indicators.
- 🎨 **Nerd Font icons** - Integrates [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) natively for clear, readable interfaces across development tools and terminals.
- 🀄 **CJK with 2:1 alignment** - Simplified Chinese, Traditional Chinese, Japanese, and Korean glyphs are exactly twice the Latin width, keeping multilingual text and Markdown tables aligned.
- 📏 **Three widths** - Default, narrow, and slim character widths.
- 🔨 **Highly customizable** - Configure OpenType features, tag ligatures, line height, character width, and weight mapping, or generate a custom font from source.

## CJK

CJK glyphs use a 2:1 width ratio with Latin characters to keep multilingual text and Markdown tables aligned; as a trade-off, the default CJK spacing is wider than in many other CJK fonts ([why](https://github.com/subframe7536/maple-font/issues/211)). Compared with V7, V8 greatly expands and improves its CJK coverage.

| Locale | Coverage                                                                | CJK font source                                                                                     |
| ------ | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| CN     | Simplified Chinese, with common Traditional Chinese and Japanese ranges | [WenYuan Rounded SC](https://github.com/takushun-wu/WenYuanFonts)                                   |
| TC     | Traditional Chinese                                                     | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)                            |
| JP     | Japanese                                                                | [Resource Han Rounded JP](https://github.com/CyanoHao/Resource-Han-Rounded)                         |
| KR     | Korean                                                                  | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc), filtered to Korean ranges |

![2-1.png](./resources/2-1.png)

See [CJK Build](./documentation/cjk.md) for details.

## Preview

![showcase.png](./resources/showcase.webp)

Generated with [CodeImg](https://github.com/subframe7536/vscode-codeimg), theme [Maple](https://github.com/subframe7536/vscode-theme-maple), 16px font size, 1.8 line height, default letter spacing.

## Ligatures & Variants

Maple Mono ships smart ligatures (enabled through `calt`), character variants (`cvXX`), and stylistic sets (`ssXX`), supported by most modern operating systems, browsers, terminals, and editors. See [OpenType Features](./documentation/opentype-features.md) for the complete list, or try them live in the [Playground](https://font.subf.dev/en/playground).

## Styles at a Glance

- **Normal preset** - A less opinionated style with glyphs similar to `JetBrains Mono` and a slashed zero.
- **Infinite arrow ligatures** - Inspired by Fira Code and Cascadia Code, arrow ligatures stretch to any length.
- **Three widths** - Default (600), narrow (550), and slim (500) Latin glyph widths.
- **Nerd Font icons** - Default, fixed-width (`NFMono`), or proportional (`NFPropo`) icon spacing.

| Normal preset                                       | Infinite arrow ligatures                                                |
| --------------------------------------------------- | ----------------------------------------------------------------------- |
| ![Normal preset](./resources/preview-normal.webp)   | ![Infinite arrow ligatures](./resources/preview-infinite-arrows.webp)   |
| **Widths**                                          | **Nerd Font icons**                                                     |
| ![Width comparison](./resources/preview-widths.webp) | ![Nerd Font spacing modes](./resources/preview-nerd-fonts.webp)        |

See [Build Options](./documentation/build-options.md) for how to build each style.

## Install

Download the font archives from [Releases](https://github.com/subframe7536/maple-font/releases/latest), or install the most common package (Maple Mono NF) with a package manager:

```sh
# Scoop (Windows)
scoop bucket add nerd-fonts
scoop install Maple-Mono-NF
# Homebrew (macOS, Linux)
brew install --cask font-maple-mono-nf
# Arch Linux (archlinuxcn)
paru -S ttf-maplemono-nf-unhinted
# Nixpkgs: add `maple-mono.NF-unhinted` to `fonts.packages`
```

Package managers currently ship v7.9. See the [installation guide](./documentation/install.md) for all packages.

### CDN

- **Maple Mono**: [fontsource](https://fontsource.org/fonts/maple-mono), [ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/)
- **Maple Mono CN**: [The Chinese Web Fonts Plan](https://chinese-font.netlify.app/zh-cn/fonts/maple-mono-cn/MapleMono-CN-Regular), [ZeoSeven Fonts](https://fonts.zeoseven.com/items/442/)

## Which File Should I Choose?

| Use case               | Choose                                |
| ---------------------- | ------------------------------------- |
| General coding         | `TTF` or `OTF`                        |
| Terminal icons         | `NF`, `NFMono`, or `NFPropo`          |
| Icons and CJK together | `NF-CN`, `NF-TC`, `NF-JP`, or `NF-KR` |
| Web pages              | `WOFF2`                               |

See [Naming and Choosing Fonts](./documentation/choose.md) for every package and the hinted / unhinted difference.

## Usage

See the [usage guide](./documentation/usage.md) for VS Code, JetBrains IDEs, Zed, Windows Terminal, Kitty, and Ghostty.

## Make Your Own Build

Every highlight above can be tuned at build time through [`config.json`](./config.json) or `build.py` options. Choose from the following build methods:

- **Playground**: Adjust features and build directly in the browser via [Playground](https://font.subf.dev/en/playground).
- **GitHub Actions**: Build in the cloud using the [GitHub Actions](https://github.com/subframe7536/maple-font/actions/workflows/custom.yml) workflow.
- **Docker**: Build with a Docker container without configuring a local Python environment.
- **Local Build**: Run `build.py` locally using Python or `uv`.

See [Custom Build](./documentation/build.md) for details.

## Documentation

- **Get started**: [Installation](./documentation/install.md) · [Naming and Choosing Fonts](./documentation/choose.md) · [Usage](./documentation/usage.md) · [OpenType Features](./documentation/opentype-features.md)
- **Build**: [Custom Build](./documentation/build.md) · [Build Options](./documentation/build-options.md) · [CJK Build](./documentation/cjk.md) · [`build.py` CLI Reference](./documentation/cli.md)
- **Contribute**: [Development](./documentation/development.md) · [Google Fonts Build and QA](./documentation/google-fonts.md)

## Credits

- [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)
- [Fira Code](https://github.com/tonsky/FiraCode)
- [Cascadia Code](https://github.com/microsoft/cascadia-code)
- [Roboto Mono](https://github.com/googlefonts/RobotoMono)
- [Victor Mono](https://github.com/rubjo/victor-mono)
- [Commit Mono](https://github.com/eigilnikolajsen/commit-mono)
- [Code Sample](https://github.com/TheRenegadeCoder/sample-programs-website)
- [Nerd Font](https://github.com/ryanoasis/nerd-fonts)
- [Font Freeze](https://github.com/MuTsunTsai/fontfreeze/)
- [Font Viewer](https://tophix.com/font-tools/font-viewer)
- [Monolisa](https://www.monolisa.dev/)
- [Recursive](https://www.recursive.design/)

## Sponsorship

If this font is helpful to you, please consider sponsoring me through [Afdian](https://afdian.com/a/subframe7536).

## Star History

<a href="https://star-history.dera.page/#subframe7536/maple-font&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
 </picture>
</a>

## License

SIL Open Font License 1.1
