from __future__ import annotations

import unittest

from scripts.task.release import (
    create_release_plan,
    next_font_version,
    next_version,
)


class ReleaseVersionTest(unittest.TestCase):
    def test_minor_version_is_calculated_without_mutation(self) -> None:
        self.assertEqual(next_version("7.9", "minor"), "7.10")

    def test_major_version_resets_minor(self) -> None:
        self.assertEqual(next_version("7.9", "major"), "8.0")

    def test_pre_major_starts_and_increments_beta_versions(self) -> None:
        self.assertEqual(next_version("7.9", "pre-major"), "8.0b1")
        self.assertEqual(next_version("8.0b1", "pre-major"), "8.0b2")

    def test_matching_bump_finalizes_a_beta_release_line(self) -> None:
        self.assertEqual(next_version("8.0b2", "major"), "8.0")
        self.assertEqual(next_version("7.10b2", "minor"), "7.10")

    def test_font_version_uses_a_single_release_line_sequence(self) -> None:
        self.assertEqual(next_font_version("7.9", "7.900", "8.0b1"), "8.001")
        self.assertEqual(next_font_version("8.0b1", "8.001", "8.0b2"), "8.002")
        self.assertEqual(next_font_version("8.0b2", "8.002", "8.0"), "8.003")

    def test_release_plan_uses_modern_build_arguments(self) -> None:
        plan = create_release_plan(
            "minor",
            current_version="7.9",
            current_font_version="7.900",
        )

        self.assertEqual(
            plan.build_args,
            ("--format", "ttf", "--no-nerd-font", "--no-hinted"),
        )
        self.assertEqual(
            plan.default_build_args,
            ("--format", "ttf", "--no-nerd-font", "--no-hinted", "--cjk", "cn"),
        )
