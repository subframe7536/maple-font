import os
import re
import shutil

from source.py.utils import run

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


def format_filename(filename: str):
    match = re.match(r"MapleMono-(.*)\.(.*)$", filename)

    if not match:
        return None

    style = match.group(1)

    weight = weight_map[style.removesuffix("Italic") if style != "Italic" else "Italic"]
    suf = "normal" if "italic" in filename.lower() else "italic"

    new_filename = f"maple-mono-latin-{weight}-{suf}.{match.group(2)}"
    return new_filename


def rename_files(dir: str):
    for filename in os.listdir(dir):
        if not filename.endswith(".woff") and not filename.endswith(".woff2"):
            continue
        new_name = format_filename(filename)
        if new_name:
            os.rename(os.path.join(dir, filename), os.path.join(dir, new_name))
            print(f"Renamed: {filename} -> {new_name}")


def main():
    target_dir = "fontsource"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    run("python build.py --ttf-only")
    run(f"ftcli converter ft2wf -f woff2 ./fonts/TTF -out {target_dir}")
    run(f"ftcli converter ft2wf -f woff ./fonts/TTF -out {target_dir}")

    rename_files(target_dir)
    shutil.copy("OFL.txt", f"{target_dir}/LICENSE")

    print(f"Please upload {target_dir} to `maple-mono/` in fontsource/font-files fork")


if __name__ == "__main__":
    main()
