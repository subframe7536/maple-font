from os import environ, path, remove
import platform
import shutil
import subprocess
from urllib.request import Request, urlopen
from zipfile import ZipFile
from fontTools.ttLib import TTFont
from glyphsLib import GSFont


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


def run(command, extra_args=None, log=not is_ci()):
    """
    Run a command line interface (CLI) command.
    """
    if extra_args is None:
        extra_args = []
    if isinstance(command, str):
        command = command.split()
    subprocess.run(command + extra_args, stdout=subprocess.DEVNULL if not log else None)


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

    result = ""
    if "Darwin" in system_name:
        result = MAC_FONTFORGE_PATH
    elif "Windows" in system_name:
        result = WIN_FONTFORGE_PATH
    else:
        result = LINUX_FONTFORGE_PATH

    if not path.exists(result):
        result = shutil.which("fontforge")

    return result


def parse_github_mirror(github_mirror: str) -> str:
    github = environ.get("GITHUB")  # custom github mirror, for CN users
    if not github:
        github = github_mirror
    return f"https://{github}"


def download_file(url: str, target_path: str):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    req = Request(url, headers={"User-Agent": user_agent})
    not_ci = not is_ci()
    with urlopen(req) as response, open(target_path, "wb") as out_file:
        total_size = int(response.getheader("Content-Length").strip())
        downloaded_size = 0
        block_size = 8192

        while True:
            buffer = response.read(block_size)
            if not buffer:
                break

            out_file.write(buffer)

            if not_ci:
                downloaded_size += len(buffer)
                percent_downloaded = (downloaded_size / total_size) * 100
                print(
                    f"Downloading: [{percent_downloaded:.2f}%] {downloaded_size} / {total_size}",
                    end="\r",
                )


def download_zip_and_extract(
    name: str, url: str, zip_path: str, output_dir: str, remove_zip: bool = False
) -> bool:
    if not path.exists(zip_path):
        print(f"{name} does not exist, download from {url}")
        try:
            download_file(url, target_path=zip_path)
        except Exception as e:
            print(
                f"\nFail to download {name}. Please check your internet connection or download it manually from {url}, then put downloaded zip into project's root and run this script again. \n    Error: {e}"
            )
            return False
    try:
        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        if remove_zip:
            remove(zip_path)
        return True
    except Exception as e:
        print(f"Fail to extract {name}. Error: {e}")
        return False


def check_font_patcher(
    version: str, github_mirror: str = "github.com", target_dir: str = "FontPatcher"
) -> bool:
    bin_path = f"{target_dir}/font-patcher"
    if path.exists(target_dir):
        with open(bin_path, "r", encoding="utf-8") as f:
            if f"# Nerd Fonts Version: {version}" in f.read():
                return True
            else:
                print("FontPatcher version not match, delete it")
                shutil.rmtree("FontPatcher", ignore_errors=True)

    zip_path = "FontPatcher.zip"
    url = f"https://{github_mirror}/ryanoasis/nerd-fonts/releases/download/v{version}/{zip_path}"
    if not download_zip_and_extract(
        name="Nerd Font Patcher", url=url, zip_path=zip_path, output_dir=target_dir
    ):
        return False

    with open(bin_path, "r", encoding="utf-8") as f:
        if f"# Nerd Fonts Version: {version}" in f.read():
            return True

    print(f"FontPatcher version is not {version}, please download it from {url}")
    return False


def download_cn_base_font(
    tag: str, zip_path: str, target_dir: str, github_mirror: str = "github.com"
) -> bool:
    url = f"https://{github_mirror}/subframe7536/maple-font/releases/download/{tag}/{zip_path}"
    return download_zip_and_extract(
        name=f"{'Static' if 'static' in zip_path else 'Variable'} CN Base Font",
        url=url,
        zip_path=zip_path,
        output_dir=target_dir,
    )


def match_unicode_names(file_path: str) -> dict[str, str]:
    font = GSFont(file_path)
    result = {}

    for glyph in font.glyphs:
        glyph_name = glyph.name
        unicode_values = glyph.unicode

        if glyph_name and unicode_values:
            unicode_str = f"uni{''.join(unicode_values).upper().zfill(4)}"
            result[unicode_str] = glyph_name

    return result


def check_glyph_width(font: TTFont, matched_width: tuple[int]):
    print("Checking glyph width...")
    result: tuple[str, int] = []
    for name in font.getGlyphOrder():
        width, _ = font["hmtx"][name]
        if width not in matched_width:
            result.append([name, width])

    if result.__len__() > 0:
        print("Exist unmatched width:")
        for item in result:
            print(f"{item[0]}\t{item[1]}")
        raise Exception(
            f"The font may contain glyphs that are not {matched_width} wide, which may broke monospace rule."
        )