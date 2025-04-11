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

<!-- CALT -->
```
::
:::
?:
:?
:?>
:=
=:
:=:
=:=
<:
:>
:<
<:<
>:>
::=
__
#{
#[
#(
#?
#!
#:
#=
#_
#__
#_(
]#
#######
<<
<<<
>>
>>>
{{
}}
{|
|}
{{--
--}}
[|
|]
!!
||
??
???
&&
&&&
//
///
/*
/**
*/
++
+++
--
---
;;
;;;
..
...
.?
?.
..<
.=
<~
~>
~~
<~>
<~~
~~>
-~
~-
~@
0xA12 0x56 1920x1080
<=>
<==>
>=
<=
<==
==>
=>
<=<
>=>
<=|
|=>
==
===
!=
!==
=/=
=!=
=<=
=>=
|=
||=
\\ \" \.
<!--
<#--
<!---->
<->
->
<-
-->
<--
<-<
>->
<-|
|->
<|||
|||>
<||
||>
<|
|>
<|>
-|
|-
_|_
||-
<>
</
/>
</>
<+
+>
<+>
<*
*>
<*>
[TRACE]
[DEBUG]
[INFO]
[WARN]
[ERROR]
[FATAL]
[TODO]
[FIXME]
todo))
fixme))
```
<!-- CALT -->

### Notice

- `>>` / `>>>` is smart, but much contextual-sensitive, so it may be not effect in some IDEs ([explaination](https://github.com/subframe7536/maple-font/discussions/275)). Turn on `ss07` to force enable.

## Features

### Character Varients (cvXX)

<!-- CV -->
- cv01: Normalize special symbols (`@ $ & % Q => ->`)
- cv02: Alternative `a` with top arm, no effect on italic `a`
- cv03: Alternative `i` without left bottom bar
- cv04: Alternative `l` with left bottom bar, like consolas, will be overrided by `cv35` in italic style
- zero: Dot style `0`
<!-- CV -->

#### Italic Only

<!-- CV-IT -->
- cv31: Alternative italic `a` with top arm
- cv32: Alternative Italic `f` without bottom tail
- cv33: Alternative Italic `i` and `j` with left bottom bar and horizen top bar
- cv34: Alternative Italic `k` without center circle
- cv35: Alternative Italic `l` without center tail
- cv36: Alternative Italic `x` without top and bottom tails
- cv37: Alternative Italic `y` with straight intersection
<!-- CV-IT -->

#### CN Only

<!-- CV-CN -->
- cv96: Full width quotes (`“` / `”` / `‘` / `’`)
- cv97: Full width ellipsis (`…`)
- cv98: Full width emdash (`—`)
- cv99: Traditional centered punctuations
<!-- CV-CN -->

### Stylistic Sets (ssXX)

<!-- SS -->
- ss01: Broken multiple equals ligatures (`==`, `===`, `!=`, `!==`, `=/=`)
- ss02: Broken compare and equal ligatures (`<=`, `>=`)
- ss03: Allow to use any case in all tags
- ss04: Broken multiple underscores ligatures (`__`, `#__`)
- ss05: Revert thin backslash in escape symbols (`\`, `\"`, `\.` ...)
- ss07: Break connected strokes between italic letters (`>>` or `>>>`)
- ss08: Double headed arrows and reverse arrows ligatures (`>>=`, `-<<`, `->>`, `>-` ...)
- ss06: Break connected strokes between italic letters (`al`, `il`, `ull` ...)
<!-- SS -->