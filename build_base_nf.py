from os import path, remove
from fontTools.varLib import TTFont
from fontTools.subset import Subsetter

from source.py.utils import del_font_name, get_font_forge_bin, set_font_name,run

base_font_path = "fonts/TTF/MapleMono-Regular.ttf"
family_name = "Maple Mono"

font_forge_bin = get_font_forge_bin()

if not path.exists(base_font_path):
    print("font not exist, please run `python build.py` first")
    exit(1)


def get_nerd_font_patcher_args(mono: bool):
    # full args: https://github.com/ryanoasis/nerd-fonts?tab=readme-ov-file#font-patcher
    _nf_args = [
        font_forge_bin,
        "FontPatcher/font-patcher",
        "-l",
        "-c",
        "--careful",
    ]
    if mono:
        _nf_args += ["--mono"]

    return _nf_args


def build_nf(mono: bool):
    nf_args = get_nerd_font_patcher_args(mono)

    nf_file_name = "NerdFont"
    if mono:
        nf_file_name += "Mono"

    style_name = "Regular"

    run(nf_args + [base_font_path])
    _path = f"{family_name.replace(' ', '')}{nf_file_name}-{style_name}.ttf"
    nf_font = TTFont(_path)
    remove(_path)

    set_font_name(nf_font, f"{family_name} NF Base{' Mono' if mono else ''}", 1)
    set_font_name(nf_font, style_name, 2)
    set_font_name(nf_font, f"{family_name} NF Base{' Mono' if mono else ''} {style_name}", 4)
    set_font_name(nf_font, f"{family_name.replace(' ', '-')}-NF-Base{'-Mono' if mono else ''}-{style_name}", 6)
    del_font_name(nf_font, 16)
    del_font_name(nf_font, 17)

    return nf_font


def subset(mono: bool):
    font = build_nf(mono)
    subsetter = Subsetter()
    subsetter.populate(
        unicodes=range(0xE000, 0xF1AF0),
    )
    subsetter.subset(font)

    # font.save("source/NerdFontBase.ttf")
    font.save(f"source/MapleMono-NF-Base{'-Mono' if mono else ''}.ttf")
    font.close()


subset(True)
subset(False)
