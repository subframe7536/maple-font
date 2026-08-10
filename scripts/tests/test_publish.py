from __future__ import annotations

import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import call, patch

from scripts.task.publish import (
    build_release_task,
    collect_release_task_archives,
    expected_release_archives,
    prepare_release_assets,
    publish,
    release_build_steps,
    release_manifest,
    release_matrix,
    resolve_release_tags,
    resolve_release_task,
)


class ResolveReleaseTagsTest(unittest.TestCase):
    @patch("scripts.task.publish.get_output")
    def test_explicit_tag_is_used_and_previous_tag_comes_from_ancestry(
        self, get_output
    ) -> None:
        get_output.side_effect = ["commit-id", "v7.8"]

        self.assertEqual(resolve_release_tags("v7.9"), ("v7.8", "v7.9"))

        self.assertEqual(
            get_output.call_args_list,
            [
                call(["git", "rev-parse", "--verify", "refs/tags/v7.9"]),
                call(
                    [
                        "git",
                        "describe",
                        "--tags",
                        "--match",
                        "v*",
                        "--abbrev=0",
                        "v7.9^",
                    ]
                ),
            ],
        )

    @patch("scripts.task.publish.get_output")
    def test_unique_tag_pointing_at_head_is_used(self, get_output) -> None:
        get_output.side_effect = ["v7.9", "v7.8"]

        self.assertEqual(resolve_release_tags(None), ("v7.8", "v7.9"))

        self.assertEqual(
            get_output.call_args_list,
            [
                call(["git", "tag", "--points-at", "HEAD"]),
                call(
                    [
                        "git",
                        "describe",
                        "--tags",
                        "--match",
                        "v*",
                        "--abbrev=0",
                        "v7.9^",
                    ]
                ),
            ],
        )

    @patch("scripts.task.publish.get_output", return_value="")
    def test_no_tag_at_head_requires_explicit_tag(self, get_output) -> None:
        with self.assertRaisesRegex(ValueError, "No release tag points at HEAD"):
            resolve_release_tags(None)

        get_output.assert_called_once_with(["git", "tag", "--points-at", "HEAD"])

    @patch("scripts.task.publish.get_output", return_value="v7.9\nv7.9-hotfix")
    def test_multiple_tags_at_head_require_explicit_tag(self, get_output) -> None:
        with self.assertRaisesRegex(ValueError, "Multiple release tags point at HEAD"):
            resolve_release_tags(None)

        get_output.assert_called_once_with(["git", "tag", "--points-at", "HEAD"])

    @patch("scripts.task.publish.get_output")
    def test_unknown_explicit_tag_fails_before_ancestry_lookup(
        self, get_output
    ) -> None:
        get_output.side_effect = subprocess.CalledProcessError(1, ["git"])

        with self.assertRaisesRegex(ValueError, "Unknown release tag: v7.9"):
            resolve_release_tags("v7.9")

        get_output.assert_called_once_with(
            ["git", "rev-parse", "--verify", "refs/tags/v7.9"]
        )

    @patch("scripts.task.publish.get_output")
    def test_tag_without_previous_ancestor_fails(self, get_output) -> None:
        ancestry_error = subprocess.CalledProcessError(128, ["git"])
        get_output.side_effect = ["commit-id", ancestry_error]

        with self.assertRaises(subprocess.CalledProcessError):
            resolve_release_tags("v1.0")

        self.assertEqual(
            get_output.call_args_list,
            [
                call(["git", "rev-parse", "--verify", "refs/tags/v1.0"]),
                call(
                    [
                        "git",
                        "describe",
                        "--tags",
                        "--match",
                        "v*",
                        "--abbrev=0",
                        "v1.0^",
                    ]
                ),
            ],
        )


class PublishTest(unittest.TestCase):
    @patch("scripts.task.publish.subprocess.run")
    @patch(
        "scripts.task.publish.Path.read_text",
        return_value="<!-- changelog -->\nhttps://<url>",
    )
    @patch("scripts.task.publish.get_output")
    def test_dry_run_uses_resolved_explicit_tag(
        self, get_output, read_text, run
    ) -> None:
        get_output.side_effect = ["commit-id", "v7.8", "Change summary"]
        output = StringIO()

        with patch("scripts.task.publish.version_tag", return_value="v7.9"):  # noqa: SIM117
            with redirect_stdout(output):
                publish(write=False, tag="v7.9", dry=True)

        self.assertIn("changelog:\nChange summary", output.getvalue())
        self.assertIn("gh release create v7.9", output.getvalue())
        self.assertEqual(
            get_output.call_args_list,
            [
                call(["git", "rev-parse", "--verify", "refs/tags/v7.9"]),
                call(
                    [
                        "git",
                        "describe",
                        "--tags",
                        "--match",
                        "v*",
                        "--abbrev=0",
                        "v7.9^",
                    ]
                ),
                call(
                    [
                        "git",
                        "log",
                        "--pretty=format:- %s\n%b",
                        "v7.8..v7.9",
                    ]
                ),
            ],
        )
        read_text.assert_called_once_with()
        run.assert_not_called()

    @patch("scripts.task.publish.subprocess.run")
    @patch("scripts.task.publish.prepare_release_assets")
    @patch("scripts.task.publish.Path.write_text")
    @patch(
        "scripts.task.publish.Path.read_text",
        return_value="<!-- changelog -->\nhttps://<url>",
    )
    @patch("scripts.task.publish.get_output")
    def test_publish_command_uses_resolved_target_tag(
        self, get_output, read_text, write_text, prepare_assets, run
    ) -> None:
        get_output.side_effect = ["commit-id", "v7.8", "Change summary"]

        with patch("scripts.task.publish.version_tag", return_value="v7.9"):
            publish(write=False, tag="v7.9", dry=False)

        run.assert_called_once_with(
            [
                "gh",
                "release",
                "create",
                "v7.9",
                "release/*.zip",
                "release/release-manifest.json",
                "--notes-file",
                ".github/release_template.md",
                "-t",
                "V7.9",
                "--draft",
            ],
            check=True,
        )
        read_text.assert_called_once_with()
        write_text.assert_called_once()
        prepare_assets.assert_called_once_with()

    @patch("scripts.task.publish.subprocess.run")
    @patch("scripts.task.publish.get_output")
    def test_unknown_tag_does_not_publish(self, get_output, run) -> None:
        get_output.side_effect = subprocess.CalledProcessError(1, ["git"])

        with self.assertRaisesRegex(ValueError, "Unknown release tag: v7.9"):
            publish(write=False, tag="v7.9", dry=False)

        run.assert_not_called()

    @patch("scripts.task.publish.version_tag", return_value="v8.0")
    @patch("scripts.task.publish.get_output")
    def test_project_version_must_match_release_tag(self, get_output, version_tag):
        get_output.side_effect = ["commit-id", "v7.8"]

        with self.assertRaisesRegex(ValueError, "does not match the project version"):
            publish(write=False, tag="v7.9", dry=True)

        version_tag.assert_called_once_with()

    @patch("scripts.task.publish.version_tag", return_value="v8.0-beta.36")
    @patch("scripts.task.publish.get_output")
    def test_legacy_beta_tag_matches_current_project_version(
        self, get_output, version_tag
    ):
        get_output.side_effect = ["commit-id", "v7.9", "Change summary"]

        publish(write=False, tag="v8.0-beta36", dry=True)

        version_tag.assert_called_once_with()

    def test_release_manifest_expands_complete_grouped_matrix(self) -> None:
        manifest = release_manifest()
        archives = expected_release_archives()

        self.assertIn("cjk", manifest)
        self.assertFalse(any(key.startswith("cjk_") for key in manifest))
        self.assertEqual(len(archives), 176)
        self.assertEqual(len(manifest["archives"]), 176)
        self.assertEqual(len(manifest["nf_variants"]), 3)
        self.assertFalse(any("NR" in name for name in archives))
        self.assertIn("MapleMonoSL-Woff2.zip", archives)
        self.assertFalse(
            any("Static" in name or "Variable" in name for name in archives)
        )
        self.assertFalse(any("NFMono-VF" in name for name in archives))
        self.assertFalse(any("NFPropo-VF" in name for name in archives))
        self.assertTrue(
            all(
                name.endswith("-NFMono-unhinted.zip") or "NFMono" not in name
                for name in archives
            )
        )
        self.assertTrue(
            all(
                name.endswith("-NFPropo-unhinted.zip") or "NFPropo" not in name
                for name in archives
            )
        )

    def test_prepare_release_assets_writes_manifest(self) -> None:
        expected = expected_release_archives()
        with tempfile.TemporaryDirectory() as tmp:
            release_dir = Path(tmp)
            for archive_name in expected:
                (release_dir / archive_name).write_bytes(archive_name.encode())

            prepare_release_assets(release_dir)

            self.assertTrue((release_dir / "release-manifest.json").is_file())
            self.assertFalse((release_dir / "SHA256SUMS").exists())
            self.assertFalse(list(release_dir.glob("*.sha256")))

    def test_release_matrix_exposes_eight_bundle_tasks(self) -> None:
        bundle = release_matrix()["task"]

        self.assertEqual(len(bundle), 8)
        self.assertFalse(any("narrow" in task for task in bundle))
        self.assertIn("bundle-normal-no-ligature-slim", bundle)

    def test_release_task_owns_build_steps_and_archive_names(self) -> None:
        with self.assertRaises(ValueError):
            resolve_release_task("base-normal-narrow")

        bundle = resolve_release_task("bundle-normal-slim")
        steps = release_build_steps(bundle, ("--least-styles",))
        self.assertEqual(len(steps), 8)
        self.assertTrue(all("--least-styles" in step.args for step in steps))
        self.assertIn("--hinted", steps[0].args)
        self.assertNotIn("--archive", steps[0].args)
        self.assertNotIn("--archive", steps[1].args)
        self.assertNotIn("--archive", steps[2].args)
        self.assertIn("--no-hinted", steps[1].args)
        self.assertIn("--nf-variable", steps[2].args)
        self.assertIn("--nf-mono", steps[3].args)
        self.assertIn("--nf-propo", steps[4].args)
        self.assertEqual(len(bundle.archive_names()), 22)
        self.assertIn("MapleMonoNormalSL-VF.zip", bundle.archive_names())
        self.assertIn("MapleMonoNormalSL-NF-VF.zip", bundle.archive_names())
        self.assertIn("MapleMonoNormalSL-NFMono-unhinted.zip", bundle.archive_names())
        self.assertIn("MapleMonoNormalSL-NFPropo-unhinted.zip", bundle.archive_names())
        self.assertIn("MapleMonoNormalSL-NF-JP-VF.zip", bundle.archive_names())
        self.assertIn("MapleMonoNormalSL-NF-KR-unhinted.zip", bundle.archive_names())

        cjk_steps = steps[5:]
        self.assertTrue(all("--cjk" in step.args for step in cjk_steps))
        self.assertTrue(all("cn,tc,jp,kr" in step.args for step in cjk_steps))
        self.assertIn("--hinted", cjk_steps[0].args)
        self.assertIn("--cache", cjk_steps[0].args)
        self.assertNotIn("--cjk-hinted", cjk_steps[0].args)
        self.assertIn("--cjk-variable", cjk_steps[2].args)
        self.assertEqual(
            {archive.directory for archive in cjk_steps[0].archives},
            {"NF-CN", "NF-TC", "NF-JP", "NF-KR"},
        )
        self.assertEqual(cjk_steps[1].archives[0].suffix, "-unhinted")
        self.assertEqual(
            {archive.directory for archive in cjk_steps[2].archives},
            {"Variable-NF-CN", "Variable-NF-TC", "Variable-NF-JP", "Variable-NF-KR"},
        )

    def test_collect_release_task_archives_isolates_job_outputs(self) -> None:
        task = resolve_release_task("bundle-default-default")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive"
            output_dir = root / "release-task"
            archive_dir.mkdir()
            for archive_name in task.archive_names():
                (archive_dir / archive_name).write_bytes(b"archive")
            (archive_dir / "MapleMono-TTF.zip").write_bytes(b"unrelated")

            collect_release_task_archives(task, archive_dir, output_dir)

            self.assertEqual(
                {path.name for path in output_dir.iterdir()},
                set(task.archive_names()),
            )

    @patch("scripts.task.publish.collect_release_task_archives")
    @patch("scripts.task.publish.archive_release_step")
    @patch("scripts.pipeline.main")
    def test_build_release_task_runs_internal_steps(
        self,
        build_main,
        archive_step,
        collect_archives,
    ) -> None:
        task = resolve_release_task("bundle-default-slim")

        build_release_task(task.id, "--least-styles")

        expected_steps = release_build_steps(task, ("--least-styles",))
        self.assertEqual(
            build_main.call_args_list,
            [call(list(step.args)) for step in expected_steps],
        )
        self.assertEqual(
            archive_step.call_args_list,
            [call(task, step) for step in expected_steps],
        )
        collect_archives.assert_called_once_with(task)


if __name__ == "__main__":
    unittest.main()
