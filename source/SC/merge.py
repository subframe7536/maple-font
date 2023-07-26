from os import getcwd, path, listdir, removedirs, makedirs
import sys

try:
    import fontforge
except ImportError:
    print(
        "fail to load fontforge module. On Windows, you can execute `fontforge-console.bat` first and then call this script"
    )
    sys.exit(1)


root = getcwd()
sc_path = path.join(root, "SC")
output_path = path.join(path.dirname(root), "output")
sc_nf_path = path.join(output_path, "SC-NF")

family_name = "Maple Mono SC NF"
file_name = "MapleMono-SC-NF"

if not path.exists(sc_nf_path):
    makedirs(sc_nf_path)


def get_subfamily_name(f: str):
    return f.split("-")[-1].split(".")[0]


def generate(f: str):
    sub = get_subfamily_name(f)
    nf = fontforge.open(path.join(output_path, "NF", f))
    sc = fontforge.open(path.join(root, "SC", f"{sub}.ttf"))

    for item in sc.glyphs():
        if item.unicode == -1:
            continue
        sc.selection.select(("more", None), item.unicode)
        nf.selection.select(("more", None), item.unicode)

    sc.copy()
    nf.paste()

    target = path.join(output_path, "SC-NF", f"{file_name}-{sub}.ttf")
    print(f"{target}")
    nf.generate(target)
    sc.close()
    nf.close()


for f in listdir(path.join(output_path, "NF")):
    if f.endswith(".ttf"):
        generate(f)
