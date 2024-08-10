import hashlib
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
import time
from functools import partial
from multiprocessing import Pool
from os import listdir, makedirs, path, remove, walk, getenv
from urllib.request import urlopen
from zipfile import ZIP_DEFLATED, ZipFile
from fontTools.ttLib import TTFont, newTable
from fontTools.merge import Merger
from fontTools.ttLib.tables import otTables

# =========================================================================================

package_name = "foundryToolsCLI"
package_installed = importlib.util.find_spec(package_name) is not None

if not package_installed:
    print(f"{package_name} is not found. Please run `pip install foundrytools-cli`")
    exit(1)

# =========================================================================================

# whether to archieve fonts
release_mode = "--release" in sys.argv

# =========================================================================================

WIN_FONTFORGE_PATH = "C:/Program Files (x86)/FontForgeBuilds/bin/fontforge.exe"
MAC_FONTFORGE_PATH = (
    "/Applications/FontForge.app/Contents/Resources/opt/local/bin/fontforge"
)
LINUX_FONTFORGE_PATH = "/usr/bin/fontforge"

system_name = platform.uname()[0]

font_forge_bin_default = LINUX_FONTFORGE_PATH
if "Darwin" in system_name:
    font_forge_bin_default = MAC_FONTFORGE_PATH
elif "Windows" in system_name:
    font_forge_bin_default = WIN_FONTFORGE_PATH

# =========================================================================================

build_config = {
    # the number of parallel tasks
    # when run in codespace, this will be 1
    "pool_size": 4,
    # font family name
    "family_name": "Maple Mono",
    # whether to use hinted ttf as base font
    "use_hinted": True,
    "feature_freeze": {
        "cv01": "ignore",
        "cv02": "ignore",
        "cv03": "ignore",
        "cv04": "ignore",
        "cv98": "ignore",
        "cv99": "ignore",
        "ss01": "ignore",
        "ss02": "ignore",
        "ss03": "ignore",
        "ss04": "ignore",
        "zero": "ignore",
    },
    # nerd font settings
    "nerd_font": {
        # whether to enable Nerd Font
        "enable": True,
        # target version of Nerd Font if font-patcher not exists
        "version": "3.2.1",
        # whether to make icon width fixed
        "mono": False,
        # prefer to use Font Patcher instead of using prebuild NerdFont base font
        # if you want to custom build nerd font using font-patcher, you need to set this to True
        "use_font_patcher": False,
        # symbol Fonts settings.
        # default args: ["--complete"]
        # if not, will use font-patcher to generate fonts
        # full args: https://github.com/ryanoasis/nerd-fonts?tab=readme-ov-file#font-patcher
        "glyphs": ["--complete"],
        # extra args for font-patcher
        # default args: ["-l", "--careful", "--outputdir", output_nf]
        # if "mono" is set to True, "--mono" will be added
        # full args: https://github.com/ryanoasis/nerd-fonts?tab=readme-ov-file#font-patcher
        "extra_args": [],
    },
    # chinese font settings
    "cn": {
        # whether to build Chinese fonts
        # skip if Chinese base fonts are not founded
        "enable": True,
        # whether to patch Nerd Font
        "with_nerd_font": True,
        # fix design language and supported languages
        "fix_meta_table": True,
        # whether to clean instantiated base CN fonts
        "clean_cache": False,
    },
}

try:
    with open("config.json", "r") as f:
        data = json.load(f)
        if "$schema" in data:
            del data["$schema"]
        build_config.update(data)
        if "font_forge_bin" not in build_config["nerd_font"]:
            build_config["nerd_font"]["font_forge_bin"] = font_forge_bin_default
except:
    print("config.json is not found. Use default config.")


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

if build_config["cn"]["with_nerd_font"]:
    cn_base_font_dir = output_nf
    suffix = "NF CN"
else:
    cn_base_font_dir = ttf_dir_path
    suffix = "CN"

suffix_compact = suffix.replace(" ", "-")
cn_static_path = f"{src_dir}/cn/static"
output_nf_cn = path.join(output_dir, suffix_compact)

# In these subfamilies:
#   - NameID1 should be the family name
#   - NameID2 should be the subfamily name
#   - NameID16 and NameID17 should be removed
# Other subfamilies:
#   - NameID1 should be the family name, append with subfamily name without "Italic"
#   - NameID2 should be the "Regular" or "Italic"
#   - NameID16 should be the family name
#   - NameID17 should be the subfamily name
# https://github.com/subframe7536/maple-font/issues/182
# https://github.com/subframe7536/maple-font/issues/183
#
# same as `ftcli assistant commit . --ls 400 700`
# https://github.com/ftCLI/FoundryTools-CLI/issues/166#issuecomment-2095756721
skip_subfamily_list = ["Regular", "Bold", "Italic", "BoldItalic"]


def pool_size():
    return build_config["pool_size"] if not getenv("CODESPACE_NAME") else 1


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
        zip_file.write("OFL.txt", "LICENSE.txt")
        if not source_file_or_dir_path.endswith("Variable"):
            zip_file.write(path.join(output_dir, "build-config.json"), "config.json")

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

    zip_path = "FontPatcher.zip"
    if not path.exists(zip_path):
        url = f"https://github.com/ryanoasis/nerd-fonts/releases/download/v{build_config['nerd_font']['version']}/FontPatcher.zip"
        try:
            print(f"NerdFont Patcher does not exist, download from {url}")
            with urlopen(url) as response, open(zip_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
        except Exception as e:
            print(
                f"\nFail to fetch NerdFont Patcher. Please download it manually from {url}, then put downloaded 'FontPatcher.zip' into project's root and run this script again. \n\tError: {e}"
            )
            print("use prebuilt Nerd Font instead")
            return False

    with ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall("FontPatcher")
    remove(zip_path)
    return True


def get_nerd_font_patcher_args():
    # full args: https://github.com/ryanoasis/nerd-fonts?tab=readme-ov-file#font-patcher
    _nf_args = [
        build_config["nerd_font"]["font_forge_bin"],
        "FontPatcher/font-patcher",
        "-l",
        "--careful",
        "--outputdir",
        output_nf,
    ] + build_config["nerd_font"]["glyphs"]

    if build_config["nerd_font"]["mono"]:
        _nf_args += ["--mono"]

    _nf_args += build_config["nerd_font"]["extra_args"]

    return _nf_args


def get_font_name(style_name_compact: str):
    is_italic = style_name_compact.endswith("Italic")

    _style_name = style_name_compact
    if is_italic and style_name_compact[0] != "I":
        _style_name = style_name_compact[:-6] + " Italic"

    if style_name_compact in skip_subfamily_list:
        return "", _style_name, _style_name
    else:
        return (
            " " + style_name_compact.replace("Italic", ""),
            "Italic" if is_italic else "Regular",
            _style_name,
        )


def add_cv98(font):
    gsub_table = font["GSUB"].table
    script_list = gsub_table.ScriptList
    feature_list = gsub_table.FeatureList
    lookup_list = gsub_table.LookupList

    # Because fonttools will auto genreate `locl` rule when merging fonts, so just reuse it
    #
    # lookup = otTables.Lookup()
    # lookup.LookupType = 1
    # lookup.LookupFlag = 0
    # subtable = otTables.SingleSubst()
    # subtable.mapping = {"emdash": "emdash.cv98", "ellipsis": "ellipsis.cv98"}
    # lookup.SubTable = [subtable]
    # lookup_list.Lookup.append(lookup)
    # lookup_index = lookup_list.LookupCount

    feature_record = otTables.FeatureRecord()
    feature_record.FeatureTag = "cv98"
    feature_record.Feature = otTables.Feature()
    feature_record.Feature.LookupListIndex = [lookup_list.LookupCount - 1]
    feature_index = len(feature_list.FeatureRecord)
    feature_list.FeatureRecord.append(feature_record)

    for script_record in script_list.ScriptRecord:
        lang_sys = script_record.Script.DefaultLangSys

        if lang_sys:
            lang_sys.FeatureIndex.append(feature_index)
        else:
            for lang_sys_rec in script_record.Script.LangSysRecord:
                lang_sys_rec.LangSys.FeatureIndex.append(feature_index)


def freeze_feature(font: TTFont):
    # check feature list
    feature_record = font["GSUB"].table.FeatureList.FeatureRecord
    feature_dict = {
        feature.FeatureTag: feature.Feature
        for feature in feature_record
        if feature.FeatureTag != "calt"
    }

    calt_features = [
        feature.Feature for feature in feature_record if feature.FeatureTag == "calt"
    ]

    # Process features
    for tag, status in build_config["feature_freeze"].items():
        target_feature = feature_dict.get(tag)
        if not target_feature or status == "ignore":
            continue

        if status == "disable":
            target_feature.LookupListIndex = []
            continue

        if tag in ["ss03"]:
            # Enable by moving rules into "calt"
            for calt_feat in calt_features:
                calt_feat.LookupListIndex.extend(target_feature.LookupListIndex)
        else:
            # Enable by replacing data in glyf and hmtx tables
            glyph_dict = font["glyf"].glyphs
            hmtx_dict = font["hmtx"].metrics
            for index in target_feature.LookupListIndex:
                lookup = font["GSUB"].table.LookupList.Lookup[index]
                for old_key, new_key in lookup.SubTable[0].mapping.items():
                    if (
                        old_key in glyph_dict
                        and old_key in hmtx_dict
                        and new_key in glyph_dict
                        and new_key in hmtx_dict
                    ):
                        glyph_dict[old_key] = glyph_dict[new_key]
                        hmtx_dict[old_key] = hmtx_dict[new_key]
                    else:
                        print(f"{old_key} or {new_key} does not exist")
                        return


def build_mono(f: str):
    _path = path.join(output_ttf, f)
    font = TTFont(_path)

    style_name_compact = f[10:-4]

    style_name1, style_name2, style_name = get_font_name(style_name_compact)

    set_font_name(
        font,
        family_name + style_name1,
        1,
    )
    set_font_name(font, style_name2, 2)
    set_font_name(
        font,
        f"{family_name} {style_name}",
        4,
    )
    set_font_name(font, f"{family_name_compact}-{style_name_compact}", 6)

    if style_name_compact not in skip_subfamily_list:
        set_font_name(font, family_name, 16)
        set_font_name(font, style_name, 17)

    # https://github.com/ftCLI/FoundryTools-CLI/issues/166#issuecomment-2095433585
    if style_name1 == " Thin":
        font["OS/2"].usWeightClass = 250
    elif style_name1 == " ExtraLight":
        font["OS/2"].usWeightClass = 275

    freeze_feature(font)

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
        return merger.merge(
            [
                path.join(ttf_dir_path, font_basename),
                f"{src_dir}/MapleMono-NF-Base{'-Mono' if build_config['nerd_font']['mono'] else ''}.ttf",
            ]
        )

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

    style_name_nf1, style_name_nf2, style_name_nf = get_font_name(style_name_compact_nf)

    set_font_name(
        nf_font,
        f"{family_name} NF{style_name_nf1}",
        1,
    )
    set_font_name(nf_font, style_name_nf2, 2)
    set_font_name(
        nf_font,
        f"{family_name} NF {style_name_nf}",
        4,
    )
    set_font_name(nf_font, f"{family_name_compact}-NF-{style_name_compact_nf}", 6)

    if style_name_compact_nf not in skip_subfamily_list:
        set_font_name(nf_font, f"{family_name} NF", 16)
        set_font_name(nf_font, style_name_nf, 17)

    _path = path.join(
        output_nf, f"{family_name_compact}-NF-{style_name_compact_nf}.ttf"
    )
    nf_font.save(_path)
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

    style_name_cn1, style_name_cn2, style_name_cn = get_font_name(style_name_compact_cn)

    set_font_name(
        font,
        f"{family_name} {suffix}{style_name_cn1}",
        1,
    )
    set_font_name(font, style_name_cn2, 2)
    set_font_name(
        font,
        f"{family_name} {suffix} {style_name_cn}",
        4,
    )
    set_font_name(
        font, f"{family_name_compact}-{suffix_compact}-{style_name_compact_cn}", 6
    )

    if style_name_compact_cn not in skip_subfamily_list:
        set_font_name(font, f"{family_name} {suffix}", 16)
        set_font_name(font, style_name_cn, 17)

    font["OS/2"].xAvgCharWidth = 600

    # https://github.com/subframe7536/maple-font/issues/188
    add_cv98(font)

    freeze_feature(font)

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
    print("=== [Clean Cache] ===")
    shutil.rmtree(output_dir, ignore_errors=True)
    shutil.rmtree(output_woff2, ignore_errors=True)
    makedirs(output_dir, exist_ok=True)
    makedirs(output_variable, exist_ok=True)

    start_time = time.time()
    print("=== [Build Start] ===")
    # =========================================================================================
    # ===================================   build basic   =====================================
    # =========================================================================================

    input_files = [
        f"{src_dir}/MapleMono-Italic[wght]-VF.ttf",
        f"{src_dir}/MapleMono[wght]-VF.ttf",
    ]
    for input_file in input_files:
        font = TTFont(input_file)
        font.save(input_file.replace(src_dir, output_variable))

    run(f"ftcli converter vf2i {output_variable} -out {output_ttf}")
    run(f"ftcli fix italic-angle {output_ttf}")
    run(f"ftcli fix monospace {output_ttf}")
    run(f"ftcli fix strip-names {output_ttf}")
    run(f"ftcli ttf dehint {output_ttf}")
    run(f"ftcli ttf fix-contours {output_ttf}")
    run(f"ftcli ttf remove-overlaps {output_ttf}")

    with Pool(pool_size()) as p:
        p.map(build_mono, listdir(output_ttf))

    # =========================================================================================
    # ====================================   build NF   =======================================
    # =========================================================================================

    if build_config["nerd_font"]["enable"]:

        use_font_patcher = (
            len(build_config["nerd_font"]["extra_args"]) > 0
            or build_config["nerd_font"]["use_font_patcher"]
            or build_config["nerd_font"]["glyphs"] != ["--complete"]
        ) and check_font_patcher()

        if use_font_patcher and not path.exists(
            build_config["nerd_font"]["font_forge_bin"]
        ):
            print(
                f"FontForge bin({build_config['nerd_font']['font_forge_bin']}) not found. Use prebuild Nerd Font instead."
            )
            use_font_patcher = False

        with Pool(pool_size()) as p:
            _build_fn = partial(build_nf, use_font_patcher=use_font_patcher)
            _version = build_config["nerd_font"]["version"]
            _name = (
                f"FontPatcher v{_version}" if use_font_patcher else "prebuild Nerd Font"
            )
            print("========================================")
            print(f"patch Nerd Font using {_name}")
            print("========================================")
            p.map(_build_fn, listdir(output_ttf))

    # =========================================================================================
    # ====================================   build CN   =======================================
    # =========================================================================================

    if build_config["cn"]["enable"] and path.exists(f"{src_dir}/cn"):

        if not path.exists(cn_static_path) or build_config["cn"]["clean_cache"]:
            print("====================================")
            print("instantiating CN font, be patient...")
            print("====================================")
            run(f"ftcli converter vf2i {src_dir}/cn -out {cn_static_path}")
            run(f"ftcli ttf fix-contours {cn_static_path}")
            run(f"ftcli ttf remove-overlaps {cn_static_path}")

        makedirs(output_nf_cn, exist_ok=True)

        with Pool(pool_size()) as p:
            p.map(build_cn, listdir(cn_base_font_dir))

    run(f"ftcli name del-mac-names -r {output_dir}")

    # =========================================================================================
    # ====================================   release   ========================================
    # =========================================================================================

    # write config to output path
    with open(
        path.join(output_dir, "build-config.json"), "w", encoding="utf-8"
    ) as config_file:
        del build_config["pool_size"]
        del build_config["nerd_font"]["font_forge_bin"]
        config_file.write(
            json.dumps(
                build_config,
                indent=4,
            )
        )

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
        with open(
            path.join(release_dir, "sha1.json"), "w", encoding="utf-8"
        ) as hash_file:
            hash_file.write(json.dumps(hash_map, indent=4))

        # copy woff2 to root
        shutil.rmtree("woff2", ignore_errors=True)
        shutil.copytree(output_woff2, "woff2")
        print("copy woff2 to root")

    print(f"=== [Build Success ({time.time() - start_time:.2f} s)] ===")


if __name__ == "__main__":
    main()
