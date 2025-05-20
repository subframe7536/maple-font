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


def has_no_changes(repo_path: str | None = None) -> bool:
    """Check if the repository has no uncommitted changes"""
    status = run_git_command(["git", "status", "--porcelain"], cwd=repo_path)
    return not bool(status)


def commit_and_push_submodule(submodule_path: str, commit_message: str) -> bool:
    """Commit and push changes in the submodule"""
    abs_submodule_path = os.path.abspath(submodule_path)

    # Check if submodule exists
    if not os.path.exists(abs_submodule_path):
        print(
            f"Error: Submodule {submodule_path} does not exist, please run `git submodule update --init` first"
        )
        sys.exit(1)

    # Check for uncommitted changes
    if has_no_changes(abs_submodule_path):
        print("Landing page data has no changes, skipping")
        return False

    # Switch to main branch
    run_git_command(["git", "checkout", "main"], cwd=abs_submodule_path)

    # Add all changes
    run_git_command(["git", "add", "."], cwd=abs_submodule_path)

    # Commit changes
    run_git_command(
        ["git", "commit", "-m", "[skip-ci]" + commit_message], cwd=abs_submodule_path
    )

    # Push to remote
    run_git_command(["git", "push", "origin", "main"], cwd=abs_submodule_path)

    print(f"Submodule {submodule_path} changes committed and pushed to main")
    return True


def update_main_repo(submodule_path: str, main_commit_message: str) -> None:
    """Update the main repository's submodule reference"""

    # Update submodule to the latest commit
    run_git_command(["git", "submodule", "update", "--remote"])

    # Add submodule changes to the main repository
    run_git_command(["git", "add", submodule_path])

    # Check if main repo has changes to commit
    if has_no_changes():
        print("Main repository has no submodule reference changes, skipping commit")
        return

    # Commit main repo changes
    run_git_command(["git", "commit", "-m", main_commit_message])

    # Push main repo
    run_git_command(["git", "push", "origin", "main"])

    print("Main repository submodule reference updated and pushed")


def page(submodule_path: str, var_dir: str, commit: bool = False) -> None:
    # Update landing page data
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

    data = read_json("config.json")
    del data["$schema"]
    write_json(joinPaths(feature_data_base, "config.json"), data)

    data = read_text(joinPaths("source", "py", "in_browser.py"))
    write_text(joinPaths(submodule_path, "data", "script.py"), minify(data))

    font_dir = joinPaths(submodule_path, "public", "fonts")
    os.system("python build.py --ttf-only --no-nerd-font --least-styles")
    os.system(f"ftcli converter ft2wf -f woff2 {var_dir}")
    shutil.rmtree(font_dir, ignore_errors=True)
    os.makedirs(font_dir, exist_ok=True)
    for filename in os.listdir(var_dir):
        if filename.endswith(".woff2"):
            os.rename(
                joinPaths(var_dir, filename),
                joinPaths(font_dir, filename.replace(".woff2", "-VF.woff2")),
            )

    # Commit changes if specified
    if commit:
        commit_message = "Update landing page data"

        # Commit and push submodule changes
        modified = commit_and_push_submodule(submodule_path, commit_message)

        # Update main repo if submodule was modified
        if not modified:
            print("No changes to update in main repository")
