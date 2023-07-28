<br>

<p align="center">
  <img src="./img/head.svg" height="230" alt="logo">
</p>

<h1 align="center"> Maple Font </h1>

<p align="center">
Open source monospace & nerd font with round corner and ligatures.
</p>

<p align="center">
  <a href="https://github.com/subframe7536/Maple-font/releases">
    <img src="https://img.shields.io/github/v/release/subframe7536/Maple-font?display_name=tag" alt="release version">
  </a>
</p>

<p align="center">
  <a href="#install">install</a> |
  <a href="https://github.com/users/subframe7536/projects/1">what's next</a> |
  English |
  <a href="./README_CN.md">中文</a>
</p>



## Features

Inspired by [Source Code Pro](https://github.com/adobe-fonts/source-code-pro), [Fira Code Retina](https://github.com/tonsky/FiraCode), [Sarasa Mono SC Nerd](https://github.com/laishulu/Sarasa-Mono-SC-Nerd) and so on, but:

- 🎨 **New shape** - such as `@ # $ % &` and new shape of italic style
- 🤙🏻 **More ligatures** - such as `.., ..., /*, /**`
- 📦 **Small size** - leave only contains latin, standard set of accents, table control characters and few symbols
- 🦾 **Better rendering effect** - redesigned it according to Fira Code Retina's spacing and glyph

  |                           v4                           |                           v5                            |
  | :----------------------------------------------------: | :-----------------------------------------------------: |
  | <img src="./img/sizechange.gif" height="200" alt="v4"> | <img src="./img/sizechange1.gif" height="200" alt="v5"> |
  |     `+` and `=` are not centered at some font-size     |             `+` and `=` are always centered             |

- 🗒 **More readable** - cursive style, better glyph shape, lower the height of capital letters and numbers, reduce or modify kerning and center operators `+ - * = ^ ~ < >`
- 🛠️ **More configable** - enable or disable font features as you want, just make your own font
- ✨ See it in [screenshots](#screenshots)



## Install


| Platform   | Command                                                                     |
| :--------- | :-------------------------------------------------------------------------- |
| macOS      | `brew tap homebrew/cask-fonts && brew install font-maple`                   |
| Arch Linux | `paru -S ttf-maple-latest`                                                  |
| Others     | Download in [releases](https://github.com/subframe7536/Maple-font/releases) |





## Notice


Because I don't have a Mac OS machine, this is the greatest adaption I can do with Mac OS currently, but I can't test whether it works.

My ability is not enough to solve other problems on Mac OS. I will record the problem and try to solve it, and **PR welcome!**

`Maple Mono NF` now maybe can't be recognized as Mono, and I try my best but it doesn't work orz


## Overview

<p align="center">
<img src="./img/base.png" /><br>
<img src="./img/ligature.png" /><br>
<img src="./img/ligature.gif"/><br>
multiply ways to get TODO tag<br>
ps: in Jetbrains' product, [todo) can't be properly rendered, so please use todo))<br>
</p>
<p align="center">
<img src="./img/option.png"/><br>
compatibility & usage: in <a href="https://github.com/tonsky/FiraCode#editor-compatibility-list" target="_blank">FiraCode README</a>
</p>

## Screenshots

code theme: [vscode-theme-maple](https://github.com/subframe7536/vscode-theme-maple)

generate by: [VSCodeSnap](https://github.com/luisllamasbinaburo/VSCodeSnap)

<details>
<summary><b>Cli (click to expand!)</b></summary>

![](img/code_sample/cli.webp)

</details>



<details>
<summary><b>React</b></summary>

![](img/code_sample/react.webp)

</details>



<details>
<summary><b>Vue</b></summary>

![](img/code_sample/vue.webp)

</details>


<details>
<summary><b>Java</b></summary>

![](img/code_sample/java.webp)

</details>


<details>
<summary><b>Go</b></summary>

<p align="center">
  <img src="img/code_sample/go.webp" width="320"/>
</p>

</details>


<details>
<summary><b>Python</b></summary>

![](img/code_sample/python.webp)

</details>


<details>
<summary><b>Rust</b></summary>

![](img/code_sample/rust.webp)


</details>


## Build

to patch Nerd Font, make sure `fontforge` is installed

you can adjust some config in `source/build.py`

Currently, the build script is only available on Windows. PRs for other platform are welcome!

more fine-grained options can be set at the comming V7


### Normal Build

```shell
git clone https://github.com/subframe7536/Maple-font --depth 1
cd ./Maple-font/source
pip install -r requirements.txt
python build.py
```

### Build font with Chinese characters

```shell
git clone https://github.com/subframe7536/Maple-font --depth 1 -b chinese
cd ./Maple-font/source
pip install -r requirements.txt
python build.py
```

## Donate

If this was helpful to you, please feel free to buy me a coffee

<a href="https://www.buymeacoffee.com/subframe753"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=subframe753&button_colour=5F7FFF&font_colour=ffffff&font_family=Lato&outline_colour=000000&coffee_colour=FFDD00" /></a>

![](img/donate.webp)

## License

SIL Open Font License 1.1
