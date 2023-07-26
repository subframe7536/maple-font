from fontTools.ttLib import TTFont
from os import getcwd, path, listdir

root = getcwd()
ttx_path = path.join(root, "ttx")
sc_nf_path = path.join(path.dirname(root), "output", "SC-NF")

family_name = "Maple Mono"
family_name_trim = family_name.replace(" ", "")

for f in listdir(ttx_path):
    _, sub = f.split("-")
    print("fix", f"{family_name} SC NF {sub}")

    target = path.join(sc_nf_path, f"{family_name_trim}-SC-NF-{sub}.ttf")
    font = TTFont(target)

    def set_name(name: str, id: int):
        font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)
        font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)

    def get_name(id: int):
        return font["name"].getName(nameID=id, platformID=3, platEncID=1)

    def del_name(id: int):
        font["name"].removeNames(nameID=id)

    # correct names
    set_name(f"{family_name} SC NF", 1)
    set_name(sub, 2)
    set_name(f"{family_name} SC NF {sub}; {get_name(5)}", 3)
    set_name(f"{family_name} SC NF {sub}", 4)
    set_name(f"{family_name_trim}SCNF-{sub}", 6)

    font.importXML(path.join(ttx_path, f, f + ".O_S_2f_2.ttx"))

    # add code page, Latin / Japanese / Simplify Chinese / Traditional Chinese
    font["OS/2"].ulCodePageRange1 = 1 << 0 | 1 << 17 | 1 << 18 | 1 << 20

    font.save(target)
    font.close()
