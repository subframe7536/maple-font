import json
from os import environ, path, remove
from urllib.request import urlopen
from fontTools.varLib import TTFont
from fontTools.subset import Subsetter

from source.py.utils import (
    check_font_patcher,
    del_font_name,
    get_font_forge_bin,
    set_font_name,
    run,
)

base_font_path = "fonts/TTF/MapleMono-Regular.ttf"
family_name = "Maple Mono"
font_forge_bin = get_font_forge_bin()

if not path.exists(base_font_path):
    print(
        "font not exist, please run this command first:\n\n    python build.py --ttf-only --no-nerd-font --least-styles\n"
    )
    exit(1)


def parse_codes_from_json(data) -> list[int]:
    """
    Load unicodes from `glyphnames.json`
    """
    try:
        codes = [
            int(f"0x{value['code']}", 16)
            for key, value in data.items()
            if isinstance(value, dict) and "code" in value
        ]

        return codes

    except json.JSONDecodeError:
        print("Invalide JSON")
        exit(1)


def update_config_json(config_path: str, version: str):
    with open(config_path, "r+", encoding="utf-8") as file:
        data = json.load(file)

        if "nerd_font" in data:
            data["nerd_font"]["version"] = version

        file.seek(0)
        json.dump(data, file, ensure_ascii=False, indent=2)


def check_update():
    current_version = None
    with open("./config.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        current_version = data["nerd_font"]["version"]

    latest_version = current_version
    print("Getting latest version from remote...")
    with urlopen(
        "https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest"
    ) as response:
        data = json.loads(response.read().decode("utf-8").split("\n")[0])
        for key in data:
            if key == "tag_name":
                latest_version = str(data[key])[1:]
                break

        if latest_version == current_version:
            print("✨ Current version match latest version")
            if not check_font_patcher(latest_version):
                print("Font-Patcher not exist and fail to download, exit")
                exit(1)
            return

        print(
            f"Current version {current_version} not match latest version {latest_version}, update"
        )
        if not check_font_patcher(latest_version, environ.get("GITHUB", "github.com")):
            print("Fail to update Font-Patcher, exit")
            exit(1)
        update_config_json("./config.json", latest_version)
        update_config_json("./source/preset-normal.json", latest_version)


def get_nerd_font_patcher_args(mono: bool, propo: bool = False):
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
    elif propo:
        _nf_args += ["--variable-width-glyphs"]

    return _nf_args


def get_font_suffix(mono: bool, propo: bool) -> str:
    """Determine the suffix for the font name and file path."""
    if mono and propo:
        raise ValueError(
            "Cannot build both `mono` and `propo` glyphs versions simultaneously."
        )
    if mono:
        return "Mono"
    elif propo:
        return "Propo"
    return ""


def build_nf(mono: bool, propo: bool = False):
    suffix = get_font_suffix(mono, propo)
    nf_args = get_nerd_font_patcher_args(mono, propo)

    nf_file_name = "NerdFont" + suffix
    style_name = "Regular"

    run(nf_args + [base_font_path])
    _path = f"{family_name.replace(' ', '')}{nf_file_name}-{style_name}.ttf"
    nf_font = TTFont(_path)
    remove(_path)

    # Set font names
    full_family_name = f"{family_name} NF Base{f' {suffix}' if suffix else ''}"
    set_font_name(nf_font, full_family_name, 1)
    set_font_name(nf_font, style_name, 2)
    set_font_name(nf_font, f"{full_family_name} {style_name}", 4)
    set_font_name(
        nf_font,
        f"{family_name.replace(' ', '-')}-NF-Base{f'-{suffix}' if suffix else ''}-{style_name}",
        6,
    )
    del_font_name(nf_font, 16)
    del_font_name(nf_font, 17)

    return nf_font


def subset(mono: bool, propo: bool, unicodes: list[int]):
    font = build_nf(mono, propo)
    subsetter = Subsetter()
    subsetter.populate(
        unicodes=unicodes,
    )
    subsetter.subset(font)

    suffix = get_font_suffix(mono, propo)
    _path = f"source/MapleMono-NF-Base{f'-{suffix}' if suffix else ''}.ttf"

    font.save(_path)
    # Apply monospace fix only for non-proportional versions
    if not propo:
        run(f"ftcli fix monospace {_path}")
    font.close()


def nerd_font(no_update: bool):
    if not no_update:
        check_update()

    with open("./FontPatcher/glyphnames.json", "r", encoding="utf-8") as f:
        unicodes = parse_codes_from_json(json.load(f))
        # Build Regular version
        subset(mono=False, propo=False, unicodes=unicodes)
        # Build Mono version
        subset(mono=True, propo=False, unicodes=unicodes)
        # Build Propo version
        subset(mono=False, propo=True, unicodes=unicodes)
