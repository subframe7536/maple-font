![封面圖](./resources/header.png)

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
  <a href="#安裝">下載</a> |
  <a href="https://font.subf.dev">網站</a> |
  <a href="https://font.subf.dev/en/playground">線上體驗</a> |
  <a href="#文件">文件</a> |
  <a href="./README.md">English</a> |
  <a href="./README_CN.md">简中</a> |
  繁中 |
  <a href="./README_JP.md">日本語</a> |
  <a href="./README_KR.md">한국어</a>
</p>

> [!WARNING]
> 目前分支為 V8 版本，仍在開發中，尚未正式發佈。如果你需要使用穩定版本，請前往 [`v7` 分支](https://github.com/subframe7536/maple-font/tree/v7)。

# Maple Mono

Maple Mono 是一款開源等寬字型，致力於讓編碼體驗更加舒適、高效。我製作它是為了提升自己的工作效率，也希望它能幫助更多人更愉快地編寫程式碼。

## 特色

- ✨ **可變字重** - 支援連續調整字重，並針對斜體字形進行細緻優化，讓排版控制更加靈活。
- ☁️ **圓角字形** - 全面採用圓角設計，重繪 `@ $ % & Q ->` 等關鍵符號，優化斜體連筆（`f i j k l x y`）。
- 🪄 **智慧連字** - 支援大量智慧連字，提供豐富的字元變體和 OpenType 樣式集，內建標籤連字，讓程式碼更易讀，也更有表現力。
- 🔣 **Unicode 擴充涵蓋** - 涵蓋製表符、盲文、數學運算子（U+2200–U+22FF）、國際象棋與撲克牌符號、終端機狀態與進度符號，以及 Claude Code 狀態載入符號。
- 🎨 **Nerd Font 圖示** - 原生整合 [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts)，相容各類開發工具和終端機環境，讓介面資訊更清晰易讀。
- 🀄 **CJK 2:1 對齊** - 簡體中文、繁體中文、日文與韓文字形寬度恰好為拉丁字元的兩倍，多語言文字和 Markdown 表格保持整齊。
- 📏 **三種字寬** - 提供 default、narrow、slim 三種字元寬度。
- 🔨 **高度可自訂** - 支援設定 OpenType 特性、標籤連字、行高、字元寬度和字重映射，也可以從原始碼產生專屬字型。

## 預覽

![showcase.png](./resources/showcase.webp)

生成工具：[CodeImg](https://github.com/subframe7536/vscode-codeimg)，主題：[Maple](https://github.com/subframe7536/vscode-theme-maple)，字號 16px、行高 1.8、預設字母間距。

## 連字與變體

Maple Mono 提供智慧連字（透過 `calt` 啟用）、字元變體（`cvXX`）和樣式集（`ssXX`），絕大多數現代作業系統、瀏覽器、終端機和編輯器都支援。完整列表請參閱 [OpenType 特性](./documentation/opentype-features.md)，也可以在[線上體驗](https://font.subf.dev/en/playground)中即時預覽。

## 樣式一覽

- **Normal 預設** - 風格更中性，字形類似 `JetBrains Mono`，`0` 中間為斜線。
- **無限箭頭連字** - 受 Fira Code 和 Cascadia Code 啟發，箭頭連字可以無限延長。
- **三種字寬** - 拉丁字元寬度可選 default（600）、narrow（550）、slim（500）。
- **Nerd Font 圖示** - 圖示間距可選預設、固定寬度（`NFMono`）或可變寬度（`NFPropo`）。

| Normal 預設                                          | 無限箭頭連字                                                          |
| ---------------------------------------------------- | --------------------------------------------------------------------- |
| ![Normal preset](./resources/preview-normal.webp)    | ![Infinite arrow ligatures](./resources/preview-infinite-arrows.webp) |
| **字寬**                                             | **Nerd Font 圖示**                                                    |
| ![Width comparison](./resources/preview-widths.webp) | ![Nerd Font spacing modes](./resources/preview-nerd-fonts.webp)       |

各樣式的建置方法請參閱[建置選項](./documentation/build-options.md)。

## CJK

CJK 字元與英文字元按 2:1 的寬度對齊，讓多語言文字和 Markdown 表格保持整齊；相應地，預設 CJK 字元的間距會比其他常見中文字型更寬（[原因](https://github.com/subframe7536/maple-font/issues/211)）。與 V7 相比，V8 大幅擴充並優化了 CJK 字集。

| 地區 | 涵蓋範圍                               | CJK 字型來源                                                                             |
| ---- | -------------------------------------- | ---------------------------------------------------------------------------------------- |
| CN   | 簡體中文，並涵蓋常用繁體中文與日文字元 | [WenYuan Rounded SC](https://github.com/takushun-wu/WenYuanFonts)                        |
| TC   | 繁體中文                               | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)                 |
| JP   | 日文                                   | [Resource Han Rounded JP](https://github.com/CyanoHao/Resource-Han-Rounded)              |
| KR   | 韓文                                   | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)，按韓文區域篩選 |

![2-1.png](./resources/2-1.png)

詳情請參閱 [CJK 建置](./documentation/cjk.md)。

## 安裝

你可以從 [Releases](https://github.com/subframe7536/maple-font/releases/latest) 下載字型壓縮包，或透過套件管理器安裝最常用的 Maple Mono NF：

```sh
# Scoop (Windows)
scoop bucket add nerd-fonts
scoop install Maple-Mono-NF
# Homebrew (macOS, Linux)
brew install --cask font-maple-mono-nf
# Arch Linux (archlinuxcn)
paru -S ttf-maplemono-nf-unhinted
# Nixpkgs：將 `maple-mono.NF-unhinted` 加入 `fonts.packages`
```

套件管理器目前提供的是 v7.9 版本。CDN：[fontsource](https://fontsource.org/fonts/maple-mono)、[ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/)；Maple Mono CN：[中文網字計劃](https://chinese-font.netlify.app/zh-cn/fonts/maple-mono-cn/MapleMono-CN-Regular)、[ZeoSeven Fonts](https://fonts.zeoseven.com/items/442/)。所有套件請參閱[安裝指南](./documentation/install.md)。

## 我該選擇哪個檔案？

| 使用場景     | 推薦選擇                              |
| ------------ | ------------------------------------- |
| 日常編碼     | `TTF` 或 `OTF`                        |
| 終端機圖示   | `NF`、`NFMono` 或 `NFPropo`           |
| 圖示與 CJK   | `NF-CN`、`NF-TC`、`NF-JP` 或 `NF-KR`  |
| 網頁         | `WOFF2`                               |

所有套件及 hinted / unhinted 的差異請參閱[字型選擇](./documentation/choose.md)。

## 使用

VS Code、JetBrains IDE、Zed、Windows Terminal、Kitty 和 Ghostty 的設定方法請參閱[使用指南](./documentation/usage.md)。

## 自行建置

上面的所有特色都可以在建置時透過 [`config.json`](./config.json) 或 `build.py` 參數調整。你可以在[線上體驗](https://font.subf.dev/en/playground)中直接建置，也可以使用 [GitHub Actions](https://github.com/subframe7536/maple-font/actions/workflows/custom.yml) 雲端建置，或透過 Docker / Python 本機建置，詳情請參閱[自訂建置](./documentation/build.md)。

## 文件

文件目前僅提供英文版本。

- **入門**：[安裝](./documentation/install.md) · [命名與字型選擇](./documentation/choose.md) · [使用](./documentation/usage.md) · [OpenType 特性](./documentation/opentype-features.md)
- **建置**：[自訂建置](./documentation/build.md) · [建置選項](./documentation/build-options.md) · [CJK 建置](./documentation/cjk.md) · [`build.py` 命令列參考](./documentation/cli.md)
- **參與開發**：[開發](./documentation/development.md) · [Google Fonts 建置與 QA](./documentation/google-fonts.md)

## 鸣謝

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

## 贊助

如果這款字型對你有所幫助，歡迎透過[愛發電](https://afdian.com/a/subframe7536)贊助我。

## Star History

<a href="https://star-history.dera.page/#subframe7536/maple-font&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
 </picture>
</a>

## 授權條款

SIL Open Font License 1.1
