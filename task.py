#!/usr/bin/env python3
import argparse


def main():
    parser = argparse.ArgumentParser(description="Task script for Maple Font")

    command = parser.add_subparsers(dest="command", help="Total tasks")
    command.required = True

    nerdfont_parser = command.add_parser("nerd-font", help="Build Nerd-Font base font")
    nerdfont_parser.add_argument(
        "--no-update",
        action="store_true",
        help="Do not check version and update if available",
    )

    feature_parser = command.add_parser("fea", help="Build fea files")
    feature_parser.add_argument("--output", type=str, default="./source/features", help="Output directory")
    feature_parser.add_argument("--cn", action="store_true", help="Generate features that contains CN features, remove exists CN feature files if not set")

    release_parser = command.add_parser("release", help="Release new version")
    release_parser.add_argument(
        "tag",
        type=str,
        help="The tag to build the release for, e.g. 7.0 or v7.0",
    )
    release_parser.add_argument(
        "beta",
        nargs="?",
        type=str,
        help="Beta tag name, e.g. 3 or beta3",
    )
    release_parser.add_argument(
        "--dry",
        action="store_true",
        help="Dry run",
    )

    args = parser.parse_args()
    if args.command == "nerd-font":
        from source.py.task.nerdfont import nerd_font

        nerd_font(args.no_update)

    elif args.command == "fea":
        from source.py.task.fea import fea

        fea(args.output, args.cn)

    elif args.command == "release":
        from source.py.task.release import release

        release(args.tag, args.beta, args.dry)


if __name__ == "__main__":
    main()
