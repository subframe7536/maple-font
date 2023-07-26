#!/bin/bash

font_dir="../output/ttf"
output_dir="../output/NF"
args="-l -c --careful"

if [ ! -d $font_dir ]; then
    echo "Font directory does not exist: $font_dir"
    exit 1
fi

font_name=$1

if [ $2 -eq 1 ]; then
    args="$args -s"
fi

if [ $3 -eq 1 ]; then
    font_dir=$font_dir-autohint
fi

font_path=$font_dir/$font_name.ttf

if [ ! -f $font_path ]; then
    echo "Font file does not exist: $font_path"
    exit 1
fi

fontforge -script ./FontPatcher/font-patcher $args --outputdir $output_dir $font_path

echo "Font patched successfully!"