from functools import partial
import hashlib
import importlib.util
import json
import platform
import shutil
import subprocess
from multiprocessing import Pool
from os import listdir, makedirs, path, remove, walk, getenv
from urllib.request import urlopen
from zipfile import ZIP_DEFLATED, ZipFile
from fontTools.ttLib import TTFont, newTable
from fontTools.merge import Merger


# whether to archieve fonts
release_mode = True
# whether to clean built fonts
clean_cache = True
# build process pool size
pool_size = 4 if not getenv("CODESPACE_NAME") else 2

build_config = {
    "family_name": "Maple Mono",
    # whether to use hinted ttf as base font
    "use_hinted": True,
    "nerd_font": {
        "enable": True,
        # target version of Nerd Font if font-patcher not exists
        "version": "3.2.1",
        # whether to make icon width fixed
        "mono": False,
        # prefer to use Font Patcher instead of using prebuild NerdFont base font
        # if you want to custom build nerd font using font-patcher, you need to set this to True
        "use_font_patcher": False,
        # extra args for font-patcher
        # default args: ["-l", "-c", "--careful", "--outputdir", output_nf]
        # if "mono" is set to True, "--mono" will be added
        # full args: https://github.com/ryanoasis/nerd-fonts?tab=readme-ov-file#font-patcher
        "extra_args": [],
    },
    "cn": {
        "enable": True,
        # whether to patch Nerd Font
        "with_nerd_font": True,
        # fix design language and supported languages
        "fix_meta_table": True,
        # whether to clean instantiated base CN fonts
        "clean_cache": False,
    },
}

package_name = "foundryToolsCLI"
package_installed = importlib.util.find_spec(package_name) is not None

if not package_installed:
    print(f"{package_name} is not found. Please run `pip install foundrytools-cli`")
    exit(1)

family_name = build_config["family_name"]
family_name_compact = family_name.replace(" ", "")

# paths
src_dir = "source"
output_dir = "fonts"
output_otf = path.join(output_dir, "OTF")
output_ttf = path.join(output_dir, "TTF")
output_ttf_autohint = path.join(output_dir, "TTF-AutoHint")
output_variable = path.join(output_dir, "Variable")
output_woff2 = path.join(output_dir, "Woff2")
output_nf = path.join(output_dir, "NF")
output_cn = path.join(output_dir, "CN")

ttf_dir_path = output_ttf_autohint if build_config["use_hinted"] else output_ttf

# =========================================================================================

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

# =========================================================================================

if build_config["cn"]["with_nerd_font"]:
    cn_base_font_dir = output_nf
    suffix = "NF CN"
else:
    cn_base_font_dir = ttf_dir_path
    suffix = "CN"

suffix_compact = suffix.replace(" ", "-")
cn_static_path = f"{src_dir}/cn/static"
output_nf_cn = path.join(output_dir, suffix_compact)


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


def check_font_patcher() -> bool:
    if path.exists("FontPatcher"):
        with open("FontPatcher/font-patcher", "r", encoding="utf-8") as f:
            if (
                f"# Nerd Fonts Version: {build_config['nerd_font']['version']}"
                in f.read()
            ):
                return True
            else:
                print("FontPatcher version not match, delete it")
                shutil.rmtree("FontPatcher", ignore_errors=True)

    url = f"https://github.com/ryanoasis/nerd-fonts/releases/download/v{build_config['nerd_font']['version']}/FontPatcher.zip"
    try:
        zip_path = "FontPatcher.zip"
        if not path.exists(zip_path):
            print(f"NerdFont Patcher does not exist, download from {url}")
            with urlopen(url) as response, open(zip_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("FontPatcher")
        remove(zip_path)
        return True
    except Exception as e:
        print(
            f"\nFail to fetch NerdFont Patcher. Please download it manually from {url}, then put downloaded 'FontPatcher.zip' into project's root and run this script again. \n\tError: {e}"
        )
        print("use prebuilt Nerd Font instead")
        return False


def get_nerd_font_patcher_args():
    # full args: https://github.com/ryanoasis/nerd-fonts?tab=readme-ov-file#font-patcher
    _nf_args = [
        font_forge_bin,
        "FontPatcher/font-patcher",
        "-l",
        "-c",
        "--careful",
        "--outputdir",
        output_nf,
    ]
    if build_config["nerd_font"]["mono"]:
        _nf_args += ["--mono"]

    _nf_args += build_config["nerd_font"]["extra_args"]

    return _nf_args


def build_mono(f: str):
    _path = path.join(output_ttf, f)
    font = TTFont(_path)

    style_name_compact_nf = f[10:-4]

    style_name_nf = style_name_compact_nf
    if style_name_nf.endswith("Italic") and style_name_nf[0] != "I":
        style_name_nf = style_name_nf[:-6] + " Italic"

    set_font_name(font, family_name, 1)
    set_font_name(font, style_name_nf, 2)
    set_font_name(font, f"{family_name} {style_name_nf}", 4)
    set_font_name(font, f"{family_name_compact}-{style_name_compact_nf}", 6)
    del_font_name(font, 16)
    del_font_name(font, 17)

    font.save(_path)
    font.close()
    run(f"ftcli converter ttf2otf {_path} -out {output_otf}")
    run(f"ftcli converter ft2wf {_path} -out {output_woff2} -f woff2")
    run(f"ftcli ttf autohint {_path} -out {output_ttf_autohint}")


def build_nf(f: str, use_font_patcher: bool):
    print(f"generate NerdFont for {f}")

    nf_args = get_nerd_font_patcher_args()

    nf_file_name = "NerdFont"
    if build_config["nerd_font"]["mono"]:
        nf_file_name += "Mono"

    def build_using_prebuild_nerd_font(font_basename: str) -> TTFont:
        merger = Merger()
        font = merger.merge(
            [
                path.join(ttf_dir_path, font_basename),
                f"{src_dir}/NerdFontBase{'Mono' if build_config['nerd_font']['mono'] else ''}.ttf",
            ]
        )
        return font

    def build_using_font_patcher(font_basename: str) -> TTFont:
        run(nf_args + [path.join(ttf_dir_path, font_basename)])
        _path = path.join(output_nf, font_basename.replace("-", f"{nf_file_name}-"))
        font = TTFont(_path)
        remove(_path)
        return font

    makedirs(output_nf, exist_ok=True)

    nf_font = (
        build_using_font_patcher(f)
        if use_font_patcher
        else build_using_prebuild_nerd_font(f)
    )

    # format font name
    style_name_compact_nf = f[10:-4]

    style_name_nf = style_name_compact_nf
    if style_name_nf.endswith("Italic") and style_name_nf[0] != "I":
        style_name_nf = style_name_nf[:-6] + " Italic"

    set_font_name(nf_font, f"{family_name} NF", 1)
    set_font_name(nf_font, style_name_nf, 2)
    set_font_name(nf_font, f"{family_name} NF {style_name_nf}", 4)
    set_font_name(nf_font, f"{family_name_compact}-NF-{style_name_compact_nf}", 6)
    del_font_name(nf_font, 16)
    del_font_name(nf_font, 17)

    nf_font.save(
        path.join(output_nf, f"{family_name_compact}-NF-{style_name_compact_nf}.ttf")
    )
    nf_font.close()


def build_cn(f: str):
    style_name_compact_cn = f.split("-")[-1].split(".")[0]

    print(f"generate CN font for {f}")

    merger = Merger()
    font = merger.merge(
        [
            path.join(cn_base_font_dir, f),
            path.join(cn_static_path, f"MapleMonoCN-{style_name_compact_cn}.ttf"),
        ]
    )

    style_name_cn = style_name_compact_cn
    if style_name_cn.endswith("Italic") and style_name_cn[0] != "I":
        style_name_cn = style_name_cn[:-6] + " Italic"

    set_font_name(font, f"{family_name} {suffix}", 1)
    set_font_name(font, style_name_cn, 2)
    set_font_name(font, f"{family_name} {suffix} {style_name_cn}", 4)
    set_font_name(
        font, f"{family_name_compact}-{suffix_compact}-{style_name_compact_cn}", 6
    )

    font["OS/2"].xAvgCharWidth = 600

    if build_config["cn"]["fix_meta_table"]:
        # add code page, Latin / Japanese / Simplify Chinese / Traditional Chinese
        font["OS/2"].ulCodePageRange1 = 1 << 0 | 1 << 17 | 1 << 18 | 1 << 20

        # fix meta table, https://learn.microsoft.com/en-us/typography/opentype/spec/meta
        meta = newTable("meta")
        meta.data = {
            "dlng": "Latn, Hans, Hant, Jpan",
            "slng": "Latn, Hans, Hant, Jpan",
        }
        font["meta"] = meta

    _path = path.join(
        output_nf_cn,
        f"{family_name_compact}-{suffix_compact}-{style_name_compact_cn}.ttf",
    )

    font.save(_path)
    font.close()


def main():
    if clean_cache:
        shutil.rmtree(output_dir, ignore_errors=True)
        shutil.rmtree(output_woff2, ignore_errors=True)
        makedirs(output_dir)
        makedirs(output_variable)

    print("=== [build start] ===")

    conf = json.dumps(
        build_config,
        indent=4,
    )

    print(conf)

    # =========================================================================================
    # ===================================   build basic   =====================================
    # =========================================================================================

    if (clean_cache and path.exists(output_ttf)) or not path.exists(output_ttf):
        input_files = [
            f"{src_dir}/MapleMono-Italic[wght]-VF.ttf",
            f"{src_dir}/MapleMono[wght]-VF.ttf",
        ]
        for input_file in input_files:
            shutil.copy(input_file, output_variable)
            run(f"ftcli converter vf2i {input_file} -out {output_ttf}")
            if "Italic" in input_file:
                # when input file is italic, set italics
                # at that time, all the fonts in {output_ttf} is italic, so there is no need to filter here
                run(f"ftcli os2 set-flags --italic {output_ttf}")

        with Pool(pool_size) as p:
            p.map(build_mono, listdir(output_ttf))

    # =========================================================================================
    # ====================================   build NF   =======================================
    # =========================================================================================

    if (
        (clean_cache and path.exists(output_nf)) or not path.exists(output_nf)
    ) and build_config["nerd_font"]["enable"]:

        use_font_patcher = (
            len(build_config["nerd_font"]["extra_args"]) > 0
            or build_config["nerd_font"]["use_font_patcher"]
        ) and check_font_patcher()

        if use_font_patcher and not path.exists(font_forge_bin):
            print(
                f"FontForge bin({font_forge_bin}) not found. Use prebuild Nerd Font instead."
            )
            use_font_patcher = False

        with Pool(pool_size) as p:
            _build_fn = partial(build_nf, use_font_patcher=use_font_patcher)
            print(
                f"patch Nerd Font using {'FontPatcher' if use_font_patcher else 'prebuild Nerd Font'}"
            )
            p.map(_build_fn, listdir(output_ttf))

    # =========================================================================================
    # ====================================   build CN   =======================================
    # =========================================================================================

    if (
        ((clean_cache and path.exists(output_cn)) or not path.exists(output_nf_cn))
        and build_config["cn"]["enable"]
        and path.exists(f"{src_dir}/cn")
    ):

        if not path.exists(cn_static_path) or build_config["cn"]["clean_cache"]:
            print("====================================")
            print("instantiating CN font, be patient...")
            print("====================================")
            run(f"ftcli converter vf2i {src_dir}/cn -out {cn_static_path}")

        makedirs(output_nf_cn, exist_ok=True)

        with Pool(pool_size) as p:
            p.map(build_cn, listdir(cn_base_font_dir))

    # =========================================================================================
    # ====================================   release   ========================================
    # =========================================================================================

    # write config to output path
    with open(path.join(output_dir, "build-config.json"), "w") as config_file:
        config_file.write(conf)

    if release_mode:
        print("=== [Release Mode] ===")

        # archieve fonts
        release_dir = path.join(output_dir, "release")
        makedirs(release_dir, exist_ok=True)

        hash_map = {}

        # archieve fonts
        for f in listdir(output_dir):
            if f == "release" or f.endswith(".json"):
                continue
            hash_map[f] = compress_folder(path.join(output_dir, f), release_dir)
            print(f"archieve: {f}")

        # write sha1
        with open(path.join(release_dir, "sha1.json"), "w") as hash_file:
            hash_file.write(json.dumps(hash_map, indent=4))

        # copy woff2 to root
        shutil.rmtree("woff2", ignore_errors=True)
        shutil.copytree(output_woff2, "woff2")
        print("copy woff2 to root")


if __name__ == "__main__":
    main()
