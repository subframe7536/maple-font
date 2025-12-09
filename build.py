#!/usr/bin/env python3
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import importlib.util
from io import BytesIO
import json
import re
import shutil
import time
from functools import partial
from os import environ, getcwd, listdir, makedirs, path, remove, getenv
from typing import Callable, Literal
from fontTools.ttLib import TTFont, newTable
from fontTools.feaLib.builder import addOpenTypeFeatures, addOpenTypeFeaturesFromString
from ttfautohint import StemWidthMode, ttfautohint
from source.py.utils import (
    add_gasp,
    add_ital_axis_to_stat,
    adjust_line_height,
    change_glyph_width_or_scale,
    check_font_patcher,
    check_directory_hash,
    expand_custom_tag_bg,
    patch_instance,
    verify_glyph_width,
    archive_fonts,
    download_cn_base_font,
    get_font_forge_bin,
    is_ci,
    match_unicode_names,
    run,
    set_font_name,
    joinPaths,
    merge_ttfonts,
    default_weight_map,
)
from source.py.freeze import freeze_feature, get_freeze_config_str, is_enable
from source.py.feature import (
    generate_fea_string,
    get_freeze_moving_rules,
    normal_enabled_features,
)


FONT_VERSION = "v7.9"
# =========================================================================================


def check_ftcli():
    package_name_v1 = "foundryToolsCLI"
    package_spec_v1 = importlib.util.find_spec(package_name_v1)
    package_name_v2 = "foundrytools_cli"
    package_spec_v2 = importlib.util.find_spec(package_name_v2)

    if not package_spec_v1 and not package_spec_v2:
        print(
            "❗ foundrytools-cli is not found. Please run `pip install foundrytools-cli`"
        )
        exit(1)

    try:
        installed_package = importlib.import_module(
            package_name_v2 if package_spec_v2 else package_name_v1
        )
        version = getattr(installed_package, "__version__", None)
        if version and version < "2":
            print(
                f"❗ foundrytools-cli version {version} is too old. Please run `pip install --upgrade foundrytools-cli`"
            )
            exit(1)
    except Exception as e:
        print(f"❗ Error checking foundrytools-cli version: {e}")
        exit(1)


# =========================================================================================


def parse_scale_factor(value) -> tuple[float, float]:
    if isinstance(value, float):
        return (value, value)
    if isinstance(value, list):
        return (float(value[0]), float(value[1]))

    # Split the value by comma to handle width and height
    parts = value.split(",")

    if len(parts) == 1:
        # Single number case
        return float(parts[0]), float(parts[0])  # Same scale for width and height
    elif len(parts) == 2:
        # Two numbers case
        return float(parts[0]), float(parts[1])
    else:
        raise argparse.ArgumentTypeError(
            "Invalid scale factor format. Use <factor> or <w_factor>,<h_factor>."
        )


def parse_args(args: list[str] | None = None):
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
        help="Add `Debug` suffix to family name and faster build",
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
        "--keep-infinite-arrow",
        default=None,
        action="store_true",
        help="(Deprecated) Keep infinite arrow ligatures in hinted font (Removed by default)",
    )
    feature_group.add_argument(
        "--infinite-arrow",
        default=None,
        action="store_true",
        dest="infinite_arrow",
        help="Enable infinite arrow ligatures (Disabled in hinted font by default)",
    )
    feature_group.add_argument(
        "--remove-tag-liga",
        default=None,
        action="store_true",
        help="Remove plain text tag ligatures like `[TODO]`",
    )
    feature_group.add_argument(
        "--line-height",
        type=float,
        help="Scale factor for line height (e.g. 1.1)",
    )
    feature_group.add_argument(
        "--nf-mono",
        action="store_true",
        help="Make Nerd Font icons' width fixed",
    )
    feature_group.add_argument(
        "--nf-propo",
        action="store_true",
        help="Make Nerd Font icons' width variable, override `--nf-mono`",
    )
    feature_group.add_argument(
        "--cn-narrow",
        action="store_true",
        help="Make CN / JP characters narrow (And the font cannot be recogized as monospaced font)",
    )
    feature_group.add_argument(
        "--cn-scale-factor",
        type=parse_scale_factor,
        help="Scale factor for CN / JP glyphs. Format: <factor> or <width_factor>,<height_factor> (e.g. 1.1 or 1.2,1.1)",
    )

    build_group = parser.add_argument_group("Build Options")
    nf_group = build_group.add_mutually_exclusive_group()
    nf_group.add_argument(
        "--nf",
        "--nerd-font",
        dest="nerd_font",
        default=None,
        action="store_true",
        help="Build Nerd-Font version (default)",
    )
    nf_group.add_argument(
        "--no-nf",
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
        "--least-styles",
        action="store_true",
        help="Only build Regular / Bold / Italic / BoldItalic style",
    )
    build_group.add_argument(
        "--font-patcher",
        action="store_true",
        help="Force the use of Nerd Font Patcher to build NF format",
    )
    build_group.add_argument(
        "--cache",
        action="store_true",
        help="Reuse font cache of TTF, OTF and Woff2 formats",
    )
    build_group.add_argument(
        "--cn-rebuild",
        action="store_true",
        help="Reinstantiate variable CN base font",
    )
    build_group.add_argument(
        "--archive",
        action="store_true",
        help="Build font archives with config and license. If has `--cache` flag, only archive NF and CN formats",
    )

    return parser.parse_args(args)


# =========================================================================================


class FontConfig:
    def __init__(self, args, version: str | None = None):
        if version:
            global FONT_VERSION
            FONT_VERSION = version

        self.archive = False
        self.use_cn_both = False
        self.ttf_only = False
        self.debug = False
        self.apply_fea_file = False
        # the number of parallel tasks
        # when run in codespace, this will be 1
        self.pool_size = 1 if not getenv("CODESPACE_NAME") else 4
        # font family name
        self.family_name = "Maple Mono"
        self.family_name_compact = "MapleMono"
        # whether to use hinted ttf as base font
        self.use_hinted = True
        # whether to enable ligature
        self.enable_ligature = True
        # whether to enable infinite arrow ligatures in hinted font
        self.infinite_arrow = None
        # whether to remove plain text ligatures like `[TODO]`
        self.remove_tag_liga = False
        self.weight_mapping = default_weight_map
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
            "cv37": "ignore",
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
            # whether to make icons' x-width fixed
            "mono": None,
            # whether to make icons' glyph width variable, override "mono"
            "propo": None,
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
            "use_static_base_font": True,  # Deprecated. Always `True`
            # scale factor for CN glyphs
            "scale_factor": (1.0, 1.0),
        }
        self.glyph_width = 600
        self.glyph_width_cn_narrow = 1000
        self.use_normal_preset = False
        self.ttfautohint_param = {}
        self.line_height = 1.0
        self.vertical_metric: tuple[int, int] = (1020, -300)

        self.__load_config()
        self.__load_args(args)

        ver = FONT_VERSION
        self.beta = None
        if "-" in FONT_VERSION:
            ver, beta = FONT_VERSION.split("-")
            self.beta = beta

        major, minor = ver.split(".")

        if major.startswith("v"):
            major = major[1:]

        self.version = f"{major}.{minor}"
        self.version_str = f"Version {major}.{minor:03}"

    def __load_config(self):
        config_file_path = "config.json"
        try:
            with open(config_file_path, "r") as f:
                data = json.load(f)
                for prop in [
                    "family_name",
                    "pool_size",
                    "use_hinted",
                    "enable_ligature",
                    "ttfautohint_param",
                    "infinite_arrow",
                    "line_height",
                    "github_mirror",
                    "weight_mapping",
                    "remove_tag_liga",
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
                if "ligature" in data and data["ligature"] is not None:
                    self.enable_ligature = data["ligature"]

        except FileNotFoundError:
            print(f"🚨 Config file not found: {config_file_path}, use default config")
        except json.JSONDecodeError:
            print(f"❗ Error: Invalid JSON in config file: {config_file_path}")
            exit(1)
        except Exception as e:
            print(f"❗ An unexpected error occurred while parsing config file: {e}")
            exit(1)

    def _apply_feature_options(self, args):
        """Apply feature-related arguments."""
        if args.normal:
            self.use_normal_preset = True
            for feat in normal_enabled_features:
                self.feature_freeze[feat] = "enable"

        if args.feat is not None:
            for f in args.feat:
                if f in self.feature_freeze:
                    self.feature_freeze[f] = "enable"

        if args.hinted is not None:
            self.use_hinted = args.hinted

        if args.liga is not None:
            self.enable_ligature = args.liga

        if args.infinite_arrow:
            self.infinite_arrow = True

        if args.remove_tag_liga:
            self.remove_tag_liga = True

        if args.line_height is not None:
            self.line_height = args.line_height

        if "font_forge_bin" not in self.nerd_font:
            self.nerd_font["font_forge_bin"] = get_font_forge_bin()

    def _apply_nerd_font_options(self, args):
        """Apply Nerd Font specific arguments."""
        if self.debug:
            self.nerd_font["enable"] = False
        if args.nerd_font is not None:
            self.nerd_font["enable"] = args.nerd_font

        if args.nf_mono:
            self.nerd_font["mono"] = args.nf_mono
            self.nerd_font["enable"] = True

        if args.nf_propo:
            self.nerd_font["propo"] = args.nf_propo
            self.nerd_font["enable"] = True

    def _apply_cn_options(self, args):
        """Apply Chinese font related arguments."""
        if args.cn is not None:
            self.cn["enable"] = args.cn

        if args.cn_narrow:
            self.cn["narrow"] = True

        if args.cn_scale_factor:
            self.cn["scale_factor"] = args.cn_scale_factor
        if isinstance(self.cn["scale_factor"], (float, list)):
            self.cn["scale_factor"] = parse_scale_factor(self.cn["scale_factor"])

    def _apply_build_options(self, args):
        """Apply general build options."""
        self.archive = args.archive
        self.use_cn_both = args.cn_both
        self.debug = args.debug

        if args.ttf_only:
            self.ttf_only = True

        if args.apply_fea_file:
            self.apply_fea_file = True

        if args.font_patcher:
            self.nerd_font["use_font_patcher"] = True

        # Deprecated --cn-rebuild handling (to be removed in future)
        if args.cn_rebuild:
            print(
                "⚠️ `--cn-rebuild` is deprecated. Run `python task.py cn-rebuild` instead"
            )
            self.cn["enable"] = True

    def _update_family_names(self):
        """Update family names based on options."""
        name_arr = [word.capitalize() for word in self.family_name.split(" ")]
        if self.use_normal_preset:
            name_arr.append("Normal")
        if not self.enable_ligature:
            name_arr.append("NL")
        if self.debug:
            name_arr.append("Debug")
        self.family_name = " ".join(name_arr)
        self.family_name_compact = "".join(name_arr)

    def __load_args(self, args):
        self._apply_build_options(args)
        self._apply_feature_options(args)
        self._apply_nerd_font_options(args)
        self._apply_cn_options(args)
        self._update_family_names()

        self.freeze_config_str = get_freeze_config_str(
            self.feature_freeze, self.enable_ligature
        )

    def should_build_nf_cn(self) -> bool:
        return self.cn["with_nerd_font"] and self.nerd_font["enable"]

    def get_nf_suffix(self) -> Literal["Mono", "Propo", ""]:
        extra_args = self.nerd_font["extra_args"]
        if (
            self.nerd_font["mono"]
            or "-s" in extra_args
            or "--mono" in extra_args
            or "--single-width-glyphs" in extra_args
        ):
            return "Mono"
        elif self.nerd_font["propo"] or "--variable-width-glyphs" in extra_args:
            return "Propo"
        return ""

    def toggle_nf_cn_config(self) -> bool:
        if not self.nerd_font["enable"]:
            print("❗Nerd-Font version is disabled, skip toggle.")
            return False
        self.cn["with_nerd_font"] = not self.cn["with_nerd_font"]
        return True

    def get_valid_glyph_width_list(self, cn=False):
        if cn:
            cn = (
                self.glyph_width_cn_narrow
                if self.cn["narrow"]
                else 2 * self.glyph_width
            )
            return [
                0,
                self.glyph_width,
                cn,
            ]
        else:
            return [0, self.glyph_width]

    def patch_font_feature(
        self,
        font: TTFont,
        issue_fea_dir: str,
        is_italic: bool,
        is_cn: bool,
        is_variable: bool,
        is_hinted: bool,
        fea_path: str,
    ):
        if self.apply_fea_file:
            if fea_path:
                print(f"Apply feature file [{fea_path}]")
                addOpenTypeFeatures(
                    font,
                    fea_path,
                )
            self.freeze_feature_static(font, is_variable)
            return

        # If is hinted and keep inf liga, skip patching feature
        if is_hinted and self.infinite_arrow:
            return

        # If `infinite_arrow` is None
        # - hinted font will disable inf
        # - unhinted font will enable inf
        # If `infinite_arrow` is True
        # - hinted font will enable inf
        # - unhinted font will enable inf
        # If `infinite_arrow` is False
        # - hinted font will disable inf
        # - unhinted font will disable inf
        enable_infinite = (
            bool(self.infinite_arrow)
            if self.infinite_arrow is not None
            else not is_hinted
        )

        fea_str = generate_fea_string(
            is_italic=is_italic,
            is_cn=is_cn,
            is_normal=self.use_normal_preset,
            is_calt=self.enable_ligature,
            enable_infinite=enable_infinite,
            enable_tag=not self.remove_tag_liga,
            variable_enabled_feature_list=[
                key for key, val in self.feature_freeze.items() if is_enable(val)
            ]
            if is_variable
            else [],
            remove_italic_calt=is_enable(self.feature_freeze["cv35"]),
        )
        try:
            addOpenTypeFeaturesFromString(font, fea_str)
        except Exception as e:
            issue_fea_path = joinPaths(issue_fea_dir, "issue.fea")
            with open(issue_fea_path, "w+") as f:
                banner = f"Generated feature with italic={is_italic}, cn={is_cn}, normal={self.use_normal_preset}, calt={self.enable_ligature}, variable={is_variable}"
                f.write(f"# {banner}\n\n{fea_str}")
            raise SyntaxError(
                f"Error patching fea string: {e}\n\nSee generated fea string in {issue_fea_path}"
            ) from e
        self.freeze_feature_static(font, is_variable)

    def freeze_feature_static(self, font: TTFont, is_variable: bool):
        if not is_variable:
            freeze_feature(
                font=font,
                calt=self.enable_ligature,
                moving_rules=get_freeze_moving_rules(),
                config=self.feature_freeze,
            )


class BuildOption:
    def __init__(self, use_hinted: bool):
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
            self.output_dir, "TTF-AutoHint" if use_hinted else "TTF"
        )

        self.cn_variable_dir = f"{self.src_dir}/cn"
        self.cn_static_dir = f"{self.cn_variable_dir}/static"

        self.cn_suffix = None
        self.cn_suffix_compact = None
        self.cn_base_font_dir = ""
        self.output_cn = ""
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
        self.base_subfamily_list = ["Regular", "Bold", "Italic", "BoldItalic"]
        self.is_nf_built = False
        self.is_cn_built = False
        self.has_cache = (
            self.__check_file_count(self.output_variable, minCount=2, end=".ttf")
            and self.__check_file_count(self.output_ttf, minCount=4, end=".ttf")
            and self.__check_file_count(self.output_ttf_hinted, minCount=4, end=".ttf")
        )
        self.github_mirror = environ.get("GITHUB", "github.com")

    def get_feature_file_path(self, is_italic: bool, is_cn: bool = False) -> str:
        return joinPaths(
            self.src_dir,
            "features",
            ("italic" if is_italic else "regular") + ("_cn" if is_cn else "") + ".fea",
        )

    def load_cn_dir_and_suffix(self, font_config: FontConfig) -> None:
        suffix = font_config.get_nf_suffix()
        if font_config.should_build_nf_cn():
            self.cn_base_font_dir = self.output_nf
            self.cn_suffix = f"NF{suffix} CN"
            self.cn_suffix_compact = f"NF{suffix}-CN"
        else:
            self.cn_base_font_dir = self.ttf_base_dir
            self.cn_suffix = self.cn_suffix_compact = "CN"
        self.output_cn = joinPaths(
            self.output_dir,
            self.cn_suffix_compact.replace(suffix, ""),
        )

    def should_use_font_patcher(
        self, config: FontConfig, should_exit: bool = True
    ) -> bool:
        if not (
            len(config.nerd_font["extra_args"]) > 0
            or config.nerd_font["use_font_patcher"]
            or config.nerd_font["glyphs"] != ["--complete"]
        ):
            return False

        bin_path = config.nerd_font["font_forge_bin"]
        if (not bin_path or not path.exists(bin_path)) and should_exit:
            print(
                f"FontForge bin ({bin_path}) not found, cannot build with Nerd Font Patcher"
            )
            exit(1)

        if (
            not check_font_patcher(
                version=config.nerd_font["version"],
                github_mirror=self.github_mirror,
            )
            and should_exit
        ):
            exit(1)

        return True

    def should_build_cn(self, config: FontConfig) -> bool:
        if not config.cn["enable"] and not config.use_cn_both:
            print(
                '\nNo `"cn.enable": true` in config.json or `--cn` / `--cn-both` in argv. Skip CN build.'
            )
            return False
        return self.__ensure_cn_static_fonts(clean_cache=config.cn["clean_cache"])

    def __ensure_cn_static_fonts(self, clean_cache: bool) -> bool:
        if clean_cache:
            print("Clean CN static fonts")
            shutil.rmtree(self.cn_static_dir, ignore_errors=True)

        if self.__check_cn_exists():
            return True

        tag = "cn-base"
        zip_path = "cn-base-static.zip"
        if download_cn_base_font(
            tag=tag,
            zip_path=zip_path,
            target_dir=self.cn_static_dir,
            github_mirror=self.github_mirror,
        ):
            if self.__check_cn_exists():
                return True

            print(
                f"❗Invalid CN static fonts hash, please delete {zip_path} in root dir and rerun the script"
            )
            return False

        # # Try using variable fonts if static fonts aren't available
        # if path.exists(self.cn_variable_dir) and self.__check_file_count(
        #     self.cn_variable_dir, 2, "-VF.ttf"
        # ):
        #     print(
        #         "No static CN fonts but detect variable version, start instantiating..."
        #     )
        #     self.__instantiate_cn_base(
        #         cn_variable_dir=self.cn_variable_dir,
        #         cn_static_dir=self.cn_static_dir,
        #         pool_size=pool_size,
        #     )
        #     return True

        # # Download variable fonts and instantiate if necessary
        # if download_cn_base_font(
        #     tag=tag,
        #     zip_path="cn-base-variable.zip",
        #     target_dir=self.cn_variable_dir,
        #     github_mirror=self.github_mirror,
        # ):
        #     self.__instantiate_cn_base(
        #         cn_variable_dir=self.cn_variable_dir,
        #         cn_static_dir=self.cn_static_dir,
        #         pool_size=pool_size,
        #     )
        #     return True

        print("\nCN base fonts don't exist. Skip CN build.")
        return False

    def __check_cn_exists(self) -> bool:
        static_path = self.cn_static_dir
        print(f"\nChecking CN static font directory {static_path}")
        if not path.exists(static_path):
            print("🔎 Does not exist")
            return False
        if not self.__check_file_count(static_path):
            print("🔎 Exists but not enough font files")
            return False

        if check_directory_hash(static_path):
            print("✅ Hash verified")
            return True
        print("❌ Hash mismatch, removing directory")
        shutil.rmtree(static_path)
        return False

    # def __instantiate_cn_base(
    #     self, cn_variable_dir: str, cn_static_dir: str, pool_size: int
    # ):
    #     print("=========================================")
    #     print("Instantiating CN Base font, be patient...")
    #     print("=========================================")
    #     run_build(
    #         pool_size=pool_size,
    #         fn=partial(
    #             instantiate_cn_var, base_dir=cn_variable_dir, output_dir=cn_static_dir
    #         ),
    #         dir=cn_variable_dir,
    #     )
    #     run_build(
    #         pool_size=pool_size,
    #         fn=partial(optimize_cn_base, base_dir=cn_static_dir),
    #         dir=cn_static_dir,
    #     )
    #     run(f"ftcli name del-mac-names -r {cn_static_dir}")
    #     with open(f"{self.cn_static_dir}.sha256", "w") as f:
    #         f.write(get_directory_hash(self.cn_static_dir))
    #         f.flush()
    #     print(f"Update {self.cn_static_dir}.sha256")

    def __check_file_count(
        self, dir: str, minCount: int = 16, end: str | None = None
    ) -> bool:
        if not path.isdir(dir):
            return False
        return (
            len([f for f in listdir(dir) if end is None or f.endswith(end)]) >= minCount
        )


# def instantiate_cn_var(f: TTFont, base_dir: str, output_dir: str):
#     run(
#         f"ftcli converter var2static -out {output_dir} {joinPaths(base_dir, f)}",
#         log=True,
#     )


# def optimize_cn_base(f: TTFont, base_dir: str):
#     font_path = joinPaths(base_dir, f)
#     print(f"✨ Optimize {font_path}")
#     run(f"ftcli font correct-contours {font_path}")
#     run(
#         f"ftcli font del-table -t kern -t GPOS {font_path}",
#     )


def parse_style_name(style_name_compact: str, skip_subfamily_list: list[str]):
    is_italic = style_name_compact.endswith("Italic")

    _style_name = style_name_compact
    if is_italic and style_name_compact[0] != "I":
        _style_name = style_name_compact[:-6] + " Italic"

    if style_name_compact in skip_subfamily_list:
        return "", _style_name, _style_name, True, is_italic
    else:
        return (
            " " + style_name_compact.replace("Italic", ""),
            "Italic" if is_italic else "Regular",
            _style_name,
            False,
            is_italic,
        )


# def fix_cn_cv(font: TTFont):
#     gsub_table = font["GSUB"].table
#     config = {
#         "cv96": ["quoteleft", "quoteright", "quotedblleft", "quotedblright"],
#         "cv97": ["ellipsis"],
#         "cv98": ["emdash"],
#     }

#     for feature_record in gsub_table.FeatureList.FeatureRecord:
#         if feature_record.FeatureTag in config:
#             sub_table = gsub_table.LookupList.Lookup[
#                 feature_record.Feature.LookupListIndex[0]
#             ].SubTable[0]
#             sub_table.mapping = {
#                 value: f"{value}.full" for value in config[feature_record.FeatureTag]
#             }


# def remove_locl(font: TTFont):
#     gsub = font["GSUB"]
#     features_to_remove = []

#     for feature in gsub.table.FeatureList.FeatureRecord:
#         feature_tag = feature.FeatureTag

#         if feature_tag == "locl":
#             features_to_remove.append(feature)

#     for feature in features_to_remove:
#         gsub.table.FeatureList.FeatureRecord.remove(feature)


def rename_glyph_name(
    font: TTFont,
    map: dict[str, str],
    post_extra_names: bool = True,
):
    def get_new_name_from_map(old_name: str, map: dict[str, str]):
        new_name = map.get(old_name)
        if not new_name:
            arr = re.split(r"[\._]", old_name, maxsplit=2)
            name = map.get(arr[0])
            if name:
                new_name = name + old_name[len(arr[0]) :]
        return new_name

    print("Rename glyph names")
    glyph_names = font.getGlyphOrder()
    extra_names = font["post"].extraNames  # type: ignore
    modified = False
    merged_map = {
        **map,
        **{
            "uni2047.liga": "question_question.liga",
            "uni2047.liga.cv62": "question_question.liga.cv62",
            "dotlessi": "idotless",
            "f_f": "f_f.liga",
            "tag_uni061C.liga": "tag_mark.liga",
            "tag_u1F5C8.liga": "tag_note.liga",
            "tag_uni26A0.liga": "tag_warning.liga",
        },
    }

    for i, _ in enumerate(glyph_names):
        old_name = str(glyph_names[i])

        new_name = get_new_name_from_map(old_name, merged_map)
        if not new_name or new_name == old_name:
            continue

        # print(f"[Rename] {old_name} -> {new_name}")
        glyph_names[i] = new_name  # type: ignore
        modified = True

        if post_extra_names and old_name in extra_names:
            extra_names[extra_names.index(old_name)] = new_name

    if modified:
        font.setGlyphOrder(glyph_names)


def get_unique_identifier(
    font_config: FontConfig,
    postscript_name: str,
    narrow: bool = False,
    variable: bool = False,
) -> str:
    suffix = ""

    if variable:
        suffix += "Variable;"

    if "NF" in postscript_name:
        nf_ver = font_config.nerd_font["version"]
        suffix += f"NF{nf_ver};"

    if "CN" in postscript_name and narrow:
        suffix += "Narrow;"

    suffix += font_config.freeze_config_str

    beta_str = f"-{font_config.beta}" if font_config.beta else ""
    return f"{font_config.version_str}{beta_str};SUBF;{postscript_name};2024;FL830;{suffix}"


def update_font_names(
    font: TTFont,
    family_name: str,  # NameID 1
    style_name: str,  # NameID 2
    unique_identifier: str,  # NameID 3
    full_name: str,  # NameID 4
    version_str: str,  # NameID 5
    postscript_name: str,  # NameID 6
    is_skip_subfamily: bool,
    preferred_family_name: str | None = None,  # NameID 16
    preferred_style_name: str | None = None,  # NameID 17
):
    # Reported in #598
    # Why: https://github.com/ryanoasis/nerd-fonts/discussions/891#discussioncomment-3471991
    if len(family_name) > 31:
        print(
            f"⚠️ The family name [{family_name}] is too long (> 31) for some old Windows softwares"
        )
    set_font_name(font, family_name, 1)
    set_font_name(font, style_name, 2)
    set_font_name(font, unique_identifier, 3)
    set_font_name(font, full_name, 4)
    set_font_name(font, version_str, 5)
    set_font_name(font, postscript_name, 6)

    if not is_skip_subfamily and preferred_family_name and preferred_style_name:
        set_font_name(font, preferred_family_name, 16)
        set_font_name(font, preferred_style_name, 17)


def build_mono(f: str, font_config: FontConfig, build_option: BuildOption):
    print(f"👉 Minimal version for {f}")
    source_path = joinPaths(build_option.output_ttf, f)

    run(f"ftcli fix italic-angle {source_path}")
    run(f"ftcli fix monospace {source_path}")
    run(f"ftcli name strip-names {source_path}")
    run(f"ftcli font correct-contours {source_path}")
    run(f"ftcli ttf dehint {source_path}")
    run(f"ftcli fix transformed-components {source_path}")

    font = TTFont(source_path)

    style_compact = f.split("-")[-1].split(".")[0]

    style_with_prefix_space, style_in_2, style_in_17, is_skip_subfamily, is_italic = (
        parse_style_name(
            style_name_compact=style_compact,
            skip_subfamily_list=build_option.base_subfamily_list,
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
        font["OS/2"].usWeightClass = 250  # type: ignore
    elif style_with_prefix_space == " ExtraLight":
        font["OS/2"].usWeightClass = 275  # type: ignore

    font_config.patch_font_feature(
        font=font,
        issue_fea_dir=build_option.output_dir,
        is_italic=is_italic,
        is_cn=False,
        is_variable=False,
        is_hinted=False,
        fea_path=build_option.get_feature_file_path(is_italic),
    )

    verify_glyph_width(
        font=font,
        expect_widths=font_config.get_valid_glyph_width_list(),
        file_name=postscript_name,
    )

    remove(source_path)
    target_path = joinPaths(build_option.output_ttf, f"{postscript_name}.ttf")
    font.save(target_path)

    if font_config.ttf_only or font_config.debug:
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
    run(f"ftcli converter ttf2otf {target_path} -out {build_option.output_otf}")
    if not font_config.debug:
        print(f"Optimize {postscript_name}.otf")
        run(f"ftcli font correct-contours {_otf_path}")
        run(f"ftcli cff set-names --version {font_config.version} {_otf_path}")


def build_mono_autohint(f: str, font_config: FontConfig, build_option: BuildOption):
    style_compact = f.split("-")[-1].split(".")[0]
    postscript_name = f"{font_config.family_name_compact}-{style_compact}"
    print(f"👉 Auto hint {postscript_name}.ttf")

    source_path = joinPaths(build_option.output_ttf, f)
    font = TTFont(source_path)
    is_italic = "Italic" in style_compact
    font_config.patch_font_feature(
        font=font,
        issue_fea_dir=build_option.output_dir,
        is_italic=is_italic,
        is_cn=False,
        is_variable=False,
        is_hinted=True,
        fea_path=build_option.get_feature_file_path(is_italic),
    )

    param: dict | None = font_config.ttfautohint_param

    buf = BytesIO()
    font.save(buf)
    font.close()

    # https://freetype.org/ttfautohint/doc/ttfautohint.html#options
    # Also see `ttfautohint.options.USER_OPTIONS`
    options = {
        "in_buffer": buf.getvalue(),
        "reference_file": joinPaths(
            build_option.output_ttf, f"{font_config.family_name_compact}-Regular.ttf"
        ),
        "out_file": joinPaths(build_option.output_ttf_hinted, f"{postscript_name}.ttf"),
    }

    def parse_stem_width_mode(mode: str) -> StemWidthMode:
        if mode == "natural":
            return StemWidthMode.NATURAL
        elif mode == "strong":
            return StemWidthMode.STRONG
        elif mode == "quantized":
            return StemWidthMode.QUANTIZED
        else:
            raise ValueError(f"Unknown stem width mode: {mode}")

    if param:
        options.update(param)
        if "stem_width_mode" in param:
            del options["stem_width_mode"]
            if "gray" in param:
                options["gray_stem_width_mode"] = parse_stem_width_mode(
                    param["stem_width_mode"]["gray"]
                )
            if "gdi_cleartype" in param:
                options["gdi_cleartype_stem_width_mode"] = parse_stem_width_mode(
                    param["stem_width_mode"]["gdi_cleartype"]
                )
            if "dw_cleartype" in param:
                options["dw_cleartype_stem_width_mode"] = parse_stem_width_mode(
                    param["stem_width_mode"]["dw_cleartype"]
                )

    ttfautohint(**options)


def build_nf_by_prebuild_nerd_font(
    font_basename: str, font_config: FontConfig, build_option: BuildOption
) -> TTFont:
    suffix = font_config.get_nf_suffix()
    if suffix:
        suffix = "-" + suffix
    return merge_ttfonts(
        base_font_path=joinPaths(build_option.ttf_base_dir, font_basename),
        extra_font_path=f"{build_option.src_dir}/MapleMono-NF-Base{suffix}.ttf",
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

    if font_config.nerd_font["propo"]:
        _nf_args += ["--variable-width-glyphs"]
    elif font_config.nerd_font["mono"]:
        _nf_args += ["--mono"]

    extra_args = font_config.nerd_font["extra_args"]
    _nf_args += extra_args

    run(_nf_args + [joinPaths(build_option.ttf_base_dir, font_basename)])

    nf_file_name = "NerdFont" + font_config.get_nf_suffix()

    _path = joinPaths(
        build_option.output_nf, font_basename.replace("-", f"{nf_file_name}-")
    )
    font = TTFont(_path)
    remove(_path)

    # Check if the glyph 'nonmarkingreturn' exists in the font
    extra_name = "nonmarkingreturn"
    if extra_name in font.getGlyphNames():
        font["hmtx"][extra_name] = (600, 0)  # type: ignore
    return font


def build_nf(
    f: str,
    get_ttfont: Callable[[str, FontConfig, BuildOption], TTFont],
    font_config: FontConfig,
    build_option: BuildOption,
):
    print(f"👉 NerdFont{font_config.get_nf_suffix()} version for {f}")
    nf_font = get_ttfont(f, font_config, build_option)

    # format font name
    style_compact_nf = f.split("-")[-1].split(".")[0]

    style_nf_with_prefix_space, style_in_2, style_in_17, is_skip_sufamily, _ = (
        parse_style_name(
            style_name_compact=style_compact_nf,
            skip_subfamily_list=build_option.base_subfamily_list,
        )
    )

    nf_sym = f"NF{font_config.get_nf_suffix()}"
    postscript_name = f"{font_config.family_name_compact}-{nf_sym}-{style_compact_nf}"

    update_font_names(
        font=nf_font,
        family_name=f"{font_config.family_name} {nf_sym}{style_nf_with_prefix_space}",
        style_name=style_in_2,
        full_name=f"{font_config.family_name} {nf_sym} {style_in_17}",
        version_str=font_config.version_str,
        postscript_name=postscript_name,
        unique_identifier=get_unique_identifier(
            font_config=font_config,
            postscript_name=postscript_name,
        ),
        is_skip_subfamily=is_skip_sufamily,
        preferred_family_name=f"{font_config.family_name} {nf_sym}",
        preferred_style_name=style_in_17,
    )

    if font_config.line_height != 1:
        adjust_line_height(
            nf_font, font_config.line_height, font_config.vertical_metric
        )

    if not (
        build_option.should_use_font_patcher(font_config)
        or font_config.get_nf_suffix() == "Propo"
    ):
        verify_glyph_width(
            font=nf_font,
            expect_widths=font_config.get_valid_glyph_width_list(),
            file_name=postscript_name,
        )

    target_path = joinPaths(
        build_option.output_nf,
        f"{postscript_name}.ttf",
    )
    nf_font.save(target_path)
    nf_font.close()


def build_cn(f: str, font_config: FontConfig, build_option: BuildOption):
    style_compact_cn = f.split("-")[-1].split(".")[0]

    print(f"👉 {build_option.cn_suffix_compact} version for {f}")

    cn_font = merge_ttfonts(
        base_font_path=joinPaths(build_option.cn_base_font_dir, f),
        extra_font_path=joinPaths(
            build_option.cn_static_dir, f"MapleMonoCN-{style_compact_cn}.ttf"
        ),
        use_pyftmerge=True,
    )

    (
        style_cn_with_prefix_space,
        style_in_2,
        style_in_17,
        is_skip_subfamily,
        is_italic,
    ) = parse_style_name(
        style_name_compact=style_compact_cn,
        skip_subfamily_list=build_option.base_subfamily_list,
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

    cn_font["OS/2"].xAvgCharWidth = 600  # type: ignore

    # https://github.com/subframe7536/maple-font/issues/188
    # https://github.com/subframe7536/maple-font/issues/313
    # fix_cn_cv(cn_font)

    font_config.patch_font_feature(
        font=cn_font,
        issue_fea_dir=build_option.output_dir,
        is_italic=is_italic,
        is_cn=True,
        is_variable=False,
        is_hinted=font_config.use_hinted,
        fea_path=build_option.get_feature_file_path(is_italic, True),
    )

    target_width = (
        font_config.glyph_width_cn_narrow if font_config.cn["narrow"] else None
    )
    scale_factor: tuple[float, float] | None = (
        font_config.cn["scale_factor"]
        if font_config.cn["scale_factor"] != (1.0, 1.0)
        else None
    )
    if target_width or scale_factor:
        match_width = 2 * font_config.glyph_width

        # Change glyph width and keep monospace identifier will cause
        # Intellij IDEA / Windows Notepad and other applications to
        # render the font incorrectly. See details in #249
        if target_width:
            cn_font["post"].isFixedPitch = False  # type: ignore
            cn_font["OS/2"].panose.bProportion = 0  # type: ignore
            cn_font["OS/2"].panose.bSpacing = 0  # type: ignore
            cn_font["hhea"].advanceWidthMax = target_width  # type: ignore
            print(
                "Changed CN glyph width, mark font file as not monospaced and skip checking glyph width"
            )
        else:
            target_width = match_width

        if scale_factor:
            print(f"Scale CN / JP glyph to ({scale_factor[0]}x, {scale_factor[1]}x)")
        else:
            scale_factor = (1.0, 1.0)

        change_glyph_width_or_scale(
            font=cn_font,
            match_width=match_width,
            target_width=target_width,
            scale_factor=scale_factor,
            skip_name=["ellipsis.full"],
        )

    # https://github.com/subframe7536/maple-font/issues/239
    # already removed at merge time
    # remove_locl(font)

    if font_config.cn["fix_meta_table"]:
        # add code page, Latin / Japanese / Simplify Chinese / Traditional Chinese
        cn_font["OS/2"].ulCodePageRange1 = 1 << 0 | 1 << 17 | 1 << 18 | 1 << 20  # type: ignore

        # fix meta table, https://learn.microsoft.com/en-us/typography/opentype/spec/meta
        meta = newTable("meta")
        meta.data = {
            "dlng": "Latn, Hans, Hant, Jpan",
            "slng": "Latn, Hans, Hant, Jpan",
        }
        cn_font["meta"] = meta

    adjust_line_height(cn_font, font_config.line_height, font_config.vertical_metric)

    if not (
        (
            font_config.should_build_nf_cn()
            and (
                build_option.should_use_font_patcher(font_config)
                or font_config.get_nf_suffix() == "Propo"
            )
        )
        or target_width
    ):
        verify_glyph_width(
            font=cn_font,
            expect_widths=font_config.get_valid_glyph_width_list(True),
            file_name=postscript_name,
        )

    target_path = joinPaths(
        build_option.output_cn,
        f"{postscript_name}.ttf",
    )
    cn_font.save(target_path)
    cn_font.close()


def run_build(
    pool_size: int, fn: Callable, dir: str, target_styles: list[str] | None = None
):
    """Run build tasks in parallel using ProcessPoolExecutor."""
    if target_styles:
        files = []
        for f in listdir(dir):
            if f.split("-")[-1][:-4] in target_styles:
                files.append(f)
            elif "NF" not in f:
                remove(joinPaths(dir, f))
    else:
        files = listdir(dir)

    if pool_size <= 1:
        for f in files:
            fn(f)
        return

    first_exc: Exception | None = None
    with ProcessPoolExecutor(max_workers=pool_size) as executor:
        futures = {executor.submit(fn, f): f for f in files}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                # Optionally, cancel other futures if needed
                for f in futures:
                    if not f.done():
                        f.cancel()
                if not first_exc:
                    first_exc = e
                    raise e


def build_variable_fonts(font_config: FontConfig, build_option: BuildOption):
    """Build variable font versions from source files."""
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

        # Fix #682
        expand_custom_tag_bg(font=font)

        is_italic = "Italic" in input_file

        font_config.patch_font_feature(
            font=font,
            issue_fea_dir=build_option.output_dir,
            is_italic=is_italic,
            is_cn=False,
            is_variable=True,
            is_hinted=False,
            fea_path=build_option.get_feature_file_path(is_italic),
        )

        style_name = "Italic" if is_italic else "Regular"
        postscript_name = f"{font_config.family_name_compact}-{style_name}"
        update_font_names(
            font=font,
            family_name=font_config.family_name,
            style_name=style_name,
            full_name=f"{font_config.family_name} {style_name}",
            version_str=font_config.version_str,
            postscript_name=postscript_name,
            unique_identifier=get_unique_identifier(
                font_config=font_config,
                postscript_name=postscript_name,
                variable=True,
            ),
            is_skip_subfamily=True,
        )

        if is_italic:
            add_ital_axis_to_stat(font)

        patch_instance(font, font_config.weight_mapping)

        if font_config.line_height != 1:
            calculated_metric = (font["hhea"].ascender, font["hhea"].descender)  # type: ignore
            if calculated_metric != font_config.vertical_metric:
                font_config.vertical_metric = calculated_metric

            adjust_line_height(font, font_config.line_height, calculated_metric)

        verify_glyph_width(
            font=font,
            expect_widths=font_config.get_valid_glyph_width_list(),
            file_name=basename,
        )

        add_gasp(font)

        file_name = font_config.family_name_compact
        if is_italic:
            file_name += "-Italic"

        font.save(joinPaths(build_option.output_variable, f"{file_name}[wght].ttf"))

    print("\n✨ Instatiate and optimize fonts...\n")

    print("Check and optimize variable fonts")
    run(f"ftcli fix italic-angle {build_option.output_variable}")
    run(f"ftcli fix monospace {build_option.output_variable}")
    # run(f"ftcli fix vertical-metrics {build_option.output_variable}")
    run(f"ftcli name del-mac-names -r {build_option.output_variable}")

    print("Instantiate TTF")
    run(
        f"ftcli converter var2static -out {build_option.output_ttf} {build_option.output_variable}"
    )


def build_base_fonts(
    font_config: FontConfig, build_option: BuildOption, target_styles: list[str] | None
):
    """Apply mono building and auto-hinting to static TTF fonts."""
    run_build(
        font_config.pool_size,
        partial(
            build_mono,
            font_config=font_config,
            build_option=build_option,
        ),
        build_option.output_ttf,
        target_styles,
    )

    run_build(
        font_config.pool_size,
        partial(
            build_mono_autohint,
            font_config=font_config,
            build_option=build_option,
        ),
        build_option.output_ttf,
        target_styles,
    )


def build_nerd_fonts(
    font_config: FontConfig, build_option: BuildOption, target_styles: list[str] | None
):
    """Build Nerd Font variants."""
    if not font_config.nerd_font["enable"]:
        return

    makedirs(build_option.output_nf, exist_ok=True)
    use_font_patcher = build_option.should_use_font_patcher(font_config)

    get_ttfont = (
        build_nf_by_font_patcher if use_font_patcher else build_nf_by_prebuild_nerd_font
    )

    _version = font_config.nerd_font["version"]
    print(
        f"\n🔧 Patch Nerd-Font v{_version} using {'Font Patcher' if use_font_patcher else 'prebuild base font'}...\n"
    )

    run_build(
        font_config.pool_size,
        partial(
            build_nf,
            get_ttfont=get_ttfont,
            font_config=font_config,
            build_option=build_option,
        ),
        build_option.ttf_base_dir,
        target_styles,
    )
    build_option.is_nf_built = True


def build_chinese_fonts(
    font_config: FontConfig, build_option: BuildOption, target_styles: list[str] | None
):
    """Build Chinese font variants."""
    if not build_option.should_build_cn(font_config):
        return

    def _build_cn(with_nf: bool = False):
        print(f"\n🔎 Build CN fonts {'with Nerd-Font' if with_nf else ''}...\n")
        makedirs(build_option.output_cn, exist_ok=True)

        run_build(
            font_config.pool_size,
            partial(
                build_cn,
                font_config=font_config,
                build_option=build_option,
            ),
            build_option.cn_base_font_dir,
            target_styles,
        )

        if font_config.cn["use_hinted"]:
            print("Auto hinting all glyphs")
            run(f"ftcli ttf autohint {build_option.output_cn}")

    _build_cn()

    if font_config.use_cn_both and font_config.toggle_nf_cn_config():
        build_option.load_cn_dir_and_suffix(font_config)
        _build_cn(True)

    build_option.is_cn_built = True


# Now, refactor the main function to use these
def main(args: list[str] | None = None, version: str | None = None):
    check_ftcli()
    parsed_args = parse_args(args)

    font_config = FontConfig(args=parsed_args, version=version)
    build_option = BuildOption(use_hinted=font_config.use_hinted)
    build_option.load_cn_dir_and_suffix(font_config)

    if parsed_args.dry:
        font_config.nerd_font["use_font_patcher"] = (
            build_option.should_use_font_patcher(config=font_config, should_exit=False)
        )
        if is_ci():
            print(json.dumps(font_config.__dict__, indent=4))
        else:
            print("font_config:", json.dumps(font_config.__dict__, indent=4))
            print("build_option:", json.dumps(build_option.__dict__, indent=4))
            print("parsed_args:", json.dumps(parsed_args.__dict__, indent=4))
        return

    should_use_cache = parsed_args.cache
    target_styles = (
        build_option.base_subfamily_list
        if parsed_args.least_styles or font_config.debug
        else None
    )

    if not should_use_cache:
        print("🧹 Clean cache...\n")
        shutil.rmtree(build_option.output_dir, ignore_errors=True)
        shutil.rmtree(build_option.output_woff2, ignore_errors=True)

    makedirs(build_option.output_dir, exist_ok=True)
    makedirs(build_option.output_variable, exist_ok=True)
    makedirs(build_option.output_ttf, exist_ok=True)
    makedirs(build_option.output_ttf_hinted, exist_ok=True)

    start_time = time.time()
    print(
        f"🚩 Start building {font_config.family_name} {font_config.version_str} ...\n"
    )

    # Build basic fonts if no cache
    if not should_use_cache or not build_option.has_cache:
        build_variable_fonts(font_config, build_option)
        build_base_fonts(font_config, build_option, target_styles)

    # Build variants
    build_nerd_fonts(font_config, build_option, target_styles)
    build_chinese_fonts(font_config, build_option, target_styles)

    # Write config
    with open(
        joinPaths(build_option.output_dir, "build-config.json"), "w", encoding="utf-8"
    ) as config_file:
        result = {
            "version": FONT_VERSION,
            "family_name": font_config.family_name,
            "weight_mapping": font_config.weight_mapping,
            "line_height": font_config.line_height,
            "use_hinted": font_config.use_hinted,
            "ligature": font_config.enable_ligature,
            "feature_freeze": font_config.feature_freeze,
            "nerd_font": font_config.nerd_font,
            "cn": font_config.cn,
        }
        del result["nerd_font"]["font_forge_bin"]
        del result["nerd_font"]["enable"]
        del result["cn"]["enable"]
        config_file.write(
            json.dumps(
                result,
                indent=4,
            )
        )

    # Archive if requested
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

            suffix = ""
            if f in ["CN", "NF", "NF-CN"]:
                if not font_config.use_hinted:
                    suffix = "-unhinted"
            else:
                if should_use_cache:
                    continue

            sha256, zip_file_name_without_ext = archive_fonts(
                family_name_compact=font_config.family_name_compact,
                suffix=suffix,
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

    # Finish
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
