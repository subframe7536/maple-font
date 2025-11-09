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
  <a href="#下载">下载</a> |
  <a href="https://font.subf.dev">网站</a> |
  <a href="./README.md">English</a> |
  中文 |
  <a href="./README_JA.md">日本語</a>
</p>

# Maple Mono

Maple Mono 是一款开源等宽字体，专注于优化您的编码体验。

我制作它是为了提升自己的工作效率，希望它也能对其他人有所帮助。

V7 是一个完全重制版本，提供了可变字体格式和字体工程源文件，重新设计了超过一半的字形，并提供更智能的连字。您可以[在这里](https://github.com/subframe7536/maple-font/tree/main)查看 V6 版本。

## 特性

- ✨ 可变 - 无限的字体粗细，以及手工微调的斜体字形。
- ☁️ 丝滑 - **圆角**，独特的 `@ $ % & Q ->` 字形，以及手写风格的斜体 `f i j k l x y`。
- 💪 实用 - 大量的智能连字，详见 [`features/`](./source/features/README.md)。
- 🎨 图标 - 提供 [Nerd-Font](https://github.com/ryanoasis/nerd-fonts) 嵌入的版本，添加图标支持。
- 🔨 定制 - 自由开关或者构建 OpenType 字体特性，打造您专属的字体。

### 简体中文、繁体中文和日文

CN 版本基于[资源圆体](https://github.com/CyanoHao/Resource-Han-Rounded)提供了完整的中文开发环境的字符集支持，包括简体中文、繁体中文和日文。同时，中英文 2:1 完美对齐的特性，使得本字体在多语言显示、Markdown 表格等场景可以做到整齐划一、美观舒适。但是中文的间距相比其他流行的中文字体更大，详情请参阅[发行版说明](https://github.com/subframe7536/maple-font/releases/tag/cn-base)和[这个议题](https://github.com/subframe7536/maple-font/issues/211)。

![2-1.png](./resources/2-1.png)

## 屏幕截图

![showcase.png](./resources/showcase.png)

- 生成：[CodeImg](https://github.com/subframe7536/vscode-codeimg)
- 主题：[Maple](https://github.com/subframe7536/vscode-theme-maple)
- 配置：字体大小 16px，行高 1.8，默认字母间距

## 下载

您可以从 [Releases](https://github.com/subframe7536/maple-font/releases) 下载所有字体压缩包。

### Scoop (Windows)

```sh
# Add bucket
scoop bucket add nerd-fonts
# Maple Mono (ttf 格式)
scoop install Maple-Mono
# Maple Mono NF
scoop install Maple-Mono-NF
# Maple Mono NF CN
scoop install Maple-Mono-NF-CN
```

<details>
  <summary>所有包 (点击展开)</summary>

  ```sh
  # 添加 bucket
  scoop bucket add nerd-fonts
  # Maple Mono (ttf 格式)
  scoop install Maple-Mono
  # Maple Mono (hinted ttf 格式)
  scoop install Maple-Mono-autohint
  # Maple Mono (otf 格式)
  scoop install Maple-Mono-otf
  # Maple Mono NF
  scoop install Maple-Mono-NF
  # Maple Mono NF CN
  scoop install Maple-Mono-NF-CN
  ```

</details>

### Homebrew (MacOS, Linux)

```sh
# Maple Mono
brew install --cask font-maple-mono
# Maple Mono NF
brew install --cask font-maple-mono-nf
# Maple Mono NF CN
brew install --cask font-maple-mono-nf-cn
```

<details>
  <summary>所有包 (点击展开)</summary>

  ```sh
  # Maple Mono
  brew install --cask font-maple-mono
  # Maple Mono NF
  brew install --cask font-maple-mono-nf
  # Maple Mono CN
  brew install --cask font-maple-mono-cn
  # Maple Mono NF CN
  brew install --cask font-maple-mono-nf-cn

  # Maple Mono Normal
  brew install --cask font-maple-mono-normal
  # Maple Mono Normal NF
  brew install --cask font-maple-mono-normal-nf
  # Maple Mono Normal CN
  brew install --cask font-maple-mono-normal-cn
  # Maple Mono Normal NF CN
  brew install --cask font-maple-mono-normal-nf-cn
  ```

</details>

### Arch Linux

ArchLinuxCN 仓库允许下载单个软件包的 zip 文件，而无需下载 pkgbase 中的所有软件包的 zip 文件，但 AUR 不允许。(如果您有好的解决方案，请联系 Cyberczy(czysheep@gmail.com))

#### ArchLinuxCN (推荐)

```sh
# Maple Mono (Ligature TTF unhinted)
paru -S ttf-maplemono
# Maple Mono NF (Ligature unhinted)
paru -S ttf-maplemono-nf-unhinted
# Maple Mono NF CN (Ligature unhinted)
paru -S ttf-maplemono-nf-cn-unhinted
```

<details>
  <summary>所有包 (点击展开)</summary>

  ```sh
  # Maple Mono (Ligature Variable)
  paru -S ttf-maplemono-variable
  # Maple Mono (Ligature TTF hinted)
  paru -S ttf-maplemono-autohint
  # Maple Mono (Ligature TTF unhinted)
  paru -S ttf-maplemono
  # Maple Mono (Ligature OTF)
  paru -S otf-maplemono
  # Maple Mono (Ligature WOFF2)
  paru -S woff2-maplemono
  # Maple Mono NF (Ligature hinted)
  paru -S ttf-maplemono-nf
  # Maple Mono NF (Ligature unhinted)
  paru -S ttf-maplemono-nf-unhinted
  # Maple Mono CN (Ligature hinted)
  paru -S ttf-maplemono-cn
  # Maple Mono CN (Ligature unhinted)
  paru -S ttf-maplemono-cn-unhinted
  # Maple Mono NF CN (Ligature hinted)
  paru -S ttf-maplemono-nf-cn
  # Maple Mono NF CN (Ligature unhinted)
  paru -S ttf-maplemono-nf-cn-unhinted

  # Maple Mono (No-Ligature Variable)
  paru -S ttf-maplemononl-variable
  # Maple Mono (No-Ligature TTF hinted)
  paru -S ttf-maplemononl-autohint
  # Maple Mono (No-Ligature TTF unhinted)
  paru -S ttf-maplemononl
  # Maple Mono (No-Ligature OTF)
  paru -S otf-maplemononl
  # Maple Mono (No-Ligature WOFF2)
  paru -S woff2-maplemononl
  # Maple Mono NF (No-Ligature hinted)
  paru -S ttf-maplemononl-nf
  # Maple Mono NF (No-Ligature unhinted)
  paru -S ttf-maplemononl-nf-unhinted
  # Maple Mono CN (No-Ligature hinted)
  paru -S ttf-maplemononl-cn
  # Maple Mono CN (No-Ligature unhinted)
  paru -S ttf-maplemononl-cn-unhinted
  # Maple Mono NF CN (No-Ligature hinted)
  paru -S ttf-maplemononl-nf-cn
  # Maple Mono NF CN (No-Ligature unhinted)
  paru -S ttf-maplemononl-nf-cn-unhinted

  # Maple Mono Normal (Ligature Variable)
  paru -S ttf-maplemononormal-variable
  # Maple Mono Normal (Ligature TTF hinted)
  paru -S ttf-maplemononormal-autohint
  # Maple Mono Normal (Ligature TTF unhinted)
  paru -S ttf-maplemononormal
  # Maple Mono Normal (Ligature OTF)
  paru -S otf-maplemononormal
  # Maple Mono Normal (Ligature WOFF2)
  paru -S woff2-maplemononormal
  # Maple Mono Normal NF (Ligature hinted)
  paru -S ttf-maplemononormal-nf
  # Maple Mono Normal NF (Ligature unhinted)
  paru -S ttf-maplemononormal-nf-unhinted
  # Maple Mono Normal CN (Ligature hinted)
  paru -S ttf-maplemononormal-cn
  # Maple Mono Normal CN (Ligature unhinted)
  paru -S ttf-maplemononormal-cn-unhinted
  # Maple Mono Normal NF CN (Ligature hinted)
  paru -S ttf-maplemononormal-nf-cn
  # Maple Mono Normal NF CN (Ligature unhinted)
  paru -S ttf-maplemononormal-nf-cn-unhinted

  # Maple Mono Normal (No-Ligature Variable)
  paru -S ttf-maplemononormalnl-variable
  # Maple Mono Normal (No-Ligature TTF hinted)
  paru -S ttf-maplemononormalnl-autohint
  # Maple Mono Normal (No-Ligature TTF unhinted)
  paru -S ttf-maplemononormalnl
  # Maple Mono Normal (No-Ligature OTF)
  paru -S otf-maplemononormalnl
  # Maple Mono Normal (No-Ligature WOFF2)
  paru -S woff2-maplemononormalnl
  # Maple Mono Normal NF (No-Ligature hinted)
  paru -S ttf-maplemononormalnl-nf
  # Maple Mono Normal NF (No-Ligature unhinted)
  paru -S ttf-maplemononormalnl-nf-unhinted
  # Maple Mono Normal CN (No-Ligature hinted)
  paru -S ttf-maplemononormalnl-cn
  # Maple Mono Normal CN (No-Ligature unhinted)
  paru -S ttf-maplemononormalnl-cn-unhinted
  # Maple Mono Normal NF CN (No-Ligature hinted)
  paru -S ttf-maplemononormalnl-nf-cn
  # Maple Mono Normal NF CN (No-Ligature unhinted)
  paru -S ttf-maplemononormalnl-nf-cn-unhinted
  ```

</details>

#### AUR (不推荐)

```sh
# Maple Mono (Ligature TTF unhinted)
paru -S maplemono-ttf
# Maple Mono NF (Ligature unhinted)
paru -S maplemono-nf-unhinted
# Maple Mono NF CN (Ligature unhinted)
paru -S maplemono-nf-cn-unhinted
```

<details>
  <summary>所有包 (点击展开)</summary>

  ```sh
  # Maple Mono (Ligature Variable)
  paru -S maplemono-variable
  # Maple Mono (Ligature TTF hinted)
  paru -S maplemono-ttf-autohint
  # Maple Mono (Ligature TTF unhinted)
  paru -S maplemono-ttf
  # Maple Mono (Ligature OTF)
  paru -S maplemono-otf
  # Maple Mono (Ligature WOFF2)
  paru -S maplemono-woff2
  # Maple Mono NF (Ligature hinted)
  paru -S maplemono-nf
  # Maple Mono NF (Ligature unhinted)
  paru -S maplemono-nf-unhinted
  # Maple Mono CN (Ligature hinted)
  paru -S maplemono-cn
  # Maple Mono CN (Ligature unhinted)
  paru -S maplemono-cn-unhinted
  # Maple Mono NF CN (Ligature hinted)
  paru -S maplemono-nf-cn
  # Maple Mono NF CN (Ligature unhinted)
  paru -S maplemono-nf-cn-unhinted

  # Maple Mono (No-Ligature Variable)
  paru -S maplemononl-variable
  # Maple Mono (No-Ligature TTF hinted)
  paru -S maplemononl-ttf-autohint
  # Maple Mono (No-Ligature TTF unhinted)
  paru -S maplemononl-ttf
  # Maple Mono (No-Ligature OTF)
  paru -S maplemononl-otf
  # Maple Mono (No-Ligature WOFF2)
  paru -S maplemononl-woff2
  # Maple Mono NF (No-Ligature hinted)
  paru -S maplemononl-nf
  # Maple Mono NF (No-Ligature unhinted)
  paru -S maplemononl-nf-unhinted
  # Maple Mono CN (No-Ligature hinted)
  paru -S maplemononl-cn
  # Maple Mono CN (No-Ligature unhinted)
  paru -S maplemononl-cn-unhinted
  # Maple Mono NF CN (No-Ligature hinted)
  paru -S maplemononl-nf-cn
  # Maple Mono NF CN (No-Ligature unhinted)
  paru -S maplemononl-nf-cn-unhinted

  # Maple Mono Normal (Ligature Variable)
  paru -S maplemononormal-variable
  # Maple Mono Normal (Ligature TTF hinted)
  paru -S maplemononormal-ttf-autohint
  # Maple Mono Normal (Ligature TTF unhinted)
  paru -S maplemononormal-ttf
  # Maple Mono Normal (Ligature OTF)
  paru -S maplemononormal-otf
  # Maple Mono Normal (Ligature WOFF2)
  paru -S maplemononormal-woff2
  # Maple Mono Normal NF (Ligature hinted)
  paru -S maplemononormal-nf
  # Maple Mono Normal NF (Ligature unhinted)
  paru -S maplemononormal-nf-unhinted
  # Maple Mono Normal CN (Ligature hinted)
  paru -S maplemononormal-cn
  # Maple Mono Normal CN (Ligature unhinted)
  paru -S maplemononormal-cn-unhinted
  # Maple Mono Normal NF CN (Ligature hinted)
  paru -S maplemononormal-nf-cn
  # Maple Mono Normal NF CN (Ligature unhinted)
  paru -S maplemononormal-nf-cn-unhinted

  # Maple Mono Normal (No-Ligature Variable)
  paru -S maplemononormalnl-variable
  # Maple Mono Normal (No-Ligature TTF hinted)
  paru -S maplemononormalnl-ttf-autohint
  # Maple Mono Normal (No-Ligature TTF unhinted)
  paru -S maplemononormalnl-ttf
  # Maple Mono Normal (No-Ligature OTF)
  paru -S maplemononormalnl-otf
  # Maple Mono Normal (No-Ligature WOFF2)
  paru -S maplemononormalnl-woff2
  # Maple Mono Normal NF (No-Ligature hinted)
  paru -S maplemononormalnl-nf
  # Maple Mono Normal NF (No-Ligature unhinted)
  paru -S maplemononormalnl-nf-unhinted
  # Maple Mono Normal CN (No-Ligature hinted)
  paru -S maplemononormalnl-cn
  # Maple Mono Normal CN (No-Ligature unhinted)
  paru -S maplemononormalnl-cn-unhinted
  # Maple Mono Normal NF CN (No-Ligature hinted)
  paru -S maplemononormalnl-nf-cn
  # Maple Mono Normal NF CN (No-Ligature unhinted)
  paru -S maplemononormalnl-nf-cn-unhinted
  ```

</details>

### Nixpkgs (NixOS, Linux, MacOS)

```nix
fonts.packages = with pkgs; [
  # Maple Mono (Ligature TTF unhinted)
  maple-mono.truetype
  # Maple Mono NF (Ligature unhinted)
  maple-mono.NF-unhinted
  # Maple Mono NF CN (Ligature unhinted)
  maple-mono.NF-CN-unhinted
];
```

<details>
  <summary>所有包 (点击展开)</summary>

  ```nix
  fonts.packages = with pkgs; [
    # Maple Mono (Ligature Variable)
    maple-mono.variable
    # Maple Mono (Ligature TTF hinted)
    maple-mono.truetype-autohint
    # Maple Mono (Ligature TTF unhinted)
    maple-mono.truetype
    # Maple Mono (Ligature OTF)
    maple-mono.opentype
    # Maple Mono (Ligature WOFF2)
    maple-mono.woff2
    # Maple Mono NF (Ligature hinted)
    maple-mono.NF
    # Maple Mono NF (Ligature unhinted)
    maple-mono.NF-unhinted
    # Maple Mono CN (Ligature hinted)
    maple-mono.CN
    # Maple Mono CN (Ligature unhinted)
    maple-mono.CN-unhinted
    # Maple Mono NF CN (Ligature hinted)
    maple-mono.NF-CN
    # Maple Mono NF CN (Ligature unhinted)
    maple-mono.NF-CN-unhinted

    # Maple Mono (No-Ligature Variable)
    maple-mono.NL-Variable
    # Maple Mono (No-Ligature TTF hinted)
    maple-mono.NL-TTF-AutoHint
    # Maple Mono (No-Ligature TTF unhinted)
    maple-mono.NL-TTF
    # Maple Mono (No-Ligature OTF)
    maple-mono.NL-OTF
    # Maple Mono (No-Ligature WOFF2)
    maple-mono.NL-Woff2
    # Maple Mono NF (No-Ligature hinted)
    maple-mono.NL-NF
    # Maple Mono NF (No-Ligature unhinted)
    maple-mono.NL-NF-unhinted
    # Maple Mono CN (No-Ligature hinted)
    maple-mono.NL-CN
    # Maple Mono CN (No-Ligature unhinted)
    maple-mono.NL-CN-unhinted
    # Maple Mono NF CN (No-Ligature hinted)
    maple-mono.NL-NF-CN
    # Maple Mono NF CN (No-Ligature unhinted)
    maple-mono.NL-NF-CN-unhinted

    # Maple Mono Normal (Ligature Variable)
    maple-mono.Normal-Variable
    # Maple Mono Normal (Ligature TTF hinted)
    maple-mono.Normal-TTF-AutoHint
    # Maple Mono Normal (Ligature TTF unhinted)
    maple-mono.Normal-TTF
    # Maple Mono Normal (Ligature OTF)
    maple-mono.Normal-OTF
    # Maple Mono Normal (Ligature WOFF2)
    maple-mono.Normal-Woff2
    # Maple Mono Normal NF (Ligature hinted)
    maple-mono.Normal-NF
    # Maple Mono Normal NF (Ligature unhinted)
    maple-mono.Normal-NF-unhinted
    # Maple Mono Normal CN (Ligature hinted)
    maple-mono.Normal-CN
    # Maple Mono Normal CN (Ligature unhinted)
    maple-mono.Normal-CN-unhinted
    # Maple Mono Normal NF CN (Ligature hinted)
    maple-mono.Normal-NF-CN
    # Maple Mono Normal NF CN (Ligature unhinted)
    maple-mono.Normal-NF-CN-unhinted

    # Maple Mono Normal (No-Ligature Variable)
    maple-mono.NormalNL-Variable
    # Maple Mono Normal (No-Ligature TTF hinted)
    maple-mono.NormalNL-TTF-AutoHint
    # Maple Mono Normal (No-Ligature TTF unhinted)
    maple-mono.NormalNL-TTF
    # Maple Mono Normal (No-Ligature OTF)
    maple-mono.NormalNL-OTF
    # Maple Mono Normal (No-Ligature WOFF2)
    maple-mono.NormalNL-Woff2
    # Maple Mono Normal NF (No-Ligature hinted)
    maple-mono.NormalNL-NF
    # Maple Mono Normal NF (No-Ligature unhinted)
    maple-mono.NormalNL-NF-unhinted
    # Maple Mono Normal CN (No-Ligature hinted)
    maple-mono.NormalNL-CN
    # Maple Mono Normal CN (No-Ligature unhinted)
    maple-mono.NormalNL-CN-unhinted
    # Maple Mono Normal NF CN (No-Ligature hinted)
    maple-mono.NormalNL-NF-CN
    # Maple Mono Normal NF CN (No-Ligature unhinted)
    maple-mono.NormalNL-NF-CN-unhinted
  ];
  ```

</details>

## CDN

### Maple Mono

- [fontsource](https://fontsource.org/fonts/maple-mono)
- [ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/)

### Maple Mono CN

- [The Chinese Web Fonts Plan (中文网字计划)](https://chinese-font.netlify.app/zh-cn/fonts/maple-mono-cn/MapleMono-CN-Regular)
- [ZeoSeven Fonts](https://fonts.zeoseven.com/items/442/)

## 使用方法 & 特性配置

请参阅 [文档](./source/features/README_CN.md) 或者在 [特性测试页面](https://font.subf.dev/zh-cn/playground) 尝试。

> [!note]
> 用于自定义构建的 Web 工具仍在开发中。

## 命名说明

### 字体特性

- **Ligature**: 带有连字的默认版本 (`Maple Mono`)
- **No-Ligature**: 没有连字的默认版本 (`Maple Mono NL`)
- **Normal-Ligature**: 带有连字的 [`--normal` 预设](#预设) (`Maple Mono Normal`)
- **Normal-No-Ligature**: 没有连字的 [`--normal` 预设](#预设) (`Maple Mono Normal NL`)

### 字体格式和字符集

- **Variable**: 最小版本，通过字体的可变轴改变字体粗细
- **TTF**: 最小版本，ttf 格式 [推荐！]
- **OTF**: 最小版本，otf 格式
- **WOFF2**: 最小版本，woff2 格式，多用于网页加载
- **NF**: 嵌入 Nerd-Font 的版本，为终端添加图标 (带有 `-NF` 后缀)
- **CN**: 中文版本，嵌入中文和日文字形 (带有 `-CN` 后缀)
- **NF-CN**: 完整版本，嵌入图标、中文和日文字形 (带有 `-NF-CN` 后缀)

### 字体微调

- **Hinted 字体** 用于低分辨率屏幕，以获得更好的渲染效果。根据我个人的经验，如果您的屏幕分辨率低于或等于 1080P，建议使用 "hinted 字体"。使用 "unhinted 字体" 会导致文本错位或粗细不均。
  - 在这种情况下，您可以选择 `MapleMono-TTF-AutoHint` / `MapleMono-NF` / `MapleMono-NF-CN` 等。
- **Unhinted 字体** 用于高分辨率屏幕（例如 MacBook）。使用 "hinted 字体" 会使您的文本模糊或看起来很奇怪。
  - 在这种情况下，您可以选择 `MapleMono-OTF` / `MapleMono-TTF` / `MapleMono-NF-unhinted` / `MapleMono-NF-CN-unhinted` 等。
- 为什么存在 `-AutoHint` 和 `-unhinted` 后缀？
  - 为了向后兼容，我保留了原始命名方案。`-AutoHint` 仅用于 `TTF` 格式。


## 自定义构建

[`config.json`](./config.json) 文件用于配置构建过程。查看 [schema](./source/schema.json) 或 [文档](./source/features/README.md) 了解更多详情。

还有一些 [命令行选项](#构建脚本用法) 用于自定义构建过程。命令行选项的优先级高于 `config.json` 中的选项。

### 浏览器中构建

进入 [特性测试页面](https://font.subf.dev/zh-cn/playground)，点击左下角的“自定义构建”按钮

### 使用 Github Actions

您可以使用 [Github Actions](https://github.com/subframe7536/maple-font/actions/workflows/custom.yml) 来构建字体。

1. Fork 仓库
2. (可选) 更改 `config.json` 中的内容
3. 转到 Actions 选项卡
4. 点击左侧的 `Custom Build` 菜单项
5. 点击 `Run workflow` 按钮并设置选项
6. 等待构建完成
7. 从 Releases 下载字体压缩包

### 使用 Docker

```shell
git clone https://github.com/subframe7536/maple-font --depth 1 -b variable
docker build -t maple-font .
docker run -v "$(pwd)/fonts:/app/fonts" -e BUILD_ARGS="--normal" maple-font
```

### 本地构建

克隆仓库并在您的本地机器上运行。确保您已安装 `python3` 和 `pip`

```shell
git clone https://github.com/subframe7536/maple-font --depth 1 -b variable
pip install -r requirements.txt
python build.py
```

> [!TIP]
> 对于 `Ubuntu` 或 `Debian`，可能还需要 `python-is-python3`
>
> 如果您在安装依赖项时遇到问题，只需创建一个新的 GitHub Codespace 并在那里运行命令

#### 自定义 Nerd-Font

如果您想获得固定宽度的图标，请在 `config.json` 中设置 `"nerd_font.mono": true` 或在构建脚本参数中添加 `--nf-mono` 标志。

如果您想获得可变宽度的图标，请在 `config.json` 中设置 `"nerd_font.propo": true` 或在构建脚本参数中添加 `--nf-propo` 标志。

对于自定义的 `font-patcher` 参数，需要 `font-forge`（也可能需要 `python3-fontforge`）。

您可能还应该在 [config.json](./config.json) 中更改 `"nerd_font.extra_args"`。

默认参数： `-l --careful --outputdir dir`
- 如果 `"nerd_font.propo"` 为 `true`，则添加 `--variable-width-glyphs`
- 否则，如果 `"nerd_font.mono"` 为 `true`，则添加 `--mono`

#### 预设

如果您想要获得固定宽度的 Nerd Font 图标，只需要在 `config.json` 中设置 `"nerd_font.mono": true` 或者在构建脚本中添加 `--nf-mono` 参数即可。

运行 `build.py` 时添加 `--normal` 参数，让字形不那么独特~~奇怪~~，就像 `JetBrains Mono` 一样（除了 `0` 的中间是斜线而不是点）。

如果您使用的是可变字体（不推荐），请启用 `calt` 特性以使所有特性正常工作。

启用的特性：
<!-- NORMAL -->
```
cv01, cv02, cv33, cv34, cv35, cv36, cv61, cv62, ss05, ss06, ss07, ss08
```
<!-- NORMAL -->

[在线预览](https://font.subf.dev/zh-cn/playground?normal)

#### 字体特性强制开启

有三种选项（[为什么](https://github.com/subframe7536/maple-font/issues/233#issuecomment-2410170270)）：

1. `enable`: 强制启用这些特性，而无需在字体特性配置中设置 `cvXX` / `ssXX` / `zero`，就像默认连字一样
2. `disable`: 删除 `cvXX` / `ssXX` / `zero` 中的特性，即使您手动启用它，也不在生效
3. `ignore`: 什么也不做

#### 自定义 OpenType Feature

OpenType Feature 可以控制字体的内置变体和连字。您可以通过修改 OpenType Feature 来删除一些不需要的连字或特征，修改特征的触发规则或添加一些新规则。

默认情况下，[`source/py/feature/`](./source/py/feature) 中的 Python 模块会生成 OpenType Feature 字符串并在构建时加载。您可以在此处修改功能或自定义标签。

如果你想通过修改 OpenType Feature 文件实现，运行 `build.py` 时添加 `--apply-fea-file` 参数，会读取 [`source/features/{regular,italic}{_cn,}.fea`](./source/features) 的特性文件并加载。

#### 无限箭头连字

受 Fira Code 的启发，从 v7.3 开始，该字体默认启用无限箭头连字。由于某种原因，在使用 Hinted 字体时连字会错位，因此在 v7.4 的 Hinted 版本中默认将其移除。

您可以在 `config.json` 中设置 `"infinite_arrow": true`，或在命令行标志中添加 `--infinite-arrow`。详情见 [#508](https://github.com/subframe7536/maple-font/issues/508)

#### 自定义字重映射

您可以通过 `config.json` 中的 `"weight_mapping"` 项修改静态字体粗细。

例如，如果您想让常规字重稍微细一些，只需将 `"weight_mapping.regular"` 的数值降低（在此示例中从 400 降到 350）：

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

### 中文版本

默认情况下不会生成中文字体，运行 `python build.py` 时添加 `--cn` 参数，中文基字（约 111 MB）将从 GitHub 下载。

如果您想从可变字体（约 27 MB）构建中文基字，请在 [config.json](./config.json) 中设置 `"cn.use_static_base_font": false` 并且**耐心等待**，可变字体静态化将花费大约 10-30 分钟。

#### 缩小中文字体的间距

如果您觉得中文字符的间距**过大**，有一个构建选项 `cn.narrow` 或 命令行参数 `--cn-narrow` 可以缩小间距，但是这将让字体无法被识别为等宽字体。

您可以在 [#249](https://github.com/subframe7536/maple-font/issues/249#issuecomment-2871260476) 中查看效果。

#### GitHub 镜像

构建脚本将自动从 GitHub 下载所需的资源。如果您在下载时遇到问题，请在 [config.json](./config.json) 中设置 `github_mirror` 或将 `$GITHUB` 设置为您的环境变量。（目标 URL 为 `https://<github_mirror>/<user>/<repo>/releases/download/<tag>/<file>`），或者直接下载目标 `.zip` 文件并将其放在与 `build.py` 相同的目录中。

#### 繁體中文標點符號支援

通過開啟 `cv99`，所有的中文標點符號都會居中，詳情見 [#150](https://github.com/subframe7536/maple-font/issues/150)

### 构建脚本用法

```
usage: build.py [-h] [-v] [-d] [--debug] [-n] [--feat FEAT] [--apply-fea-file]
                [--hinted | --no-hinted] [--liga | --no-liga] [--keep-infinite-arrow]
                [--infinite-arrow] [--remove-tag-liga] [--line-height LINE_HEIGHT]
                [--nf-mono] [--nf-propo] [--cn-narrow]
                [--cn-scale-factor CN_SCALE_FACTOR] [--nf | --no-nf] [--cn | --no-cn]
                [--cn-both] [--ttf-only] [--least-styles] [--font-patcher] [--cache]
                [--cn-rebuild] [--archive]

✨ Builder and optimizer for Maple Mono

options:
  -h, --help            显示此帮助信息并退出
  -v, --version         显示程序版本号并退出
  -d, --dry             输出配置并退出
  --debug               在字体名称中添加 `Debug` 后缀并加快构建速度

Feature Options:
  -n, --normal          使用 normal 预设，就像带斜杠零的 `JetBrains Mono`
  --feat FEAT           强制启用字体特性，用 `,` 分隔（例如 `--feat
                        zero,cv01,ss07,ss08`）。 对可变字体无效
  --apply-fea-file      从 `source/features/{regular,italic}.fea` 加载特性文件到
                        可变字体
  --hinted              在 NF / CN / NF-CN 中使用 hinted 字体作为基础字体（默认）
  --no-hinted           在 NF / CN / NF-CN 中使用 unhinted 字体作为基础字体
  --liga                保留所有连字（默认）
  --no-liga             删除所有连字
  --infinite-arrow      开启无限箭头连字 (默认在 hinted 格式中禁用)
  --remove-tag-liga     移除纯文本标签连字，例如 `[TODO]`
  --line-height LINE_HEIGHT
                        行高的缩放因子 (例如 1.1)
  --nf-mono             使 Nerd Font 图标的宽度固定
  --nf-propo            使 Nerd Font 图标的宽度不固定，覆盖 `--nf-mono`
  --cn-narrow           减小中文/日文字形间距（同时会让系统无法识别为等宽字体）
  --cn-scale-factor CN_SCALE_FACTOR
                        中文/日文字形的缩放因子。格式：<因子> 或
                        <宽度因子>,<高度因子> (例如 1.1 或 1.2,1.1)

Build Options:
  --nf, --nerd-font     构建 Nerd-Font 版本（默认）
  --no-nf, --no-nerd-font
                        不构建 Nerd-Font 版本
  --cn                  构建中文版本
  --no-cn               不构建中文版本（默认）
  --cn-both             同时构建 `Maple Mono CN` 和 `Maple Mono NF CN`。必须启用
                        Nerd-Font 版本
  --ttf-only            仅构建 TTF 格式
  --least-styles        仅构建 常规 / 粗体 / 斜体 / 粗斜体 样式
  --font-patcher        强制使用 Nerd Font Patcher 构建 NF 格式
  --cache               重用 TTF、OTF 和 Woff2 格式的字体缓存
  --cn-rebuild          重新静态化可变的中文基字
  --archive             构建带有配置和许可的字体压缩包。如果带有 `--cache`
                        标志，则仅打包 NF 和 CN 格式
```

## 我个人在用的其他中文字体资源

[cn-resource](https://github.com/subframe7536/maple-font/tree/other-resources/cn-resource)

## 鸣谢

- [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono)
- [Roboto Mono](https://github.com/googlefonts/RobotoMono)
- [Fira Code](https://github.com/tonsky/FiraCode)
- [Victor Mono](https://github.com/rubjo/victor-mono)
- [Commit Mono](https://github.com/eigilnikolajsen/commit-mono)
- [Code Sample](https://github.com/TheRenegadeCoder/sample-programs-website)
- [Nerd Font](https://github.com/ryanoasis/nerd-fonts)
- [Font Freeze](https://github.com/MuTsunTsai/fontfreeze/)
- [Font Viewer](https://tophix.com/font-tools/font-viewer)
- [Monolisa](https://www.monolisa.dev/)
- [Recursive](https://www.recursive.design/)

## 赞助

如果这个字体对您有所帮助，可以通过 [爱发电](https://afdian.com/a/subframe7536) 赞助我

## 点星

<a href="https://www.star-history.com/#subframe7536/maple-font&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=subframe7536/maple-font&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
 </picture>
</a>

## 许可

SIL Open Font License 1.1
