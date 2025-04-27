import hashlib
from os import environ, path, remove, walk
import sys
import shutil
import subprocess
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile
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
    subprocess.run(
        command + extra_args,
        stdout=subprocess.DEVNULL if not log else None,
        check=True,
    )


def set_font_name(font: TTFont, name: str, id: int):
    font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)  # type: ignore
    font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)  # type: ignore


def get_font_name(font: TTFont, id: int) -> str:
    return (
        font["name"]
        .getName(nameID=id, platformID=3, platEncID=1, langID=0x409)  # type: ignore
        .__str__()
    )


def del_font_name(font: TTFont, id: int):
    font["name"].removeNames(nameID=id)  # type: ignore


def joinPaths(*args: str) -> str:
    return "/".join(args)


def is_windows():
    return sys.platform == "win32"


def is_macos():
    return sys.platform == "darwin"


def get_font_forge_bin():
    WIN_FONTFORGE_PATH = "C:/Program Files (x86)/FontForgeBuilds/bin/fontforge.exe"
    MAC_FONTFORGE_PATH = (
        "/Applications/FontForge.app/Contents/Resources/opt/local/bin/fontforge"
    )
    LINUX_FONTFORGE_PATH = "/usr/bin/fontforge"

    result = ""
    if is_macos():
        result = MAC_FONTFORGE_PATH
    elif is_windows():
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


# https://github.com/subframe7536/maple-font/issues/314
def verify_glyph_width(
    font: TTFont, expect_widths: list[int], file_name: str | None = None
):
    print("Verify glyph width")
    result = []
    for name in font.getGlyphNames():
        width, _ = font["hmtx"][name]  # type: ignore
        if width not in expect_widths:
            result.append([name, width])

    if result.__len__() > 0:
        print(f"Every glyph's width should be in {expect_widths}, but these are not:")
        for item in result:
            print(f"{item[0]}  =>  {item[1]}")

        raise Exception(
            f"{file_name or 'The font'} may contain glyphs that width is not in {expect_widths}, which may broke monospace rule."
        )


def compress_folder(
    source_file_or_dir_path: str,
    target_parent_dir_path: str,
    family_name_compact: str,
    suffix: str,
    build_config_path: str,
) -> tuple[str, str]:
    """
    Archive folder and return sha1 and file name
    """
    source_folder_name = path.basename(source_file_or_dir_path)

    zip_name_without_ext = f"{family_name_compact}-{source_folder_name}{suffix}"

    zip_path = joinPaths(
        target_parent_dir_path,
        f"{zip_name_without_ext}.zip",
    )

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=5) as zip_file:
        for root, _, files in walk(source_file_or_dir_path):
            for file in files:
                file_path = joinPaths(root, file)
                zip_file.write(
                    file_path, path.relpath(file_path, source_file_or_dir_path)
                )
        zip_file.write("OFL.txt", "LICENSE.txt")
        if not source_file_or_dir_path.endswith("Variable"):
            zip_file.write(
                build_config_path,
                "config.json",
            )

    zip_file.close()
    sha256 = hashlib.sha256()
    with open(zip_path, "rb") as zip_file:
        while True:
            data = zip_file.read(1024)
            if not data:
                break
            sha256.update(data)

    return sha256.hexdigest(), zip_name_without_ext


def get_directory_hash(dir_path: str) -> str:
    hasher = hashlib.sha256()
    for root, _, files in sorted(walk(dir_path)):
        for file in sorted(files):
            file_path = path.join(root, file)
            try:
                with open(file_path, "rb") as f:
                    while True:
                        # 4KB chunk size
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        hasher.update(chunk)

            except (IOError, OSError) as e:
                raise Exception(f"Error reading file: {file_path} - {e}")

    return hasher.hexdigest()


def check_directory_hash(dir_path: str) -> bool:
    if not path.exists(dir_path):
        print(f"{dir_path} not exist, skip computing hash")
        return False
    with open(f"{dir_path}.sha256", "r") as f:
        return f.readline() == get_directory_hash(dir_path)


def merge_ttfonts(base_font_path: str, extra_font_path: str) -> TTFont:
    """
    Merge glyphs from ``source_font`` into ``base_font``, skipping duplicate glyph names.

    ``fontTools.merge.Merger`` will erase the glyph names, so merge them manually

    Args:
        base_font (TTFont): The base font to merge into
        source_font (TTFont): The font to merge from

    Returns:
        TTFont: The modified base_font with merged glyphs
    """
    try:
        base_font = TTFont(base_font_path)
        extra_font = TTFont(extra_font_path)
        # Get glyph tables and orders
        base_glyf = base_font["glyf"]
        extra_glyf = extra_font["glyf"]
        base_glyph_order = base_font.getGlyphOrder()
        extra_glyph_order = extra_font.getGlyphOrder()

        base_hmtx = base_font["hmtx"] if "hmtx" in base_font else None
        extra_hmtx = extra_font["hmtx"] if "hmtx" in extra_font else None

        base_glyph_names = set(base_glyph_order)

        glyphs_to_add = []

        for glyph_name in extra_glyph_order:
            if glyph_name not in base_glyph_names:
                # Copy glyph from source
                base_glyf.glyphs[glyph_name] = extra_glyf.glyphs[glyph_name]  # type: ignore

                # Copy metrics if hmtx tables exist
                if base_hmtx and extra_hmtx and glyph_name in extra_hmtx.metrics:  # type: ignore
                    base_hmtx.metrics[glyph_name] = extra_hmtx.metrics[glyph_name]  # type: ignore
                elif base_hmtx:
                    # Fallback: use default metrics if source doesn't have them
                    base_hmtx.metrics[glyph_name] = (0, 0)  # type: ignore # advanceWidth, lsb

                glyphs_to_add.append(glyph_name)

        if not glyphs_to_add:
            print("No new glyphs to merge")
            return base_font

        # Update glyph order
        updated_glyph_order = base_glyph_order + glyphs_to_add
        base_font.setGlyphOrder(updated_glyph_order)

        # Update maxp table
        base_font["maxp"].numGlyphs = len(updated_glyph_order)  # type: ignore

        # Update cmap if it exists
        if "cmap" in extra_font and "cmap" in base_font:
            base_cmap = base_font["cmap"].getBestCmap()  # type: ignore
            extra_cmap = extra_font["cmap"].getBestCmap()  # type: ignore
            if base_cmap and extra_cmap:
                for code, name in extra_cmap.items():
                    if name in glyphs_to_add and code not in base_cmap:
                        base_cmap[code] = name

        # Update hhea table if it exists
        if "hhea" in base_font:
            if base_hmtx:
                # Ensure hhea matches the number of hmtx entries
                base_font["hhea"].numberOfHMetrics = len(base_hmtx.metrics)  # type: ignore
            base_font["hhea"].recalc(base_font)  # type: ignore

        return base_font

    except Exception as e:
        print(f"Error merging fonts: {str(e)}")
        raise
