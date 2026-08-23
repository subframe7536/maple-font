"""Project logging configuration for command-line entrypoints."""

from __future__ import annotations

import logging
import os
import time
from contextvars import ContextVar
from enum import Enum
from typing import Any

ENVIRONMENT_VARIABLE = "MAPLE_LOG_LEVEL"
DEFAULT_LEVEL_NAME = "INFO"
_HANDLER_NAME = "maple-font-stderr"


class TaskName(str, Enum):
    """Known task categories used by the project logger."""

    SYSTEM = "system"
    BUILD = "build"
    PREPARE = "prepare"
    FONTMAKE = "fontmake"
    VARIABLE = "variable"
    TTF = "ttf"
    OTF = "otf"
    TTF_AUTOHINT = "ttf-autohint"
    WOFF = "woff"
    WOFF2 = "woff2"
    NERD_FONT = "nerd-font"
    CJK = "cjk"
    ARCHIVE = "archive"
    DESIGNSPACE = "designspace"
    FEA = "fea"
    NF = "nf"
    GOOGLEFONTS = "googlefonts"
    RELEASE = "release"
    PUBLISH = "publish"


_VALID_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
logger = logging.getLogger("scripts")
logger.addHandler(logging.NullHandler())
_current_task: ContextVar[str] = ContextVar("maple_log_task", default="system")
_last_started_task: ContextVar[str | None] = ContextVar(
    "maple_last_started_log_task", default=None
)


class TaskContextFilter(logging.Filter):
    """Attach the active task to records that do not set one explicitly."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "task"):
            record.task = _current_task.get()
        return True


class TaskFormatter(logging.Formatter):
    """Keep routine INFO output compact while preserving diagnostic severity."""

    def __init__(self) -> None:
        super().__init__("%(message)s")

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        task = getattr(record, "task", "system")
        if record.levelno == logging.INFO:
            return f"[{task}] {message}"
        if record.levelno == logging.DEBUG:
            return f"> {message}"
        return f"[{record.levelname}] [{task}] {message}"


def configure_logging() -> None:
    """Configure the project logger without changing third-party logging."""
    _current_task.set("system")
    _last_started_task.set(None)
    requested_level = os.environ.get(ENVIRONMENT_VARIABLE, DEFAULT_LEVEL_NAME).upper()
    level = _VALID_LEVELS.get(requested_level, logging.INFO)

    handler = next(
        (
            candidate
            for candidate in logger.handlers
            if candidate.get_name() == _HANDLER_NAME
        ),
        None,
    )
    if handler is None:
        handler = logging.StreamHandler()
        handler.set_name(_HANDLER_NAME)
        handler.setFormatter(TaskFormatter())
        handler.addFilter(TaskContextFilter())
        logger.addHandler(handler)

    logger.setLevel(level)
    logger.propagate = False

    if requested_level not in _VALID_LEVELS:
        logger.warning(
            "Invalid %s=%r; using %s",
            ENVIRONMENT_VARIABLE,
            requested_level,
            DEFAULT_LEVEL_NAME,
        )


def set_log_task(task: str) -> None:
    """Set the task label inherited by subsequent log records in this worker."""
    _current_task.set(task)


def _write_blank_line() -> None:
    """Write a task separator without manufacturing an empty log record."""
    for handler in logger.handlers:
        if handler.get_name() != _HANDLER_NAME:
            continue
        handler.acquire()
        try:
            stream = getattr(handler, "stream", None)
            if stream is not None:
                stream.write("\n")
                stream.flush()
        finally:
            handler.release()


def log_progress(message: str, *args: Any, complete: bool = False) -> None:
    """Refresh one INFO progress record in place on the project log stream."""
    if not logger.isEnabledFor(logging.INFO):
        return
    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        __file__,
        0,
        message,
        args,
        None,
    )
    for handler in logger.handlers:
        if handler.get_name() != _HANDLER_NAME or not handler.filter(record):
            continue
        handler.acquire()
        try:
            stream = getattr(handler, "stream", None)
            if stream is not None:
                stream.write(f"\r{handler.format(record)}")
                if complete:
                    stream.write("\n")
                stream.flush()
        finally:
            handler.release()


def log_task(
    task: TaskName,
    message: str,
    *args: Any,
    task_label: str | None = None,
    force_separator: bool = False,
) -> float:
    """Start a named task and retain its label for subsequent log records."""
    label = task_label or task.value
    previous_task = _last_started_task.get()
    if previous_task is not None and (previous_task != label or force_separator):
        _write_blank_line()
    set_log_task(label)
    _last_started_task.set(label)
    logger.info(message, *args)
    return time.monotonic()


def log_task_complete(started_at: float, summary: str | None = None) -> None:
    """Finish the active task with a stable duration and optional result summary."""
    message = f"Done in {time.monotonic() - started_at:.2f}s"
    if summary:
        message += f" ({summary})"
    logger.info(message)
