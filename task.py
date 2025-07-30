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
    page_parser.add_argument("--woff2", action="store_true", help="Generate new woff2 fonts")
    page_parser.add_argument("--commit", action="store_true", help="Commit changes")

    command.add_parser("cn-rebuild", help="Rebuild CN static font")

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
    elif args.command == "cn-rebuild":
        from source.py.task.cn_rebuild import cn_rebuild

        cn_rebuild("./source/cn")
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
