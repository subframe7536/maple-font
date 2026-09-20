from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.task.publish import (
    collect_release_task_archives,
    expected_release_archives,
    prepare_release_assets,
    release_build_steps,
    release_manifest,
    release_matrix,
    render_download_matrix,
    resolve_release_task,
)


class PublishTest(unittest.TestCase):
    def test_release_manifest_expands_complete_grouped_matrix(self) -> None:
        manifest = release_manifest()
        archives = expected_release_archives()

        self.assertIn("cjk", manifest)
        self.assertFalse(any(key.startswith("cjk_") for key in manifest))
        self.assertEqual(len(archives), 176)
        self.assertEqual(len(manifest["archives"]), 176)
        self.assertEqual(len(manifest["nf_variants"]), 3)
        self.assertIn("MapleMonoNR-Woff2.zip", archives)
        self.assertIn("MapleMonoSL-Woff2.zip", archives)
        self.assertNotIn("MapleMonoNR-NF-VF.zip", archives)
        self.assertNotIn("MapleMonoSL-NFMono-unhinted.zip", archives)
        self.assertNotIn("MapleMonoNR-NF-CN-VF.zip", archives)
        self.assertIn("MapleMonoNR-NF-CN-unhinted.zip", archives)
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

    def test_release_matrix_exposes_twelve_bundle_tasks(self) -> None:
        bundle = release_matrix()["task"]

        self.assertEqual(len(bundle), 12)
        self.assertIn("bundle-default-narrow", bundle)
        self.assertIn("bundle-normal-no-ligature-slim", bundle)

    def test_release_task_uses_full_and_compact_width_plans(self) -> None:
        default_bundle = resolve_release_task("bundle-normal-default")
        default_steps = release_build_steps(default_bundle, ("--least-styles",))
        self.assertEqual(len(default_steps), 8)
        self.assertEqual(len(default_bundle.archive_names()), 22)
        self.assertIn("--nf-variable", default_steps[2].args)
        self.assertIn("--nf-mono", default_steps[3].args)
        self.assertIn("--nf-propo", default_steps[4].args)
        self.assertIn("MapleMonoNormal-NF-JP-VF.zip", default_bundle.archive_names())

        narrow_bundle = resolve_release_task("bundle-normal-narrow")
        narrow_steps = release_build_steps(narrow_bundle, ("--least-styles",))
        self.assertEqual(len(narrow_steps), 4)
        self.assertTrue(all("--least-styles" in step.args for step in narrow_steps))
        self.assertEqual(len(narrow_bundle.archive_names()), 11)
        self.assertIn("--no-nf", narrow_steps[2].args)
        self.assertNotIn("--nf-variable", narrow_steps[2].args)
        self.assertTrue("--cjk" in narrow_steps[3].args)
        self.assertIn("--no-cjk-hinted", narrow_steps[3].args)
        self.assertIn("MapleMonoNormalNR-VF.zip", narrow_bundle.archive_names())
        self.assertIn(
            "MapleMonoNormalNR-NF-KR-unhinted.zip", narrow_bundle.archive_names()
        )
        self.assertNotIn("MapleMonoNormalNR-NF-VF.zip", narrow_bundle.archive_names())
        self.assertNotIn(
            "MapleMonoNormalNR-NFMono-unhinted.zip", narrow_bundle.archive_names()
        )
        self.assertNotIn("MapleMonoNormalNR-NF-JP.zip", narrow_bundle.archive_names())
        self.assertNotIn(
            "MapleMonoNormalNR-NF-JP-VF.zip", narrow_bundle.archive_names()
        )

    def test_download_matrix_is_generated_from_release_config(self) -> None:
        matrix = render_download_matrix()

        self.assertIn("### Narrow width (NR)", matrix)
        self.assertIn("### Slim width (SL)", matrix)
        self.assertIn("MapleMonoNR-NF-CN-unhinted.zip", matrix)
        self.assertNotIn("MapleMonoNR-NF-CN-VF.zip", matrix)
        self.assertNotIn("MapleMonoSL-NFMono-unhinted.zip", matrix)
        self.assertIn("MapleMono-NFMono-unhinted.zip", matrix)

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


if __name__ == "__main__":
    unittest.main()
