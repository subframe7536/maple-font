#!/usr/bin/env python3
import argparse
import importlib.util
import json
import re
import shutil
import time
from functools import partial
from multiprocessing import Pool
from os import environ, getcwd, listdir, makedirs, path, remove, getenv
from typing import Callable
from fontTools.ttLib import TTFont, newTable
from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.merge import Merger
from source.py.utils import (
    check_font_patcher,
    verify_glyph_width,
    compress_folder,
    download_cn_base_font,
    get_font_forge_bin,
    get_font_name,
    is_ci,
    match_unicode_names,
    run,
    set_font_name,
    joinPaths,
)
from source.py.feature import freeze_feature, get_freeze_config_str

FONT_VERSION = "v7.0-beta36"
# =========================================================================================


def check_ftcli():
    package_name = "foundryToolsCLI"
    package_installed = importlib.util.find_spec(package_name) is not None

    if not package_installed:
        print(
            f"❗{package_name} is not found. Please run `pip install foundrytools-cli`"
        )
        exit(1)


# =========================================================================================


def parse_args():
    parser = argparse.ArgumentParser(
        description="✨ Builder and optimizer for Maple Mono",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"Maple Mono Builder v{FONT_VERSION}",
    )
    parser.add_argument(
        "-d",
        "--dry",
        dest="dry",
        action="store_true",
        help="Output config and exit",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Add `Debug` suffix to family name, skip optimization",
    )

    feature_group = parser.add_argument_group("Feature Options")
    feature_group.add_argument(
        "-n",
        "--normal",
        dest="normal",
        action="store_true",
        help="Use normal preset, just like `JetBrains Mono` with slashed zero",
    )
    feature_group.add_argument(
        "--feat",
        type=lambda x: x.strip().split(","),
        help="Freeze font features, splited by `,` (e.g. `--feat zero,cv01,ss07,ss08`). No effect on variable format",
    )
    feature_group.add_argument(
        "--apply-fea-file",
        default=None,
        action="store_true",
        help="Load feature file from `source/features/{regular,italic}.fea` to variable font",
    )
    hint_group = feature_group.add_mutually_exclusive_group()
    hint_group.add_argument(
        "--hinted",
        dest="hinted",
        default=None,
        action="store_true",
        help="Use hinted font as base font in NF / CN / NF-CN (default)",
    )
    hint_group.add_argument(
        "--no-hinted",
        dest="hinted",
        default=None,
        action="store_false",
        help="Use unhinted font as base font in NF / CN / NF-CN",
    )
    liga_group = feature_group.add_mutually_exclusive_group()
    liga_group.add_argument(
        "--liga",
        dest="liga",
        default=None,
        action="store_true",
        help="Preserve all the ligatures (default)",
    )
    liga_group.add_argument(
        "--no-liga",
        dest="liga",
        default=None,
        action="store_false",
        help="Remove all the ligatures",
    )
    feature_group.add_argument(
        "--cn-narrow",
        action="store_true",
        help="Make CN characters narrow (experimental)",
    )

    build_group = parser.add_argument_group("Build Options")
    nf_group = build_group.add_mutually_exclusive_group()
    nf_group.add_argument(
        "--nerd-font",
        dest="nerd_font",
        default=None,
        action="store_true",
        help="Build Nerd-Font version (default)",
    )
    nf_group.add_argument(
        "--no-nerd-font",
        dest="nerd_font",
        default=None,
        action="store_false",
        help="Do not build Nerd-Font version",
    )
    cn_group = build_group.add_mutually_exclusive_group()
    cn_group.add_argument(
        "--cn",
        dest="cn",
        default=None,
        action="store_true",
        help="Build Chinese version",
    )
    cn_group.add_argument(
        "--no-cn",
        dest="cn",
        default=None,
        action="store_false",
        help="Do not build Chinese version (default)",
    )
    build_group.add_argument(
        "--cn-both",
        action="store_true",
        help="Build both `Maple Mono CN` and `Maple Mono NF CN`. Nerd-Font version must be enabled",
    )
    build_group.add_argument(
        "--ttf-only",
        action="store_true",
        help="Only build TTF format",
    )
    build_group.add_argument(
        "--cache",
        action="store_true",
        help="Reuse font cache of TTF, OTF and Woff2 formats",
    )
    build_group.add_argument(
        "--cn-rebuild",
        action="store_true",
        help="Reinstantiate CN base font",
    )
    build_group.add_argument(
        "--archive",
        action="store_true",
        help="Build font archives with config and license. If has `--cache` flag, only archive Nerd-Font and CN formats",
    )
    build_group.add_argument(
        "--forgive",
        action="store_true",
        help="Forgive errors",
    )

    return parser.parse_args()


# =========================================================================================


class FontConfig:
    def __init__(self, args):
        self.archive = None
        self.use_cn_both = None
        self.ttf_only = None
        self.debug = None
        self.apply_fea_file = None
        # the number of parallel tasks
        # when run in codespace, this will be 1
        self.pool_size = 1 if not getenv("CODESPACE_NAME") else 4
        # font family name
        self.family_name = "Maple Mono"
        self.family_name_compact = "MapleMono"
        # whether to use hinted ttf as base font
        self.use_hinted = True
        # whether to enable ligature
        self.enable_liga = True
        self.feature_freeze = {
            "cv01": "ignore",
            "cv02": "ignore",
            "cv03": "ignore",
            "cv04": "ignore",
            "cv31": "ignore",
            "cv32": "ignore",
            "cv33": "ignore",
            "cv34": "ignore",
            "cv35": "ignore",
            "cv36": "ignore",
            "cv96": "ignore",
            "cv97": "ignore",
            "cv98": "ignore",
            "cv99": "ignore",
            "ss01": "ignore",
            "ss02": "ignore",
            "ss03": "ignore",
            "ss04": "ignore",
            "ss05": "ignore",
            "ss06": "ignore",
            "ss07": "ignore",
            "ss08": "ignore",
            "zero": "ignore",
        }
        # Nerd-Font settings
        self.nerd_font = {
            # whether to enable Nerd-Font
            "enable": True,
            # target version of Nerd-Font if font-patcher not exists
            "version": "3.2.1",
            # whether to make icon width fixed
            "mono": False,
            # prefer to use Font Patcher instead of using prebuild NerdFont base font
            # if you want to custom build Nerd-Font using font-patcher, you need to set this to True
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
        }
        # chinese font settings
        self.cn = {
            # whether to build Chinese fonts
            # skip if Chinese base fonts are not founded
            "enable": False,
            # whether to patch Nerd-Font
            "with_nerd_font": True,
            # fix design language and supported languages
            "fix_meta_table": True,
            # whether to clean instantiated base CN fonts
            "clean_cache": False,
            # whether to narrow CN glyphs
            "narrow": False,
            # whether to hint CN font (will increase about 33% size)
            "use_hinted": False,
            # whether to use pre-instantiated static CN font as base font
            "use_static_base_font": True,
        }
        self.glyph_width = 600
        self.glyph_width_cn_narrow = 1000
        self.forgive = False
        self.__load_config(args.normal)
        self.__load_args(args)

        ver = FONT_VERSION
        self.beta = None
        if "-" in FONT_VERSION:
            ver, beta = FONT_VERSION.split("-")
            self.beta = beta

        major, minor = ver.split(".")

        if major.startswith("v"):
            major = major[1:]

        self.version_str = f"Version {major}.{minor:03}"

    def __load_config(self, use_normal):
        try:
            config_file_path = (
                "./source/preset-normal.json" if use_normal else "config.json"
            )
            with open(config_file_path, "r") as f:
                data = json.load(f)
                for prop in [
                    "family_name",
                    "use_hinted",
                    "enable_liga",
                    "pool_size",
                    "github_mirror",
                    "feature_freeze",
                    "nerd_font",
                    "cn",
                ]:
                    if prop in data:
                        val = data[prop]
                        setattr(
                            self,
                            prop,
                            val
                            if type(val) is not dict
                            else {**getattr(self, prop), **val},
                        )

        except ():
            print("Fail to load config.json. Please check your config.json.")
            exit(1)

    def __load_args(self, args):
        self.archive = args.archive
        self.use_cn_both = args.cn_both
        self.debug = args.debug

        if "font_forge_bin" not in self.nerd_font:
            self.nerd_font["font_forge_bin"] = get_font_forge_bin()

        if args.feat is not None:
            for f in args.feat:
                if f in self.feature_freeze:
                    self.feature_freeze[f] = "enable"

        if args.hinted is not None:
            self.use_hinted = args.hinted

        if args.liga is not None:
            self.enable_liga = args.liga

        if args.nerd_font is not None:
            self.nerd_font["enable"] = args.nerd_font

        if args.cn is not None:
            self.cn["enable"] = args.cn

        if args.cn_narrow:
            self.cn["narrow"] = True

        if args.ttf_only:
            self.ttf_only = True

        if args.apply_fea_file:
            self.apply_fea_file = True

        if args.forgive:
            self.forgive = True

        if args.cn_rebuild:
            self.cn["clean_cache"] = True
            self.cn["use_static_base_font"] = False

        name_arr = [word.capitalize() for word in self.family_name.split(" ")]
        if not self.enable_liga:
            name_arr.append("NL")
        if self.debug:
            name_arr.append("Debug")
        self.family_name = " ".join(name_arr)
        self.family_name_compact = "".join(name_arr)

        self.freeze_config_str = get_freeze_config_str(
            self.feature_freeze, self.enable_liga
        )

    def should_build_nf_cn(self) -> bool:
        return self.cn["with_nerd_font"] and self.nerd_font["enable"]

    def toggle_nf_cn_config(self) -> bool:
        if not self.nerd_font["enable"]:
            print("❗Nerd-Font version is disabled, skip toggle.")
            return False
        self.cn["with_nerd_font"] = not self.cn["with_nerd_font"]
        return True

    def get_valid_glyph_width_list(self, cn=False):
        if cn:
            return [
                0,
                self.glyph_width,
                self.glyph_width_cn_narrow
                if self.cn["narrow"]
                else 2 * self.glyph_width,
            ]
        else:
            return [0, self.glyph_width]


class BuildOption:
    def __init__(self, config: FontConfig):
        # paths
        self.src_dir = "source"
        self.output_dir = "fonts"
        self.output_otf = joinPaths(self.output_dir, "OTF")
        self.output_ttf = joinPaths(self.output_dir, "TTF")
        self.output_ttf_hinted = joinPaths(self.output_dir, "TTF-AutoHint")
        self.output_variable = joinPaths(self.output_dir, "Variable")
        self.output_woff2 = joinPaths(self.output_dir, "Woff2")
        self.output_nf = joinPaths(self.output_dir, "NF")
        self.ttf_base_dir = joinPaths(
            self.output_dir, "TTF-AutoHint" if config.use_hinted else "TTF"
        )

        self.cn_variable_dir = f"{self.src_dir}/cn"
        self.cn_static_dir = f"{self.cn_variable_dir}/static"

        self.cn_base_font_dir = None
        self.cn_suffix = None
        self.cn_suffix_compact = None
        self.output_cn = None
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
        self.skip_subfamily_list = ["Regular", "Bold", "Italic", "BoldItalic"]
        self.is_nf_built = False
        self.is_cn_built = False
        self.has_cache = (
            self.check_cache_dir(self.output_variable, count=2)
            and self.check_cache_dir(self.output_otf)
            and self.check_cache_dir(self.output_ttf)
            and self.check_cache_dir(self.output_ttf_hinted)
            and self.check_cache_dir(self.output_woff2)
        )
        self.github_mirror = environ.get("GITHUB", "github.com")

    def load_cn_dir_and_suffix(self, with_nerd_font: bool) -> None:
        if with_nerd_font:
            self.cn_base_font_dir = self.output_nf
            self.cn_suffix = "NF CN"
            self.cn_suffix_compact = "NF-CN"
        else:
            self.cn_base_font_dir = joinPaths(self.output_dir, "TTF")
            self.cn_suffix = self.cn_suffix_compact = "CN"
        self.output_cn = joinPaths(self.output_dir, self.cn_suffix_compact)

    def should_use_font_patcher(self, config: FontConfig) -> bool:
        if not (
            len(config.nerd_font["extra_args"]) > 0
            or config.nerd_font["use_font_patcher"]
            or config.nerd_font["glyphs"] != ["--complete"]
        ):
            return False

        if check_font_patcher(
            version=config.nerd_font["version"],
            github_mirror=self.github_mirror,
        ) and not path.exists(config.nerd_font["font_forge_bin"]):
            print(
                f"FontForge bin({config.nerd_font['font_forge_bin']}) not found. Use prebuild Nerd-Font base font instead."
            )
            return False

        return True

    def should_build_cn(self, config: FontConfig) -> bool:
        if not config.cn["enable"] and not config.use_cn_both:
            print(
                '\nNo `"cn.enable": true` in config.json or no `--cn` / `--cn-both` in argv. Skip CN build.'
            )
            return False

        if config.cn["clean_cache"]:
            print("Clean CN static fonts")
            shutil.rmtree(self.cn_static_dir, ignore_errors=True)

        if (
            not path.exists(self.cn_static_dir)
            or listdir(self.cn_static_dir).__len__() != 16
        ):
            tag = "cn-base"
            if is_ci() or config.cn["use_static_base_font"]:
                return download_cn_base_font(
                    tag=tag,
                    zip_path="cn-base-static.zip",
                    target_dir=self.cn_static_dir,
                    github_mirror=self.github_mirror,
                )

            if not config.cn["use_static_base_font"] or not path.exists(
                self.cn_static_dir
            ):
                if (
                    path.exists(self.cn_variable_dir)
                    and listdir(self.cn_variable_dir).__len__() == 2
                ):
                    print("No static CN fonts but detect CN base fonts")
                    instantiate_cn_base(self.cn_variable_dir, self.cn_static_dir)
                    return True

                result = download_cn_base_font(
                    tag=tag,
                    zip_path="cn-base-variable.zip",
                    target_dir=self.cn_variable_dir,
                    github_mirror=self.github_mirror,
                )
                if result:
                    instantiate_cn_base(self.cn_variable_dir, self.cn_static_dir)
                    return True

            print("\nCN base fonts don't exist. Skip CN build.")
            return False
        return True

    def check_cache_dir(self, cache_dir: str, count: int = 16) -> bool:
        if not path.isdir(cache_dir):
            return False
        return listdir(cache_dir).__len__() == count


def handle_ligatures(
    font: TTFont, enable_ligature: bool, freeze_config: dict[str, str]
):
    """
    whether to enable ligatures and freeze font features
    """

    freeze_feature(
        font=font,
        calt=enable_ligature,
        moving_rules=["ss03", "ss07", "ss08"],
        config=freeze_config,
    )


def instantiate_cn_base(cn_variable_dir: str, cn_static_dir: str):
    print("=========================================")
    print("Instantiating CN Base font, be patient...")
    print("=========================================")
    run(
        f"ftcli converter vf2i {cn_variable_dir} -out {cn_static_dir}",
        log=True,
    )
    run(f"ftcli ttf fix-contours {cn_static_dir}", log=True)
    run(f"ftcli ttf remove-overlaps {cn_static_dir}", log=True)
    run(
        f"ftcli utils del-table -t kern -t GPOS {cn_static_dir}",
        log=True,
    )


def parse_style_name(style_name_compact: str, skip_subfamily_list: list[str]):
    is_italic = style_name_compact.endswith("Italic")

    _style_name = style_name_compact
    if is_italic and style_name_compact[0] != "I":
        _style_name = style_name_compact[:-6] + " Italic"

    if style_name_compact in skip_subfamily_list:
        return "", _style_name, _style_name, True
    else:
        return (
            " " + style_name_compact.replace("Italic", ""),
            "Italic" if is_italic else "Regular",
            _style_name,
            False,
        )


def fix_cn_cv(font: TTFont):
    gsub_table = font["GSUB"].table
    config = {
        "cv96": ["quoteleft", "quoteright", "quotedblleft", "quotedblright"],
        "cv97": ["ellipsis"],
        "cv98": ["emdash"],
    }

    for feature_record in gsub_table.FeatureList.FeatureRecord:
        if feature_record.FeatureTag in config:
            sub_table = gsub_table.LookupList.Lookup[
                feature_record.Feature.LookupListIndex[0]
            ].SubTable[0]
            sub_table.mapping = {
                value: f"{value}.full" for value in config[feature_record.FeatureTag]
            }


def remove_locl(font: TTFont):
    gsub = font["GSUB"]
    features_to_remove = []

    for feature in gsub.table.FeatureList.FeatureRecord:
        feature_tag = feature.FeatureTag

        if feature_tag == "locl":
            features_to_remove.append(feature)

    for feature in features_to_remove:
        gsub.table.FeatureList.FeatureRecord.remove(feature)


def drop_mac_names(dir: str):
    run(f"ftcli name del-mac-names -r {dir}")


def get_new_name_from_map(old_name: str, map: dict[str, str]):
    new_name = map.get(old_name)
    if not new_name:
        arr = re.split(r"[\._]", old_name, maxsplit=2)
        if map.get(arr[0]):
            new_name = map.get(arr[0]) + old_name[len(arr[0]) :]
    return new_name


def rename_glyph_name(
    font: TTFont,
    map: dict[str, str],
    post_extra_names: bool = True,
):
    print("Rename glyph names")
    glyph_names = font.getGlyphOrder()
    extra_names = font["post"].extraNames
    modified = False
    merged_map = {
        **map,
        **{
            "uni2047.liga": "question_question.liga",
            "dotlessi": "idotless",
            "f_f": "f_f.liga",
        },
    }

    for i, _ in enumerate(glyph_names):
        old_name = str(glyph_names[i])

        new_name = get_new_name_from_map(old_name, merged_map)
        if not new_name or new_name == old_name:
            continue

        # print(f"[Rename] {old_name} -> {new_name}")
        glyph_names[i] = new_name
        modified = True

        if post_extra_names and old_name in extra_names:
            extra_names[extra_names.index(old_name)] = new_name

    if modified:
        font.setGlyphOrder(glyph_names)


def get_unique_identifier(
    font_config: FontConfig,
    postscript_name: str,
    narrow: bool = False,
    ignore_suffix: bool = False,
) -> str:
    if ignore_suffix:
        suffix = ""
    else:
        suffix = font_config.freeze_config_str
        if "CN" in postscript_name and narrow:
            suffix += "Narrow;"

        if "NF" in postscript_name:
            nf_ver = font_config.nerd_font["version"]
            suffix = f"NF{nf_ver};{suffix}"

    beta_str = f"-{font_config.beta}" if font_config.beta else ""
    return f"{font_config.version_str}{beta_str};SUBF;{postscript_name};2024;FL830;{suffix}"


def change_glyph_width(font: TTFont, match_width: int, target_width: int):
    font["hhea"].advanceWidthMax = target_width
    for name in font.getGlyphOrder():
        glyph = font["glyf"][name]
        width, lsb = font["hmtx"][name]
        if width != match_width:
            continue
        if glyph.numberOfContours == 0:
            font["hmtx"][name] = (target_width, lsb)
            continue

        delta = round((target_width - width) / 2)
        glyph.coordinates.translate((delta, 0))
        glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax = (
            glyph.coordinates.calcIntBounds()
        )
        font["hmtx"][name] = (target_width, lsb + delta)


def update_font_names(
    font: TTFont,
    family_name: str,  # NameID 1
    style_name: str,  # NameID 2
    unique_identifier: str,  # NameID 3
    full_name: str,  # NameID 4
    version_str: str,  # NameID 5
    postscript_name: str,  # NameID 6
    is_skip_subfamily: bool,
    preferred_family_name: str = None,  # NameID 16
    preferred_style_name: str = None,  # NameID 17
):
    set_font_name(font, family_name, 1)
    set_font_name(font, style_name, 2)
    set_font_name(font, unique_identifier, 3)
    set_font_name(font, full_name, 4)
    set_font_name(font, version_str, 5)
    set_font_name(font, postscript_name, 6)

    if not is_skip_subfamily and preferred_family_name and preferred_style_name:
        set_font_name(font, preferred_family_name, 16)
        set_font_name(font, preferred_style_name, 17)


def add_gasp(font: TTFont):
    print("Fix GASP table")
    gasp = newTable("gasp")
    gasp.gaspRange = {65535: 15}
    font["gasp"] = gasp


def build_mono(f: str, font_config: FontConfig, build_option: BuildOption):
    print(f"👉 Minimal version for {f}")
    source_path = joinPaths(build_option.output_ttf, f)
    font = TTFont(source_path)

    style_compact = f.split("-")[-1].split(".")[0]

    style_with_prefix_space, style_in_2, style_in_17, is_skip_subfamily = (
        parse_style_name(
            style_name_compact=style_compact,
            skip_subfamily_list=build_option.skip_subfamily_list,
        )
    )

    postscript_name = f"{font_config.family_name_compact}-{style_compact}"

    update_font_names(
        font=font,
        family_name=font_config.family_name + style_with_prefix_space,
        style_name=style_in_2,
        full_name=f"{font_config.family_name} {style_in_17}",
        version_str=font_config.version_str,
        postscript_name=postscript_name,
        unique_identifier=get_unique_identifier(
            font_config=font_config,
            postscript_name=postscript_name,
        ),
        is_skip_subfamily=is_skip_subfamily,
        preferred_family_name=font_config.family_name,
        preferred_style_name=style_in_17,
    )

    # https://github.com/ftCLI/FoundryTools-CLI/issues/166#issuecomment-2095433585
    if style_with_prefix_space == " Thin":
        font["OS/2"].usWeightClass = 250
    elif style_with_prefix_space == " ExtraLight":
        font["OS/2"].usWeightClass = 275

    handle_ligatures(
        font=font,
        enable_ligature=font_config.enable_liga,
        freeze_config=font_config.feature_freeze,
    )

    remove(source_path)
    target_path = joinPaths(build_option.output_ttf, f"{postscript_name}.ttf")
    font.save(target_path)
    font.close()

    # Autohint version
    print(f"Auto hint {postscript_name}.ttf")
    run(f"ftcli ttf autohint {target_path} -out {build_option.output_ttf_hinted}")

    if font_config.ttf_only:
        return

    # Woff2 version
    print(f"Convert {postscript_name}.ttf to WOFF2")
    run(
        f"ftcli converter ft2wf {target_path} -out {build_option.output_woff2} -f woff2"
    )

    # OTF version
    _otf_path = joinPaths(
        build_option.output_otf, path.basename(target_path).replace(".ttf", ".otf")
    )
    print(f"Convert {postscript_name}.ttf to OTF")
    run(
        f"ftcli converter ttf2otf --silent {target_path} -out {build_option.output_otf}"
    )
    if not font_config.debug:
        print(f"Optimize {postscript_name}.otf")
        run(f"ftcli otf fix-contours --silent {_otf_path}")
        run(f"ftcli otf fix-version {_otf_path}")


def build_nf_by_prebuild_nerd_font(
    font_basename: str, font_config: FontConfig, build_option: BuildOption
) -> TTFont:
    merger = Merger()
    return merger.merge(
        [
            joinPaths(build_option.ttf_base_dir, font_basename),
            f"{build_option.src_dir}/MapleMono-NF-Base{'-Mono' if font_config.nerd_font['mono'] else ''}.ttf",
        ]
    )


def build_nf_by_font_patcher(
    font_basename: str, font_config: FontConfig, build_option: BuildOption
) -> TTFont:
    """
    full args: https://github.com/ryanoasis/nerd-fonts?tab=readme-ov-file#font-patcher
    """
    _nf_args = [
        font_config.nerd_font["font_forge_bin"],
        "FontPatcher/font-patcher",
        "-l",
        "--careful",
        "--outputdir",
        build_option.output_nf,
    ] + font_config.nerd_font["glyphs"]

    if font_config.nerd_font["mono"]:
        _nf_args += ["--mono"]

    _nf_args += font_config.nerd_font["extra_args"]

    run(_nf_args + [joinPaths(build_option.ttf_base_dir, font_basename)], log=True)
    nf_file_name = "NerdFont"
    if font_config.nerd_font["mono"]:
        nf_file_name += "Mono"
    _path = joinPaths(
        build_option.output_nf, font_basename.replace("-", f"{nf_file_name}-")
    )
    font = TTFont(_path)
    remove(_path)
    return font


def build_nf(
    f: str,
    get_ttfont: Callable[[str, FontConfig, BuildOption], TTFont],
    font_config: FontConfig,
    build_option: BuildOption,
):
    print(f"👉 NerdFont version for {f}")
    makedirs(build_option.output_nf, exist_ok=True)
    nf_font = get_ttfont(f, font_config, build_option)

    # format font name
    style_compact_nf = f.split("-")[-1].split(".")[0]

    style_nf_with_prefix_space, style_in_2, style_in_17, is_skip_sufamily = (
        parse_style_name(
            style_name_compact=style_compact_nf,
            skip_subfamily_list=build_option.skip_subfamily_list,
        )
    )

    postscript_name = f"{font_config.family_name_compact}-NF-{style_compact_nf}"

    update_font_names(
        font=nf_font,
        family_name=f"{font_config.family_name} NF{style_nf_with_prefix_space}",
        style_name=style_in_2,
        full_name=f"{font_config.family_name} NF {style_in_17}",
        version_str=font_config.version_str,
        postscript_name=postscript_name,
        unique_identifier=get_unique_identifier(
            font_config=font_config,
            postscript_name=postscript_name,
        ),
        is_skip_subfamily=is_skip_sufamily,
        preferred_family_name=f"{font_config.family_name} NF",
        preferred_style_name=style_in_17,
    )

    target_path = joinPaths(
        build_option.output_nf,
        f"{font_config.family_name_compact}-NF-{style_compact_nf}.ttf",
    )
    nf_font.save(target_path)
    nf_font.close()


def build_cn(f: str, font_config: FontConfig, build_option: BuildOption):
    style_compact_cn = f.split("-")[-1].split(".")[0]

    print(f"👉 {build_option.cn_suffix_compact} version for {f}")

    merger = Merger()
    cn_font = merger.merge(
        [
            joinPaths(build_option.cn_base_font_dir, f),
            joinPaths(
                build_option.cn_static_dir, f"MapleMonoCN-{style_compact_cn}.ttf"
            ),
        ]
    )

    style_cn_with_prefix_space, style_in_2, style_in_17, is_skip_subfamily = (
        parse_style_name(
            style_name_compact=style_compact_cn,
            skip_subfamily_list=build_option.skip_subfamily_list,
        )
    )

    postscript_name = f"{font_config.family_name_compact}-{build_option.cn_suffix_compact}-{style_compact_cn}"

    update_font_names(
        font=cn_font,
        family_name=f"{font_config.family_name} {build_option.cn_suffix}{style_cn_with_prefix_space}",
        style_name=style_in_2,
        full_name=f"{font_config.family_name} {build_option.cn_suffix} {style_in_17}",
        version_str=font_config.version_str,
        postscript_name=postscript_name,
        unique_identifier=get_unique_identifier(
            font_config=font_config,
            postscript_name=postscript_name,
            narrow=font_config.cn["narrow"],
        ),
        is_skip_subfamily=is_skip_subfamily,
        preferred_family_name=f"{font_config.family_name} {build_option.cn_suffix}",
        preferred_style_name=style_in_17,
    )

    cn_font["OS/2"].xAvgCharWidth = 600

    # https://github.com/subframe7536/maple-font/issues/188
    # https://github.com/subframe7536/maple-font/issues/313
    fix_cn_cv(cn_font)

    handle_ligatures(
        font=cn_font,
        enable_ligature=font_config.enable_liga,
        freeze_config=font_config.feature_freeze,
    )

    if font_config.cn["narrow"]:
        change_glyph_width(
            font=cn_font,
            match_width=2 * font_config.glyph_width,
            target_width=font_config.glyph_width_cn_narrow,
        )

    # https://github.com/subframe7536/maple-font/issues/239
    # already removed at merge time
    # remove_locl(font)

    if font_config.cn["fix_meta_table"]:
        # add code page, Latin / Japanese / Simplify Chinese / Traditional Chinese
        cn_font["OS/2"].ulCodePageRange1 = 1 << 0 | 1 << 17 | 1 << 18 | 1 << 20

        # fix meta table, https://learn.microsoft.com/en-us/typography/opentype/spec/meta
        meta = newTable("meta")
        meta.data = {
            "dlng": "Latn, Hans, Hant, Jpan",
            "slng": "Latn, Hans, Hant, Jpan",
        }
        cn_font["meta"] = meta

    target_path = joinPaths(
        build_option.output_cn,
        f"{font_config.family_name_compact}-{build_option.cn_suffix_compact}-{style_compact_cn}.ttf",
    )
    cn_font.save(target_path)
    cn_font.close()


def run_build(pool_size: int, fn: Callable, dir: str):
    if pool_size > 1:
        with Pool(pool_size) as p:
            p.map(fn, listdir(dir))
    else:
        for f in listdir(dir):
            fn(f)


def main():
    check_ftcli()
    parsed_args = parse_args()

    font_config = FontConfig(args=parsed_args)
    build_option = BuildOption(font_config)
    build_option.load_cn_dir_and_suffix(font_config.should_build_nf_cn())

    if parsed_args.dry:
        print("font_config:", json.dumps(font_config.__dict__, indent=4))
        if not is_ci():
            print("build_option:", json.dumps(build_option.__dict__, indent=4))
            print("parsed_args:", json.dumps(parsed_args.__dict__, indent=4))
        return

    should_use_cache = parsed_args.cache

    if not should_use_cache:
        print("🧹 Clean cache...\n")
        shutil.rmtree(build_option.output_dir, ignore_errors=True)
        shutil.rmtree(build_option.output_woff2, ignore_errors=True)

    makedirs(build_option.output_dir, exist_ok=True)
    makedirs(build_option.output_variable, exist_ok=True)

    start_time = time.time()
    print("🚩 Start building ...\n")

    # =========================================================================================
    # ===================================   Build basic   =====================================
    # =========================================================================================

    if not should_use_cache or not build_option.has_cache:
        input_files = [
            joinPaths(build_option.src_dir, "MapleMono-Italic[wght]-VF.ttf"),
            joinPaths(build_option.src_dir, "MapleMono[wght]-VF.ttf"),
        ]
        for input_file in input_files:
            font = TTFont(input_file)
            basename = path.basename(input_file)
            print(f"👉 Variable version for {basename}")

            # fix auto rename by FontLab
            rename_glyph_name(
                font=font,
                map=match_unicode_names(
                    input_file.replace(".ttf", ".glyphs").replace("-VF", "")
                ),
            )

            if font_config.apply_fea_file:
                fea_path = joinPaths(
                    build_option.src_dir,
                    "features/italic.fea"
                    if "Italic" in input_file
                    else "features/regular.fea",
                )
                print(f"Apply feature file [{fea_path}] into [{basename}]")
                addOpenTypeFeatures(
                    font,
                    fea_path,
                )

            set_font_name(
                font,
                get_unique_identifier(
                    font_config=font_config,
                    postscript_name=get_font_name(font, 6),
                    ignore_suffix=True,
                ),
                3,
            )

            verify_glyph_width(
                font=font,
                expect_widths=font_config.get_valid_glyph_width_list(),
                forgive=font_config.forgive,
            )

            add_gasp(font)

            font.save(
                input_file.replace(
                    build_option.src_dir, build_option.output_variable
                ).replace("-VF", "")
            )

        print("\n✨ Instatiate and optimize fonts...\n")

        print("Check and optimize variable fonts")
        if not font_config.debug:
            run(f"ftcli fix decompose-transformed {build_option.output_variable}")

        run(f"ftcli fix italic-angle {build_option.output_variable}")
        run(f"ftcli fix monospace {build_option.output_variable}")
        print("Instantiate TTF")
        run(
            f"ftcli converter vf2i {build_option.output_variable} -out {build_option.output_ttf}"
        )
        print("Fix static TTF")
        run(f"ftcli fix italic-angle {build_option.output_ttf}")
        run(f"ftcli fix monospace {build_option.output_ttf}")
        run(f"ftcli fix strip-names {build_option.output_ttf}")

        if font_config.debug:
            run(f"ftcli ttf dehint {build_option.output_ttf}")
        else:
            # dehint, remove overlap and fix contours
            run(f"ftcli ttf fix-contours --silent {build_option.output_ttf}")

        _build_mono = partial(
            build_mono, font_config=font_config, build_option=build_option
        )

        run_build(font_config.pool_size, _build_mono, build_option.output_ttf)

        drop_mac_names(build_option.output_variable)
        drop_mac_names(build_option.output_ttf)

        if not font_config.ttf_only:
            drop_mac_names(build_option.output_ttf_hinted)
            drop_mac_names(build_option.output_otf)
            drop_mac_names(build_option.output_woff2)

    # =========================================================================================
    # ====================================   Build NF   =======================================
    # =========================================================================================

    if font_config.nerd_font["enable"]:
        use_font_patcher = build_option.should_use_font_patcher(font_config)

        get_ttfont = (
            build_nf_by_font_patcher
            if use_font_patcher
            else build_nf_by_prebuild_nerd_font
        )

        _build_fn = partial(
            build_nf,
            get_ttfont=get_ttfont,
            font_config=font_config,
            build_option=build_option,
        )
        _version = font_config.nerd_font["version"]
        print(
            f"\n🔧 Patch Nerd-Font v{_version} using {'Font Patcher' if use_font_patcher else 'prebuild base font'}...\n"
        )

        run_build(font_config.pool_size, _build_fn, build_option.output_ttf)
        drop_mac_names(build_option.output_ttf)
        build_option.is_nf_built = True

        verify_glyph_width(
            font=TTFont(
                joinPaths(build_option.output_nf, listdir(build_option.output_nf)[0])
            ),
            expect_widths=font_config.get_valid_glyph_width_list(),
            forgive=font_config.forgive,
        )

    # =========================================================================================
    # ====================================   Build CN   =======================================
    # =========================================================================================

    if build_option.should_build_cn(font_config):

        def _build_cn():
            print(
                f"\n🔎 Build CN fonts {'with Nerd-Font' if font_config.should_build_nf_cn() else ''}...\n"
            )
            makedirs(build_option.output_cn, exist_ok=True)
            fn = partial(build_cn, font_config=font_config, build_option=build_option)

            run_build(font_config.pool_size, fn, build_option.cn_base_font_dir)

            if font_config.cn["use_hinted"]:
                print("Auto hinting all glyphs")
                run(f"ftcli ttf autohint {build_option.output_cn}")

            drop_mac_names(build_option.cn_base_font_dir)

        _build_cn()

        if font_config.use_cn_both:
            result = font_config.toggle_nf_cn_config()
            if result:
                build_option.load_cn_dir_and_suffix(font_config.should_build_nf_cn())
                _build_cn()

        build_option.is_cn_built = True

        verify_glyph_width(
            font=TTFont(
                joinPaths(build_option.output_cn, listdir(build_option.output_cn)[0])
            ),
            expect_widths=font_config.get_valid_glyph_width_list(True),
            forgive=font_config.forgive,
        )

    # =========================================================================================
    # ==================================   Write Config   =====================================
    # =========================================================================================
    with open(
        joinPaths(build_option.output_dir, "build-config.json"), "w", encoding="utf-8"
    ) as config_file:
        result = {
            "version": FONT_VERSION,
            "family_name": font_config.family_name,
            "use_hinted": font_config.use_hinted,
            "ligature": font_config.enable_liga,
            "feature_freeze": font_config.feature_freeze,
            "nerd_font": font_config.nerd_font,
            "cn": font_config.cn,
        }
        del result["nerd_font"]["font_forge_bin"]
        result["nerd_font"]["enable"] = build_option.is_nf_built
        result["cn"]["enable"] = build_option.is_cn_built
        config_file.write(
            json.dumps(
                result,
                indent=4,
            )
        )

    # =========================================================================================
    # ====================================   archive   ========================================
    # =========================================================================================
    if font_config.archive:
        print("\n🚀 archive files...\n")

        # archive fonts
        archive_dir_name = "archive"
        archive_dir = joinPaths(build_option.output_dir, archive_dir_name)
        makedirs(archive_dir, exist_ok=True)

        # archive fonts
        for f in listdir(build_option.output_dir):
            if f == archive_dir_name or f.endswith(".json"):
                continue

            if should_use_cache and f not in ["CN", "NF", "NF-CN"]:
                continue

            sha256, zip_file_name_without_ext = compress_folder(
                family_name_compact=font_config.family_name_compact,
                suffix="-unhinted" if not font_config.use_hinted else "",
                source_file_or_dir_path=joinPaths(build_option.output_dir, f),
                build_config_path=joinPaths(
                    build_option.output_dir, "build-config.json"
                ),
                target_parent_dir_path=archive_dir,
            )
            with open(
                joinPaths(archive_dir, f"{zip_file_name_without_ext}.sha256"),
                "w",
                encoding="utf-8",
            ) as hash_file:
                hash_file.write(sha256)

            print(f"👉 archive: {f}")

    # =========================================================================================
    # =====================================   Finish   ========================================
    # =========================================================================================
    if is_ci():
        return

    freeze_str = (
        font_config.freeze_config_str
        if font_config.freeze_config_str != ""
        else "default config"
    )
    end_time = time.time()
    date_time_fmt = time.strftime("%H:%M:%S", time.localtime(end_time))
    time_diff = end_time - start_time
    output = joinPaths(getcwd().replace("\\", "/"), build_option.output_dir)
    print(
        f"\n🏁 Build finished at {date_time_fmt}, cost {time_diff:.2f} s, family name is {font_config.family_name}, {freeze_str}\n   See your fonts in {output}"
    )


if __name__ == "__main__":
    main()
