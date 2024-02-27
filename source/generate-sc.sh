#!/bin/sh
set -xeuo
python=$(which python3)
python_forge_exe=$(which fontforge)

#@REM available: ttf / ttf-autohint / nf
#@REM 构建的基准字体
base_font="nf"

#@REM available: 0 / 1
#@REM 是否修复编码和元数据，出现乱码时可尝试切换
fix_encoding_and_meta=1

${python} ./SC/merge.py ${base_font} $1

if [ $? -eq 0 ];then
    ${python} ./SC/fix.py ${base_font} ${fix_encoding_and_meta} $1
fi
