from __future__ import annotations

import argparse
from collections.abc import Callable

from scripts.task import cjk, designspace, fea, googlefonts, nf, publish, release
from scripts.utils.logging import TaskName, configure_logging, log_task

CommandHandler = Callable[[argparse.Namespace], None]


def _register(
    parser: argparse._SubParsersAction[argparse.ArgumentParser], module
) -> None:
    subparser = module.register_parser(parser)
    if subparser is not None:
        subparser.set_defaults(_command_handler=module.run)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Task script for Maple Font")
    subparsers = parser.add_subparsers(dest="command", help="Total tasks")

    for module in (nf, fea, designspace, release, cjk, googlefonts, publish):
        _register(subparsers, module)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    handler: CommandHandler | None = getattr(args, "_command_handler", None)
    if handler is None:
        parser.print_help()
        return
    configure_logging()
    log_task(TaskName(args.command), "Running task: %s", args.command)
    handler(args)
