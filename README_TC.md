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
  <a href="#下載與安裝">下載</a> |
  <a href="https://font.subf.dev">網站</a> |
  <a href="./README.md">English</a> |
  <a href="./README_CN.md">簡中</a> |
  繁中 |
  <a href="./README_JP.md">日本語</a> |
  <a href="./README_KR.md">한국어</a>
</p>

> [!WARNING]
> V8 版本仍在開發中，尚未正式發佈。如果你需要使用穩定版本，請前往 [`v7` 分支](https://github.com/subframe7536/maple-font/tree/v7)。

# Maple Mono

Maple Mono 是一款開源等寬字型，致力於讓編碼體驗更加舒適、高效。

我製作它是為了提升自己的工作效率，也希望它能幫助更多人更愉快地編寫程式碼。

## 為什麼選擇 Maple Mono？

- ✨ **可變字型支援** - 支援連續調整字重，並針對斜體字形進行細緻優化，讓排版控制更加靈活。
- ☁️ **圓角與視覺優化** - 全面採用圓角設計，重繪 `@ $ % & Q ->` 等關鍵符號，優化斜體連筆（`f i j k l x y`），並提供多種字元寬度模式。
- 🪄 **智慧連字增強** - 支援大量智慧連字，提供豐富的字元變體和 OpenType 樣式集，內建標籤連字，讓程式碼更易讀，也更有表現力。
- 🔣 **Unicode 擴充涵蓋** - 涵蓋製表符、盲文、數學運算子（U+2200–U+22FF）、國際象棋與撲克牌符號、終端機狀態與進度符號，以及 Claude Code 狀態載入符號，適用於科學計算和開發場景。
- 🎨 **Nerd Font 圖示支援** - 原生整合 [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts)，相容各類開發工具和終端機環境，讓介面資訊更清晰易讀。
- 🔨 **高度可自訂建置** - 支援強制啟用 OpenType 特性、自訂標籤連字、行高、字元寬度和字重映射，也可以從原始碼產生專屬字型。

### 簡體中文、繁體中文、日文與韓文

Maple Mono 支援 CJK 字集。與 V7 相比，V8 大幅擴充並優化了 CJK 字集，涵蓋簡體中文、繁體中文、日文與韓文。為了讓多語言文字和 Markdown 表格保持整齊，CJK 字元與英文字符按 2:1 的寬度對齊；相應地，預設 CJK 字元的間距會比其他常見中文字型更寬，詳見[這個議題](https://github.com/subframe7536/maple-font/issues/211)。

| 地區 | 涵蓋範圍                               | CJK 字型來源                                                                             | 建置輸出 |
| ---- | -------------------------------------- | ---------------------------------------------------------------------------------------- | -------- |
| CN   | 簡體中文，並涵蓋常用繁體中文與日文字符 | [WenYuan Rounded SC](https://github.com/takushun-wu/WenYuanFonts)                        | `CN`     |
| TC   | 繁體中文                               | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)                 | `TC`     |
| JP   | 日文                                   | [Resource Han Rounded JP](https://github.com/CyanoHao/Resource-Han-Rounded)              | `JP`     |
| KR   | 韓文                                   | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)，按韓文區域篩選 | `KR`     |

CJK 建置預設關閉。你可以透過 CJK 建置設定選擇地區、靜態或可變輸出，以及是否啟用緊湊寬度模式。

<!--
|Go|od| t|yp|og|ra|ph|y |re|ad|s |ea|si|ly|
|优|美|的|字|体|让|阅|读|变|得|更|加|轻|松|
|優|美|的|字|體|讓|閱|讀|變|得|更|加|輕|鬆|
|美|し|い|書|体|は|も|っ|と|読|み|や|す|い|
|아|름|다|운|글|꼴|은|더|읽|기|가|편|해|요|
|1!|2@|3#|4$|5%|6^|7&|8*|9(|0)|_+|{}|[]|;:|
-->

![2-1.png](./resources/2-1.png)

## 預覽

![showcase.png](./resources/showcase.webp)

- 生成工具：[CodeImg](https://github.com/subframe7536/vscode-codeimg)
- 主題：[Maple](https://github.com/subframe7536/vscode-theme-maple)
- 設定：字號 16px、行高 1.8、預設字母間距

## 開始使用

### 下載與安裝

你可以從 [Releases](https://github.com/subframe7536/maple-font/releases/latest) 下載字型壓縮包。

你也可以透過 Scoop、Homebrew、AUR/Paru、NixPkgs 等套件管理器安裝 Maple Mono，詳情請參閱[安裝指南](./docs/install.md)。

### 使用與特性設定

使用方法和設定說明請參閱[使用指南](./docs/usage.md)。

#### 命名說明與字型選擇

Maple Mono 根據使用者回饋，在發行版中提供多種字型格式和字元集範圍。你可以根據使用場景選擇合適的字型檔案，詳情請參閱[字型選擇](./docs/choose.md)。

### CDN

### Maple Mono

- [fontsource](https://fontsource.org/fonts/maple-mono)
- [ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/)

## 特色介紹

你可以在[page#todo]()預覽所有特色。

### 自訂建置

Maple Mono 提供高度可自訂的建置方式。你可以修改 [`config.json`](./config.json)，或在命令列中加入參數，產生符合需求的字型檔案，詳情請參閱[自訂建置](./docs/build.md)。

查看完整的 [`build.py` 命令列選項](#buildpy-cli)。

### 窄字元

在 V8 中，Maple Mono 提供三種字元寬度模式。你可以修改 [`config.json`](./config.json) 中的 `"width"` 欄位，或在命令列中加入參數 `--width <mode>` 來選擇寬度模式。

可選模式如下：

- default: 600
- narrow: 550
- slim: 500

![Width comparison](./resources/preview-widths.webp)

### OpenType 特性開關

「OpenType 特性」用於控制字型內建的變體和連字，絕大多數現代作業系統、瀏覽器、終端機和編輯器都支援它。你可以透過啟用或停用 OpenType 特性來控制連字和字元樣式。

Maple Mono 提供大量細粒度的 OpenType 特性。為了減少設定成本，建置時可以為這些特性選擇三種處理方式（[原因](https://github.com/subframe7536/maple-font/issues/233#issuecomment-2410170270)）：

1. `enable`：強制啟用這些特性，無需在字型特性設定中設定 `cvXX` / `ssXX` / `zero`，行為類似預設連字。
2. `disable`：移除 `cvXX` / `ssXX` / `zero` 中的特性，即使手動啟用也不會生效。
3. `ignore`：保持預設行為，不做任何處理。

### Normal 預設

Maple Mono 的預設字形設計偏向獨特和個人化，可能不適合所有人的審美或使用場景。因此 Maple Mono 提供 `--normal` 建置預設，產生類似 `JetBrains Mono` 的字形（`0` 的中間為斜線，而不是圓點）。

`--normal` 會啟用以下特性：

```
cv01, cv02, cv33, cv34, cv35, cv36, cv61, cv62, ss05, ss06, ss07, ss08
```

![Normal preset](./resources/preview-normal.webp)

#### 自訂 OpenType 特性

絕大多數字型不支援自訂 OpenType 特性，而 Maple Mono 支援透過程式設計方式定製這些特性。

預設情況下，[`scripts/feature/`](./scripts/feature) 中的 Python 模組會產生 OpenType 特性程式碼，並在建置時載入。你可以修改這些模組來調整功能或自訂標籤；如果希望直接編輯 OpenType 特性原始檔（`.fea`），請在執行 `build.py` 時加入 `--apply-fea-file` 參數，建置腳本會讀取並載入 [`source/features/{regular,italic}{_cn,}.fea`](./source/features) 中的特性檔案。

### 無限箭頭連字

受 Fira Code 和 Cascadia Code 啟發，Maple Mono 從 v7.3 開始支援無限箭頭連字。由於渲染方面的未知原因，Hinted 字型中的箭頭連字可能發生錯位，因此 v7.4 起的 Hinted 版本預設移除了該特性。

你可以在 `config.json` 中設定 `"infinite_arrow": true`，或在命令列中加入 `--infinite-arrow` 強制啟用該特性。遇到問題時，請在[#508](https://github.com/subframe7536/maple-font/issues/508)中討論。

![Infinite arrow ligatures](./resources/preview-infinite-arrows.webp)

### 標準 Zero 特性

預設情況下，`0` 是斜線樣式，啟用 `zero` 後顯示圓點。使用 `--standard-zero` 可恢復標準的 OpenType 語義：`0` 預設顯示圓點，啟用 `zero` 後顯示斜線。

### 自訂行高

Maple Mono 的預設行高為 `1`。你可以修改 [`config.json`](./config.json) 中的 `"line_height"` 欄位，或在命令列中加入參數 `--line-height <value>` 來調整行高；最終行高的計算公式為 `(ascender - descender) * line_height`。

### 自訂 Unicode 映射

如果 Maple Mono 缺少某些 Unicode 碼點，相關字元可能無法顯示。你可以修改 [`config.json`](./config.json) 中的 `"codepoint_alias"` 項目，自訂 Unicode 映射。

例如，將現有字元映射到另一個 Unicode 碼點：

```json
{
  "codepoint_alias": {
    "U+E000": "U+E001",
    "U+E002": "U+E003"
  }
}
```

### 自訂字重映射

你可以透過 `config.json` 中的 `"weight_mapping"` 項目修改靜態字型的粗細。

例如，要讓常規字重稍微變細，只需降低 `"weight_mapping.regular"` 的數值（本例從 400 調整為 350）：

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

### 自訂 Nerd Font 設定

Maple Mono 內建 Nerd Font 圖示支援，並遵循其命名規則。預設情況下，每個圖示使用一個拉丁字元的字寬，但其字形寬度可能不同。

- 如果需要讓圖示佔用一個拉丁字元的寬度（Nerd Font Mono），請在 `config.json` 中設定 `"nerd_font.mono": true`，或在建置參數中加入 `--nf-mono`。
- 如果需要使用可變寬度圖示（Nerd Font Propo），請在 `config.json` 中設定 `"nerd_font.propo": true`，或在建置參數中加入 `--nf-propo`。

如果要自訂 `font-patcher` 參數，需要安裝 `fontforge`（可能還需要 `python3-fontforge`）。你也可能需要在 [config.json](./config.json) 中修改 `"nerd_font.extra_args"`。

![Nerd Font spacing modes](./resources/preview-nerd-fonts.webp)

#### 參數解析規則

預設參數：`-l --careful --outputdir dir`

- 當 `"nerd_font.propo"` 為 `true` 時，加入 `--variable-width-glyphs`。
- 當 `"nerd_font.mono"` 為 `true` 時，加入 `--mono`。

## CJK 版本（繁體中文）

預設情況下不會生成繁體中文字型。執行 `python build.py` 時加入 `--cjk tc` 參數，建置腳本會從 [GitHub Release](https://github.com/subframe7536/maple-font/releases/tag/cjk-base) 下載繁體中文基礎字形。

### 縮小 CJK 字型的間距

如果只有 CJK 字元的間距**過大**，而拉丁字母的間距正常，可以透過建置選項 `cjk.narrow` 或命令列參數 `--cjk-narrow` 縮小 CJK 字元間距，但這會導致字型無法再被識別為等寬字型。

你可以在[#249](https://github.com/subframe7536/maple-font/issues/249#issuecomment-2871260476)中查看效果或參與討論。

- 如果還想改變拉丁字母的寬度，請使用[`--width` 參數](#窄字元)。

### 置中全形標點支援

Maple Mono 支援 `cpct` 特性，讓全形標點置中顯示；也可以啟用 `cv99` 特性強制套用該效果，詳情請參閱[#150](https://github.com/subframe7536/maple-font/issues/150)。

### GitHub 鏡像

建置腳本會自動從 GitHub 下載所需資源。如果下載失敗，可以在 [config.json](./config.json) 中設定 `github_mirror`，或將 `$GITHUB` 設定為環境變數。目標 URL 格式為 `https://<github_mirror>/<user>/<repo>/releases/download/<tag>/<file>`；也可以直接下載目標 `.zip` 檔案，並將它放在 `build.py` 所在目錄中。

<a id="buildpy-cli"></a>

## `build.py` 命令列選項

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

Maple Mono 建置與最佳化工具

選項：
  -h, --help            顯示此說明並結束
  -v, --version         顯示程式版本並結束
  -d, --dry             輸出設定並結束
  --debug               使用快速除錯建置：加入 `Debug`、啟用除錯記錄、
                        僅建置 Regular/Italic，並略過 OTF/WOFF2/Nerd Font 輸出

特性選項：
  -n, --normal          使用 Normal 預設，產生類似 `JetBrains Mono` 的字形，
                        其中 0 使用斜線樣式
  --standard-zero       使用標準 zero 語義：預設顯示圓點，啟用 `zero` 後顯示斜線
  --feat FEAT           啟用並凍結指定特性，以逗號分隔
                        （例如 `--feat zero,cv01,ss07,ss08`）；上下文規則透過
                        `calt` 啟用
  --apply-fea-file      將符合的
                        `source/features/{regular,italic}{_cn,}.fea` 套用到靜態與可變字型
  --hinted              在 NF/CJK/NF-CJK 中使用 Hinted 字型作為基礎字型（預設）
  --no-hinted           在 NF/CJK/NF-CJK 中使用未加提示的字型作為基礎字型
  --liga                保留所有連字（預設）
  --no-liga             移除所有連字
  --infinite-arrow      啟用無限箭頭連字（Hinted 字型預設停用）
  --remove-tag-liga     移除類似 `[TODO]` 的純文字標籤連字
  --line-height LINE_HEIGHT
                        行高縮放因子（例如 1.1）
  --width {default,narrow,slim}
                        設定字形寬度：default（600）、narrow（550）、slim（500）

建置選項：
  --format FORMATS      以逗號分隔的清單選擇所需基礎輸出格式：ttf、otf、woff2；
                        可變字型基礎版本一律會建置
  --least-styles        僅建置 Regular/Bold/Italic/BoldItalic 樣式
  --cache               重複使用 `fonts/` 下有效的快取流程階段，並保留其他現有輸出
  --archive             使用設定與授權條款，封存每個現有的非 JSON 輸出目錄

Nerd Font 選項：
  --nf, --nerd-font     建置 Nerd Font 版本（預設）
  --no-nf, --no-nerd-font
                        不建置 Nerd Font 版本
  --nf-mono             固定 Nerd Font 圖示的寬度
  --nf-propo            讓 Nerd Font 圖示寬度可變，覆蓋 `--nf-mono`
  --nf-variable         建置 Nerd Font 可變字型
  --font-patcher        強制使用 Nerd Font Patcher 建置 NF 格式

CJK 選項：
  --cjk CJK             建置 Maple Mono + CJK 擴充字型，地區為 cn、jp、tc、kr。
                        可重複指定或使用逗號分隔的值。
  --cjk-variable        將 CJK 擴充輸出保留為合併的可變字型
  --cjk-narrow          對選定地區套用窄 CJK 間距
  --cjk-scale-factor CJK_SCALE_FACTOR
                        設定選定 CJK 地區的縮放因子。格式為：
                        <factor> 或 <width_factor>,<height_factor>
  --cjk-both            啟用 Nerd Font 時，同時建置 NF CJK 與非 NF CJK 輸出
  --cjk-hinted          自動為最終靜態 CJK 字型加上提示
  --no-cjk-hinted       不為最終靜態 CJK 字型加上提示（預設）

已棄用的 CN 選項：
  --cn                  已棄用的 `--cjk cn` 別名
  --no-cn               已棄用的從所選 CJK 地區移除 `cn` 的別名
  --cn-narrow           已棄用的針對 `cn` 使用 `--cjk-narrow` 的別名
  --cn-scale-factor CN_SCALE_FACTOR
                        已棄用的針對 `cn` 使用 `--cjk-scale-factor` 的別名
  --cn-both             已棄用的 `--cjk-both` 別名
```

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

<a href="https://www.star-history.com/#subframe7536/maple-font&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=subframe7536/maple-font&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
 </picture>
</a>

## 授權條款

SIL Open Font License 1.1
