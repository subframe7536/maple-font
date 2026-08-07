from __future__ import annotations

import os
import sys
import unittest
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from unittest.mock import MagicMock, patch

from scripts.errors import ExternalToolError
from scripts.external.process import (
    _probe_process_worker,
    create_process_executor,
    run,
    run_jobs,
    run_process_jobs,
)


class ProcessExecutorTest(unittest.TestCase):
    def test_run_preserves_arguments_and_reports_ci_failure(self) -> None:
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "1"}):
            result = run(
                [sys.executable, "-c", "import sys; print(sys.argv[1])", "a b"]
            )
            self.assertEqual(result.stdout.strip(), "a b")
            with self.assertRaises(ExternalToolError) as raised:
                run(
                    [
                        sys.executable,
                        "-c",
                        "import sys; print('out'); print('err', file=sys.stderr); sys.exit(7)",
                    ]
                )
        self.assertEqual(raised.exception.exit_code, 7)
        self.assertIn("out", raised.exception.stdout)
        self.assertIn("err", raised.exception.stderr)

    def test_run_rejects_shell_like_strings(self) -> None:
        with self.assertRaisesRegex(TypeError, "argv sequence"):
            run("echo unsafe")  # type: ignore[arg-type]

    @patch("scripts.external.process.ProcessPoolExecutor")
    def test_create_process_executor_probes_worker_before_returning(
        self, process_pool: MagicMock
    ) -> None:
        executor = process_pool.return_value
        probe_future = executor.submit.return_value

        result = create_process_executor(3)

        self.assertIs(result, executor)
        executor.submit.assert_called_once_with(_probe_process_worker)
        probe_future.result.assert_called_once_with()

    @patch("scripts.external.process.ThreadPoolExecutor")
    @patch("scripts.external.process.ProcessPoolExecutor")
    def test_create_process_executor_falls_back_after_constructor_failure(
        self, process_pool: MagicMock, thread_pool: MagicMock
    ) -> None:
        process_pool.side_effect = OSError("processes unavailable")

        result = create_process_executor(3, fallback_to_threads=True)

        self.assertIs(result, thread_pool.return_value)
        thread_pool.assert_called_once_with(max_workers=3)

    @patch("scripts.external.process.ThreadPoolExecutor")
    @patch("scripts.external.process.ProcessPoolExecutor")
    def test_create_process_executor_propagates_constructor_failure(
        self, process_pool: MagicMock, thread_pool: MagicMock
    ) -> None:
        error = OSError("processes unavailable")
        process_pool.side_effect = error

        with self.assertRaises(OSError) as raised:
            create_process_executor(3)

        self.assertIs(raised.exception, error)
        thread_pool.assert_not_called()

    @patch("scripts.external.process.ThreadPoolExecutor")
    @patch("scripts.external.process.ProcessPoolExecutor")
    def test_create_process_executor_shuts_down_after_submit_failure(
        self, process_pool: MagicMock, thread_pool: MagicMock
    ) -> None:
        executor = process_pool.return_value
        executor.submit.side_effect = PermissionError("workers unavailable")

        result = create_process_executor(2, fallback_to_threads=True)

        self.assertIs(result, thread_pool.return_value)
        executor.shutdown.assert_called_once_with(wait=True, cancel_futures=True)
        thread_pool.assert_called_once_with(max_workers=2)

    @patch("scripts.external.process.ThreadPoolExecutor")
    @patch("scripts.external.process.ProcessPoolExecutor")
    def test_create_process_executor_handles_broken_probe_worker(
        self, process_pool: MagicMock, thread_pool: MagicMock
    ) -> None:
        executor = process_pool.return_value
        error = BrokenProcessPool("worker failed to start")
        executor.submit.return_value.result.side_effect = error

        with self.assertRaises(BrokenProcessPool) as raised:
            create_process_executor(2)

        self.assertIs(raised.exception, error)
        executor.shutdown.assert_called_once_with(wait=True, cancel_futures=True)
        thread_pool.assert_not_called()

    @patch(
        "scripts.external.process.ProcessPoolExecutor",
        side_effect=BrokenProcessPool("worker failed to start"),
    )
    def test_thread_fallback_runs_jobs_after_startup_failure(
        self, _process_pool: MagicMock
    ) -> None:
        with create_process_executor(2, fallback_to_threads=True) as executor:
            self.assertIsInstance(executor, ThreadPoolExecutor)
            results = run_jobs(executor, lambda value: value * 2, [1, 2, 3])

        self.assertEqual(results, [2, 4, 6])

    def test_run_process_jobs_uses_serial_execution_for_one_worker(self) -> None:
        calls: list[int] = []

        results = run_process_jobs(
            1,
            lambda value: calls.append(value) or value * 2,
            [1, 2, 3],
        )

        self.assertEqual(results, [2, 4, 6])
        self.assertEqual(calls, [1, 2, 3])

    def test_run_jobs_preserves_input_order(self) -> None:
        executor = MagicMock()
        futures: list[Future[int]] = []
        for result in (4, 2, 6):
            future: Future[int] = Future()
            future.set_result(result)
            futures.append(future)
        executor.submit.side_effect = futures

        results = run_jobs(executor, lambda value: value * 2, [2, 1, 3])

        self.assertEqual(results, [4, 2, 6])

    def test_run_jobs_cancels_pending_work_after_failure(self) -> None:
        executor = MagicMock()
        failed: Future[None] = Future()
        failed.set_exception(RuntimeError("failed"))
        pending: Future[None] = Future()
        executor.submit.side_effect = [failed, pending]

        with self.assertRaisesRegex(RuntimeError, "failed"):
            run_jobs(executor, lambda _: None, [1, 2])

        self.assertTrue(pending.cancelled())


if __name__ == "__main__":
    unittest.main()
