![](/img/head.svg)

# Maple Series V5

## 下载

Release

[国内地址](https://gitee.com/subframe7536/Maple/releases/v5.0)

### V5 新增

- ✨ 参考`Fira Code Retina`重新设计了字形，将宽度从原来的 600 改成了 1200，应该可以提升低分屏上的渲染效果，下面是在我的屏幕(1080P)下测试的对比
  - v4: ![](/img/sizechange.gif)
  - v5: ![](/img/sizechange1.gif)
- 优化字形，降低大写和数字的高度，提升阅读舒适度
- 添加`..`,`...`的连字，有其他需要可以提 issue

---

[Maple Mono SC NF](#maple-mono-sc-nf)

- ✨ 合并了 NF 和 SC，现在只需一个字体就可以适用所有场景，并且支持中英文 2:1
- (半成品)支持使用其他的字体生成中文部分

## Maple Mono

开源的圆角等宽字体，只有基础拉丁文(英数+符号)、制表符

- 参考了 [Source Code Pro](https://github.com/adobe-fonts/source-code-pro), [Fira Code](https://github.com/tonsky/FiraCode), ubuntu mono, operator mono, [sarasa mono sc nerd](https://github.com/laishulu/Sarasa-Mono-SC-Nerd) 等优秀字体
- 修改了`@ # $ % &`的形状
- 有连字
- 花体的斜体
- `source/mono.fea`: 有注释的 OpenType 脚本，方便阅读

### 样例

#### 全部字符

![](img/base.png)

#### Ligature

![](img/ligature.png)
![](img/ligature.gif)

#### Cli

![](img/code_sample/cli.webp)

#### React

![](img/code_sample/react.webp)

#### Vue

![](img/code_sample/vue.webp)

#### Java

![](img/code_sample/java.webp)

#### Go

![](img/code_sample/go.webp)

#### Python

![](img/code_sample/python.webp)

#### Rust

![](img/code_sample/rust.webp)

## 开发

### 使用的模块

python fonttools

### 如何构建

```
git clone https://github.com/subframe7536/Maple-font
cd Maple-font/source
pip install fonttools
python build.py
```

## Maple Mono SC NF

中英文 2:1 + Nerd Font 控制台字体

- 在 VSCode 和 IDEA 上测试均能正常显示

![](/img/CE21.png)

## Maple UI

自改自用的字体，用的是 Google Sans 英数 + 中兴正圆的汉字，侵删

自用在 浏览器 和 Window 全局字体

Windows 使用 [noMeiryoUI](https://github.com/Tatsu-syo/noMeiryoUI)全局替换windows字体 + [Mactype](https://github.com/snowie2000/mactype) + [自用脚本](https://gitee.com/subframe7536/mactype) 进行全局替换，网页使用 油猴/暴力猴插件 + [自用脚本](https://github.com/subframe7536/UserScript) 全局字体替换，有些不适配的可以手动添加 css

- 较上一版粗暴的减小了粗细，有可能有些字形粗细不正常或错位，欢迎提 issue
- 扩大了中文引号的宽度

### 样例

![](img/UI.webp)
![](img/Browser.webp)
![](img/Browser2.webp)

## Maple Hand

手写体，クレ pro 英数微调+唐美人汉字部分，目前用在手机端，配合空字体模块做全局字体模块

### 样例

![](img/%E6%89%8B%E6%9C%BA.jpg)

## 许可证

SIL Open Font License 1.1
