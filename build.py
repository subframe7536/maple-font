from enum import Enum, unique
import hashlib
import importlib.util
import json
import platform
import shutil
import subprocess
from os import listdir, makedirs, path, remove, walk
from urllib.request import urlopen
from zipfile import ZIP_DEFLATED, ZipFile
from fontTools.ttLib import TTFont
from fontTools.merge import Merger


@unique
class Status(Enum):
    DISABLE = "0"
    ENABLE = "1"
    IGNORE = "2"


# whether to archieve fonts
release_mode = True
# whether to build nerd font
build_nerd_font = True

build_config = {
    "family_name": "Maple Mono",
    "nerd_font": {
        # whether to make icon width fixed
        "mono": Status.DISABLE,
        # whether to generate Nerd Font patch based on hinted ttf
        "use_hinted": Status.ENABLE,
        # whether to use Nerd Font Patcher (auto enable when no fontforge bin is found)
        "use_font_patcher": Status.DISABLE,
    },
}

# =========================================================================================

# fontforge.exe path, use on Windows
WIN_FONTFORGE_PATH = "C:/Program Files (x86)/FontForgeBuilds/bin/fontforge.exe"
# fontforge path, use on MacOS
MAC_FONTFORGE_PATH = (
    "/Applications/FontForge.app/Contents/Resources/opt/local/bin/fontforge"
)
# fontforge path, use on Linux
LINUX_FONTFORGE_PATH = "/usr/local/bin/fontforge"

# =========================================================================================

package_name = "foundryToolsCLI"
package_installed = importlib.util.find_spec(package_name) is not None
family_name = build_config["family_name"]
family_name_compact = family_name.replace(" ", "")

if not package_installed:
    print(f"{package_name} is not found. Please run `pip install foundrytools-cli`")
    exit(1)


# run command
def run(cli: str | list[str], extra_args: list[str] = []) -> None:
    subprocess.run((cli.split(" ") if isinstance(cli, str) else cli) + extra_args)


def set_font_name(font: TTFont, name: str, id: int):
    font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)
    font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)


def del_font_name(font: TTFont, id: int):
    font["name"].removeNames(nameID=id)


# compress folder and return sha1
def compress_folder(source_file_or_dir_path: str, target_parent_dir_path: str) -> str:
    source_folder_name = path.basename(source_file_or_dir_path)

    zip_path = path.join(
        target_parent_dir_path, f"{family_name_compact}-{source_folder_name}.zip"
    )
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=5) as zip_file:
        for root, _, files in walk(source_file_or_dir_path):
            for file in files:
                file_path = path.join(root, file)
                zip_file.write(
                    file_path, path.relpath(file_path, source_file_or_dir_path)
                )
    zip_file.close()
    sha1 = hashlib.sha1()
    with open(zip_path, "rb") as zip_file:
        while True:
            data = zip_file.read(1024)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def check_font_patcher():
    if path.exists("FontPatcher"):
        return

    version = "3.1.1"
    url = f"https://github.com/ryanoasis/nerd-fonts/releases/download/v{version}/FontPatcher.zip"
    try:
        zip_path = "FontPatcher.zip"
        if not path.exists(zip_path):
            print(f"NerdFont Patcher does not exist, download from {url}")
            with urlopen(url) as response, open(zip_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("FontPatcher")
        remove(zip_path)
    except Exception as e:
        print(
            f"\nFail to get NerdFont Patcher. Please download it manually from {url}, then put downloaded 'FontPatcher.zip' into project's root and run this script again. \n\tError: {e}"
        )
        exit(1)


def get_build_nerd_font_fn():
    font_dir = (
        output_ttf_autohint
        if build_config["nerd_font"]["use_hinted"] == Status.ENABLE
        else output_ttf
    )

    system_name = platform.uname()[0]

    font_forge_bin = LINUX_FONTFORGE_PATH
    if "Darwin" in system_name:
        font_forge_bin = MAC_FONTFORGE_PATH
    elif "Windows" in system_name:
        font_forge_bin = WIN_FONTFORGE_PATH

    # full args: https://github.com/ryanoasis/nerd-fonts?tab=readme-ov-file#font-patcher
    nf_args = [
        font_forge_bin,
        "-script",
        "FontPatcher/font-patcher",
        "-l",
        "-c",
        "--careful",
        "--outputdir",
        output_nf,
    ]
    if build_config["nerd_font"]["mono"] == Status.ENABLE:
        nf_args += ["--mono"]

    nf_file_name = "NerdFont"
    if build_config["nerd_font"]["mono"] == Status.ENABLE:
        nf_file_name += "Mono"

    def build_using_prebuild_nerd_font(font_basename: str) -> TTFont:
        merger = Merger()
        font = merger.merge(
            [path.join(font_dir, font_basename), "src-font/NerdFontBase.ttf"]
        )
        return font

    def build_using_font_patcher(font_basename: str) -> TTFont:
        run(nf_args + [path.join(font_dir, font_basename)])
        _path = path.join(output_nf, font_basename.replace("-", f"{nf_file_name}-"))
        font = TTFont(_path)
        remove(_path)
        return font

    if (
        not path.exists(font_forge_bin)
        or build_config["nerd_font"]["use_font_patcher"] == Status.DISABLE
    ):
        build_fn = build_using_prebuild_nerd_font
        makedirs(output_nf, exist_ok=True)
        print("patch NerdFont using prebuild base font")
    else:
        build_fn = build_using_font_patcher
        check_font_patcher()
        print("patch NerdFont using font-patcher")
    return build_fn


output_dir = "fonts"
output_otf = path.join(output_dir, "otf")
output_ttf = path.join(output_dir, "ttf")
output_ttf_autohint = path.join(output_dir, "ttf-autohint")
output_variable = path.join(output_dir, "variable")
output_woff2 = path.join(output_dir, "woff2")
output_nf = path.join(output_dir, "nf")

shutil.rmtree(output_dir, ignore_errors=True)
shutil.rmtree("woff2", ignore_errors=True)
makedirs(output_dir)
makedirs(output_variable)

print("=== [build start] ===")

conf = json.dumps(
    build_config,
    default=lambda x: x.name if isinstance(x, Status) else None,
    indent=4,
)

print(conf)

input_files = [
    "src-font/MapleMono-Italic[wght]-VF.ttf",
    "src-font/MapleMono[wght]-VF.ttf",
]
for input_file in input_files:
    shutil.copy(input_file, output_variable)
    run(f"ftcli converter vf2i {input_file} -out {output_ttf}")
    if "Italic" in input_file:
        # when input file is italic, set italics
        # currently all the fonts in {output_ttf} is italic, so there is no need to filter here
        run(f"ftcli os2 set-flags --italic {output_ttf}")

# fix font name
for f in listdir(output_ttf):
    _path = path.join(output_ttf, f)
    font = TTFont(_path)

    style_name = f[10:-4]
    if style_name.endswith("Italic") and style_name[0] != "I":
        style_name = style_name[:-6] + " Italic"

    set_font_name(font, family_name, 1)
    set_font_name(font, style_name, 2)
    set_font_name(font, f"{family_name} {style_name}", 4)
    set_font_name(font, f"{family_name_compact}-{style_name}", 6)
    del_font_name(font, 16)
    del_font_name(font, 17)

    font.save(_path)
    font.close()

run(f"ftcli converter ttf2otf {output_ttf} -out {output_otf}")
run(f"ftcli converter ft2wf {output_ttf} -out {output_woff2} -f woff2")
run(f"ftcli ttf autohint {output_ttf} -out {output_ttf_autohint}")


if build_nerd_font:

    build_fn = get_build_nerd_font_fn()

    for f in listdir(output_ttf):

        print(f"generate NerdFont for {f}")
        nf_font = build_fn(f)

        # format font name

        style_name = f[10:-4]
        if style_name.endswith("Italic") and style_name[0] != "I":
            style_name = style_name[:-6] + " Italic"

        set_font_name(nf_font, f"{family_name} NF", 1)
        set_font_name(nf_font, style_name, 2)
        set_font_name(nf_font, f"{family_name} NF {style_name}", 4)
        set_font_name(nf_font, f"{family_name_compact}-NF-{f[10:-4]}", 6)
        del_font_name(nf_font, 16)
        del_font_name(nf_font, 17)

        nf_font.save(path.join(output_nf, f.replace("-", "-NF-")))
        nf_font.close()

# write config to output path
with open(path.join(output_dir, "build-config.json"), "w") as config_file:
    config_file.write(conf)

if release_mode:
    print("=== [Release Mode] ===")

    # archieve fonts
    release_dir = path.join(output_dir, "release")
    makedirs(release_dir)

    hash_map = {}

    for f in listdir(output_dir):
        if f == "release" or f.endswith(".json"):
            continue
        hash_map[f] = compress_folder(path.join(output_dir, f), release_dir)
        print(f"archieve: {f}")

    # write sha1
    with open(path.join(release_dir, "sha1.json"), "w") as hash_file:
        hash_file.write(json.dumps(hash_map, indent=4))

    shutil.rmtree("woff2", ignore_errors=True)
    shutil.copytree(output_woff2, "woff2")
    print("copy woff2 to root")
