![커버](./resources/header.png)

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
  <a href="#다운로드">다운로드</a> |
  <a href="https://font.subf.dev">웹사이트</a> |
  <a href="./README.md">English</a> |
  <a href="./README_CN.md">中文</a> |
  <a href="./README_JA.md">日本語</a> |
  한국어
</p>

# Maple Mono

Maple Mono는 코딩 흐름을 부드럽게 만드는 데 초점을 둔 오픈소스 모노스페이스 폰트입니다.

원본 프로젝트는 개발 작업 경험을 개선하기 위해 만들어졌고, V7에서는 가변 폰트 형식, 폰트 프로젝트 소스, 절반 이상의 글리프 재설계, 더 똑똑한 ligature를 제공합니다. V6는 [여기](https://github.com/subframe7536/maple-font/tree/main)에서 확인할 수 있습니다.


## 특징

- ✨ 가변 - 세밀하게 조정된 italic 글리프와 자유로운 weight 조절을 제공하는 원본 Maple Mono 가변 폰트.
- ☁️ 부드러움 - 둥근 모서리, 새로 설계된 `@ $ % & Q ->` 글리프, italic 스타일의 필기체 `f i j k l x y`.
- 💪 실용성 - 풍부한 smart ligature. 자세한 내용은 [`features/`](./source/features/README.md)를 참고하세요.
- 🎨 아이콘 - 터미널을 더 풍부하게 만드는 [Nerd Font](https://github.com/ryanoasis/nerd-fonts) 지원.
- 🔨 커스터마이즈 - OpenType 기능을 켜거나 끄고, 필요한 형태로 직접 빌드할 수 있습니다.

### 중국어, 일본어, 한국어

CN 버전은 [Resource Han Rounded](https://github.com/CyanoHao/Resource-Han-Rounded)를 기반으로 중국어 개발 환경을 위한 문자 집합을 제공하며, 간체 중국어, 번체 중국어, 일본어를 포함합니다. 중국어와 영문을 2:1로 맞춰 다국어 표시나 Markdown 표에서 정렬된 모습을 만들 수 있지만, 다른 인기 중국어 폰트보다 중국어 자간이 더 넓을 수 있습니다. 자세한 내용은 [release notes](https://github.com/subframe7536/maple-font/releases/tag/cn-base)와 [이 issue](https://github.com/subframe7536/maple-font/issues/211)를 참고하세요.

- CN 버전은 가변 폰트 형식을 지원하지 않습니다.

KO 버전은 [Noto Sans Mono CJK KR](https://github.com/notofonts/noto-cjk)의 한국어 소스만 사용해 `Maple Mono KO`와 `Maple Mono NF KO`를 생성합니다. Latin, 프로그래밍 기호, Maple Mono ligature, contextual alternate, feature freezing 동작, Nerd Font 심볼은 기존 Maple Mono / Maple Mono NF 결과물을 최대한 유지합니다.

한국어 글리프는 기본 모노스페이스 출력에서 Latin 폭의 정확히 2배가 되도록 맞췄습니다. 따라서 한글 주석, Markdown 표, ASCII diagram, 터미널 파일 목록처럼 영문과 한글이 섞이는 환경에서 fallback 폰트에 의존할 때보다 정렬이 안정적입니다.

또한 KO 빌드는 Noto CJK KR의 Hangul shaping 일부를 보존합니다. 최종 KO / NF-KO 폰트에는 `hang` script와 `ccmp`, `ljmo`, `vjmo`, `tjmo` 기능이 유지되어 macOS/CoreText나 HarfBuzz 경로에서 분해된 Hangul Jamo가 한 음절 cluster로 렌더링될 수 있습니다.

- KO 버전은 가변 폰트 형식을 지원하지 않습니다.
- KO 글리프 소스는 `NotoSansMonoCJKkr-*` 파일로 제한됩니다. JP, SC, TC, HK Noto CJK 폰트는 사용하지 않습니다.

![2-1.png](./resources/2-1.png)

## 스크린샷

![showcase.png](./resources/showcase.png)

- 생성: [CodeImg](https://github.com/subframe7536/vscode-codeimg)
- 테마: [Maple](https://github.com/subframe7536/vscode-theme-maple)
- 설정: 폰트 크기 16px, 줄 높이 1.8, 기본 letter spacing

## 다운로드

원본 Maple Mono 폰트 아카이브는 [upstream Releases](https://github.com/subframe7536/maple-font/releases)에서 받을 수 있습니다.

이 fork의 KO / NF-KO 아카이브는 [maple-font-ko Releases](https://github.com/kuskhan/maple-font-ko/releases)에서 받거나, 아래의 로컬 빌드 방법으로 생성하세요.

### Scoop (Windows)

```sh
# bucket 추가
scoop bucket add nerd-fonts
# Maple Mono (ttf 형식)
scoop install Maple-Mono
# Maple Mono NF
scoop install Maple-Mono-NF
# Maple Mono NF CN
scoop install Maple-Mono-NF-CN
```

현재 공개 package manager 항목은 upstream Maple Mono / CN 패키지 기준입니다. KO / NF-KO가 package manager에 등록되지 않은 환경에서는 release archive를 받거나 직접 빌드하세요.

### Homebrew (MacOS, Linux)

```sh
# Maple Mono
brew install --cask font-maple-mono
# Maple Mono NF
brew install --cask font-maple-mono-nf
# Maple Mono NF CN
brew install --cask font-maple-mono-nf-cn
```

### Arch Linux

ArchLinuxCN 저장소는 pkgbase 안의 모든 패키지 zip을 내려받지 않고 단일 패키지 zip을 받을 수 있지만, AUR은 그렇지 않습니다.

#### ArchLinuxCN (권장)

```sh
# Maple Mono (Ligature TTF unhinted)
paru -S ttf-maplemono
# Maple Mono NF (Ligature unhinted)
paru -S ttf-maplemono-nf-unhinted
# Maple Mono NF CN (Ligature unhinted)
paru -S ttf-maplemono-nf-cn-unhinted
```

#### AUR (권장하지 않음)

```sh
# Maple Mono (Ligature TTF unhinted)
paru -S maplemono-ttf
# Maple Mono NF (Ligature unhinted)
paru -S maplemono-nf-unhinted
# Maple Mono NF CN (Ligature unhinted)
paru -S maplemono-nf-cn-unhinted
```

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

## CDN

### Maple Mono

- [fontsource](https://fontsource.org/fonts/maple-mono)
- [ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/)

### Maple Mono CN

- [The Chinese Web Fonts Plan (中文网字计划)](https://chinese-font.netlify.app/zh-cn/fonts/maple-mono-cn/MapleMono-CN-Regular)
- [ZeoSeven Fonts](https://fonts.zeoseven.com/items/442/)

KO / NF-KO 웹폰트 CDN은 현재 별도로 제공하지 않습니다. 필요한 경우 로컬 빌드 후 생성된 TTF를 기준으로 프로젝트에 맞게 변환하세요.

## 사용법 & 기능 설정

자세한 OpenType 기능 설명은 [문서](./source/features/README.md)를 참고하거나 [Playground](https://font.subf.dev/en/playground)에서 확인할 수 있습니다.

## 이름 FAQ

### 기능

- **Ligature**: ligature가 포함된 기본 버전 (`Maple Mono`)
- **No-Ligature**: ligature가 제거된 기본 버전 (`Maple Mono NL`)
- **Normal-Ligature**: [`--normal` preset](#preset)에 ligature가 포함된 버전 (`Maple Mono Normal`)
- **Normal-No-Ligature**: [`--normal` preset](#preset)에 ligature가 제거된 버전 (`Maple Mono Normal NL`)

### 형식과 글리프 세트

- **Variable**: 가변 weight를 지원하는 최소 버전
- **TTF**: ttf 형식의 최소 버전 [권장]
- **OTF**: otf 형식의 최소 버전
- **WOFF2**: 웹페이지에서 작은 용량으로 쓰기 위한 woff2 형식
- **NF**: 터미널 아이콘을 추가한 Nerd Font 패치 버전 (`-NF` suffix)
- **CN**: 중국어/일본어 글리프를 포함한 버전 (`-CN` suffix)
- **NF-CN**: 아이콘과 중국어/일본어 글리프를 포함한 버전 (`-NF-CN` suffix)
- **KO**: Noto Sans Mono CJK KR 기반 한국어 글리프를 포함한 버전 (`-KO` suffix)
- **NF-KO**: 아이콘과 한국어 글리프를 포함한 버전 (`-NF-KO` suffix)

### Font Hint

- **Hinted font**는 낮은 해상도 화면에서 더 나은 렌더링을 얻기 위한 폰트입니다. 1080p 이하 화면에서는 hinted font가 더 안정적으로 보일 수 있습니다.
  - 예: `MapleMono-TTF-AutoHint` / `MapleMono-NF` / `MapleMono-NF-CN`
- **Unhinted font**는 MacBook 같은 고해상도 화면에 적합합니다. 고해상도 환경에서 hinted font는 흐리거나 어색하게 보일 수 있습니다.
  - 예: `MapleMono-OTF` / `MapleMono-TTF` / `MapleMono-NF-unhinted` / `MapleMono-NF-CN-unhinted`

## 커스텀 빌드

[`config.json`](./config.json)은 빌드 과정을 설정하는 파일입니다. 자세한 내용은 [schema](./source/schema.json) 또는 [features 문서](./source/features/README.md)를 참고하세요.

명령줄 옵션도 사용할 수 있으며, CLI 옵션은 `config.json`보다 우선합니다.

### 빌드 방법

#### 1. 브라우저에서 빌드

[Playground](https://font.subf.dev/en/playground)로 이동한 뒤 왼쪽 아래의 "Custom Build" 버튼을 누릅니다.

- 현재는 OpenType feature freezing만 지원합니다.

#### 2. GitHub Actions 사용

이 fork의 [GitHub Actions](https://github.com/kuskhan/maple-font-ko/actions/workflows/custom.yml)에서 커스텀 빌드를 실행할 수 있습니다.

1. 저장소를 fork합니다.
2. 필요하면 `config.json`을 수정합니다.
3. Actions 탭으로 이동합니다.
4. 왼쪽에서 `Custom Build` workflow를 선택합니다.
5. `Run workflow` 버튼을 누르고 옵션을 설정합니다.
6. 빌드가 끝날 때까지 기다립니다.
7. 생성된 font archive를 다운로드합니다.

#### 3. Docker 사용

```shell
git clone https://github.com/kuskhan/maple-font-ko --depth 1
docker build -t maple-font .
docker run -v "$(pwd)/fonts:/app/fonts" -e BUILD_ARGS="--ko-both --normal" maple-font
```

#### 4. 로컬 빌드

저장소를 clone한 뒤 로컬에서 실행합니다. Python 3와 의존성이 필요합니다.

```shell
git clone https://github.com/kuskhan/maple-font-ko --depth 1
cd maple-font-ko
pip install -r requirements.txt
python build.py --ko-both
```

> [!TIP]
> `Ubuntu`나 `Debian`에서는 `python-is-python3`가 필요할 수 있습니다.
>
> 의존성 설치가 어렵다면 GitHub Codespace에서 실행하는 방법도 있습니다.

### 좁은 글리프 폭

`config.json`에서 `"width": "narrow"`를 설정하거나 CLI에서 `--width slim`을 추가해 Latin 글리프 폭을 바꿀 수 있습니다.

옵션은 3가지입니다.

- default: 600
- narrow: 550
- slim: 500

KO 기본 출력에서는 Korean glyph advance가 Latin 폭의 2배가 되도록 처리됩니다. KO 글리프 자체를 좁히는 옵션은 `ko.narrow` 설정이며, 이 경우 폰트가 monospaced font로 인식되지 않을 수 있습니다.

### Custom Nerd-Font

고정 폭 아이콘이 필요하면 `config.json`에서 `"nerd_font.mono": true`를 설정하거나 `--nf-mono`를 추가합니다.

가변 폭 아이콘이 필요하면 `config.json`에서 `"nerd_font.propo": true`를 설정하거나 `--nf-propo`를 추가합니다.

custom `font-patcher` 인자를 쓰려면 `font-forge` 또는 `python3-fontforge`가 필요할 수 있습니다.

### Preset

`build.py`에 `--normal` flag를 주면 Maple Mono의 개성 있는 일부 feature를 줄이고 `JetBrains Mono`에 가까운 느낌으로 빌드합니다.

가변 폰트를 사용하는 경우에는 모든 feature가 동작하도록 `calt`를 활성화하세요.

활성화되는 feature:

```text
cv01, cv02, cv33, cv34, cv35, cv36, cv61, cv62, ss05, ss06, ss07, ss08
```

[온라인 미리보기](https://font.subf.dev/en/playground?normal)

### OpenType Feature Freeze

feature freeze 옵션은 세 종류입니다.

1. `enable`: `cvXX` / `ssXX` / `zero`를 별도로 설정하지 않아도 feature를 기본 글리프/ligature처럼 강제로 활성화합니다.
2. `disable`: 해당 feature가 수동으로 활성화되어도 효과가 없도록 제거합니다.
3. `ignore`: 아무 작업도 하지 않습니다.

#### Custom OpenType Feature

OpenType feature는 폰트 내부 variant와 ligature를 제어합니다. 필요 없는 ligature나 feature를 제거하거나, trigger rule을 바꾸거나, 새 rule을 추가할 수 있습니다.

기본적으로 [`source/py/feature/`](./source/py/feature)의 Python module이 feature rule string을 생성하고 빌드 시 로드합니다. feature file을 직접 적용하려면 `build.py`에 `--apply-fea-file` flag를 주면 [`source/features/{regular,italic}{_cn,}.fea`](./source/features)를 로드합니다.

### Infinite Arrow Ligatures

V7.3부터 Fira Code에서 영감을 받은 infinite arrow ligature가 기본으로 활성화되었습니다. Hinted font에서는 일부 ligature가 어긋나는 문제가 있어 V7.4부터 hinted 버전에서는 기본 제거됩니다.

강제로 활성화하려면 `config.json`에서 `"infinite_arrow": true`를 설정하거나 CLI에 `--infinite-arrow`를 추가하세요. 자세한 내용은 [#508](https://github.com/subframe7536/maple-font/issues/508)을 참고하세요.

### Custom Font Weight Mapping

`config.json`의 `"weight_mapping"` 항목으로 static font weight를 조정할 수 있습니다.

예를 들어 Regular를 조금 가볍게 만들려면 `"weight_mapping.regular"` 값을 낮춥니다.

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

### 중국어 버전

CN 버전은 기본적으로 꺼져 있습니다. `python build.py --cn`을 실행하면 CN base font가 GitHub에서 다운로드됩니다.

가변 폰트에서 CN base font를 빌드하려면 [config.json](./config.json)에 `"cn.use_static_base_font": false`를 설정하세요. 이 과정은 10-30분 정도 걸릴 수 있습니다.

#### CN 글리프 간격 좁히기

CN / JP 글리프 간격이 너무 넓게 느껴진다면 `cn.narrow` 설정이나 `--cn-narrow` CLI flag를 사용할 수 있습니다. 이 옵션을 쓰면 폰트가 monospaced font로 인식되지 않을 수 있습니다.

Latin 폭도 함께 바꾸고 싶다면 [`--width` 옵션](#좁은-글리프-폭)을 사용하세요.

#### GitHub Mirror

빌드 스크립트는 필요한 asset을 GitHub에서 자동으로 다운로드합니다. 다운로드에 문제가 있으면 [config.json](./config.json)의 `github_mirror` 또는 환경 변수 `$GITHUB`를 설정하세요. 대상 URL은 `https://<github_mirror>/<user>/<repo>/releases/download/<tag>/<file>` 형식입니다.

#### 번체 중국어 문장부호 지원

`cv99`를 활성화하면 중국어 문장부호가 가운데 정렬됩니다. 자세한 내용은 [#150](https://github.com/subframe7536/maple-font/issues/150)을 참고하세요.

### 한국어 버전

KO 버전은 기본적으로 꺼져 있습니다. `python build.py --ko`로 `Maple Mono KO`를 빌드하거나, `--ko-both`로 `Maple Mono KO`와 `Maple Mono NF KO`를 함께 빌드합니다.

KO source와 static base는 다음 명령으로 준비합니다.

```sh
uv run task.py ko --pull
uv run task.py ko --rebuild
uv run build.py --ko-both
```

KO pipeline의 핵심 규칙은 다음과 같습니다.

- 최종 KO / NF-KO 폰트는 이 저장소의 Maple Mono / Maple Mono NF 결과물을 기반으로 합니다.
- 한국어 글리프 소스는 Noto CJK 프로젝트의 Noto Sans Mono CJK KR만 사용합니다.
- JP, SC, TC, HK Noto CJK 폰트는 한국어 fallback으로 사용하지 않습니다.
- 한국어 범위 밖의 Maple Mono Latin, 프로그래밍 기호, ligature, Nerd Font glyph는 유지합니다.
- 기본 monospaced KO 출력은 Korean:Latin advance width를 2:1로 유지합니다.
- italic 한국어 글리프는 Korean source outline을 slant해서 만듭니다.
- 최종 KO / NF-KO `GSUB`에는 Maple feature의 `DFLT`, `latn`과 Noto CJK KR 기반 `hang` shaping이 함께 남아야 합니다.

자세한 구현 및 검증 절차는 [`dev-doc/guide/2604261127_KOREAN_FONT_GENERATION_GUIDE.md`](./dev-doc/guide/2604261127_KOREAN_FONT_GENERATION_GUIDE.md)와 [`dev-doc/guide/2604270825_KOREAN_CODING_FONT_RENDERING_FIX_GUIDE.md`](./dev-doc/guide/2604270825_KOREAN_CODING_FONT_RENDERING_FIX_GUIDE.md)를 참고하세요.

### Build Script Usage

```text
usage: build.py [-h] [-v] [-d] [--debug] [-n] [--feat FEAT] [--apply-fea-file]
                [--hinted | --no-hinted] [--liga | --no-liga]
                [--keep-infinite-arrow] [--infinite-arrow] [--remove-tag-liga]
                [--line-height LINE_HEIGHT] [--width {default,narrow,slim}]
                [--nf-mono] [--nf-propo] [--cn-narrow]
                [--cn-scale-factor CN_SCALE_FACTOR] [--nf | --no-nf]
                [--cn | --no-cn] [--cn-both] [--ko | --no-ko] [--ko-both]
                [--ttf-only] [--least-styles] [--font-patcher] [--cache]
                [--cn-rebuild] [--archive]
```

주요 KO 관련 옵션:

```text
--ko                  Korean version 빌드
--no-ko               Korean version 빌드 안 함 (default)
--ko-both             `Maple Mono KO`와 `Maple Mono NF KO`를 함께 빌드
```

## 개발

### 디자인

[FontLab](https://www.fontlab.com/) 또는 [Glyphs](https://glyphs.app)를 사용해 가변 TTF를 `source/` 폴더에 생성합니다.

### 빌드

```sh
# 프로젝트 초기화
uv sync
# KO static base 준비
uv run task.py ko --rebuild
# 개발 빌드
uv run build.py --ko-both --least-styles --no-hinted --liga
# Nerd Font 업데이트
uv run task.py nerd-font
# fea file 업데이트
uv run task.py fea
# landing page 정보 업데이트
uv run task.py page --sync
# 두 폰트 병합
uv run task.py merge
# 릴리스
uv run task.py release minor
```

## Credit

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
- [Noto CJK](https://github.com/notofonts/noto-cjk)

## Sponsor

원본 Maple Mono가 도움이 되었다면 원작자를 후원할 수 있습니다.

<a href="https://www.buymeacoffee.com/subframe753"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" /></a>

또는 [Afdian](https://afdian.com/a/subframe7536)을 통해 후원할 수 있습니다.

## Star History

<a href="https://www.star-history.com/#subframe7536/maple-font&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=subframe7536/maple-font&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
 </picture>
</a>

## License

SIL Open Font License 1.1
