from __future__ import annotations

import os
import sys
import unittest
from concurrent.futures import Future
from unittest.mock import MagicMock, patch

from scripts.utils.errors import ExternalToolError
from scripts.utils.process import (
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
