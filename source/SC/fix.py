import sys
from fontTools.ttLib import TTFont, newTable
from os import getcwd, path, listdir


if len(sys.argv) < 4:
    print("配置不正确，将使用默认配置")
    base_font = "nf"
    fix_encoding_and_meta = True
    family_name = "Maple Mono"
else:
    base_font = sys.argv[1]
    fix_encoding_and_meta = sys.argv[2] == "1"
    family_name = sys.argv[3]

suffix = "SC-NF" if base_font == "nf" else "SC"
suffix_alt = suffix.replace("-", " ")

root = getcwd()
ttx_path = path.join(root, "ttx")
sc_nf_path = path.join(path.dirname(root), "output", suffix)

family_name_trim = family_name.replace(" ", "")

for f in listdir(ttx_path):
    _, sub = f.split("-")

    target = path.join(sc_nf_path, f"{family_name_trim}-{suffix}-{sub}.ttf")
    font = TTFont(target)

    def set_name(name: str, id: int):
        font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)
        font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)

    def get_name(id: int):
        return font["name"].getName(nameID=id, platformID=3, platEncID=1)

    def del_name(id: int):
        font["name"].removeNames(nameID=id)

    # correct names
    set_name(f"{family_name} {suffix_alt}", 1)
    set_name(sub, 2)
    set_name(f"{family_name} {suffix_alt} {sub}; {get_name(5)}", 3)
    set_name(f"{family_name} {suffix_alt} {sub}", 4)
    set_name(f"{family_name_trim}{suffix.replace('-', '')}-{sub}", 6)

    font.importXML(path.join(ttx_path, f, f + ".O_S_2f_2.ttx"))

    if fix_encoding_and_meta:
        # add code page, Latin / Japanese / Simplify Chinese / Traditional Chinese
        font["OS/2"].ulCodePageRange1 = 1 << 0 | 1 << 17 | 1 << 18 | 1 << 20

        # fix meta table, https://learn.microsoft.com/en-us/typography/opentype/spec/meta
        meta = newTable("meta")
        meta.data = {
            "dlng": "Latn, Hans, Hant, Jpan",
            "slng": "Latn, Hans, Hant, Jpan",
        }
        font["meta"] = meta

    font.save(target)
    font.close()
    print("fix:", f"{family_name} {suffix_alt} {sub}")
