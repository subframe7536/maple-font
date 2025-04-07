import json
import os
import re
import shutil
from typing import Callable
from fontTools.ttLib import TTFont
from source.py.utils import generate_directory_hash, run

# Mapping of style names to weights
weight_map = {
    "Thin": "100",
    "ExtraLight": "200",
    "Light": "300",
    "Regular": "400",
    "Italic": "400",
    "SemiBold": "500",
    "Medium": "600",
    "Bold": "700",
    "ExtraBold": "800",
}


def format_fontsource_name(filename: str):
    match = re.match(r"MapleMono-(.*)\.(.*)$", filename)

    if not match:
        return None

    style = match.group(1)

    weight = weight_map[style.removesuffix("Italic") if style != "Italic" else "Italic"]
    suf = "italic" if "italic" in filename.lower() else "normal"

    new_filename = f"maple-mono-latin-{weight}-{suf}.{match.group(2)}"
    return new_filename


def format_woff2_name(filename: str):
    return filename.replace(".woff2", "-VF.woff2")


def rename_files(dir: str, fn: Callable[[str], str | None]):
    for filename in os.listdir(dir):
        if not filename.endswith(".woff") and not filename.endswith(".woff2"):
            continue
        new_name = fn(filename)
        if new_name:
            os.rename(os.path.join(dir, filename), os.path.join(dir, new_name))
            print(f"Renamed: {filename} -> {new_name}")


def parse_tag(tag: str, beta: str):
    """
    Parse the tag from the command line arguments.
    Format: v7.0[-beta3]
    """

    if not tag.startswith("v"):
        tag = f"v{tag}"

    match = re.match(r"^v(\d+)\.(\d+)$", tag)
    if not match:
        raise ValueError(f"Invalid tag: {tag}, expected format: v7.0")

    major, minor = match.groups()
    # Remove leading zero from the minor version if necessary
    minor = str(int(minor))
    tag = f"v{major}.{minor}"

    if beta:
        tag += "-" if beta.startswith("beta") else "-beta" + beta

    return tag


def update_build_script_version(tag):
    with open("build.py", "r", encoding="utf-8") as f:
        content = f.read()
        f.close()
    content = re.sub(r'FONT_VERSION = ".*"', f'FONT_VERSION = "{tag}"', content)
    with open("build.py", "w", encoding="utf-8") as f:
        f.write(content)
        f.close()


def git_release_commit(tag, files):
    run(f"git add {' '.join(files)}")
    run(["git", "commit", "-m", f"Release {tag}"])
    run(f"git tag {tag}")
    print("Committed and tagged")

    run("git push origin")
    run(f"git push origin {tag}")
    print("Pushed to origin")


def update_submodule(cwd: str):
    run("git pull", cwd=cwd)
    run("git add .", cwd=cwd)
    run(["git", "commit", "-m", "Update font"], cwd=cwd)
    run("git push origin", cwd=cwd)
    print("Update page files")


def format_font_map_key(key: int) -> str:
    formatted_key = f"{key:05X}"
    if formatted_key.startswith("0"):
        return formatted_key[1:]
    return formatted_key


def write_unicode_map_json(font_path: str, output: str):
    font = TTFont(font_path)
    font_map = {
        format_font_map_key(k): v
        for k, v in font.getBestCmap().items()
        if k is not None
    }
    with open(output, "w", encoding="utf-8") as f:
        f.write(json.dumps(font_map, indent=2))
    print(f"Write font map to {output}")
    font.close()


def release(tag: str, beta: str, dry: bool):
    tag = parse_tag(tag, beta)
    # prompt and wait for user input
    choose = input(f"{'[DRY] ' if dry else ''}Tag {tag}? (Y or n) ")
    if choose != "" and choose.lower() != "y":
        print("Aborted")
        return
    update_build_script_version(tag)

    shutil.rmtree("./cdn", ignore_errors=True)
    target_fontsource_dir = "cdn/fontsource"
    run("python build.py --ttf-only --no-nerd-font --cn --no-hinted")
    run(f"ftcli converter ft2wf -f woff2 ./fonts/TTF -out {target_fontsource_dir}")
    run(f"ftcli converter ft2wf -f woff ./fonts/TTF -out {target_fontsource_dir}")
    rename_files(target_fontsource_dir, format_fontsource_name)
    print("Generate fontsource files")

    run(
        "uv export --format requirements-txt --no-hashes --output-file requirements.txt --quiet"
    )

    shutil.copytree("./fonts/CN", "./cdn/cn")
    print("Generate CN files")

    woff2_dir = "woff2/var"
    if os.path.exists(target_fontsource_dir):
        shutil.rmtree(woff2_dir)
    run(f"ftcli converter ft2wf -f woff2 ./fonts/Variable -out {woff2_dir}")
    rename_files(woff2_dir, format_woff2_name)

    cn_static_path = "./source/cn/static"
    with open(f"{cn_static_path}.sha256", "w") as f:
        f.write(generate_directory_hash(cn_static_path))
        f.flush()

    submodule_path = "./maple-font-page"
    public_path = f"{submodule_path}/public/fonts"
    shutil.rmtree(public_path, ignore_errors=True)
    shutil.copytree(woff2_dir, public_path)
    update_submodule(submodule_path)

    print("Update variable WOFF2")

    # write_unicode_map_json(
    #     "./fonts/TTF/MapleMono-Regular.ttf", "./resources/glyph-map.json"
    # )

    if dry:
        print("Dry run")
    else:
        git_release_commit(tag, ["build.py", "woff2"])
