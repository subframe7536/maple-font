from fontTools.ttLib import TTFont, woff2
from afdko.otf2ttf import otf_to_ttf
from os import path, getcwd, makedirs, listdir, remove, walk
from subprocess import run
from zipfile import ZipFile, ZIP_DEFLATED
from urllib.request import urlopen
from ttfautohint import ttfautohint
from enum import Enum, unique
import shutil
import json
import hashlib
import platform


@unique
class Status(Enum):
    DISABLE = "0"
    ENABLE = "1"
    IGNORE = "2"


# whether to archieve fonts
release_mode = True
# whether to build nerd font
build_nerd_font = True
# whether to clear old build before build new
clear_old_build = True

build_config = {
    # font family name
    "family_name": "Maple Mono",
    # whether to enable font features by default
    "freeze_feature_list": {
        # ======
        # ligatures:
        # Status.IGNORE: do nothing
        # Status.ENABLE: move font features to default ligature
        # Status.DISABLE: remove font features
        "ss01": Status.IGNORE,  # == === != !==
        "ss02": Status.IGNORE,  # [info] [trace] [debug] [warn] [error] [fatal] [vite]
        "ss03": Status.IGNORE,  # __
        "ss04": Status.IGNORE,  # >= <=
        "ss05": Status.IGNORE,  # {{ }}
        # ======
        # character variant:
        # Status.IGNORE: do nothing
        # Status.ENABLE: enable character variants by default
        # Status.DISABLE: remove character variants
        "cv01": Status.IGNORE,  # @ # $ % & Q -> =>
        "cv02": Status.IGNORE,  # alt i
        "cv03": Status.IGNORE,  # alt a
        "cv04": Status.IGNORE,  # alt @
        "zero": Status.IGNORE,  # alt 0
        # ======
    },
    # config for nerd font
    # total config: generate-nerdfont.{bat/sh}:17
    "nerd_font": {
        "mono": Status.ENABLE,  # whether to use half width icon
        "use_hinted": Status.ENABLE,  # whether to use hinted ttf to generate Nerd Font patch
    },
}

root = getcwd()
ttx_path = path.join(root, "ttx")
output_path = path.join(path.dirname(root), "output")

family_name = build_config["family_name"]
family_name_trim = family_name.replace(" ", "")

if not path.exists(path.join(root, "FontPatcher")):
    url = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.2/FontPatcher.zip"
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
            f"fail to download Font Patcher, please consider to download it manually, put downloaded 'FontPatcher.zip' in the 'source' folder and run this script again. Error: {e}"
        )
        exit(1)


def mkdirs(dir):
    if not path.exists(dir):
        makedirs(dir)


if clear_old_build and path.exists(output_path):
    shutil.rmtree(output_path)

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
    if not build_nerd_font:
        return

    system = platform.uname()[0]
    script = f"generate-nerdfont.bat"
    if "Windows" not in system:
        script = f"generate-nerdfont.sh"

    run(
        [
            path.join(
                root,
                script,
            ),
            f,
            build_config["nerd_font"]["mono"].value,
            build_config["nerd_font"]["use_hinted"].value,
        ]
    )
    _, sub = f.split("-")

    mono = "Mono" if build_config["nerd_font"]["mono"] == Status.ENABLE else ""
    nf_path = path.join(
        output_path,
        "NF",
        f"{family_name_trim}NerdFont{mono}-{sub}.ttf",
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


print("=== [build start] ===")

conf = json.dumps(
    build_config,
    default=lambda x: x.name if isinstance(x, Status) else None,
    indent=4,
)

print(conf)


for f in listdir(ttx_path):
    # load font
    font = TTFont()
    font.importXML(fileOrPath=path.join(root, "ttx", f, f + ".ttx"))

    # check feature list
    feature_record = font["GSUB"].table.FeatureList.FeatureRecord
    feature_dict = {feature.FeatureTag: feature.Feature for feature in feature_record}

    calt_lookup_list = feature_dict.get("calt").LookupListIndex

    def replace_glyph(old_key: str, new_key: str):
        cff_dict = font["CFF "].cff.values()[0].CharStrings.charStrings
        hmtx_dict = font["hmtx"].metrics
        if not (
            old_key in cff_dict
            and old_key in hmtx_dict
            and new_key in cff_dict
            and new_key in hmtx_dict
        ):
            print(f"{old_key} or {new_key} does not exist")
            return
        else:
            cff_dict[old_key] = cff_dict[new_key]
            hmtx_dict[old_key] = hmtx_dict[new_key]

    for key, feat in feature_dict.items():
        if key == "calt":
            continue

        status = build_config["freeze_feature_list"][key]
        if status == Status.IGNORE:
            continue

        if status == Status.DISABLE:
            # clear lookup list
            feat.LookupListIndex = []
        elif key.startswith("ss"):
            # to freeze styleset, target lookup list should be push into calt's lookup list
            calt_lookup_list.extend(feat.LookupListIndex)
        else:
            # to freeze character variants, apply the replacement of pair that defined in lookup list in cff table and hmtx table
            for index in feat.LookupListIndex:
                dict = font["GSUB"].table.LookupList.Lookup[index].SubTable[0].mapping
                for k, v in dict.items():
                    replace_glyph(k, v)

    # correct names
    _, sub = f.split("-")

    current_family = f"{family_name_trim}-{sub}"

    # correct names
    def set_name(name: str, id: int):
        font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)

    def get_name(id: int):
        font["name"].getName(nameID=id, platformID=3, platEncID=1)

    set_name(family_name, 1)
    set_name(sub, 2)
    set_name(f"{family_name} {sub}; {get_name(5)}", 3)
    set_name(f"{family_name} {sub}", 4)
    set_name(current_family, 6)

    otf_path = path.join(output_path, "otf", f"{current_family}.otf")
    ttf_path = path.join(output_path, "ttf", f"{current_family}.ttf")

    # save otf font
    font.save(otf_path)

    # save ttf font
    otf_to_ttf(font)
    font.save(ttf_path)

    # auto hint
    auto_hint(current_family, ttf_path)

    font.close()

    # generate nerd font
    generate_nerd_font(f)

    # generate woff2
    woff2.compress(otf_path, path.join(output_path, "woff2", f"{current_family}.woff2"))

    print("generated:", current_family)

# check whether have script to generate sc
sc_path = path.join(
    root,
    f"generate-sc.bat",
)
if path.exists(sc_path):
    run([sc_path, family_name])


# compress folder and return sha1
def compress_folder(source_folder_path, target_path):
    source_folder_name = path.basename(source_folder_path)

    zip_path = path.join(target_path, f"{family_name_trim}-{source_folder_name}.zip")
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=5) as zip_file:
        for root, dirs, files in walk(source_folder_path):
            for file in files:
                file_path = path.join(root, file)
                zip_file.write(file_path, path.relpath(file_path, source_folder_path))
    zip_file.close()
    sha1 = hashlib.sha1()
    with open(zip_path, "rb") as zip_file:
        while True:
            data = zip_file.read(1024)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


# write config to output path
with open(path.join(output_path, "build-config.json"), "w") as config_file:
    config_file.write(conf)

if release_mode:
    print("=== [Release Mode] ===")

    # archieve fonts
    mkdirs(path.join(output_path, "release"))

    hash_map = {}

    for f in listdir(output_path):
        if f == "release" or f.endswith(".json"):
            continue
        zip_path = path.join(output_path, "release")
        target_path = path.join(output_path, f)
        hash_map[f] = compress_folder(target_path, zip_path)
        # write config
        print("archieve:", f)

    # write sha1
    with open(path.join(output_path, "release", "sha1.json"), "w") as hash_file:
        hash_file.write(json.dumps(hash_map, indent=4))

    # copy woff
    woff2_path = path.join(path.dirname(output_path), "woff2")
    if path.exists(woff2_path):
        shutil.rmtree(woff2_path)
    shutil.copytree(path.join(output_path, "woff2"), woff2_path)
    print("copy woff to root")
