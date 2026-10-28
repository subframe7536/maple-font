![封面图](./resources/header.png)

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
  <a href="#安装">下载</a> |
  <a href="https://font.subf.dev">网站</a> |
  <a href="https://font.subf.dev/zh-cn/playground">在线体验</a> |
  <a href="#文档">文档</a> |
  <a href="./README.md">English</a> |
  中文 |
  <a href="./README_TC.md">繁中</a> |
  <a href="./README_JP.md">日本語</a> |
  <a href="./README_KR.md">한국어</a>
</p>

> [!WARNING]
> 当前分支为 V8 版本，仍在开发中，尚未正式发布。如果你需要使用稳定版本，请前往 [`v7` 分支](https://github.com/subframe7536/maple-font/tree/v7)。

# Maple Mono

Maple Mono 是一款开源等宽字体，致力于让编码体验更加舒适、高效。我制作它是为了提升自己的工作效率，也希望它能帮助更多人更愉快地编写代码。

## 亮点

- ✨ **可变字重** - 支持连续调节字重，并针对斜体字形进行细致优化，让排版控制更加灵活。
- ☁️ **圆角字形** - 全面采用圆角设计，重绘 `@ $ % & Q ->` 等关键符号，优化斜体连笔（`f i j k l x y`）。
- 🪄 **智能连字** - 支持大量智能连字，提供丰富的字符变体和 OpenType 样式集，内置标签连字，帮助代码更易读，也更有表现力。
- 🔣 **Unicode 扩展覆盖** - 覆盖制表符、盲文、数学运算符（U+2200–U+22FF）、国际象棋与扑克牌符号、终端状态与进度符号，以及 Claude Code 状态加载符号等。
- 🎨 **Nerd Font 图标** - 原生集成 [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts)，兼容各类开发工具和终端环境，让界面信息更清晰易读。
- 🀄 **CJK 2:1 对齐** - 简体中文、繁体中文、日文和韩文字形宽度恰好为拉丁字符的两倍，多语言文本和 Markdown 表格保持整齐。
- 📏 **三种字宽** - 提供 default、narrow、slim 三种字符宽度。
- 🔨 **高度可定制** - 支持配置 OpenType 特性、标签连字、行高、字符宽度和字重映射，也可以从源码生成专属字体。

## CJK

CJK 字符与英文字符按 2:1 的宽度对齐，让多语言文本和 Markdown 表格保持整齐；相应地，默认 CJK 字符的间距会比其他常见中文字体更宽（[原因](https://github.com/subframe7536/maple-font/issues/211)）。与 V7 相比，V8 大幅扩充并优化了 CJK 字符集。

| 地区 | 覆盖范围                           | CJK 字库来源                                                                             |
| ---- | ---------------------------------- | ---------------------------------------------------------------------------------------- |
| CN   | 简体中文，并覆盖常用繁体与日文字符 | [WenYuan Rounded SC](https://github.com/takushun-wu/WenYuanFonts)                        |
| TC   | 繁体中文                           | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)                 |
| JP   | 日文                               | [Resource Han Rounded JP](https://github.com/CyanoHao/Resource-Han-Rounded)              |
| KR   | 韩文                               | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)，按韩文区域筛选 |

![2-1.png](./resources/2-1.png)

详情见 [CJK 构建](./documentation/cjk.md)。

## 我个人在用的其他中文字体资源

参见 [cn-base](https://github.com/subframe7536/maple-font/releases/tag/cn-base)。

## 预览

![showcase.png](./resources/showcase.webp)

生成工具：[CodeImg](https://github.com/subframe7536/vscode-codeimg)，主题：[Maple](https://github.com/subframe7536/vscode-theme-maple)，字号 16px，行高 1.8，默认字母间距。

## 连字与变体

Maple Mono 提供智能连字（通过 `calt` 启用）、字符变体（`cvXX`）和样式集（`ssXX`），绝大多数现代操作系统、浏览器、终端和编辑器都支持。完整列表见 [OpenType 特性](./documentation/opentype-features.md)，也可以在[在线体验](https://font.subf.dev/zh-cn/playground)中实时预览。

## 样式一览

- **Normal 预设** - 风格更中性，字形类似 `JetBrains Mono`，`0` 中间为斜线。
- **无限箭头连字** - 受 Fira Code 和 Cascadia Code 启发，箭头连字可以无限延长。
- **三种字宽** - 拉丁字符宽度可选 default（600）、narrow（550）、slim（500）。
- **Nerd Font 图标** - 图标间距可选默认、固定宽度（`NFMono`）或可变宽度（`NFPropo`）。

| Normal 预设                                          | 无限箭头连字                                                          |
| ---------------------------------------------------- | --------------------------------------------------------------------- |
| ![Normal preset](./resources/preview-normal.webp)    | ![Infinite arrow ligatures](./resources/preview-infinite-arrows.webp) |
| **字宽**                                             | **Nerd Font 图标**                                                    |
| ![Width comparison](./resources/preview-widths.webp) | ![Nerd Font spacing modes](./resources/preview-nerd-fonts.webp)       |

各样式的构建方法见[构建选项](./documentation/build-options.md)。

## 安装

你可以从 [Releases](https://github.com/subframe7536/maple-font/releases/latest) 下载字体压缩包，或通过包管理器安装最常用的 Maple Mono NF CN：

```sh
# Scoop (Windows)
scoop bucket add nerd-fonts
scoop install Maple-Mono-NF-CN
# Homebrew (macOS, Linux)
brew install --cask font-maple-mono-nf-cn
# Arch Linux (archlinuxcn)
paru -S ttf-maplemono-nf-cn-unhinted
# Nixpkgs：将 `maple-mono.NF-CN-unhinted` 添加到 `fonts.packages`
```

包管理器目前提供的是 v7.9 版本。全部软件包见[安装指南](./documentation/install.md)。

### CDN

- **Maple Mono**：[fontsource](https://fontsource.org/fonts/maple-mono)、[ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/)
- **Maple Mono CN**：[中文网字计划](https://chinese-font.netlify.app/zh-cn/fonts/maple-mono-cn/MapleMono-CN-Regular)、[ZeoSeven Fonts](https://fonts.zeoseven.com/items/442/)

## 我该选择哪个文件？

| 使用场景          | 推荐选择                              |
| ----------------- | ------------------------------------- |
| 日常编码          | `TTF` 或 `OTF`                        |
| 终端图标          | `NF`、`NFMono` 或 `NFPropo`           |
| 图标与 CJK        | `NF-CN`、`NF-TC`、`NF-JP` 或 `NF-KR`  |
| 网页              | `WOFF2`                               |

所有软件包及 hinted / unhinted 的区别见[字体选择](./documentation/choose.md)。

## 使用

VS Code、JetBrains IDE、Zed、Windows Terminal、Kitty 和 Ghostty 的配置方法见[使用指南](./documentation/usage.md)。

## 自行构建

上面的所有亮点都可以在构建时通过 [`config.json`](./config.json) 或 `build.py` 参数调整。你可以选择以下方式进行构建：

- **在线体验**：在[在线体验](https://font.subf.dev/zh-cn/playground)中直接调整特性并生成字体。
- **GitHub Actions**：使用 [GitHub Actions](https://github.com/subframe7536/maple-font/actions/workflows/custom.yml) 在云端自动构建。
- **Docker**：使用 Docker 容器构建，无需配置本地环境。
- **本地构建**：使用 Python 或 `uv` 在本地运行 `build.py` 构建。

详情见[自定义构建](./documentation/build.md)。

## 文档

文档目前仅提供英文版本。

- **入门**：[安装](./documentation/install.md) · [命名与字体选择](./documentation/choose.md) · [使用](./documentation/usage.md) · [OpenType 特性](./documentation/opentype-features.md)
- **构建**：[自定义构建](./documentation/build.md) · [构建选项](./documentation/build-options.md) · [CJK 构建](./documentation/cjk.md) · [`build.py` 命令行参考](./documentation/cli.md)
- **参与开发**：[开发](./documentation/development.md) · [Google Fonts 构建与 QA](./documentation/google-fonts.md)

## 鸣谢

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

## 赞助

如果这个字体对你有所帮助，欢迎通过[爱发电](https://afdian.com/a/subframe7536)赞助我。

## 点星

<a href="https://star-history.dera.page/#subframe7536/maple-font&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
 </picture>
</a>

## 许可

SIL Open Font License 1.1
