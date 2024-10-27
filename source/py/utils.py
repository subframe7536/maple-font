from os import environ, path, remove
import platform
import shutil
import subprocess
from urllib.request import urlopen
from zipfile import ZipFile
from fontTools.ttLib import TTFont


# run command
def run(cli: str | list[str], extra_args: list[str] = []):
    subprocess.run((cli.split(" ") if isinstance(cli, str) else cli) + extra_args)


def set_font_name(font: TTFont, name: str, id: int):
    font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)
    font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)


def get_font_name(font: TTFont, id: int) -> str:
    return (
        font["name"]
        .getName(nameID=id, platformID=3, platEncID=1, langID=0x409)
        .__str__()
    )


def del_font_name(font: TTFont, id: int):
    font["name"].removeNames(nameID=id)


def joinPaths(*args: list[str]) -> str:
    return "/".join(args)


def get_font_forge_bin():
    WIN_FONTFORGE_PATH = "C:/Program Files (x86)/FontForgeBuilds/bin/fontforge.exe"
    MAC_FONTFORGE_PATH = (
        "/Applications/FontForge.app/Contents/Resources/opt/local/bin/fontforge"
    )
    LINUX_FONTFORGE_PATH = "/usr/bin/fontforge"

    system_name = platform.uname()[0]

    if "Darwin" in system_name:
        return MAC_FONTFORGE_PATH
    elif "Windows" in system_name:
        return WIN_FONTFORGE_PATH
    else:
        return LINUX_FONTFORGE_PATH


def check_font_patcher(version: str, github_mirror: str = "github.com") -> bool:
    if path.exists("FontPatcher"):
        with open("FontPatcher/font-patcher", "r", encoding="utf-8") as f:
            if f"# Nerd Fonts Version: {version}" in f.read():
                return True
            else:
                print("FontPatcher version not match, delete it")
                shutil.rmtree("FontPatcher", ignore_errors=True)

    zip_path = "FontPatcher.zip"
    if not path.exists(zip_path):
        github = environ.get("GITHUB")  # custom github mirror, for CN users
        if not github:
            github = github_mirror
        url = f"https://{github}/ryanoasis/nerd-fonts/releases/download/v{version}/FontPatcher.zip"
        try:
            print(f"NerdFont Patcher does not exist, download from {url}")
            with urlopen(url) as response, open(zip_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
        except Exception as e:
            print(
                f"\nFail to download NerdFont Patcher. Please download it manually from {url}, then put downloaded 'FontPatcher.zip' into project's root and run this script again. \n    Error: {e}"
            )
            exit(1)

    with ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall("FontPatcher")
    remove(zip_path)
    return True