# changelog

## v6.4

### feature

- upgrade Nerd Font version to 3.0.2 #111
- enable to custom build for font features and Nerd Font! setup config and see details in [README](README.md#build) and [source/build.py](source/build.py) #89 #112
  - currently, build script is only available on Windows. **PR welcome!**
  - 现在可以生成不包含 Nerd Font 的中文字体了，详见 chinese 分支 generate-sc.bat 中
- add ttfautohint version (friendly for low resolution devices) #16

### fix

- italic `<->`
- fix meta table for SC-NF #116

## v6.3

### feature

- liga: add `~~` in `calt`
- liga: add `__` in `ss03`
- liga: add `>=` `<=` in `ss04`
- liga: add `{{` `}}` in `ss05`

### fix & optimze

- fix: make second character center in `::<`/`>::` etc
- fix: italic $D0 `Đ`
- opt: italic $79 `y`
- opt: italic kerning

## v6.2

### change

- **break**: normalize the division of StyleSet(ss01,ss02...) and CharactorVariant(cv01,cv02...)
  - move `==`,`===`,`!=`,`!==` from cv02 to ss01
  - remove cv03 exclaim_equal_equal_equal(`!===`)
  - move `[vite]` from cv04 to ss02
  - move `[info]`,`[trace]`,`[debug]`,`[warn]`,`[error]`,`[fatal]` from calt to ss02
  - add `a`(cv02) `i`(cv03) variants #83
  - add `->`, `=>` and other arrays in pure version(cv01) #83
  - add `@`(cv04) variant

### feature

- init changelog #71
- add `/=` `|=` #72
- add `<==` for mybatisplus sql log
- fill all characters in Latin 1 Supplement(`U+00A0-00FF`) except `U+00B2`, `U+00B3`, `U+00B9,` `U+00BC-00BE` #76
