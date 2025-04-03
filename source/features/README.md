[👉 中文版](./README_CN.md)

# Ligatures And Features

Here is the check list and explaination of Maple Mono ligatures and features.

For more details, please check out `.fea` files in same directory and [OpenType Feature Spec](https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html).

## Usage

### VSCode

Setup in your VSCode settings json file

```jsonc
{
  // Setup font family
  "editor.fontFamily": "Maple Mono NF, Jetbrains Mono, Menlo, Consolas, monospace",
  // Enable ligatures
  "editor.fontLigatures": "'calt'",
  // Or enable OpenType features
  "editor.fontLigatures": "'calt', 'cv01', 'ss01', 'zero'",
}
```

### IDEA / Pycharm / WebStorm / GoLand / CLion

1. Open Settings
2. Click "Editor"
3. Click "Font"
4. Choose "Maple Mono NF" in the font menu
5. Click "Enable Ligatures"

OpenType Features are not supported, you need to custom build to freeze features.

## Ligatures

"Enable ligature", is same as "enable `calt` feature":

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
!!
!=
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
>=>
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
\\ \/ \"
```

### Notice

- `>>` / `>>>` is smart, but much contextual-sensitive, so it may be not effect in some IDEs ([explaination](https://github.com/subframe7536/maple-font/discussions/275)). Turn on `ss07` to force enable.

## Features

### Character Varients (cvXX)

- zero: `0` with dot style
- cv01: `@ $ & % Q => ->` without gap
- cv02: `a` with top arm, no effect on italic `a`
- cv03: `i` without left bottom bar
- cv04: `l` with left bottom bar, like consolas, will be overrided by `cv35` in italic style

#### Italic Only
- cv31: italic `a` with top arm
- cv32: italic `f` without bottom tail, just like regular style
- cv33: italic `i j` with left bottom bar and horizen top bar, just like regular style
- cv34: italic `k` without center circle, just like regular style
- cv35: italic `l` without center tail, just like regular style
- cv36: italic `x` without top and bottom tails, just like regular style
- cv37: italic `y` with straight intersection, just like regular style

#### CN Only

- cv96: Full width `“`(double quote left), `”`(double quote right), `‘`(single quote left), `’`(single quote right)
- cv97: Full width `…`(ellipsis)
- cv98: Full width `—`(emdash)
- cv99: Traditional punctuations (centered)

### Stylistic Sets (ssXX)

- ss01: Broken equals ligatures (`==`, `===`, `!=`, `!==`, `=/=`)
- ss02: Broken compare and equal ligatures (`<=`, `>=`)
- ss03: Enable arbitrary tag (allow to use any case in all tags)
- ss04: Break multiple underscores (`__`, `#__`)
- ss05: Revert thin backslash in escape punctuations (`\\`, `\"`, `\.` ...)
- ss06: Break connected strokes between italic letters (`al`, `ul`, `il` ...)
- ss07: Relax the conditions for multiple greaters ligatures (`>>` or `>>>`)
- ss08: Enable double headed arrows and reverse arrows (`>>=`, `-<<`, `->>`, `>-` ...)
