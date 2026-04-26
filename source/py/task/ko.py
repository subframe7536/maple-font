from copy import deepcopy
from math import radians, tan
from os import listdir, makedirs, path
import shutil
from typing import Iterable
from zipfile import ZIP_BZIP2, ZipFile

from fontTools.misc.transform import Transform
from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from source.py.utils import download_file, get_directory_hash, joinPaths


NOTO_CJK_TAG = "Sans2.004"
NOTO_RAW_BASE = f"https://raw.githubusercontent.com/notofonts/noto-cjk/{NOTO_CJK_TAG}"

KO_SOURCE_FILES = {
    "NotoSansMonoCJKkr-VF.ttf": f"{NOTO_RAW_BASE}/Sans/Variable/TTF/Mono/NotoSansMonoCJKkr-VF.ttf",
    "NotoSansMonoCJKkr-Regular.otf": f"{NOTO_RAW_BASE}/Sans/Mono/NotoSansMonoCJKkr-Regular.otf",
    "NotoSansMonoCJKkr-Bold.otf": f"{NOTO_RAW_BASE}/Sans/Mono/NotoSansMonoCJKkr-Bold.otf",
}

STYLE_SPECS = [
    ("Thin", 100, False),
    ("ExtraLight", 200, False),
    ("Light", 300, False),
    ("Regular", 400, False),
    ("Medium", 500, False),
    ("SemiBold", 600, False),
    ("Bold", 700, False),
    ("ExtraBold", 800, False),
    ("ThinItalic", 100, True),
    ("ExtraLightItalic", 200, True),
    ("LightItalic", 300, True),
    ("Italic", 400, True),
    ("MediumItalic", 500, True),
    ("SemiBoldItalic", 600, True),
    ("BoldItalic", 700, True),
    ("ExtraBoldItalic", 800, True),
]

KO_UNICODE_RANGES = [
    (0x1100, 0x11FF),  # Hangul Jamo
    (0x2E80, 0x2EFF),  # CJK radicals supplement
    (0x2F00, 0x2FDF),  # Kangxi radicals
    (0x3000, 0x303F),  # CJK symbols and punctuation
    (0x3130, 0x318F),  # Hangul Compatibility Jamo
    (0x31C0, 0x31EF),  # CJK strokes
    (0x3200, 0x33FF),  # Enclosed/square CJK compatibility
    (0x3400, 0x4DBF),  # CJK Extension A
    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
    (0xA960, 0xA97F),  # Hangul Jamo Extended-A
    (0xAC00, 0xD7AF),  # Hangul Syllables
    (0xD7B0, 0xD7FF),  # Hangul Jamo Extended-B
    (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
    (0xFE10, 0xFE1F),  # Vertical forms
    (0xFE30, 0xFE4F),  # CJK compatibility forms
    (0xFF00, 0xFFEF),  # Halfwidth and fullwidth forms
]

TABLES_TO_DROP = [
    "avar",
    "BASE",
    "fvar",
    "gvar",
    "GDEF",
    "GPOS",
    "HVAR",
    "kern",
    "MVAR",
    "STAT",
    "vhea",
    "vmtx",
]

HANGUL_GSUB_FEATURES = {"ccmp", "ljmo", "vjmo", "tjmo"}


def _all_ko_unicodes() -> list[int]:
    result: list[int] = []
    for start, end in KO_UNICODE_RANGES:
        result.extend(range(start, end + 1))
    return result


def _archive(source: str, target: str, files: Iterable[str]):
    with ZipFile(target, "w", compression=ZIP_BZIP2, compresslevel=9) as zip_file:
        for file in files:
            file_path = joinPaths(source, file)
            if path.exists(file_path):
                zip_file.write(file_path, file)
    print(f"📦 Package {target}")


def _download_sources(ko_root: str):
    makedirs(ko_root, exist_ok=True)
    for filename, url in KO_SOURCE_FILES.items():
        target_path = joinPaths(ko_root, filename)
        if path.exists(target_path):
            print(f"✅ {filename} already exists")
            continue
        print(f"⬇️ Download {filename}")
        download_file(url, target_path)
        print("")


def _get_italic_angle() -> float:
    italic_vf = "source/MapleMono-Italic[wght]-VF.ttf"
    if not path.exists(italic_vf):
        return -11.0
    font = TTFont(italic_vf)
    angle = float(font["post"].italicAngle)  # type: ignore
    font.close()
    return angle or -11.0


def _subset_to_ko_ranges(font: TTFont):
    options = Options()
    # Preserve only the Hangul layout closure needed for modern Jamo composition.
    # Keeping every Noto CJK layout script pulls in too many glyphs for TTF maxp.
    options.layout_scripts = ["hang"]
    options.layout_features = ["ccmp", "ljmo", "vjmo", "tjmo"]
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.name_languages = ["*"]
    subsetter = Subsetter(options)
    subsetter.populate(unicodes=_all_ko_unicodes())
    subsetter.subset(font)


def _transform_glyph(glyph, glyf, transform: Transform):
    try:
        glyph.transform(transform, glyf)
        return
    except Exception:
        pass

    if glyph.isComposite():
        for component in glyph.components:
            if hasattr(component, "x"):
                component.x = int(round(component.x + transform.dx))
            if hasattr(component, "y"):
                component.y = int(round(component.y + transform.dy))
        glyph.recalcBounds(glyf)
        return

    if glyph.numberOfContours > 0:
        glyph.coordinates.transform(
            ((transform.xx, transform.xy), (transform.yx, transform.yy))
        )
        if transform.dx or transform.dy:
            glyph.coordinates.translate((transform.dx, transform.dy))
        glyph.coordinates.toInt()
        glyph.recalcBounds(glyf)


def _slant_font(font: TTFont, italic_angle: float):
    if "glyf" not in font:
        return

    shear = tan(radians(abs(italic_angle)))
    transform = Transform(1, 0, shear, 1, 0, 0)
    glyf = font["glyf"]
    for glyph_name in font.getGlyphOrder():
        glyph = glyf[glyph_name]
        _transform_glyph(glyph, glyf, transform)

    font["post"].italicAngle = italic_angle  # type: ignore
    font["head"].macStyle |= 0b10  # type: ignore


def _normalize_width(font: TTFont, target_width: int = 1200):
    if "hmtx" not in font:
        return

    hmtx = font["hmtx"]
    glyf = font["glyf"] if "glyf" in font else None

    for glyph_name in font.getGlyphOrder():
        width, lsb = hmtx[glyph_name]
        if width == 0:
            continue

        new_lsb = lsb
        if glyf and glyph_name in glyf.glyphs:
            glyph = glyf[glyph_name]
            if glyph.numberOfContours > 0 or glyph.isComposite():
                glyph.recalcBounds(glyf)
                glyph_width = glyph.xMax - glyph.xMin
                dx = int(round((target_width - glyph_width) / 2 - glyph.xMin))
                if dx:
                    _transform_glyph(glyph, glyf, Transform(1, 0, 0, 1, dx, 0))
                    glyph.recalcBounds(glyf)
                new_lsb = glyph.xMin if hasattr(glyph, "xMin") else lsb

        hmtx[glyph_name] = (target_width, new_lsb)

    font["hhea"].advanceWidthMax = target_width  # type: ignore
    if "OS/2" in font:
        font["OS/2"].xAvgCharWidth = target_width  # type: ignore
        font["OS/2"].panose.bProportion = 9  # type: ignore
        font["OS/2"].panose.bSpacing = 9  # type: ignore
    if "post" in font:
        font["post"].isFixedPitch = True  # type: ignore


def _cleanup_tables(font: TTFont):
    # Keep GSUB: CoreText needs Noto's Hangul Jamo composition features
    # when macOS/APFS exposes Korean filenames as decomposed NFD text.
    for table in TABLES_TO_DROP:
        if table in font:
            del font[table]


def _remap_langsys_features(langsys, feature_index_map: dict[int, int]) -> None:
    feature_indices = [
        feature_index_map[index]
        for index in langsys.FeatureIndex
        if index in feature_index_map
    ]
    langsys.FeatureIndex = feature_indices
    langsys.FeatureCount = len(feature_indices)


def restore_hangul_gsub(target_font: TTFont, ko_static_font_path: str) -> None:
    source_font = TTFont(ko_static_font_path)
    try:
        if "GSUB" not in source_font or "GSUB" not in target_font:
            return

        source_gsub = source_font["GSUB"].table
        target_gsub = target_font["GSUB"].table

        source_hang_record = next(
            (
                record
                for record in source_gsub.ScriptList.ScriptRecord
                if record.ScriptTag == "hang"
            ),
            None,
        )
        if source_hang_record is None:
            return

        source_feature_records = source_gsub.FeatureList.FeatureRecord
        source_hang_indices: set[int] = set()
        langsys_list = []
        if source_hang_record.Script.DefaultLangSys:
            langsys_list.append(source_hang_record.Script.DefaultLangSys)
        langsys_list.extend(
            record.LangSys for record in source_hang_record.Script.LangSysRecord
        )
        for langsys in langsys_list:
            source_hang_indices.update(
                index
                for index in langsys.FeatureIndex
                if source_feature_records[index].FeatureTag in HANGUL_GSUB_FEATURES
            )

        if not source_hang_indices:
            return

        lookup_index_map: dict[int, int] = {}
        feature_index_map: dict[int, int] = {}

        for feature_index in sorted(source_hang_indices):
            feature_record = source_feature_records[feature_index]
            for lookup_index in feature_record.Feature.LookupListIndex:
                if lookup_index in lookup_index_map:
                    continue
                lookup_index_map[lookup_index] = len(target_gsub.LookupList.Lookup)
                target_gsub.LookupList.Lookup.append(
                    deepcopy(source_gsub.LookupList.Lookup[lookup_index])
                )
        target_gsub.LookupList.LookupCount = len(target_gsub.LookupList.Lookup)

        for feature_index in sorted(source_hang_indices):
            feature_record = deepcopy(source_feature_records[feature_index])
            feature_record.Feature.LookupListIndex = [
                lookup_index_map[index]
                for index in feature_record.Feature.LookupListIndex
                if index in lookup_index_map
            ]
            feature_record.Feature.LookupCount = len(
                feature_record.Feature.LookupListIndex
            )
            feature_index_map[feature_index] = len(
                target_gsub.FeatureList.FeatureRecord
            )
            target_gsub.FeatureList.FeatureRecord.append(feature_record)
        target_gsub.FeatureList.FeatureCount = len(target_gsub.FeatureList.FeatureRecord)

        hang_record = deepcopy(source_hang_record)
        if hang_record.Script.DefaultLangSys:
            _remap_langsys_features(hang_record.Script.DefaultLangSys, feature_index_map)
        for langsys_record in hang_record.Script.LangSysRecord:
            _remap_langsys_features(langsys_record.LangSys, feature_index_map)

        target_gsub.ScriptList.ScriptRecord = [
            record
            for record in target_gsub.ScriptList.ScriptRecord
            if record.ScriptTag != "hang"
        ]
        target_gsub.ScriptList.ScriptRecord.append(hang_record)
        target_gsub.ScriptList.ScriptRecord.sort(key=lambda record: record.ScriptTag)
        target_gsub.ScriptList.ScriptCount = len(target_gsub.ScriptList.ScriptRecord)
    finally:
        source_font.close()


def _instantiate_from_variable(vf_path: str, weight: int) -> TTFont:
    variable_font = TTFont(vf_path)
    return instantiateVariableFont(variable_font, {"wght": weight}, inplace=True)


def _load_fallback_static(ko_root: str, weight: int) -> TTFont:
    filename = (
        "NotoSansMonoCJKkr-Bold.otf"
        if weight >= 600
        else "NotoSansMonoCJKkr-Regular.otf"
    )
    return TTFont(joinPaths(ko_root, filename))


def _prepare_static_font(
    ko_root: str,
    style_name: str,
    weight: int,
    is_italic: bool,
    italic_angle: float,
) -> TTFont:
    vf_path = joinPaths(ko_root, "NotoSansMonoCJKkr-VF.ttf")
    try:
        if not path.exists(vf_path):
            raise FileNotFoundError(vf_path)
        font = _instantiate_from_variable(vf_path, weight)
    except Exception as e:
        print(f"⚠️ Variable instantiation failed for {style_name}: {e}")
        print("   Falling back to static Noto Sans Mono CJK KR Regular/Bold source")
        font = _load_fallback_static(ko_root, weight)

    _subset_to_ko_ranges(font)
    if is_italic:
        _slant_font(font, italic_angle)
    _normalize_width(font)
    _cleanup_tables(font)

    if "OS/2" in font:
        font["OS/2"].usWeightClass = weight  # type: ignore
        fs_selection = 0
        if is_italic:
            fs_selection |= 0x01
        if weight >= 600:
            fs_selection |= 0x20
        elif weight == 400 and not is_italic:
            fs_selection |= 0x40
        font["OS/2"].fsSelection = fs_selection  # type: ignore
    if "head" in font:
        mac_style = 0
        if weight >= 600:
            mac_style |= 0x01
        if is_italic:
            mac_style |= 0x02
        font["head"].macStyle = mac_style  # type: ignore

    return font


def _update_dir_hash(dir_path: str):
    with open(f"{dir_path}.sha256", "w") as f:
        f.write(get_directory_hash(dir_path))
        f.flush()
    print(f"#️⃣ Update {dir_path}.sha256")


def ko(ko_root: str, pull: bool = False, rebuild: bool = False):
    if pull:
        _download_sources(ko_root)
        return

    if not rebuild:
        print("❗ `--rebuild` is not enabled, exit")
        return

    print("🔨 Rebuilding KO static font...")
    _download_sources(ko_root)

    static_dir = joinPaths(ko_root, "static")
    shutil.rmtree(static_dir, ignore_errors=True)
    makedirs(static_dir, exist_ok=True)

    italic_angle = _get_italic_angle()
    for style_name, weight, is_italic in STYLE_SPECS:
        print(f"👉 Generate MapleMonoKO-{style_name}.ttf")
        font = _prepare_static_font(ko_root, style_name, weight, is_italic, italic_angle)
        font.save(joinPaths(static_dir, f"MapleMonoKO-{style_name}.ttf"))
        font.close()

    _update_dir_hash(static_dir)

    archive_base_dir = joinPaths(ko_root, "archive")
    shutil.rmtree(archive_base_dir, ignore_errors=True)
    makedirs(archive_base_dir)

    _archive(
        ko_root,
        joinPaths(archive_base_dir, "ko-source.zip"),
        KO_SOURCE_FILES.keys(),
    )
    _archive(
        static_dir,
        joinPaths(archive_base_dir, "ko-base-static.zip"),
        [f for f in listdir(static_dir) if f.endswith(".ttf")],
    )

    print("✅ KO rebuild complete.")
