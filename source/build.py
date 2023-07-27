from fontTools.ttLib import TTFont, woff2
from afdko.otf2ttf import otf_to_ttf
from os import path, getcwd, makedirs, listdir, remove
from subprocess import run
from zipfile import ZipFile
from urllib.request import urlopen
from ttfautohint import ttfautohint
from enum import Enum, unique
import shutil
import platform
import json


@unique
class Status(Enum):
    DISABLE = "0"
    ENABLE = "1"
    IGNORE = "2"


config = {
    "family_name": "Maple Mono",  # font family name
    "freeze_feature_list": {
        "ss01": Status.IGNORE,  # == === != !==
        "ss02": Status.IGNORE,  # [info] [trace] [debug] [warn] [error] [fatal] [vite]
        "ss03": Status.IGNORE,  # __
        "ss04": Status.IGNORE,  # >= <=
        "ss05": Status.IGNORE,  # {{ }}
        "cv01": Status.IGNORE,  # @ # $ % & Q -> =>
        "cv02": Status.IGNORE,  # alt i
        "cv03": Status.IGNORE,  # alt a
        "cv04": Status.IGNORE,  # alt @
        "zero": Status.IGNORE,  # alt 0
    },
    "nerd_font": {
        "enable": Status.ENABLE,  # whether to use nerd font
        "mono": Status.ENABLE,  # whether to use half width icon
        "use_hinted": Status.ENABLE,  # whether to use hinted ttf to generate Nerd Font
    },
}

root = getcwd()
ttx_path = path.join(root, "ttx")
output_path = path.join(path.dirname(root), "output")

family_name = config["family_name"]
family_name_trim = family_name.replace(" ", "")

if not path.exists(path.join(root, "FontPatcher")):
    url = "https://github.com/ryanoasis/nerd-fonts/releases/download/latest/FontPatcher.zip"
    print(f"Font Patcher does not exist, download from {url}")
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
            "fail to download Font Patcher, please consider to download it manually, put downloaded 'FontPatcher.zip' in the 'source' folder and run this script again."
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
    if config["nerd_font"]["enable"] != Status.ENABLE:
        return

    run(
        [
            path.join(
                root,
                f"generate-nerdfont.{'bat' if platform.system() == 'Windows' else 'sh'}",
            ),
            f,
            config["nerd_font"]["mono"].value,
            config["nerd_font"]["use_hinted"].value,
        ]
    )
    _, sub = f.split("-")

    nf_path = path.join(
        output_path,
        "NF",
        f"{family_name_trim}NerdFont-{sub}.ttf",
    )
    # load font
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

    # save font
    nf_font.save(path.join(output_path, "NF", f"{family_name_trim}-NF-{sub}.ttf"))
    nf_font.close()

    # remove original font
    remove(nf_path)


print("=== build start ===")

conf = json.dumps(
    config,
    default=lambda x: x.name if isinstance(x, Status) else None,
    indent=4,
)

print(conf)

# write config
with open(path.join(output_path, "config.json"), "w") as file:
    file.write(conf)

for f in listdir(ttx_path):
    print("generate:", f)

    # load font
    font = TTFont()
    font.importXML(fileOrPath=path.join(root, "ttx", f, f + ".ttx"))

    # check feature list
    feature_dict = {
        feature.FeatureTag: feature.Feature
        for feature in font["GSUB"].table.FeatureList.FeatureRecord
    }

    calt_lookup_list = feature_dict.get("calt").LookupListIndex

    for key, features in feature_dict.items():
        if key == "calt":
            continue

        if config["freeze_feature_list"][key] == Status.ENABLE:
            calt_lookup_list.extend(features.LookupListIndex)
        elif config["freeze_feature_list"][key] == Status.DISABLE:
            features.LookupListIndex = []

    # correct names
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

    # save otf font
    font.save(otf_path)

    # save ttf font
    otf_to_ttf(font)
    font.save(ttf_path)

    # auto hint
    auto_hint(f, ttf_path)

    font.close()

    # generate nerd font
    generate_nerd_font(f)

    # generate woff2
    woff2.compress(otf_path, path.join(output_path, "woff2", f + ".woff2"))


print("=== build end ===")


# copy woff
woff2_path = path.join(path.dirname(output_path), "woff2")
if path.exists(woff2_path):
    shutil.rmtree(woff2_path)
shutil.copytree(path.join(output_path, "woff2"), woff2_path)
print("=== copy woff to root ===")
