from functools import partial
from os import listdir, makedirs, path, system
import shutil
from typing import Callable, Iterable
from zipfile import ZIP_BZIP2, ZipFile
from source.py.utils import get_directory_hash, joinPaths


def run_pool_process(fn: Callable, items: Iterable):
    from multiprocessing import Pool

    with Pool(processes=4) as pool:
        pool.map(fn, items)


def archive(source: str, target: str, filter: Callable[[str], bool]):
    with ZipFile(target, "w", compression=ZIP_BZIP2, compresslevel=9) as zip_file:
        for file in listdir(source):
            file_path = joinPaths(source, file)
            if filter(file_path):
                zip_file.write(file_path, file)

    zip_file.close()
    print(f"📦 Package {target}")


def instantiate_cn_var(f: str, base_dir: str, static_dir: str, italic_tmp_dir: str):
    output_dir = italic_tmp_dir if "Italic" in f else static_dir
    system(
        f"ftcli converter var2static -out {output_dir} {joinPaths(base_dir, f)}",
    )


def flatten_italic_fonts(italic_tmp_dir: str, target_dir: str):
    for f in listdir(italic_tmp_dir):
        shutil.move(
            joinPaths(italic_tmp_dir, f),
            joinPaths(
                target_dir,
                f if "Italic" in f else f.replace(".ttf", "Italic.ttf"),
            ),
        )
    shutil.rmtree(italic_tmp_dir)


def optimize_cn_base(f: str, base_dir: str):
    font_path = joinPaths(base_dir, f)
    print(f"✨ Optimize {font_path}")
    system(f"ftcli font correct-contours {font_path}")
    system(
        f"ftcli font del-table -t kern -t GPOS {font_path}",
    )


def update_dir_hash(dir: str):
    system(f"ftcli name del-mac-names -r {dir}")
    with open(f"{dir}.sha256", "w") as f:
        f.write(get_directory_hash(dir))
        f.flush()
    print(f"#️⃣ Update {dir}.sha256")


var_font_names = ["MapleMono-CN-VF.ttf", "MapleMono-CN-Italic-VF.ttf"]

static_dir_name = "static"


def cn_rebuild(root: str):
    # 1. Check variable fonts exist in root dir
    var_fonts = [f for f in var_font_names if path.exists(joinPaths(root, f))]
    if len(var_fonts) != len(var_font_names):
        print("❗ Missing variable fonts in", root, var_fonts)
        return

    # 2. Instantiate static fonts in parallel
    static_dir = joinPaths(root, static_dir_name)
    italic_tmp_dir = joinPaths(static_dir, "italic")

    makedirs(static_dir, exist_ok=True)

    run_pool_process(
        partial(
            instantiate_cn_var,
            base_dir=root,
            static_dir=static_dir,
            italic_tmp_dir=italic_tmp_dir,
        ),
        var_font_names,
    )

    # 3. Flatten italic fonts
    flatten_italic_fonts(italic_tmp_dir, static_dir)

    # 4. Optimize static fonts
    run_pool_process(
        partial(optimize_cn_base, base_dir=static_dir), listdir(static_dir)
    )

    # 5. Update directory hash
    update_dir_hash(static_dir)

    # 6. Archive source fonts
    archive_base_dir = joinPaths(root, "archive")
    shutil.rmtree(archive_base_dir, ignore_errors=True)
    makedirs(archive_base_dir)

    archive(
        root,
        joinPaths(archive_base_dir, "vfc.zip"),
        lambda x: x.endswith(".vfc"),
    )
    archive(
        root,
        joinPaths(archive_base_dir, "cn-base-variable.zip"),
        lambda x: x.endswith(".ttf"),
    )
    archive(
        static_dir,
        joinPaths(archive_base_dir, "cn-base-static.zip"),
        lambda x: x.endswith(".ttf"),
    )

    print("✅ CN rebuild complete.")
