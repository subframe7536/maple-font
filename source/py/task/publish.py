from pathlib import Path
from source.py.task._utils import is_ci
import subprocess


def get_output(cmd: list[str]) -> str:
    return subprocess.check_output(cmd).decode("utf-8").strip()


def publish(write: bool, dry: bool = not is_ci()):
    # get tag
    tag_list = get_output(["git", "tag", "--list", "--sort=committerdate"]).split("\n")
    prev_tag = tag_list[-2]
    tag = tag_list[-1]
    print(f"Tag: {prev_tag} -> {tag}")

    # generate changelog
    changelog = get_output(
        ["git", "log", "--pretty=format:- %s\n%b", f"{prev_tag}..{tag}"]
    )

    # build release command
    template_path = Path(".github/release_template.md")
    title = " ".join(part.capitalize() for part in tag.split("-"))
    cmd = [
        "gh",
        "release",
        "create",
        tag,
        "release/**/*.*",
        "--notes-file",
        template_path.as_posix(),
        "-t",
        title,
        "--draft",
    ]

    # read release template
    template = (
        template_path.read_text()
        .replace("<!-- changelog -->", changelog)
        .replace(
            "https://<url>",
            f"https://github.com/subframe7536/maple-font/releases/download/{tag}",
        )
    )
    if write or not dry:
        template_path.write_text(template)

    if dry:
        print(f"changelog:\n{changelog}\n\nRun command: {' '.join(cmd)}")
    else:
        subprocess.run(cmd, check=True)
