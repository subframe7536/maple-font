#!/usr/bin/env python3
import argparse
from os import path
import shutil


def main():
    parser = argparse.ArgumentParser(description="Task script for Maple Font")

    command = parser.add_subparsers(dest="command", help="Total tasks")

    nerdfont_parser = command.add_parser("nf", help="Build Nerd-Font base font")
    nerdfont_parser.add_argument(
        "--no-update",
        action="store_true",
        help="Do not check version and update if available",
    )

    feature_parser = command.add_parser("fea", help="Build fea files")
    feature_parser.add_argument(
        "--output", type=str, default="./source/features", help="Output directory"
    )
    feature_parser.add_argument(
        "--cn",
        action="store_true",
        help="Generate features that contains CN features, remove exists CN feature files if not set",
    )

    release_parser = command.add_parser("release", help="Release new version")
    release_parser.add_argument(
        "type",
        choices=["major", "minor"],
        help="Bump version type",
    )
    release_parser.add_argument(
        "--dry",
        action="store_true",
        help="Dry run",
    )

    page_parser = command.add_parser("page", help="Update landing page data")
    page_parser.add_argument(
        "--woff2", action="store_true", help="Generate new woff2 fonts"
    )
    page_parser.add_argument("--commit", action="store_true", help="Commit changes")

    cn = command.add_parser("cn", help="Rebuild CN static font")
    cn.add_argument(
        "--pull", action="store_true", help="pull the latest CN source files"
    )
    cn.add_argument("--rebuild", action="store_true", help="rebuild the CN static font")

    publish_parser = command.add_parser(
        "publish", help="Publish the font archives to GitHub Release"
    )
    publish_parser.add_argument(
        "--write",
        action="store_true",
        help="Write changelog to release note file (auto write in CI)",
    )

    args = parser.parse_args()
    if args.command == "nf":
        from source.py.task.nerdfont import nerd_font

        nerd_font(args.no_update)

    elif args.command == "fea":
        from source.py.task.fea import fea

        fea(args.output, args.cn)

    elif args.command == "release":
        from source.py.task.release import release

        release(args.type, args.dry)
    elif args.command == "page":
        from source.py.task.page import page

        page("./maple-font-page", "./fonts/Variable", args.woff2, args.commit)
    elif args.command == "cn":
        from source.py.task.cn import cn

        cn("./source/cn", args.pull, args.rebuild)
    elif args.command == "publish":
        from source.py.task.publish import publish

        publish(args.write)
    else:
        print("Test only")
        from source.py.in_browser import main

        zip_path = "./fonts/archive/MapleMono-NF-CN-unhinted.zip"
        if not path.exists(zip_path):
            print("No zip file, please run `uv run build --archive` first")
            return
        test_path = zip_path.replace(".zip", "-test.zip")
        shutil.copy(zip_path, test_path)
        main(
            test_path,
            zip_path.replace(".zip", "-result.zip"),
            {"cv01": "1", "cv02": "1"},
        )


if __name__ == "__main__":
    main()
