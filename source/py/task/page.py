import os
import shutil
import subprocess
import sys
from source.py.feature import (
    get_cv_cn_version_info,
    get_cv_italic_version_info,
    get_cv_version_info,
    get_ss_version_info,
    get_total_feat_ts,
)
from source.py.task._utils import read_json, read_text, write_json, write_text
from source.py.utils import joinPaths
from python_minifier import minify


def run_git_command(args: list, cwd=None, check=True):
    """Run a Git command and return output, handling errors"""
    try:
        result = subprocess.run(
            args, cwd=cwd, check=check, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(
            f"Error: Failed to execute {' '.join(args)} in {cwd or os.getcwd()}: {e.stderr}"
        )
        sys.exit(1)


def page(
    submodule_path: str,
    var_dir: str,
    woff2: bool = False,
    sync: bool = False,
) -> None:
    # Switch to main branch
    abs_submodule_path = os.path.abspath(submodule_path)

    if not os.path.exists(abs_submodule_path):
        print(
            f"Error: Submodule {submodule_path} does not exist, please run `git submodule update --init` first"
        )
        sys.exit(1)

    if sync:
        run_git_command(["git", "submodule", "update", "--remote"])
        print("Checkout main")
        run_git_command(["git", "checkout", "main"], cwd=abs_submodule_path)

        run_git_command(["git", "pull"], cwd=abs_submodule_path)
        print("Sync remote")

    # Update landing page data
    print("Update features")
    feature_data_base = joinPaths(submodule_path, "data", "features")
    os.makedirs(feature_data_base, exist_ok=True)
    write_json(joinPaths(feature_data_base, "cv.json"), get_cv_version_info())
    write_json(joinPaths(feature_data_base, "cn.json"), get_cv_cn_version_info())
    write_json(
        joinPaths(feature_data_base, "italic.json"), get_cv_italic_version_info()
    )
    write_json(joinPaths(feature_data_base, "ss.json"), get_ss_version_info())
    write_text(
        joinPaths(feature_data_base, "features.ts"),
        get_total_feat_ts(),
    )

    print("Update config")
    data = read_json("config.json")
    del data["$schema"]
    write_json(joinPaths(submodule_path, "data", "config.json"), data)

    print("Update script")
    data = read_text(joinPaths("source", "py", "in_browser.py"))
    write_text(
        joinPaths(submodule_path, "data", "script.py"),
        "# Source: https://github.com/subframe7536/maple-font/blob/variable/source/py/in_browser.py\n"
        + minify(data),
    )

    if woff2:
        print("Update woff2")
        font_dir = joinPaths(submodule_path, "public", "fonts")
        os.system("python build.py --ttf-only --no-nerd-font --least-styles")
        os.system(f"ftcli converter ft2wf -f woff2 {var_dir}")
        shutil.rmtree(font_dir, ignore_errors=True)
        os.makedirs(font_dir, exist_ok=True)
        for filename in os.listdir(var_dir):
            if filename.endswith(".woff2"):
                os.rename(
                    joinPaths(var_dir, filename),
                    joinPaths(font_dir, filename.replace(".ttf.woff2", "-VF.woff2")),
                )

    # Commit changes if specified
    if sync:
        # Add all changes
        run_git_command(["git", "add", "."], cwd=abs_submodule_path)

        # Commit changes
        print("Commit submodule")
        run_git_command(
            ["git", "commit", "-m", "Update landing page data"], cwd=abs_submodule_path
        )

        # Push submodule to remote
        print("Update remote submodule")
        run_git_command(["git", "push", "origin", "main"], cwd=abs_submodule_path)

        # Reset to HEAD
        run_git_command(["git", "submodule", "update", "--remote"])

        # Add all changes
        run_git_command(["git", "add", "."])

        # Commit changes
        print("Commit main")
        run_git_command(["git", "commit", "-m", "sync landing page"])

        # Push main to remote
        print("Update remote main")
        run_git_command(["git", "push", "origin"])
