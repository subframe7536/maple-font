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
  <a href="#ダウンロードとインストール">ダウンロード</a> |
  <a href="https://font.subf.dev">ウェブサイト</a> |
  <a href="./README.md">English</a> |
  <a href="./README_CN.md">簡中</a> |
  <a href="./README_TC.md">繁中</a> |
  日本語 |
  <a href="./README_KR.md">한국어</a>
</p>

> [!WARNING]
> V8 は現在開発中で、まだ正式リリースされていません。安定版が必要な場合は [`v7` ブランチ](https://github.com/subframe7536/maple-font/tree/v7) を使用してください。

# Maple Mono

Maple Mono は、コーディングをより快適かつ効率的にすることを目指したオープンソースの等幅フォントです。

自分の作業効率を高めるために制作しました。このフォントが、より多くの人に楽しくコードを書いてもらう助けになればと思っています。

## Maple Mono を選ぶ理由

- ✨ **可変フォント対応** - ウェイトを連続的に調整でき、斜体グリフも細かく最適化しています。
- ☁️ **丸みのあるデザインと視覚的な改善** - 全体に丸みを持たせ、`@ $ % & Q ->` などを再設計し、斜体の連結（`f i j k l x y`）を改善しています。複数の文字幅モードにも対応します。
- 🪄 **スマートリガチャの強化** - 多数のスマートリガチャ、文字バリアント、OpenType スタイルセット、組み込みのラベル用リガチャを利用できます。
- 🔣 **Unicode の拡張カバレッジ** - 罫線文字、点字、数学演算子（U+2200–U+22FF）、チェスとカードの記号、ターミナルの状態・進捗記号、Claude Code のローディング記号を含みます。
- 🎨 **Nerd Font アイコン対応** - [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) を標準で統合し、開発ツールやターミナルで利用できます。
- 🔨 **高いカスタマイズ性** - OpenType 機能、カスタムタグ用リガチャ、行の高さ、文字幅、ウェイトマッピングを設定でき、ソースから専用フォントを生成できます。

### 簡体字中国語、繁体字中国語、日本語、韓国語

Maple Mono は CJK 文字セットに対応しています。V7 と比べて、V8 では CJK 文字セットを大幅に拡張・改善し、簡体字中国語、繁体字中国語、日本語、韓国語をカバーしています。多言語テキストや Markdown テーブルを整列させるため、CJK 文字と英字は 2:1 の幅で揃います。その代わり、標準の CJK 文字間隔は一般的な日本語フォントより広くなっています。詳しくは[この issue](https://github.com/subframe7536/maple-font/issues/211)をご覧ください。

| 地域 | 対応範囲                                         | CJK フォントのソース                                                                         | ビルド出力 |
| ---- | ------------------------------------------------ | -------------------------------------------------------------------------------------------- | ---------- |
| CN   | 簡体字中国語、一般的な繁体字中国語と日本語を含む | [WenYuan Rounded SC](https://github.com/takushun-wu/WenYuanFonts)                            | `CN`       |
| TC   | 繁体字中国語                                     | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)                     | `TC`       |
| JP   | 日本語                                           | [Resource Han Rounded JP](https://github.com/CyanoHao/Resource-Han-Rounded)                  | `JP`       |
| KR   | 韓国語                                           | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)、韓国語の範囲を抽出 | `KR`       |

CJK ビルドはデフォルトで無効です。CJK ビルド設定で対象地域、静的または可変出力、コンパクトな文字幅を選択できます。

<!--
|Go|od| t|yp|og|ra|ph|y |re|ad|s |ea|si|ly|
|优|美|的|字|体|让|阅|读|变|得|更|加|轻|松|
|優|美|的|字|體|讓|閱|讀|變|得|更|加|輕|鬆|
|美|し|い|書|体|は|も|っ|と|読|み|や|す|い|
|아|름|다|운|글|꼴|은|더|읽|기|가|편|해|요|
|1!|2@|3#|4$|5%|6^|7&|8*|9(|0)|_+|{}|[]|;:|
-->

![2-1.png](./resources/2-1.png)

## プレビュー

![showcase.png](./resources/showcase.webp)

- 生成ツール：[CodeImg](https://github.com/subframe7536/vscode-codeimg)
- テーマ：[Maple](https://github.com/subframe7536/vscode-theme-maple)
- 設定：フォントサイズ 16px、行の高さ 1.8、デフォルトの文字間隔

## はじめに

### ダウンロードとインストール

[Releases](https://github.com/subframe7536/maple-font/releases/latest) からフォントのアーカイブをダウンロードできます。

Scoop、Homebrew、AUR/Paru、NixPkgs などのパッケージマネージャーから Maple Mono をインストールすることもできます。詳しくは[インストールガイド](./docs/install.md)をご覧ください。

### 使用方法と機能設定

使用方法と設定については[使用ガイド](./docs/usage.md)をご覧ください。

#### 命名規則とフォントの選択

Maple Mono はユーザーからのフィードバックをもとに、複数のフォント形式と文字セット範囲を提供しています。用途に合ったフォントファイルを選択してください。詳しくは[フォントの選択](./docs/choose.md)をご覧ください。

### CDN

### Maple Mono

- [fontsource](https://fontsource.org/fonts/maple-mono)
- [ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/)

## 特徴

[page#todo]()ですべての特徴をプレビューできます。

### カスタムビルド

Maple Mono は高いカスタマイズ性を備えています。[`config.json`](./config.json) を変更するか、コマンドライン引数を追加して、必要なフォントを生成できます。詳しくは[カスタムビルド](./docs/build.md)をご覧ください。

完全な [`build.py` コマンドラインオプション一覧](#buildpy-cli)も参照してください。

### 文字幅の縮小

V8 では 3 種類の文字幅モードを利用できます。[`config.json`](./config.json) の `"width"` フィールドを変更するか、コマンドラインで `--width <mode>` を指定してください。

利用できるモード：

- default: 600
- narrow: 550
- slim: 500

![Width comparison](./resources/preview-widths.webp)

### OpenType 機能の切り替え

OpenType 機能はフォント内蔵のバリアントとリガチャを制御する仕組みで、現代の多くの OS、ブラウザ、ターミナル、エディターが対応しています。OpenType 機能を有効または無効にして、リガチャや文字スタイルを制御できます。

Maple Mono には細かく調整できる OpenType 機能が多数あります。設定の手間を減らすため、ビルド時に次の 3 つの処理方法を選べます（[理由](https://github.com/subframe7536/maple-font/issues/233#issuecomment-2410170270)）。

1. `enable`：`cvXX` / `ssXX` / `zero` を設定しなくても機能を強制的に有効にします。
2. `disable`：`cvXX` / `ssXX` / `zero` から機能を削除し、手動で有効にしても適用されません。
3. `ignore`：デフォルトの動作を維持します。

### Normal プリセット

Maple Mono のデフォルトのグリフデザインは個性的なため、すべての好みや用途に合うとは限りません。`--normal` ビルドプリセットでは、`JetBrains Mono` に似たグリフを生成します（`0` の中央は点ではなく斜線です）。

`--normal` は次の機能を有効にします：

```
cv01, cv02, cv33, cv34, cv35, cv36, cv61, cv62, ss05, ss06, ss07, ss08
```

![Normal preset](./resources/preview-normal.webp)

#### カスタム OpenType 機能

ほとんどのフォントはカスタム OpenType 機能に対応していませんが、Maple Mono ではプログラムで定義できます。

デフォルトでは、[`scripts/feature/`](./scripts/feature) の Python モジュールが OpenType 機能コードを生成し、ビルド時に読み込みます。これらのモジュールを変更して機能やラベルをカスタマイズできます。`.fea` ソースを直接編集する場合は、`build.py` に `--apply-fea-file` を追加してください。ビルドスクリプトは [`source/features/{regular,italic}{_cn,}.fea`](./source/features) を読み込みます。

### 無限矢印リガチャ

Fira Code と Cascadia Code に着想を得て、Maple Mono は v7.3 から無限矢印リガチャに対応しています。描画上の問題により、Hinted フォントでは矢印リガチャがずれる場合があるため、v7.4 以降の Hinted 版ではデフォルトで無効になっています。

`config.json` に `"infinite_arrow": true` を設定するか、コマンドラインに `--infinite-arrow` を追加して強制的に有効化できます。問題は[#508](https://github.com/subframe7536/maple-font/issues/508)でご相談ください。

![Infinite arrow ligatures](./resources/preview-infinite-arrows.webp)

### 標準 Zero 機能

デフォルトでは、`0` はスラッシュ付きで、`zero` を有効にするとドット付きになります。`--standard-zero` を使うと標準の OpenType の意味に戻り、デフォルトの `0` はドット付きで、`zero` を有効にするとスラッシュ付きになります。

### 行の高さのカスタマイズ

Maple Mono のデフォルトの行の高さは `1` です。[`config.json`](./config.json) の `"line_height"` フィールドを変更するか、`--line-height <value>` を指定してください。最終的な行の高さは `(ascender - descender) * line_height` で計算されます。

### Unicode マッピングのカスタマイズ

Maple Mono に Unicode コードポイントがない場合、該当する文字が表示されないことがあります。[`config.json`](./config.json) の `"codepoint_alias"` でマッピングをカスタマイズできます。

```json
{
  "codepoint_alias": {
    "U+E000": "U+E001",
    "U+E002": "U+E003"
  }
}
```

### ウェイトマッピングのカスタマイズ

`config.json` の `"weight_mapping"` で静的フォントの太さを変更できます。

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

### Nerd Font 設定のカスタマイズ

Maple Mono は Nerd Font アイコンを内蔵し、その命名規則に従っています。デフォルトでは、各アイコンの送り幅はラテン文字 1 文字分ですが、グリフの見た目の幅は異なる場合があります。

- アイコンをラテン文字 1 文字分の幅（Nerd Font Mono）にするには、`config.json` の `"nerd_font.mono": true` または `--nf-mono` を使用します。
- 可変幅アイコンを使用するには、`config.json` の `"nerd_font.propo": true` または `--nf-propo` を使用します。

`font-patcher` の引数をカスタマイズするには `fontforge`（場合によっては `python3-fontforge` も）をインストールしてください。[config.json](./config.json) の `"nerd_font.extra_args"` の変更も必要になる場合があります。

![Nerd Font spacing modes](./resources/preview-nerd-fonts.webp)

#### 引数の解析規則

デフォルト引数：`-l --careful --outputdir dir`

- `"nerd_font.propo"` が `true` の場合、`--variable-width-glyphs` を追加します。
- `"nerd_font.mono"` が `true` の場合、`--mono` を追加します。

## CJK 版（日本語）

デフォルトでは日本語フォントは生成されません。`python build.py` に `--cjk jp` を追加すると、ビルドスクリプトが [GitHub Release](https://github.com/subframe7536/maple-font/releases/tag/cjk-base) から日本語のベースグリフをダウンロードします。

### CJK 文字間隔の縮小

ラテン文字の間隔は正常なのに CJK 文字だけ間隔が**広すぎる**場合は、ビルドオプション `cjk.narrow` または `--cjk-narrow` を使用できます。ただし、フォントは厳密な等幅として認識されなくなります。

詳しくは[#249](https://github.com/subframe7536/maple-font/issues/249#issuecomment-2871260476)をご覧ください。

- ラテン文字の幅も変更する場合は[`--width` オプション](#文字幅の縮小)を使用してください。

### GitHub ミラー

ビルドスクリプトは必要なリソースを GitHub から自動的にダウンロードします。失敗する場合は [config.json](./config.json) の `github_mirror` または環境変数 `$GITHUB` を設定してください。URL の形式は `https://<github_mirror>/<user>/<repo>/releases/download/<tag>/<file>` です。対象の `.zip` をダウンロードして `build.py` と同じディレクトリに置くこともできます。

<a id="buildpy-cli"></a>

## `build.py` コマンドラインオプション

```text
使い方: build.py [-h] [-v] [-d] [--debug] [-n] [--standard-zero] [--feat FEAT]
                 [--apply-fea-file] [--hinted | --no-hinted]
                 [--liga | --no-liga] [--infinite-arrow] [--remove-tag-liga]
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
  --feat FEAT           指定した機能を有効化して固定します。`,` で区切って指定します
                        （例: `--feat zero,cv01,ss07,ss08`）。コンテキストルールは
                        `calt` で有効になります
  --apply-fea-file      対応する
                        `source/features/{regular,italic}{_cn,}.fea` を静的・可変フォントに適用します
  --hinted              NF/CJK/NF-CJK の基底フォントにヒンティング済みフォントを使用します（デフォルト）
  --no-hinted           NF/CJK/NF-CJK の基底フォントにヒンティングなしフォントを使用します
  --liga                すべてのリガチャを保持します（デフォルト）
  --no-liga             すべてのリガチャを削除します
  --infinite-arrow      無限矢印リガチャを有効にします（Hinted フォントではデフォルトで無効）
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
