from __future__ import annotations

import os
import shutil
import subprocess
import sys
from concurrent.futures import (
    Executor,
    Future,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
)
from concurrent.futures.process import BrokenProcessPool
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from scripts.errors import ExternalToolError
from scripts.utils.logging import configure_logging, logger

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

CI_ENVIRONMENTS = (
    "JENKINS_HOME",
    "TRAVIS",
    "CIRCLECI",
    "GITHUB_ACTIONS",
    "GITLAB_CI",
    "TF_BUILD",
)
T = TypeVar("T")
R = TypeVar("R")


def _probe_process_worker() -> bool:
    """Confirm that a process worker can start before accepting build jobs."""
    return True


class SynchronousExecutor(Executor):
    """Executor-compatible inline execution for explicitly sequential builds."""

    def submit(
        self,
        fn: Callable[..., R],
        /,
        *args: Any,
        **kwargs: Any,
    ) -> Future[R]:
        future: Future[R] = Future()
        try:
            future.set_result(fn(*args, **kwargs))
        except BaseException as error:
            future.set_exception(error)
        return future

    def shutdown(
        self,
        wait: bool = True,
        *,
        cancel_futures: bool = False,
    ) -> None:
        del wait, cancel_futures


def is_ci() -> bool:
    return any(os.environ.get(name) for name in CI_ENVIRONMENTS)


def run(
    command: Sequence[str],
    extra_args: Sequence[str] | None = None,
    log: bool | None = None,
    cwd: str | Path | None = None,
) -> subprocess.CompletedProcess[str]:
    if isinstance(command, str):
        raise TypeError("command must be an argv sequence, not a shell-like string")
    args = list(command)
    args.extend(extra_args or ())
    should_log = not is_ci() if log is None else log
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            stdout=None if should_log else subprocess.PIPE,
            stderr=None if should_log else subprocess.PIPE,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        failure = ExternalToolError(
            tuple(args), error.returncode, error.stdout or "", error.stderr or ""
        )
        if not should_log:
            logger.error("%s", failure)
        raise failure from error


def create_process_executor(
    max_workers: int,
    *,
    initializer: Callable[..., object] | None = configure_logging,
    initargs: tuple[Any, ...] = (),
    fallback_to_threads: bool = False,
) -> Executor:
    """Create a process executor with consistent logging and optional fallback."""
    executor: ProcessPoolExecutor | None = None
    try:
        executor = ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=initializer,
            initargs=initargs,
        )
        executor.submit(_probe_process_worker).result()
        return executor
    except (OSError, PermissionError, BrokenProcessPool):
        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=True)
        if not fallback_to_threads:
            raise
        logger.warning("Process pool unavailable; falling back to thread pool")
        return ThreadPoolExecutor(max_workers=max_workers)


def create_thread_executor(max_workers: int) -> Executor:
    """Create a bounded thread executor through the shared process utility."""
    return ThreadPoolExecutor(max_workers=max_workers)


def run_jobs(
    executor: Executor,
    worker: Callable[[T], R],
    jobs: Iterable[T],
) -> list[R]:
    """Run jobs, preserve input order, and cancel pending work after a failure."""
    futures: list[Future[R]] = [executor.submit(worker, job) for job in jobs]
    if not futures:
        return []

    try:
        for future in as_completed(futures):
            future.result()
    except Exception:
        for future in futures:
            if not future.done():
                future.cancel()
        raise
    return [future.result() for future in futures]


def run_process_jobs(
    pool_size: int,
    worker: Callable[[T], R],
    jobs: Iterable[T],
    executor: Executor | None = None,
) -> list[R]:
    """Run pickle-safe jobs with an optional caller-owned executor."""
    job_list = list(jobs)
    if not job_list:
        return []
    if executor is not None:
        return run_jobs(executor, worker, job_list)
    if pool_size <= 1:
        return [worker(job) for job in job_list]

    with create_process_executor(
        pool_size, fallback_to_threads=True
    ) as process_executor:
        return run_jobs(process_executor, worker, job_list)


def get_font_forge_bin() -> str | None:
    platform_paths = {
        "win32": Path("C:/Program Files (x86)/FontForgeBuilds/bin/fontforge.exe"),
        "darwin": Path(
            "/Applications/FontForge.app/Contents/Resources/opt/local/bin/fontforge"
        ),
    }
    candidate = platform_paths.get(sys.platform, Path("/usr/bin/fontforge"))
    if candidate.exists():
        return str(candidate)
    return shutil.which("fontforge")
