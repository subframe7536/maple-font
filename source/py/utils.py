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


def is_ci():
    ci_envs = [
        "JENKINS_HOME",
        "TRAVIS",
        "CIRCLECI",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "TF_BUILD",
    ]

    for env in ci_envs:
        if environ.get(env):
            return True

    return False


def parse_github_mirror(github_mirror: str) -> str:
    github = environ.get("GITHUB")  # custom github mirror, for CN users
    if not github:
        github = github_mirror
    return f"https://{github}"


def download_zip_and_extract(
    name: str, url: str, zip_path: str, output_dir: str, remove_zip: bool = True
) -> bool:
    try:
        if not path.exists(zip_path):
            try:
                print(f"NerdFont Patcher does not exist, download from {url}")
                with urlopen(url) as response, open(zip_path, "wb") as out_file:
                    shutil.copyfileobj(response, out_file)
            except Exception as e:
                print(
                    f"\nFail to download {name}. Please download it manually from {url}, then put downloaded file into project's root and run this script again. \n    Error: {e}"
                )
                return False
        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        if remove_zip:
            remove(zip_path)
        return True
    except Exception as e:
        print(f"Download zip and extract failed, error: {e}")
        return False


def check_font_patcher(version: str, github_mirror: str = "github.com") -> bool:
    target_dir = "FontPatcher"
    if path.exists(target_dir):
        with open(f"{target_dir}/font-patcher", "r", encoding="utf-8") as f:
            if f"# Nerd Fonts Version: {version}" in f.read():
                return True
            else:
                print("FontPatcher version not match, delete it")
                shutil.rmtree("FontPatcher", ignore_errors=True)

    zip_path = "FontPatcher.zip"
    url = f"{parse_github_mirror(github_mirror)}/ryanoasis/nerd-fonts/releases/download/v{version}/{zip_path}"
    return download_zip_and_extract(
        name="Nerd Font Patcher", url=url, zip_path=zip_path, output_dir=target_dir
    )


def download_cn_static_fonts(
    tag: str, target_dir: str, github_mirror: str = "github.com"
) -> bool:
    url = f"{parse_github_mirror(github_mirror)}/subframe7536/maple-font/releases/download/{tag}/cn-base.zip"
    zip_path = "cn-base-static.zip"
    return download_zip_and_extract(
        name="Nerd Font Patcher", url=url, zip_path=zip_path, output_dir=target_dir
    )
