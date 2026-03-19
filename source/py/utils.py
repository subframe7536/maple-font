import hashlib
from os import environ, path, remove, walk
import sys
import shutil
import subprocess
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile
from fontTools.ttLib import TTFont, newTable
from fontTools.merge import Merger
from source.py.task._utils import is_ci, default_weight_map


def run(command: str | list[str], extra_args: list[str] | None = None, log=not is_ci()):
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
        stderr=subprocess.DEVNULL if not log else None,
        check=True,
    )


def set_font_name(font: TTFont, name: str, id: int, mac: bool | None = None):
    font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)  # type: ignore
    if mac:
        font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)  # type: ignore


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
                f"❗\nFail to download {name}. Please check your internet connection or download it manually from {url}, then put downloaded zip into project's root and run this script again. \n    Error: {e}"
            )
            return False
    try:
        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        if remove_zip:
            remove(zip_path)
        return True
    except Exception as e:
        print(f"❗Fail to extract {name}. Error: {e}")
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

    print(f"❗FontPatcher version is not {version}, please download it from {url}")
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
    try:
        from glyphsLib import GSFont
    except ImportError:
        print("❗ glyphsLib is not found. Please run `pip install glyphsLib`")
        exit(1)

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
    result = []
    for name in font.getGlyphNames():
        width, _ = font["hmtx"][name]  # type: ignore
        if width not in expect_widths:
            result.append([name, width])

    if result.__len__() == 0:
        print(f"✅ Verified glyph width in {file_name}")
        return

    unexpected_glyphs = "\n".join(
        [f"{item[0]}  =>  {item[1]}" for item in result[1:20]]
    )

    raise Exception(
        f"{file_name or 'The font'} may contains glyphs that width is not in {expect_widths}, which may broke monospace rule.\n{unexpected_glyphs}"
    )


def archive_fonts(
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


def merge_ttfonts(
    base_font_path: str, extra_font_path: str, use_pyftmerge: bool = False
) -> TTFont:
    """
    Merge glyphs from ``source_font`` into ``base_font``, skipping duplicate glyph names.

    ``fontTools.merge.Merger`` will erase the glyph names, so merge them manually

    Args:
        base_font (str): The base font path to merge into
        source_font (str): The font path to merge from
        use_pyftmerge (bool): Force to use pyftmerge

    Returns:
        TTFont: The modified base_font with merged glyphs
    """
    if use_pyftmerge:
        merger = Merger()
        return merger.merge([base_font_path, extra_font_path])

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


def add_ital_axis_to_stat(font: TTFont):
    """
    Add fake ``ital`` axis to append "italic" to subfamily name in italic variable font
    """
    from fontTools.ttLib.tables import otTables as ot

    name = font["name"]
    stat_table = font["STAT"].table  # type: ignore

    # Add fake axis name
    id = name._findUnusedNameID()  # type: ignore
    set_font_name(font, "Italic", id, True)

    # Add AxisRecord
    axis = ot.AxisRecord()  # type: ignore
    axis.AxisTag = "ital"
    axis.AxisOrdering = len(stat_table.DesignAxisRecord.Axis)
    axis.AxisNameID = id
    stat_table.DesignAxisRecord.Axis.append(axis)
    stat_table.DesignAxisCount += 1

    # Add AxisValue
    axisValRec = ot.AxisValue()  # type: ignore
    axisValRec.AxisIndex = axis.AxisOrdering
    axisValRec.Flags = 0
    axisValRec.Format = 1
    axisValRec.ValueNameID = id
    axisValRec.Value = 1.0
    stat_table.AxisValueArray.AxisValue.append(axisValRec)
    stat_table.AxisValueCount += 1


def adjust_line_height(
    font: TTFont, factor: float, metric: tuple[float, float]
) -> None:
    """
    Adjust the line height of the font by modifying the hhea and OS/2 table.
    """

    if "hhea" not in font:
        raise ValueError("No hhea table found.")
    if "OS/2" not in font:
        raise ValueError("No OS/2 table found.")

    head = font["head"]
    hhea = font["hhea"]
    os2 = font["OS/2"]

    asc, desc = metric
    # Maintain original ascender/descender ratio
    ascender_ratio = asc / (asc - desc)  # type: ignore
    # Calculate target total height
    target_total_height = int(round(factor * (asc - desc)))

    # Calculate new metrics
    new_ascender = int(round(target_total_height * ascender_ratio))
    new_descender = new_ascender - target_total_height

    print(f"Change vertical metric to [{new_ascender}, {new_descender}]")

    # Apply changes to hhea table
    head.yMax = new_ascender  # type: ignore
    head.yMin = new_descender  # type: ignore
    hhea.ascent = new_ascender  # type: ignore
    hhea.descent = new_descender  # type: ignore
    os2.sTypoAscender = new_ascender  # type: ignore
    os2.sTypoDescender = new_descender  # type: ignore
    os2.usWinAscent = new_ascender  # type: ignore
    os2.usWinDescent = -new_descender  # type: ignore


def patch_instance(font: TTFont, all_weight_map: dict[str, int]):
    if all_weight_map == default_weight_map:
        print("Skip weight remapping since nothing changed.")
        return

    if "fvar" not in font or "STAT" not in font:
        return

    if all_weight_map["thin"] != 100:
        raise Exception("Font weight of `thin` must be 100")

    if all_weight_map["extrabold"] != 800:
        raise Exception("Font weight of `extrabold` must be 800")

    value_to_name = {v: k for k, v in default_weight_map.items()}

    for instance in font["fvar"].instances:  # type: ignore
        current_weight = int(instance.coordinates["wght"])
        weight_name = value_to_name.get(current_weight)
        if weight_name and weight_name in all_weight_map:
            instance.coordinates["wght"] = all_weight_map[weight_name]

    axes = font["fvar"].axes  # type: ignore
    wght_index = next((i for i, ax in enumerate(axes) if ax.axisTag == "wght"), None)
    if wght_index is None:
        return

    stat = font["STAT"].table  # type: ignore
    if not stat.AxisValueArray:
        return

    handlers = {
        1: lambda av: patch_single_value(av, "Value"),
        2: lambda av: patch_range_value(av),
        3: lambda av: (
            patch_single_value(av, "Value"),
            patch_single_value(av, "LinkedValue"),
        ),
        4: lambda av: [
            patch_single_value(rec, "Value")
            for rec in av.AxisValueRecord
            if rec.AxisIndex == wght_index
        ],
    }

    def patch_single_value(obj, attr: str) -> None:
        current_value = int(getattr(obj, attr))
        weight_name = value_to_name.get(current_value)
        if weight_name and weight_name in all_weight_map:
            setattr(obj, attr, all_weight_map[weight_name])

    def patch_range_value(av) -> None:
        current_value = int(av.NominalValue)
        weight_name = value_to_name.get(current_value)
        if weight_name and weight_name in all_weight_map:
            new_value = all_weight_map[weight_name]
            delta = new_value - av.NominalValue
            av.RangeMinValue += delta
            av.RangeMaxValue += delta
            av.NominalValue = new_value

    for av in stat.AxisValueArray.AxisValue:
        fmt = av.Format
        if fmt not in handlers or (fmt != 4 and av.AxisIndex != wght_index):
            continue
        handlers[fmt](av)


def add_gasp(font: TTFont):
    print("Fix GASP table")
    gasp = newTable("gasp")
    gasp.gaspRange = {65535: 15}  # type: ignore
    font["gasp"] = gasp


def remove_target_glyph(font: TTFont, glyph_name_suffix: str):
    """
    Remove glyphs from the font that end with the specified suffix.
    """
    from fontTools.subset import Subsetter, Options

    keep_glyphs = [n for n in font.getGlyphOrder() if not n.endswith(glyph_name_suffix)]
    subsetter = Subsetter(Options(hinting=False))
    subsetter.populate(glyphs=keep_glyphs)
    subsetter.subset(font)


def parse_style_name(style_name_compact: str):
    is_italic = style_name_compact.endswith("Italic")

    _style_name = style_name_compact
    if is_italic and style_name_compact[0] != "I":
        _style_name = style_name_compact[:-6] + " Italic"

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
    base_subfamily_list = ["Regular", "Bold", "Italic", "BoldItalic"]
    if style_name_compact in base_subfamily_list:
        return "", _style_name, _style_name, True, is_italic
    else:
        return (
            " " + style_name_compact.replace("Italic", ""),
            "Italic" if is_italic else "Regular",
            _style_name,
            False,
            is_italic,
        )


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
    font["name"].removeNames(platformID=1)  # type: ignore
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


DEFAULT_COMPAT_ALIASES: dict[int, int] = {
    0x2126: 0x03A9,  # Ω → Ω
    0x212A: 0x004B,  # K → K
    0x212B: 0x00C5,  # Å → Å
}


def alias_codepoints(font: TTFont, mapping: dict[int, int] | None = None):
    """
    Add cmap aliases: src_codepoint → dst_codepoint
    """
    if mapping is None:
        mapping = DEFAULT_COMPAT_ALIASES

    cmap_tables = font["cmap"].tables  # type: ignore

    dst_glyphs: dict[int, str] = {}
    for src, dst in mapping.items():
        glyph = None
        for table in cmap_tables:
            if not table.isUnicode():
                continue
            if dst in table.cmap:
                glyph = table.cmap[dst]
                break
        if glyph is None:
            continue
        dst_glyphs[src] = glyph

    for table in cmap_tables:
        if not table.isUnicode():
            continue
        cmap = table.cmap
        for src, glyph in dst_glyphs.items():
            cmap[src] = glyph
