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
  <a href="#下载与安装">下载</a> |
  <a href="https://font.subf.dev">网站</a> |
  <a href="./README.md">English</a> |
  中文 |
  <a href="./README_TC.md">繁中</a> |
  <a href="./README_JP.md">日本語</a> |
  <a href="./README_KR.md">한국어</a>
</p>

> [!WARNING]
> V8 版本仍在开发中，尚未正式发布。如果你需要使用稳定版本，请前往 [`v7` 分支](https://github.com/subframe7536/maple-font/tree/v7)。

# Maple Mono

Maple Mono 是一款开源等宽字体，致力于让编码体验更加舒适、高效。

我制作它是为了提升自己的工作效率，也希望它能帮助更多人更愉快地编写代码。

## 为什么选择 Maple Mono？

- ✨ **可变字体支持** - 支持连续调节字重，并针对斜体字形进行细致优化，让排版控制更加灵活。
- ☁️ **圆角与视觉优化** - 全面采用圆角设计，重绘 `@ $ % & Q ->` 等关键符号，优化斜体连笔（`f i j k l x y`），并提供多种字符宽度模式。
- 🪄 **智能连字增强** - 支持大量智能连字，提供丰富的字符变体和 OpenType 样式集，内置标签连字，帮助代码更易读，也更有表现力。
- 🔣 **Unicode 扩展覆盖** - 覆盖制表符、盲文、数学运算符（U+2200–U+22FF）、国际象棋与扑克牌符号、终端状态与进度符号，以及 Claude Code 状态加载符号等，适用于科学计算和开发场景。
- 🎨 **Nerd Font 图标支持** - 原生集成 [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts)，兼容各类开发工具和终端环境，让界面信息更清晰易读。
- 🔨 **高度可定制构建** - 支持强制启用 OpenType 特性、自定义标签连字、行高、字符宽度和字重映射等配置，也可以从源码生成专属字体。

### 简体中文、繁体中文、日文与韩文

Maple Mono 支持 CJK 字符集。与 V7 相比，V8 大幅扩充并优化了 CJK 字符集，覆盖简体中文、繁体中文、日文和韩文。为了让多语言文本和 Markdown 表格保持整齐，CJK 字符与英文字符按 2:1 的宽度对齐；相应地，默认 CJK 字符的间距会比其他常见中文字体更宽，详见[这个议题](https://github.com/subframe7536/maple-font/issues/211)。

| 地区 | 覆盖范围                           | CJK 字库来源                                                                             | 构建输出 |
| ---- | ---------------------------------- | ---------------------------------------------------------------------------------------- | -------- |
| CN   | 简体中文，并覆盖常用繁体与日文字符 | [WenYuan Rounded SC](https://github.com/takushun-wu/WenYuanFonts)                        | `CN`     |
| TC   | 繁体中文                           | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)                 | `TC`     |
| JP   | 日文                               | [Resource Han Rounded JP](https://github.com/CyanoHao/Resource-Han-Rounded)              | `JP`     |
| KR   | 韩文                               | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)，按韩文区域筛选 | `KR`     |

CJK 构建默认关闭。你可以通过 CJK 构建配置选择地区、静态或可变输出，以及是否启用紧凑宽度模式。

<!--
|Go|od| t|yp|og|ra|ph|y |re|ad|s |ea|si|ly|
|优|美|的|字|体|让|阅|读|变|得|更|加|轻|松|
|優|美|的|字|體|讓|閱|讀|變|得|更|加|輕|鬆|
|美|し|い|書|体|は|も|っ|と|読|み|や|す|い|
|아|름|다|운|글|꼴|은|더|읽|기|가|편|해|요|
|1!|2@|3#|4$|5%|6^|7&|8*|9(|0)|_+|{}|[]|;:|
-->

![2-1.png](./resources/2-1.png)

## 预览

![showcase.png](./resources/showcase.webp)

- 生成工具：[CodeImg](https://github.com/subframe7536/vscode-codeimg)
- 主题：[Maple](https://github.com/subframe7536/vscode-theme-maple)
- 配置：字号 16px，行高 1.8，默认字母间距

## 开始使用

### 下载与安装

你可以从 [Releases](https://github.com/subframe7536/maple-font/releases/latest) 下载字体压缩包。

你也可以通过 Scoop、Homebrew、AUR/Paru、NixPkgs 等包管理器安装 Maple Mono，详情见[安装指南](./docs/install.md)。

### 使用与特性配置

使用方法和配置说明请参阅[使用指南](./docs/usage.md)。

#### 命名说明与字体选择

Maple Mono 根据用户反馈，在发行版中提供了多种字体格式和字符集范围。你可以根据使用场景选择合适的字体文件，详情见[字体选择](./docs/choose.md)。

### CDN

### Maple Mono

- [fontsource](https://fontsource.org/fonts/maple-mono)
- [ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/)

### Maple Mono CN

- [The Chinese Web Fonts Plan (中文网字计划)](https://chinese-font.netlify.app/zh-cn/fonts/maple-mono-cn/MapleMono-CN-Regular)
- [ZeoSeven Fonts](https://fonts.zeoseven.com/items/442/)


## 亮点介绍

你可以在[page#todo]()预览所有亮点。

### 自定义构建

Maple Mono 提供了高度可定制的构建方式。你可以修改 [`config.json`](./config.json)，或在命令行中添加参数，生成符合需求的字体文件，详情见[自定义构建](./docs/build.md)。

查看完整的 [`build.py` 命令行选项](#buildpy-cli)。

### 窄字符

在 V8 中，Maple Mono 提供三种字符宽度模式。你可以修改 [`config.json`](./config.json) 中的 `"width"` 字段，或在命令行中添加参数 `--width <mode>` 来选择宽度模式。

可选模式如下：

- default: 600
- narrow: 550
- slim: 500

![Width comparison](./resources/preview-widths.webp)

### OpenType 特性开关

“OpenType 特性”是用于控制字体内置变体和连字的机制，绝大多数现代操作系统、浏览器、终端和编辑器都支持它。你可以通过启用或禁用 OpenType 特性，控制连字和字符样式。

Maple Mono 提供大量细粒度的 OpenType 特性。为了减少配置成本，构建时可以为这些特性选择三种处理方式（[为什么](https://github.com/subframe7536/maple-font/issues/233#issuecomment-2410170270)）：

1. `enable`：强制启用这些特性，无需在字体特性配置中设置 `cvXX` / `ssXX` / `zero`，行为类似于默认连字。
2. `disable`：移除 `cvXX` / `ssXX` / `zero` 中的特性，即使手动启用，也不会生效。
3. `ignore`：保持默认行为，不做任何处理。

### Normal 预设

Maple Mono 的默认字形设计偏向独特和个性化，可能不适合所有人的审美或使用场景。为此，Maple Mono 提供了 `--normal` 构建预设，生成类似 `JetBrains Mono` 的字形（`0` 的中间为斜线，而不是圆点）。

![Normal preset](./resources/preview-normal.webp)

### 自定义 OpenType 特性

绝大多数字体不支持自定义 OpenType 特性，而 Maple Mono 支持通过编程方式定制这些特性。

默认情况下，[`scripts/feature/`](./scripts/feature) 中的 Python 模块会生成 OpenType 特性代码，并在构建时加载。你可以修改这些模块来调整功能或自定义标签；如果希望直接编辑 OpenType 特性源文件（`.fea`），请在运行 `build.py` 时添加 `--apply-fea-file` 参数，构建脚本会读取并加载 [`source/features/{regular,italic}{_cn,}.fea`](./source/features) 中的特性文件。

### 无限箭头连字

受 Fira Code 和 Cascadia Code 启发，Maple Mono 从 v7.3 开始支持无限箭头连字。由于渲染方面的未知原因，Hinted 字体中的箭头连字可能发生错位，因此 v7.4 起的 Hinted 版本默认移除了该特性。

你可以在 `config.json` 中设置 `"infinite_arrow": true`，或在命令行中添加 `--infinite-arrow` 强制启用该特性。遇到问题时，请在[#508](https://github.com/subframe7536/maple-font/issues/508)中讨论。

![Infinite arrow ligatures](./resources/preview-infinite-arrows.webp)

### 标准 Zero 特性

默认情况下，`0` 是斜线样式，启用 `zero` 后显示圆点。使用 `--standard-zero` 可恢复标准的 OpenType 语义：`0` 默认显示圆点，启用 `zero` 后显示斜线。

### 自定义行高

Maple Mono 的默认行高为 `1`。你可以修改 [`config.json`](./config.json) 中的 `"line_height"` 字段，或在命令行中添加参数 `--line-height <value>` 来调整行高；最终行高的计算公式为 `(ascender - descender) * line_height`。

### 自定义 Unicode 映射

如果 Maple Mono 缺少某些 Unicode 码点，相关字符可能无法显示。你可以修改 [`config.json`](./config.json) 中的 `"codepoint_alias"` 项，自定义 Unicode 映射。

例如，将一个现有的字符映射到另一个 Unicode 码点：

```json
{
  "codepoint_alias": {
    "U+E000": "U+E001",
    "U+E002": "U+E003"
  }
}
```

### 自定义字重映射

你可以通过 `config.json` 中的 `"weight_mapping"` 项修改静态字体的粗细。

例如，要让常规字重稍微变细，只需降低 `"weight_mapping.regular"` 的数值（本例从 400 调整为 350）：

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

### 自定义 Nerd Font 配置

Maple Mono 内置 Nerd Font 图标支持，并遵循其命名规则。默认情况下，每个图标使用一个拉丁字符的字宽，但其字形宽度可能不同。

- 如果需要让图标占用一个拉丁字符的宽度（Nerd Font Mono），请在 `config.json` 中设置 `"nerd_font.mono": true`，或在构建参数中添加 `--nf-mono`。
- 如果需要使用可变宽度图标（Nerd Font Propo），请在 `config.json` 中设置 `"nerd_font.propo": true`，或在构建参数中添加 `--nf-propo`。

如果要自定义 `font-patcher` 参数，需要安装 `fontforge`（可能还需要 `python3-fontforge`）。你也可能需要在 [config.json](./config.json) 中修改 `"nerd_font.extra_args"`。

![Nerd Font spacing modes](./resources/preview-nerd-fonts.webp)

#### 参数解析规则

默认参数：`-l --careful --outputdir dir`

- 当 `"nerd_font.propo"` 为 `true` 时，添加 `--variable-width-glyphs`。
- 当 `"nerd_font.mono"` 为 `true` 时，添加 `--mono`。

## CJK 版本（简体中文）

默认情况下不会生成中文字体。运行 `python build.py` 时添加 `--cjk cn` 参数，构建脚本会从 [GitHub Release](https://github.com/subframe7536/maple-font/releases/tag/cjk-base) 下载中文基字形。

### 缩小中文字体的间距

如果只有中文字符的间距**过大**，而英文字母的间距正常，可以通过构建选项 `cjk.narrow` 或命令行参数 `--cjk-narrow` 缩小中文字符间距，但这样会导致字体无法再被识别为等宽字体。

你可以在[#249](https://github.com/subframe7536/maple-font/issues/249#issuecomment-2871260476)中查看效果或参与讨论。

- 如果还想改变拉丁字母的宽度，请使用[`--width` 参数](#窄字符)。

### 居中全宽标点支持

Maple Mono 支持 `cpct` 特性，让全宽标点居中显示（繁体中文中较为常见）；也可以启用 `cv99` 特性强制应用该效果，详情见[#150](https://github.com/subframe7536/maple-font/issues/150)。

### GitHub 镜像

构建脚本会自动从 GitHub 下载所需资源。如果下载失败，可以在 [config.json](./config.json) 中设置 `github_mirror`，或将 `$GITHUB` 设置为环境变量。目标 URL 格式为 `https://<github_mirror>/<user>/<repo>/releases/download/<tag>/<file>`；也可以直接下载目标 `.zip` 文件，并将其放在 `build.py` 所在目录中。

## 我个人在用的其他中文字体资源

参见 [cn-resource](https://github.com/subframe7536/maple-font/tree/other-resources/cn-resource) 和 [cn-base](https://github.com/subframe7536/maple-font/releases/tag/cn-base)。

<a id="buildpy-cli"></a>

## `build.py` 命令行选项

```text
用法：build.py [-h] [-v] [-d] [--debug] [-n] [--standard-zero] [--feat FEAT]
               [--apply-fea-file] [--hinted | --no-hinted]
               [--liga | --no-liga] [--infinite-arrow] [--remove-tag-liga]
               [--line-height LINE_HEIGHT] [--width {default,narrow,slim}]
               [--format FORMATS] [--least-styles] [--cache] [--archive]
               [--nf | --no-nf] [--nf-mono] [--nf-propo] [--nf-variable]
               [--font-patcher] [--cjk CJK] [--cjk-variable] [--cjk-narrow]
               [--cjk-scale-factor CJK_SCALE_FACTOR] [--cjk-both]
               [--cjk-hinted | --no-cjk-hinted] [--cn | --no-cn]
               [--cn-narrow] [--cn-scale-factor CN_SCALE_FACTOR] [--cn-both]

Maple Mono 构建与优化工具

选项：
  -h, --help            显示帮助信息并退出
  -v, --version         显示程序版本并退出
  -d, --dry             输出配置并退出
  --debug               使用快速调试构建：添加 `Debug`、启用调试日志、
                        仅构建 Regular/Italic，并跳过 OTF/WOFF2/Nerd Font 输出

特性选项：
  -n, --normal          使用 Normal 预设，生成类似 `JetBrains Mono` 的字形，
                        其中 0 使用斜线样式
  --standard-zero       使用标准 zero 语义：默认显示圆点，启用 `zero` 后显示斜线
  --feat FEAT           启用并冻结指定特性，以逗号分隔
                        （例如 `--feat zero,cv01,ss07,ss08`）；上下文规则通过
                        `calt` 启用
  --apply-fea-file      将匹配的
                        `source/features/{regular,italic}{_cn,}.fea` 应用到静态和可变字体
  --hinted              在 NF/CJK/NF-CJK 中使用 Hinted 字体作为基础字体（默认）
  --no-hinted           在 NF/CJK/NF-CJK 中使用未加提示的字体作为基础字体
  --liga                保留所有连字（默认）
  --no-liga             移除所有连字
  --infinite-arrow      启用无限箭头连字（Hinted 字体默认禁用）
  --remove-tag-liga     移除类似 `[TODO]` 的纯文本标签连字
  --line-height LINE_HEIGHT
                        行高缩放因子（例如 1.1）
  --width {default,narrow,slim}
                        设置字形宽度：default（600）、narrow（550）、slim（500）

构建选项：
  --format FORMATS      以逗号分隔的列表选择所需基础输出格式：ttf、otf、woff2；
                        可变字体基础版本始终会构建
  --least-styles        仅构建 Regular/Bold/Italic/BoldItalic 样式
  --cache               复用 `fonts/` 下有效的缓存流水线阶段，并保留其他已有输出
  --archive             使用配置和许可证，将每个已有的非 JSON 输出目录归档

Nerd Font 选项：
  --nf, --nerd-font     构建 Nerd Font 版本（默认）
  --no-nf, --no-nerd-font
                        不构建 Nerd Font 版本
  --nf-mono             固定 Nerd Font 图标的宽度
  --nf-propo            使 Nerd Font 图标宽度可变，覆盖 `--nf-mono`
  --nf-variable         构建 Nerd Font 可变字体
  --font-patcher        强制使用 Nerd Font Patcher 构建 NF 格式

CJK 选项：
  --cjk CJK             构建 Maple Mono + CJK 扩展字体，区域为 cn、jp、tc、kr。
                        可重复指定或使用逗号分隔的值。
  --cjk-variable        将 CJK 扩展输出保留为合并的可变字体
  --cjk-narrow          对选定区域应用窄 CJK 间距
  --cjk-scale-factor CJK_SCALE_FACTOR
                        设置选定 CJK 区域的缩放因子。格式为：
                        <factor> 或 <width_factor>,<height_factor>
  --cjk-both            启用 Nerd Font 时，同时构建 NF CJK 和非 NF CJK 输出
  --cjk-hinted          自动为最终静态 CJK 字体添加提示
  --no-cjk-hinted       不为最终静态 CJK 字体添加提示（默认）

已弃用的 CN 选项：
  --cn                  已弃用的 `--cjk cn` 别名
  --no-cn               已弃用的从所选 CJK 区域中移除 `cn` 的别名
  --cn-narrow           已弃用的针对 `cn` 使用 `--cjk-narrow` 的别名
  --cn-scale-factor CN_SCALE_FACTOR
                        已弃用的针对 `cn` 使用 `--cjk-scale-factor` 的别名
  --cn-both             已弃用的 `--cjk-both` 别名
```

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
