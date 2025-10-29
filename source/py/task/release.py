import os
import re
import shutil
from typing import Callable
from fontTools.ttLib import TTFont
from source.py.task._utils import write_json, write_text, default_weight_map
from source.py.utils import joinPaths, run
from build import main


def format_fontsource_name(filename: str):
    match = re.match(r"MapleMono-(.*)\.(.*)$", filename.replace(".ttf", ""))

    if not match:
        return None

    style = match.group(1)
    # Remove 'Italic' only if it is a suffix
    if style.endswith("Italic") and style != "Italic":
        base_style = style[:-6]  # Remove 'Italic' (6 chars)
    else:
        base_style = style
    # Fallback to 'Regular' if not found
    weight = default_weight_map.get(
        base_style.lower(), default_weight_map.get("regular", 400)
    )
    suf = "italic" if "italic" in style.lower() else "normal"

    new_filename = f"maple-mono-latin-{weight}-{suf}.{match.group(2)}"
    return new_filename


def format_woff2_name(filename: str):
    return filename.replace(".ttf.woff2", "-VF.woff2")


def rename_woff_files(dir: str, fn: Callable[[str], str | None]):
    for filename in os.listdir(dir):
        if not filename.endswith(".woff") and not filename.endswith(".woff2"):
            continue
        new_name = fn(filename)
        if new_name:
            os.rename(joinPaths(dir, filename), joinPaths(dir, new_name))
            print(f"Renamed: {filename} -> {new_name}")


def parse_tag(type: str):
    out = os.popen(f"uv version --bump {type}").readline()
    return "v" + out.split(" ")[-1][:-1]


def update_build_script_version(script_path: str, tag: str):
    with open(script_path, "r", encoding="utf-8", newline="\n") as f:
        content = re.sub(r'FONT_VERSION = ".*"', f'FONT_VERSION = "{tag}"', f.read())
    write_text(script_path, content)


def git_release_commit(tag, files):
    run(f"git add {' '.join(files)}")
    run(["git", "commit", "-m", f"Release {tag}"])
    run(f"git tag {tag}")
    print("Committed and tagged")

    run("git push origin")
    run(f"git push origin {tag}")
    print("Pushed to origin")


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
    write_json(output, font_map)
    print(f"Write font map to {output}")
    font.close()


def release(type: str, dry: bool):
    tag = parse_tag(type)
    # prompt and wait for user input
    choose = input(f"{'[DRY] ' if dry else ''}Tag {tag}? (Y or n) ")
    if choose != "" and choose.lower() != "y":
        print("Aborted")
        return

    script_path = "build.py"
    update_build_script_version(script_path, tag)
    target_fontsource_dir = "cdn/fontsource"
    main(["--ttf-only", "--no-nerd-font", "--cn", "--no-hinted"], tag)

    shutil.rmtree("./cdn", ignore_errors=True)
    run(f"ftcli converter ft2wf -f woff2 ./fonts/TTF -out {target_fontsource_dir}")
    run(f"ftcli converter ft2wf -f woff ./fonts/TTF -out {target_fontsource_dir}")
    rename_woff_files(target_fontsource_dir, format_fontsource_name)
    print("Generate fontsource files")

    dep_file = "requirements.txt"
    run(
        f"uv export --format requirements-txt --no-hashes --output-file {dep_file} --quiet"
    )

    shutil.copytree("./fonts/CN", "./cdn/cn")
    print("Generate CN files")

    woff2_dir = "woff2/var"
    if os.path.exists(target_fontsource_dir):
        shutil.rmtree(woff2_dir)
    run(f"ftcli converter ft2wf -f woff2 ./fonts/Variable -out {woff2_dir}")
    rename_woff_files(woff2_dir, format_woff2_name)

    # write_unicode_map_json(
    #     "./fonts/TTF/MapleMono-Regular.ttf", "./resources/glyph-map.json"
    # )

    if dry:
        print("Dry run")
    else:
        git_release_commit(tag, [script_path, "woff2", dep_file, "pyproject.toml"])
