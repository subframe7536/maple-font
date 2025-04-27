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
{{!--
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
\\ \' \.
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
[NOTE]
[HACK]
[MARK]
[EROR]
[WARNING]
todo))
fixme))
Cl
al
cl
el
il
tl
ul
xl
ff
tt
all
ell
ill
ull
ll
```
<!-- CALT -->

### Notice

- `>>` / `>>>` is smart, but much contextual-sensitive, so it may be not effect in some IDEs ([explaination](https://github.com/subframe7536/maple-font/discussions/275)). Turn on `ss07` to force enable.

## Features

### Character Varients (cvXX)

<!-- CV -->
- [v7.0] cv01: Normalize special symbols (`@ $ & % Q => ->`)
- [v7.0] cv02: Alternative `a` with top arm, no effect in italic style
- [v7.0] cv03: Alternative `i` without left bottom bar
- [v7.0] cv04: Alternative `l` with left bottom bar, like consolas, will be overrided by `cv35` in italic style
- [v7.1] cv05: Alternative `g` in double story style, no effect in italic style
- [v7.1] cv06: Alternative `i` without bottom bar, no effect in italic style
- [v7.1] cv07: Alternative `J` without top bar, no effect in italic style
- [v7.1] cv08: Alternative `r` with bottom bar, no effect in italic style
- [v7.1] cv61: Alternative `,` and `;` with straight tail
- [v7.1] cv62: Alternative `?` with larger openings
- [v7.1] cv63: Alternative `<=` in arrow style
- [v7.0] zero: Dot style `0`
<!-- CV -->

#### Italic Only

<!-- CV-IT -->
- [v7.0] cv31: Alternative italic `a` with top arm
- [v7.0] cv32: Alternative Italic `f` without bottom tail
- [v7.0] cv33: Alternative Italic `i` and `j` with left bottom bar and horizen top bar
- [v7.0] cv34: Alternative Italic `k` without center circle
- [v7.0] cv35: Alternative Italic `l` without center tail
- [v7.0] cv36: Alternative Italic `x` without top and bottom tails
- [v7.0] cv37: Alternative Italic `y` with straight intersection
- [v7.1] cv38: Alternative italic `g` in double story style
- [v7.1] cv39: Alternative Italic `i` without bottom bar
- [v7.1] cv40: Alternative italic `J` without top bar
- [v7.1] cv41: Alternative italic `r` with bottom bar
<!-- CV-IT -->

#### CN Only

<!-- CV-CN -->
- [v7.0] cv96: Full width quotes (`“` / `”` / `‘` / `’`)
- [v7.0] cv97: Full width ellipsis (`…`)
- [v7.0] cv98: Full width emdash (`—`)
- [v7.0] cv99: Traditional centered punctuations
<!-- CV-CN -->

### Stylistic Sets (ssXX)

<!-- SS -->
- [v7.0] ss01: Broken multiple equals ligatures (`==`, `===`, `!=`, `!==` ...)
- [v7.0] ss02: Broken compare and equal ligatures (`<=`, `>=`)
- [v7.0] ss03: Allow to use any case in all tags
- [v7.0] ss04: Broken multiple underscores ligatures (`__`, `#__`)
- [v7.0] ss05: Revert thin backslash in escape symbols (`\\`, `\"`, `\.` ...)
- [v7.0] ss06: Break connected strokes between italic letters (`al`, `il`, `ull` ...)
- [v7.0] ss07: Relax the conditions for multiple greaters ligatures (`>>` or `>>>`)
- [v7.0] ss08: Double headed arrows and reverse arrows ligatures (`>>=`, `-<<`, `->>`, `>-` ...)
- [v7.1] ss09: Asciitilde equal as not equal to ligature (`~=`)
- [v7.1] ss10: Approximately equal to and approximately not equal to ligatures (`=~`, `!~`)
- [v7.1] ss11: Equal and extra punctuation ligatures (`|=`, `/=`, `?=`, `&=`, ...)
<!-- SS -->