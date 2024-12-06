from os import listdir, mkdir, path
from shutil import move, rmtree
import subprocess

from source.py.utils import joinPaths

output_base = "fonts"
output_release = "release"


def move_and_log(file_path: str, target_path: str):
    print(f"Move {file_path} -> {target_path}")
    move(file_path, target_path)


def build(normal: bool, hinted: bool, liga: bool, cache: bool = False):
    args = [
        "python",
        "build.py",
        "--archive",
        "--cn-both",
    ]

    if cache:
        args.append("--cache")

    if normal:
        args.append("--normal")

    if hinted:
        args.append("--hinted")
    else:
        args.append("--no-hinted")

    if liga:
        args.append("--liga")
    else:
        args.append("--no-liga")

    print(" ".join(args))
    subprocess.run(args)

    build_archive_dir = f"{output_base}/archive"

    for file_name in listdir(build_archive_dir):
        file_path = joinPaths(build_archive_dir, file_name)
        if path.isfile(file_path):
            if not hinted:
                name, ext = path.splitext(file_name)
                file_name = f"{name}-unhinted{ext}"
            if "Variable" in file_name and file_name != "MapleMono-Variable.zip":
                continue
            move_and_log(file_path, joinPaths(output_release, file_name))


# clear old releases
rmtree(output_base, ignore_errors=True)
mkdir(output_base)
rmtree(output_release, ignore_errors=True)
mkdir(output_release)

# build all formats
build(normal=True, liga=False, hinted=True)
build(normal=True, liga=False, hinted=False, cache=True)
build(normal=True, liga=True, hinted=True)
build(normal=True, liga=True, hinted=False, cache=True)
build(normal=False, liga=False, hinted=True)
build(normal=False, liga=False, hinted=False, cache=True)
build(normal=False, liga=True, hinted=True)
build(normal=False, liga=True, hinted=False, cache=True)

# copy woff2 to root
rmtree("woff2", ignore_errors=True)
print("Generate variable woff2")
subprocess.run(f"ftcli converter ft2wf -out woff2/var -f woff2 {output_base}/variable")
