![표지 이미지](./resources/header.png)

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
  <a href="#설치">다운로드</a> |
  <a href="https://font.subf.dev">웹사이트</a> |
  <a href="https://font.subf.dev/en/playground">Playground</a> |
  <a href="#문서">문서</a> |
  <a href="./README.md">English</a> |
  <a href="./README_CN.md">简中</a> |
  <a href="./README_TC.md">繁中</a> |
  <a href="./README_JP.md">日本語</a> |
  한국어
</p>

> [!WARNING]
> 이 브랜치는 V8이며 아직 개발 중으로 정식 출시되지 않았습니다. 안정 버전이 필요하다면 [`v7` 브랜치](https://github.com/subframe7536/maple-font/tree/v7)를 사용하세요.

# Maple Mono

Maple Mono는 코딩을 더 편안하고 효율적으로 할 수 있도록 만든 오픈 소스 고정폭 글꼴입니다. 제 작업 효율을 높이기 위해 만들었으며, 더 많은 사람이 즐겁게 코드를 작성하는 데 도움이 되기를 바랍니다.

## 주요 특징

- ✨ **가변 두께** - 글꼴 두께를 연속적으로 조절할 수 있으며, 기울임 글리프를 세밀하게 다듬었습니다.
- ☁️ **둥근 글리프** - 전체적으로 둥근 디자인을 사용하고 `@ $ % & Q ->` 같은 핵심 기호를 다시 그렸으며, 기울임 연결(`f i j k l x y`)을 개선했습니다.
- 🪄 **스마트 합자** - 다양한 스마트 합자, 문자 변형, OpenType 스타일 세트와 상태 라벨 합자를 제공하여 코드를 더 읽기 쉽고 표현력 있게 만듭니다.
- 🔣 **확장된 Unicode 지원** - 상자 그리기 문자, 점자, 수학 연산자(U+2200–U+22FF), 체스와 카드 기호, 터미널 상태 및 진행률 기호, Claude Code 상태 로딩 기호를 지원합니다.
- 🎨 **Nerd Font 아이콘** - [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts)를 기본으로 통합하여 다양한 개발 도구와 터미널 환경에서 사용할 수 있습니다.
- 🀄 **CJK 2:1 정렬** - 중국어 간체, 중국어 번체, 일본어, 한국어 글리프의 폭이 라틴 문자의 정확히 두 배라서 다국어 텍스트와 Markdown 표가 정렬됩니다.
- 📏 **세 가지 문자 폭** - default, narrow, slim 세 가지 문자 폭을 제공합니다.
- 🔨 **높은 사용자 설정 가능성** - OpenType 기능, 태그 합자, 줄 높이, 문자 폭과 글꼴 두께 매핑을 설정하거나 소스에서 전용 글꼴을 생성할 수 있습니다.

## CJK

다국어 텍스트와 Markdown 표를 정렬하기 위해 CJK 문자와 라틴 문자는 2:1 폭으로 맞춰집니다. 그 대신 기본 CJK 문자 간격은 일반적인 한국어 글꼴보다 넓습니다([이유](https://github.com/subframe7536/maple-font/issues/211)). V7과 비교해 V8은 CJK 문자 세트를 크게 확장하고 개선했습니다.

| 지역 | 지원 범위                                       | CJK 글꼴 소스                                                                          |
| ---- | ----------------------------------------------- | -------------------------------------------------------------------------------------- |
| CN   | 중국어 간체 및 일반적인 중국어 번체·일본어 문자 | [WenYuan Rounded SC](https://github.com/takushun-wu/WenYuanFonts)                      |
| TC   | 중국어 번체                                     | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)               |
| JP   | 일본어                                          | [Resource Han Rounded JP](https://github.com/CyanoHao/Resource-Han-Rounded)            |
| KR   | 한국어                                          | [Chiron Go Round TC](https://github.com/chiron-fonts/chiron-go-round-tc)의 한국어 범위 |

![2-1.png](./resources/2-1.png)

자세한 내용은 [CJK 빌드](./documentation/cjk.md)를 참고하세요.

## 미리보기

![showcase.png](./resources/showcase.webp)

생성 도구: [CodeImg](https://github.com/subframe7536/vscode-codeimg), 테마: [Maple](https://github.com/subframe7536/vscode-theme-maple), 글꼴 크기 16px, 줄 높이 1.8, 기본 글자 간격.

## 합자와 변형

Maple Mono는 스마트 합자(`calt`로 활성화), 문자 변형(`cvXX`), 스타일 세트(`ssXX`)를 제공하며, 대부분의 최신 운영 체제, 브라우저, 터미널, 편집기에서 지원됩니다. 전체 목록은 [OpenType 기능](./documentation/opentype-features.md)을 참고하거나 [Playground](https://font.subf.dev/en/playground)에서 직접 사용해 보세요.

## 스타일 한눈에 보기

- **Normal 프리셋** - `JetBrains Mono`와 비슷한 덜 개성적인 글리프와 사선이 있는 `0`.
- **무한 화살표 합자** - Fira Code와 Cascadia Code에서 영감을 받아 화살표 합자를 원하는 길이로 늘릴 수 있습니다.
- **세 가지 문자 폭** - 라틴 문자 폭을 default(600), narrow(550), slim(500) 중에서 선택할 수 있습니다.
- **Nerd Font 아이콘** - 아이콘 폭을 기본, 고정 폭(`NFMono`), 가변 폭(`NFPropo`) 중에서 선택할 수 있습니다.

| Normal 프리셋                                        | 무한 화살표 합자                                                      |
| ---------------------------------------------------- | --------------------------------------------------------------------- |
| ![Normal preset](./resources/preview-normal.webp)    | ![Infinite arrow ligatures](./resources/preview-infinite-arrows.webp) |
| **문자 폭**                                          | **Nerd Font 아이콘**                                                  |
| ![Width comparison](./resources/preview-widths.webp) | ![Nerd Font spacing modes](./resources/preview-nerd-fonts.webp)       |

각 스타일의 빌드 방법은 [빌드 옵션](./documentation/build-options.md)을 참고하세요.

## 설치

[Releases](https://github.com/subframe7536/maple-font/releases/latest)에서 글꼴 압축 파일을 다운로드하거나, 패키지 관리자로 가장 많이 쓰는 Maple Mono NF를 설치할 수 있습니다:

```sh
# Scoop (Windows)
scoop bucket add nerd-fonts
scoop install Maple-Mono-NF
# Homebrew (macOS, Linux)
brew install --cask font-maple-mono-nf
# Arch Linux (archlinuxcn)
paru -S ttf-maplemono-nf-unhinted
# Nixpkgs: `maple-mono.NF-unhinted`를 `fonts.packages`에 추가
```

패키지 관리자에서는 현재 v7.9를 제공합니다. CDN: [fontsource](https://fontsource.org/fonts/maple-mono), [ZeoSeven Fonts](https://fonts.zeoseven.com/items/443/); Maple Mono CN: [The Chinese Web Fonts Plan](https://chinese-font.netlify.app/zh-cn/fonts/maple-mono-cn/MapleMono-CN-Regular), [ZeoSeven Fonts](https://fonts.zeoseven.com/items/442/). 모든 패키지는 [설치 가이드](./documentation/install.md)를 참고하세요.

## 어떤 파일을 선택해야 하나요?

| 용도             | 추천                                  |
| ---------------- | ------------------------------------- |
| 일반 코딩        | `TTF` 또는 `OTF`                      |
| 터미널 아이콘    | `NF`, `NFMono`, `NFPropo`             |
| 아이콘과 CJK     | `NF-CN`, `NF-TC`, `NF-JP`, `NF-KR`    |
| 웹 페이지        | `WOFF2`                               |

모든 패키지와 hinted / unhinted의 차이는 [글꼴 선택](./documentation/choose.md)을 참고하세요.

## 사용법

VS Code, JetBrains IDE, Zed, Windows Terminal, Kitty, Ghostty 설정 방법은 [사용 가이드](./documentation/usage.md)를 참고하세요.

## 직접 빌드하기

위의 모든 특징은 [`config.json`](./config.json) 또는 `build.py` 옵션으로 빌드 시 조정할 수 있습니다. [Playground](https://font.subf.dev/en/playground)에서 브라우저로, [GitHub Actions](https://github.com/subframe7536/maple-font/actions/workflows/custom.yml)로 클라우드에서, 또는 Docker / Python으로 로컬에서 빌드할 수 있습니다. 자세한 내용은 [사용자 정의 빌드](./documentation/build.md)를 참고하세요.

## 문서

문서는 현재 영어로만 제공됩니다.

- **시작하기**: [설치](./documentation/install.md) · [이름 규칙 및 글꼴 선택](./documentation/choose.md) · [사용법](./documentation/usage.md) · [OpenType 기능](./documentation/opentype-features.md)
- **빌드**: [사용자 정의 빌드](./documentation/build.md) · [빌드 옵션](./documentation/build-options.md) · [CJK 빌드](./documentation/cjk.md) · [`build.py` CLI 참조](#buildpy-cli)
- **개발 참여**: [개발](./documentation/development.md) · [Google Fonts 빌드 및 QA](./documentation/google-fonts.md)

<a id="buildpy-cli"></a>

## `build.py` 명령줄 옵션

```text
사용법: build.py [-h] [-v] [-d] [--debug] [-n] [--standard-zero]
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

Maple Mono 빌더 및 최적화 도구

옵션:
  -h, --help            이 도움말을 표시하고 종료합니다
  -v, --version         프로그램 버전을 표시하고 종료합니다
  -d, --dry             설정을 출력하고 종료합니다
  --debug               빠른 디버그 빌드를 사용합니다. `Debug`를 추가하고,
                        디버그 로깅을 활성화하며 Regular/Italic만 빌드하고,
                        OTF/WOFF2/Nerd Font 출력을 건너뜁니다

기능 옵션:
  -n, --normal          `JetBrains Mono`와 비슷한 Normal 프리셋을 사용하며,
                        `0`은 사선 모양이 됩니다
  --standard-zero       표준 zero 의미를 사용합니다. 기본 `0`은 점 모양이고,
                        `zero`를 활성화하면 사선 모양이 됩니다
  --legacy-thin-weight-class
                        Thin 및 ExtraLight 정적 글꼴에 레거시 weight class 값
                        (100/200 대신 250/275)을 사용하여 Windows의
                        JetBrains IDE에서 GDI 가짜 굵은체 문제를 해결합니다
  --feat FEAT           지정한 기능을 활성화하고 고정합니다. `,`로 구분합니다
                        (예: `--feat zero,cv01,ss07,ss08`). 문맥 규칙은 `calt`를
                        통해 활성화됩니다
  --apply-fea-file      일치하는
                        `sources/features/{regular,italic}{_cn,}.fea`를 정적 및 가변 글꼴에 적용합니다
  --hinted              NF/CJK/NF-CJK의 기본 글꼴로 힌팅된 글꼴을 사용합니다（기본값）
  --no-hinted           NF/CJK/NF-CJK의 기본 글꼴로 힌팅되지 않은 글꼴을 사용합니다
  --liga                모든 합자를 유지합니다（기본값）
  --no-liga             모든 합자를 제거합니다
  --infinite-arrow      무한 화살표 합자 지원을 추가합니다（기본값）
  --no-infinite-arrow   무한 화살표 합자 지원을 추가하지 않습니다
  --remove-tag-liga     `[TODO]`와 같은 일반 텍스트 태그 합자를 제거합니다
  --line-height LINE_HEIGHT
                        줄 높이 배율（예: 1.1）
  --width {default,narrow,slim}
                        글리프 폭을 설정합니다: default（600）, narrow（550）, slim（500）

빌드 옵션:
  --format FORMATS      필요한 기본 출력 형식을 쉼표로 구분해 선택합니다: ttf, otf, woff2.
                        가변 글꼴 기본 버전은 항상 빌드됩니다
  --least-styles        Regular / Bold / Italic / BoldItalic 스타일만 빌드합니다
  --cache               `fonts/` 아래의 유효한 캐시 파이프라인 단계를 재사용하고,
                        관련 없는 기존 출력을 보존합니다
  --archive             설정과 라이선스를 포함하여 기존의 각 비 JSON 출력 디렉터리를 보관합니다

Nerd Font 옵션:
  --nf, --nerd-font     Nerd Font 버전을 빌드합니다（기본값）
  --no-nf, --no-nerd-font
                        Nerd Font 버전을 빌드하지 않습니다
  --nf-mono             Nerd Font 아이콘 폭을 고정합니다
  --nf-propo            Nerd Font 아이콘 폭을 가변으로 만들고 `--nf-mono`를 덮어씁니다
  --nf-variable         Nerd Font를 가변 글꼴로 빌드합니다
  --font-patcher        Nerd Font Patcher를 사용해 NF 형식을 빌드하도록 강제합니다

CJK 옵션:
  --cjk CJK             cn, jp, tc, kr 로케일용 Maple Mono + CJK 확장 글꼴을 빌드합니다.
                        반복해서 지정하거나 쉼표로 구분할 수 있습니다
  --cjk-variable        CJK 확장 출력을 병합된 가변 글꼴로 유지합니다
  --cjk-narrow          선택한 로케일에 좁은 CJK 간격을 적용합니다
  --cjk-scale-factor CJK_SCALE_FACTOR
                        선택한 CJK 로케일의 배율을 설정합니다. 형식:
                        <factor> 또는 <width_factor>,<height_factor>
  --cjk-both            Nerd Font가 활성화되면 NF CJK와 비 NF CJK 출력을 모두 빌드합니다
  --cjk-hinted          최종 정적 CJK 글꼴에 자동 힌팅을 적용합니다
  --no-cjk-hinted       최종 정적 CJK 글꼴에 자동 힌팅을 적용하지 않습니다（기본값）

더 이상 사용하지 않는 CN 옵션:
  --cn                  더 이상 사용하지 않습니다. `--cjk cn`의 별칭입니다
  --no-cn               더 이상 사용하지 않습니다. 선택한 CJK 로케일에서 `cn`을 제거하는 별칭입니다
  --cn-narrow           더 이상 사용하지 않습니다. `cn` 대상 `--cjk-narrow`의 별칭입니다
  --cn-scale-factor CN_SCALE_FACTOR
                        더 이상 사용하지 않습니다. `cn` 대상 `--cjk-scale-factor`의 별칭입니다
  --cn-both             더 이상 사용하지 않습니다. `--cjk-both`의 별칭입니다
```

## 감사의 글

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

## 후원

이 글꼴이 도움이 되었다면 [아이파뎬](https://afdian.com/a/subframe7536)을 통해 후원해 주세요.

## Star History

<a href="https://star-history.dera.page/#subframe7536/maple-font&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://star-history.dera.page/svg?repos=subframe7536/maple-font&type=date&legend=top-left" />
 </picture>
</a>

## 라이선스

SIL Open Font License 1.1
