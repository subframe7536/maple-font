# Ligatures And Features

Here is the basic list and explaination of Maple Mono ligatures and features.

For more details, please check out `.fea` files and [OpenType Feature Spec](https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html).

### calt

```
{{
}}
{{--
--}}
{|
|}
[|
|]
//
///
/*
/**
++
+++
.?
..
...
..<
<!--
<-
<#--
<>
<:
<:<
>:>
<=>
<->
<|||
<||
<|
<|>
||>
|>
-|
-->
->
>=
<=
<==
!=
!!
!==
=!=
=>
==
=:=
:=:
:=
:>
:<
::
;;
;;;
:?
:?>
::=
||-
||=
|-
|=
||
--
---
<--
??
???
?:
?.
&&
__
=/=
<-<
<=<
<==>
==>
=>>
>=>
>>=
>>-
-<
-<<
<-|
<=|
|=>
<~
~~
<~>
<~~
-~
~~>
~>
~-
~@
<+>
<+
+>
<*>
<*
*>
</>
</
/>
<<
<<<
>>
>>>
#{
#[
#(
#?
#_
#__
#:
#=
#_(
]#
0x12
[TRACE]
[DEBUG]
[INFO]
[WARN]
[ERROR]
[FATAL]
[TODO]
todo))
[FIXME]
fixme))
########
<!---->
\\
```

#### Notice

- `>>` / `>>>` is much contextual-sensitive

### Character Varients (cvXX)

- zero: `0` with dot style
- cv01: `@ $ & % Q => ->` without gap
- cv02: `a` with top arm, no effect on italic `a`
- cv03: `i` without left bottom bar
- cv04: `l` with left bottom bar, like consolas, will be overrided by cv35 in italic style

#### Italic Only
- cv31: italic `a` with top arm
- cv32: italic `f` without bottom tail, just like regular style
- cv33: italic `i j` with left bottom bar and horizen top bar, just like regular style
- cv34: italic `k` without circle, just like regular style
- cv35: italic `l` without tail, just like regular style
- cv36: italic `x` without tails, just like regular style

#### CN Only

- cv96: Full width `“`(double quote left), `”`(double quote right), `‘`(single quote left), `’`(single quote right)
- cv97: Full width `…`(ellipsis)
- cv98: Full width `—`(emdash)
- cv99: Traditional punctuations

### Style Sets (ssXX)

- ss01: Broken equals ligatures (`==`, `===`, `!=`, `!==`, `=/=`)
- ss02: Broken compare and equal ligatures (`<=`, `>=`)
- ss03: Enable arbitrary tag (allow to use any case in all tags)
- ss04: Break multiple underscores (`__`, `#__`)
- ss05: Thin backslash in escape letters (`\w`, `\n`, `\r` ...)
- ss06: Break connected strokes between italic letters (`al`, `ul`, `il` ...)
- ss07: Relax the conditions for multiple greaters ligatures (`>>` or `>>>`)
- ss08: Enable double headed arrows and reverse arrows (`>>=`, `-<<`, `->>`, `>-` ...)
