from enum import Enum, unique
import hashlib
import importlib.util
import json
import platform
import shutil
import subprocess
from os import listdir, makedirs, path, remove, walk
from urllib.request import urlopen
from zipfile import ZIP_DEFLATED, ZipFile
from fontTools.ttLib import TTFont


@unique
class Status(Enum):
    DISABLE = "0"
    ENABLE = "1"
    IGNORE = "2"

# whether to archieve fonts
release_mode = True
# whether to build nerd font
build_nerd_font = True

build_config = {
    "family_name": "Maple Mono",
    "nerd_font": {
        # whether to make icon width fixed
        "mono": Status.DISABLE,
        # whether to generate Nerd Font patch based on hinted ttf
        "use_hinted": Status.ENABLE,
    },
}


package_name = "foundryToolsCLI"
package_installed = importlib.util.find_spec(package_name) is not None
family_name = build_config["family_name"]
family_name_compact = family_name.replace(" ", "")

if not package_installed:
    print(f"{package_name} is not found. Please run `pip install foundryToolsCLI`")
    exit(1)

# run command
def run(cli: str | list[str], extra_args: list[str] = []) -> None:
    subprocess.run(
        (cli.split(" ") if isinstance(cli, str) else cli) + extra_args, shell=True
    )


# compress folder and return sha1
def compress_folder(source_file_or_dir_path: str, target_parent_dir_path: str) -> str:
    source_folder_name = path.basename(source_file_or_dir_path)

    zip_path = path.join(target_parent_dir_path, f"{family_name_compact}-{source_folder_name}.zip")
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=5) as zip_file:
        for root, dirs, files in walk(source_file_or_dir_path):
            for file in files:
                file_path = path.join(root, file)
                zip_file.write(file_path, path.relpath(file_path, source_file_or_dir_path))
    zip_file.close()
    sha1 = hashlib.sha1()
    with open(zip_path, "rb") as zip_file:
        while True:
            data = zip_file.read(1024)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


input_files = [
    "src-font/MapleMono[wght]-VF.ttf",
    "src-font/MapleMono-Italic[wght]-VF.ttf",
]
output_dir = "fonts"
output_otf = path.join(output_dir, "otf")
output_ttf = path.join(output_dir, "ttf")
output_ttf_autohint = path.join(output_dir, "ttf-autohint")
output_variable = path.join(output_dir, "variable")
output_woff2 = path.join(output_dir, "woff2")
output_nf = path.join(output_dir, "nf")

shutil.rmtree(output_dir, ignore_errors=True)
shutil.rmtree("woff2", ignore_errors=True)
makedirs(output_dir)
makedirs(output_variable)

print("=== [build start] ===")

conf = json.dumps(
    build_config,
    default=lambda x: x.name if isinstance(x, Status) else None,
    indent=4,
)

print(conf)

for input_file in input_files:
    shutil.copy(input_file, output_variable)
    run(f"ftcli converter vf2i {input_file} -out {output_ttf}")

# fix font name
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

if build_nerd_font:
  for f in listdir(output_ttf):
      print(f"generate NerdFont for {f}")
      run(
          [
              script_path,
              f[:-4],
              build_config["nerd_font"]["mono"].value,
              build_config["nerd_font"]["use_hinted"].value,
          ]
      )

      # fix font name
      _path = path.join(output_nf, f.replace("-", "NerdFont-"))
      nf_font = TTFont(_path)

      def set_nf_name(name: str, id: int):
          nf_font["name"].setName(
              name, nameID=id, platformID=3, platEncID=1, langID=0x409
          )
          nf_font["name"].setName(name, nameID=id, platformID=1, platEncID=0, langID=0x0)

      def del_nf_name(id: int):
          nf_font["name"].removeNames(nameID=id)

      style_name = f[10:-4]
      if style_name.endswith("Italic") and style_name[0] != "I":
          style_name = style_name[:-6] + " Italic"

      set_nf_name(f"{family_name} NF", 1)
      set_nf_name(style_name, 2)
      set_nf_name(f"{family_name} NF {style_name}", 4)
      set_nf_name(f"{family_name_compact}-NF-{f[10:-4]}", 6)
      del_nf_name(16)
      del_nf_name(17)
      nf_font.save(_path)
      nf_font.close()

      # rename file name
      shutil.move(_path, path.join(output_nf, f.replace("-", "-NF-")))

# write config to output path
with open(path.join(output_dir, "build-config.json"), "w") as config_file:
    config_file.write(conf)

if release_mode:
    print("=== [Release Mode] ===")

    # archieve fonts
    release_dir = path.join(output_dir, "release")
    makedirs(release_dir)

    hash_map = {}

    for f in listdir(output_dir):
        if f == "release" or f.endswith(".json"):
            continue
        hash_map[f] = compress_folder(path.join(release_dir, f), release_dir)
        print(f"archieve: {f}")

    # write sha1
    with open(path.join(release_dir, "sha1.json"), "w") as hash_file:
        hash_file.write(json.dumps(hash_map, indent=4))

    shutil.rmtree("woff2", ignore_errors=True)
    shutil.copytree(output_woff2, "woff2")
    print("copy woff2 to root")
