from enum import Enum, unique
import json
from os import getcwd, path, listdir, makedirs
import sys

try:
    import fontforge
except ImportError:
    print(
        "fail to load fontforge module. On Windows, you can execute `fontforge-console.bat` first and then call this script"
    )
    sys.exit(1)

config = sys.argv[1]

if config not in ["ttf", "ttf-autohint", "nf"] or config == "":
    print("config is incorrect or not set, switch to default 'nf'")
    config = "nf"

suffix = "SC-NF" if config == "nf" else "SC"
suffix_alt = suffix.replace("-", " ")

root = getcwd()
sc_path = path.join(root, "SC")
output_path = path.join(path.dirname(root), "output")
sc_nf_path = path.join(output_path, suffix)
base_font_path = path.join(output_path, config)

family_name = f"Maple Mono {suffix_alt}"
file_name = f"MapleMono-{suffix}"

if not path.exists(sc_nf_path):
    makedirs(sc_nf_path)


def get_subfamily_name(f: str):
    return f.split("-")[-1].split(".")[0]


def generate(f: str):
    sub = get_subfamily_name(f)
    nf = fontforge.open(path.join(base_font_path, f))
    sc = fontforge.open(path.join(root, "SC", f"{sub}.ttf"))

    for item in sc.glyphs():
        if item.unicode == -1:
            continue
        sc.selection.select(("more", None), item.unicode)
        nf.selection.select(("more", None), item.unicode)

    sc.copy()
    nf.paste()

    nf.generate(path.join(output_path, suffix, f"{file_name}-{sub}.ttf"))
    sc.close()
    nf.close()


with open(path.join(sc_nf_path, "sc-config.json"), "w") as f:
    c = {"base": ""}
    if config == "nf":
        c["base"] = "nerd font"
    elif config == "ttf-autohint":
        c["base"] = "autohint ttf"
    else:
        c["base"] = "ttf"
    f.write(json.dumps(c, indent=4))

for f in listdir(base_font_path):
    if f.endswith(".ttf"):
        print("generate:", f)
        generate(f)
