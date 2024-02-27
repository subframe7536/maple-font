#!/bin/sh
set -xeuo

python=$(which python3)
output_dir="../output/NF"
font_dir="../output/ttf"

if [ "$3" = "1" ]; then
    font_dir="${font_dir}-autohint"
fi

if [ ! -d "${font_dir}" ]; then
    echo "Font directory does not exist: ${font_dir}"
    exit 1
fi

# full args: https://github.com/ryanoasis/nerd-fonts#font-patcher
args="-l -c --careful"
if [ "$2" = "1" ]; then
    args="${args} -s"
fi

font_name="$1"
target_font_path="${font_dir}/${font_name}.ttf"

if [ ! -f "${target_font_path}" ]; then
    echo "Font file does not exist: ${target_font_path}"
    exit 1
fi

eval "${python} ./FontPatcher/font-patcher ${args} --outputdir ${output_dir} ${target_font_path}"