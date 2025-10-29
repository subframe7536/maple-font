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

> [!note]
> Enabling OpenType Feature is not supported, you need to custom build to freeze features.

## Ligatures

"Enable ligature", is same as "enable `calt` feature":

<!-- CALT -->
<table>
<tr><td><code>::</code></td><td><code>?.</code></td><td><code>&lt;#--</code></td></tr>
<tr><td><code>:::</code></td><td><code>..&lt;</code></td><td><code>&lt;!----&gt;</code></td></tr>
<tr><td><code>?:</code></td><td><code>.=</code></td><td><code>&lt;-&gt;</code></td></tr>
<tr><td><code>:?</code></td><td><code>&lt;~</code></td><td><code>&lt;--&gt;</code></td></tr>
<tr><td><code>:?&gt;</code></td><td><code>~&gt;</code></td><td><code>-&gt;</code></td></tr>
<tr><td><code>&lt;:</code></td><td><code>~~</code></td><td><code>&lt;-</code></td></tr>
<tr><td><code>:&gt;</code></td><td><code>&lt;~&gt;</code></td><td><code>--&gt;</code></td></tr>
<tr><td><code>:&lt;</code></td><td><code>&lt;~~</code></td><td><code>&lt;--</code></td></tr>
<tr><td><code>&lt;:&lt;</code></td><td><code>~~&gt;</code></td><td><code>&gt;-&gt;</code></td></tr>
<tr><td><code>&gt;:&gt;</code></td><td><code>-~</code></td><td><code>&lt;-&lt;</code></td></tr>
<tr><td><code>__</code></td><td><code>~-</code></td><td><code>|-&gt;</code></td></tr>
<tr><td><code>#{</code></td><td><code>~@</code></td><td><code>&lt;-|</code></td></tr>
<tr><td><code>#[</code></td><td><code>~~~~~~~</code></td><td><code>-------</code></td></tr>
<tr><td><code>#(</code></td><td><code>0xA12 0x56 1920x1080</code></td><td><code>&gt;--</code></td></tr>
<tr><td><code>#?</code></td><td><code>&lt;&gt;</code></td><td><code>--&lt;</code></td></tr>
<tr><td><code>#!</code></td><td><code>&lt;/</code></td><td><code>&lt;|||</code></td></tr>
<tr><td><code>#:</code></td><td><code>/&gt;</code></td><td><code>|||&gt;</code></td></tr>
<tr><td><code>#=</code></td><td><code>&lt;/&gt;</code></td><td><code>&lt;||</code></td></tr>
<tr><td><code>#_</code></td><td><code>&lt;+</code></td><td><code>||&gt;</code></td></tr>
<tr><td><code>#__</code></td><td><code>+&gt;</code></td><td><code>&lt;|</code></td></tr>
<tr><td><code>#_(</code></td><td><code>&lt;+&gt;</code></td><td><code>|&gt;</code></td></tr>
<tr><td><code>]#</code></td><td><code>&lt;*</code></td><td><code>&lt;|&gt;</code></td></tr>
<tr><td><code>#######</code></td><td><code>*&gt;</code></td><td><code>_|_</code></td></tr>
<tr><td><code>&lt;&lt;</code></td><td><code>&lt;*&gt;</code></td><td><code>[TRACE]</code></td></tr>
<tr><td><code>&lt;&lt;&lt;</code></td><td><code>&gt;=</code></td><td><code>[DEBUG]</code></td></tr>
<tr><td><code>&gt;&gt;</code></td><td><code>&lt;=</code></td><td><code>[INFO]</code></td></tr>
<tr><td><code>&gt;&gt;&gt;</code></td><td><code>&lt;=&lt;</code></td><td><code>[WARN]</code></td></tr>
<tr><td><code>{{</code></td><td><code>&gt;=&gt;</code></td><td><code>[ERROR]</code></td></tr>
<tr><td><code>}}</code></td><td><code>==</code></td><td><code>[FATAL]</code></td></tr>
<tr><td><code>{|</code></td><td><code>===</code></td><td><code>[TODO]</code></td></tr>
<tr><td><code>|}</code></td><td><code>!=</code></td><td><code>[FIXME]</code></td></tr>
<tr><td><code>{{--</code></td><td><code>!==</code></td><td><code>[NOTE]</code></td></tr>
<tr><td><code>{{!--</code></td><td><code>=/=</code></td><td><code>[HACK]</code></td></tr>
<tr><td><code>--}}</code></td><td><code>=!=</code></td><td><code>[MARK]</code></td></tr>
<tr><td><code>[|</code></td><td><code>|=</code></td><td><code>[EROR]</code></td></tr>
<tr><td><code>|]</code></td><td><code>&lt;=&gt;</code></td><td><code>[WARNING]</code></td></tr>
<tr><td><code>!!</code></td><td><code>&lt;==&gt;</code></td><td><code>todo))</code></td></tr>
<tr><td><code>||</code></td><td><code>&lt;==</code></td><td><code>fixme))</code></td></tr>
<tr><td><code>??</code></td><td><code>==&gt;</code></td><td><code><em>Cl</em></code></td></tr>
<tr><td><code>???</code></td><td><code>=&gt;</code></td><td><code><em>al</em></code></td></tr>
<tr><td><code>&amp;&amp;</code></td><td><code>&lt;=|</code></td><td><code><em>cl</em></code></td></tr>
<tr><td><code>&amp;&amp;&amp;</code></td><td><code>|=&gt;</code></td><td><code><em>el</em></code></td></tr>
<tr><td><code>//</code></td><td><code>=&lt;=</code></td><td><code><em>il</em></code></td></tr>
<tr><td><code>///</code></td><td><code>=&gt;=</code></td><td><code><em>tl</em></code></td></tr>
<tr><td><code>/*</code></td><td><code>=======</code></td><td><code><em>ul</em></code></td></tr>
<tr><td><code>/**</code></td><td><code>&gt;=&lt;</code></td><td><code><em>xl</em></code></td></tr>
<tr><td><code>*/</code></td><td><code>:=</code></td><td><code><em>ff</em></code></td></tr>
<tr><td><code>++</code></td><td><code>=:</code></td><td><code><em>tt</em></code></td></tr>
<tr><td><code>+++</code></td><td><code>:=:</code></td><td><code><em>all</em></code></td></tr>
<tr><td><code>;;</code></td><td><code>=:=</code></td><td><code><em>ell</em></code></td></tr>
<tr><td><code>;;;</code></td><td><code>\\ \&#x27; \.</code></td><td><code><em>ill</em></code></td></tr>
<tr><td><code>..</code></td><td><code>--</code></td><td><code><em>ull</em></code></td></tr>
<tr><td><code>...</code></td><td><code>---</code></td><td><code><em>ll</em></code></td></tr>
<tr><td><code>.?</code></td><td><code>&lt;!--</code></td><td></td></tr>
</table>
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
- [v7.5] cv09: Alternative `7` with middle bar, no effect in italic style
- [v7.5] cv10: Alternative `Z` and `z` with middle bar, no effect in italic style
- [v7.7] cv11: Alternative `f` with bottom bar
- [v7.1] cv61: Alternative `,` and `;` with straight tail
- [v7.1] cv62: Alternative `?` with larger openings
- [v7.1] cv63: Alternative `<=` in arrow style
- [v7.3] cv64: Alternative `<=` and `>=` with horizen bottom bar
- [v7.3] cv65: Alternative `&` in handwriting style
- [v7.8] cv66: Alternative pipe arrows
- [v7.0] zero: Dot style `0`
<!-- CV -->

#### Italic Only

<!-- CV-IT -->
- [v7.0] cv31: Alternative italic _`a`_ with top arm
- [v7.0] cv32: Alternative Italic _`f`_ without bottom tail
- [v7.0] cv33: Alternative Italic _`i`_ and _`j`_ with left bottom bar and horizen top bar
- [v7.0] cv34: Alternative Italic _`k`_ without center circle
- [v7.0] cv35: Alternative Italic _`l`_ without center tail
- [v7.0] cv36: Alternative Italic _`x`_ without top and bottom tails
- [v7.0] cv37: Alternative Italic _`y`_ with straight intersection
- [v7.1] cv38: Alternative italic _`g`_ in double story style
- [v7.1] cv39: Alternative Italic _`i`_ without bottom bar
- [v7.1] cv40: Alternative italic _`J`_ without top bar
- [v7.1] cv41: Alternative italic _`r`_ with bottom bar
- [v7.5] cv42: Alternative italic _`7`_ with middle bar
- [v7.5] cv43: Alternative italic _`Z`_ and _`z`_ with middle bar
- [v7.7] cv44: Alternative Italic _`f`_ with bottom bar
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
- [v7.0] ss06: Break connected strokes between italic letters (_`al`_, _`il`_, _`ull`_ ...)
- [v7.0] ss07: Relax the conditions for multiple greaters ligatures (`>>` or `>>>`)
- [v7.0] ss08: Double headed arrows and reverse arrows ligatures (`>>=`, `-<<`, `->>`, `>>-` ...)
- [v7.1] ss09: Asciitilde equal as not equal to ligature (`~=`)
- [v7.1] ss10: Approximately equal to and approximately not equal to ligatures (`=~`, `!~`)
- [v7.1] ss11: Equal and extra punctuation ligatures (`|=`, `/=`, `?=`, `&=`, ...)
<!-- SS -->