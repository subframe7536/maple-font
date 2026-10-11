![カバー画像](./resources/header.png)

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
  <a href="#インストール">ダウンロード</a> |
  <a href="https://font.subf.dev">ウェブサイト</a> |
  <a href="https://font.subf.dev/en/playground">Playground</a> |
  <a href="#ドキュメント">ドキュメント</a> |
  <a href="./README.md">English</a> |
  <a href="./README_CN.md">简中</a> |
  <a href="./README_TC.md">繁中</a> |
  日本語 |
  <a href="./README_KR.md">한국어</a>
</p>

> [!WARNING]
> このブランチは V8 で、現在開発中のためまだ正式リリースされていません。安定版が必要な場合は [`v7` ブランチ](https://github.com/subframe7536/maple-font/tree/v7) を使用してください。

# Maple Mono

Maple Mono は、コーディングをより快適かつ効率的にすることを目指したオープンソースの等幅フォントです。自分の作業効率を高めるために制作しました。このフォントが、より多くの人に楽しくコードを書いてもらう助けになればと思っています。

## 特徴

- ✨ **可変ウェイト** - ウェイトを連続的に調整でき、斜体グリフも細かく最適化しています。
- ☁️ **丸みのあるグリフ** - 全体に丸みを持たせ、`@ $ % & Q ->` などを再設計し、斜体の連結（`f i j k l x y`）を改善しています。
- 🪄 **スマートリガチャ** - 多数のスマートリガチャ、文字バリアント、OpenType スタイルセット、組み込みのラベル用リガチャを利用できます。
- 🔣 **Unicode の拡張カバレッジ** - 罫線文字、点字、数学演算子（U+2200–U+22FF）、チェスとカードの記号、ターミナルの状態・進捗記号、Claude Code のローディング記号を含みます。
- 🎨 **Nerd Font アイコン** - [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) を標準で統合し、開発ツールやターミナルで利用できます。
- 🀄 **CJK の 2:1 整列** - 簡体字中国語、繁体字中国語、日本語、韓国語のグリフ幅はラテン文字のちょうど 2 倍で、多言語テキストや Markdown テーブルが揃います。
- 📏 **3 種類の文字幅** - default、narrow、slim の 3 種類の文字幅を用意しています。
- 🔨 **高いカスタマイズ性** - OpenType 機能、タグ用リガチャ、行の高さ、文字幅、ウェイトマッピングを設定でき、ソースから専用フォントを生成できます。

## CJK

多言語テキストや Markdown テーブルを整列させるため、CJK 文字と英字は 2:1 の幅で揃います。その代わり、標準の CJK 文字間隔は一般的な日本語フォントより広くなっています（[理由](https://github.com/subframe7536/maple-font/issues/211)）。V7 と比べて、V8 では CJK 文字セットを大幅に拡張・改善しています。

| 地域 | 対応範囲                                         | CJK フォントのソース                                                                         |
| ---- | ------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| CN   | 簡体字中国語、一般的な繁体字中国語と日本語を含む | [WenYuan Rounded SC](https://github.com/takushun-wu/WenYuanFonts)                            |
| TC   | 繁体字中国語                                     | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)                     |
| JP   | 日本語                                           | [Resource Han Rounded JP](https://github.com/CyanoHao/Resource-Han-Rounded)                  |
| KR   | 韓国語                                           | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)、韓国語の範囲を抽出 |

![2-1.png](./resources/2-1.png)

詳しくは [CJK ビルド](./documentation/cjk.md)をご覧ください。

## プレビュー

![showcase.png](./resources/showcase.webp)

生成ツール：[CodeImg](https://github.com/subframe7536/vscode-codeimg)、テーマ：[Maple](https://github.com/subframe7536/vscode-theme-maple)、フォントサイズ 16px、行の高さ 1.8、デフォルトの文字間隔。

## リガチャとバリアント

Maple Mono はスマートリガチャ（`calt` で有効化）、文字バリアント（`cvXX`）、スタイルセット（`ssXX`）を備えており、ほとんどの最新の OS、ブラウザー、ターミナル、エディターで利用できます。完全な一覧は [OpenType 機能](./documentation/opentype-features.md)を参照するか、[Playground](https://font.subf.dev/en/playground) で試してください。

## スタイル一覧

- **Normal プリセット** - `JetBrains Mono` に近い、癖の少ないグリフ（スラッシュ付きの `0`）。
- **無限矢印リガチャ** - Fira Code と Cascadia Code に着想を得た、任意の長さに伸びる矢印リガチャ。
- **3 種類の文字幅** - ラテン文字幅は default（600）、narrow（550）、slim（500）から選べます。
- **Nerd Font アイコン** - アイコン幅はデフォルト、固定幅（`NFMono`）、可変幅（`NFPropo`）から選べます。

| Normal プリセット                                    | 無限矢印リガチャ                                                      |
| ---------------------------------------------------- | --------------------------------------------------------------------- |
| ![Normal preset](./resources/preview-normal.webp)    | ![Infinite arrow ligatures](./resources/preview-infinite-arrows.webp) |
| **文字幅**                                           | **Nerd Font アイコン**                                                |
| ![Width comparison](./resources/preview-widths.webp) | ![Nerd Font spacing modes](./resources/preview-nerd-fonts.webp)       |

各スタイルのビルド方法は[ビルドオプション](./documentation/build-options.md)をご覧ください。

## インストール

[Releases](https://github.com/subframe7536/maple-font/releases/latest) からフォントのアーカイブをダウンロードするか、パッケージマネージャーで最も一般的な Maple Mono NF をインストールできます：

```sh
# Scoop (Windows)
scoop bucket add nerd-fonts
scoop install Maple-Mono-NF
# Homebrew (macOS, Linux)
brew install --cask font-maple-mono-nf
# Arch Linux (archlinuxcn)
paru -S ttf-maplemono-nf-unhinted
# Nixpkgs: `maple-mono.NF-unhinted` を `fonts.packages` に追加
```

パッケージマネージャーで現在提供されているのは v7.9 です。CDN：[fontsource](https://fontsource.org/fonts/maple-mono)、[ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/)。Maple Mono CN：[The Chinese Web Fonts Plan](https://chinese-font.netlify.app/zh-cn/fonts/maple-mono-cn/MapleMono-CN-Regular)、[ZeoSeven Fonts](https://fonts.zeoseven.com/items/442/)。すべてのパッケージは[インストールガイド](./documentation/install.md)をご覧ください。

## どのファイルを選べばよいですか？

| 用途                   | 推奨                                  |
| ---------------------- | ------------------------------------- |
| 一般的なコーディング   | `TTF` または `OTF`                    |
| ターミナルのアイコン   | `NF`、`NFMono`、`NFPropo`             |
| アイコンと CJK         | `NF-CN`、`NF-TC`、`NF-JP`、`NF-KR`    |
| ウェブページ           | `WOFF2`                               |

すべてのパッケージと hinted / unhinted の違いは[フォントの選択](./documentation/choose.md)をご覧ください。

## 使用方法

VS Code、JetBrains IDE、Zed、Windows Terminal、Kitty、Ghostty の設定方法は[使用ガイド](./documentation/usage.md)をご覧ください。

## 自分でビルドする

上記の特徴はすべて、[`config.json`](./config.json) または `build.py` のオプションでビルド時に調整できます。[Playground](https://font.subf.dev/en/playground) でブラウザー上から、[GitHub Actions](https://github.com/subframe7536/maple-font/actions/workflows/custom.yml) でクラウド上から、または Docker / Python でローカルにビルドできます。詳しくは[カスタムビルド](./documentation/build.md)をご覧ください。

## ドキュメント

ドキュメントは現在英語のみです。

- **はじめに**：[インストール](./documentation/install.md) · [命名規則とフォントの選択](./documentation/choose.md) · [使用方法](./documentation/usage.md) · [OpenType 機能](./documentation/opentype-features.md)
- **ビルド**：[カスタムビルド](./documentation/build.md) · [ビルドオプション](./documentation/build-options.md) · [CJK ビルド](./documentation/cjk.md) · [`build.py` CLI リファレンス](#buildpy-cli)
- **開発に参加**：[開発](./documentation/development.md) · [Google Fonts のビルドと QA](./documentation/google-fonts.md)

<a id="buildpy-cli"></a>

## `build.py` コマンドラインオプション

```text
使い方: build.py [-h] [-v] [-d] [--debug] [-n] [--standard-zero]
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

Maple Mono のビルダーおよびオプティマイザー

オプション:
  -h, --help            このヘルプメッセージを表示して終了
  -v, --version         プログラムのバージョンを表示して終了
  -d, --dry             設定を出力して終了
  --debug               高速なデバッグビルドを使用します。`Debug` を追加し、
                        デバッグログを有効にして Regular/Italic のみをビルドし、
                        OTF/WOFF2/Nerd Font の出力をスキップします

機能オプション:
  -n, --normal          `JetBrains Mono` のような Normal プリセットを使用します。
                        `0` はスラッシュ付きになります
  --standard-zero       標準の zero の意味を使用します。デフォルトの 0 はドット付きで、
                        `zero` を有効にするとスラッシュ付きになります
  --legacy-thin-weight-class
                        Thin および ExtraLight の静的フォントに、Windows 上の
                        JetBrains IDE の GDI 擬似ボールド問題を回避するため、
                        レガシー weight class 値（100/200 の代わりに 250/275）を使用します
  --feat FEAT           指定した機能を有効化して固定します。`,` で区切って指定します
                        （例: `--feat zero,cv01,ss07,ss08`）。コンテキストルールは
                        `calt` で有効になります
  --apply-fea-file      対応する
                        `sources/features/{regular,italic}{_cn,}.fea` を静的・可変フォントに適用します
  --hinted              NF/CJK/NF-CJK の基底フォントにヒンティング済みフォントを使用します（デフォルト）
  --no-hinted           NF/CJK/NF-CJK の基底フォントにヒンティングなしフォントを使用します
  --liga                すべてのリガチャを保持します（デフォルト）
  --no-liga             すべてのリガチャを削除します
  --infinite-arrow      無限矢印リガチャのサポートを追加します（デフォルト）
  --no-infinite-arrow   無限矢印リガチャのサポートを追加しません
  --remove-tag-liga     `[TODO]` のようなプレーンテキストのタグリガチャを削除します
  --line-height LINE_HEIGHT
                        行の高さの倍率（例: 1.1）
  --width {default,narrow,slim}
                        グリフ幅を設定します: default（600）、narrow（550）、slim（500）

ビルドオプション:
  --format FORMATS      必要な基本出力形式をカンマ区切りで選択します: ttf、otf、woff2。
                        可変フォントの基底版は常にビルドされます
  --least-styles        Regular / Bold / Italic / BoldItalic スタイルのみビルドします
  --cache               `fonts/` 下の有効なキャッシュ済みパイプライン段階を再利用し、
                        無関係な既存出力を保持します
  --archive             設定とライセンスを添えて、既存の各非 JSON 出力ディレクトリをアーカイブします

Nerd Font オプション:
  --nf, --nerd-font     Nerd Font 版をビルドします（デフォルト）
  --no-nf, --no-nerd-font
                        Nerd Font 版をビルドしません
  --nf-mono             Nerd Font アイコンの幅を固定します
  --nf-propo            Nerd Font アイコンの幅を可変にし、`--nf-mono` を上書きします
  --nf-variable         Nerd Font を可変フォントとしてビルドします
  --font-patcher        Nerd Font Patcher を使って NF 形式をビルドするよう強制します

CJK オプション:
  --cjk CJK             ロケール cn、jp、tc、kr 向けの Maple Mono + CJK 拡張フォントを
                        ビルドします。繰り返し指定するか、カンマ区切りで指定できます
  --cjk-variable        CJK 拡張出力を結合済み可変フォントとして保持します
  --cjk-narrow          選択したロケールに狭い CJK 字間を適用します
  --cjk-scale-factor CJK_SCALE_FACTOR
                        選択した CJK ロケールの倍率。形式は次のいずれかです:
                        <factor> または <width_factor>,<height_factor>
  --cjk-both            Nerd Font が有効な場合、NF CJK と非 NF CJK の両方を出力します
  --cjk-hinted          最終的な静的 CJK フォントに自動ヒンティングを適用します
  --no-cjk-hinted       最終的な静的 CJK フォントに自動ヒンティングを適用しません（デフォルト）

非推奨の CN オプション:
  --cn                  非推奨。`--cjk cn` のエイリアスです
  --no-cn               非推奨。選択した CJK ロケールから `cn` を削除するエイリアスです
  --cn-narrow           非推奨。`cn` を対象にした `--cjk-narrow` のエイリアスです
  --cn-scale-factor CN_SCALE_FACTOR
                        非推奨。`cn` を対象にした `--cjk-scale-factor` のエイリアスです
  --cn-both             非推奨。`--cjk-both` のエイリアスです
```

## クレジット

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

## スポンサー

このフォントがお役に立ちましたら、[愛発電](https://afdian.com/a/subframe7536)からスポンサーになっていただけると幸いです。

## Star History

<a href="https://star-history.dera.page/#subframe7536/maple-font&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
 </picture>
</a>

## ライセンス

SIL Open Font License 1.1
