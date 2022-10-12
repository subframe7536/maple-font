<br>

<p align="center">
  <img src="./img/head.svg" height="230" alt="logo">
</p>

<h1 align="center"> Maple Font </h1>

<p align="center">
带连字和圆角的等宽字体和控制台字体
</p>

<p align="center">
  <a>
    <img src="https://img.shields.io/github/v/release/subframe7536/Maple-font?display_name=tag" alt="release version">
  </a>
</p>

<p align="center">
  <a href="#安装">安装</a> | 
  <a href="https://github.com/users/subframe7536/projects/1">下一步计划</a> |
  <a href="./README.md">English</a>
</p>


## 特性

参考了 [Source Code Pro](https://github.com/adobe-fonts/source-code-pro)、[Fira Code Retina](https://github.com/tonsky/FiraCode)、[Sarasa Mono SC Nerd](https://github.com/laishulu/Sarasa-Mono-SC-Nerd) 等优秀字体, 但是：

- 🎨 **新的形状** -  比如 `@ # $ % &` 和新的斜体样式
- 🤙🏻 **更多连字** - 比如 `.., ..., /*, /**` 
- 📦 **更小的体积** - 只留下了基础拉丁文（英数 + 符号）、制表符
- 🦾 **更好的渲染效果** - 参考`Fira Code Retina`重新设计了字形，将宽度从原来的 600 改成了 1200，以下是在 1080p 屏幕上的对比

  | v4                                                     | v5                                                      |
  | :----------------------------------------------------- | :------------------------------------------------------ |
  | <img src="./img/sizechange.gif" height="200" alt="v4"> | <img src="./img/sizechange1.gif" height="200" alt="v5"> |

- 🗒 **更易于阅读** - 花体斜体；优化字形，降低大写和数字的高度；减少间距，现在和 `Jetbrains Mono`间距类似，居中显示 `+ - * = ^ ~ < >` 
- ✨ 点击查看 [屏幕截图](#屏幕截图) 


## 安装

| Platform   | Command                                                                                                                                  |
| :--------- | :--------------------------------------------------------------------------------------------------------------------------------------- |
| macOS      | ` brew tap homebrew/cask-fonts && brew install font-maple`                                                                               |
| Arch Linux | `sudo pacman -S ttf-maple`                                                                                                               |
| Others     | 从 [releases](https://github.com/subframe7536/Maple-font/releases) 中下载安装，[国内地址](https://gitee.com/subframe7536/Maple/releases) |




## 注意事项

因为我没有 mac 的机子，所以目前能做的适配我都做了，但是出了问题没法测试...所以可能需要研究研究
目前有好几个问题重启解决了...
有问题欢迎提 issue

`Maple Mono NF` `Maple Mono SC NF`可能没法被识别为等宽字体，我尽力了，来个大佬吧 qwq

如果觉得字太宽，可以使用 [更纱黑体 SC Nerd](https://github.com/laishulu/Sarasa-Mono-SC-Nerd)



## 屏幕截图


<details>
<summary><b>Total (click to expand!)</b></summary>

![](img/base.png)

</details>



<details>
<summary><b>Ligature</b></summary>

![](img/ligature.png)
![](img/ligature.gif)

</details>



<details>
<summary><b>Cli</b></summary>

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

![](img/code_sample/go.webp)

</details>


<details>
<summary><b>Python</b></summary>

![](img/code_sample/python.webp)

</details>


<details>
<summary><b>Rust</b></summary>

![](img/code_sample/rust.webp)


</details>

## 构建

```
git clone https://github.com/subframe7536/Maple-font
cd Maple-font/source
pip install fonttools
python build.py
```

## [Maple Mono SC NF](#maple-mono-sc-nf)

- ✨ 合并了 NF 和 SC，现在只需一个字体就可以适用所有**编码**场景，并且支持中英文 2:1
- 需要当作阅读字体请使用 Maple UI
- (半成品)支持使用其他的字体生成中文部分
- (v5.5)中文的间距也减小了，高度进行了调整
- 中英文 2:1 + Nerd Font 控制台字体
- 在 VSCode 和 IDEA 上测试均能正常显示

<p align="center">
  <img src="./img/CE21.png" alt="logo">
</p>

## Maple UI

> 自改自用的字体，用的是 Google Sans 英数 + 中兴正圆的汉字，侵删


- Windows 使用 [noMeiryoUI](https://github.com/Tatsu-syo/noMeiryoUI) + [Mactype](https://github.com/snowie2000/mactype) + [自用脚本](https://gitee.com/subframe7536/mactype) 进行全局替换并优化渲染效果
- 网页使用 油猴/暴力猴插件 + [自用脚本](https://github.com/subframe7536/UserScript) 全局字体替换，有些不适配的可以手动添加 css
- 较上一版粗暴的减小了粗细，有可能有些字形粗细不正常或错位，欢迎提 issue
- 扩大了中文引号的宽度

<p align="center">
  <img src="./img/UI.webp">
  <img src="./img/Browser.webp">
  <img src="./img/Browser2.webp">
</p>


## Maple Hand

手写体，クレ pro 英数微调+唐美人汉字部分，目前用在手机端，配合空字体模块做全局字体模块

### 样例

<p align="center">
  <img src="./img/%E6%89%8B%E6%9C%BA.jpg">
</p>


## 许可证

SIL Open Font License 1.1

## 免责声明

本项目中`Maple Mono SC NF`中的汉仪正圆仅供学习与交流，本人不对使用、传播本程序及附属产物造成的任何后果承担任何责任
