from os import path, remove
import platform
import subprocess
from fontTools.varLib import TTFont
from fontTools.subset import Subsetter

base_font_path = "fonts/TTF/MapleMono-Regular.ttf"
family_name = "Maple Mono"

WIN_FONTFORGE_PATH = "C:/Program Files (x86)/FontForgeBuilds/bin/fontforge.exe"
MAC_FONTFORGE_PATH = (
    "/Applications/FontForge.app/Contents/Resources/opt/local/bin/fontforge"
)
LINUX_FONTFORGE_PATH = "/usr/local/bin/fontforge"

system_name = platform.uname()[0]

font_forge_bin = LINUX_FONTFORGE_PATH
if "Darwin" in system_name:
    font_forge_bin = MAC_FONTFORGE_PATH
elif "Windows" in system_name:
    font_forge_bin = WIN_FONTFORGE_PATH

if not path.exists(base_font_path):
    print("font not exist, please run `python build.py` first")
    exit(1)


def set_font_name(font: TTFont, name: str, id: int):
    font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)
    font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)


def del_font_name(font: TTFont, id: int):
    font["name"].removeNames(nameID=id)


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

    subprocess.run(nf_args + [base_font_path])
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
