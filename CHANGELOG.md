# changelog

## v6.2

### change

- **break**: normalize the division of StyleSet(ss01,ss02...) and CharactorVariant(cv01,cv02...)
  - move `==`,`===`,`!=`,`!==` from cv02 to ss01
  - remove cv03 exclaim_equal_equal_equal(`!===`)
  - move `[vite]` from cv04 to ss02
  - move `[info]`,`[trace]`,`[debug]`,`[warn]`,`[error]`,`[fatal]` from calt to ss02

### feature

- init changelog #71
- add `/=` `|=` #72
- add `<==` for mybatisplus sql log
- add `a`(cv02) `i`(cv03) variants #83
- add `->`, `=>` and other arrays in pure version(cv01) #83
- add `@`(cv04) variant
- fill all characters in Latin 1 Supplement(`U+00A0-00FF`) except `U+00B2`, `U+00B3`, `U+00B9,` `U+00BC-00BE` #76