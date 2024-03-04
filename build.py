import importlib.util
import platform
import shutil
import subprocess
from os import listdir, mkdir, path, remove
from urllib.request import urlopen
from zipfile import ZipFile
from fontTools.ttLib import TTFont

package_name = "foundryToolsCLI"
package_installed = importlib.util.find_spec(package_name) is not None

if not package_installed:
    print(
        f"{package_name} is not found. Please install it using `pip install foundryToolsCLI`"
    )
    exit(1)


def run(cli: str | list[str], extra_args: list[str] = []) -> None:
    subprocess.run(
        (cli.split(" ") if isinstance(cli, str) else cli) + extra_args, shell=True
    )


family_name = "Maple Mono"
family_name_compact = family_name.replace(" ", "")

input_files = [
    "src-font/MapleMono[wght]-VF.ttf",
    "src-font/MapleMono-Italic[wght]-VF.ttf",
]
output_dir = "fonts"
output_otf = path.join(output_dir, "otf")
output_ttf = path.join(output_dir, "ttf")
output_ttf_autohint = path.join(output_dir, "ttf-autohint")
output_variable = path.join(output_dir, "variable")
output_woff2 = "woff2"
output_nf = path.join(output_dir, "nf")

shutil.rmtree(output_dir, ignore_errors=True)
shutil.rmtree("woff2", ignore_errors=True)
mkdir(output_dir)
mkdir(output_variable)

for input_file in input_files:
    shutil.copy(input_file, output_variable)
    run(f"ftcli converter vf2i {input_file} -out {output_ttf}")

for f in listdir(output_ttf):
    _path = path.join(output_ttf, f)
    font = TTFont(_path)

    def set_name(name: str, id: int):
        font["name"].setName(name, nameID=id, platformID=3, platEncID=1, langID=0x409)
        font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)

    def del_name(id: int):
        font["name"].removeNames(nameID=id)

    style_name = f[10:-4]
    if style_name.endswith("Italic") and style_name[0] != "I":
        style_name = style_name[:-6] + " Italic"

    set_name(family_name, 1)
    set_name(style_name, 2)
    set_name(f"{family_name} {style_name}", 4)
    set_name(f"{family_name_compact}-{f[10:-4]}", 6)
    del_name(16)
    del_name(17)
    font.save(_path)
    font.close()

run(f"ftcli converter ttf2otf {output_ttf} -out {output_otf}")
run(f"ftcli converter ft2wf {output_ttf} -out {output_woff2} -f woff2")
run(f"ftcli ttf autohint {output_ttf} -out {output_ttf_autohint}")

if not path.exists("FontPatcher"):
    version = "3.1.1"
    url = f"https://github.com/ryanoasis/nerd-fonts/releases/download/v{version}/FontPatcher.zip"
    try:
        zip_path = "FontPatcher.zip"
        if not path.exists(zip_path):
            print(f"NerdFont Patcher does not exist, download from {url}")
            with urlopen(url) as response, open(zip_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("FontPatcher")
        remove(zip_path)
    except Exception as e:
        print(
            f"\nFail to get NerdFont Patcher. Please download it manually from {url}, then put downloaded 'FontPatcher.zip' into project's root and run this script again. \n\tError: {e}"
        )
        exit(1)

system = platform.uname()[0]
script_path = path.abspath(
    path.join(
        "scripts",
        f"generate-nerdfont{'-mac' if 'Darwin' in system else ''}.{'bat' if 'Windows' in system else 'sh'}",
    )
)

for f in listdir(output_ttf):
    print(f"generate NerdFont for {f}")
    run([script_path, f[:-4], "0", "1"])
    _path = path.join(output_nf, f.replace("-", "NerdFont-"))
    nf_font = TTFont(_path)

    def set_nf_name(name: str, id: int):
        nf_font["name"].setName(
            name, nameID=id, platformID=3, platEncID=1, langID=0x409
        )
        nf_font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)

    def del_nf_name(id: int):
        nf_font["name"].removeNames(nameID=id)

    set_nf_name(f"{family_name} NF", 1)
    style_name = f[10:-4]
    if style_name.endswith("Italic") and style_name[0] != "I":
        style_name = style_name[:-6] + " Italic"
    set_nf_name(style_name, 2)
    set_nf_name(f"{family_name} NF {style_name}", 4)
    set_nf_name(f"{family_name_compact}-NF-{f[10:-4]}", 6)
    del_nf_name(16)
    del_nf_name(17)
    nf_font.save(_path)
    nf_font.close()
    shutil.move(_path, path.join(output_nf, f.replace("-", "-NF-")))
