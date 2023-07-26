from fontTools.ttLib import TTFont, woff2
import shutil
from afdko.otf2ttf import otf_to_ttf
from os import path, getcwd, makedirs, listdir, remove, write
from subprocess import run
from zipfile import ZipFile
from urllib.request import urlopen
import platform
from ttfautohint import ttfautohint

config = {
    "nerd_font": True,  # whether to use nerd font
    "mono": True,  # whether to use half width icon
    "family_name": "Maple Mono",  # font family name
    "nf_use_hinted_ttf": True,  # whether to use hinted ttf to generate Nerd Font
}

root = getcwd()
ttx_path = path.join(root, "ttx")
output_path = path.join(path.dirname(root), "output")

family_name = config["family_name"]
family_name_trim = family_name.replace(" ", "")

if not path.exists(path.join(root, "FontPatcher")):
    url = "https://github.com/ryanoasis/nerd-fonts/releases/download/latest/FontPatcher.zip"
    print(f"download Font Patcher from {url}")
    try:
        zip_path = path.join(root, "FontPatcher.zip")
        if not path.exists(zip_path):
            with urlopen(url) as response, open(zip_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(path.join(root, "FontPatcher"))
        remove(zip_path)
    except Exception as e:
        print(
            "fail to download Font Patcher, please consider to manually download it and put downloaded 'FontPatcher.zip' in the 'source' folder."
        )
        exit(1)


def mkdirs(dir):
    if not path.exists(dir):
        makedirs(dir)


mkdirs(path.join(output_path, "otf"))
mkdirs(path.join(output_path, "ttf"))
mkdirs(path.join(output_path, "ttf-autohint"))
mkdirs(path.join(output_path, "woff2"))


def auto_hint(f: str, ttf_path: str):
    ttfautohint(
        in_file=ttf_path,
        out_file=path.join(output_path, "ttf-autohint", f + ".ttf"),
    )


def generate_nerd_font(f: str):
    def get_arg(key: str):
        return "1" if config[key] else "0"

    run(
        [
            path.join(
                root,
                f"generate-nerdfont.{'bat' if platform.system() == 'Windows' else 'sh'}",
            ),
            f,
            get_arg("mono"),
            get_arg("nf_use_hinted_ttf"),
        ]
    )
    _, sub = f.split("-")
    mono = "Mono" if config["mono"] else ""
    nf_path = path.join(
        output_path,
        "NF",
        f"{family_name_trim}NerdFont{mono}-{sub}.ttf",
    )

    nf_font = TTFont(nf_path)

    def set_name(name: str, id: int):
        nf_font["name"].setName(
            name, nameID=id, platformID=3, platEncID=1, langID=0x409
        )
        nf_font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)

    def get_name(id: int):
        return nf_font["name"].getName(nameID=id, platformID=3, platEncID=1)

    def del_name(id: int):
        nf_font["name"].removeNames(nameID=id)

    # correct names
    set_name(f"{family_name} NF", 1)
    set_name(sub, 2)
    set_name(f"{family_name} NF {sub}; {get_name(5)}", 3)
    set_name(f"{family_name} NF {sub}", 4)
    set_name(f"{family_name_trim}NF-{sub}", 6)

    # remove additional names
    del_name(16)
    del_name(17)
    del_name(18)
    del_name(20)

    nf_font.importXML(path.join(ttx_path, f, f + ".O_S_2f_2.ttx"))

    nf_font.save(path.join(output_path, "NF", f"{family_name_trim}-NF-{sub}.ttf"))
    nf_font.close()

    remove(nf_path)


print("=== build start ===")
for f in listdir(ttx_path):
    print("generate:", f)

    font = TTFont()
    font.importXML(fileOrPath=path.join(root, "ttx", f, f + ".ttx"))

    _, sub = f.split("-")

    def set_name(name: str, id: int):
        font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)

    def get_name(id: int):
        font["name"].getName(nameID=id, platformID=3, platEncID=1)

    set_name(family_name, 1)
    set_name(f"{family_name} {sub}; {get_name(5)}", 3)
    set_name(f"{family_name} {sub}", 4)
    set_name(f"{family_name_trim}-{sub}", 6)

    otf_path = path.join(output_path, "otf", f + ".otf")
    ttf_path = path.join(output_path, "ttf", f + ".ttf")

    font.save(otf_path)

    otf_to_ttf(font)
    font.save(ttf_path)

    auto_hint(f, ttf_path)

    font.close()

    if config["nerd_font"]:
        generate_nerd_font(f)

    woff2.compress(otf_path, path.join(output_path, "woff2", f + ".woff2"))


print("=== build end ===")

woff2_path = path.join(path.dirname(output_path), "woff2")

with open(path.join(output_path, "NF", "config.txt"), "w") as file:
    file.write(f"use_hinted_ttf = {config['nf_use_hinted_ttf']}\n")
    file.write(f"mono = {config['mono']}\n")

if path.exists(woff2_path):
    shutil.rmtree(woff2_path)
shutil.copytree(path.join(output_path, "woff2"), woff2_path)
print("=== copy woff to root ===")
