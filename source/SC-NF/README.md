# !!! 此脚本还未完成，仅供参考 !!!

# 中英文 2:1 生成

## 需要的模块

fontforge
fonttools

## 方法

1. 将中文字体放入 SC
2. 默认的格式是 regular.ttf、bold.ttf、italic.ttf、bolditalic.ttf
3. generate.bat

## 注意事项

1. 中文字体宽度需要 2400，不然无法中英文 2:1
2. fontforge script 我用不太来，setWidth() 设置宽度会导致“日”偏掉，CenterInWidth() 会导致“月”骗掉，建议直接用 font creater
3. Nerd Font 的 Material icons 会导致部分不常用中文字被占用，不清楚 fontforge 是否会直接覆盖
